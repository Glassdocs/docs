# Glassdocs KB Template (Zensical)

A **"Use this template"** repo for new [Glassdocs](https://glassdocs.site)
knowledge bases. Pure **Markdown**, built with
**[Zensical](https://zensical.org/)** (the MIT-licensed MkDocs successor),
diagrams as **Mermaid**, **private by default**.

Glassdocs never creates repos on your behalf — **you** create your KB from this
template, then Glassdocs configures and publishes it.

## Create a new KB

1. **Create the repo** from this template: GitHub → **Use this template** →
   your org, private.
2. **Install the Glassdocs app** on the new repo (if it isn't already installed
   org-wide), so Glassdocs can configure and deploy it.
3. **Set it up in Glassdocs** — open your [admin dashboard](https://glassdocs.site),
   pick your org, and under **Knowledge bases → Set up a KB** enter the repo name
   and a Cloudflare Pages project name (e.g. `acme-handbook`). Glassdocs sets the
   `CF_PAGES_PROJECT` variable and triggers the first deploy.
   - Alternatively, set the repo variable **`CF_PAGES_PROJECT`** yourself and push.
4. **Customise** `mkdocs.yml` (`site_name`, `nav`) and replace `docs/index.md`.

The publisher **creates the Cloudflare Pages project + Access app on first
deploy**, deploys to `<project>.pages.dev`, and **verifies the site is gated —
rolling the deploy back if it is ever publicly reachable.** No `wrangler`
project setup, no shared secrets in this repo.

## Access

Access is **Cloudflare Access (SSO)**, enforced by the Glassdocs publisher at the
Cloudflare platform — not by any code in this repo. Grant access via repo
variables:

| Variable | Grants |
| --- | --- |
| `EMAIL_DOMAIN` | everyone at your staff email domain (e.g. `acme.com`) |
| `CLIENT_DOMAIN` | one client email domain |
| `CLIENT_EMAILS` | specific client emails (comma-separated) |

**Fail-closed:** with none of these set, the KB deploys locked rather than
public. Manage client access from the Glassdocs admin dashboard.

## Local preview

```bash
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
zensical serve   # http://127.0.0.1:8000
zensical build   # output to ./site
```

## Authoring

- All content is Markdown in [`docs/`](docs/). Add a page → add it to `nav:` in `mkdocs.yml`.
- Diagrams are **Mermaid** code fences (rendered to vector SVG).
- Component styles (cards, grids, tags) live in
  [`docs/stylesheets/extra.css`](docs/stylesheets/extra.css).
- See [`docs/getting-started.md`](docs/getting-started.md) for the conventions.

## Stack

| Concern | Tool |
| --- | --- |
| Generator | Zensical (MkDocs successor, MIT) |
| Config | `mkdocs.yml` (read natively by Zensical) |
| Diagrams | Mermaid → vector SVG |
| Hosting | Cloudflare Pages, private |
| Access | Cloudflare Access (SSO), enforced by the Glassdocs publisher |
| CI/CD | Glassdocs reusable `deploy-pages.yml` (pinned `@v1`) |
