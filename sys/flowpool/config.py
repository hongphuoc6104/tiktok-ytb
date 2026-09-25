"""FlowPool configuration: sys/config.json keys merged over safe defaults."""
import json
from pathlib import Path

SYS = Path(__file__).resolve().parents[1]
HOME = Path(__file__).resolve().parent

DEFAULTS = {
    'flowpool_enabled': False,
    # Profiles driven at the same time (all share the user's one Chrome and the
    # daemon's single CDP connection; each profile has its own tab).
    'flowpool_max_parallel': 2,
    # Requests queued in one B-2 tool at once (x4 accepted on 22/09/2026).
    'flowpool_per_browser_queue': 4,
    # Credits each Google AI Pro account may spend per month (override per profile
    # with `monthly_credits` in profiles.json).
    'flowpool_profile_monthly_credits': 1050,
    'flowpool_image_variants': 2,
    'flowpool_flow_url': 'https://flow.google.com/',
    'flowpool_ui_port': 8765,
    'flowpool_daemon_socket': None,  # default sys/flowpool/daemon.sock
    'flowpool_state_dir': str(HOME),
    # The user's declared, already signed-in profiles (the only ones FlowPool uses).
    'flowpool_browser_profiles': str(SYS / 'experiments/b2_illustrator/browser-profiles.json'),
    'flowpool_image_timeout_seconds': 300,
    'flowpool_clip_timeout_seconds': 1800,
    'flowpool_cooldown_seconds': 900,
    'flowpool_max_profile_attempts': 2,
    'flowpool_clip_seconds': 8,
    # Credit cost per generated clip, used only until the ledger has measured
    # before/after deltas for that model. Values are estimates, never billing proof.
    'flowpool_clip_credit_estimate': {'veo-fast': 20, 'veo-quality': 100},
    'flowpool_model_labels': {'veo-fast': 'Veo 3.1 - Fast', 'veo-quality': 'Veo 3.1 - Quality'},
    # Where the balance is shown. Tried in order; 'open' selectors are clicked
    # (menus only, never a generation control) and closed with Escape.
    'flowpool_credit_probe': {'selectors': ['[aria-label*="credit" i]', '[data-testid*="credit" i]'],
                              'open': []},
    'flowpool_node': 'node',
    'flowpool_chrome': '/opt/google/chrome/google-chrome',
    'flow_model': 'Nano Banana 2',
    'flow_project': 'Video Pilot',
    'veo_model': 'veo-fast',
    'video_generation': False,
    'credit_budget': 0,
}


def load(overrides=None, root=SYS):
    """Merge DEFAULTS < sys/config.json < overrides (dict)."""
    cfg = dict(DEFAULTS)
    path = Path(root) / 'config.json'
    if path.exists():
        cfg.update(json.loads(path.read_text(encoding='utf-8')))
    if overrides:
        cfg.update(overrides)
    return cfg


def state_dir(cfg):
    d = Path(cfg.get('flowpool_state_dir') or HOME)
    d.mkdir(parents=True, exist_ok=True)
    return d
