#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "pyyaml>=6.0"]
# ///
"""Snapshot ORCID works into data/publications.yaml and report coverage.

This is Phase 0 of plan.md: it changes nothing that Hugo renders. It builds a
committed snapshot of every work claimed on ORCID, enriches each DOI with
DataCite/Crossref metadata (authors, venue, resource type, relations), merges
optional per-record overrides, and compares the result against the hand-written
pages in content/papers and content/software.

Usage:
    uv run python/sync_publications.py            # fetch, write YAML, report
    uv run python/sync_publications.py --check    # report only, write nothing
    uv run python/sync_publications.py --refresh  # ignore the HTTP cache
    uv run python/sync_publications.py --offline  # cache only, no network

The snapshot is written to data/publications.yaml (keyed by a slugified DOI),
so templates can later read it via site.Data.publications.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import yaml

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
OUT_FILE = ROOT / "data" / "publications.yaml"
OVERRIDE_DIR = ROOT / "data" / "overrides"
MANUAL_DIR = ROOT / "data" / "manual"
TAGS_FILE = ROOT / "data" / "tags.yaml"
CACHE_DIR = Path(__file__).resolve().parent / ".cache" / "publications"

ORCID = "0009-0000-5893-9000"
SECTIONS = ("papers", "software")

USER_AGENT = (
    "f-hafner.github.io publication sync "
    "(+https://f-hafner.github.io; mailto:f.hafner@esciencecenter.nl)"
)

# DOI prefixes registered with DataCite; everything else is tried on Crossref.
DATACITE_PREFIXES = ("10.48550", "10.5281", "10.6084", "10.5061", "10.1594")

# DataCite resourceType/resourceTypeGeneral -> kind (None = uninformative)
DATACITE_KIND = {
    "software": "software",
    "dataset": "data",
    "preprint": "paper",
    "book": "paper",
    "bookchapter": "paper",
    "conferencepaper": "paper",
    "journalarticle": "paper",
    "conferencepresentation": "talk",
    "presentation": "talk",
    "poster": "talk",
    "lecture": "talk",
    "event": "talk",
    "audiovisual": "talk",
    "report": "report",
    "dissertation": "report",
    "text": None,
    "other": None,
    "collection": None,
}

# ORCID work type -> kind
ORCID_KIND = {
    "journal-article": "paper",
    "conference-paper": "paper",
    "conference-abstract": "paper",
    "book-chapter": "paper",
    "book": "paper",
    "edited-book": "paper",
    "preprint": "paper",
    "review": "paper",
    "report": "report",
    "dissertation": "report",
    "software": "software",
    "research-tool": "software",
    "dataset": "data",
    "lecture-speech": "talk",
    "conference-presentation": "talk",
    "conference-poster": "talk",
    "other": None,
}

DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>)\]}]+", re.IGNORECASE)
ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?", re.IGNORECASE)
TITLE_MATCH_THRESHOLD = 0.87

# DataCite values that carry no information about *what* the record is.
GENERIC_DATACITE_TYPES = {"text", "other", "collection", ""}


# --------------------------------------------------------------------------- #
# HTTP with on-disk cache
# --------------------------------------------------------------------------- #


class Http:
    """Tiny JSON GET client with an on-disk cache and polite retries."""

    def __init__(self, refresh: bool = False, offline: bool = False) -> None:
        self.refresh = refresh
        self.offline = offline
        self.failures: list[tuple[str, str]] = []
        self._client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        )

    def _cache_path(self, url: str, accept: str) -> Path:
        key = hashlib.sha256(f"{url}\n{accept}".encode()).hexdigest()[:16]
        return CACHE_DIR / f"{key}.json"

    def get(self, url: str, accept: str = "application/json") -> Any | None:
        cache = self._cache_path(url, accept)
        if cache.exists() and not self.refresh:
            return json.loads(cache.read_text())
        if self.offline:
            self.failures.append((url, "offline and not cached"))
            return None

        for attempt in range(3):
            try:
                response = self._client.get(url, headers={"Accept": accept})
                if response.status_code == 404:
                    self.failures.append((url, "HTTP 404"))
                    return None
                response.raise_for_status()
                payload = response.json()
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps(payload, indent=1))
                return payload
            except (httpx.HTTPError, json.JSONDecodeError) as exc:
                if attempt == 2:
                    self.failures.append((url, f"{type(exc).__name__}: {exc}"))
                    return None
        return None

    def close(self) -> None:
        self._client.close()


# --------------------------------------------------------------------------- #
# Normalisation helpers
# --------------------------------------------------------------------------- #


def slugify_doi(doi: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", doi.lower()).strip("-")


def norm_title(title: str) -> str:
    text = unicodedata.normalize("NFKD", title or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def clean_doi(value: str) -> str:
    # DOIs are case-insensitive; normalising keeps keys and diffs stable.
    return value.strip().rstrip(".,;").rstrip("/").lower()


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.lower()
        if item and key not in seen:
            seen.add(key)
            out.append(item)
    return out


def year_of(*candidates: Any) -> int | None:
    for candidate in candidates:
        if isinstance(candidate, int) and 1900 < candidate < 2100:
            return candidate
        if isinstance(candidate, str):
            match = re.search(r"(\d{4})", candidate)
            if match:
                return int(match.group(1))
    return None


# A specific non-paper claim from either source beats the "paper" default.
NON_PAPER_PRIORITY = ("software", "data", "talk", "report")


def classify(
    orcid_type: str | None, resource_type: str | None, resource_general: str | None
) -> tuple[str, str]:
    """Classify a record from both sources; returns (kind, deciding source).

    Neither source is authoritative: ORCID's `type` is user-curated but often
    misused (a Zenodo poster typed `journal-article`), while DataCite reports
    `resourceTypeGeneral: "Text"` for every Zenodo deposit but a specific
    `resourceType` ("Poster", "Presentation"). So collect every signal and let
    the most specific non-paper one win; `paper` is the fallback bucket.
    """
    signals: list[tuple[str, str]] = []
    mapped = ORCID_KIND.get(orcid_type or "")
    if mapped:
        signals.append((mapped, "orcid"))
    for candidate in (resource_type, resource_general):
        key = (candidate or "").lower().replace(" ", "").replace("-", "")
        if key in GENERIC_DATACITE_TYPES:
            continue
        mapped = DATACITE_KIND.get(key)
        if mapped:
            signals.append((mapped, "datacite"))
    for kind in NON_PAPER_PRIORITY:
        for mapped, source in signals:
            if mapped == kind:
                return kind, source
    return "paper", (signals[0][1] if signals else "default")



def section_of(kind: str) -> str:
    return "software" if kind in {"software", "data"} else "papers"


# --------------------------------------------------------------------------- #
# ORCID
# --------------------------------------------------------------------------- #


@dataclass
class Work:
    """One ORCID `work-summary`, flattened."""

    put_code: int | None
    title: str
    orcid_type: str | None
    journal_title: str | None
    year: int | None
    url: str | None
    source: str | None
    dois: list[tuple[str, str]] = field(default_factory=list)  # (doi, relationship)


def fetch_orcid_works(http: Http, orcid: str) -> list[Work]:
    payload = http.get(f"https://pub.orcid.org/v3.0/{orcid}/works")
    if not payload:
        return []

    works: list[Work] = []
    for group in payload.get("group") or []:
        summaries = group.get("work-summary") or []
        if not summaries:
            continue
        summary = summaries[0]
        external = (summary.get("external-ids") or {}).get("external-id") or []
        dois = [
            (clean_doi(item["external-id-value"]), item.get("external-id-relationship") or "")
            for item in external
            if item.get("external-id-type") == "doi" and item.get("external-id-value")
        ]
        works.append(
            Work(
                put_code=summary.get("put-code"),
                title=((summary.get("title") or {}).get("title") or {}).get("value") or "Untitled",
                orcid_type=summary.get("type"),
                journal_title=(summary.get("journal-title") or {}).get("value"),
                year=year_of((summary.get("publication-date") or {}).get("year", {}).get("value")),
                url=(summary.get("url") or {}).get("value"),
                source=(((summary.get("source") or {}).get("source-name") or {}).get("value")),
                dois=dois,
            )
        )
    return works


def primary_doi(work: Work) -> tuple[str | None, list[tuple[str, str]]]:
    """Pick a primary DOI plus the remaining self DOIs as version links."""
    if not work.dois:
        return None, []
    self_dois = [doi for doi, rel in work.dois if rel in ("self", "")]
    ordered = self_dois or [doi for doi, _ in work.dois]
    # Prefer a version of record over the arXiv preprint.
    favoured = [doi for doi in ordered if not doi.lower().startswith("10.48550/")]
    primary = (favoured or ordered)[0]
    return primary, [(doi, rel) for doi, rel in work.dois]


# --------------------------------------------------------------------------- #
# Enrichment: DataCite / Crossref
# --------------------------------------------------------------------------- #


@dataclass
class Enrichment:
    authors: list[str] = field(default_factory=list)
    venue: str | None = None
    publisher: str | None = None
    resource_general: str | None = None
    resource_type: str | None = None
    abstract: str | None = None
    year: int | None = None
    version: str | None = None
    license: str | None = None
    source: str | None = None
    links: list[dict[str, str]] = field(default_factory=list)


def _datacite_links(attributes: dict[str, Any]) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    for rel in attributes.get("relatedIdentifiers") or []:
        target = rel.get("relatedIdentifier")
        if not target:
            continue
        if (rel.get("relatedIdentifierType") or "").upper() == "DOI":
            target = f"https://doi.org/{clean_doi(target)}"
        links.append(
            {
                "rel": (rel.get("relationType") or "related").lower().replace("_", "-"),
                "url": target,
            }
        )
    return links


def _datacite_abstract(attributes: dict[str, Any]) -> str | None:
    descriptions = attributes.get("descriptions") or []
    for description in descriptions:
        if (description.get("descriptionType") or "").lower() == "abstract":
            return description.get("description")
    return descriptions[0].get("description") if descriptions else None


def enrich_datacite(http: Http, doi: str) -> Enrichment | None:
    payload = http.get(f"https://api.datacite.org/dois/{doi}")
    if not payload or "data" not in payload:
        return None
    attributes = payload["data"].get("attributes") or {}
    types = attributes.get("types") or {}
    container = attributes.get("container") or {}
    return Enrichment(
        authors=[
            # DataCite gives "Family, Given" in `name` plus the split fields.
            (
                f"{c['givenName']} {c['familyName']}"
                if c.get("givenName") and c.get("familyName")
                else c.get("name")
            )
            for c in (attributes.get("creators") or [])
            if c.get("name") or (c.get("givenName") and c.get("familyName"))
        ],
        # `container` is empty for Zenodo/arXiv; `types.resourceType` is a type
        # ("Article", "Presentation"), never a venue -- keep it in its own field.
        venue=container.get("title"),
        publisher=attributes.get("publisher"),
        resource_general=types.get("resourceTypeGeneral"),
        resource_type=types.get("resourceType"),
        abstract=_datacite_abstract(attributes),
        year=year_of(attributes.get("publicationYear")),
        version=attributes.get("version"),
        license=((attributes.get("rightsList") or [{}])[0]).get("rights"),
        source="datacite",
        links=_datacite_links(attributes),
    )


def enrich_crossref(http: Http, doi: str) -> Enrichment | None:
    payload = http.get(f"https://api.crossref.org/works/{doi}")
    if not payload or "message" not in payload:
        return None
    message = payload["message"]
    container = (message.get("container-title") or [None])[0]
    authors = []
    for author in message.get("author") or []:
        name = " ".join(p for p in (author.get("given"), author.get("family")) if p)
        if name:
            authors.append(name)
    issued = ((message.get("issued") or {}).get("date-parts") or [[None]])[0]
    links = [
        {
            "rel": (relation_type or "related").lower().replace("_", "-"),
            "url": (
                f"https://doi.org/{clean_doi(target)}"
                if "://" not in target
                else target
            ),
        }
        for relation_type, targets in (message.get("relation") or {}).items()
        for target in targets
        if target and relation_type != "is-preprint-of"
    ]
    return Enrichment(
        authors=authors,
        venue=container,
        publisher=message.get("publisher"),
        resource_general=None,
        resource_type=message.get("type"),
        abstract=re.sub(r"<[^>]+>", "", message.get("abstract") or "") or None,
        year=year_of(issued[0] if issued else None),
        source="crossref",
        links=links,
    )


def enrich(http: Http, doi: str) -> Enrichment | None:
    prefix = doi.split("/")[0].lower()
    if prefix in DATACITE_PREFIXES:
        found = enrich_datacite(http, doi)
        if found:
            return found
        return enrich_crossref(http, doi)
    found = enrich_crossref(http, doi)
    if found:
        return found
    return enrich_datacite(http, doi)


# --------------------------------------------------------------------------- #
# Record assembly
# --------------------------------------------------------------------------- #


def enrich_zenodo(http: Http, doi: str | None) -> dict[str, Any] | None:
    """Resolve the newest published version via the Zenodo API.

    Zenodo redirects `/api/records/<any version id>` to the latest version, so the
    returned `doi` is the newest one. Returns None when the record already *is*
    the latest version (nothing to link to).
    """
    if not doi or not doi.startswith("10.5281/"):
        return None
    payload = http.get(f"https://zenodo.org/api/records/{doi.rsplit('.', 1)[-1]}")
    if not payload:
        return None
    # Version records return themselves; the concept record redirects to the newest
    # published version, which is what "latest" should point at.
    concept_recid = payload.get("conceptrecid")
    latest = (
        http.get(f"https://zenodo.org/api/records/{concept_recid}")
        if concept_recid
        else payload
    ) or payload
    latest_doi = clean_doi(latest.get("doi") or "")
    if not latest_doi or latest_doi == doi:
        return None
    return {
        "latest_doi": latest_doi,
        "latest_version": ((latest.get("metadata") or {}).get("version") or "").strip()
        or None,
    }


def build_record(
    work: Work,
    enrichments: dict[str, Enrichment | None],
    http: Http | None = None,
) -> dict[str, Any]:
    doi, all_dois = primary_doi(work)
    main = enrichments.get(doi or "", None) or Enrichment()
    kind, kind_source = classify(
        work.orcid_type, main.resource_type, main.resource_general
    )

    repository = _repository_of(doi) or _repository_of(
        next((d for d, _ in all_dois), None)
    )
    if not repository and work.journal_title and _is_repository_name(work.journal_title):
        repository = work.journal_title.strip()
    # `venue` is the publication venue, `repository` the deposit/registry.
    # DataCite reports e.g. resourceType "Article" for arXiv uploads -- not a venue.
    venue = next(
        (
            candidate
            for candidate in (work.journal_title, main.venue)
            if candidate and not _is_repository_name(candidate)
        ),
        None,
    )
    # `preprint` describes *this* DOI, not the ORCID type of the whole work.
    is_preprint = (main.resource_type or "").lower().startswith("preprint") or (
        (doi or "").startswith("10.48550/")
    )
    has_preprint = any(d.startswith("10.48550/") for d, _ in all_dois) or is_preprint

    links: list[dict[str, str]] = []
    if doi:
        links.append({"rel": "doi", "url": f"https://doi.org/{doi}"})
    for other, _rel in all_dois:
        if doi and other == doi:
            continue
        rel = "preprint" if other.startswith("10.48550/") else "version"
        links.append({"rel": rel, "url": f"https://doi.org/{other}"})
    if work.url:
        links.append({"rel": "url", "url": work.url})
    links.extend(main.links)

    abstract = main.abstract
    if abstract:
        abstract = " ".join(abstract.split())
        if len(abstract) > 1200:
            abstract = abstract[:1197].rstrip() + "..."

    # DataCite reports bare integers (arXiv v1, v2) as "version" -- noise on a card.
    version = main.version if main.version and not main.version.strip("v").isdigit() else None
    latest = enrich_zenodo(http, doi) if http else None

    return {
        "doi": doi,
        "kind": kind,
        "section": section_of(kind),
        "preprint": bool(is_preprint),
        "has_preprint": bool(has_preprint),
        "title": work.title,
        "authors": main.authors,
        "year": work.year or main.year,
        "venue": venue,
        "repository": repository,
        "publisher": main.publisher,
        "abstract": abstract,
        "orcid_put_code": work.put_code,
        "orcid_type": work.orcid_type,
        "datacite_type": main.resource_type,
        "kind_source": kind_source,
        "orcid_source": work.source,
        "version": version,
        "latest_doi": (latest or {}).get("latest_doi"),
        "latest_version": (latest or {}).get("latest_version"),
        "behind_latest": bool(
            latest
            and version
            and latest.get("latest_version")
            and latest["latest_version"] != version
        ),
        "license": main.license,
        "links": _dedupe_links(links),
        "enriched_by": main.source,
        "manual_page": None,
    }


def _repository_of(doi: str | None) -> str | None:
    if not doi:
        return None
    return {
        "10.48550": "arXiv",
        "10.5281": "Zenodo",
        "10.6084": "figshare",
        "10.5061": "Dryad",
        "10.1594": "PANGAEA",
    }.get(doi.split("/")[0].lower())


def _is_repository_name(value: str) -> bool:
    return value.strip().lower() in {
        "zenodo",
        "arxiv",
        "figshare",
        "dryad",
        "pangaea",
        "osf",
        "github",
    }


def _dedupe_links(links: list[dict[str, str]]) -> list[dict[str, str]]:
    """One link per target URL; the first (most specific) relation wins."""
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for link in links:
        url = (link.get("url") or "").strip()
        if not url.lower().startswith(("http://", "https://")):
            continue
        key = url.lower().rstrip("/")
        if key not in seen:
            seen.add(key)
            out.append({"rel": link.get("rel", "related"), "url": url})
    return out


# --------------------------------------------------------------------------- #
# Overrides
# --------------------------------------------------------------------------- #


def load_overrides() -> dict[str, dict[str, Any]]:
    overrides: dict[str, dict[str, Any]] = {}
    if not OVERRIDE_DIR.exists():
        return overrides
    for path in sorted(OVERRIDE_DIR.glob("*.y*ml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            print(f"  ! could not parse override {path}: {exc}", file=sys.stderr)
            continue
        if isinstance(data, dict):
            overrides[path.stem.lower()] = data
    return overrides


def apply_overrides(records: dict[str, dict[str, Any]]) -> int:
    applied = 0
    for key, patch in load_overrides().items():
        if key not in records:
            print(f"  ! override for unknown doi key '{key}' ignored", file=sys.stderr)
            continue
        for field_name, value in patch.items():
            if value is not None:
                records[key][field_name] = value
        applied += 1
    return applied


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #


def write_snapshot(records: dict[str, dict[str, Any]], out: Path) -> bool:
    """Write the snapshot; returns False when nothing changed (stable diffs)."""
    ordered = dict(
        sorted(
            records.items(),
            key=lambda item: (
                -(item[1].get("year") or 0),
                norm_title(item[1].get("title") or ""),
            ),
        )
    )
    body = yaml.safe_dump(
        ordered,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )
    if out.exists():
        previous = "\n".join(
            line
            for line in out.read_text(encoding="utf-8").splitlines()
            if not line.startswith("#")
        )
        if previous.strip() == body.strip():
            return False
    header = (
        "# Generated by python/sync_publications.py -- do not edit by hand.\n"
        "# Per-record corrections belong in data/overrides/<key>.yaml.\n"
        f"# Synced: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}\n"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(header + body, encoding="utf-8")
    return True



# --------------------------------------------------------------------------- #
# Manual records (data/manual/*.yaml): hand-maintained, never regenerated
# --------------------------------------------------------------------------- #

MANUAL_KINDS = {"paper", "software", "data", "talk", "report"}


@dataclass
class ManualRecord:
    key: str
    path: Path
    data: dict[str, Any]
    problems: list[str] = field(default_factory=list)


def load_manual_records() -> list[ManualRecord]:
    """Load and sanity-check entries that have no ORCID work (no DOI, etc.)."""
    records: list[ManualRecord] = []
    if not MANUAL_DIR.exists():
        return records
    for path in sorted(MANUAL_DIR.glob("*.y*ml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            print(f"  ! could not parse {path.name}: {exc}", file=sys.stderr)
            continue
        if not isinstance(data, dict):
            print(f"  ! {path.name} is not a mapping, skipped", file=sys.stderr)
            continue
        record = ManualRecord(key=path.stem, path=path, data=data)
        if not data.get("title"):
            record.problems.append("missing `title`")
        kind = data.get("kind") or "paper"
        if kind not in MANUAL_KINDS:
            record.problems.append(f"unknown kind `{kind}` (one of {sorted(MANUAL_KINDS)})")
        if not data.get("year"):
            record.problems.append("missing `year` (cards sort on it)")
        if not data.get("summary") and not data.get("abstract"):
            record.problems.append("no `summary`/`abstract` (card body would be empty)")
        title_url = data.get("title_url")
        if title_url and not str(title_url).startswith(("/", "http")):
            record.problems.append("`title_url` must be a site path or an URL")
        for link in data.get("links") or []:
            if not isinstance(link, dict) or not str(link.get("url", "")).startswith(
                ("/", "http")
            ):
                record.problems.append(f"link without usable `url`: {link}")
        records.append(record)
    return records


def report_manual(
    manual: list[ManualRecord], records: dict[str, dict[str, Any]]
) -> None:
    line = "=" * 78
    print(f"\n{line}\nManual records (data/manual): {len(manual)}\n{line}")
    known_dois = {
        (record.get("doi") or "").lower()
        for record in records.values()
        if record.get("doi")
    }
    for item in manual:
        data = item.data
        doi = str(data.get("doi") or "").lower()
        where = doi or "no DOI"
        extra = f" [{data['comment']}]" if data.get("comment") else ""
        print(
            f"  {(data.get('kind') or 'paper'):9} {item.key:24} {where:34}"
            f"{str(data.get('title'))[:38]}{extra}"
        )
        for problem in item.problems:
            print(f"      ! {problem}")
        if doi and doi in known_dois:
            print(
                "      ! also on ORCID -- drop the manual file and curate via "
                "data/overrides/ instead"
            )


# --------------------------------------------------------------------------- #
# Tags: controlled vocabulary in data/tags.yaml, assignments in overrides
# --------------------------------------------------------------------------- #


def slugify_tag(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_vocabulary() -> tuple[dict[str, str], dict[str, str]]:
    """Returns (slug -> display title, alias slug -> canonical slug)."""
    titles: dict[str, str] = {}
    aliases: dict[str, str] = {}
    if not TAGS_FILE.exists():
        print(f"  ! {TAGS_FILE.name} missing, tags are not validated", file=sys.stderr)
        return titles, aliases
    data = yaml.safe_load(TAGS_FILE.read_text(encoding="utf-8")) or {}
    for slug, entry in data.items():
        entry = entry or {}
        titles[slug] = entry.get("title") or slug
        for alias in entry.get("aliases") or []:
            aliases[slugify_tag(alias)] = slug
    return titles, aliases


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_front_matter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not match:
        return {}, text
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - broken front matter
        print(f"  ! could not parse front matter in {path}: {exc}", file=sys.stderr)
        data = {}
    return data if isinstance(data, dict) else {}, match.group(2)


def collect_content_tags(root: Path) -> dict[str, list[str]]:
    """Tags of every markdown page on the site, keyed by path (for validation)."""
    found: dict[str, list[str]] = {}
    for path in sorted((root / "content").rglob("*.md")):
        front, _ = read_front_matter(path)
        tags = [str(tag) for tag in (front.get("tags") or [])]
        if tags:
            found[_relative(path)] = tags
    return found


def validate_tags(
    records: dict[str, dict[str, Any]],
    content_tags: dict[str, list[str]],
    titles: dict[str, str],
    aliases: dict[str, str],
) -> list[str]:
    problems: list[str] = []

    def check(tag: str, where: str) -> None:
        slug = slugify_tag(tag)
        if tag in titles and tag == slug:
            return
        if slug in titles:
            problems.append(f"non-canonical `{tag}` in {where} -- use `{slug}`")
        elif slug in aliases:
            target = aliases[slug]
            problems.append(f"alias `{tag}` in {where} -- use `{target}`")
        else:
            problems.append(f"unknown `{tag}` in {where} -- add it to data/tags.yaml")

    for key, record in records.items():
        for tag in record.get("tags") or []:
            check(str(tag), f"{key}")
    for path, tags in content_tags.items():
        for tag in tags:
            check(tag, path)
    return problems


def report_tags(
    records: dict[str, dict[str, Any]],
    content_tags: dict[str, list[str]],
    titles: dict[str, str],
    problems: list[str],
) -> None:
    line = "=" * 78
    used: set[str] = set()
    untagged: list[str] = []
    per_tag: dict[str, int] = {}
    for record in records.values():
        assigned = [str(tag) for tag in (record.get("tags") or [])]
        if not assigned:
            untagged.append(record.get("title") or record.get("doi") or "?")
        for tag in assigned:
            used.add(tag)
            per_tag[tag] = per_tag.get(tag, 0) + 1
    for tags in content_tags.values():
        used.update(tags)
        for tag in tags:
            per_tag[tag] = per_tag.get(tag, 0) + 1

    print(f"\n{line}\nTags\n{line}")
    print(f"vocabulary            : {len(titles)} terms")
    print(f"ORCID records tagged  : {len(records) - len(untagged)}/{len(records)}")
    if untagged:
        print("  without tags        : " + "; ".join(t[:44] for t in untagged))
    unused = sorted(set(titles) - used)
    if unused:
        print("  unused terms        : " + ", ".join(unused))
    if per_tag:
        top = sorted(per_tag.items(), key=lambda item: (-item[1], item[0]))[:6]
        print("  most used           : " + ", ".join(f"{t} ({c})" for t, c in top))
    for problem in problems:
        print(f"  ! {problem}")


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #


def _doi_of(url: str) -> str | None:
    marker = "doi.org/"
    if marker not in url:
        return None
    return clean_doi(url.split(marker, 1)[1])


def possible_duplicates(records: dict[str, dict[str, Any]]) -> list[tuple[str, str, str]]:
    """Records that point at each other's DOIs (preprint/published, deposit/paper)."""
    owners: dict[str, str] = {}
    for key, record in records.items():
        for doi in [record.get("doi")] + [_doi_of(l["url"]) for l in record["links"]]:
            if doi:
                owners.setdefault(doi, key)
    pairs: set[tuple[str, str]] = set()
    found: list[tuple[str, str, str]] = []
    for key, record in records.items():
        for link in record["links"]:
            other = owners.get(_doi_of(link["url"]) or "")
            if other and other != key and (other, key) not in pairs:
                pairs.add((key, other))
                found.append((key, other, link["rel"]))
    return found


def report(
    records: dict[str, dict[str, Any]],
    http: Http,
    written: Path | None,
    check: bool = False,
) -> None:
    line = "=" * 78
    print(f"\n{line}\nORCID works: {len(records)}\n{line}")
    for record in records.values():
        flags = []
        if record.get("preprint"):
            flags.append("preprint")
        if record.get("manual_page"):
            flags.append("page")
        else:
            flags.append("NO PAGE")
        print(
            f"{record.get('year') or '????'!s:4}  {record['kind']:9} "
            f"{record['title'][:46]:48} "
            f"{(record.get('venue') or record.get('repository') or '-'):22} "
            f"[{', '.join(flags)}]"
        )

    duplicates = possible_duplicates(records)
    if duplicates:
        print("\nPossible duplicate records (same work, several ORCID entries):")
        for left, right, rel in duplicates:
            print(f"  {left}\n    <-> {right}  ({rel})")

    stale = [
        r for r in records.values() if r.get("behind_latest") and r.get("latest_doi")
    ]
    if stale:
        print("\nNewer version published on Zenodo than claimed on ORCID:")
        for record in stale:
            print(
                f"  {record['title'][:52]:54} {record.get('version') or '?'}"
                f" -> {record.get('latest_version') or '?'}  ({record['latest_doi']})"
            )

    if http.failures:
        print("\nFetch problems:")
        for url, reason in http.failures:
            print(f"  {reason:32} {url}")

    if written:
        print(f"\nSnapshot written to {_relative(written)} ({len(records)} records)")
    elif check:
        print("\n--check: snapshot not written")
    else:
        print(f"\nSnapshot unchanged, nothing written to {_relative(OUT_FILE)}")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report only, write nothing")
    parser.add_argument("--refresh", action="store_true", help="ignore the HTTP cache")
    parser.add_argument("--offline", action="store_true", help="cache only, no network")
    parser.add_argument("--out", type=Path, default=OUT_FILE, help="snapshot path")
    parser.add_argument("--orcid", default=ORCID, help="ORCID iD to sync")
    args = parser.parse_args(argv)

    http = Http(refresh=args.refresh, offline=args.offline)
    try:
        print(f"Fetching ORCID works for {args.orcid} ...")
        works = fetch_orcid_works(http, args.orcid)
        if not works:
            print("No works returned; nothing to do.", file=sys.stderr)
            return 1
        print(f"  {len(works)} works")

        doi_set = dedupe(
            [doi for work in works for doi, _ in work.dois if doi]
        )
        print(f"Enriching {len(doi_set)} DOIs via DataCite/Crossref ...")
        enrichments = {doi: enrich(http, doi) for doi in doi_set}
        missing = [doi for doi, value in enrichments.items() if not value]
        if missing:
            print(f"  {len(missing)} DOI(s) could not be enriched: {', '.join(missing)}")

        records: dict[str, dict[str, Any]] = {}
        for work in works:
            record = build_record(work, enrichments, http)
            key = slugify_doi(record["doi"] or norm_title(record["title"]))
            if key in records:
                key = f"{key}-{record['orcid_put_code']}"
            records[key] = record

        overrides = apply_overrides(records)
        if overrides:
            print(f"  {overrides} override file(s) applied")

        written = None
        if not args.check:
            written = args.out if write_snapshot(records, args.out) else None

        manual = load_manual_records()
        report(records, http, written, check=args.check)
        titles, aliases = load_vocabulary()
        content_tags = collect_content_tags(ROOT)
        for item in manual:
            tags = [str(tag) for tag in (item.data.get("tags") or [])]
            if tags:
                content_tags[str(item.path.relative_to(ROOT))] = tags
        report_tags(
            records,
            content_tags,
            titles,
            validate_tags(records, content_tags, titles, aliases),
        )
        report_manual(manual, records)
    finally:
        http.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
