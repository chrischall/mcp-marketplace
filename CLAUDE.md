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

<!-- pr-workflow:v2 -->
## Pull requests & releases

**Default workflow: branch + PR.** This repo **squash-merges**, so the **PR title MUST be a Conventional Commit** (`fix(scope): …`, `feat(scope): …`) — it becomes the squash commit's subject line, the only thing release-please (`.github/workflows/release-please.yml`) parses to pick the version bump and changelog section. Only `feat` (minor), `fix` (patch), and `!`/`BREAKING CHANGE` (major) cut a release; `perf`/`refactor`/`docs` show in the changelog without bumping; `ci`/`test`/`build`/`chore` are recognised but hidden (`release-please-config.json` → `changelog-sections`). A title without a conventional type is invisible to release-please.

**Don't run `gh pr merge` yourself.** `pr-auto-review.yml` reviews every PR and adds `ready-to-merge` on a `pass` **or** `warn` verdict; `auto-merge.yml` then arms `gh pr merge --auto --squash`. A `warn`/`fail` also opens or updates a single `auto-review-followup` issue capturing the findings; only `fail` blocks auto-merge (override it by adding the label yourself). Open a PR only when the change is done — it auto-merges on a passing review.

### Auto-review follow-up issues

When a PR's auto-review verdict is `warn` or `fail`, the `chrischall/workflows` pipeline opens or updates a single `auto-review-followup` issue ("Auto-review follow-ups for PR #N") whose checklist captures every finding, and links it from the PR's `<!-- auto-review-verdict -->` comment (`📋 Tracking follow-ups: #N`). `warn` (nits only) still auto-merges — the issue carries the nits forward, so most nits are fixed in a *later* PR; `fail` blocks until the important findings are addressed on the PR itself.

When asked to address the auto-review comments / review findings on a PR:

1. Read the verdict comment, open the linked `auto-review-followup` issue, and treat its checklist as the work list (alongside any inline review comments).
2. Resolve each item, checking off only what you've **verified** is genuinely fixed.
3. If every item is resolved on the current PR, add `Closes #<issue>` to that PR's body so the merge closes it; if some are deferred, check off only the resolved ones and leave the issue open.
4. For nits whose `warn` PR already auto-merged, address them in a follow-up PR that references `Closes #<issue>`.

(Mirrors the fleet-wide convention in `~/.claude/CLAUDE.md`.)
