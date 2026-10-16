"""A git-source plugin install clones the repo and runs no build, so a plugin
MCP config that launches `${CLAUDE_PLUGIN_ROOT}/dist/index.js` from a repo
that gitignores dist/ installs fine and then dies with MODULE_NOT_FOUND
(chrischall/fleet-audit#1195, reproduced with `claude plugin install
skill-mcp@chrischall` in an isolated config dir). regen.py cannot fix that
from the catalog (a catalog entry's `mcpServers` does not override the
plugin's own, even with `strict: false`), so it names every such plugin."""
import contextlib
import io
import unittest

from tests.helpers import load

regen = load("regen")


class Source:
    def __init__(self, files, blobs):
        self.files = files      # {(repo, path): data}
        self.blobs = blobs      # {repo: set(paths)}

    def list_repos(self):
        return [{"name": r, "isFork": False, "isArchived": False, "visibility": "PUBLIC"}
                for r in sorted(self.blobs)]

    def manifest_paths(self, repo):
        return sorted(p for (r, p) in self.files if r == repo and p.endswith("marketplace.json"))

    def blob_paths(self, repo):
        return self.blobs[repo]

    def read(self, repo, path):
        if (repo, path) not in self.files:
            raise SystemExit(f"404 {repo}/{path}")
        return self.files[(repo, path)]


def plugin(repo, cfg, rel="", mcp_servers="./.mcp.json"):
    pre = f"{rel}/" if rel else ""
    return {
        (repo, f"{pre}.claude-plugin/marketplace.json"):
            {"plugins": [{"name": repo, "version": "1.0.0", "description": "d"}]},
        (repo, f"{pre}.claude-plugin/plugin.json"): {"name": repo, "mcpServers": mcp_servers},
        (repo, f"{pre}.mcp.json"): cfg,
    }


def node(path):
    return {"mcpServers": {"s": {"command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/" + path]}}}


class LaunchPaths(unittest.TestCase):
    def test_flags_an_untracked_dist_entry_point(self):
        src = Source(plugin("a-mcp", node("dist/index.js")),
                     {"a-mcp": {".claude-plugin/marketplace.json", ".mcp.json", "src/index.ts"}})
        self.assertEqual(regen.untracked_launch_paths(src, "a-mcp", "."), ["dist/index.js"])

    def test_tracked_entry_point_and_npx_are_fine(self):
        files = {**plugin("b-mcp", node("build/index.js")),
                 **plugin("c-mcp", {"mcpServers": {"s": {"command": "npx", "args": ["-y", "c-mcp"]}}})}
        src = Source(files, {"b-mcp": {"build/index.js"}, "c-mcp": set()})
        self.assertEqual(regen.untracked_launch_paths(src, "b-mcp", "."), [])
        self.assertEqual(regen.untracked_launch_paths(src, "c-mcp", "."), [])

    def test_resolves_against_a_monorepo_subpackage(self):
        src = Source(plugin("mono", node("dist/index.js"), rel="packages/x"),
                     {"mono": {"packages/x/dist/index.js"}})
        self.assertEqual(regen.untracked_launch_paths(src, "mono", "packages/x"), [])

    def test_inline_mcp_servers_object(self):
        src = Source(plugin("d-mcp", None, mcp_servers=node("dist/x.js")["mcpServers"]),
                     {"d-mcp": set()})
        self.assertEqual(regen.untracked_launch_paths(src, "d-mcp", "."), ["dist/x.js"])

    def test_no_plugin_json_or_no_mcp_is_not_flagged(self):
        files = {("e-mcp", ".claude-plugin/marketplace.json"): {"plugins": []}}
        src = Source(files, {"e-mcp": set()})
        self.assertEqual(regen.untracked_launch_paths(src, "e-mcp", "."), [])

    def test_collect_warns_and_still_lists_the_plugin(self):
        src = Source(plugin("a-mcp", node("dist/index.js")), {"a-mcp": set()})
        broken = {}
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            got = regen.collect(src, broken_launch=broken)
        self.assertEqual([p["name"] for p in got], ["a-mcp"])
        self.assertEqual(broken, {"a-mcp": ["dist/index.js"]})
        self.assertIn("a-mcp", err.getvalue())
        self.assertIn("dist/index.js", err.getvalue())

    def test_source_without_blob_paths_skips_the_check(self):
        class Old(Source):
            blob_paths = None
        src = Old(plugin("a-mcp", node("dist/index.js")), {"a-mcp": set()})
        self.assertEqual(regen.untracked_launch_paths(src, "a-mcp", "."), [])


if __name__ == "__main__":
    unittest.main()
