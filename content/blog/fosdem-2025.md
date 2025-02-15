---
title: "FOSDEM 2025 Highlights"
date: 2025-02-15
url: /fosdem-2025/
author: "Flavio Hafner"
description: "My summary of the FOSDEM conference"
tags: ["conference", "open-source-software", "differential-privacy", "python"]
summary: "Highlights and notes from FOSDEM 2025"
showToc: false 
disableAnchoredHeadings: false

---

In the beginning of February, I went to the FOSDEM conference in Brussels, attending devrooms related to Python, data analytics, and privacy. Here are my insights.

## Confidential computing and privacy

### Confidential computing
I attended the first sessions of the Confidential Computing devroom. It's the first time I heard about Trusted Execution Environments and the like. 
- Interest in Confidential Computing is exploding among cloud service providers. This makes sense, given that more data are moving to the cloud, and data owners have an interest in keeping their data safe. 
- Trusted Execution Environments (TEE) protect the data and code loaded into a computer from unauthorized access. 
- The CCC=Confidential Computing Consortium has Special Interest Groups with recordings, which may be interesting to check out
- Dayeol Lee from TikTok talked about `ManaTEE`, an open-source private data analytics framework with confidential computing. [Github repository](https://github.com/manatee-project/manatee).
    - They divide data analysis workflow in two stages, and use different technologies in the two.
        1. For interactive, model development tasks, it is hard to control what happens to the data, and risk of privacy leakage is high. In turn, not the complete data set is necessary for developing the model. Thus, for the interactive front-end, they generate differentially-private synthetic data following [McKenna et. al. 2018](https://arxiv.org/pdf/2108.04978). 
        2. In the execution stage, the model is trained on the full data. Here, it's easier to deploy the model on the real data without human intervention. Therefore, this stage is deployed in a TEE without the analyst interacting with it. 
    - My thoughts:
        - This is another example of how privacy-preserving technologies are complementary to each other, here it is differential privacy and TEES.
        - I understood that ManaTEE assumes that the final model is executed only once on the entire dataset. From my experience, this seems rarely to be the case (but may depend on the quality of the synthetic data in the first stage). 
        - In addition, machine learning models learn to represent their training data, and therefore a TEE is not enough for ensuring data privacy against an adversarial data analyst. Additional constraints are necessary, for instance noise infusion through differential privacy, or legal rules that impose high cost on abusing research data, as is common when accessing registry data. But if legal restrictions are used, why are they not imposed directly on the first stage of the analytics workflow? 

### PostgreSQL Anonymizer
In the PostgreSQL devroom, Damien Clochard talked about his [anonymizer](https://gitlab.com/dalibo/postgresql_anonymizer) extension for Postgres.
The extension has several features for protecting sensitive data. 
- A masking engine with different ways to mask data
    - For instance, static masking displays a number partially masked: `0352*****831`. For instance, a person in customer service may need the start/end of a social security number of identifying the caller, but does not need to know the entire number.
- A masking toolbox with randomization, faking/synthesizing, data destruction and noise addition.
- It's all about reducing the attack surface for an adversary: each person that has access to the data is a potential attack target.
    - For instance, the software developer working on applications of the data can work with an anonymized dump, or fake data.
    - The data scientist doing the analytics can work with data that are masked, sub-sampled and potentially noise-infused.
    - The extension allows defining role-based rules for such access restrictions.
- The extension provides an implementation of k-anonymity, currently the industry standard. Differential privacy is on the roadmap, too.


## Python and data analysis
- The talk *advanced parsing of structured data* showed how to use Python's `match` statement. For instance, parsing JSON and GeoJSON. 
    - As of now, it seems `match` is about 2x slower than `if`, but makes code more readable.
    - The code is [here](https://github.com/eGenix/egenix-advanced-match-parsing).
- There were several talks about the Apache Arrow memory format. I want to have a closer look at this.
- There was an interesting talk about `Polylith`, a modular architecture for mono-repos and a substitute for microservices. The main benefit is modularity, the cost are bloated dependencies and potentially version conflicts. Link [here](https://github.com/DavidVujic/python-polylith).
- A developer from Target showed how to use `make` for reproducing python environments with one click ("no one reads the documentation"). Another benefit so that `make` tasks can be used in CI builds to mirror the development environment. Link [here](https://tech.target.com/blog/make-python-devex).
- People from Picnic introduced the `dbt-score` linter for enforcing consistency in `dbt` config files written in `yaml`. This is a cool idea, and it also seems more general: the linter operates on the dictionary defined by the `yaml` files, and therefore rules could be applied to any kind of `yaml` configuration files. Link [here](https://dbt-score.picnic.tech/).





---
