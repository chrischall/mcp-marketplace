"""validate.py pins every plugin source to a chrischall GitHub repo, so CI —
not only the LLM reviewer — rejects an entry pointing at someone else's code
(chrischall/fleet-audit#553)."""
import json
import pathlib
import tempfile
import unittest

from tests.helpers import load

validate = load("validate")


def errors_for(plugin):
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / ".claude-plugin").mkdir()
        (root / ".release-please-manifest.json").write_text('{".": "1.0.0"}')
        catalog = {
            "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
            "name": "chrischall",
            "metadata": {"version": "1.0.0"},
            "plugins": [dict({"name": "p", "description": "d"}, **plugin)],
        }
        (root / ".claude-plugin" / "marketplace.json").write_text(json.dumps(catalog))
        return validate.validate(root)


def github(repo):
    return {"source": {"source": "github", "repo": repo}}


def subdir(url, path="packages/p"):
    return {"source": {"source": "git-subdir", "url": url, "path": path}}


class SourceAllowlist(unittest.TestCase):
    def test_chrischall_github_repo_passes(self):
        self.assertEqual(errors_for(github("chrischall/ofw-mcp")), [])

    def test_chrischall_git_subdir_passes(self):
        self.assertEqual(errors_for(subdir("https://github.com/chrischall/gogcli-mcp.git",
                                           "packages/gogcli-mcp-docs")), [])

    def test_github_repo_of_another_owner_fails(self):
        for repo in ("evil/ofw-mcp", "chrischall-evil/ofw-mcp", "chrischall/ofw-mcp/../x",
                     "chrischall/", "ofw-mcp"):
            with self.subTest(repo=repo):
                self.assertTrue(errors_for(github(repo)))

    def test_git_subdir_url_of_another_owner_or_host_fails(self):
        for url in ("https://github.com/evil/gogcli-mcp.git",
                    "https://gitlab.com/chrischall/gogcli-mcp.git",
                    "http://github.com/chrischall/gogcli-mcp.git",
                    "https://github.com.evil.io/chrischall/gogcli-mcp.git",
                    "https://github.com/chrischall/gogcli-mcp",
                    "git@github.com:chrischall/gogcli-mcp.git"):
            with self.subTest(url=url):
                self.assertTrue(errors_for(subdir(url)))

    def test_git_subdir_path_must_be_clean_and_relative(self):
        url = "https://github.com/chrischall/gogcli-mcp.git"
        for path in ("/etc", "../other", "packages/../../x", "packages/p/..", "."):
            with self.subTest(path=path):
                self.assertTrue(errors_for(subdir(url, path)))

    def test_homepage_and_repository_must_be_chrischall_github(self):
        ok = github("chrischall/ofw-mcp")
        self.assertEqual(errors_for(dict(ok, homepage="https://github.com/chrischall/ofw-mcp",
                                         repository="https://github.com/chrischall/ofw-mcp")), [])
        for field in ("homepage", "repository"):
            with self.subTest(field=field):
                self.assertTrue(errors_for(dict(ok, **{field: "https://github.com/evil/ofw-mcp"})))


if __name__ == "__main__":
    unittest.main()
