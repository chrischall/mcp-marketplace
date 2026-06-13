#!/usr/bin/env python3
"""Validate .claude-plugin/marketplace.json — the CI gate for this catalog.

Checks structural integrity rather than regenerating (regen.py depends on the
sibling source repos existing on disk, which they don't in CI):
  - JSON parses
  - top-level $schema / name / metadata.version present
  - every plugin has name + description + a valid source (github+repo, or
    git-subdir+url+path for monorepo subpackages)
  - plugin names are unique
Exit non-zero with a readable report on any failure.
"""
import json
import pathlib
import sys

MANIFEST = pathlib.Path(".claude-plugin/marketplace.json")


def main() -> int:
    try:
        data = json.loads(MANIFEST.read_text())
    except FileNotFoundError:
        print(f"{MANIFEST} not found")
        return 1
    except json.JSONDecodeError as e:
        print(f"{MANIFEST} is not valid JSON: {e}")
        return 1

    errs = []
    if not data.get("$schema"):
        errs.append("missing $schema")
    if not data.get("name"):
        errs.append("missing top-level name")
    if not (data.get("metadata") or {}).get("version"):
        errs.append("missing metadata.version")

    plugins = data.get("plugins") or []
    if not plugins:
        errs.append("no plugins listed")

    names = []
    for i, p in enumerate(plugins):
        where = p.get("name") or f"index {i}"
        names.append(p.get("name"))
        if not p.get("name"):
            errs.append(f"plugin {where}: missing name")
        if not p.get("description"):
            errs.append(f"plugin {where}: missing description")
        src = p.get("source") or {}
        kind = src.get("source")
        if kind == "github" and src.get("repo"):
            pass  # root-level plugin in its own repo
        elif kind == "git-subdir" and src.get("url") and src.get("path"):
            pass  # monorepo subpackage
        else:
            errs.append(
                f"plugin {where}: source must be {{source: github, repo: ...}} "
                f"or {{source: git-subdir, url: ..., path: ...}}"
            )

    dups = sorted({n for n in names if n and names.count(n) > 1})
    if dups:
        errs.append(f"duplicate plugin names: {dups}")

    if errs:
        print(f"{MANIFEST} INVALID:")
        for e in errs:
            print(f"  - {e}")
        return 1

    print(f"{MANIFEST} OK — {len(plugins)} plugins, version {data['metadata']['version']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
