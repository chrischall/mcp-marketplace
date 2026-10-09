#!/usr/bin/env python3
"""Validate .claude-plugin/marketplace.json — the CI gate for this catalog.

Checks structural integrity rather than regenerating (regen.py reads every
source repo from GitHub, which a PR's CI token can't do across private repos):
  - JSON parses
  - top-level $schema / name / metadata.version present
  - every plugin has name + description + a valid source (github+repo, or
    git-subdir+url+path for monorepo subpackages)
  - every source, homepage and repository points at a chrischall GitHub repo,
    and a git-subdir path is a clean relative path (a catalog entry decides
    what code users clone and run, so this is enforced here, not left to
    review — chrischall/fleet-audit#553)
  - plugin names are unique
  - metadata.version equals .release-please-manifest.json (release-please owns
    it; a regen that resets it is caught here)
Exit non-zero with a readable report on any failure.
"""
import json
import pathlib
import re
import sys

MANIFEST = pathlib.Path(".claude-plugin/marketplace.json")
RELEASE_MANIFEST = pathlib.Path(".release-please-manifest.json")
OWNER = "chrischall"
_NAME = r"[A-Za-z0-9._-]*[A-Za-z0-9_-][A-Za-z0-9._-]*"  # a repo name, not "." / ".."
REPO_RE = re.compile(rf"{OWNER}/{_NAME}")
URL_RE = re.compile(rf"https://github\.com/{OWNER}/{_NAME}\.git")
LINK_RE = re.compile(rf"https://github\.com/{OWNER}/{_NAME}(/[^\s]*)?")


def _clean_rel_path(path):
    parts = path.split("/")
    return (not path.startswith("/") and "\\" not in path
            and all(part not in ("", ".", "..") for part in parts))


def validate(root=pathlib.Path(".")) -> list:
    """Return a list of error strings for the catalog under `root`."""
    root = pathlib.Path(root)
    try:
        data = json.loads((root / MANIFEST).read_text())
    except FileNotFoundError:
        return [f"{MANIFEST} not found"]
    except json.JSONDecodeError as e:
        return [f"{MANIFEST} is not valid JSON: {e}"]

    errs = []
    if not data.get("$schema"):
        errs.append("missing $schema")
    if not data.get("name"):
        errs.append("missing top-level name")
    if not (data.get("metadata") or {}).get("version"):
        errs.append("missing metadata.version")
    else:
        try:
            released = json.loads((root / RELEASE_MANIFEST).read_text()).get(".")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            errs.append(f"cannot read {RELEASE_MANIFEST}: {e}")
        else:
            if data["metadata"]["version"] != released:
                errs.append(
                    f"metadata.version is {data['metadata']['version']} but "
                    f"{RELEASE_MANIFEST} says {released} — release-please owns "
                    f"this field; don't reset it")

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
            # root-level plugin in its own repo
            if not REPO_RE.fullmatch(str(src["repo"])):
                errs.append(f"plugin {where}: source.repo {src['repo']!r} "
                            f"is not a {OWNER}/<repo> repo")
        elif kind == "git-subdir" and src.get("url") and src.get("path"):
            # monorepo subpackage
            if not URL_RE.fullmatch(str(src["url"])):
                errs.append(f"plugin {where}: source.url {src['url']!r} is not "
                            f"https://github.com/{OWNER}/<repo>.git")
            if not _clean_rel_path(str(src["path"])):
                errs.append(f"plugin {where}: source.path {src['path']!r} must be "
                            f"a relative path without '.' or '..' segments")
        else:
            errs.append(
                f"plugin {where}: source must be {{source: github, repo: ...}} "
                f"or {{source: git-subdir, url: ..., path: ...}}"
            )
        for field in ("homepage", "repository"):
            link = p.get(field)
            if link is not None and not LINK_RE.fullmatch(str(link)):
                errs.append(f"plugin {where}: {field} {link!r} is not under "
                            f"https://github.com/{OWNER}/")

    dups = sorted({n for n in names if n and names.count(n) > 1})
    if dups:
        errs.append(f"duplicate plugin names: {dups}")

    return errs


def main() -> int:
    errs = validate()
    if errs:
        print(f"{MANIFEST} INVALID:")
        for e in errs:
            print(f"  - {e}")
        return 1

    data = json.loads(MANIFEST.read_text())
    print(f"{MANIFEST} OK — {len(data['plugins'])} plugins, version {data['metadata']['version']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
