"""metadata.version is owned by release-please (chrischall/fleet-audit#160)."""
import json
import pathlib
import tempfile
import unittest

from tests.helpers import load

regen = load("regen")
validate = load("validate")


def write_repo(root, manifest_version, catalog_version):
    root = pathlib.Path(root)
    (root / ".claude-plugin").mkdir()
    (root / ".release-please-manifest.json").write_text(json.dumps({".": manifest_version}))
    catalog = {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": "chrischall",
        "metadata": {"version": catalog_version},
        "plugins": [{"name": "a", "description": "d",
                     "source": {"source": "github", "repo": "chrischall/a"}}],
    }
    (root / ".claude-plugin" / "marketplace.json").write_text(json.dumps(catalog))
    return root


class RegenVersion(unittest.TestCase):
    def test_catalog_version_comes_from_release_please_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            root = write_repo(d, "1.0.4", "1.0.4")
            self.assertEqual(regen.catalog_version(root), "1.0.4")

    def test_build_catalog_uses_given_version_not_a_literal(self):
        market = regen.build_catalog([], "1.7.3")
        self.assertEqual(market["metadata"]["version"], "1.7.3")


class ValidateVersion(unittest.TestCase):
    def test_matching_versions_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root = write_repo(d, "1.0.4", "1.0.4")
            self.assertEqual(validate.validate(root), [])

    def test_version_drift_from_manifest_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = write_repo(d, "1.0.4", "1.0.0")
            errs = validate.validate(root)
            self.assertTrue(any("1.0.0" in e and "1.0.4" in e for e in errs), errs)


if __name__ == "__main__":
    unittest.main()
