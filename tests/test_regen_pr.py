"""scripts/regen-pr.sh, the step regen.yml runs after regen.py: open/update
the bot/regen-catalog PR when the catalog changed, and close a stale one when
the catalog is already current (a leftover regen PR carries outdated plugin
versions and must not be mergeable later — follow-up #30)."""
import os
import pathlib
import stat
import subprocess
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "regen-pr.sh"

FAKE_GH = """#!/bin/sh
echo "$*" >> "$GH_LOG"
case "$1 $2" in
  "pr list")
    [ -n "$GH_LIST_FAIL" ] && { echo "gh: HTTP 502" >&2; exit 1; }
    [ -n "$OPEN_PR" ] && echo "$OPEN_PR" ;;
esac
exit 0
"""


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class RegenPr(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.remote = self.tmp / "remote.git"
        self.work = self.tmp / "work"
        self.bin = self.tmp / "bin"
        self.log = self.tmp / "gh.log"
        self.log.write_text("")
        git(self.tmp, "init", "-q", "--bare", "-b", "main", str(self.remote))
        git(self.tmp, "init", "-q", "-b", "main", str(self.work))
        (self.work / ".claude-plugin").mkdir()
        (self.work / ".claude-plugin" / "marketplace.json").write_text("{}\n")
        (self.work / "README.md").write_text("# r\n")
        git(self.work, "add", ".")
        git(self.work, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
        git(self.work, "remote", "add", "origin", str(self.remote))
        git(self.work, "push", "-q", "origin", "main")
        self.bin.mkdir()
        gh = self.bin / "gh"
        gh.write_text(FAKE_GH)
        gh.chmod(gh.stat().st_mode | stat.S_IEXEC)

    def run_script(self, open_pr="", list_fails=False):
        env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}",
                   GH_LOG=str(self.log), OPEN_PR=open_pr, BRANCH="bot/regen-catalog",
                   GH_LIST_FAIL="1" if list_fails else "")
        r = subprocess.run(["bash", str(SCRIPT)], cwd=self.work, env=env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return self.log.read_text().splitlines()

    def test_current_catalog_closes_stale_regen_pr(self):
        calls = self.run_script(open_pr="42")
        closes = [c for c in calls if c.startswith("pr close")]
        self.assertEqual(len(closes), 1, calls)
        self.assertIn("42", closes[0])
        self.assertIn("--delete-branch", closes[0])
        self.assertFalse(any(c.startswith("pr create") for c in calls), calls)

    def test_current_catalog_without_open_pr_does_nothing(self):
        calls = self.run_script(open_pr="")
        self.assertFalse(any(c.startswith(("pr close", "pr create")) for c in calls), calls)

    def test_current_catalog_survives_failed_pr_lookup(self):
        # A transient `gh pr list` failure must not fail the regen run: with
        # nothing to publish, the stale-PR sweep is best-effort and the next
        # scheduled run retries it (follow-up #33).
        calls = self.run_script(open_pr="42", list_fails=True)
        self.assertFalse(any(c.startswith(("pr close", "pr create")) for c in calls), calls)

    def test_changed_catalog_opens_pr_and_never_closes(self):
        (self.work / "README.md").write_text("# changed\n")
        calls = self.run_script(open_pr="")
        self.assertTrue(any(c.startswith("pr create") for c in calls), calls)
        self.assertFalse(any(c.startswith("pr close") for c in calls), calls)
        out = subprocess.run(["git", "ls-remote", "--heads", str(self.remote), "bot/regen-catalog"],
                             capture_output=True, text=True).stdout
        self.assertIn("bot/regen-catalog", out)

    def test_changed_catalog_with_open_pr_only_updates_branch(self):
        (self.work / "README.md").write_text("# changed\n")
        calls = self.run_script(open_pr="42")
        self.assertFalse(any(c.startswith(("pr create", "pr close")) for c in calls), calls)


if __name__ == "__main__":
    unittest.main()
