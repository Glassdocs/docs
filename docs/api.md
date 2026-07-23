# Managed Backend API

The Glassdocs managed backend at `https://app.glassdocs.site` is what the [extension's](extension.md) default **Managed (no key)** mode talks to: an authenticating, budgeting, usage-metering reverse proxy in front of an OpenAI-compatible model provider, plus a small identity endpoint. You authenticate with a GitHub token — there is no Glassdocs API key or account — and the backend stores no prompt or completion text, only token counts for metering.

## Authentication

Every request carries a **GitHub token** as a bearer credential:

```
Authorization: Bearer <github-token>
```

The backend verifies the token against GitHub on each request and discards it — no user tokens are stored server-side. The extension supplies the token from your GitHub sign-in automatically.

| Response | Meaning |
| --- | --- |
| `401` | Missing or invalid GitHub token. |
| `503` | GitHub itself couldn't be reached to verify your identity (outage, rate limit). Your token may be fine — retry. |

The API is browser-callable: CORS is enabled for `GET`, `POST`, and `OPTIONS` with the `Authorization` and `Content-Type` headers.

## Error shape

All errors are JSON with the HTTP status carrying the semantics:

```json
{ "error": "Invalid GitHub token" }
```

## POST /v1/chat/completions

An OpenAI-compatible chat completion. Point any OpenAI-format client at `https://app.glassdocs.site/v1` with the GitHub token in the API-key slot.

```bash
curl -sS https://app.glassdocs.site/v1/chat/completions \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      { "role": "user", "content": "Summarize this page for me." }
    ]
  }'
```

The response is a standard OpenAI-format chat completion, passed through from the provider.

### What the backend enforces

The request body is OpenAI-format, but a few fields are controlled server-side:

- **Model** — the backend chooses the model (the operator-configured managed model, or your organization's configured model if it has a shared key). A `model` field in the request is overridden.
- **No streaming** — responses are returned complete; `stream` is forced off.
- **Output clamp** — `max_tokens` is capped at 8192 per request; multi-sample knobs (`n`, `best_of`, `logprobs`, `top_logprobs`) are dropped.

### Who pays: org key or free tier

- If you belong to a GitHub organization whose admin configured a **shared provider key** (see [Admin](admin.md)), that key and model are used. The org's own spend pays, and the free-tier caps below don't apply.
- Otherwise you're on the **free tier**: Glassdocs' key pays, gated by fair-use token caps — a per-user daily cap and a global daily circuit breaker. Caps reset at midnight UTC. Check your remaining budget with [`GET /api/me`](#get-apime).

### Responses

| Status | Meaning |
| --- | --- |
| `200` | Completion succeeded; OpenAI-format body. |
| `400` | Unreadable or invalid JSON body. |
| `401` | Missing or invalid GitHub token. |
| `413` | Request too large — trim the prompt or page context and retry. Free tier only: this is an input-size estimate on free-tier requests; org-shared-key requests aren't size-checked. |
| `429` | Free-tier cap hit: either your personal daily limit (resets tomorrow, UTC) or Glassdocs' global daily capacity. |
| `503` | GitHub identity verification temporarily unavailable — retry. |
| other | Upstream provider errors are passed through with the provider's status code. |

!!! note "Zero-data metering"
    Request and response bodies pass straight through. Only token *counts* are persisted for budgeting and usage attribution — no prompt or completion text is stored. Failed upstream calls refund the free-tier budget they reserved.

## GET /api/me

Identity, tenant, and remaining free-tier budget for the token's user. The extension calls this to display who you are and how much free budget remains.

```bash
curl -sS https://app.glassdocs.site/api/me \
  -H "Authorization: Bearer $GITHUB_TOKEN"
```

Response:

```json
{
  "login": "octocat",
  "tenant": null,
  "billing": "free",
  "orgs": ["your-org"],
  "budget": {
    "perUserDaily": 100000,
    "usedToday": 1234,
    "remaining": 98766
  }
}
```

| Field | Meaning |
| --- | --- |
| `login` | Your GitHub login, as verified from the token. |
| `tenant` | Always `null` — free-tier identities have no stored tenant record (see [Security](security.md)). Retained for wire compatibility. |
| `billing` | `"org"` when an organization's shared key pays for your requests, `"free"` when Glassdocs' free tier does. |
| `orgs` | GitHub organizations the token can see. Informational only — org billing on `/v1` is resolved by a server-side seat lookup, not this list. |
| `budget.perUserDaily` | Your daily free-tier token cap; `null` means uncapped. |
| `budget.usedToday` | Tokens consumed so far today (UTC day). |
| `budget.remaining` | Tokens left today; `null` when uncapped. |

The budget shown here is computed with the same defaults the `/v1` enforcer uses, so what you see is what is enforced. When `billing` is `"org"` the free-tier numbers don't apply — your organization's key pays and Glassdocs enforces no cap.

| Status | Meaning |
| --- | --- |
| `200` | Identity and budget returned. |
| `401` | Missing or invalid GitHub token. |
| `503` | GitHub identity verification temporarily unavailable — retry. |

## Self-hosting

The backend is the same software whether Glassdocs hosts it or you do. The two endpoints above are the surface for the extension and API consumers; the server also exposes the admin/control-plane API used by the [admin dashboard](admin.md) — GitHub OAuth sign-in plus `/api/admin/org/...` routes for org configuration, keys, access, and KB setup. A self-hosted deployment ships the full surface. Point the extension's **Managed base URL** (up to `/v1`) at your host, or push it to your whole organization via [enterprise policy](enterprise.md). See [Hosting](hosting.md) for the deployment options.

## See also

- [Extension](extension.md) — the primary client of this API
- [Enterprise deployment](enterprise.md) — pointing every staff install at a hosted or self-hosted backend
- [Admin](admin.md) — configuring an org shared key so members skip the free-tier caps
- [Security](security.md) — the identity model and what is (and isn't) stored
