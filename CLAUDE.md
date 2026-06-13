# CLAUDE.md — mcp-marketplace

This repo is a **Claude Code marketplace catalog**: a single
`.claude-plugin/marketplace.json` that indexes Chris Hall's MCP servers, each
referenced by its own GitHub source repo. It contains no application code.

## Conventions

- **`.claude-plugin/marketplace.json` is generated, not hand-edited.** It is
  produced by `scripts/regen.py`, which reads each `chrischall/*-mcp` repo's own
  `.claude-plugin/marketplace.json` and rewrites each `source` to a GitHub
  source (adding a `path` for monorepo subpackages like `gogcli-mcp`). To change
  the catalog, add/adjust the source repo, then run `python3 scripts/regen.py`
  and commit the result.
- **Formatting is canonical** `json.dumps(..., indent=2)` + trailing newline.
  CI fails if `marketplace.json` doesn't match that exact formatting.
- **Plugin `name`s must be unique** across the catalog.
- Every plugin entry must have a `name`, a `description`, and a
  `source` of the form `{ "source": "github", "repo": "chrischall/<repo>" }`
  (optionally with `"path": "<subdir>"` for monorepos).
- **`metadata.version`** is the catalog's own version and is bumped by
  release-please (see below). Per-plugin `version` fields mirror their upstream
  source repos and are carried over by `regen.py` — do not bump them here.

## Releases

release-please (`release-type: simple`) drives versioning from Conventional
Commit messages on `main`:

- `fix:` → patch, `feat:` → minor, `feat!:` / `BREAKING CHANGE` → major.
- It opens a release PR that bumps `metadata.version` +
  `.release-please-manifest.json` and updates `CHANGELOG.md`. Merging that PR
  tags `v<version>` and cuts a GitHub Release.
- Add `ready-to-merge` to a PR to arm auto-merge (lands when `ci / ci` is green).
  Add `release-ready` to a release-please PR to run CI/review and ship it.

## CI

`ci.yml` (job `ci`, check context `ci / ci`, the required status check in the
branch ruleset) runs `scripts/validate.py` and the formatting check. No build,
no Node — Python only.
