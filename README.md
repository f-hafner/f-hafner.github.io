
# Personal website

Personal website, built with Hugo from my ORCID record and enriched
with linked open data.

## Architecture
- Items for paper and software lists are built with Hugo layouts. The data 
are read from `yaml` files with metadata:
    - `data/publications.yaml` is auto-generated.
    - Manual entries can be added in `data/manual`.
- In the built website, each item links to at least one source.
    - For published papers, that is at least the DOI.
    - For unpublished papers, static content like pdfs can be put in `static`,
    and linked in `data/manual/*.yaml` via `title_url` or `links`.
- Blogs and teaching are maintained by hand.
- `data/overrides` contains user-defined data such as publication tags
and publication status.
- Tags are from a controlled vocabulary in `data/tags.yaml` and used by
    `content/tags/_content.gotmpl`


## Workflow
- Set your ORCID id in `config.yml`
- If necessary, edit manual entries in `data/manual`. 
- Fetch data with `uv run python/sync_publications.py`
- Update `data/overrides` by adding tags or abstract as desired. 
    - Use the controlled vocabulary in `data/tags.yaml`.
    - If you use new tags, they need to be lowercase and hyphenated and added 
    to `data/tags.yaml`.
- Re-run `uv run python/sync_publications.py` to apply overrides and
  update `data/publications.yaml`. Run `uv run python/sync_publications.py --check` 
  to verify the vocabulary.
- Build website: `hugo server`
- Publishing
    - commit also `data/`
    - Push and publish via GitHub actions.


## Credits
- The template is forked from Pascal Michaillat; the documentation is [here](https://pascalmichaillat.org/d5/). 
- The idea of using layouts for integrating ORCID data is adapted from https://kotthoff.dev/posts/202411-hugoorcid/  under the CC-BY 4.0 license


