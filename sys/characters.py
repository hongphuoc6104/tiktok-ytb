"""Canonical mascot resolution by channel.

One brief field decides which physical character design a job's CH01 slot
uses: brief `channel` == 'tiensu' -> assets/characters/tiensu-mascot/; no
`channel` (or any other value) -> assets/characters/channel-mascot/ (the
pre-existing vocab default). See AGENTS.md, "Nhân vật đại diện kênh".

Every caller that needs the canonical mascot's reference image or Flow media
id (adapters.py, image_pipeline.py, b2_bridge.py, flowpool/*) should resolve
it through mascot_for()/resolve() here instead of hard-coding a literal path
or media id, so adding a new channel is one CHANNEL_MASCOTS entry plus a new
assets/characters/<id>/character.json -- never a code change scattered across
Python and the Node B-2 Illustrator tools.

A resolved mascot with no reference image yet raises Blocked with the
MASCOT_REFERENCE_MISSING code and a command to fix it -- callers must never
substitute a different channel's mascot for a missing one.
"""
import shutil
from pathlib import Path

from pilot import Blocked, digest, read, write

CHARACTER_ID = 'CH01'  # The mascot is always the CH01 slot in a script's characters list.
DEFAULT_MASCOT_ID = 'channel-mascot'  # No/unknown channel -> current (vocab) behaviour.
CHANNEL_MASCOTS = {
    'tiensu': 'tiensu-mascot',
}


def known_channels():
    return sorted(CHANNEL_MASCOTS) + ['default']


def resolve_mascot_id(name):
    """Map a channel key ('tiensu'), 'default', or a literal folder id to a folder id."""
    if name in (None, '', 'default', 'vocab', 'channel'):
        return DEFAULT_MASCOT_ID
    if name in CHANNEL_MASCOTS:
        return CHANNEL_MASCOTS[name]
    if name == DEFAULT_MASCOT_ID or name in CHANNEL_MASCOTS.values():
        return name
    raise Blocked(f"Unknown mascot/channel '{name}'. Known: {', '.join(known_channels())}")


def job_of(path):
    """Best-effort job id from a runs/<job>/... path; None if it isn't under runs/."""
    parts = Path(path).resolve().parts
    if 'runs' in parts:
        i = parts.index('runs')
        if i + 1 < len(parts):
            return parts[i + 1]
    return None


def _channel_of(p, job_or_brief):
    if job_or_brief is None:
        return None
    if isinstance(job_or_brief, dict):
        return job_or_brief.get('channel')
    if isinstance(job_or_brief, (list, tuple)):
        return (job_or_brief[0] or {}).get('channel') if job_or_brief else None
    # A job id: look up its saved brief (may legitimately be None -- no brief yet/legacy job).
    brief = p.brief(job_or_brief)
    return brief[0].get('channel') if brief else None


def resolve(root, channel=None, *, require_media_id=False):
    """Resolve the canonical mascot folder for `channel` under `root` (sys/).

    Returns {'id', 'character_id', 'reference_path', 'media_id', 'appearance',
    'character_json'}. Raises Blocked(MASCOT_REFERENCE_MISSING: ...) when the
    folder's character.json has no approved reference image yet -- never
    silently substitutes another channel's mascot. With require_media_id=True
    (batch/queue paths, which need an already Flow-registered character),
    also raises Blocked(MASCOT_MEDIA_ID_MISSING: ...) when the reference
    exists but character.json's flow.media_id is still null.
    """
    root = Path(root)
    mascot_id = CHANNEL_MASCOTS.get(channel, DEFAULT_MASCOT_ID)
    char_dir = root / 'assets/characters' / mascot_id
    cj_path = char_dir / 'character.json'
    cj = read(cj_path) if cj_path.exists() else {}
    ref_name = cj.get('reference')
    ref_path = (char_dir / ref_name) if ref_name else None
    if not ref_path or not ref_path.exists():
        raise Blocked(
            f"MASCOT_REFERENCE_MISSING: {mascot_id} has no approved reference image yet. "
            f"Get an approved image for this character, then run: "
            f"python3 pilot.py mascot-reference {channel or 'default'} --from FILE "
            f"(fills reference/sha256 in {cj_path.relative_to(root)})."
        )
    media_id = (cj.get('flow') or {}).get('media_id')
    if require_media_id and not media_id:
        raise Blocked(
            f"MASCOT_MEDIA_ID_MISSING: {mascot_id} has a reference image but is not yet "
            f"registered in Flow (character.json flow.media_id is null). Batch/queue "
            f"generation needs an already-registered character; register {mascot_id} in "
            f"Flow first, or avoid flow_batch/flowpool_enabled for this channel until it is."
        )
    return {
        'id': mascot_id,
        'character_id': CHARACTER_ID,
        'reference_path': ref_path,
        'media_id': media_id,
        'appearance': cj.get('identity', {}),
        'character_json': cj_path,
    }


def try_resolve(root, channel=None, *, require_media_id=False):
    """Like resolve(), but returns None instead of raising. For opportunistic/
    legacy call sites that historically used a plain `.exists()` check and
    must keep degrading gracefully rather than blocking production."""
    try:
        return resolve(root, channel, require_media_id=require_media_id)
    except Blocked:
        return None


def mascot_for(p, job_or_brief, *, require_media_id=False):
    """Resolve the mascot for a Pilot job.

    `job_or_brief` may be a job id (str, looked up via p.brief()), a brief
    dict, the (brief, revision, hash) tuple p.brief() returns, or None.
    `p` only needs a `.root` attribute (and `.brief(job_id)` if a job id is
    passed).
    """
    channel = _channel_of(p, job_or_brief)
    return resolve(p.root, channel, require_media_id=require_media_id)


def try_mascot_for(p, job_or_brief, *, require_media_id=False):
    try:
        return mascot_for(p, job_or_brief, require_media_id=require_media_id)
    except Blocked:
        return None


def set_reference(root, name, from_file):
    """Copy an already-approved image into <mascot>/reference-v1.<ext> and
    fill character.json's reference/sha256. Never generates an image itself.
    Used by `python3 pilot.py mascot-reference <channel> --from FILE`.
    """
    root = Path(root)
    mascot_id = resolve_mascot_id(name)
    char_dir = root / 'assets/characters' / mascot_id
    if not char_dir.is_dir():
        raise Blocked(f'Unknown mascot folder: {char_dir}')
    src = Path(from_file)
    if not src.is_file():
        raise Blocked(f'--from file not found: {from_file}')
    if src.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
        raise Blocked(f'--from must be a png/jpg/jpeg/webp image, got: {src.suffix}')
    cj_path = char_dir / 'character.json'
    cj = read(cj_path) if cj_path.exists() else {}
    ref_name = 'reference-v1' + src.suffix.lower()
    dest = char_dir / ref_name
    shutil.copy(src, dest)
    sha = digest(dest)
    cj['reference'] = ref_name
    cj['sha256'] = sha
    write(cj_path, cj)
    return {'id': mascot_id, 'reference': str(dest.relative_to(root)), 'sha256': sha,
            'character_json': str(cj_path.relative_to(root))}
