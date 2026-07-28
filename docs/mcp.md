# MCP Server

The Glassdocs MCP server lets an AI coding agent — Claude Code, Claude Desktop, Cursor — read every knowledge base in your GitHub organization directly. Ask "what does our runbook say about failover?" in the terminal you're already in, and the agent searches across all your KBs and answers from the source. No browser, no tab switching, no copy-pasting a page into a prompt.

It complements the [browser extension](extension.md): the extension is for reading and editing *the page in front of you*, the MCP server is for asking questions *across everything you have*.

!!! info "Availability"
    The hosted server is **live** and needs no install — see [Connecting](#connecting). Open to any member of your GitHub organization.

## What you get

Five tools, all read-only:

| Tool | What it does |
| --- | --- |
| `list_kbs` | Every KB in the org — repo, Cloudflare project, live URL, access mode, deploy status. |
| `list_docs` | The Markdown pages in one KB. |
| `read_doc` | One page's full content. |
| `kb_status` | Live deploy status straight from GitHub Actions. Use when a publish looks stuck. |
| `search` | Case-insensitive search across pages, returning matching lines. Narrow with `repo` for speed. |

Every tool is annotated `readOnlyHint: true` and `destructiveHint: false`, so well-behaved MCP clients run them without interrupting you for confirmation.

## Authentication

Your own **GitHub token** — the same credential the rest of the [managed API](api.md) takes. There is no Glassdocs API key, no OAuth consent screen, and no account to create.

If you're signed in with the [GitHub CLI](https://cli.github.com), `gh auth token` supplies it and there is nothing else to configure.

Nothing is stored: Glassdocs verifies the token against GitHub on each request and discards it. It is read-only — the server refuses a token-authenticated write outright, so a connected agent cannot change anything even if asked.

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

## It is read-only — here's how to write

The MCP server cannot create or change pages, and this is deliberate rather than a gap waiting to be filled. Writes to a KB should carry the author's own GitHub identity and land through review, which a background tool call is a poor fit for.

To change KB content:

- **Use the [browser extension](extension.md)** — describe the change, review the diff, Apply. Commits are attributed to you and can open a pull request.
- **Or edit the repo directly** — a KB is just Markdown in `docs/` plus `mkdocs.yml`. Clone it, write, push; the publish workflow deploys it. See [Writing a KB](authoring.md).

An agent with this MCP server connected can do the second option itself: it reads the KB through the MCP tools, then edits the cloned repo with its normal file tools. That combination — read through Glassdocs, write through git — is the intended workflow for bulk authoring.

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
