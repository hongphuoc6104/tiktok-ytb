---
trigger: always_on
---

# Accounts and runtime

Before Colab operations in a checkout with the bridge, run `python3 -m colab_bridge.accounts list` from sys; never print tokens. Browser profiles, Google identity, Colab OAuth and sessions are separate objects.

Metadata inventory neither launches every browser nor proves login. Token presence means configured; live auth, Flow project/model/reference and T4 capability require separate checks. Units=0, quota, capacity or network errors do not imply logout. The user completes OAuth/OTP/CAPTCHA.

Selecting multiple accounts creates a session pool, not combined quota. Honor explicit account selection. Submitted requests retain owner/account/session even when defaults change; never transfer inflight/unknown work to another account.

T4 is the required preset; report its absence without CPU/local fallback or unit purchases. Time/image counters are internal budgets with timestamps, evidence and uncertainty, not guaranteed Google quotas. Allocated runtime includes idle time; closing a tab does not prove release. The 24h marker means recheck, not guaranteed recovery.

No rotation to bypass quota/bot/abuse restrictions. Login/quota/CAPTCHA/503/unknown blocks only its dependent scope; bounded temporary recovery must not duplicate generation. Tokens/cookies/OAuth codes never enter frontend, reports, Git or Colab bundles. Collect durable results before releasing an owned VM.

## Existing browser profiles

The current user selection is to reuse existing Chrome profiles only. Do not create fresh browser roots/profiles, copy cookies or treat missing CDP transport as logout. Open the selected existing profile through project Chrome tools. Computer Use is excluded by the current user instruction; do not route browser actions through it. A source profile without the project transport remains unsupported for automation, even if logged in. Login remains a human handoff when actually required. Existing managed profiles may be reused only when explicitly selected; they do not replace the source profile silently.
