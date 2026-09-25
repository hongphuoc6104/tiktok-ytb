"""characters.py: channel -> canonical mascot resolution, isolated fixtures only."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from pilot import ROOT, Blocked, digest, read, write
import characters as ch


def _write_mascot(root, folder_id, *, reference='reference-v1.png', media_id=None, extra=None):
    d = Path(root) / 'assets/characters' / folder_id
    d.mkdir(parents=True, exist_ok=True)
    cj = {'id': folder_id}
    if reference is not None:
        Image.new('RGB', (8, 8)).save(d / reference)
        cj['reference'] = reference
    cj['flow'] = {'media_id': media_id}
    if extra:
        cj.update(extra)
    write(d / 'character.json', cj)
    return d


class ResolveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_no_channel_resolves_default_channel_mascot_current_behaviour(self):
        _write_mascot(self.root, 'channel-mascot', media_id='M-VOCAB')
        m = ch.resolve(self.root, None)
        self.assertEqual(m['id'], 'channel-mascot')
        self.assertEqual(m['character_id'], 'CH01')
        self.assertEqual(m['media_id'], 'M-VOCAB')
        self.assertTrue(m['reference_path'].is_file())

    def test_unknown_channel_also_falls_back_to_default(self):
        _write_mascot(self.root, 'channel-mascot', media_id='M-VOCAB')
        m = ch.resolve(self.root, 'some-other-channel-nobody-registered')
        self.assertEqual(m['id'], 'channel-mascot')

    def test_tiensu_channel_resolves_its_own_mascot_not_vocab(self):
        _write_mascot(self.root, 'channel-mascot', media_id='M-VOCAB')
        _write_mascot(self.root, 'tiensu-mascot', media_id='M-TIENSU')
        m = ch.resolve(self.root, 'tiensu')
        self.assertEqual(m['id'], 'tiensu-mascot')
        self.assertEqual(m['media_id'], 'M-TIENSU')
        self.assertNotIn('channel-mascot', str(m['reference_path']))

    def test_missing_reference_raises_actionable_error_not_silent_vocab_fallback(self):
        _write_mascot(self.root, 'channel-mascot', media_id='M-VOCAB')  # vocab mascot IS available
        _write_mascot(self.root, 'tiensu-mascot', reference=None)  # tiensu has no reference yet
        with self.assertRaises(Blocked) as cm:
            ch.resolve(self.root, 'tiensu')
        msg = str(cm.exception)
        self.assertIn('MASCOT_REFERENCE_MISSING', msg)
        self.assertIn('tiensu-mascot', msg)
        self.assertIn('pilot.py mascot-reference', msg)
        self.assertNotIn('channel-mascot', msg)  # never points at a substitute mascot

    def test_missing_character_json_is_also_reference_missing(self):
        (self.root / 'assets/characters/channel-mascot').mkdir(parents=True)
        with self.assertRaisesRegex(Blocked, 'MASCOT_REFERENCE_MISSING'):
            ch.resolve(self.root, None)

    def test_require_media_id_raises_distinct_code_when_reference_exists_but_unregistered(self):
        _write_mascot(self.root, 'tiensu-mascot', media_id=None)
        with self.assertRaisesRegex(Blocked, 'MASCOT_MEDIA_ID_MISSING'):
            ch.resolve(self.root, 'tiensu', require_media_id=True)
        # Without the stricter flag, the same mascot resolves fine (image-only generation).
        m = ch.resolve(self.root, 'tiensu')
        self.assertIsNone(m['media_id'])

    def test_try_resolve_returns_none_instead_of_raising(self):
        self.assertIsNone(ch.try_resolve(self.root, 'tiensu'))
        _write_mascot(self.root, 'tiensu-mascot', media_id='M')
        self.assertIsNotNone(ch.try_resolve(self.root, 'tiensu'))


class MascotForTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        _write_mascot(self.root, 'channel-mascot', media_id='M-VOCAB')
        _write_mascot(self.root, 'tiensu-mascot', media_id='M-TIENSU')

    def test_accepts_brief_dict(self):
        p = SimpleNamespace(root=self.root)
        self.assertEqual(ch.mascot_for(p, {'channel': 'tiensu'})['id'], 'tiensu-mascot')
        self.assertEqual(ch.mascot_for(p, {'aspect_ratio': '16:9'})['id'], 'channel-mascot')
        self.assertEqual(ch.mascot_for(p, None)['id'], 'channel-mascot')

    def test_accepts_brief_tuple_like_pilot_brief_returns(self):
        p = SimpleNamespace(root=self.root)
        self.assertEqual(ch.mascot_for(p, ({'channel': 'tiensu'}, 1, 'hash'))['id'], 'tiensu-mascot')

    def test_accepts_job_id_and_looks_up_via_p_brief(self):
        calls = []

        class FakeP:
            root = self.root

            def brief(self, j):
                calls.append(j)
                return ({'channel': 'tiensu'}, 1, 'h') if j == 'tiensu-job' else None

        p = FakeP()
        self.assertEqual(ch.mascot_for(p, 'tiensu-job')['id'], 'tiensu-mascot')
        self.assertEqual(calls, ['tiensu-job'])
        self.assertEqual(ch.mascot_for(p, 'legacy-job-no-brief')['id'], 'channel-mascot')

    def test_try_mascot_for_never_raises(self):
        p = SimpleNamespace(root=self.root)
        # Unknown channel legitimately falls back to the default vocab mascot, which setUp provided.
        self.assertEqual(ch.try_mascot_for(p, {'channel': 'unknown-and-unwritten'})['id'], 'channel-mascot')
        _write_mascot(self.root, 'channel-mascot', reference=None)  # now break the fallback too
        self.assertIsNone(ch.try_mascot_for(p, {'channel': 'unknown-and-unwritten'}))


class HelperTests(unittest.TestCase):
    def test_resolve_mascot_id_known_and_unknown(self):
        self.assertEqual(ch.resolve_mascot_id('tiensu'), 'tiensu-mascot')
        self.assertEqual(ch.resolve_mascot_id('default'), 'channel-mascot')
        self.assertEqual(ch.resolve_mascot_id(None), 'channel-mascot')
        self.assertEqual(ch.resolve_mascot_id('channel-mascot'), 'channel-mascot')
        self.assertEqual(ch.resolve_mascot_id('tiensu-mascot'), 'tiensu-mascot')
        with self.assertRaises(Blocked):
            ch.resolve_mascot_id('nope-not-a-channel')

    def test_job_of_parses_runs_path_and_handles_no_runs_segment(self):
        self.assertEqual(ch.job_of(Path('/x/runs/abc123/flow/attempts/k/download')), 'abc123')
        self.assertIsNone(ch.job_of(Path('/x/y/z')))
        self.assertIsNone(ch.job_of(Path('/x/runs')))  # 'runs' with nothing after it


class SetReferenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        (self.root / 'assets/characters/tiensu-mascot').mkdir(parents=True)
        write(self.root / 'assets/characters/tiensu-mascot/character.json',
              {'id': 'tiensu-mascot', 'reference': None, 'sha256': None})
        self.src = self.root / 'approved.png'
        Image.new('RGB', (16, 16), (10, 20, 30)).save(self.src)

    def test_copies_file_and_fills_reference_and_sha256(self):
        result = ch.set_reference(self.root, 'tiensu', str(self.src))
        dest = self.root / 'assets/characters/tiensu-mascot/reference-v1.png'
        self.assertTrue(dest.is_file())
        self.assertEqual(result['sha256'], digest(dest))
        cj = read(self.root / 'assets/characters/tiensu-mascot/character.json')
        self.assertEqual(cj['reference'], 'reference-v1.png')
        self.assertEqual(cj['sha256'], digest(dest))
        # And the resolver now finds it -- the previously-missing mascot is fixed, not worked around.
        m = ch.resolve(self.root, 'tiensu')
        self.assertEqual(m['reference_path'], dest)

    def test_does_not_generate_only_copies_an_existing_approved_file(self):
        before = ch.try_resolve(self.root, 'tiensu')
        self.assertIsNone(before)
        ch.set_reference(self.root, 'tiensu', str(self.src))
        # The copied bytes are exactly the source file's -- nothing was regenerated.
        dest = self.root / 'assets/characters/tiensu-mascot/reference-v1.png'
        self.assertEqual(dest.read_bytes(), self.src.read_bytes())

    def test_missing_source_file_is_blocked(self):
        with self.assertRaises(Blocked):
            ch.set_reference(self.root, 'tiensu', str(self.root / 'nope.png'))

    def test_unknown_mascot_folder_is_blocked(self):
        with self.assertRaises(Blocked):
            ch.set_reference(self.root, 'a-channel-with-no-folder', str(self.src))


class UnchangedVocabBehaviourTests(unittest.TestCase):
    """The real repo's committed vocab mascot must resolve exactly as before:
    same id, same reference file, same recorded media id -- this feature adds
    tiensu routing without touching the existing (missing-channel) path."""

    def test_real_repo_channel_mascot_still_resolves_as_before(self):
        m = ch.resolve(ROOT, None)
        self.assertEqual(m['id'], 'channel-mascot')
        self.assertEqual(m['reference_path'], ROOT / 'assets/characters/channel-mascot/reference-v1.png')
        self.assertEqual(m['media_id'], 'de94a39b-155f-4afe-acbb-d9d4b59ad532')

    def test_real_repo_tiensu_mascot_has_no_reference_yet(self):
        # Documents current repo state: tiensu-mascot exists as a text-only
        # character definition (see assets/characters/tiensu-mascot/character.json),
        # so resolving it must fail loudly, not fall back to the vocab mascot.
        with self.assertRaises(Blocked) as cm:
            ch.resolve(ROOT, 'tiensu')
        self.assertIn('MASCOT_REFERENCE_MISSING', str(cm.exception))


class CliTests(unittest.TestCase):
    """pilot.py mascot-reference: end-to-end through the real CLI entry point."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        for n in ['schemas', '.agents', 'renderer', 'examples', 'scripts']:
            shutil.copytree(ROOT / n, self.root / n)
        for n in ['pilot.py', 'workflow.py', 'machine_review.py', 'image_pipeline.py', 'characters.py',
                  'content_contract.py', 'prompt_templates.py', 'adapters.py', 'config.json', 'AGENTS.md', 'GEMINI.md']:
            shutil.copy(ROOT / n, self.root / n)
        (self.root / 'assets/characters/tiensu-mascot').mkdir(parents=True)
        write(self.root / 'assets/characters/tiensu-mascot/character.json',
              {'id': 'tiensu-mascot', 'reference': None, 'sha256': None})
        self.src = self.root / 'approved.png'
        Image.new('RGB', (16, 16), (1, 2, 3)).save(self.src)

    def test_mascot_reference_cli_installs_the_file(self):
        out = subprocess.check_output(
            [str(ROOT / '.venv/bin/python'), str(self.root / 'pilot.py'), 'mascot-reference', 'tiensu',
             '--from', str(self.src)],
            cwd=self.root, text=True)
        result = json.loads(out)
        self.assertEqual(result['id'], 'tiensu-mascot')
        cj = read(self.root / 'assets/characters/tiensu-mascot/character.json')
        self.assertEqual(cj['reference'], 'reference-v1.png')
        self.assertTrue((self.root / 'assets/characters/tiensu-mascot/reference-v1.png').is_file())

    def test_mascot_reference_cli_requires_from(self):
        proc = subprocess.run(
            [str(ROOT / '.venv/bin/python'), str(self.root / 'pilot.py'), 'mascot-reference', 'tiensu'],
            cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('--from FILE', proc.stdout + proc.stderr)


if __name__ == '__main__':
    unittest.main()
