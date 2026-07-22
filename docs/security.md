# Security & privacy

Glassdocs is a **zero-data control plane**: your Markdown lives in your GitHub repos, your published sites live on your Cloudflare account, and Glassdocs never stores document content, prompts, or model responses. This page explains the authentication model, exactly what data flows where (and when), what the managed backend can and cannot see, how private sites are gated, and what Glassdocs will never do with your data.

## The zero-data model

Glassdocs orchestrates; it does not host your data. The data plane — content, access rules, published sites, build compute — stays in **your** GitHub and Cloudflare accounts.

| State | Lives in |
| --- | --- |
| KB content (`docs/*.md`), nav and theme (`mkdocs.yml`), branding assets | Your GitHub repo — Glassdocs never copies it |
| Published site | Your Cloudflare Pages, deployed by your own GitHub Actions |
| Read-access policy (who can view the site) | Your repo's Actions variables → Cloudflare Access |
| GitHub App installation | Your GitHub org — revocation = uninstall |
| Identity records and one AES-GCM-encrypted org AI key | Glassdocs (no content) |
| Usage counters | Glassdocs — **token counts only**, never prompts or responses |
| KB inventory and audit log | Glassdocs — the inventory is regenerable from GitHub; audit records hold metadata (e.g. a file path and byte count), never content |

Editing keeps the same invariant: whether you edit through the [extension](extension.md) or the [in-console editor](admin.md), the page body only *transits* the control plane — no document body is ever written to Glassdocs storage. Unsaved edits live in your browser.

## Authentication

**GitHub is the identity.** There is no Glassdocs password or separate account — every actor proves who they are with a GitHub token, and every write is attributed to their own GitHub user.

### Humans in the extension — GitHub App device flow

The extension signs you in with the GitHub App **device flow** (no client secret, no redirect). You authorize on github.com; GitHub returns a short-lived user token (about 8 hours) plus a rotating refresh token (about 6 months) that the extension renews transparently. If the refresh token is truly dead — expired, revoked, or the app uninstalled — the stored token is cleared and you're prompted to sign in again.

These tokens are stored in your browser's `chrome.storage` and are **never sent to any Glassdocs server**, with one exception: in Managed mode the token is presented as a bearer credential so the backend can verify who you are (below). A power user can paste a Personal Access Token instead of using the device flow.

### Org admins in the dashboard — GitHub OAuth

The [admin dashboard](admin.md) uses a standard GitHub OAuth flow (scope `read:org`) with defense in depth:

- A server-generated `state` value, held in an HttpOnly, Secure, SameSite=Lax cookie, protects the flow against CSRF.
- Your admin session is an **AES-GCM-encrypted**, HttpOnly cookie with expiry checking.
- Post-login redirects derive from the request origin, never from a request parameter — no open redirect.

Every admin route verifies you are a **GitHub admin of the org in question** before doing anything on that org — authorization is checked *before* any org-scoped credential is minted, so tokens cannot be used cross-tenant.

### The server acting on your repos — installation tokens

To configure or deploy a KB, the backend acts as the **GitHub App installation on your org** — never with an admin's personal token. It mints short-lived (1-hour) installation tokens scoped to your installation, and only after the org-admin check above. The app's footprint is least-privilege: read code, read/write Actions variables and workflows; it never creates or deletes repos. Uninstalling the app revokes everything.

## How page content reaches AI backends

Nothing is sent anywhere until you act. The extension reads the **active tab only**, and **only when you send a message** — there is no background collection. What it reads: the page's URL, title, visible text and HTML, plus any text you selected. Where it goes depends on the backend *you* choose:

=== "Bring-your-own-key (Claude, OpenAI, GitHub Models)"

    Your prompt and page context go **directly from your browser to the provider** you configured, authenticated with your own key. Glassdocs is not in the path and never sees this data.

=== "Managed (no key)"

    Your prompt and page context pass through the managed backend at `app.glassdocs.site`, which:

    - **verifies your identity** by checking your GitHub token against GitHub per request — the token is verified and discarded, never stored server-side;
    - **resolves the key**: your org's shared key if an admin configured one (see [the admin dashboard](admin.md)), otherwise the Glassdocs free-tier key with fair-use caps;
    - **streams the request and response straight through**, persisting **only token counts** for metering — never the prompt, the page content, or the model's reply.

    The in-console editor's AI Assist uses the same core with the same guarantees, authenticated by the admin session instead of a bearer token. Switch to a BYO-key backend at any time to keep everything browser-to-provider.

Reads and writes to your repos (fetching source files, commits, pull requests) go from your browser to the GitHub API with your own token, and are attributed to your GitHub identity.

## Key and token custody

| Credential | Where it lives | Notes |
| --- | --- | --- |
| Your GitHub sign-in tokens (extension) | Your browser (`chrome.storage`) | Sent to Glassdocs only as the Managed-mode bearer credential; verified per request, never stored |
| Your BYO provider keys (extension) | Your browser (`chrome.storage`) | Sent only to the provider you chose |
| Org shared AI key | Glassdocs, **AES-GCM encrypted at rest** | Sent only to the AI provider; never shown to members; removable by an org admin at any time |
| Cloudflare API token | **Your repo**, as a GitHub Actions secret | Verified once at connect time, then sealed into the repo — Glassdocs never stores it; only your own CI uses it |
| App installation tokens | Minted on demand, ~1-hour lifetime | Only after the org-admin check |
| Admin session | Encrypted HttpOnly cookie | AES-GCM, expiry-checked |

Secrets never appear in logs or URLs; error messages carry provider error text, not tokens.

## Private sites: Cloudflare Access, fail-closed

Published KBs are gated by **Cloudflare Access** on your own account: visitors must pass SSO (staff email domain) or an explicit client grant (external domain or listed emails) before seeing any content. The design is deliberately **fail-closed**:

- **No default access.** A blank access field grants no one; a KB with nothing set deploys locked to nobody — never public by accident.
- **Gate before content.** On first deploy, if the Access application can't be created, the deploy aborts *before* any content is published.
- **Pre-flight check.** If the site is already publicly reachable, the deploy fails rather than proceed without an active gate.
- **Verify or roll back.** After each deploy the workflow probes the site; if it's publicly readable, the deployment is deleted, re-probed, and escalated until the exposure is actually closed — success is never reported on an open exposure.
- **Independent policy verification.** Every deploy re-derives the expected Access policy from its inputs and compares it to the live policy; a mismatch (for example a manual dashboard edit) fails the deploy.
- **Preview deployments are disabled**, so no preview URL can bypass the gate.

You can verify the gate yourself any time: open your site's URL signed out and confirm you're redirected to the Cloudflare Access login. See [Hosting](hosting.md).

## What Glassdocs does not do

- No analytics, telemetry, tracking pixels, or advertising.
- No selling or sharing of your data with third parties for their own purposes.
- No use of your content to train AI models by Glassdocs.
- No background collection — page content is read only when you actively send a message.
- No repo creation or deletion on your org, ever.

!!! note "Optional local debug channel"
    For developers, an off-by-default diagnostics option can stream extension events to a local collector. It is restricted to loopback addresses (`localhost` / `127.0.0.1`); a non-loopback destination is ignored, so page content cannot be exfiltrated. It stays off unless you turn it on.

## Your controls

- **Revoke Glassdocs's access to your org** by uninstalling the GitHub App — the installation record is all Glassdocs keeps.
- **Clear keys, tokens, and chat history** any time from the extension's Options page, or by removing the extension.
- **Avoid the managed backend entirely** by choosing a bring-your-own-key backend.
- **Rotate the Cloudflare token** per KB from the [admin dashboard](admin.md); it re-seals into your repo.
- Data handled by the AI providers and by GitHub is governed by their own privacy policies.

If your organization deploys the extension via Chrome enterprise policy, an administrator may push a read-only shared configuration (such as which backend to use); that config is set by your organization, not collected by Glassdocs, and GitHub sign-in remains per-user. See [Enterprise](enterprise.md).

## Privacy policy

The full privacy policy for the extension (published as "Docs Chat") is at **[glassdocs.site/privacy.html](https://glassdocs.site/privacy.html)**.

## Related pages

- [How it works](how-it-works.md) — the architecture behind these guarantees.
- [Admin dashboard](admin.md) — the org-level controls described above.
- [Extension](extension.md) · [Publishing](publishing.md) · [Hosting](hosting.md) · [API](api.md)
