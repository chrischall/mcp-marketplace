"""regen.py reads each repo's DEFAULT BRANCH from GitHub, driven by the org's
repo list, not by whatever ~/git happens to have checked out
(chrischall/fleet-audit#159)."""
import json
import pathlib
import tempfile
import unittest

from tests.helpers import load

regen = load("regen")


def manifest(name, version="1.0.0"):
    return {"name": name, "plugins": [{"name": name, "version": version, "description": f"{name} d"}]}


class FakeSource:
    def __init__(self, repos, files):
        self.repos = repos          # list of {name, isFork, isArchived}
        self.files = files          # {(repo, path): data}

    def list_repos(self):
        return self.repos

    def manifest_paths(self, repo):
        return sorted(p for (r, p) in self.files if r == repo)

    def read(self, repo, path):
        return self.files[(repo, path)]


def repo(name, fork=False, archived=False, visibility="PUBLIC"):
    return {"name": name, "isFork": fork, "isArchived": archived, "visibility": visibility}


class Collect(unittest.TestCase):
    def test_root_and_monorepo_entries_get_github_sources(self):
        src = FakeSource(
            [repo("ofw-mcp"), repo("gogcli-mcp")],
            {("ofw-mcp", ".claude-plugin/marketplace.json"): manifest("ofw", "2.19.0"),
             ("gogcli-mcp", "packages/gogcli-mcp-docs/.claude-plugin/marketplace.json"):
                 manifest("gogcli-mcp-docs")})
        got = {p["name"]: p for p in regen.collect(src)}
        self.assertEqual(got["ofw"]["version"], "2.19.0")
        self.assertEqual(got["ofw"]["source"], {"source": "github", "repo": "chrischall/ofw-mcp"})
        self.assertEqual(got["ofw"]["homepage"], "https://github.com/chrischall/ofw-mcp")
        self.assertEqual(got["gogcli-mcp-docs"]["source"], {
            "source": "git-subdir",
            "url": "https://github.com/chrischall/gogcli-mcp.git",
            "path": "packages/gogcli-mcp-docs"})
        self.assertEqual(got["gogcli-mcp-docs"]["homepage"],
                         "https://github.com/chrischall/gogcli-mcp/tree/main/packages/gogcli-mcp-docs")

    def test_skips_self_archived_unlisted_forks_and_node_modules(self):
        src = FakeSource(
            [repo("mcp-marketplace"), repo("old-mcp", archived=True),
             repo("apple-mcp", fork=True), repo("apple-mail-mcp", fork=True), repo("x-mcp")],
            {("mcp-marketplace", ".claude-plugin/marketplace.json"): manifest("self"),
             ("old-mcp", ".claude-plugin/marketplace.json"): manifest("old"),
             ("apple-mcp", ".claude-plugin/marketplace.json"): manifest("upstream-apple"),
             ("apple-mail-mcp", ".claude-plugin/marketplace.json"): manifest("apple-mail"),
             ("x-mcp", "node_modules/dep/.claude-plugin/marketplace.json"): manifest("dep"),
             ("x-mcp", ".claude-plugin/marketplace.json"): manifest("x")})
        self.assertEqual(sorted(p["name"] for p in regen.collect(src)), ["apple-mail", "x"])

    def test_skips_private_and_internal_repos(self):
        # The catalog is public: a private repo's manifest must not leak its
        # existence, description or version into it (fleet-audit#1054, #550).
        src = FakeSource(
            [repo("pub-mcp"), repo("secret-mcp", visibility="PRIVATE"),
             repo("corp-mcp", visibility="INTERNAL")],
            {("pub-mcp", ".claude-plugin/marketplace.json"): manifest("pub"),
             ("secret-mcp", ".claude-plugin/marketplace.json"): manifest("secret"),
             ("corp-mcp", ".claude-plugin/marketplace.json"): manifest("corp")})
        self.assertEqual([p["name"] for p in regen.collect(src)], ["pub"])

    def test_private_repo_is_never_even_read(self):
        read = []

        class Spy(FakeSource):
            def manifest_paths(self, r):
                read.append(r)
                return super().manifest_paths(r)
        src = Spy([repo("secret-mcp", visibility="PRIVATE")],
                  {("secret-mcp", ".claude-plugin/marketplace.json"): manifest("secret")})
        regen.collect(src)
        self.assertEqual(read, [])

    def test_missing_visibility_is_treated_as_private(self):
        r = repo("unknown-mcp")
        del r["visibility"]
        src = FakeSource([r], {("unknown-mcp", ".claude-plugin/marketplace.json"): manifest("u")})
        self.assertEqual(regen.collect(src), [])

    def test_private_allowlist_opts_a_private_repo_in(self):
        src = FakeSource([repo("secret-mcp", visibility="PRIVATE")],
                         {("secret-mcp", ".claude-plugin/marketplace.json"): manifest("secret")})
        orig = regen.PRIVATE_ALLOWLIST
        regen.PRIVATE_ALLOWLIST = {"secret-mcp"}
        try:
            self.assertEqual([p["name"] for p in regen.collect(src)], ["secret"])
        finally:
            regen.PRIVATE_ALLOWLIST = orig

    def test_private_allowlist_ships_empty(self):
        self.assertEqual(regen.PRIVATE_ALLOWLIST, set())


class Removals(unittest.TestCase):
    def run_main(self, previous_names, source, argv=()):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / ".claude-plugin").mkdir()
            (root / ".release-please-manifest.json").write_text('{".": "1.0.4"}')
            out = root / ".claude-plugin" / "marketplace.json"
            out.write_text(json.dumps({"plugins": [n if isinstance(n, dict) else {"name": n}
                                                   for n in previous_names]}))
            regen.main(list(argv), source=source, root=str(root))
            return json.loads(out.read_text())

    def test_vanished_plugin_fails_loudly(self):
        src = FakeSource([repo("x-mcp")], {("x-mcp", ".claude-plugin/marketplace.json"): manifest("x")})
        with self.assertRaises(SystemExit) as cm:
            self.run_main(["x", "apple-mail"], src)
        self.assertIn("apple-mail", str(cm.exception))

    def test_removal_allowed_explicitly(self):
        src = FakeSource([repo("x-mcp")], {("x-mcp", ".claude-plugin/marketplace.json"): manifest("x")})
        got = self.run_main(["x", "apple-mail"], src, ["--allow-removal", "apple-mail"])
        self.assertEqual([p["name"] for p in got["plugins"]], ["x"])
        self.assertEqual(got["metadata"]["version"], "1.0.4")

    def test_plugin_whose_repo_went_private_drops_out_without_failing(self):
        # Going private is a deliberate exclusion, not a vanished repo.
        src = FakeSource([repo("x-mcp"), repo("secret-mcp", visibility="PRIVATE")],
                         {("x-mcp", ".claude-plugin/marketplace.json"): manifest("x"),
                          ("secret-mcp", ".claude-plugin/marketplace.json"): manifest("secret")})
        secret = {"name": "secret", "source": {"source": "github", "repo": "chrischall/secret-mcp"}}
        got = self.run_main(["x", secret], src)
        self.assertEqual([p["name"] for p in got["plugins"]], ["x"])

    def test_private_monorepo_subpackage_drops_out_without_failing(self):
        src = FakeSource([repo("x-mcp"), repo("mono", visibility="PRIVATE")],
                         {("x-mcp", ".claude-plugin/marketplace.json"): manifest("x")})
        sub = {"name": "sub", "source": {"source": "git-subdir",
                                         "url": "https://github.com/chrischall/mono.git", "path": "p/sub"}}
        got = self.run_main(["x", sub], src)
        self.assertEqual([p["name"] for p in got["plugins"]], ["x"])


class GitHubSource(unittest.TestCase):
    def make(self, responses):
        calls = []

        def run(args):
            calls.append(args)
            for key, value in responses.items():
                if key in " ".join(args):
                    return value
            raise AssertionError(f"unexpected gh call: {args}")
        return regen.GitHub(run=run), calls

    def test_lists_the_org_not_the_local_directory(self):
        gh, calls = self.make({"repo list": json.dumps([repo("a-mcp")])})
        self.assertEqual(gh.list_repos(), [repo("a-mcp")])
        self.assertEqual(calls[0][:3], ["repo", "list", "chrischall"])
        json_fields = calls[0][calls[0].index("--json") + 1].split(",")
        self.assertIn("visibility", json_fields)

    def test_manifest_paths_come_from_the_default_branch_tree(self):
        tree = {"truncated": False, "tree": [
            {"path": ".claude-plugin/marketplace.json", "type": "blob"},
            {"path": "packages/p/.claude-plugin/marketplace.json", "type": "blob"},
            {"path": "README.md", "type": "blob"}]}
        gh, calls = self.make({"git/trees/HEAD": json.dumps(tree)})
        self.assertEqual(gh.manifest_paths("a-mcp"),
                         [".claude-plugin/marketplace.json", "packages/p/.claude-plugin/marketplace.json"])

    def test_truncated_tree_is_an_error_not_a_silent_drop(self):
        gh, _ = self.make({"git/trees/HEAD": json.dumps({"truncated": True, "tree": []})})
        with self.assertRaises(SystemExit):
            gh.manifest_paths("a-mcp")

    def test_read_fetches_default_branch_contents(self):
        gh, calls = self.make({"contents/": json.dumps(manifest("a"))})
        self.assertEqual(gh.read("a-mcp", ".claude-plugin/marketplace.json"), manifest("a"))
        joined = " ".join(calls[0])
        self.assertIn("repos/chrischall/a-mcp/contents/.claude-plugin/marketplace.json", joined)
        self.assertNotIn("ref=", joined)


if __name__ == "__main__":
    unittest.main()
