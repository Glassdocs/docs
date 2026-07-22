# Browser Extension

The Glassdocs browser extension turns any published knowledge base into something you can talk to — and edit. Open the side panel on a docs page to ask questions about what you're reading; switch to Edit mode and an AI agent proposes concrete changes to the page's source in GitHub. You review a diff, then Apply to open a pull request or push a commit — every change attributed to your own GitHub identity. No "open the repo, find the file, clone, edit, PR" detour.

!!! note "Store listing name"
    The extension is currently listed on the Chrome Web Store as **Docs Chat** (v0.53.0). It is being renamed **GlassDocs** in its next release — same extension, same ID, same link.

## What it does

- **Chat about the current page.** The extension reads the docs page in your active tab (URL, title, and visible text — only when you send a message) and answers questions about it.
- **Edit mode.** Ask for a change and the agent proposes edits to the page's source files in GitHub. You see a diff preview with **Apply** / **Cancel** — nothing is written until you apply.
- **Apply → PR or direct commit.** Applied edits either open a pull request or push a commit directly, depending on the mode you choose. Commits are made with *your* GitHub sign-in, so authorship and review flows stay honest.
- **Per-repo chat history.** Conversations are kept per repository, so switching between docs sites keeps each thread intact.

## Install

Install from the Chrome Web Store:

**[Install from the Chrome Web Store](https://chromewebstore.google.com/detail/docs-chat/ljbopnkkljoapnahdpodpbjlgkjccdoc)**

The listing is **unlisted** — reachable only via this link, not via store search. Store installs update automatically in the background.

Compatible with any Chromium browser that supports Manifest V3 and the side-panel API: Chrome 120+, Edge, Brave, Arc.

### First run

1. Open any Glassdocs-enabled docs site.
2. Click the extension's toolbar icon (pin it so it's always visible). The browser opens a side panel.
3. The banner under the header shows the repo and source path resolved from the current URL, e.g. `your-org/your-repo — docs/index.md`.
4. Sign in with GitHub (a one-time device-flow authorization). That's all you need for the default **Managed** backend — no API key.
5. Start chatting. To bring your own key instead, open the options page and pick a different backend.

## Backends

The extension is a chat surface; the actual AI calls go through a pluggable backend. Pick one in the extension's Options page.

### Managed (no key) — the default

Sign in with GitHub and go. Glassdocs runs the AI: the extension sends your requests to the managed backend at `app.glassdocs.site`, using your GitHub sign-in token as the credential. The backend verifies your identity, enforces fair-use caps, and forwards to the provider with its own key — you never obtain or paste an API key.

To point at a self-hosted backend instead, set a **Managed base URL** (up to `/v1`) in Options. See [API](api.md) for the backend's endpoints.

### Claude (bring your own key)

1. Open the extension **Options**.
2. Paste your own **Anthropic API key**.
3. Sign in with GitHub (device flow) or paste a personal access token with `repo` scope — GitHub auth is shared across backends.
4. Pick a model.

Traffic goes straight from your browser to the Anthropic API; there is no Glassdocs server in the path.

### OpenAI (bring your own key)

Same as Claude, with your own **OpenAI API key** in the OpenAI section of Options. Uses the same multi-turn tool loop (list pages, read files, propose edits) and the same GitHub auth.

### GitHub Models

Uses GitHub's OpenAI-compatible inference at `models.github.ai` — no separate AI key.

1. In Options, open the GitHub Models section and pick a model.
2. Leave the token blank to reuse your GitHub sign-in (it needs the `models:read` permission), or paste a models-scoped fine-grained personal access token.

!!! tip "Organizations"
    Admins can push a shared backend configuration to every install via Chrome managed policy, so staff never pick a backend or paste a key. See [Enterprise deployment](enterprise.md).

## How a site opts in

A docs site connects to the extension by emitting a single meta tag in its rendered HTML:

```html
<meta name="source-repo" content="owner/repo">
```

That's the whole contract — no registry, no per-user setup. The extension reads the tag to resolve which repository backs the page, fetch source files, propose edits, and open pull requests.

- Repo detection is **only** via this tag. The GitHub repository's website/homepage field is not used.
- `docs-repo` is accepted as a legacy alias for the tag name.
- Sites built and published with Glassdocs emit the tag automatically at deploy time — see [Publishing](publishing.md).
- Clean URLs (no `.html` suffix) and trailing slashes are resolved to source files automatically.

### Where in-page affordances appear

The side panel and repo detection work on **any** site that carries the `source-repo` meta tag. The in-page affordances (the "Edit this" control and highlight overlays, injected by the content script) load automatically only on `https://*.pages.dev/*` — docs sites published on Cloudflare Pages.

On any other site — including `*.glassdocs.site` hosts — opening the side panel from the toolbar icon injects the content script into the active tab, so the affordances appear there once the panel is open.

## GitHub identity

The extension has no account or login of its own — GitHub is the identity. Signing in uses the **GitHub App device flow**: click **Sign in with GitHub**, enter the short code on github.com, and authorize. Tokens are stored in your browser's extension storage and refreshed automatically; they are never sent to any Glassdocs server, except that in Managed mode your token rides along as the bearer credential, where the backend verifies it per-request and stores nothing. See [Security](security.md) for the full model.

A power user can paste a personal access token instead of using the device flow.

## Privacy

The extension sends network traffic only to:

- the AI backend you configured — your own provider (Anthropic, OpenAI, GitHub Models) in bring-your-own-key modes, or the Glassdocs managed backend in Managed mode;
- GitHub, for reading source files and opening pull requests or pushing commits;
- the current tab's page (read-only, to extract the text you're chatting about).

No telemetry and no phone-home. In bring-your-own-key modes there is no shared server at all. In Managed mode, prompts and page context pass through the managed backend (which authenticates you and meters usage for fair-use caps); switch to a bring-your-own-key backend to keep everything client-to-provider. Settings live in Chrome's synced extension storage, scoped to your browser profile, and are cleared when you remove the extension.

## See also

- [Getting Started](getting-started.md) — authoring conventions for the pages you'll be editing
- [How it works](how-it-works.md) — the overall Glassdocs pipeline
- [Enterprise deployment](enterprise.md) — force-install and shared configuration for organizations
- [API](api.md) — the managed backend the default mode talks to
