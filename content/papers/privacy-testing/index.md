---
title: "Empirical Privacy Evaluations of Generative and Predictive Machine Learning Models -- A review and challenges for practice"
date: 2024-11-20
url: /privacy-testing/
# aliases: 
#     - /old_url.html
tags: ["machine learning", "differential privacy", "literature review"]
author: ["Flavio Hafner", "Chang Sun"]
description: "We review the empirical testing of privacy in machine learning. We discuss whether and how these tests could be used when evaluating generative algorithms for deployment at statistical agencies and in the health care system. " 
summary: "We review the empirical testing of privacy in machine learning. We discuss whether and how these tests could be used when evaluating generative algorithms for deployment at statistical agencies and in the health care system. " 
# cover:
#     image: "/paper_figure.png"
#     alt: "Figure from paper"
#     relative: false
# editPost:
#     URL: null
#     Text: "Draft"

---

---

##### Download:

- [Preprint](privacy-testing.pdf)
<!-- - [Online appendix](/appendix.pdf)
- [Code and data](https://github.com/paper_repo) -->

---

##### Abstract:

Synthetic data generators, when trained using privacy-preserving techniques like differential privacy, promise to produce synthetic data with formal privacy guarantees, facilitating the sharing of sensitive data. However, it is crucial to empirically assess the privacy risks associated with the generated synthetic data before deploying generative technologies. This paper outlines the key concepts and assumptions underlying empirical privacy evaluation in machine learning-based generative and predictive models. Then, this paper explores the practical challenges for privacy evaluations of generative models for use cases with millions of training records, such as data from statistical agencies and healthcare providers. Our findings indicate that methods designed to verify the correct operation of the training algorithm are effective for large datasets, but they often assume an adversary that is unrealistic in many scenarios. Based on the findings, we highlight a crucial trade-off between the computational feasibility of the evaluation and the level of realism of the assumed threat model. Finally, we conclude with ideas and suggestions for future research.

<!-- --- -->

<!-- ##### Figure X:  Figure title

![](/figurex.png)

--- -->

<!-- ##### Citation

Author 1, Author 2. Year. "Title." *Journal* Volume (Issue): First page–Last page. https://doi.org/paper_doi.

```BibTeX
@article{AAYY,
author = {Author 1 and Author 2},
doi = {paper_doi},
journal = {Journal},
number = {Issue},
pages = {XXX--YYY},
title = {Title},
volume = {Volume},
year = {Year}}
``` -->

---

##### Related material

<!-- + [Presentation slides](/presentation.pdf) -->
- [Project on the Research Software Directory](https://research-software-directory.org/projects/gans)
- [arxiv](https://arxiv.org/abs/2411.12451)
- [Presentation at the Odissei Community conference 2024](https://doi.org/10.5281/zenodo.14439435)
