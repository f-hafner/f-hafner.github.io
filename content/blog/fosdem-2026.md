---
title: "FOSDEM 2026 highlights: security, LLMs, and software performance"
date: 2026-02-04
url: /fosdem-2026/
author: "Flavio Hafner"
description: "My summary of FOSDEM 2026"
tags: ["conference", "open-source-software", "machine learning", "tools"]
summary: "Highlights and notes from FOSDEM 2026."
showToc: true
disableAnchoredHeadings: false

---

My highlights from this year's Fosdem are in the areas of LLM/security/open source, in machine learning/software performance, and in databases/search.

## Upcoming features in git

Patrick Steinhardt from Gitlab, and git contributor, [presented](https://fosdem.org/2026/schedule/event/HTJK33-evolving_git_for_the_next_decade/) about some upcoming changes, planned for the major 3.0 release towards mid-2026.

### Under the hood, git changes the hashing algorithm from SHA-1 to SHA-256. 
- This is because SHA-1 is not secure---a paper from around 2017 showed that it does not create unique hashes. 
- While git itself does not rely on uniqueness of hashes, the ecosystem implicitly does, for instance by pinning software dependencies to git hashes.
- At the same time, large parts of the ecosystem (GitHub for instance) do currently not support SHA-256 hashes. 
- By moving the default in git, the contributors want to solve the chicken-and-egg problem of "no one wanting to use the feature because no-one supports it" and vice versa.

### New command: `git history` for easier rewriting of history
- In git, rewriting history through an interactive rebase is cumbersome and takes several steps. 
- Another limitation is that it leads to orphane branches because other branches depending on the changed commits are not update. For instance, this makes is tedious to use workflows with stacked branches.
- The new `git history` command, inspired other version control systems such as Jujutsu and Mercurial, provides some functionality that makes such workflows easier. For instance, `git history reword <commit>` allows to amend the commit message of a specific commit; `git history split <commit>` allows to split a specific commit.
- The new commands *also* rebase other branches that depend on respective commits.


## Open Source, LLMs, and security

This was a major topic in this year's conference and featured in two keynotes: Michael Leenaars [(talk)](https://fosdem.org/2026/schedule/event/FE7ULY-foss-in-times-of-war-scarcity-and-ai/) from NLnet, and Daniel Stenberg, founder and lead developer of curl [(talk)](https://fosdem.org/2026/schedule/event/B7YKQ7-oss-in-spite-of-ai/).
- Both highlighted that LLMs can help malicious actors find and exploit vulnerabilities in open-source code, and thus open-source will become more vulnerable to supply-chain attacks.
- Stenberg further detailed how LLMs brings out the worst and best at the same time. On one hand, the curl project is bombarded by AI-generated security reports. This has led curl to stop their bug bounty. On the other hand, they use LLMs selectively to find security issues and review code. 

Several talks in the security devroom addressed the same problem.


### Updated governance model for open-weight LLMs
- A [talk](https://fosdem.org/2026/schedule/event/VGMUYA-the-open-weight-dilemma/) about LLMs and cyber risks argued for an updated governance model for open source (and maybe open weight) LLMs.
- While closed LLMs are easily controllable, safeguards in open models can easily be finetuned away. 
- Therefore, open LLMs cannot be regulated like an API, and closed LLMs may even have an advantage because they are easier to regulate---a "mitigation gap".
- The solution proposed is to define fine-tuned models as "substantial modification", and shift the liability burden from the issuer of the original model to the fine-tuner.

### Auditing and securing supply chains
- The Open Source Technology Improvement Fund (OSTIF) presented their work on providing security audits to open source software [(talk)](https://fosdem.org/2026/schedule/event/Z7D3MW-security_audits_and_security/).
- [AboutCode](https://aboutcode.org/) presented their tool to detect LLM-generated code [(talk)](https://fosdem.org/2026/schedule/event/XGLP7J-ai-generated-code/). If I understood correctly, the tool finds parts of a codebase that have been regurgitated from another source, and can pinpoint to the source. One challenge was that LLMs often create similar control flow, but different variable names from the original. In their `scancode.io` [tool](https://github.com/aboutcode-org/scancode.io/), they solve this problem with code stemming, a method also used by treesitter.

## Data, Search and LLMs

### Vector search
- In a RAG pipeline, the hard part is data engineering: one has to understand the data and the context [(talk)](https://fosdem.org/2026/schedule/event/DHTAXQ-prevent-ai-garbage/). For instance, the chunking strategy is crucial for the retrieved the results.
- Weaviate [presented and demoed](https://fosdem.org/2026/schedule/event/3AWMQZ-multi-vector-embeddings-revolution-or-evolution/) multi-vector retrieval. This is particularly useful for search on pdfs that include images. Their [tool](https://github.com/weaviate/weaviate) implements the MUVERA algorithm [(paper)](https://arxiv.org/abs/2405.19504).


### Speeding up LLM inference
- The vLLM project [explained](https://fosdem.org/2026/schedule/speaker/eldar_kurtic/) how they speed up LLM inference with quantization and speculative decoding. 
- Quantization a compresses the network weights into buckets. This leads to a smaller footprint in memory and to faster transfer of the weights from the GPU's high-bandwidth memory to the SRAM and Tensor cores that do the matrix multiplications. 
- Their benchmarks show that the ideal strategy (4-bit integer quantization vs. 8-bit integer quantization vs. no quantization) depends on the number of queries per second.
- For speculative decoding, one trains a light-weight "speculator" model that generates tokens at inference time, and the main model approves or rejects the generated tokens.

## Machine learning, performance, and observability

### Performance engineering
- Two talks discussed best practices for performance engineering: To reliably capture performance regressions, benchmarks should be repeatable and representative, and setting them up for this requires some thought. Challenges include isolating the benchmark environments and avoiding too many false positives.
- The first [outlined](https://fosdem.org/2026/schedule/event/8AS3XD-how-to-reliably-measure-software-performance/) a statistical testing approach to increase the signal-to-noise ratio, and to decide when to reject the null hypothesis of no performance regression. Further, running benchmarks in the cloud poses challenges, and they recommend avoiding virtualized environments. The slides of the talk are [here](https://github.com/igoragoli/fosdem-2026-software-performance).
- The second [focused](https://fosdem.org/2026/schedule/event/YNB7KR-continuous-perf-engineering/) on change point detection. I also liked the idea of using canaries to track the performance of the benchmark infrastructure itself---you want to know when the problem is with the infrastructure and when it is with your software.
- Both argued for continuous performance monitoring and presented some tools for this. [nyrkio](https://nyrkio.com/frontpage) provides CI runners for change point detection; the runners are not free but according to the provider, they are of better quality than other runners (such as the [github-action-benchmark](https://github.com/benchmark-action/github-action-benchmark)). [hyperfine](https://github.com/sharkdp/hyperfine) is a command-line benchmarking tool.


### Performance monitoring of deep learning workloads on HPC

Two talks addressed performance monitoring for deep learning workloads on HPC systems.
- The first [highlighted](https://fosdem.org/2026/schedule/event/BBYZLU-gpu-performance-monitoring/) the shortcomings of `nvidia-smi` compared to `dcgmi`. In short, the former only tells us *whether* the GPUs are busy, but not *how efficiently* they are being used (tensor cores, streaming multiprocessors, DRAM). One example was that using 32-bit and 16-bit precision on a H100 shows the same utilization on `nvidia-smi`, even though FP32 is less efficient because H100s do not support tensor core computations with this precision.
- The talk suggested that running `dcgmi` incurs no overhead because it is reading data that is already being tracked. I found useful docs from SURF [here](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/92668151/dcgmi+dmon), and they are more cautious, mentioning that `dcgmi` may slightly slow down your code. I guess one has to test and see it for themselves. The NVIDIA docs for `dcgmi` are [here](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html#profiling-metrics)  
- The second [presented](https://fosdem.org/2026/schedule/event/FYLDFE-observability_for_ai_workloads_on_hpc_beyond_gpu_utilization_metrics/) presented an open-source observability dashboard for deep learning on HPC. It covers hardware, workload, and model health (such as gradient tracking). The [tool](https://github.com/erythix4/HPCOBS) was just released during the conference. I'm curious to see how it evolves and how it compares to other tools.

