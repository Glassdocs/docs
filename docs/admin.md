# Org admin dashboard

The Glassdocs admin dashboard at [app.glassdocs.site/admin](https://app.glassdocs.site/admin/) is where an organization owner runs Glassdocs for their whole team: sign in with GitHub, pick your org, set one shared AI key so staff never paste credentials, connect Cloudflare, and set up, monitor, and redeploy knowledge bases — all without Glassdocs ever creating repos or storing your content.

!!! info "Who can use it"
    You must be an **admin/owner of a GitHub organization**. Glassdocs has no accounts of its own — GitHub is the identity, and the dashboard only shows orgs where GitHub says you are an admin. If you sign in and see "No organizations to manage", ask an org owner to set things up (or create an org). See [Security & privacy](security.md) for how sign-in works under the hood.

## Sign in and pick your organization

1. Open [app.glassdocs.site/admin](https://app.glassdocs.site/admin/) and click **Sign in with GitHub**. This is a standard GitHub OAuth flow (scope `read:org`) that identifies you and your org roles.
2. After sign-in, the dashboard shows an **Organization** picker listing every GitHub org you administer. Everything on the page — the shared key, the KB list, every action — is scoped to the selected org.

Your dashboard session lasts about 8 hours. If it expires while a tab is still open, the page switches to the signed-out view with a "session expired" note rather than leaving a stale header — sign in again to continue.

## Set the org-wide shared AI key

The **Shared AI key** card lets you set **one provider key for your whole GitHub org**. Your teammates just install the [extension](extension.md), sign in with GitHub, and start editing — their extension resolves to the org key automatically via a membership lookup, so **staff never paste a key**.

On the card you can:

- **Choose a provider** — OpenAI or Anthropic — and a **model** (any model your key can access; a custom model already configured is preserved in the list).
- **Set or replace the key.** It is stored AES-encrypted at rest, sent only to the AI provider, and never shown to your members. The card records which admin last updated it. Leaving the field blank on save keeps the existing key — but only while the provider stays the same; switching provider requires entering a key for the new provider (the save is rejected otherwise).
- **Sync members** — refresh the org membership so new teammates resolve to the shared key.
- **Remove key** — members lose managed AI until you set a new one.
- **Watch usage** — the card shows member count plus tokens used today and in total. Only token *counts* are metered; prompts and responses are never stored (see [Security & privacy](security.md)).

!!! tip "Your key means your spend — and no free-tier cap"
    When your org has a key configured, members' AI usage runs on your key and your provider account, and is not counted against the Glassdocs free-tier caps. Without an org key, members fall back to the free managed tier with fair-use limits.

## Connect GitHub (install the Glassdocs app)

Knowledge-base features need the **Glassdocs GitHub App** installed on your org. If it isn't installed yet, the dashboard shows a **Connect GitHub** card:

1. Click **Install the Glassdocs app on GitHub**, pick your org, choose which repos to grant, and approve.
2. Back in the dashboard, click **I've installed it — recheck**.

The app asks for **least-privilege** access — read and write repo contents (scaffolding the KB starter files), Actions variables, workflows, secrets (sealing your Cloudflare token), and pull requests (for protected branches). It **never creates or deletes repos**, and never stores your content. The installation record is the only thing Glassdocs keeps, and the grant is yours to revoke at any time by uninstalling the app.

## Knowledge bases

The **Knowledge bases** card lists every KB in the org with its repo, published site URL (`<project>.pages.dev`), the Cloudflare account it deploys to, its access state (staff-only, client grants, or a 🌐 **public** chip for explicitly public KBs), and a **live deploy status chip** — queued, running, deployed, or failed — pulled straight from GitHub Actions and linked to the run logs. Status refreshes automatically (faster while a deploy is in flight) and on demand via **Refresh**, which re-crawls the org's repos.

### Set up a KB

Glassdocs configures existing repos; it doesn't create them. First create a repo in your org from the [Glassdocs KB template](https://github.com/Glassdocs/kb-template/generate), then click **＋ Set up a KB**:

1. **Pick your repo and name the site.** Only repos the Glassdocs app can access appear — grant the app the repo (or click **Reload**) if yours is missing. The **Cloudflare Pages project** name becomes your site URL, `<project>.pages.dev`.

    !!! warning "Reconnecting an existing site?"
        If the KB already has a live Pages site, enter that project's **exact** name — a new name creates a second, separate site and orphans the real one. After you connect Cloudflare, the form warns if the name you chose isn't an existing project on the account. A name that *does* match an existing project triggers a blocking confirmation at submit — deploying there replaces whatever that site currently serves. And a project name already registered to a **different** KB is refused outright (a hard 409, no override — and the error never names another customer's repo).

2. **Connect Cloudflare.** Click **Create token on Cloudflare** — the link pre-selects exactly the two permissions the publisher needs (**Cloudflare Pages: Edit** and **Access: Apps and Policies: Edit**) and pre-fills a per-KB token name. Create the token, paste it, and press **Connect**. Glassdocs verifies the token and **seals it into the repo as a GitHub Actions secret** — the token is **never stored by Glassdocs**; from then on only your own CI uses it. If the token spans multiple Cloudflare accounts, the form asks which one to deploy to — use the same account for all your KBs. If the repo already carried a `CLOUDFLARE_API_TOKEN` secret (say, for its own CI), Connect replaces it and warns you it did — re-check any other workflow that relied on the old one.

    !!! warning "Don't use Cloudflare's *Connect to Git*"
        Glassdocs publishes by direct upload from GitHub Actions. A Pages project wired to Git won't accept these deploys.

3. **Set who can read it.** Access is **fail-closed with no default** — a blank field grants no one through that channel, and leaving *every* field blank deploys the site locked to nobody. Set the **Staff domain** (your org's email domain) to grant your whole team SSO read access; optionally add a **Client domain** or individual **Client emails** for external readers. For docs meant for the whole world, tick **🌐 Public KB** instead — an explicit opt-in that publishes the site world-readable with **no** Access gate. Checking it disables and clears the staff/client fields (public and access grants are mutually exclusive); leaving it unchecked keeps the default staff-gated setup. See [Hosting](hosting.md) for the full access model and [Publishing](publishing.md#public-mode) for public mode.

4. **Deploy.** Leave **Add Glassdocs KB files** checked if the repo didn't start from the template (it commits `deploy.yml`, `mkdocs.yml`, and `docs/`), then click **Set up & deploy**. Glassdocs writes the project and access variables to the repo and dispatches the first deploy in **your** GitHub Actions — which builds the Markdown with Zensical, publishes to your Cloudflare Pages, and creates the Cloudflare Access gate fail-closed. If the repo's default branch is protected, Glassdocs opens a pull request with the files instead and links it.

Watch the status chip in the KB list; a failed run names the step that broke and links to the logs. Full pipeline details are in [Publishing](publishing.md).

### Manage an existing KB

Each KB row offers:

- **📄 Pages** — a read-only viewer for the KB's `docs/*.md`: browse what each page contains without leaving the console, with an **Edit on GitHub** link per page. Editing itself lives in the [extension's Edit mode](extension.md) or on GitHub, where changes carry your own identity and the nav (`mkdocs.yml`) can be updated too. Content passes through, but is never stored by, Glassdocs.
- **Access** — loads the KB's **current live** staff/client values, lets you change them, and **Save & redeploy** applies the new policy. Clearing every field locks the site to no one (fail-closed) — this panel is also how you recover a locked-out KB: set the staff domain and save.
- **☁ Cloudflare** — re-connect and re-seal the Cloudflare token for this KB (the fix for a "check Cloudflare credentials" deploy failure), then **Redeploy**.
- **Redeploy** — trigger a fresh deploy of the current content.
- **Remove** — unpublish: stops future deploys and removes the KB from the list. The live site and Cloudflare project stay up; you can re-add the KB anytime via **Set up a KB**.

## After deploying: verify the gate

Once a KB reports **deployed**, open its `pages.dev` URL in a private window — you should be redirected to the Cloudflare Access login, not shown content. See [Hosting](hosting.md) for the verification steps and [Security & privacy](security.md) for why publishing is fail-closed by design.

## Related pages

- [How it works](how-it-works.md) — the zero-data control-plane model.
- [Getting started](getting-started.md) — the end-to-end first-KB walkthrough.
- [Extension](extension.md) — what your teammates install.
- [Enterprise](enterprise.md) — org-managed rollout options.
- [API](api.md) — the endpoints behind the dashboard.
