"""FlowPool configuration: sys/config.json keys merged over safe defaults."""
import json
from pathlib import Path

SYS = Path(__file__).resolve().parents[1]
HOME = Path(__file__).resolve().parent

DEFAULTS = {
    'flowpool_enabled': False,
    # Profiles driven at the same time. All profiles of one user-data-dir live in
    # one Chrome process (one window per profile), so this is "active profile
    # windows", sized for a 14-16 GB laptop.
    'flowpool_max_browsers': 2,
    # Requests queued in one B-2 tool at once (x4 accepted on 22/09/2026).
    'flowpool_per_browser_queue': 4,
    # true = never drive two profiles of the same user-data-dir concurrently
    # (fallback if live acceptance shows per-profile tab binding is unreliable).
    'flowpool_serialize_user_data_dir': False,
    'flowpool_state_dir': str(HOME),
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
