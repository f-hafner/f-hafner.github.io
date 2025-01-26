---
title: "Representation learning on population registry data"
date: 2025-01-16
url: /odissei-lifecourse/
tags: ["machine learning", "registry data", "deepwalk", "transformer architecture"]
author: ["Flavio Hafner", "Tanzir Pial", "Dakota Handzlik"]
description: "Training vector representations on Dutch registry data."
summary: "Training vector representations on Dutch registry data."
disableAnchoredHeadings: false
showToc: false

---

##### Links

- [`pop2vec`: Main code of the project](https://github.com/odissei-lifecourse/life-sequencing-dutch)
- [A parallel random walk algorithm for heterogeneous graph edges](https://github.com/odissei-lifecourse/layered_walk)
    - We are currently packaging this code, new repository coming soon.


##### Description

In this project, we train vector representations on registry data. The sequential approach uses a BERT-type sequence model for life events. The graph approach trains embeddings with `deepwalk` on population-scale network data.
We deploy the model training and inference on GPUs of the national cluster computer.
We evaluate the model performance on prediction tasks from the social sciences.

---
