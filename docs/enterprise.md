# Enterprise Deployment

Organizations on Google Workspace / Chrome Enterprise (or any MDM) can roll the [Glassdocs extension](extension.md) out to staff centrally: force-install it by its Chrome Web Store ID, then push a shared configuration — which backend to use and, optionally, a shared API key — through Chrome's managed policy. Staff open the side panel, sign in with GitHub, and start editing; nobody pastes a key. GitHub sign-in is always per-user, so every commit and pull request stays attributed to the individual who made it.

## How managed configuration works

The extension reads its policy from Chrome's read-only **managed storage** (the schema ships with the extension as `managed_schema.json`). An admin pushes the configuration once and every install in scope picks it up.

- Locking is per **top-level key**: pushing any part of a provider block (e.g. `claude`) **overrides** and **locks** that whole block in the extension's Options page — including fields inside it you didn't set — shown under a "managed by your organization" banner.
- Top-level keys you leave out entirely stay user-controlled.
- **GitHub sign-in and commit identity are always per-user.** The schema does not accept a GitHub commit token — there is no policy key for one, and the extension ignores a `claude.githubToken` even if a stale cached policy still carries it. Every commit and pull request is attributed to the signed-in user; a policy cannot change that. (Users may still paste their *own* personal access token locally in the extension's Options — it stays in their own browser storage.)

The policy keys mirror the extension's settings:

| Key | Meaning |
| --- | --- |
| `adapter` | `"managed"` \| `"claude"` \| `"openai"` \| `"github-models"` |
| `managed.baseUrl` | Self-hosted backend URL (up to `/v1`); omit for the hosted default |
| `claude.apiKey` / `claude.model` | Shared Anthropic key + model |
| `openai.apiKey` / `openai.model` | Shared OpenAI key + model |
| `githubModels.token` / `githubModels.model` | GitHub Models token (needs `models:read`) + model |

## Force-install via Google Workspace

The extension's Chrome Web Store item ID is:

```
ljbopnkkljoapnahdpodpbjlgkjccdoc
```

In the Google Admin console:

1. Go to **Devices → Chrome → Apps & extensions → Users & browsers**.
2. Select the target **OU or group**.
3. Click **＋ → Add from Chrome Web Store** and paste the item ID. (The listing is unlisted, so adding by ID is the way in.)
4. Set **Installation policy** to *Force install* (or *Allow*).
5. Paste one of the configurations below into **Policy for extensions**.

!!! warning "Scope your rollout"
    Select a narrow OU or group before saving — a policy set at the org root pushes to everyone. Start with a test OU containing just your own user.

## Ready-to-paste configurations

**A. Managed backend, hosted (simplest — staff just sign in with GitHub):**

```json
{ "adapter": "managed" }
```

**B. Managed backend, self-hosted (keep inference in-house):**

```json
{ "adapter": "managed", "managed": { "baseUrl": "https://docs-ai.internal.example.com/v1" } }
```

**C. Shared Anthropic key (staff never see or paste it):**

```json
{
  "adapter": "claude",
  "claude": { "apiKey": "sk-ant-REPLACE_ME", "model": "claude-sonnet-4-6" }
}
```

**D. Shared OpenAI key:**

```json
{
  "adapter": "openai",
  "openai": { "apiKey": "sk-REPLACE_ME", "model": "gpt-5.4" }
}
```

**E. GitHub Models (shared models-scoped token):**

```json
{
  "adapter": "github-models",
  "githubModels": { "token": "github_pat_REPLACE_ME", "model": "openai/gpt-4o" }
}
```

!!! tip "Prefer the managed backend over a shared key"
    Pushing a real key (C/D/E) puts a secret into your Chrome policy and hands it to every browser in scope. With the managed backend (A/B) the provider key lives server-side and is never delivered to the browser at all — that's the point of the managed tier. Use a shared key only if you specifically don't want a backend in the path.

## Other platforms

- **Windows:** set the same JSON object in the registry under `Software\Policies\Google\Chrome\3rdparty\extensions\<id>`.
- **Linux:** a JSON policy file with the same object.
- **macOS (without MDM, for testing):** deliver the policy as a Configuration Profile — Chrome only honours *forced* preferences as policy, so a plain `defaults write` is silently ignored. Restart Chrome fully after installing the profile; OS policy is only re-read on a full restart.

!!! note "Unpacked developer builds may not receive policy"
    Chrome often will not attach third-party managed storage to a developer-mode (unpacked) extension: `chrome://policy` shows the extension's section but reads "No policies set". This is a dev-mode limitation, not a policy mistake. Managed storage binds reliably once the extension is installed from the Chrome Web Store and the config is pushed as cloud policy via the Admin console — the production path.

## Verify it landed

Any one of these confirms delivery:

- Open the extension's **Options** page — the controlled fields are disabled under the "managed by your organization" banner.
- Visit `chrome://policy` (hit *Reload policies*) — a section for the extension appears with your values.
- In the extension's service-worker console (`chrome://extensions` → the extension → "service worker"), run:

```js
chrome.storage.managed.get(null).then(console.log)
```

Expect the object you pushed.

## See also

- [Extension](extension.md) — what each backend does, and how users experience the locked settings
- [API](api.md) — the managed backend the `"managed"` adapter talks to
- [Admin](admin.md) — org-level administration of your knowledge bases
- [Security](security.md) — the identity and data-handling model
