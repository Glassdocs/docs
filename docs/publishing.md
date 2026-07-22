# Publishing (client-hosted)

Client-hosted publishing means your KB deploys to your own Cloudflare account from your own GitHub Actions. The repo carries one small workflow that calls the reusable Glassdocs publisher, which builds your Markdown with Zensical and publishes it to Cloudflare Pages, secure by default behind Cloudflare Access. This page covers the workflow, the variables and secrets it needs, the access model, the security checks, and the opt-in public mode.

## The deploy workflow

Every KB created from the template carries `.github/workflows/deploy.yml`:

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    if: vars.CF_PAGES_PROJECT != ''
    permissions:
      contents: read
      deployments: write
    uses: Glassdocs/publisher/.github/workflows/deploy-pages.yml@v1
    with:
      project-name: ${{ vars.CF_PAGES_PROJECT }}
      email-domain: ${{ vars.EMAIL_DOMAIN }}
      client-domain: ${{ vars.CLIENT_DOMAIN }}
      client-emails: ${{ vars.CLIENT_EMAILS }}
    secrets: inherit
```

It runs on every push to `main` (and on manual dispatch), and it is a no-op until the `CF_PAGES_PROJECT` variable is set, which is what makes a KB "live". The publisher is pinned by release tag (`@v1`): it runs across every consumer repo, so it is a release-gated artifact.

!!! tip "The admin dashboard does this for you"
    Setting the variable and sealing the secrets by hand is the manual path. The [admin dashboard](admin.md) configures the repo and connects Cloudflare with one paste. The result is identical: everything below still applies.

## Configuration

### Required repo variable

| Variable | Purpose |
| --- | --- |
| `CF_PAGES_PROJECT` | Cloudflare Pages project name. Becomes `<name>.pages.dev`. Lowercase letters, digits, and hyphens only; the publisher rejects anything else. |

### Required repo secrets

| Secret | Purpose |
| --- | --- |
| `CLOUDFLARE_API_TOKEN` | API token scoped to exactly two permission groups: **Pages: Edit** and **Access: Apps and Policies: Edit** |
| `CLOUDFLARE_ACCOUNT_ID` | The Cloudflare account that owns the Pages project |

Set both as Actions secrets on the KB repo (or its org); the workflow forwards them to the publisher with `secrets: inherit`. The publisher verifies the credentials up front, and it confirms the token can actually reach Access on that account before doing anything, so a mis-scoped token fails fast with a clear message instead of a cryptic API error later.

## Who can read the site

Read access is controlled by three optional repo variables, enforced as Cloudflare Access policies:

| Variable | Grants access to |
| --- | --- |
| `EMAIL_DOMAIN` | Everyone at your organization's email domain (e.g. `acme.com`). This is what makes a KB "staff-only". |
| `CLIENT_DOMAIN` | Everyone at one external client email domain, in addition to the staff domain |
| `CLIENT_EMAILS` | Specific client email addresses, comma-separated, in addition to the staff domain |

!!! danger "Fail-closed: blank means locked, not staff-only"
    There is no default grant. A variable left blank grants no one through that channel, and a KB with none of the three set deploys **locked to nobody** rather than public. To let your team in, set `EMAIL_DOMAIN`. To recover a locked-out KB, set the variables and redeploy.

Unauthenticated visitors are redirected to a Cloudflare Access login before they can see anything. The publisher reconciles the Access policies on every deploy, so changing a variable and redeploying is how you change who can read the site.

## What the publisher checks

The publisher treats "the KB is live" and "the KB is gated" as the same event. In order:

1. **Project name validation.** A malformed project name fails the run before it reaches any API call.
2. **Compliance lint.** The Markdown source is linted before any side effects: a deploy workflow must exist, no custom HTML may be tracked, and commercial content is blocked unless the deploy sets `allow-financial: true`. Violations block the deploy.
3. **Access app.** The publisher finds or creates the Cloudflare Access app for the site's domain. On a true first deploy the Pages project doesn't exist yet, so the app is created immediately after the first deploy instead.
4. **Pre-flight.** Before deploying, the publisher probes the live domain. If the site answers publicly, the deploy is blocked.
5. **Direct-upload check.** The Pages project is created (or verified) as a direct-upload project. A project wired to Git via Cloudflare's "Connect to Git" cannot accept these deploys; the publisher detects that and tells you to delete the project and redeploy rather than failing opaquely.
6. **Deploy.** The built site is pushed to Cloudflare Pages. Preview deployments are disabled.
7. **Post-deploy verification.** The publisher probes the live site again. The only positive proof the gate is up is an unauthenticated request being redirected to the Access login. A 200 means the site is public; an unreachable site or an error is not proof either.
8. **Rollback.** If the gate can't be positively confirmed, the deployment is deleted rather than left up. You cannot accidentally ship an ungated site.

!!! note "pages.dev names are globally unique"
    A `<name>.pages.dev` subdomain is unique across all of Cloudflare, not just your account. If your chosen name is taken elsewhere, Cloudflare assigns a suffixed subdomain instead. The publisher detects the real subdomain and gates that, so the KB still works and is still protected; only the exact hostname differs.

## Public mode

Some KBs are meant for everyone: public product documentation, this site included. For those, the publisher supports an opt-in public mode:

```yaml
    uses: Glassdocs/publisher/.github/workflows/deploy-pages.yml@v1
    with:
      project-name: ${{ vars.CF_PAGES_PROJECT }}
      public: true
    secrets: inherit
```

With `public: true`, the publisher skips Cloudflare Access entirely and the site is publicly reachable. The access variables are irrelevant in this mode.

!!! warning "Public is an explicit choice"
    The default remains locked. Nothing you leave unset can make a KB public; only writing `public: true` into the workflow does, and that change is visible in the repo's history like any other. Use it only for documentation intended for the whole world.

## Other workflow inputs

| Input | Default | Purpose |
| --- | --- | --- |
| `allowed-emails` | empty | Comma-separated emails to allow. With no `email-domain`, only these emails get access. |
| `allow-financial` | `false` | Permit financial/contractual content (dedicated pre-sales KBs only) |
| `skip-lint` | `false` | Skip the compliance lint (not recommended) |
| `python-version` | `3.12` | Python version used for the build |
| `wrangler-version` | latest | Pin a specific Wrangler version |

A KB may also pin Zensical or add build plugins via its own `requirements.txt`; when it ships none, the publisher installs Zensical directly.

## See also

- [Managed hosting](hosting.md) if you'd rather not run Cloudflare yourself
- [Admin dashboard](admin.md) for the guided setup flow
- [Security](security.md) for the full security model
- [Writing a KB](authoring.md) for what goes in the pages themselves
