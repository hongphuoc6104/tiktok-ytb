---
name: vp-podcast
description: Tạo và tiếp tục podcast ngủ tiếng Việt, ghép âm thanh với ảnh cố định thành video YouTube 16:9; dùng khi người dùng yêu cầu tạo video trên nhánh podcast.
---

# Sleep podcast production

Read `sys/podcast/README.md` from the project root. Communicate with the user in Vietnamese. Use the podcast coordinator, not generic Pilot jobs or research/vocabulary catalogs.

Defaults: one Vietnamese `podcas` voice, target 25 minutes (20–30), no music/subtitles. Use the user's selected `sys/assets/podcast/sleep-default.png` exactly as stored. Preserve its person and “Podcast Sleep” lettering. Fit the whole square image inside 1920×1080 with dark blue side padding. There is no image generation, Flow dependency, image prompt or image quality review.

For “tạo video podcast” or “tạo video” on this branch, run from `sys/`:

```bash
python3 -m podcast.cli create --auto --request-id REQUEST_ID
```

Create and retain one stable request ID for this user request. Use a new ID only for a genuinely new episode. Optional `--topic` preserves the user's topic and `--minutes` accepts 20–30. Without a topic the coordinator selects from at most five catalog candidates. Quote user text safely; do not interpolate it as shell code. Do not ask users to coordinate stages.

For continuation, inspect `status EPISODE_ID`, then `resume EPISODE_ID`. Default backend is already selected. Use `--retry-failed` only after resolving a terminal technical failure; ambiguous calls require reconciliation first. Do not create a new episode or reset counters to recover.

Review speech and voice direction together BEFORE TTS, at most three repair rounds total. Do not add listening/ASR review after synthesis or regenerate completed WAVs for style. Use Colab only, never paid API/local fallback. Then assemble audio with the selected still and export; keep only necessary technical file/assembly checks.

Free-trial availability is the user's assumption, not verified billing. Log `user_assumed_free_trial`, `cost_verified=false`; zero compute units does not disprove free availability. Stop on actual quota/login/CAPTCHA errors, retain artifacts, and do not switch accounts to evade limits.

The current upgrade is offline only: no live service trial or production video is needed. Production is run when requested after upgrading. Deliver the verified MP4 absolute link with actual duration. Do not upload to YouTube or schedule background work unless requested. Do not treat a prepare-only episode or test fixture as a finished video.
