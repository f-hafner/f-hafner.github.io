---
title: "How we won the Amsterdam Policy Hackathon 2025 and what I learned"
date: 2025-09-18
url: /aph-2025/
author: "Flavio Hafner"
description: "The event, our work, and some reflections."
tags: ["hacking", "policy-making", "causal-inference"]
summary: "I participated in the first Amsterdam Policy Hackathon. Here's how we won our challenge, and what I learned on the way."
showToc: false 
disableAnchoredHeadings: false

---

Last weekend I participated in the first edition of the [Amsterdam Policy Hackathon](https://amsterdampolicyhackathon.org/). 80 participants, grouped into teams of 3-5, worked on one of 4 challenges provided by challenge partners:
1. *Amsterdam Institute for Advanced Metropolitan Solutions (AMS)*: Making biodiversity matter through data-informed policy.
2. *PAVA.ai*: How can we demonstrate and communicate the value of preventive healthcare technologies like PAVA?
3. *Province Gelderland*: Streamlining the construction permit process and using AI to scan ecological reports and ensure fair, transparent evaluations.
4. *City of Amsterdam*: Powering Amsterdam's Future---supporting the residents in the energy transition.

### Winning the PAVA challenge

We argued that improved remote monitoring technologies such as PAVA's system enhance not only the alarm quality (fewer false positives), but also enhance the context of nurses, which improves their decision-making. Through a causal chain, this improves outcomes such as residents' sleep quality and sleep debt. Using data from PAVA, we quantified some of these effects. Our framework is human-centered and modular---it can be applied to different technologies and different downstream outcomes.

### Lessons learned

*A team with diverse backgrounds is key*

We only learned the details of the challenge (such as data to work with) after forming the team. With backgrounds in NLP, human-centric AI, public policy and economics, our team was well "diversified" for either a more or less technical case.

*Causal inference was useful, but in an unexpected way*

The challenge asked us to "make visible the unseen preventive effects". At first, I considered this a problem of estimating causal effects ex-post with observational data---however, the only data we were given were some comparisons of using different remote monitoring technologies. Nothing that one can run regressions on.

Still, thinking in terms of causal effects helped us link a predictive system's technical efficiency---such as metrics of accuracy---to its effects on people: implicitly, we used an [instrumental variable](https://en.wikipedia.org/wiki/Instrumental_variables_estimation) approach to solve the challenge.

*Policy hackathons---A use-case for Trusted Research Environments?*

I had signed up to the hackathon because I was excited about hacking software for public policy. In the words of the organizers:
> A "Policy Hackathon" leverages technical and soft skills to tackle all kinds of societal/policy challenges.


While I did expect interdisciplinary cases, I do think they could have been a bit more technical. A good fraction of other participants did also have technical backgrounds, and at least some had expected the challenges also to have some more technical aspects. 

Gelderland's challenge probably had the most potential for technical exploration, allowing teams to use NLP and large language models to streamline the permit granting process---however, Gelderland could only share a few examples of permit applications, and participants had to sign non-disclosure agreements to protect personal information contained in the samples.

That's why I have an idea for future challenges: How about using a [Trusted Research Environment](https://lifebit.ai/blog/what-is-trusted-research-environment/) to share data with challenge teams? This way, participants could get access to more detailed data without having them on their personal laptops. And more challenge partners could benefit from the full pool of expertise of hackathon participants.

Surely the organizational overhead would increase, and non-disclosure agreements would still be necessary, but I think this could be exciting. In the Netherlands, my colleagues at [ODISSEI](https://odissei-data.nl/) and [SURF](https://www.surf.nl/) provide this service via [SANE: Secure Analysis Environment](https://odissei-data.nl/facility/secure-analysis-environment-sane/). I'd be happy to explore this option for future editions of the hackathon.

### Until next year

I think this hackathon is a great initiative, and I'm looking forward to seeing it develop in the coming years!


---
