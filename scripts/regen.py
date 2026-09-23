#!/usr/bin/env python3
"""Regenerate .claude-plugin/marketplace.json from the chrischall GitHub repos.

The repo list is the chrischall GitHub account (archived repos skipped; forks
only when listed in INCLUDE_FORKS), and every manifest is read from the repo's
DEFAULT BRANCH on GitHub. Nothing is read from local clones: they may sit on an
unmerged branch, and a repo that isn't cloned would silently drop out.

Each repo's own .claude-plugin/marketplace.json plugin entry is authoritative;
this script only rewrites `source` to point at the GitHub repo (a `git-subdir`
source for monorepo subpackages). metadata.version is carried from
.release-please-manifest.json, which release-please owns.

A plugin that was in the catalog but is no longer found fails the run; pass
`--allow-removal <name>` (repeatable) when the removal is intended.

Needs an authenticated `gh` CLI. Run: python3 scripts/regen.py
"""
import argparse
import json
import os
import subprocess

OWNER = "chrischall"
SELF = "mcp-marketplace"  # don't scan the catalog repo itself
MANIFEST = ".claude-plugin/marketplace.json"
# Forks are usually upstream projects whose own manifest isn't ours to publish.
# These forks are maintained here and ship a chrischall plugin.
INCLUDE_FORKS = {"apple-mail-mcp"}
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def _gh(args):
    res = subprocess.run(["gh", *args], capture_output=True, text=True)
    if res.returncode != 0:
        raise SystemExit(f"gh {' '.join(args)} failed: {res.stderr.strip()}")
    return res.stdout


class GitHub:
    """Reads repos and manifests from GitHub via the `gh` CLI."""

    def __init__(self, run=_gh, owner=OWNER):
        self.run = run
        self.owner = owner

    def list_repos(self):
        return json.loads(self.run(["repo", "list", self.owner, "--limit", "1000",
                                    "--json", "name,isFork,isArchived"]))

    def manifest_paths(self, repo):
        tree = json.loads(self.run(["api", f"repos/{self.owner}/{repo}/git/trees/HEAD?recursive=1"]))
        if tree.get("truncated"):
            raise SystemExit(f"{self.owner}/{repo}: git tree listing truncated; can't find every manifest")
        return sorted(e["path"] for e in tree.get("tree", [])
                      if e.get("type") == "blob"
                      and (e["path"] == MANIFEST or e["path"].endswith("/" + MANIFEST)))

    def read(self, repo, path):
        # No ?ref= — the contents API defaults to the repo's default branch.
        return json.loads(self.run(["api", "-H", "Accept: application/vnd.github.raw+json",
                                    f"repos/{self.owner}/{repo}/contents/{path}"]))


def plugin_entry(repo, rel, data, owner=OWNER):
    entry = (data.get("plugins") or [None])[0]
    if not entry:
        return None
    entry = dict(entry)
    base = f"https://github.com/{owner}/{repo}"
    if rel == ".":
        entry["source"] = {"source": "github", "repo": f"{owner}/{repo}"}
    else:
        # Monorepo subpackage: `github` sources have no `path` field
        # (Claude Code silently ignores it and looks at the repo root),
        # so subdirectory plugins must use the `git-subdir` source type.
        entry["source"] = {"source": "git-subdir", "url": f"{base}.git", "path": rel}
    entry.setdefault("homepage", base if rel == "." else f"{base}/tree/main/{rel}")
    entry.setdefault("repository", base)
    return entry


def collect(source):
    plugins = []
    for r in sorted(source.list_repos(), key=lambda r: r["name"]):
        name = r["name"]
        if name == SELF or r.get("isArchived"):
            continue
        if r.get("isFork") and name not in INCLUDE_FORKS:
            continue
        for path in source.manifest_paths(name):
            if "node_modules/" in path:
                continue
            rel = os.path.dirname(os.path.dirname(path)) or "."
            entry = plugin_entry(name, rel, source.read(name, path))
            if entry:
                plugins.append(entry)
    return plugins


def catalog_version(root=ROOT):
    """metadata.version is owned by release-please (extra-files), so carry the
    released version from .release-please-manifest.json instead of resetting it."""
    with open(os.path.join(root, ".release-please-manifest.json")) as f:
        return json.load(f)["."]


def build_catalog(plugins, version):
    plugins = sorted(plugins, key=lambda p: p["name"])
    names = [p["name"] for p in plugins]
    dups = {n for n in names if names.count(n) > 1}
    if dups:
        raise SystemExit(f"Duplicate plugin names: {dups}")
    return {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": "chrischall",
        "owner": {"name": "Chris Hall", "email": "chris.c.hall@gmail.com"},
        "metadata": {
            "description": "Chris Hall's MCP servers for Claude — real estate, family/school, "
                           "reservations, music, Google Workspace, and productivity tools. Most route "
                           "through your own signed-in browser sessions via the fetchproxy extension.",
            "version": version,
        },
        "plugins": plugins,
    }


def main(argv=None, source=None, root=ROOT):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--allow-removal", action="append", default=[], metavar="NAME",
                    help="allow a currently listed plugin to drop out of the catalog")
    args = ap.parse_args(argv)
    out = os.path.join(root, ".claude-plugin", "marketplace.json")

    try:
        with open(out) as f:
            previous = {p["name"] for p in json.load(f).get("plugins", [])}
    except FileNotFoundError:
        previous = set()

    plugins = collect(source or GitHub())
    gone = sorted(previous - {p["name"] for p in plugins} - set(args.allow_removal))
    if gone:
        raise SystemExit(
            f"These listed plugins were not found on any default branch: {', '.join(gone)}. "
            f"If that is intended, re-run with --allow-removal for each.")

    market = build_catalog(plugins, catalog_version(root))
    with open(out, "w") as f:
        # ensure_ascii=False to match release-please's JSON.stringify output
        json.dump(market, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {len(market['plugins'])} plugins to {os.path.normpath(out)}")
    for p in market["plugins"]:
        s = p["source"]
        loc = s.get("repo") or s.get("url", "")
        if "path" in s:
            loc += "/" + s["path"]
        print(f"  - {p['name']:24} {loc}")


if __name__ == "__main__":
    main()
