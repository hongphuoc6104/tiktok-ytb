# Colab audio and video processing

Engine 4 sends TTS/assembly/mastering/timeline/subtitles/props/render/encode to Colab. The machine packages source/metadata, manages sessions and collects results; Flow generates images. Remote errors do not trigger heavy local fallback. Voice/rate come from each brief and actual request, never unrelated defaults overriding a contract.

New English briefs use **reference-narrator at 0.92**, the exact user-selected 3.24-second clone sample; see its [profile](../assets/voices/reference-narrator/profile.json). Vietnamese Minh Quân Pro stays unchanged. Existing jobs retain their saved choices, including Alba. Default changes do not edit saved briefs/requests/WAV.

## Setup and lifecycle

Before any Colab operation from a bridge checkout's `sys/`, run `python3 -m colab_bridge.accounts list`. Authentication/profiles stay in their local store, never copied into repo/Colab/frontend. The user completes OAuth/OTP/CAPTCHA. Token presence does not prove live auth; auth does not prove T4/units/capacity.

After setup/pool selection, use explicit account/session: `python3 -m colab_bridge start --account ACCOUNT --session SESSION`, then `setup` with the same choice. Start allocates a real VM only for assigned processing. Allocation timeout uses `reconcile`, never another start. `status` reads the service with required authentication; units=0 is not logout. Do not buy compute or fall back to CPU/local.

Confirmed connected T4 records identity/session/timestamp in the ledger, counting idle and unconfirmed-release intervals. The 6h display/5h usable/1h reserve and 24h marker are internal budgets, not guaranteed Google quotas. Pools do not combine quota; rotation cannot evade restrictions.

## Requests and results

The official workflow packages text/voice/rate/reference hashes/languages/output selection with validated source bundles. TTS returns real WAV/tracks/duration; render returns MP4/stills/layout/editorial/remote report with request-linked hashes. English9:16 requires English tracks/cues/timeline; aspect ratio does not imply language.

Submitted work retains account/session/request pins. `collect` retrieves old work without generation; unknown/ambiguous waits for reconciliation. Quota/bot/CAPTCHA/auth/503 blocks only dependent scope; network recovery is finite per episode. Collect important files and verify hashes/manifests before `stop --account ACCOUNT --session SESSION` on the completed owned runtime. Closing a browser tab does not release GPU.

Passing fixtures/protocol checks do not prove actual T4, pronunciation, voice similarity or video quality. Report real measurements and only actual viewing/listening. [Progress/evidence](implementation/normalization-progress.md) tracks trials; the [earlier Colab guide](legacy/colab-tts-before-normalization.md) preserves historical design/testing.

Engine 4 uses measured WAV duration for downstream timeline/rendering; the brief range is an estimate, not a TTS stop condition. Keep narration, voice and rate when the measurement differs. Positive finite WAV/header/segment durations, manifest hashes and audio/video consistency remain mandatory; legacy v3 or an explicit source-backed required duration retains its contract.
