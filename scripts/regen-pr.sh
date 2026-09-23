#!/usr/bin/env bash
# Run by regen.yml after scripts/regen.py + validate.py. Publishes the
# regenerated catalog as ONE PR from $BRANCH (default bot/regen-catalog):
#   - catalog changed  -> force-push $BRANCH and open the PR if none is open;
#   - catalog current  -> close any still-open regen PR and delete its branch,
#     so a stale PR carrying outdated plugin versions can't be merged later.
# Needs GH_TOKEN for `gh`, and a checkout whose `origin` it may push to.
set -euo pipefail

BRANCH="${BRANCH:-bot/regen-catalog}"
FILES=(.claude-plugin/marketplace.json README.md)

open_pr() {
  gh pr list --head "$BRANCH" --state open --json number --jq '.[].number'
}

if git diff --quiet -- "${FILES[@]}"; then
  echo "catalog already current"
  pr="$(open_pr)"
  if [ -n "$pr" ]; then
    echo "closing stale regen PR #$pr"
    gh pr close "$pr" --delete-branch \
      --comment "Closing: \`main\` already matches the regenerated catalog, so this PR is stale (regen.yml)."
  fi
  exit 0
fi

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git switch -C "$BRANCH"
git add "${FILES[@]}"
git commit -m "fix: refresh the plugin catalog from the source repos"
git push --force origin "$BRANCH"
if [ -z "$(open_pr)" ]; then
  gh pr create --head "$BRANCH" --base main \
    --title "fix: refresh the plugin catalog from the source repos" \
    --body "Automated \`scripts/regen.py\` run (regen.yml): rebuilt the catalog and README server list from every chrischall repo's default branch."
fi
