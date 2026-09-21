# Experimental tool contract — implementation target

This document defines acceptance requirements, not a claim of live support.
Production stays unchanged. The experimental credit authorization is 1,050 total;
prior image cost is unknown, so remaining balance must not be invented.

## Primary Objective: Progressive Layering & Visual Beats Engine

Mục tiêu cốt lõi của công cụ này là phục vụ kỹ thuật:
**"Diễn hoạt phân lớp theo nhịp thoại" (Progressive Layering / Visual Beats) trong video dạng Explainer / Kể chuyện**.

1. **Kiến trúc phân lớp gia số (Incremental Layering):**
   - Trong cùng một cảnh (Single Scene), nhân vật và hậu cảnh (Base Scene & Character) được bảo lưu cố định (Stasis & Identity Continuity).
   - Các yếu tố biểu đạt gia tăng (bóng thoại suy nghĩ, bong bóng lời nói, biểu tượng cảm xúc, dấu gạch chéo đỏ, chữ cái/từ khóa nổi bật) được kích hoạt tuần tự theo từng mốc thời gian của âm thanh (Audio Beats Alignment).
2. **Cơ chế kép (Dual Pipeline Support):**
   - **Tầng 1 (AI Reference Generation):** Sinh ảnh gốc (Base Image) chất lượng cao, đúng tư thế và biểu cảm của nhân vật trên nền màu/texture chuẩn thông qua Google Flow (VP Stickman Lab).
   - **Tầng 2 (Video Compositing Overlay):** Điều phối các lớp phủ đồ họa (vector/bubble/text overlay) xuất hiện chính xác từng mili-giây khớp với giọng đọc voiceover, đảm bảo 100% không bị lệch vị trí, không giật hình (pixel-perfect continuity) và tối ưu hóa tối đa chi phí credit.

## Ownership

The local controller owns durable attempts, budget accounting, queue ordering,
reference ancestry, downloads and evidence. Flow performs one image generation.
Browser localStorage is a recovery hint only: tool rebuilds and iframe origins
must not become the authoritative job ledger. No automatic batch inside the tool.

## Input

One request includes tool revision/source hash, model actually selected, topic,
style, aspect ratio, preserve/change instructions, literal allowed text and its
font/color/placement. No default narrative topic. Internal IDs never enter visible
text. Capture the final expanded prompt, rather than hashing only form inputs.

References contain role (base/character), source file SHA256, Flow mediaId and
actual attachment evidence. A dependent image needs an accepted parent of the same
ratio. Selection of a thumbnail or a local path alone does not prove conditioning.
Character and base must remain separately identified even if the SDK uses an array.

## Submission and recovery

Write and sync intent before clicking Generate. Hold a per-attempt exclusive lock
across the external operation. Interrupted/ambiguous submissions are unknown and
must be reconciled; never automatically click again. Unknown credit cost is null,
not zero. Authentication/CAPTCHA/quota errors halt the queue.

Persist the returned mediaId immediately, before dimension decoding, download or
quality evaluation. These later failures must retain it. A known mediaId permits
retrying collection, never generation. Reconciliation requires evidence mapping
the result to the original request and profile; matching timestamps alone is not
sufficient.

## Output

Result: request identity, mediaId, actual model if available, declared MIME, actual
bytes, expanded prompt, reference mapping, source revision and cost evidence.
Decode bytes independently. No fallback PNG extension or fabricated resolution.
Technical validation and visual acceptance are separate: verify text, no stray
IDs, character consistency, continuity, composition and ratio on actual images.

## Before live generation

- Verified exact Chrome executable and Profile 10; retain that same tab.
- Full input fields and values observable in the tool, including editable Style.
- Source snapshot/version saved before edits, narrow changes reviewed afterward.
- Immediate result identity observable even if browser storage or decoding fails.
- Real reference selection, model and credit behavior checked in UI.
- Local crash/recovery and duplicate-submission tests pass.

Current live submit remains disabled. The new ledger and asset validator require
adapter wiring and live acceptance before they can protect production work.
