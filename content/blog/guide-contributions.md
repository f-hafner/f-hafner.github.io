---
title: "Contributions to the eScience Center guide" 
date: 2025-01-13
url: /escience-guide/
author: "Flavio Hafner"
description: "Contributions I made to the Guide of the Netherlands eScience Center."
tags: ["data", "software-development", "continuous-integration"]
summary: "Contributions I made to the Guide of the Netherlands eScience Center."
showToc: true 
disableAnchoredHeadings: false

---

In summer 2024, I co-authored a chapter on [tabular datasets](https://guide.esciencecenter.nl/#/technology/datasets), where we tested DuckDB's limits on nested queries on big datasets. We found that it works well when enough memory is available, but using it on a local machine with such datasets does not easily work out of the box. Some code can be found [here](https://github.com/f-hafner/db_comparisons).

Earlier I also updated the [instructions](https://guide.esciencecenter.nl/#/language_guides/python?id=packaging-and-distributing-your-package) for automatically publishing python packages from github, using the trusted publishing method instead of secret tokens.

---
