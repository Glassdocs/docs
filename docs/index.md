# What is Glassdocs

Glassdocs turns a Markdown GitHub repository into a published, access-gated knowledge base — and adds an AI chat layer that lets readers ask questions about any page and propose edits straight back to the source repo. Your content lives in **your** GitHub, your site runs on **your** Cloudflare, and Glassdocs orchestrates the rest without ever storing your documents.

## The transparency layer for AI-authored work

Glassdocs began as an answer to a modern problem: AI agents now write a lot of code, and the humans responsible for it need a way to read, approve, and steer that work. Glassdocs makes documentation the interface for that loop:

1. **Agents write the docs** — every change lands with a Markdown page explaining what was built, why, and where.
2. **You read and approve** — the docs are the diff you review. Edit what is wrong, accept what is right.
3. **Agents read on the next prompt** — the approved docs become the contract. Work that contradicts them is flagged.

The same machinery works just as well for human-authored docs: project knowledge bases, client-facing documentation, internal handbooks — anything you can express as Markdown in a repo.

## Who it's for

- **Teams shipping with AI agents** who want AI-written documentation they can actually review and trust.
- **Consultancies and agencies** publishing per-client knowledge bases that must stay private — gated to staff and, selectively, to each client.
- **Any organization** that wants docs-as-code (Markdown in Git, CI-published) without building and securing the pipeline themselves.

## The three pillars

### 1. Markdown knowledge bases

A Glassdocs KB is deliberately simple: a GitHub repository containing

- `docs/*.md` — your pages, and
- `mkdocs.yml` — navigation and theme.

That's it. The site is built by **Zensical**, the MkDocs successor from the Material for MkDocs team, which reads your `mkdocs.yml` unchanged. You start from a ready-made template repo and get a polished, searchable site out of the box. See [Authoring](authoring.md) for how to write pages.

### 2. Secure publishing — in your accounts, not ours

Glassdocs is a **zero-data control plane**. Publishing runs in **your own GitHub Actions**, with **your own Cloudflare credentials**, deploying to **your own Cloudflare Pages** project behind **Cloudflare Access**:

- **Nothing is public by default.** Access is fail-closed: a KB with no access rules deploys locked to nobody, and every deploy verifies the gate is actually up — rolling itself back rather than leaving content exposed.
- **You keep custody.** Glassdocs never creates or deletes repos, never stores your Cloudflare token (it is sealed into your repo as an Actions secret), and never stores your document content, prompts, or AI responses.
- **Revocation is yours.** Uninstall the Glassdocs GitHub App and the grant is gone.

Details in [Publishing](publishing.md), [Hosting](hosting.md), and the [Security model](security.md).

### 3. Docs chat and the edit flow

The Glassdocs browser extension (Docs Chat) attaches an AI side panel to any published KB page. Readers can:

- **Ask** — chat about the page they're reading, with the page as context.
- **Edit** — describe a change in plain language; the AI drafts the edit, shows a preview, and on approval the change is committed back to the source repo via GitHub, so the site republishes through the normal pipeline.

A site opts in with a single meta tag naming its source repository — no SDK, no embedded script. AI calls go through the managed backend at [app.glassdocs.site](https://app.glassdocs.site), which supports a free tier or your organization's own AI provider key, and meters token counts only. See the [Extension guide](extension.md) and [How it works](how-it-works.md).

!!! note "Your docs never leave your accounts"
    This is the product's core design decision, not a footnote. Content lives in your GitHub repo; the published site lives in your Cloudflare account; access policy is derived from variables in your repo. The Glassdocs backend keeps identity, an encrypted org AI key if you bring one, usage counters, and an audit log — and nothing else. See [Security](security.md).

## What Glassdocs is not

- **Not a wiki or a hosted CMS.** There is no Glassdocs database of your pages — GitHub is the source of truth.
- **Not a build service.** Your CI builds and deploys; Glassdocs configures and orchestrates it.
- **Not open source.** Glassdocs is a commercial product by [Rocket Lab](https://www.rocketlab.com.au).

## Where to go next

- [Getting started](getting-started.md) — stand up your first KB end to end.
- [How it works](how-it-works.md) — the architecture, for the technically curious.
- [Admin console](admin.md) — managing KBs, access, and deploys at [app.glassdocs.site](https://app.glassdocs.site).
- [Enterprise](enterprise.md) — org-wide rollout, BYO AI keys, and policy-managed extension install.
- [API](api.md) — programmatic access to the control plane.
