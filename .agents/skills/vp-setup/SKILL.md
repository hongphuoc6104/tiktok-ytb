---
name: vp-setup
description: First-time machine onboarding and environment bootstrap; install dependencies, configure accounts and run login scripts.
---

# Setup and machine onboarding

Use setup authority from AGENTS and permissions.md for initial machine onboarding and environment bootstrap. Read sys/docs/getting-started.md for a new machine.

Setup responsibilities:
1. Environment bootstrap: install `uv`, configure `.venv`, install required project packages and verify operational tools.
2. Initial account & credential onboarding: run interactive Colab CLI login scripts (`python3 -m colab_bridge.accounts login-many`), guide and configure Chrome browser profiles for Google Flow, and save account profiles to configured stores.
3. System inventory & verification: report missing/configured/verified accounts and runtime tools; user completes OAuth/OTP/CAPTCHA during onboarding.

Keep auth, profiles and credentials safely in their configured stores (`~/.config/video-pilot/`). Setup does not produce videos. Once dependencies and account stores are configured, routine execution and on-demand runtime management belong to production.

