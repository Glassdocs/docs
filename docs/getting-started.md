# Getting started

This is the end-to-end guide for a team adopting Glassdocs: create a knowledge base (KB) repo from the template, connect it in the admin console, deploy it to your own Cloudflare account behind an access gate, and pick up the browser extension for chat and edits. Glassdocs is a zero-data control plane — it orchestrates your setup, but your Markdown lives in your GitHub repo, your site is published to your Cloudflare Pages by your own GitHub Actions, and Glassdocs never creates or deletes repos and never stores your content.

## Before you start

You need two things:

1. **A GitHub organization** — your KB repos live here, and this is where you install the Glassdocs GitHub App.
2. **A Cloudflare account** — your published sites live here as Cloudflare Pages projects, gated by Cloudflare Access.

!!! warning "Pick ONE Cloudflare account for all your KBs"
    If you connect different KBs to different Cloudflare accounts, you'll eventually go looking for a site in one account and not find it because it deployed to another. Decide up front which account owns your KBs and stick to it. (See step 5 and [Troubleshooting](#troubleshooting).)

## Step 1 — Install the Glassdocs GitHub App on your org

Open the [Glassdocs admin](https://app.glassdocs.site), sign in with GitHub, and select your organization. If the app isn't installed yet, you'll be prompted to **Install the Glassdocs app on GitHub**.

The app asks for **least-privilege** access — it can read and write repo contents (for scaffolding KB files and committing editor changes), Actions variables, workflows, secrets (sealing your Cloudflare token), and pull requests (for protected branches). It **never creates or deletes repos**, and never stores your content. On GitHub, pick your org, choose which repos to grant, and approve. Then come back to the admin and click **recheck**.

The installation record is the only thing Glassdocs keeps. The grant is yours to revoke at any time by uninstalling the app.

## Step 2 — Create a KB repo from the template

Glassdocs configures repos; it doesn't create them. Create your KB repo yourself from the Glassdocs KB template:

**<https://github.com/Glassdocs/kb-template/generate>**

Create it **into your org**. A KB is just Markdown:

- `docs/*.md` — your pages.
- `mkdocs.yml` — navigation and theme.

These are built into a site by **Zensical** (the MkDocs-successor engine). The template also ships the deploy workflow that publishes the site. See [Authoring](authoring.md) for writing conventions.

!!! note
    The repo must be one the Glassdocs app can access. If you granted the app only specific repos in step 1, either create the new repo under that grant or grant the app the new repo (there's a **Grant the app another repo** link in the admin).

## Step 3 — Open the admin and select the repo

Back in the [Glassdocs admin](https://app.glassdocs.site), with your org selected, find the **Knowledge bases** card and click **＋ Set up a KB**.

- **Repo** — pick the repo you just created. Only repos the app can access appear here; if yours is missing, click **Reload** (or grant the app the repo first).
- **Cloudflare Pages project** — choose a project name. This becomes your site URL: `<name>.pages.dev`. The admin suggests one from the repo name; you can change it. **If this KB already has a live Cloudflare Pages site, enter that project's exact name** — a new name creates a *second, separate* site and orphans the real one. After you connect Cloudflare (step 4), the admin lists the account's existing projects and warns if the name you chose isn't one of them.

## Step 4 — Connect Cloudflare

In the setup form, use the **Connect Cloudflare** section:

1. Click **Create token on Cloudflare**. The link pre-selects **exactly** the two permissions Glassdocs needs — **Cloudflare Pages: Edit** and **Access: Apps and Policies: Edit** — so you don't have to pick any permissions yourself. Before clicking Create, confirm both permission rows show **Edit** — a read-only token connects but can't deploy. Create the token.
2. Paste the token into the field and press **Connect** (for the selected repo).

Glassdocs verifies the token and **seals it into the repo as an Actions secret**. The token is **never stored by Glassdocs** — from here on, only your own GitHub Actions use it.

Two things to get right:

- **Use the ONE Cloudflare account you chose up front.** If your token can access multiple accounts, the admin will ask which one to deploy to — pick the same account you use for your other KBs. Mixing accounts is the most common cause of "I can't find my site."
- **Do NOT use Cloudflare's "Connect to Git".** Glassdocs publishes by **direct upload** from GitHub Actions. A Pages project wired to Git won't accept these deploys.

## Step 5 — Set who can read the site

Still in the setup form (and all editable later per KB):

- **Staff domain** *(recommended)* — your own organization's email domain (e.g. `yourcompany.com`). Grants your whole team SSO read access. This is what makes a KB "staff-only".
- **Client domain** *(optional)* — grants read access to everyone at an external email domain (e.g. `client.com`).
- **Client emails** *(optional)* — a comma-separated list of individual addresses.

Access is **fail-closed**, and there is **no default** — an access field left blank grants no one through that channel. In particular, leaving **every** field blank deploys the site **locked to nobody** (not "staff-only"). To let your team in, set the **Staff domain**. Nothing is ever public by default.

You can change access on an existing KB anytime via **Access** on the KB — the panel loads the KB's current live values, and saving redeploys so the new policy takes effect. That's also how you recover a locked-out KB: open **Access**, set the **Staff domain**, and save. (A malformed domain, e.g. a pasted URL, is rejected with an error rather than silently clearing the field.)

## Step 6 — Set up & deploy

Click **Set up & deploy**. Glassdocs configures the existing repo (writing the Pages-project and access variables) and dispatches the first deploy. Two variations: if Cloudflare isn't connected yet, the dispatch is skipped with a warning until you connect; and if the default branch is protected, Glassdocs opens a setup PR instead — merging it triggers the first deploy (the KB row shows "setup PR #N — merge to publish"). From here everything runs in **your** GitHub Actions:

- The workflow **builds your Markdown KB with Zensical** into a site.
- It **deploys that site to your Cloudflare Pages** project.
- It **creates and reconciles a Cloudflare Access policy** so the site is gated — and it does this **fail-closed** (if the Access app can't be created, it aborts *before* publishing any content).

If your repo was created from the template it already has everything it needs. (For a repo that started empty, leave **Add Glassdocs KB files** checked so the setup commits the deploy workflow, `mkdocs.yml`, and `docs/`.)

Watch the deploy status live in the KB list in the admin — it shows the real GitHub Actions run status (queued / running / deployed / failed) and links to the run logs. More on the pipeline in [Publishing](publishing.md).

## Step 7 — Verify the site is gated

Once the deploy reports **deployed**, confirm the gate is actually up: open your `<name>.pages.dev` URL **signed out** (or in a private window). You should be **redirected to the Cloudflare Access login**, not shown the KB. If you see content without signing in, the site is not gated — stop and check the deploy.

You can also check from a terminal — a gated site answers with a redirect, never a 200:

```bash
curl -s -o /dev/null -w "%{http_code}" https://<name>.pages.dev
```

For the full security model behind the gate, see [Security](security.md).

## Step 8 — Install the browser extension

With the site live, install the **Glassdocs browser extension (Docs Chat)** to chat about pages and make edits without leaving the site. The extension recognizes any published page that declares its source repo via a meta tag (see [How it works](how-it-works.md#how-a-site-opts-in-the-source-repo-meta-tag)) and adds a side panel where you can:

- **Ask** questions about the page you're reading.
- **Edit** the page in plain language — the change is committed back to your repo via GitHub, and the site republishes automatically.

See the [Extension guide](extension.md) for installation and sign-in, and [Enterprise](enterprise.md) for rolling the extension out org-wide by policy.

## Troubleshooting

**Where's my deploy status?**
The KB list in the admin shows each KB's live deploy status (queued, running, deployed, failed) pulled straight from GitHub Actions, with a link to the run. A failed run also names the step that broke, so you can jump to the logs. Use **Redeploy** on a KB to trigger a fresh deploy.

**My site URL has a random suffix.**
`pages.dev` subdomains are **globally unique across all of Cloudflare**. If the project name you chose is already taken, Cloudflare hands you a suffixed URL (e.g. `myname-a1b2.pages.dev`). That's fine — the suffixed URL still works and is still gated. Just use whatever URL the deploy/Cloudflare reports.

**I deleted a Pages project and now can't recreate it under the same name.**
Cloudflare enforces a **name-reuse cooldown** after a Pages project is deleted. Wait it out, then redeploy — the name will free up. (Or pick a different project name to avoid the wait.)

**I can't find my site / "it deployed but it's not there."**
Almost always this is a **wrong Cloudflare account**. Check that the KB is connected to the account you intended — when a token spans multiple accounts, the account you picked at Connect time is where the site lives. Reconnect Cloudflare (step 4) with the correct account if needed. This is why picking **one** Cloudflare account for all your KBs up front saves grief.

**The deploy fails at the Access step.**
The publisher is deliberately **fail-closed**: if it can't create or verify the Cloudflare Access policy, it aborts before publishing rather than risk exposing your content. Check that the connected token still has **Access: Apps and Policies: Edit** (and **Cloudflare Pages: Edit**), then redeploy.

## How this maps to the security model

For the full design — the zero-data control plane, the per-customer GitHub App installation, the token sealed into your repo, and the fail-closed publish invariants — see [How it works](how-it-works.md) and [Security](security.md).
