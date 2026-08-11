# MCP Server

The Glassdocs MCP server lets an AI coding agent — Claude Code, Claude Desktop, Cursor — read every knowledge base in your GitHub organization directly. Ask "what does our runbook say about failover?" in the terminal you're already in, and the agent searches across all your KBs and answers from the source. No browser, no tab switching, no copy-pasting a page into a prompt.

It complements the [browser extension](extension.md): the extension is for reading and editing *the page in front of you*, the MCP server is for asking questions *across everything you have*.

!!! info "Availability"
    The hosted server is **live** and needs no install — see [Connecting](#connecting). Open to any member of your GitHub organization.

## What you get

Seven reads and three writes:

| Tool | What it does |
| --- | --- |
| `list_kbs` | Every KB in the org — repo, Cloudflare project, live URL, access mode, deploy status. |
| `list_docs` | The Markdown pages in one KB. |
| `read_doc` | One page's full content. |
| `kb_status` | Live deploy status straight from GitHub Actions. Use when a publish looks stuck. |
| `search` | Case-insensitive search across pages, returning matching lines. Narrow with `repo` for speed. |
| `list_prs` | Pull requests in a KB — state, URL, title, branch, and whether it merged. This is how an agent finds the PR it opened earlier. See [Following a pull request](#following-a-pull-request). |
| `pr_status` | One pull request in full, including whether it **merged** and whether GitHub currently considers it mergeable. |
| `write_doc` | Create or replace a page — **as you**, opening a pull request by default. See [Writing](#writing). |
| `delete_doc` | Remove a page — as you, opening a pull request by default. |
| `move_doc` | Rename or relocate a page, keeping its content, as one reviewable change. See [Renaming a page](#renaming-a-page). |

The seven reads are annotated `readOnlyHint: true`, so well-behaved clients run them without interrupting you. The three writes are annotated `destructiveHint: true`, so clients ask before they commit — that prompt is the equivalent of the extension's **Apply / Cancel** diff review.

### What it will and won't reach

Every tool — **reads included**, not only the writes — is confined to repositories registered as knowledge bases in the org you name. Ask an agent to read `docs/secrets.md` from a repo that isn't a KB and it is refused, by name, with a pointer to `list_kbs`. This matters because reads run on the Glassdocs GitHub App's installation token while you are authorized only as an org *member*: without that confinement, membership alone would reach any repo the app can see. Membership is not a repository permission, and the KB registry is the boundary that matches what someone actually consented to publish.

Archived KBs are excluded from every tool.

### Limits

Defaults, and an operator can change them for a deployment:

| Limit | Default | What happens at the edge of it |
| --- | --- | --- |
| Tool calls per org, per hour | 300 | The next call is refused with the reset time, in minutes. |
| Size of a page `write_doc` may write | 1 MB | The write is refused, naming the size and the limit, so an agent can split the page and retry. |
| JSON-RPC messages per batch | 16 | The request is refused with HTTP 400. Ordinary clients send one message per request and never see this. |
| Pages one `search` call can read | Depends on the org — see [Search](#search) | The result says so and is explicitly not complete. |

### Search

`search` reads pages from GitHub one at a time, and a single request has a fixed budget of GitHub calls. Listing each KB spends part of it, so **the number of pages one query can cover falls as the organization registers more KBs** — there is no single page count to quote.

When a query doesn't fit, the result carries a `truncated` field saying how many pages of how many were read and why, plus `reposSkipped` for any KB not searched at all. Treat that as a warning and not a footnote: the answer is a real answer from a partial view, so re-run with `repo` to search one KB at a time. A result with no `truncated` field covered everything.

## Authentication

Your own **GitHub token** — the same credential the rest of the [managed API](api.md) takes. There is no Glassdocs API key, no OAuth consent screen, and no account to create.

If you're signed in with the [GitHub CLI](https://cli.github.com), `gh auth token` supplies it and there is nothing else to configure.

Your token is never stored — it is verified against GitHub on each request and discarded. The only thing kept is an anonymous hourly request counter, keyed by a hash of your organization name, used to enforce the hourly allowance under [Limits](#limits). It holds no document content, no page names and no user identity.

The same token is what commits. When an agent writes a page, the commit is authored by **you** — the same mechanism the extension uses — so authorship, review and blame all work normally. Glassdocs never signs a change on your behalf.

To revoke access, revoke the token at GitHub. There is no separate Glassdocs credential to hunt down.

## Connecting

One line, nothing to download:

```bash
claude mcp add --transport http glassdocs https://app.glassdocs.site/mcp \
  --header "Authorization: Bearer $(gh auth token)"
```

Restart your session and ask your agent to list your knowledge bases.

!!! warning "`https://app.glassdocs.site/mcp` is the only endpoint — this page's own URL is not one"
    The address of *this page* — `https://docs.glassdocs.site/mcp/` — is documentation, not a server. Point a client at it and it will hang rather than fail: the docs site answers **200 with HTML**, so the client reads that as a stream that opened and closed, and reconnects for as long as you leave it running. Nothing reports an error at either end. If your agent connects but never lists a knowledge base, check the URL you pasted.

For Claude Desktop or Cursor, put the same URL and header in their MCP config. Any client that speaks HTTP transport works — there is no Glassdocs package to install.

The `--header` is a temporary step: a browser sign-in is coming, after which the URL alone will do. An unauthenticated request already gets a proper **401** with the `WWW-Authenticate` challenge an OAuth-capable client looks for, so a client can tell an unauthenticated connection from a broken server. The metadata document that challenge points at is not served yet — a client that fetches it gets a clean 404, which correctly reads as "this server runs no authorization server". Nothing about your setup will need to change when sign-in lands.

Each tool takes an `org` argument, so one connection covers every organization you belong to.

### Who can use it

Any **member** of the GitHub organization, not only admins — reading your team's docs shouldn't require the standing to rotate the team's API keys.

It does not reach people outside your GitHub organization. A client or colleague who reads a published KB is authenticated by Cloudflare Access on *your* account, from the staff and client grants you set; Glassdocs writes those grants but never authenticates those readers and holds no identity for them. Extending MCP to them would mean giving Glassdocs its own notion of who they are — a deliberate architectural decision, not a follow-up, and not currently planned.

## Writing

`write_doc` creates or replaces a page, `delete_doc` removes one, and `move_doc` renames one. All three commit as **you**. Two modes, and the choice is yours — the same choice the extension offers under **Commit mode**:

| Mode | What happens |
| --- | --- |
| `pr` (**default**) | Branches from your default branch, commits, and opens a pull request. You get the URL back and review before anything is live. |
| `direct` | Commits straight to the default branch, which republishes immediately. |

Pull request is the default in both the extension and here, because the two shouldn't disagree about what's safe.

`move_doc` is the exception: it has **no `direct` mode**, and asking for one is refused. A rename is two commits — create the new page, remove the old — and two commits straight to your default branch can't be atomic. If the second one failed, the page would be live at *both* paths and the publisher would build the duplicate. On the pull-request path both halves sit on one branch, so your site only ever sees the finished move. To land a rename immediately, merge the pull request it opens.

Ask for what you want and the agent picks the tool:

> *"Add a rate-limits section to the API page and open a PR."*
> *"Fix the typo on the runbook index — commit it directly."*
> *"That runbook is superseded — delete it."*

Writes are confined to Markdown under `docs/` in **registered knowledge bases**. The server will refuse a path outside `docs/**.md`, and refuse a repository that isn't set up as a KB — so a connected agent can't reach the rest of your organization's code. For `move_doc` that applies to *both* ends: a destination outside `docs/**.md` is refused rather than approximated.

All three writes accept the `sha` that `read_doc` returned for the page. Supplying it makes the change conditional on the version the agent actually read: if anyone commits to that page while you're reviewing the diff, the change is refused instead of quietly reverting them. Well-behaved agents pass it, because `write_doc` sends the *whole* page — without it, every byte that changed in the meantime is silently overwritten.

### Renaming a page

Use `move_doc` rather than asking for a create-then-delete. An agent composing those two calls itself gets it wrong in the obvious place: if the delete fails, the page is left live at both paths and your site publishes both copies. `move_doc` either moves the page or changes nothing — both halves land on one branch and one pull request, and if any part of it fails the branch is discarded.

It refuses rather than guessing in two cases worth knowing about: the destination already exists (it will not overwrite a page you didn't mention), and the source has changed since the agent read it.

Renaming a page changes its published URL. Nothing rewrites the links that pointed at the old one, so a rename is worth reviewing in the pull request even when the diff looks trivial.

### Following a pull request

A write returns the pull request URL once. `list_prs` and `pr_status` are how an agent picks the thread back up in a later turn — "did that PR get merged?", "what else is open?" — without you having to keep the link.

Pull requests these tools opened are flagged with `openedByGlassdocs`, so an agent can pick its own edits out of a busy repo; the branch names are `glassdocs/…`. `list_prs` covers every KB in the org if you omit `repo`, and defaults to **all** states rather than open ones, because a PR you're following up has usually already closed.

A closed pull request may have been merged or abandoned, and `state` alone can't tell you which. `pr_status` reports both GitHub's `merged` flag and an `outcome` in words — `open`, `merged`, or `closed without merging`. Its `mergeable` field can be `null`, which means GitHub hasn't finished computing the test merge yet, not that the PR can't be merged; that usually resolves within seconds of a PR being opened.

### If you'd rather it didn't write

Nothing forces you to use them. Your MCP client controls whether a destructive tool runs, and all three writes are annotated so that a client prompts by default. You can also just not ask.

For bulk authoring, cloning the repo and editing locally is still often faster — the agent can read through Glassdocs and write through git.

## Troubleshooting

Your agent relays these verbatim, so they are listed here exactly as they appear.

| Message | Cause | What to do |
| --- | --- | --- |
| *Not signed in* — HTTP **401** | No credential reached the server. The `Authorization` header is missing from the connection. | Re-add the connection with the `--header` line above. |
| *Invalid or expired GitHub token* — HTTP **401** | GitHub rejected the token: expired, revoked, or never valid. | `gh auth status`, then re-add the connection. Both 401s carry a `WWW-Authenticate` challenge, which is what lets a client tell "unauthenticated" from "broken". |
| *You must be a member of this GitHub organization* | You aren't in the org you named — or your token can't see that you are. Membership is read from GitHub, and a token without the `read:org` scope makes a member look like a stranger. | Check the org spelling, then check the token's scopes. |
| *`<org>` has used its hourly Glassdocs request allowance (300). It resets in about N minutes.* | The org hit the hourly tool-call limit — almost always an agent in a loop rather than a person. | Wait for the reset. If it keeps happening, something is retrying automatically. |
| *"`<org>/<repo>`" is not a knowledge base in `<org>`* | The repo isn't registered as a KB, or it's archived. This applies to **reads as well as writes**. | Run `list_kbs`, or set the repo up as a KB in the [admin dashboard](admin.md). |
| *Page is N kB; the limit is 1000 kB. Split it into several pages.* | `write_doc` was given more than the maximum page size. | Split the page. A KB page this large is usually several pages anyway. |
| *Batch too large: N messages (max 16). Split it.* — HTTP **400** | The client sent more JSON-RPC messages in one request than the server accepts. | Normal clients never hit this; if yours does, it is batching aggressively. |
| *Unsupported MCP-Protocol-Version "…"* — HTTP **400** | The client asked for a protocol revision this server does not implement. The message lists the ones it does. | Update the client, or pin it to a listed revision. |
| *Cross-origin requests are not accepted by this endpoint.* — HTTP **403** | The request carried a browser `Origin` header from another site. The endpoint is for MCP clients, not web pages, and refusing this is what stops a hostile page using your browser's credentials. | Connect from an MCP client rather than a browser. |
| *`<path>` in `<org>/<repo>` changed since you read it, so this write was refused rather than overwriting someone else's edit* | Someone committed to the page between your agent reading it and writing it back. | Ask the agent to re-read the page and re-apply your change to the new content. It can do that in one turn. |
| *That page doesn't exist in this KB.* | The path is wrong, or the page has been moved or deleted. | `list_docs` to see the real paths. |
| *`<path>` does not exist in `<org>/<repo>`, so there is nothing to delete / move.* | The agent guessed a path, or the page was already removed. | `list_docs`. Nothing was changed. |
| *`<path>` already exists in `<org>/<repo>`. move_doc will not overwrite a page* | The rename's destination is an existing page. | Pick a different name, or if the two really should be merged, have the agent write the combined page and delete the old one. |
| *move_doc has no 'direct' mode.* | A rename was asked for with `mode: 'direct'`. A move is two commits and can't be committed atomically to your default branch — see [Writing](#writing). | Let it open the pull request, then merge it. |
| *`<org>/<repo>` has no pull request #N.* | The number is wrong, or the PR is in a different KB. | `list_prs` for the repo. |

A `search` result that carries `truncated` is not an error — see [Search](#search).

## Related

- [API Reference](api.md) — the HTTP endpoints underneath, callable directly.
- [Browser Extension](extension.md) — read and edit the page you're on.
- [Admin Dashboard](admin.md) — set up KBs and manage org access.
