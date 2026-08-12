# Glassdocs/docs — working agreements

This repo is the **public product documentation** for Glassdocs, published to
`https://docs.glassdocs.site` by the `Glassdocs/publisher` action on push to `main`.

## Delivery mode

**Straight to `main`. No branch, no pull request.**

Declared by the maintainer on 2026-08-12. This is the decision the global rule
("read the repo's `## Delivery mode` before your first commit; open a PR and ask
if the repo declares nothing") is looking for — before this, agents correctly
opened PRs and asked, which left PR #8 waiting while the published page stated
something production contradicted.

The consequence to respect: **a push to `main` publishes the public docs site.**
There is no staging step. `docs/llms.txt` and `docs/llms-full.txt` are generated
artifacts — run `python3 scripts/gen_llms_txt.py` and commit the result in the
same change, or the `llms.txt up to date` check fails.

## What lives here

Product documentation only — what Glassdocs is and how to use it. Internal
operational notes belong in the `Glassdocs/glassdocs` monorepo under `docs/`.

Claims about behaviour must match production. The page describing MCP token
custody was wrong for several hours on 2026-08-12 because the OAuth server
shipped and the docs did not follow in the same change.
