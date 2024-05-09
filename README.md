# Minimalist Hugo Template for Academic Websites

This repository contains a [Hugo](https://github.com/gohugoio/hugo) template to create a personal academic website. The template uses the [PaperMod theme](https://github.com/adityatelange/hugo-PaperMod) but modifies it in various ways to be more minimalist and more adapted to academic websites. The website is hosted on [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages).

## Documentation

The template is forked from Pascal Michaillat; the documentation is [here](https://pascalmichaillat.org/d5/). 

## Illustration

The website produced by the template can be viewed at https://pascalmichaillat.org/hugo-website/.

## Installation

### On your local machine

+ Clone the repository to your local machine
+ Install [Hugo](https://gohugo.io/installation/). On a Mac, this is easily done with [Homebrew](https://brew.sh): simply run `brew install hugo` in the terminal.
+ Since the website is hosted on GitHub Pages, it is convenient to install [GitHub Desktop](https://desktop.github.com). The website can conveniently be updated from your local machine via GitHub Desktop without going to GitHub.
+ Update the `baseURL` parameter in `config.yml` with the website URL that you plan to use. By default the ULR is `https://username.github.io`.

### On your GitHub account

+ The first time that you push your repository to GitHub, you need to allow GitHub Actions and GitHub Pages so the website can be built and deployed to GitHub Pages.
+ The first step is to [ask GitHub to publish the website with a GitHub Action](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow).  GitHub offers a ready-made action to publish a Hugo website, called `Deploy Hugo site to Pages`. This action must be enabled in the [Pages Settings](https://github.com/pmichaillat/hugo-website/settings/pages) of your GitHub repository. You can view the workflow triggered by the action in the `.github/workflows/hugo.yml` file.
+ Once the GitHub Actions are enabled, GitHub will build and publish the website as soon as the repository is updated. 

## Usage

### Development

Navigate to the website directory and run `hugo server` in the terminal. The command builds the website on your machine and makes it available at http://localhost:1313. You can modify the content of the repository and develop your website entirely on your local machine.

### Compilation

Once your website is ready to be made public, run `hugo` in the terminal from the website directory. When you run the `hugo` command, Hugo processes your content, templates, and other project files and generates a static website. The resulting output is placed in the `public` folder.

### Deployment

With GitHub Desktop, commit the changes and push them to the website repository on GitHub. Then, [GitHub Actions](https://github.com/pmichaillat/hugo-website/actions/workflows/hugo.yml) build the website and deploy it to [GitHub Pages](https://github.com/pmichaillat/hugo-website/deployments/github-pages).

## Performance

Despite the modifications to the PaperMod theme, the website continues to perform well on mobile and desktop devices. Here is an overview of the mobile performance from [PageSpeed Insights](https://pagespeed.web.dev/):

<img width="470" alt="mobile" src="https://github.com/pmichaillat/hugo-website/assets/85443660/1488df3e-19bb-4f9f-8a86-11f361414d92">

And here is an overview of the desktop performance:

<img width="453" alt="desktop" src="https://github.com/pmichaillat/pmichaillat.github.io/assets/85443660/eff134d2-6097-4bc2-bfd7-4f5c18571789">

## Software

The website was built with Hugo v0.124.1 on an Apple Silicon Mac running macOS Sonoma 14.4.1.

## License

The content of this repository is licensed under the terms of the MIT License.
