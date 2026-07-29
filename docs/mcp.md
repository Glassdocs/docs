# MCP Server

The Glassdocs MCP server lets an AI coding agent — Claude Code, Claude Desktop, Cursor — read every knowledge base in your GitHub organization directly. Ask "what does our runbook say about failover?" in the terminal you're already in, and the agent searches across all your KBs and answers from the source. No browser, no tab switching, no copy-pasting a page into a prompt.

It complements the [browser extension](extension.md): the extension is for reading and editing *the page in front of you*, the MCP server is for asking questions *across everything you have*.

!!! info "Availability"
    The hosted server is **live** and needs no install — see [Connecting](#connecting). Open to any member of your GitHub organization.

## What you get

Five reads and one write:

| Tool | What it does |
| --- | --- |
| `list_kbs` | Every KB in the org — repo, Cloudflare project, live URL, access mode, deploy status. |
| `list_docs` | The Markdown pages in one KB. |
| `read_doc` | One page's full content. |
| `kb_status` | Live deploy status straight from GitHub Actions. Use when a publish looks stuck. |
| `search` | Case-insensitive search across pages, returning matching lines. Narrow with `repo` for speed. |
| `write_doc` | Create or replace a page — **as you**, opening a pull request by default. See [Writing](#writing). |

The five reads are annotated `readOnlyHint: true`, so well-behaved clients run them without interrupting you. `write_doc` is annotated `destructiveHint: true`, so clients ask before it commits — that prompt is the equivalent of the extension's **Apply / Cancel** diff review.

## Authentication

Your own **GitHub token** — the same credential the rest of the [managed API](api.md) takes. There is no Glassdocs API key, no OAuth consent screen, and no account to create.

If you're signed in with the [GitHub CLI](https://cli.github.com), `gh auth token` supplies it and there is nothing else to configure.

Nothing is stored: Glassdocs verifies the token against GitHub on each request and discards it.

The same token is what commits. When an agent writes a page, the commit is authored by **you** — the same mechanism the extension uses — so authorship, review and blame all work normally. Glassdocs never signs a change on your behalf.

To revoke access, revoke the token at GitHub. There is no separate Glassdocs credential to hunt down.

## Connecting

One line, nothing to download:

```bash
claude mcp add --transport http glassdocs https://app.glassdocs.site/mcp \
  --header "Authorization: Bearer $(gh auth token)"
```

Restart your session and ask your agent to list your knowledge bases.

For Claude Desktop or Cursor, put the same URL and header in their MCP config. Any client that speaks HTTP transport works — there is no Glassdocs package to install.

The `--header` is a temporary step: a browser sign-in is coming, after which the URL alone will do. The endpoint already advertises the challenge OAuth-capable clients look for, so your setup won't need to change when it lands.

Each tool takes an `org` argument, so one connection covers every organization you belong to.

### Who can use it

Any **member** of the GitHub organization, not only admins — reading your team's docs shouldn't require the standing to rotate the team's API keys.

It does not reach people outside your GitHub organization. A client or colleague who reads a published KB is authenticated by Cloudflare Access on *your* account, from the staff and client grants you set; Glassdocs writes those grants but never authenticates those readers and holds no identity for them. Extending MCP to them would mean giving Glassdocs its own notion of who they are — a deliberate architectural decision, not a follow-up, and not currently planned.

## Writing

`write_doc` creates or replaces a page. Two modes, and the choice is yours — the same choice the extension offers under **Commit mode**:

| Mode | What happens |
| --- | --- |
| `pr` (**default**) | Branches from your default branch, commits, and opens a pull request. You get the URL back and review before anything is live. |
| `direct` | Commits straight to the default branch, which republishes immediately. |

Pull request is the default in both the extension and here, because the two shouldn't disagree about what's safe.

Ask for what you want and the agent picks the tool:

> *"Add a rate-limits section to the API page and open a PR."*
> *"Fix the typo on the runbook index — commit it directly."*

Writes are confined to Markdown under `docs/` in **registered knowledge bases**. The server will refuse a path outside `docs/**.md`, and refuse a repository that isn't set up as a KB — so a connected agent can't reach the rest of your organization's code.

### If you'd rather it didn't write

Nothing forces you to use it. Your MCP client controls whether a destructive tool runs, and `write_doc` is annotated so that a client prompts by default. You can also just not ask.

For bulk authoring, cloning the repo and editing locally is still often faster — the agent can read through Glassdocs and write through git.

## Troubleshooting

| Message | Cause |
| --- | --- |
| *the GitHub token is missing, expired, or revoked* | The token isn't reaching the server, or GitHub has invalidated it. Check `gh auth status`. |
| *You must be a member of this GitHub organization* | You aren't in the org you named, or your token can't see that membership. |
| *Not signed in* | The `Authorization` header isn't reaching the server. Re-add the connection. |

Search reports its own limits: it scans at most 200 pages per query and tells you when it truncated, along with any KB it couldn't read. If a result says it was truncated, narrow it with `repo`.

## Related

- [API Reference](api.md) — the HTTP endpoints underneath, callable directly.
- [Browser Extension](extension.md) — read and edit the page you're on.
- [Admin Dashboard](admin.md) — set up KBs and manage org access.
