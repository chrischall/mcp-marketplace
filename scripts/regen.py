#!/usr/bin/env python3
"""Regenerate .claude-plugin/marketplace.json from every chrischall/*-mcp repo
under ~/git. Each repo's own marketplace.json plugin entries are authoritative;
this script only rewrites `source` to point at the GitHub repo (with a `path`
for monorepo subpackages). Run: python3 scripts/regen.py
"""
import json, os, glob, subprocess

GITROOT = os.path.expanduser("~/git")
SELF = "mcp-marketplace"  # don't scan the catalog repo itself
OUT = os.path.join(os.path.dirname(__file__), "..", ".claude-plugin", "marketplace.json")


def remote(repo):
    try:
        return subprocess.run(
            ["git", "-C", os.path.join(GITROOT, repo), "remote", "get-url", "origin"],
            capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""


def main():
    plugins = []
    for repo in sorted(os.listdir(GITROOT)):
        repodir = os.path.join(GITROOT, repo)
        if repo == SELF or not os.path.isdir(repodir):
            continue
        r = remote(repo)
        if "chrischall/" not in r:
            continue
        # find every marketplace.json in the repo, skipping node_modules
        for mpath in sorted(glob.glob(os.path.join(repodir, "**", ".claude-plugin", "marketplace.json"),
                                      recursive=True)):
            if os.sep + "node_modules" + os.sep in mpath:
                continue
            rel = os.path.relpath(os.path.dirname(os.path.dirname(mpath)), repodir)
            data = json.load(open(mpath))
            entry = (data.get("plugins") or [None])[0]
            if not entry:
                continue
            entry = dict(entry)
            src = {"source": "github", "repo": f"chrischall/{repo}"}
            if rel != ".":
                src["path"] = rel
            entry["source"] = src
            base = f"https://github.com/chrischall/{repo}"
            entry.setdefault("homepage", base if rel == "." else f"{base}/tree/main/{rel}")
            entry.setdefault("repository", base)
            plugins.append(entry)

    plugins.sort(key=lambda p: p["name"])
    market = {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": "chrischall",
        "owner": {"name": "Chris Hall", "email": "chris.c.hall@gmail.com"},
        "metadata": {
            "description": "Chris Hall's MCP servers for Claude — real estate, family/school, "
                           "reservations, music, Google Workspace, and productivity tools. Most route "
                           "through your own signed-in browser sessions via the fetchproxy extension.",
            "version": "1.0.0",
        },
        "plugins": plugins,
    }
    names = [p["name"] for p in plugins]
    dups = {n for n in names if names.count(n) > 1}
    if dups:
        raise SystemExit(f"Duplicate plugin names: {dups}")
    with open(OUT, "w") as f:
        json.dump(market, f, indent=2)
        f.write("\n")
    print(f"Wrote {len(plugins)} plugins to {os.path.normpath(OUT)}")
    for p in plugins:
        s = p["source"]
        loc = s["repo"] + ("/" + s["path"] if "path" in s else "")
        print(f"  - {p['name']:24} {loc}")


if __name__ == "__main__":
    main()
