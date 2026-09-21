"""
Tests for scripts/clean_production.py — per-module revision pruning.

Bug this guards against: each module (content, audio, images, render, ...) has
its OWN independent revision counter in SQLite (pilot.py run(): `rev =
revision + 1` per module). The old prune_unapproved_revisions() took a single
job-wide `approved_rev` (the render module's revision) and applied it while
walking every module's revisions/<module>/ folder. When a module's approved
revision number differs from render's (e.g. render approved@1, images
approved@3 after two rejections), the old code deleted the media of the
actually-approved images/3 and kept the stale, rejected images/1.

scripts/clean_production.py computes ROOT/RUNS_DIR/DB_PATH/EXPORTS_DIR at
import time from Path(__file__). These tests patch those module-level
constants directly to point at a temporary directory instead of copying the
whole repository tree.
"""
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scripts.clean_production as cp


def make_db(db_path: Path, rows):
    """rows: list of (job, module, state, revision) tuples."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS modules("
        "job TEXT, module TEXT, state TEXT, revision INTEGER, "
        "envelope TEXT, hash TEXT, PRIMARY KEY(job, module))"
    )
    for job, module, state, revision in rows:
        conn.execute(
            "INSERT INTO modules(job, module, state, revision, envelope, hash) "
            "VALUES (?,?,?,?,?,?)",
            (job, module, state, revision, "", ""),
        )
    conn.commit()
    conn.close()


def make_rev_file(revisions_dir: Path, module: str, revision, filename: str, content: bytes = b"x" * 1024):
    p = revisions_dir / module / str(revision)
    p.mkdir(parents=True, exist_ok=True)
    f = p / filename
    f.write_bytes(content)
    return f


class CleanProductionPruneTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.runs_dir = self.root / "runs"
        self.state_dir = self.root / ".state"
        self.db_path = self.state_dir / "jobs.sqlite"
        self.exports_dir = self.root / "exports"
        self.runs_dir.mkdir(parents=True)
        self.state_dir.mkdir(parents=True)

        patcher_root = patch.object(cp, "ROOT", self.root)
        patcher_runs = patch.object(cp, "RUNS_DIR", self.runs_dir)
        patcher_db = patch.object(cp, "DB_PATH", self.db_path)
        patcher_exports = patch.object(cp, "EXPORTS_DIR", self.exports_dir)
        patcher_state = patch.object(cp, "STATE_DIR", self.state_dir)
        for p in (patcher_root, patcher_runs, patcher_db, patcher_exports, patcher_state):
            p.start()
            self.addCleanup(p.stop)

        self.addCleanup(self.tmp.cleanup)

    def revisions_dir(self, job_id):
        return self.runs_dir / job_id / "revisions"

    # --- Case 1: original bug scenario ------------------------------------
    def test_prunes_only_within_each_modules_own_approved_revision(self):
        """render approved@1, images approved@3 (after two rejections).
        Must keep render/1 and images/3, and clean images/1 + images/2.
        This reproduces the exact scenario from the bug report."""
        job = "jobA"
        rev_dir = self.revisions_dir(job)
        render1 = make_rev_file(rev_dir, "render", 1, "out.mp4")
        images1 = make_rev_file(rev_dir, "images", 1, "scene1.png")
        images2 = make_rev_file(rev_dir, "images", 2, "scene1.png")
        images3 = make_rev_file(rev_dir, "images", 3, "scene1.png")

        make_db(self.db_path, [
            (job, "render", "approved", 1),
            (job, "images", "approved", 3),
        ])

        cp.prune_unapproved_revisions(job, dry_run=False)

        self.assertTrue(images3.exists(), "approved images revision 3 must survive pruning")
        self.assertTrue(render1.exists(), "approved render revision 1 must survive pruning")
        self.assertFalse(images1.exists(), "rejected images revision 1 must be pruned")
        self.assertFalse(images2.exists(), "rejected images revision 2 must be pruned")

    # --- Case 2: fail-closed on non-approved module -------------------------
    def test_fail_closed_when_module_not_approved(self):
        """A module sitting in needs_changes/pending/stale/blocked must have
        NOTHING deleted from its revisions/ folder — we cannot know which
        draft, if any, is worth keeping."""
        job = "jobB"
        rev_dir = self.revisions_dir(job)
        audio1 = make_rev_file(rev_dir, "audio", 1, "line.wav")
        audio2 = make_rev_file(rev_dir, "audio", 2, "line.wav")

        make_db(self.db_path, [
            (job, "render", "approved", 1),
            (job, "audio", "needs_changes", 2),
        ])

        cp.prune_unapproved_revisions(job, dry_run=False)

        self.assertTrue(audio1.exists(), "non-approved module: revision 1 must be untouched")
        self.assertTrue(audio2.exists(), "non-approved module: revision 2 must be untouched")

    # --- Case 3: module folder with no database row at all ------------------
    def test_module_folder_without_database_row_is_untouched(self):
        job = "jobC"
        rev_dir = self.revisions_dir(job)
        orphan = make_rev_file(rev_dir, "subtitles", 1, "cap.png")

        # 'subtitles' has no row in modules at all.
        make_db(self.db_path, [
            (job, "render", "approved", 1),
        ])

        cp.prune_unapproved_revisions(job, dry_run=False)

        self.assertTrue(orphan.exists(), "module absent from DB must not be pruned")

    # --- Case 4: dry_run must not delete, but must count correctly ----------
    def test_dry_run_reports_bytes_without_deleting(self):
        job = "jobD"
        rev_dir = self.revisions_dir(job)
        render1 = make_rev_file(rev_dir, "render", 1, "out.mp4", content=b"r" * 500)
        images_approved = make_rev_file(rev_dir, "images", 2, "scene1.png", content=b"i" * 700)
        images_draft = make_rev_file(rev_dir, "images", 1, "scene1.png", content=b"d" * 300)

        make_db(self.db_path, [
            (job, "render", "approved", 1),
            (job, "images", "approved", 2),
        ])

        freed = cp.prune_unapproved_revisions(job, dry_run=True)

        self.assertEqual(freed, 300, "dry_run must still count the bytes that WOULD be freed")
        self.assertTrue(render1.exists())
        self.assertTrue(images_approved.exists())
        self.assertTrue(images_draft.exists(), "dry_run must not actually delete anything")

    # --- Case 5: non-media files in an unapproved revision are preserved ----
    def test_non_media_files_preserved_in_unapproved_revision(self):
        job = "jobE"
        rev_dir = self.revisions_dir(job)
        draft_json = make_rev_file(rev_dir, "content", 1, "draft.json", content=b'{"a":1}')
        draft_media = make_rev_file(rev_dir, "content", 1, "still.png")
        approved_dir = rev_dir / "content" / "2"
        approved_dir.mkdir(parents=True, exist_ok=True)
        (approved_dir / "final.json").write_bytes(b'{"a":2}')

        make_db(self.db_path, [
            (job, "render", "approved", 1),
            (job, "content", "approved", 2),
        ])

        cp.prune_unapproved_revisions(job, dry_run=False)

        self.assertTrue(draft_json.exists(), "non-media (.json) files must never be deleted by this tool")
        self.assertFalse(draft_media.exists(), "media (.png) file in the unapproved revision must be pruned")


if __name__ == "__main__":
    unittest.main()
