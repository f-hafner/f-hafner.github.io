---
# Leave the homepage title empty to use the site title
title:
date: 2022-10-24
type: landing

sections:
  - block: about.avatar
    id: about
    content:
      # Choose a user profile to display (a folder name within `content/authors/`)
      username: admin
      # Override your bio text from `authors/admin/_index.md`?
      text:
  - block: experience
    content:
      title: Experience
      # Date format for experience
      #   Refer to https://wowchemy.com/docs/customization/#date-format
      date_format: Jan 2006
      # Experiences.
      #   Add/remove as many `experience` items below as you like.
      #   Required fields are `title`, `company`, and `date_start`.
      #   Leave `date_end` empty if it's your current employer.
      #   Begin multi-line descriptions with YAML's `|2-` multi-line prefix.
      items:
        - title: Research Software Engineer
          company: Netherlands eScience Center
          company_url: ''
          # company_logo: org-gc
          location: Amsterdam
          date_start: '2022-11-15'
          date_end: ''
          description: |2-
              Contributing to software and research:

              * REL -- Radboud entity linker. [Project](https://research-software-directory.org/projects/rel20).
              * Privacy-preserving synthetic data and machine learning. [Project](https://research-software-directory.org/projects/gans).
              * Labor market careers of PhD graduates. [Project](https://research-software-directory.org/projects/from-the-ivory-tower-to-public-or-private-power).
        - title: Postdoctoral Fellow
          company: Aalto University
          company_url: ''
          # company_logo: org-x
          location: Helsinki
          date_start: '2020-09-01'
          date_end: '2022-10-31'
          description: |2-
              * Data warehousing, data integration, entity disambiguation
              * Statistical modeling & causal inference
              * Design & teach graduate course in labor economics
        - title: PhD in Economics
          company: Universitat Pompeu Fabra
          location: Barcelona
          date_start: '2014-09-01'
          date_end: '2020-08-31'
          description: |2-
            Labor economics

              * Statistical modeling & causal inference
              * Numerical optimization
    design:
      columns: '2'
  # - block: accomplishments
  #   content:
  #     # Note: `&shy;` is used to add a 'soft' hyphen in a long heading.
  #     title: 'Accomplish&shy;ments'
  #     subtitle:
  #     # Date format: https://wowchemy.com/docs/customization/#date-format
  #     date_format: Jan 2006
  #     # Accomplishments.
  #     #   Add/remove as many `item` blocks below as you like.
  #     #   `title`, `organization`, and `date_start` are the required parameters.
  #     #   Leave other parameters empty if not required.
  #     #   Begin multi-line descriptions with YAML's `|2-` multi-line prefix.
  #     items:
  #       - certificate_url: https://www.coursera.org
  #         date_end: ''
  #         date_start: '2021-01-25'
  #         description: ''
  #         organization: Coursera
  #         organization_url: https://www.coursera.org
  #         title: Neural Networks and Deep Learning
  #         url: ''
  #       - certificate_url: https://www.edx.org
  #         date_end: ''
  #         date_start: '2021-01-01'
  #         description: Formulated informed blockchain models, hypotheses, and use cases.
  #         organization: edX
  #         organization_url: https://www.edx.org
  #         title: Blockchain Fundamentals
  #         url: https://www.edx.org/professional-certificate/uc-berkeleyx-blockchain-fundamentals
  #       - certificate_url: https://www.datacamp.com
  #         date_end: '2020-12-21'
  #         date_start: '2020-07-01'
  #         description: ''
  #         organization: DataCamp
  #         organization_url: https://www.datacamp.com
  #         title: 'Object-Oriented Programming in R'
  #         url: ''
  #   design:
  #     columns: '2'
  - block: collection
    id: research
    content:
      title: Research
      # text: |-
      #   {{% callout note %}}
      #   Quickly discover relevant content by [filtering publications](./publication/).
      #   {{% /callout %}}
      filters:
        folders:
          - publication
    design:
      columns: '2'
      view: citation
  - block: markdown
    id: code
    content:
      title: Code
      text: |2-
        **[sirup: Simple IP rotation with python](https://github.com/ivory-tower-private-power/sirup)**
        - A wrapper around the `openvpn` command line interface to connect to VPN servers and rotate the IP address in python programs.

        I also maintain the following repositories for bibliometric research on the careers for PhD graduates in the United States:

        **[mag_sample (proper name coming soon)](https://github.com/f-hafner/mag_sample)**
        - Load and clean Microsoft Academic Graph
        - Create additional tables and integrate different data sources
        - Use active learning to link records in MAG to other data sources
        - Run some quality checks on the data

        **[magutils](https://github.com/f-hafner/magutils)**
        - R package that eases querying the linked data created above.
  - block: markdown
    id: teaching
    content:
      title: Teaching
      text: |2-
        **Carpentries instructor certification (2023)**

        **Digital skills workshops at the eScience Center (2023)**
        - *Machine learning in Python with scikit-learn* (role: supporting instructor)
        - *Parallel Python*, *Introduction to deep learning*, *R packaging*, *Intermediate Research Software Development with Python* (role: helper)

        **Labor economics II, Aalto University (2021, 2022)**
        - [Syllabus](uploads/labor2-syllabus.pdf)
        - Role: Main instructor
  - block: contact
    id: contact
    content:
      title: Contact
      subtitle:
      email: f.hafner@esciencecenter.nl
      address:
        street: Science Park 402
        city: Amsterdam
        postcode: '1098 XH'
        country: Netherlands
        country_code: NL
      # Automatically link email and phone or display as text?
      # autolink: true
      # # Email form provider
      # form:
      #   provider: netlify
      #   formspree:
      #     id:
      #   netlify:
      #     # Enable CAPTCHA challenge to reduce spam?
      #     captcha: false
    design:
      columns: '2'
---
