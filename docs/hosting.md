# Managed hosting

Managed hosting means Glassdocs builds and serves your KB on Cloudflare infrastructure it operates, so you never touch a Cloudflare account: you keep writing Markdown in your GitHub repo, and Glassdocs handles the rest. This page explains what hosting looks like today, honestly: the fully supported path is client-hosted on your own Cloudflare (with a guided dashboard that makes it a five-minute job), while the fully managed offering is built on publisher machinery that ships today but is not yet a self-serve product.

## Two hosting models

| | Client-hosted (available now) | Managed (in development) |
| --- | --- | --- |
| Content lives in | Your GitHub | Your GitHub |
| Build runs in | Your GitHub Actions | Glassdocs-operated CI |
| Site served from | Your Cloudflare account | Glassdocs-operated Cloudflare |
| Cloudflare account needed | Yes (free tier is fine) | No |
| Setup | [deploy.yml + variables](publishing.md), or the guided dashboard below | Planned as a managed onboarding |

In both models the source of truth is the same: a Markdown repo created from the KB template. Moving between models is a deployment change, not a content migration.

## What's available today: your Cloudflare, guided setup

The live hosting product is a zero-data control plane over the client-hosted path. Glassdocs configures your repo and deploys from your GitHub Actions to your Cloudflare. It never creates or deletes repos, never stores your content, and never holds your Cloudflare token: the token is sealed into your repo as an Actions secret and used only by your own CI. Your docs never leave your GitHub and your Cloudflare.

Setup from the [admin dashboard](admin.md) takes about five minutes:

1. **Install the Glassdocs GitHub App** on your org. It asks for a least-privilege footprint: read/write repo contents (scaffolding and editor commits), Actions variables, workflows, secrets (sealing the Cloudflare token), and pull requests (for protected-branch PRs). It never creates or deletes repos, and an owner approves.
2. **Create your repo from the KB template** at [github.com/Glassdocs/kb-template/generate](https://github.com/Glassdocs/kb-template/generate), or point setup at any existing repo: the wizard's "Add Glassdocs KB files" option scaffolds the KB files into it, template not required. Glassdocs never creates repos for you.
3. **Pick the repo in the dashboard** and name the Cloudflare Pages project. If the KB already has a live site, use that project's exact existing name; a new name spins up a second, separate site and orphans the real one.
4. **Connect Cloudflare with one paste.** A pre-scoped token link selects exactly the two permission groups the publisher needs. Create the token, paste it, press Connect. Glassdocs verifies it and seals it into the repo; the token is never stored by Glassdocs.
5. **Set who can read it.** Set a staff domain for your team, plus optional client access. Access is fail-closed: leave every field blank and the site deploys locked to nobody, not "staff-only". The Access panel is also how you recover a locked-out KB later. Docs meant for the whole world can instead opt in to a public, ungated KB right in the wizard — see [public mode](publishing.md#public-mode).
6. **Press "Set up & deploy"** and watch live status in the dashboard. On the first run, Cloudflare Access is created to gate the site, and the deploy only reports success once an unauthenticated request is provably redirected to the Access login. See [Publishing](publishing.md) for the full verify-or-rollback pipeline.

!!! tip "Pick one Cloudflare account"
    Choose the single Cloudflare account you want all your KBs to live in and connect tokens from that account. Mixing accounts across KBs is the most common source of confusion. If a token can reach more than one account, the dashboard asks which one to deploy to.

!!! warning "Don't use \"Connect to Git\" on the Pages project"
    Glassdocs publishes by direct upload from CI. A Pages project wired to a Git repo via Cloudflare's "Connect to Git" can't accept these deploys. Let Glassdocs create and drive the project, and leave its Git integration off.

A couple of Cloudflare behaviors worth knowing: `pages.dev` subdomains are globally unique across all of Cloudflare, so a taken name gets you a suffixed URL (still gated, still working; the dashboard links you to the real URL). And if you delete a Pages project and recreate one with the same name, Cloudflare enforces a short name-reuse cooldown before the name is available again.

## How managed hosting works

The publisher already contains the mechanism managed hosting is built on. Normally the reusable workflow builds the repo that calls it. It also accepts a `source-repo` input (with an optional `source-ref`, and a `SOURCE_TOKEN` secret granting read access), which tells it to build a *different* repo: your KB repo, checked out and built from a workflow running on Glassdocs infrastructure instead of in your own Actions.

Everything downstream is the same secure-by-default pipeline described in [Publishing](publishing.md): Zensical build, compliance lint, Cloudflare Access gating, fail-closed access grants, post-deploy verification with rollback. The difference is who owns the CI minutes and the Cloudflare account.

!!! info "Status: not yet generally available"
    The `source-repo` build path ships in the publisher today, but managed hosting as a product (sign-up, plans, a free trial, Glassdocs-operated serving for your KB) is still being built. Until it launches, the supported paths are client-hosted: the plain [deploy.yml](publishing.md) or the guided dashboard flow above. If managed hosting is what you're waiting for, [contact us](mailto:hello@rocketlab.com.au).

## Choosing a model

- **Choose client-hosted** if your docs must never leave infrastructure you own. The zero-data property is absolute: Glassdocs orchestrates, but the repo, the build, the published site, the Access policy, and the API token all stay in your accounts.
- **Watch for managed** if you want zero Cloudflare setup and are comfortable with Glassdocs-operated infrastructure reading your repo and serving your site.

Larger organizations weighing the two should also read [Enterprise](enterprise.md) and [Security](security.md).
