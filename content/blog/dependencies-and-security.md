---
title: "Dependency management and security"
date: 2025-01-22
url: /dependency-and-security/
author: "Flavio Hafner"
description: "Thoughts on dependency management in python and security issues"
tags: ["reproducibility", "computer-security"]
summary: "Thoughts on dependency management in python and security issues"
showToc: false 
disableAnchoredHeadings: false

---

On Thursday, 30 January 2025, I'm giving a talk at Tilburg University on dependency management in R and Python. The slides are available [here](https://f-hafner.github.io/dependency-management/slides.html#/title-slide). 

While preparing the slides, I realized how routinely using popular open source libraries such as pytorch or huggingface can introduce vulnerabilities for [supply-chain](https://johnstawinski.com/2024/01/11/playing-with-fire-how-we-executed-a-critical-supply-chain-attack-on-pytorch/) or [backdoor](https://jfrog.com/blog/data-scientists-targeted-by-malicious-hugging-face-ml-models-with-silent-backdoor/) attacks. Fortunately, in both examples, the issues were found before by researchers before it was exploited by a malicious actor. 

Despite this, I think that security needs more attention in research software development.

And no, closed-source [is not better](https://www.economist.com/leaders/2024/04/04/a-chilling-near-miss-shows-how-todays-digital-infrastructure-is-vulnerable).



---
