---
name: vp-colab-runner
description: Automated provisioning, bidirectional telemetry, and execution controller for offloading heavy Video Pilot tasks (Remotion 1080p Video Rendering & Expressive TTS / Voice Cloning) to Google Colab GPU (Tesla T4).
---

# Video Pilot Colab Runner (Autonomous Cloud GPU Offload)

Sử dụng skill này khi cần giải phóng 100% tài nguyên CPU/RAM/VRAM của máy tính cá nhân bằng cách tự động đẩy các tác vụ nặng (Remotion Video Render 1080p và Expressive Neural TTS / Voice Cloning) lên GPU đám mây (Google Colab Tesla T4 16GB VRAM).

---

## 1. Nguyên Tắc Vận Hành Cốt Lõi (Mental Model)
- **Tự động 100% qua CLI chính thức (`colab`)**: Sử dụng công cụ `google-colab-cli` do Google phát hành. Agent có thể cấp phát máy ảo, truyền mã nguồn, thực thi và thu hồi mà không cần mở trình duyệt web.
- **Vòng đời máy ảo (Lifecycle)**:
  1. **Provision**: `colab new -s video-worker --gpu T4` (khởi tạo VM với GPU Tesla T4).
  2. **Deploy Daemon**: Nạp mã nguồn và khởi động worker daemon (`colab exec -s video-worker -f sys/colab_bridge/remote_boot.py`).
  3. **Execute**: Client cục bộ gửi gói nhị phân (props + assets) qua đường truyền bảo mật, nhận kết quả video `.mp4` hoặc `.wav` + `.srt`.
  4. **Teardown**: Bắt buộc giải phóng máy ảo (`colab stop -s video-worker`) ngay khi hoàn tất để bảo toàn hạn mức GPU miễn phí.
- **Dự phòng an toàn (Zero Disruption)**: Nếu Colab mất kết nối hoặc hết hạn mức, hệ thống tự động fallback về chạy local mà không làm hỏng job sản xuất.

---

## 2. Quy Trình Clone Giọng Biểu Cảm (Expressive Voice Cloning)

Hệ thống hỗ trợ clone giọng kể chuyện từ URL YouTube hoặc file WAV với mô hình **KhanhTTS-OmniVoice (8.400h)** trên Colab GPU:

```
[Audio mẫu 12-15s] -> [Chunkformer ASR] -> [Prompt Vector Extraction] -> [Batch Synthesis GPU T4] -> [Mastering -1dBFS / SRT]
```

### Tiêu chuẩn kỹ thuật đầu ra:
- **Tần số lấy mẫu:** `24,000 Hz, Mono, 16-bit PCM`.
- **Headroom chống clipping:** Đỉnh âm thanh (Peak) $\le -1.0\text{ dBFS}$ (áp dụng hệ số chuẩn hóa $0.89$).
- **Độ mượt nối câu:** Cosine Cross-fade $5\text{ ms}$, chêm khoảng lặng tự nhiên $200\text{ ms}$ giữa các câu.
- **Hồ sơ lưu trữ vĩnh viễn:** Lưu tại `sys/assets/voices/<voice_id>/` gồm:
  - `<voice_id>.wav`: Audio tham chiếu gốc.
  - `<voice_id>.txt`: Văn bản phiên âm chính xác từ ASR.
  - `voice_config.json`: Toàn bộ thông số cấu hình và style tags.

---

## 3. Bảng Tra Cứu Lệnh Điều Khiển & Giám Sát (Agent Cheatsheet)

### 🔍 Kiểm tra trạng thái & Phiên làm việc
```bash
# Kiểm tra các máy ảo Colab đang hoạt động
colab sessions

# Kiểm tra thông số phần cứng GPU và trạng thái của máy ảo
colab status -s video-worker

# Xem lịch sử logs của phiên làm việc
colab log -s video-worker -n 20
```

### 🚀 Khởi tạo & Cấp phát GPU
```bash
# Khởi tạo máy ảo với GPU T4 (mặc định cho Video Pilot)
colab new -s video-worker --gpu T4

# Khởi động worker daemon trên Colab
colab exec -s video-worker -f sys/colab_bridge/remote_boot.py
```

### 🎙️ Clone Giọng Nói & Quản Lý Hồ Sơ Giọng
```bash
# Clone giọng từ YouTube URL:
python3 tools/voice_cloner.py --voice-id van_vo --url "https://www.youtube.com/watch?v=ZQzFXMn9bKU" --start 180 --duration 15

# Clone giọng từ file WAV cục bộ:
python3 tools/voice_cloner.py --voice-id vui_ve --wav scratch/vui_ve_sample.wav

# Kiểm tra chất lượng âm thanh đầu ra:
python3 -c "import wave, struct, math; wf=wave.open('scratch/output.wav'); s=struct.unpack(f'<{wf.getnframes()}h', wf.readframes(wf.getnframes())); print('Peak dBFS:', 20*math.log10(max(abs(x) for x in s)/32768))"
```

### ⚡ Chạy Tác Vụ Thử Nghiệm & Đo Lường
```bash
cd sys

# Kiểm tra độ trễ và khả năng kết nối tới worker
.venv/bin/python scripts/colab_benchmark.py status

# Render video Remotion 1080p mẫu qua GPU Colab:
.venv/bin/python scripts/colab_benchmark.py render --seconds 30 --scenes 2 --out scratch/colab_outputs/render

# Tổng hợp giọng đọc diễn xuất có nhịp thở qua GPU Colab:
.venv/bin/python scripts/colab_benchmark.py tts --text "Năm mươi nghìn năm trước, tổ tiên chúng ta bắt đầu học cách giữ lửa." --out scratch/colab_outputs/tts
```

### 🛑 Giải phóng máy ảo (BẮT BUỘC KHI XONG VIỆC)
```bash
colab stop -s video-worker
```

---

## 4. Sổ Tay Xử Lý Sự Cố Kỹ Thuật (Troubleshooting & Root Causes)

Dưới đây là 6 sự cố kỹ thuật đặc thù đã được phân tích nguyên nhân và xử lý dứt điểm:

1. **Lỗi `pedalboard` treo vô tận (Deadlock trên Headless Linux):**
   - *Nguyên nhân:* Spotify JUCE audio scanning bị kẹt khi tìm card âm thanh vật lý trên máy ảo Linux.
   - *Giải pháp:* Không import `pedalboard` ở module level, gán `PB = None; PitchShift = None`.
2. **Lỗi `torch.compile` làm GPU T4 đơ cứng:**
   - *Nguyên nhân:* `reduce-overhead` CUDA Graphs bị treo với chuỗi âm thanh độ dài biến thiên liên tục.
   - *Giải pháp:* Ép mô hình chạy **Eager Mode FP32** chuẩn (`torch.compile = False`). Thời gian nạp giảm xuống còn $2.34\text{s}$.
3. **Tiếng rè / nổ lách tách kỹ thuật số tại giây thứ 3:**
   - *Nguyên nhân:* Hàm `fix_silent_and_speed_audio` cắt xén $84\text{ms}$ biên độ sóng không có cross-fade gây đứt gãy pha (bước nhảy $39,000$ đơn vị).
   - *Giải pháp:* Trả về Pure Neural Audio nguyên bản; dùng Cosine Cross-fade $5\text{ms}$ khi ghép câu.
4. **Vỡ tiếng do Clipping khi nhân 32767:**
   - *Nguyên nhân:* Mạng nơ-ron sinh biên độ $> 1.0$ dẫn đến tràn số kiểu int16.
   - *Giải pháp:* Luôn chuẩn hóa với hệ số $0.89$ để giữ Peak ở mức an toàn $-1.01\text{ dBFS}$.
5. **ASR Chunkformer thiếu dependency:**
   - *Nguyên nhân:* Thiếu `colorama` khi khởi tạo module Chunkformer.
   - *Giải pháp:* Chạy `pip install colorama` trong quy trình thiết lập môi trường Colab.
6. **Tối ưu RTF (Thời gian sinh âm thanh):**
   - *Nguyên nhân:* Việc trích xuất prompt và nạp lại weights nhiều lần gây lãng phí thời gian.
   - *Giải pháp:* Lưu prompt vectors vào file JSON cache (`voice_clone_prompt_cache.json`) để nạp tức thì trong $0.1\text{s}$.
