#!/usr/bin/env python3
"""Read-only project Chrome configuration diagnostic. Never reads auth stores."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def inspect():
    config = json.loads((ROOT / 'config.json').read_text())
    data = Path(config.get('flow_user_data_dir') or ROOT / '.gflow/profiles' / config.get('flow_profile', 'video-pilot')).resolve()
    profile = config.get('flow_profile_directory', 'Default')
    running = []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            args = (proc / 'cmdline').read_bytes().decode().split('\0')
            if args[0] != '/opt/google/chrome/chrome' or any('--type=' in a for a in args):
                continue
            user_dir = next((a.split('=', 1)[1] for a in args if a.startswith('--user-data-dir=')), None)
            running.append({'pid': int(proc.name), 'executable': args[0],
                            'explicit_user_data_dir': user_dir,
                            'uses_default_user_data_dir': user_dir is None,
                            'debug_flag_present': any(a.startswith('--remote-debugging-') for a in args)})
        except (OSError, UnicodeError, IndexError):
            continue
    return {'observation': 'local configuration and process metadata; not live authentication evidence',
            'configured_data_dir': str(data), 'configured_profile_directory': profile,
            'configured_debug_port_file_exists': (data / 'DevToolsActivePort').is_file(),
            'running_chrome': running, 'authentication_verified': False,
            'generation_submitted': False}


if __name__ == '__main__':
    print(json.dumps(inspect(), indent=2))
