# MCP Server

The Glassdocs MCP server lets an AI coding agent — Claude Code, Claude Desktop, Cursor — read every knowledge base in your GitHub organization directly. Ask "what does our runbook say about failover?" in the terminal you're already in, and the agent searches across all your KBs and answers from the source. No browser, no tab switching, no copy-pasting a page into a prompt.

It complements the [browser extension](extension.md): the extension is for reading and editing *the page in front of you*, the MCP server is for asking questions *across everything you have*.

!!! info "Availability"
    In preview for design partners and Glassdocs staff. The hosted version — which needs no install at all, just a URL, and which grants access based on **who may read a KB** rather than requiring GitHub org admin — is in development. See [Availability](#availability).

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

By default the server runs `gh auth token`, so if you're signed in with the [GitHub CLI](https://cli.github.com) there is nothing to configure. Set `GLASSDOCS_TOKEN` instead if you'd rather supply it directly.

You must be an **admin** of the GitHub organization, exactly as for the [admin dashboard](admin.md). Nothing is stored: Glassdocs verifies the token against GitHub per request and discards it.

To revoke access, revoke the token at GitHub. There is no separate Glassdocs credential to hunt down.

## Availability

Two versions, and the difference is who they can serve.

**Today — preview.** A local server that runs on your own machine and forwards your GitHub token. It requires you to be an **admin of the GitHub organization**, which in practice means it is for the team already working in the repos. Design partners and Glassdocs staff can get it from us.

**In development — hosted.** Added with a URL, no install:

```bash
claude mcp add --transport http glassdocs https://app.glassdocs.site/mcp
```

The important difference isn't convenience, it's authorization. The hosted server grants access based on **who may read a KB** — your staff domain, and the client domains and addresses you've granted — rather than on GitHub org membership. That means the people your KBs were published *for* can use it: a client reading their own knowledge base, someone in ops or marketing with no repo access at all. They have no GitHub permission to forward, so the local version can never serve them.

### Configuration

These apply to the local preview.

| Variable | Default | Purpose |
| --- | --- | --- |
| `GLASSDOCS_ORG` | — | Your GitHub org. Every tool also accepts an `org` argument, so this is just the default. |
| `GLASSDOCS_TOKEN` | `gh auth token` | Supply a GitHub token directly instead of using the CLI. |
| `GLASSDOCS_API` | `https://app.glassdocs.site` | Point at a different Glassdocs backend. |

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
| *you must be an ADMIN of this GitHub org* | MCP access follows dashboard access. Org owners can grant admin. |
| *No GitHub token* | Neither `GLASSDOCS_TOKEN` nor `gh auth token` produced anything. Run `gh auth login`. |
| *Couldn't reach https://app.glassdocs.site* | Network or backend problem — the origin is named in the message. |

Search reports its own limits: it scans at most 300 pages per query and tells you when it truncated, along with any KB it couldn't read. If a result says it was truncated, narrow it with `repo`.

## Related

- [API Reference](api.md) — the HTTP endpoints underneath, callable directly.
- [Browser Extension](extension.md) — read and edit the page you're on.
- [Admin Dashboard](admin.md) — set up KBs and manage org access.
