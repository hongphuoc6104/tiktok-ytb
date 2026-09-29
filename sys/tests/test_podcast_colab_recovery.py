import json
import hashlib
import io
from pathlib import Path
import tempfile
import time
import unittest
import urllib.error
import wave
from unittest.mock import patch

from colab_bridge.config import ColabConfig
from podcast.coordinator import Coordinator, EpisodeError
from podcast.colab_deploy import (
    ColabProvisioningError,
    deploy_podcast_worker,
    keepalive_podcast_worker,
    restore_local_tts_checkpoints,
)
from podcast.tts import PodcastColabTTS, PodcastTTSAmbiguous, _RemoteHTTPError


class PodcastColabRecoveryTests(unittest.TestCase):
    def _episode(self, root: Path) -> PodcastColabTTS:
        state_dir = root / ".state"
        state_dir.mkdir(parents=True)
        state_path = state_dir / "podcast-colab.json"
        state_path.write_text(json.dumps({"session": "podcast-worker", "profile_alias": "alternate"}))
        state_path.chmod(0o600)

        run_dir = root / "runs" / "episode-001" / "tts"
        run_dir.mkdir(parents=True)
        manifest = {
            "schema_version": 1,
            "episode_id": "episode-001",
            "parts": {"P01": "request-1"},
            "requests": {"request-1": {
                "request_id": "request-1", "part_id": "P01", "state": "running",
                "runtime_id": "runtime-old", "chunk_ids": ["P01-C001"], "remote_attempts": 1,
            }},
            "chunks": {},
        }
        (run_dir / "manifest.json").write_text(json.dumps(manifest))
        return PodcastColabTTS("episode-001", root / "runs" / "episode-001", sys_root=root)

    def _episode_with_checkpoint(self, root: Path) -> PodcastColabTTS:
        tts = self._episode(root)
        tts_dir = root / "runs" / "episode-001" / "tts"
        text = "Một câu dịu dàng để mẫu kiểm tra có giọng đọc tự nhiên."
        wav_path = tts_dir / "checkpoints" / "request-1" / "chunks" / "P01-C001.wav"
        wav_path.parent.mkdir(parents=True)
        with wave.open(str(wav_path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(24000)
            wav.writeframes(bytes(2400 * 2))
        wav_hash = hashlib.sha256(wav_path.read_bytes()).hexdigest()
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        chunk_hash = "a" * 64
        meta = {"scene_id": "P01-C001", "text": text, "text_sha256": text_hash,
                "chunk_hash": chunk_hash, "profile_fingerprint": "profile-fp",
                "voice_id": "voice", "model": "model", "sample_rate": 24000,
                "channels": 1, "duration_seconds": 0.1, "wav_sha256": wav_hash}
        metadata_dir = tts_dir / "checkpoints" / "request-1" / "chunk_meta"
        metadata_dir.mkdir(parents=True)
        (metadata_dir / "P01-C001.json").write_text(json.dumps(meta))
        (tts_dir / "requests").mkdir()
        (tts_dir / "requests" / "request-1.json").write_text(json.dumps({
            "settings": {"tts_engine": "omnivoice", "tts_voice": "voice", "tts_speed": 0.9,
                         "pitch_shift": 1.0},
            "scenes": [{"id": "P01-C001", "narration": text, "chunk_hash": chunk_hash}],
        }))
        (tts_dir / "profiles").mkdir()
        (tts_dir / "profiles" / "profile-fp.json").write_text(json.dumps({"profile_fingerprint": "profile-fp"}))
        manifest = tts._read_manifest()
        manifest["planned_parts"] = ["P01", "P02"]
        manifest["planned_chunks"] = {"P01-C001": {"chunk_id": "P01-C001", "part_id": "P01",
                                                      "chunk_hash": chunk_hash, "state": "pending"}}
        manifest["requests"]["request-1"].update({
            "profile_fingerprint": "profile-fp", "spec_path": "requests/request-1.json",
            "profile_bundle_path": "profiles/profile-fp.json",
        })
        (tts_dir / "manifest.json").write_text(json.dumps(manifest))
        return tts

    def test_lost_session_can_be_retired_for_a_bounded_part_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            tts = self._episode(Path(temp))
            with patch("podcast.colab_deploy._session_exists", return_value=False):
                result = tts.mark_part_failed_if_session_missing("P01")
            record = tts._read_manifest()["requests"]["request-1"]
            self.assertEqual(result["status"], "failed_runtime_lost")
            self.assertEqual(record["state"], "failed")
            self.assertEqual(record["runtime_loss_verified"]["session"], "podcast-worker")

    def test_active_session_is_never_retired_or_resent(self):
        with tempfile.TemporaryDirectory() as temp:
            tts = self._episode(Path(temp))
            with patch("podcast.colab_deploy._session_exists", return_value=True):
                with self.assertRaises(PodcastTTSAmbiguous):
                    tts.mark_part_failed_if_session_missing("P01")
            self.assertEqual(tts._read_manifest()["requests"]["request-1"]["state"], "running")

    def test_replaced_runtime_requires_current_task_404_before_retiring(self):
        with tempfile.TemporaryDirectory() as temp:
            tts = self._episode(Path(temp))
            with patch("podcast.colab_deploy._session_exists", return_value=True), \
                 patch.object(tts, "_runtime", return_value="runtime-new"), \
                 patch.object(tts, "_get_task", side_effect=_RemoteHTTPError(404, "not found")):
                result = tts.mark_part_failed_if_runtime_changed("P01")
            record = tts._read_manifest()["requests"]["request-1"]
            self.assertEqual(result["status"], "failed_runtime_replaced")
            self.assertEqual(record["state"], "failed")
            self.assertEqual(record["runtime_loss_verified"]["from_runtime_id"], "runtime-old")
            self.assertEqual(record["runtime_loss_verified"]["to_runtime_id"], "runtime-new")

    def test_local_checkpoint_is_verified_and_adopted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            tts = self._episode_with_checkpoint(root)
            saved = tts.import_local_checkpoints("P01")
            self.assertEqual([item["chunk_id"] for item in saved], ["P01-C001"])
            self.assertTrue(tts._local_chunks_valid(tts._read_manifest()["requests"]["request-1"]))
            self.assertEqual(tts.progress()["completed_chunks"], 1)

    def test_checkpoint_restore_skips_untouched_parts_and_uploads_verified_entries(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._episode_with_checkpoint(root)
            with patch("podcast.colab_deploy._upload") as upload:
                result = restore_local_tts_checkpoints(root, "episode-001")
            self.assertEqual(result["restored_chunks"], 1)
            self.assertEqual(result["profile_alias"], "alternate")
            self.assertEqual(upload.call_count, 2)

    def test_checkpoint_restore_keeps_local_chunks_after_part_request_id_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            tts = self._episode_with_checkpoint(root)
            tts.import_local_checkpoints("P01")
            manifest = tts._read_manifest()
            manifest["requests"]["request-2"] = {
                "request_id": "request-2", "part_id": "P01", "state": "running",
                "runtime_id": "runtime-new", "chunk_ids": ["P01-C001"], "remote_attempts": 1,
                "profile_fingerprint": "profile-fp", "spec_path": "requests/request-1.json",
                "profile_bundle_path": "profiles/profile-fp.json",
            }
            manifest["parts"]["P01"] = "request-2"
            (root / "runs" / "episode-001" / "tts" / "manifest.json").write_text(
                json.dumps(manifest))
            with patch("podcast.colab_deploy._upload") as upload:
                result = restore_local_tts_checkpoints(root, "episode-001")
            self.assertEqual(result["restored_chunks"], 1)
            self.assertEqual(upload.call_count, 2)
            self.assertTrue(all("P01-C001" in call.args[2].name for call in upload.call_args_list))

    def test_unsubmitted_preflight_failure_refunds_only_its_retry_slot(self):
        with tempfile.TemporaryDirectory() as temp:
            coordinator = Coordinator(Path(temp))
            episode_id = "episode-001"
            coordinator.create_episode(
                topic="Khoảng yên dịu dàng",
                brief={"podcast_policy_version": 1},  # Existing legacy checkpoint fixture.
                episode_id=episode_id,
            )
            text = " ".join(["Một câu chuyện yên bình."] * 126)
            parts = [
                {"id": f"P{i:02}", "title": f"Phần {i}", "script": text,
                 "chunks": [text]}
                for i in range(1, 5)
            ]
            coordinator.set_script(episode_id, {"title": "Yên bình", "topic": "Yên bình",
                                                 "target_minutes": 25, "estimated_wpm": 100,
                                                 "parts": parts})
            coordinator.set_chunk_state(episode_id, "P01-C001", "running")
            coordinator.set_chunk_remote_request(episode_id, "P01-C001", "older-request")
            coordinator.set_chunk_state(episode_id, "P01-C001", "failed", "Older remote attempt failed")
            time.sleep(1.05)
            coordinator.set_chunk_state(episode_id, "P01-C001", "running", retry_failed=True)
            detail = "No saved TTS request for part P02"
            coordinator.set_chunk_state(episode_id, "P01-C001", "failed", detail)
            saved = coordinator.refund_unsubmitted_chunk_attempt(episode_id, "P01-C001", detail)
            chunk = saved["parts"][0]["chunks"][0]
            self.assertEqual(chunk["state"], "pending")
            self.assertEqual(chunk["attempts"], 1)
            self.assertEqual(chunk["attempt_history"][-1]["state"], "not_submitted")

    def test_unsubmitted_attempt_cannot_refund_a_chunk_with_remote_request(self):
        with tempfile.TemporaryDirectory() as temp:
            coordinator = Coordinator(Path(temp))
            episode_id = "episode-001"
            coordinator.create_episode(
                topic="Khoảng yên dịu dàng",
                brief={"podcast_policy_version": 1},  # Existing legacy checkpoint fixture.
                episode_id=episode_id,
            )
            text = " ".join(["Một câu chuyện yên bình."] * 126)
            parts = [
                {"id": f"P{i:02}", "title": f"Phần {i}", "script": text,
                 "chunks": [text]}
                for i in range(1, 5)
            ]
            coordinator.set_script(episode_id, {"title": "Yên bình", "topic": "Yên bình",
                                                 "target_minutes": 25, "estimated_wpm": 100,
                                                 "parts": parts})
            coordinator.set_chunk_state(episode_id, "P01-C001", "running")
            coordinator.set_chunk_remote_request(episode_id, "P01-C001", "request-1")
            detail = "Colab TTS failed"
            coordinator.set_chunk_state(episode_id, "P01-C001", "failed", detail)
            with self.assertRaises(EpisodeError):
                coordinator.refund_unsubmitted_chunk_attempt(episode_id, "P01-C001", detail)

    def test_free_trial_does_not_query_paid_balance(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch("podcast.colab_deploy._compute_units_balance") as balance, \
                 patch("podcast.colab_deploy._load_state", side_effect=ColabProvisioningError("missing config")), \
                 patch("podcast.colab_deploy._provision") as provision:
                with self.assertRaisesRegex(ColabProvisioningError, "missing config"):
                    deploy_podcast_worker(sys_root=Path(temp), profile_alias="alternate")
            balance.assert_not_called()
            provision.assert_not_called()

    def test_keepalive_uses_saved_colab_alias_and_does_not_change_gpu(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state_dir = root / ".state"
            state_dir.mkdir()
            state_path = state_dir / "podcast-colab.json"
            state_path.write_text(json.dumps({"session": "podcast-worker", "profile_alias": "alternate"}))
            state_path.chmod(0o600)
            (root / "podcast").mkdir()
            script = root / "podcast" / "colab_keepalive.py"
            script.write_text('print("PODCAST_COLAB_KEEPALIVE_OK")\n')
            with patch("podcast.colab_deploy._exec_remote") as exec_remote:
                exec_remote.return_value.returncode = 0
                result = keepalive_podcast_worker(root)
            self.assertEqual(result, {"session": "podcast-worker", "profile_alias": "alternate"})
            self.assertEqual(exec_remote.call_args.args[:2], ("alternate", "podcast-worker"))
            self.assertEqual(exec_remote.call_args.kwargs["timeout"], 30)
            self.assertEqual(exec_remote.call_args.args[2], script)

    def test_gateway_5xx_keeps_the_remote_request_ambiguous(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = ColabConfig(enabled=True, endpoint="https://worker.example",
                                 auth_token="x" * 48, tasks={"expressive_tts": True})
            tts = PodcastColabTTS("episode-001", root / "runs" / "episode-001",
                                  sys_root=root, config=config)
            failure = urllib.error.HTTPError("https://worker.example/job", 503,
                                             "Service Unavailable", {}, io.BytesIO(b"gateway offline"))
            with patch("podcast.tts.urllib.request.urlopen", side_effect=failure):
                with self.assertRaises(PodcastTTSAmbiguous):
                    tts._http("GET", "/api/v1/podcast/tts/jobs/request-1")


if __name__ == "__main__":
    unittest.main()
