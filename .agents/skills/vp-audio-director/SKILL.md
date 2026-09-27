---
name: vp-audio-director
description: Chỉ đạo giọng kể, phát âm mẫu, khoảng chờ luyện nói, kiểm soát chất lượng giọng clone và vai trò âm thanh cho Video Pilot; dùng khi lập hoặc kiểm tra audio, không tự đổi TTS hay dùng API trả phí.
---

# Audio direction for Video Pilot

Read [the direction contract](../vp-content/references/director-contract.md) and [audio operations](../vp-media/references/audio.md). Audio is produced before images; changes follow vp-media.

## Direct a communicative act

For a spoken scene specify who is being addressed, what the speaker wants to do (tease, warn, reassure, explain, invite), the important words, the pause needed and any pronunciation risk. Avoid vague “energetic/natural” direction without a behavior to listen for.

In content-v3 use `audio_direction.vi` and, when applicable, `.en`, each with `intent`, `pronunciation_notes`, `learner_pause_seconds`. The first two are reviewer/retake instructions, not supported TTS controls; do not claim the engine honored them without listening. A zero pause means no additional learner hold. A positive value requests at least that much quiet at the end of the scene and is included in the total duration. Put the model utterance/question at the scene end if the learner should answer there. For an internal practice turn, plan a scene boundary before anchoring narration; do not insert untracked silence into approved media.

## Expressive Voice Clones & Storytelling Archetypes

Video Pilot supports high-expressivity voice clones stored under `sys/assets/voices/<voice_id>/` (via OmniVoice on Colab GPU):
- **Vui Vẻ (`vui_ve`)**: Deadpan humor, hypothetical speculation, fast-paced and captivating narration. Phù hợp với các video giải thích khoa học, đặt câu hỏi giả định hoặc tình huống bất ngờ.
- **Văn Vở (`van_vo`)**: Deep voice, calm, reflective, narrative recap. Phù hợp với các video lịch sử, tiền sử, phân tích tâm lý hoặc tóm tắt tác phẩm.
- **Minh Quân Pro (`vieneu`)**: Giọng đọc trung tính, chuẩn mực, nhanh và ổn định cục bộ.

Khi chỉ đạo giọng clone:
1. Đảm bảo nhịp ngắt câu tự nhiên (khoảng lặng 200ms - 350ms giữa các mệnh đề).
2. Kiểm tra độ liền mạch của pha âm thanh: Tuyệt đối không chấp nhận các bước nhảy biên độ sóng đột ngột (phase discontinuity) gây tiếng nổ (pop/crackle) ở đầu/cuối câu. Nối câu phải có 5ms Cosine Cross-fade.
3. Không để âm thanh bị vỡ tiếng (digital clipping): Kiểm tra Peak luôn nằm dưới ngưỡng an toàn $-1.0\text{ dBFS}$.

## Spoken English

Keep correct English in narration, visible_text, subtitles and anchors. Engine-specific pronunciation spelling belongs only in the synthesis adapter. Do not replace I with Ai in the script or narration_en. Do not force lowercase acronyms or apply Vietnamese pronunciation rules to the English worker.

Select pronunciation guidance appropriate to the word, accent and learner. Do not force etymology/linking/IPA into every clip. Verify claims against a pronunciation source when needed. Use “listen and repeat” when the learner repeats after a pause; use shadowing only when the task actually asks them to track speech. Still pictures cannot demonstrate moving lips.

Listen to the entire WAV: target sounds and stress, English sentences inside Vietnamese, consonant endings, I, changing language, edits, intelligibility and useful waiting time. Reject the smallest faulty scene/part. A transcript, ASR result, waveform or LUFS value cannot certify pronunciation or acting.

## Sound hierarchy

Narration and the model sentence lead. Silence is a legitimate choice. Propose a sound only if it clarifies cause, action, setting or a learning turn; avoid whooshes on every cut and music under difficult phonemes. Use existing supported tools/assets only. Background music/SFX mixing is not currently a content-v3 runtime feature; a sound plan is a proposal until implementation is explicitly supported and verified.

Measure levels for technical defects; do not label speech robotic from low loudness range or call a universal LUFS value a platform rule. Audition on headphones and a small speaker when available. If listening is unavailable, return unsupported for auditory judgments and keep that gate open.

Report observations in Vietnamese, with the heard/intended phrase, timestamp and proposed retake. Sources: [source notes](../vp-content/references/director-sources.md).
