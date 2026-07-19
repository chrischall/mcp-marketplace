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
- Every plugin entry must have a `name`, a `description`, and a `source`. A
  root-level plugin uses
  `{ "source": "github", "repo": "chrischall/<repo>" }`. A monorepo subpackage
  uses `{ "source": "git-subdir", "url": "https://github.com/chrischall/<repo>.git", "path": "<subdir>" }`
  — the `github` source type has **no** `path` field (Claude Code silently
  ignores it and looks at the repo root), so subdirectory plugins must use
  `git-subdir` or they won't load.
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
- `ready-to-merge` arms auto-merge (lands when `ci-gated` is green); auto-review
  adds it on a `pass`/`warn` verdict, or add it yourself to override a `fail`.
  Add `release-ready` to a release-please PR to run CI/review and ship it.

## CI

`ci.yml` (job `ci`, check context `ci-gated`, the required status check in the
branch ruleset) runs `scripts/validate.py` and the formatting check. No build,
no Node — Python only.

<!-- pr-workflow:v3 -->
## Pull requests & release notes

Fleet policy — Conventional-Commit PR titles, labels, the auto-review /
auto-merge ladder, auto-review follow-up issues, PR timing, and release PRs —
lives in `~/.claude/CLAUDE.md`. Don't restate it here; the copies drifted.

Shared technical conventions (publishing, bundling, versioning guards,
write-verification, transport archetypes, testing traps) live in
[`chrischall/workflows`](https://github.com/chrischall/workflows):
`docs/fleet-conventions.md`, plus `README.md` for the CI pipeline contract.

