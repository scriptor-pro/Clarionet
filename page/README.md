# Clarionet GitHub Pages

This directory contains the GitHub Pages Jekyll site for Clarionet.

## Structure

```
page/
├── _config.yml          # Jekyll configuration
├── _layouts/            # Page templates
├── _includes/           # Reusable components
├── assets/              # Images and stylesheets
│   ├── css/
│   └── screenshots/
└── index.md             # Main landing page
```

## Local Development

Install Jekyll dependencies:

```bash
cd page
gem install jekyll jekyll-seo-tag jekyll-sitemap
```

Run local server:

```bash
cd page
jekyll serve
```

Visit http://localhost:4000 to preview.

## Deployment

The site is automatically deployed to GitHub Pages when pushing to the `page` branch.

GitHub Actions workflow: `.github/workflows/pages.yml`

## Features

- Bilingual support (French/English)
- Language switcher with localStorage persistence
- Responsive design
- Dark theme matching app color scheme
- Multiple installation methods
- Keyboard shortcuts table
- GitHub integration
