"""The README's server list is regenerated with the catalog, so it can't go
stale on its own (chrischall/fleet-audit#158)."""
import json
import pathlib
import unittest

from tests.helpers import load

regen = load("regen")
REPO = pathlib.Path(__file__).resolve().parent.parent


def entry(name, category=None, display=None):
    p = {"name": name, "description": f"{name} does things",
         "homepage": f"https://github.com/chrischall/{name}"}
    if category:
        p["category"] = category
    if display:
        p["displayName"] = display
    return p


class RenderServers(unittest.TestCase):
    def test_groups_by_category_with_display_names(self):
        text = regen.render_servers([entry("b-mcp", "music", "Bee"), entry("a-mcp", "finance"),
                                     entry("c-mcp")])
        self.assertEqual(text, (
            "## Servers (3)\n\n"
            "### finance\n\n"
            "- **[a-mcp](https://github.com/chrischall/a-mcp)** (`a-mcp`) — a-mcp does things\n\n"
            "### music\n\n"
            "- **[Bee](https://github.com/chrischall/b-mcp)** (`b-mcp`) — b-mcp does things\n\n"
            "### other\n\n"
            "- **[c-mcp](https://github.com/chrischall/c-mcp)** (`c-mcp`) — c-mcp does things\n\n"))

    def test_update_readme_replaces_only_the_servers_section(self):
        before = "# T\n\n## Install\n\nx\n\n## Servers (1)\n\n### old\n\n- old\n\n## Regenerating\n\ny\n"
        after = regen.update_readme(before, [entry("a-mcp", "finance")])
        self.assertTrue(after.startswith("# T\n\n## Install\n\nx\n\n## Servers (1)\n\n### finance\n"))
        self.assertTrue(after.endswith("\n\n## Regenerating\n\ny\n"))
        self.assertNotIn("- old", after)

    def test_committed_readme_matches_committed_catalog(self):
        plugins = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text())["plugins"]
        readme = (REPO / "README.md").read_text()
        self.assertEqual(regen.update_readme(readme, plugins), readme)


if __name__ == "__main__":
    unittest.main()
