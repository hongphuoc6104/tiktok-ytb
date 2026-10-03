# Setup after download/clone

The machine holds UI, grants, accounts, plans, metadata and collected products. Colab processes TTS/audio assembly/timeline/subtitles/rendering; Flow generates images. Local setup does not require models or heavy render dependencies.

1. Read INDEX/AGENTS, identify checkout/branch and the setup task. Never copy another machine's `.state`, tokens, profiles, models or jobs.
2. From `sys/`, inspect `python3 scripts/bootstrap.py plan`, then `check`. These inspect environment/metadata without login, GPU allocation or production.
3. When management installation is authorized, run `python3 scripts/bootstrap.py apply --install`. It creates `.venv-management`, installs pinned jsonschema/Pillow and browser-control-only Playwright 1.58.2 under `~/.local/share/video-pilot/control/playwright-1.58.2`. No `sys/node_modules` or old-machine dependencies are needed. Installation skips lifecycle scripts/browser downloads and does not install Remotion/models/TTS/local renderer. Resume failed installation with `resume --install`.
4. Open `.venv-management/bin/python -m dashboard.server --port 8765`, or an existing compatible management interpreter. This loopback dashboard is not a public service.
5. Inventory browser profiles and Colab accounts in the account tab; the user completes OAuth/login. Before Colab operations run `python3 -m colab_bridge.accounts list`, never printing tokens. Token/profile presence means configured; live auth, Flow capability and T4 are separate checks.
6. Select pool/defaults or explicit accounts and preset `remote-t4`. A pool does not combine quotas. Existing requests retain account ownership when defaults change.
7. Flow requires an actual profile on this machine, the correct browser/profile and a per-machine tool/project URL. URL/profile/model must match the saved session configuration; do not reuse another machine's private URL/home path/IDs. `bootstrap.py check` separately reports Node, Playwright dependency, listener/socket and auth; dependency readiness does not prove login. Setup verifies connection only; image generation requires the assigned production/service-test scope.
8. Verify mascot/voice reference sources and hashes. Report missing assets instead of replacing standards. Allocate T4 only for authorized processing, never an auth probe. Collect important results before releasing an owned runtime.

Handoff distinguishes present/configured/verified/missing/not_tested/unsupported for each capability, pool/session, valid authority and next action. Bootstrap/fixtures do not prove live Flow/T4/WAV/MP4; see [progress](implementation/normalization-progress.md).

Node/npm must already be installed. Use Node LTS from the [official source](https://nodejs.org/en/download); the controller needs Node 18.18 or newer. Bootstrap searches PATH. For another installed location, pass `--node PATH --npm PATH` to check/apply/control-start. It does not download binaries or replace shared runtimes.

After profile/URL configuration through setup, use stored setup/development authority to open the listener from `sys/`:

```bash
.venv-management/bin/python scripts/bootstrap.py control-status
.venv-management/bin/python scripts/bootstrap.py control-start --grant GRANT_ID --source TEXT
```

Start opens only the B-2 listener with a short checkout-specific socket; it does not open a browser, connect Flow, perform OAuth, allocate GPU or generate media. A live existing listener is reused; uncertain socket ownership is retained for reconciliation. The operator opens/connects the browser afterward through profile setup. Do not install the sys package merely to start the listener: that package also contains renderer dependencies for remote workers.

The ESM resolver redirects only Playwright imports to the pinned control dependency. [Node loader documentation](https://nodejs.org/api/module.html#customization-hooks) and [Playwright browser-download guidance](https://playwright.dev/docs/browsers#skip-browser-downloads) are implementation references.

## Recover a departed Flow listener

An existing browser can remain healthy after its separate listener process exits. A stale Unix socket is not proof that its owner is dead: a bound socket that is not listening can also reject connections while a live process still owns it. Read both transport and ownership before recovery:

```bash
.venv-management/bin/python scripts/bootstrap.py control-status
.venv-management/bin/python scripts/bootstrap.py control-ownership
```

`control-status` distinguishes `connection_refused` from timeout/invalid/unresponsive. `control-ownership` reads the kernel socket table, socket inode descriptors, exact same-checkout daemon command identity and an existing `.state/flow-control.json` owner record. An inaccessible process audit, live/reused PID, foreign owner record, live kernel socket or another exact-checkout daemon prevents cleanup. A missing owner journal is recorded as missing; it is never described as a known dead PID.

For an authorized setup/development task, the explicit recovery command can remove only the checkout's exact private, same-UID socket, after terminal connection refusal and two matching ownership/inode checks:

```bash
.venv-management/bin/python scripts/bootstrap.py control-recover-stale --grant GRANT_ID --source "Actual recovery instruction"
.venv-management/bin/python scripts/bootstrap.py control-start --grant GRANT_ID --source "Actual listener startup instruction"
```

The recovery operation saves evidence and a separate outcome under `.state/flow-control-recoveries/`; it does not terminate processes, remove browser lock/profile files, open a browser, connect Flow, login, allocate GPU, generate images or alter job/request history. Timeout and unknown/shared ownership keep the socket untouched. `control-start` itself does not silently unlink stale sockets. Startup records kernel process start ticks to distinguish later PID reuse. Resume pending provider work only through its original job/request/account workflow after the listener and browser identity have been checked separately.

## Current existing-profile selection

`flow_profile_policy=existing_only` is the selected setup policy. Use the project Chrome tools and an existing profile. Computer Use is excluded by the current user instruction. Existing B-2/CDP profiles can be reused; an ordinary default-root profile without that transport is not automatically controllable. A missing CDP connection is not a sign-out. Setup must not create a replacement browser root, copy cookies, bypass default-root CDP protection or fabricate Flow login. If extension control is unavailable, preserve the original profile and report the connection handoff; other independent work can continue.
