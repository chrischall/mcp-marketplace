#!/usr/bin/env python3
"""Regenerate .claude-plugin/marketplace.json from the chrischall GitHub repos.

The repo list is the chrischall GitHub account's PUBLIC repos (archived repos
skipped; forks only when listed in INCLUDE_FORKS; private/internal repos only
when listed in PRIVATE_ALLOWLIST, and otherwise never even read), and every manifest is read from the repo's
DEFAULT BRANCH on GitHub. Nothing is read from local clones: they may sit on an
unmerged branch, and a repo that isn't cloned would silently drop out.

Each repo's own .claude-plugin/marketplace.json plugin entries (all of them)
are authoritative; this script only rewrites `source` to point at the GitHub repo (a `git-subdir`
source for monorepo subpackages). metadata.version is carried from
.release-please-manifest.json, which release-please owns.

A plugin that was in the catalog but is no longer found fails the run; pass
`--allow-removal <name>` (repeatable) when the removal is intended. A plugin
whose repo is now private is dropped without failing: that exclusion is the
point, not an accident. Empty repos are skipped; a repo that can't be read is
warned about and skipped, but fails the run if it backs an already-listed plugin.

Needs an authenticated `gh` CLI. Run: python3 scripts/regen.py
"""
import argparse
import json
import os
import posixpath
import re
import subprocess
import sys

OWNER = "chrischall"
SELF = "mcp-marketplace"  # don't scan the catalog repo itself
MANIFEST = ".claude-plugin/marketplace.json"
# Forks are usually upstream projects whose own manifest isn't ours to publish.
# These forks are maintained here and ship a chrischall plugin.
INCLUDE_FORKS = {"apple-mail-mcp"}
# This catalog is PUBLIC. A private repo listed here would disclose its
# existence, description, version cadence and source URL, and offer an install
# that fails for everyone but the owner (chrischall/fleet-audit#550, #1054).
# Private/internal repos are skipped unless named here. Keep it empty; make a
# repo public instead of adding it.
PRIVATE_ALLOWLIST = set()
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
                                    "--json", "name,isFork,isArchived,isEmpty,visibility"]))

    def blob_paths(self, repo):
        """Every tracked file on the default branch (cached per repo)."""
        cache = self.__dict__.setdefault("_blobs", {})
        if repo not in cache:
            tree = json.loads(self.run(["api", f"repos/{self.owner}/{repo}/git/trees/HEAD?recursive=1"]))
            if tree.get("truncated"):
                raise SystemExit(f"{self.owner}/{repo}: git tree listing truncated; can't find every manifest")
            cache[repo] = {e["path"] for e in tree.get("tree", []) if e.get("type") == "blob"}
        return cache[repo]

    def manifest_paths(self, repo):
        return sorted(p for p in self.blob_paths(repo)
                      if p == MANIFEST or p.endswith("/" + MANIFEST))

    def read(self, repo, path):
        # No ?ref= — the contents API defaults to the repo's default branch.
        return json.loads(self.run(["api", "-H", "Accept: application/vnd.github.raw+json",
                                    f"repos/{self.owner}/{repo}/contents/{path}"]))


def plugin_entries(repo, rel, data, owner=OWNER):
    """Catalog entries for EVERY plugin in a source manifest (not just the
    first — chrischall/fleet-audit#551). `rel` is the manifest's package dir.

    A plugin's own `source` path ("./" or e.g. "./skills") is resolved against
    that dir and rewritten to a GitHub source; a non-path source maps to the
    dir itself. A path that escapes the repo is an error, not a silent drop.
    """
    entries = []
    for entry in data.get("plugins") or []:
        if not entry:
            continue
        entry = dict(entry)
        where = f"{owner}/{repo}:{rel}/{MANIFEST} plugin {entry.get('name')!r}"
        rel_src = entry.get("source")
        if not isinstance(rel_src, str):
            # Non-path sources (e.g. ioffice-mcp's {"source": "npm", ...}) are
            # replaced by the manifest's own package dir, as before.
            rel_src = "./"
        if rel_src.startswith("/"):
            raise SystemExit(f"{where}: source {rel_src!r} must be a path relative to the manifest")
        sub = posixpath.normpath(posixpath.join(rel, rel_src))
        if sub == ".." or sub.startswith("../"):
            raise SystemExit(f"{where}: source {rel_src!r} points outside the repo")
        base = f"https://github.com/{owner}/{repo}"
        if sub == ".":
            entry["source"] = {"source": "github", "repo": f"{owner}/{repo}"}
        else:
            # Monorepo subpackage: `github` sources have no `path` field
            # (Claude Code silently ignores it and looks at the repo root),
            # so subdirectory plugins must use the `git-subdir` source type.
            entry["source"] = {"source": "git-subdir", "url": f"{base}.git", "path": sub}
        entry.setdefault("homepage", base if sub == "." else f"{base}/tree/main/{sub}")
        entry.setdefault("repository", base)
        entries.append(entry)
    return entries


PLUGIN_ROOT_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s\"']+)")


def untracked_launch_paths(source, repo, rel):
    """`${CLAUDE_PLUGIN_ROOT}/<path>` files a plugin's MCP config launches that
    the repo does not track (chrischall/fleet-audit#1195).

    A git-source install clones the repo and runs no build, so an entry point
    under a gitignored dist/ is simply absent and the server dies at startup.
    The catalog cannot repair it — an entry's own `mcpServers` does not
    override the plugin's, even with `strict: false` — so this only reports.
    Best-effort: an unreadable plugin.json or MCP config is not flagged.
    """
    blob_paths = getattr(source, "blob_paths", None)
    if not callable(blob_paths):
        return []
    pre = "" if rel == "." else rel + "/"
    try:
        manifest = source.read(repo, pre + ".claude-plugin/plugin.json")
        servers = manifest.get("mcpServers") if isinstance(manifest, dict) else None
        if isinstance(servers, str):
            cfg = source.read(repo, posixpath.normpath(pre + servers))
            servers = cfg.get("mcpServers", cfg) if isinstance(cfg, dict) else None
        if not isinstance(servers, dict):
            return []
        tracked = blob_paths(repo)
    except (SystemExit, Exception):  # _gh raises SystemExit
        return []
    missing = []
    for server in servers.values():
        if not isinstance(server, dict):
            continue
        words = [server.get("command") or ""] + [a for a in server.get("args") or [] if isinstance(a, str)]
        for word in words:
            for path in PLUGIN_ROOT_RE.findall(word):
                if posixpath.normpath(pre + path) not in tracked and path not in missing:
                    missing.append(path)
    return missing


def is_listable(r):
    """Public repos only (a missing visibility counts as private), unless allowlisted."""
    return r.get("visibility") == "PUBLIC" or r["name"] in PRIVATE_ALLOWLIST


def collect(source, skipped_private=None, failed=None, broken_launch=None):
    """Plugin entries from every listable repo. Names of repos skipped for being
    private are added to `skipped_private` (a set) when given.

    Empty repos are skipped (the trees API 409s on them). A repo whose
    manifests can't be fetched is warned about and skipped rather than
    aborting every later repo (chrischall/fleet-audit#1053); its name is added
    to `failed` (a set) when given, so main() can refuse to drop a plugin that
    is already listed.

    A plugin whose MCP config launches an untracked `${CLAUDE_PLUGIN_ROOT}`
    file is still listed, with a warning, and recorded in `broken_launch`
    ({plugin name: [paths]}) when given — see untracked_launch_paths()."""
    plugins = []
    for r in sorted(source.list_repos(), key=lambda r: r["name"]):
        name = r["name"]
        if name == SELF or r.get("isArchived") or r.get("isEmpty"):
            continue
        if r.get("isFork") and name not in INCLUDE_FORKS:
            continue
        if not is_listable(r):
            if skipped_private is not None:
                skipped_private.add(name)
            continue
        try:
            found = [(path, source.read(name, path)) for path in source.manifest_paths(name)
                     if "node_modules/" not in path]
        except (SystemExit, Exception) as e:  # _gh raises SystemExit
            print(f"warning: skipping {OWNER}/{name}: {e}", file=sys.stderr)
            if failed is not None:
                failed.add(name)
            continue
        for path, data in found:
            rel = os.path.dirname(os.path.dirname(path)) or "."
            entries = plugin_entries(name, rel, data)
            missing = untracked_launch_paths(source, name, rel)
            if missing:
                for e in entries:
                    print(f"warning: plugin {e.get('name')!r} ({OWNER}/{name}) launches "
                          f"{', '.join(missing)}, which the repo does not track; a "
                          f"git-source install will fail to start it", file=sys.stderr)
                    if broken_launch is not None:
                        broken_launch[e.get("name")] = missing
            plugins.extend(entries)
    return plugins


def source_repo(entry):
    """The repo name a catalog entry's `source` points at, or None."""
    s = entry.get("source") or {}
    loc = s.get("repo") or s.get("url") or ""
    name = loc.rstrip("/").rsplit("/", 1)[-1]
    return name.removesuffix(".git") or None


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


def render_servers(plugins):
    """The README's `## Servers` section: one list per category."""
    by_cat = {}
    for p in sorted(plugins, key=lambda p: p["name"]):
        by_cat.setdefault(p.get("category") or "other", []).append(p)
    out = [f"## Servers ({len(plugins)})\n\n"]
    for cat in sorted(by_cat):
        out.append(f"### {cat}\n\n")
        for p in by_cat[cat]:
            out.append(f"- **[{p.get('displayName') or p['name']}]({p['homepage']})** "
                       f"(`{p['name']}`) — {p['description']}\n")
        out.append("\n")
    return "".join(out)


def update_readme(text, plugins):
    start = text.index("## Servers")
    end = text.index("\n## ", start) + 1
    return text[:start] + render_servers(plugins) + text[end:]


def main(argv=None, source=None, root=ROOT):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--allow-removal", action="append", default=[], metavar="NAME",
                    help="allow a currently listed plugin to drop out of the catalog")
    args = ap.parse_args(argv)
    out = os.path.join(root, ".claude-plugin", "marketplace.json")

    try:
        with open(out) as f:
            previous = {p["name"]: source_repo(p) for p in json.load(f).get("plugins", [])}
    except FileNotFoundError:
        previous = {}

    private, failed = set(), set()
    plugins = collect(source or GitHub(), private, failed)
    unreadable = sorted(n for n, r in previous.items() if r in failed)
    if unreadable:
        raise SystemExit(
            f"Could not read the source repo of these listed plugins: {', '.join(unreadable)} "
            f"(repos: {', '.join(sorted(failed))}). Not regenerating with them missing.")
    now_private = {n for n, r in previous.items() if r in private}
    for n in sorted(now_private):
        print(f"Dropping {n}: its source repo is not public")
    gone = sorted(set(previous) - {p["name"] for p in plugins} - now_private
                  - set(args.allow_removal))
    if gone:
        raise SystemExit(
            f"These listed plugins were not found on any default branch: {', '.join(gone)}. "
            f"If that is intended, re-run with --allow-removal for each.")

    market = build_catalog(plugins, catalog_version(root))
    with open(out, "w") as f:
        # ensure_ascii=False to match release-please's JSON.stringify output
        json.dump(market, f, indent=2, ensure_ascii=False)
        f.write("\n")
    readme = os.path.join(root, "README.md")
    if os.path.exists(readme):
        with open(readme) as f:
            text = f.read()
        with open(readme, "w") as f:
            f.write(update_readme(text, market["plugins"]))
    print(f"Wrote {len(market['plugins'])} plugins to {os.path.normpath(out)}")
    for p in market["plugins"]:
        s = p["source"]
        loc = s.get("repo") or s.get("url", "")
        if "path" in s:
            loc += "/" + s["path"]
        print(f"  - {p['name']:24} {loc}")


if __name__ == "__main__":
    main()
