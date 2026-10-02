---
name: vp-script-director
description: Thiết kế và phản biện câu chuyện, lời thoại và hoạt động học cho kịch bản Video Pilot; dùng cùng vp-content, không vận hành job hoặc tạo media.
---

# Script direction for Video Pilot

Use the current brief as the contract. Read [the direction contract](../vp-content/references/director-contract.md). For vocabulary, also read [vocabulary pedagogy](../vp-content/references/vocab-pedagogy.md). Direct the script inside content; do not introduce another approval stage.

## Decisions before prose

- Name the learner's observable action after watching. “Enjoy the video” is not evidence of learning.
- Choose the smallest story that demonstrates the intended meaning: someone wants something, encounters resistance, acts, and gets a consequence. A change of place or the labels setup/climax/resolution do not establish causality.
- **Micro-Drama 4-Act Framework (TikTok/Shorts Gen-Z Viral Formula)**:
  1. **Act 1 (0-4s, Relatable Hook & Breaking 4th Wall)**: Bắt quả tang tình huống đời thực của người xem (lướt Tóp Tóp đêm, đặt 10 cái báo thức, ngắm gương tự luyến). **Quy tắc Phi Giới Tính (Gender-Neutral)**: Tuyệt đối không dùng từ ngữ chỉ nhắm vào 1 giới ("soái ca", "đẹp trai", "gái chê"). Sử dụng từ ngữ toàn dân cho cả nam lẫn nữ ("visual vạn người mê", "tự luyến nhan sắc", "người ta né", "ế dài hạn").
  2. **Act 2 (4-8s, Vocab Solution Key & Explicit Echo Prompt)**: Giới thiệu từ khóa tiếng Anh kèm **khẩu lệnh bắt buộc người xem mở mồm đọc theo ngay** ("Mở mồm nhại theo tao liền coi:", "Đọc to theo tao từ này:"). Không được giới thiệu suông rồi sang Act 3 vô cớ mắng người xem.
  3. **Act 3 (8-13s, Interactive 2-Way Speaking Practice)**: Phản ứng khi người xem im lặng ("Ủa tao kêu mày đọc mà đứng im ru vậy?!"), giục hô to lại cụm từ, kèm khoảng dừng luyện nói (`learner_pause_seconds` 0.9 - 1.2s) và bóng thoại trực quan.
  4. **Act 4 (13-18s, Comic Meme Twist & Unique Contextual CTA)**: Cú twist trớ trêu nhớ đời. **Quy tắc Chống Đúc Khuôn Câu Kết (Anti-Template Fatigue)**: Tuyệt đối không dùng một câu kết khuôn sáo lặp lại cho mọi video ("Chưa thuộc từ thì bấm coi lại..."). Biến tấu câu chốt giữ chân (Replay Loop) và kéo vào kênh gắn chặt với ngữ cảnh riêng của từng từ (báo thức -> coi lại cho tỉnh ngủ; gương -> coi lại soi mụn; tắm -> coi lại kẻo tối ám mộng).
- **Quy tắc Ngôn Ngữ & Phát Âm TTS**:
  - Tiếng Việt (Adam bựa): Dùng 100% tiếng Việt chuẩn văn nói (`vậy`, `sao`, `thế`, `mày`, `Tóp Tóp`). Tuyệt đối cấm teencode (`zậy`, `z`, `mài`, `đc`) vì mô hình Vieneu sẽ đánh vần thành *"zét ậy"*. Không nhét bất kỳ từ tiếng Anh nào vào prompt của Adam.
  - Tiếng Anh: 100% từ khóa và cụm từ tiếng Anh phải do mô hình Native English (Edge-TTS Christopher) phát âm chuẩn quốc tế, nối nhịp thở zero-gap 0.04s và bù âm lượng (+3.5dB).

- Decide what must remain explicit for this learner. A1 examples may need simple literal explanation; do not hide the lesson behind sophisticated jokes or subtext.
- Use the existing `outline[].purpose/transition`, `scenes[].purpose/action`, `beats[].purpose` to carry these decisions. Each transition should explain what changes or why the next scene follows.

## Write and edit

Write narration first, including full English sentences in correct spelling, then freeze it before attaching quotes/coverage/anchors. Read [narration style](../vp-content/references/narration-style.md).

For each line ask: who needs to say this now, what changes because of it, and what new information does it give? Keep required facts/examples; shorten repetition and filler, not the brief. If the brief is too dense, flag the conflict and use the established revision route.

Make examples actions inside the story. If three are explicitly required, retain all three while connecting them through goal, cause, consequence or a meaningful contrast. Do not relabel three unrelated examples as a narrative arc.

Provide one manageable retrieval opportunity: choose, complete, predict or produce a short sentence. The learner must have a way to check the answer. Match CTA effort to proficiency; a partially supplied sentence can lead to an original comment. Do not make engagement counts stand in for learning.

For end-of-scene practice, set `audio_direction.vi/en.learner_pause_seconds` to the time the learner needs for that utterance, then verify the resulting WAV. It is a deliberate hold, not narration text or a new scene. Omit it outside content-v3. Do not promise a mouth demonstration when the available medium is still images.

## Review evidence

Report in Vietnamese with scene IDs and quoted lines: the actual problem, why it affects this learner, and the smallest repair. If an opening raises a question, locate its payoff. If claiming a causal story, identify the causal links. Distinguish factual errors from taste and alternatives.

Do not approve content, change the selected vocabulary entry, translate narration_en into Vietnamese, or omit required coverage. A technically valid JSON does not prove a good lesson.

Sources and adaptation rationale: [source notes](../vp-content/references/director-sources.md).
