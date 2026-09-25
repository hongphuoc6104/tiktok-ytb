"""Long-form content-v3 (8-12 min explainers): budgeted scene-by-scene generation with bounded repair.

One agy call cannot write a 2,000-syllable script with 100+ beats reliably, so after the outline the
adapter asks for the cast, then one scene at a time (with the narration already written for earlier
scenes), then packaging. Every call is recorded under the attempt dir. The assembled draft goes
through the unchanged content_contract; failing scenes get at most `rounds` targeted repair calls.
Nothing here approves, measures audio or generates media: budgets are estimates, WAV decides later.
"""
import copy
import json
import math
import re

from content_contract import ContractError, error, validate_content
from pilot import Blocked, read, write
from scripts.story_plan import plan_languages

LONGFORM_MIN_SECONDS = 300
BEAT_SECONDS = 5          # target: one beat (image or overlay change) every 4-6 s
IMAGES_PER_BEAT = .5      # distinct images per beat; the rest re-use a still with new overlays
TOLERANCE = .15           # budgets are hard targets +-15 %
REPAIR_ROUNDS = 2


def is_longform(b):
    """Long-form briefs use the scene-by-scene path; everything else keeps the single call."""
    return b.get('schema_version') == '3.0' and (
        b.get('channel') == 'tiensu' or b['duration']['max_seconds'] > LONGFORM_MIN_SECONDS)


def units(text):
    """Same unit as story_plan.estimates: space-separated words (Vietnamese syllables)."""
    return len((text or '').split())


def clip_split(total, n):
    """Spread brief.clips.max over scenes: hook and ending first, then the chapters in order."""
    counts = [0] * n
    order = list(dict.fromkeys([0, n - 1] + list(range(1, n - 1))))
    for i in range(max(0, total)):
        counts[order[i % len(order)]] += 1
    return counts


def budgets(b, outline):
    """Per-scene targets from brief duration midpoint and speech_rates; scenes carrying more
    required points get proportionally more time."""
    rows = outline['outline']
    target = (b['duration']['min_seconds'] + b['duration']['max_seconds']) / 2
    weights = [1 + .2 * max(0, len(x['requirements']) - 1) for x in rows]
    clips = clip_split(int((b.get('clips') or {}).get('max', 0)), len(rows))
    rates = b['planning']['speech_rates']
    scenes = []
    for row, weight, clip_max in zip(rows, weights, clips):
        seconds = target * weight / sum(weights)
        beats = max(2, round(seconds / BEAT_SECONDS))
        images = max(2, min(beats, round(beats * IMAGES_PER_BEAT)))
        speech = {}
        for lang in plan_languages(b):
            n = round(seconds * rates[lang]['units_per_second'])
            speech[lang] = {'target': n, 'min': math.floor(n * (1 - TOLERANCE)), 'max': math.ceil(n * (1 + TOLERANCE))}
        scenes.append({'scene_id': row['scene_id'], 'seconds': round(seconds, 1), 'units': speech,
                       'beats': beats, 'beats_min': max(1, math.floor(seconds / 6)), 'beats_max': math.ceil(seconds / 4),
                       'images': images, 'images_min': max(1, math.floor(images * (1 - TOLERANCE))),
                       'clips_max': clip_max})
    total = {lang: sum(s['units'][lang]['target'] for s in scenes) for lang in plan_languages(b)}
    return {'target_seconds': target, 'units_total': total, 'beats_total': sum(s['beats'] for s in scenes),
            'images_total': sum(s['images'] for s in scenes), 'clips_max': sum(clips), 'scenes': scenes,
            'unit': 'space-separated words (Vietnamese syllables); estimate, WAV measures real duration'}


def _schema(root):
    return read(root / 'schemas/content-v3.json')


def _drop_scene_id(item):
    item = copy.deepcopy(item)
    item['properties'].pop('scene_id', None)
    item['required'] = [x for x in item['required'] if x != 'scene_id']
    return item


def scene_schema(root):
    s = _schema(root)['properties']
    return {'type': 'object', 'additionalProperties': False, 'required': ['scene', 'coverage', 'claims'],
            'properties': {'scene': copy.deepcopy(s['scenes']['items']),
                           'coverage': {'type': 'array', 'items': _drop_scene_id(s['coverage']['items'])},
                           'claims': {'type': 'array', 'items': _drop_scene_id(s['claims']['items'])}}}


def cast_schema(root):
    s = _schema(root)['properties']
    return {'type': 'object', 'additionalProperties': False, 'required': ['characters'],
            'properties': {'characters': dict(copy.deepcopy(s['characters']), minItems=1)}}


def closing_schema(root):
    s = _schema(root)['properties']
    keys = ['packaging', 'open_questions', 'revision_response']
    return {'type': 'object', 'additionalProperties': False, 'required': keys,
            'properties': {k: copy.deepcopy(s[k]) for k in keys}}


RULES = '''
LONG-FORM MODE (overrides any instruction above to return the whole content-v3 in one reply).
The video is long, so it is written scene by scene. In this call write exactly ONE scene: the one named in "task".
Hard rules:
1. Narration first. Write the complete narration of this scene to its budget (hard target, +-15%; units are
   space-separated words, i.e. Vietnamese syllables). Only after the narration is final, place beat anchors,
   coverage quotes and claim quotes on top of it; each must be a verbatim substring of THIS scene's narration.
   Never edit narration after anchoring. Continue naturally from the narration of earlier scenes; do not repeat it.
2. Beats: one beat every 4-6 seconds of narration (see the beats budget). The first beat anchors the very first
   words of the narration; later anchors appear in strictly increasing order.
3. Images: about the images budget of distinct images. Re-use a still across consecutive beats and change the
   overlay/effect/focus instead of drawing a new image each time. based_on only names an earlier image of this
   scene. Ids: stills "<scene>_I01", "<scene>_I02"...; clips "<scene>_C01"...; beats "<scene>_B01"...
4. Never write management ids (character ids such as CH01, scene ids such as SC03, image or beat ids) in the
   narration, in image description/preserve/change/motion, or in overlay text. Describe characters by their
   name and appearance from the cast (e.g. "the prehistoric mascot with messy brown hair and a hide tunic").
5. Overlay text is short: label and map_pin <= 40 characters, chapter_title <= 60, counter and arrow <= 30.
6. Keep visible_text [] when the brief forbids text in images; all words go into beat overlays.
7. Clips: at most clips_max in this scene; a clip needs from_image = a still of this scene, motion in English,
   and no visible_text.
8. scene.id, scene.purpose and scene.requirements must equal the outline row for this scene. Use only
   character ids from the cast. coverage: one item per requirement of this scene, quoting the sentence that
   really conveys it. claims: every number, named study or site in the narration, fact copied verbatim from
   the brief sources[].facts, source_id also listed in scene.source_ids.
Return only JSON {"scene", "coverage", "claims"} matching the schema.'''

CAST = '''
LONG-FORM MODE: before scenes are written, declare the cast for the whole video. Return only JSON {"characters"}.
The main character follows the brief (channel mascot when the brief names one). name/appearance/outfit describe
people visually and must never contain ids of any kind (no CH01, SC01, image or beat ids). Keep the cast small.'''

CLOSING = '''
LONG-FORM MODE: all scenes are written and checked. Do not change them. Return only JSON with
"packaging" (follow the brief/channel packaging rules; thumbnail.image_id must be one of the listed still ids),
"open_questions" and "revision_response" (one item per revision request, status addressed/unresolved with
honest explanation and the scene_ids it touched; empty list when there are no requests).'''

REPAIR = '''
REPAIR MODE: the scene below failed validation. Fix every listed error and return the corrected scene in the
same JSON schema ({"scene", "coverage", "claims"}). Change only what the errors require.
If an error concerns the narration (BUDGET_UNITS length, ids spoken in the narration), rewrite the narration first,
then re-derive every beat anchor, coverage quote and claim quote verbatim from the new narration.
Otherwise keep the narration byte-identical. All long-form rules above still apply.'''


class Recorder:
    """Every agy call leaves <attempt>/calls/NN-label.request.json and .response.json (or .error.json)."""

    def __init__(self, out, invoke, timeout):
        self.out, self.dir = out, out / 'calls'; self.dir.mkdir(exist_ok=True)
        self.invoke, self.timeout, self.n, self.log = invoke, timeout, 0, []

    def __call__(self, label, prompt, schema):
        self.n += 1; stem = f'{self.n:02}-{label}'
        write(self.dir / f'{stem}.request.json', {'label': label, 'timeout': self.timeout, 'prompt': prompt, 'schema': schema})
        try:
            result = self.invoke(prompt, schema, self.out, timeout=self.timeout)
        except Exception as ex:
            write(self.dir / f'{stem}.error.json', {'label': label, 'error': str(ex)}); raise
        write(self.dir / f'{stem}.response.json', result)
        self.log.append({'call': stem, 'conversation_id': result.get('conversation_id')})
        data = result.get('structured_output')
        if not isinstance(data, dict): raise Blocked(f'AGY_PROTOCOL: {label} missing structured_output')
        return data


def internal_ids(content):
    ids = [s['id'] for s in content['scenes']] + [c['id'] for c in content['characters']]
    ids += [x['id'] for s in content['scenes'] for k in ('images', 'beats') for x in s.get(k, [])]
    return [x for x in ids if x]


def has_id(text, ids):
    return any(re.search(r'(?<!\w)' + re.escape(code) + r'(?!\w)', text or '', re.I) for code in ids)


def local_errors(b, content, plan):
    """Budget and spoken-id checks the contract does not make; each error names its scene."""
    errors = []
    budget = {x['scene_id']: x for x in plan['scenes']}
    ids = internal_ids(content)
    for s in content['scenes']:
        q = budget.get(s['id'])
        if not q: continue
        for lang in plan_languages(b):
            n = units(s.get('narration_en' if lang == 'en' else 'narration'))
            u = q['units'][lang]
            if not u['min'] <= n <= u['max']:
                errors.append(error('BUDGET_UNITS', s['id'], f'Lời dẫn {lang} có {n} âm tiết/từ, ngân sách {u["min"]}-{u["max"]} (mục tiêu {u["target"]})',
                                    'Viết lại lời dẫn đúng ngân sách rồi đặt lại neo/coverage/claims.'))
        beats, images = s.get('beats', []), s.get('images', [])
        if not q['beats_min'] <= len(beats) <= q['beats_max']:
            errors.append(error('BUDGET_BEATS', s['id'], f'{len(beats)} nhịp, cần {q["beats_min"]}-{q["beats_max"]} (4-6 giây/nhịp)',
                                'Thêm/bớt nhịp; dùng lại ảnh still với overlay mới.'))
        if len(images) < q['images_min']:
            errors.append(error('BUDGET_IMAGES', s['id'], f'{len(images)} ảnh, cần ít nhất {q["images_min"]}', 'Thêm ảnh có chức năng kể chuyện.'))
        clips = sum(1 for im in images if im.get('kind') == 'clip')
        if clips > q['clips_max']:
            errors.append(error('BUDGET_CLIPS', s['id'], f'{clips} clip, tối đa {q["clips_max"]}', 'Đổi clip thừa thành ảnh still.'))
        if has_id(s.get('narration', '') + ' ' + s.get('narration_en', ''), ids):
            errors.append(error('INTERNAL_LABEL', s['id'], 'Mã nội bộ bị đọc trong lời dẫn', 'Gọi nhân vật bằng tên/mô tả, không dùng mã.'))
    return errors


def contract_errors(root, b, revision, bhash, content):
    try:
        validate_content(root, b, revision, bhash, content)
    except ContractError as ex:
        errors = ex.errors
    else:
        return []
    if not any(e['code'] == 'SCHEMA' for e in errors):
        # validate_content stops before the plan checks; collect them too so one repair round sees all errors.
        from scripts.story_plan import validate_plan
        try:
            validate_plan(b, content)
        except ContractError as ex:
            errors += [e for e in ex.errors if e not in errors]
        except Exception:
            pass
    return errors


def assign(content, errors):
    """Map each error to the scene that owns it; None = packaging; 'other' = not repairable per scene."""
    scenes = content['scenes']
    owner = {}
    for s in scenes:
        owner[s['id']] = s['id']
        for k in ('images', 'beats'):
            for x in s.get(k, []): owner.setdefault(x['id'], s['id'])
    by_id = {s['id']: s for s in scenes}
    def bad_items():
        bad = set()
        for c in content['coverage']:
            s = by_id.get(c['scene_id'], {})
            if c['quote'] not in s.get('narration', '') or c['requirement_id'] not in s.get('requirements', []): bad.add(c['scene_id'])
            if c.get('quote_en') is not None and c['quote_en'] not in s.get('narration_en', ''): bad.add(c['scene_id'])
        covered = {(c['scene_id'], c['requirement_id']) for c in content['coverage']}
        for s in scenes:
            if any((s['id'], r) not in covered for r in s.get('requirements', [])): bad.add(s['id'])
        for c in content['claims']:
            s = by_id.get(c['scene_id'], {})
            text = s.get('narration_en' if c['language'] == 'en' else 'narration', '')
            if c['quote'] not in text or c['source_id'] not in s.get('source_ids', []): bad.add(c['scene_id'])
        return bad
    result, other = {}, []
    for e in errors:
        path = e['path']; head = path.split('/')[0]
        targets = []
        if path.startswith('scenes/') and path.split('/')[1].isdigit() and int(path.split('/')[1]) < len(scenes):
            targets = [scenes[int(path.split('/')[1])]['id']]
        elif head in owner:
            targets = [owner[head]]
        elif head in ('coverage', 'claims'):
            parts = path.split('/')
            items = content[head]
            if len(parts) > 1 and parts[1].isdigit() and int(parts[1]) < len(items): targets = [items[int(parts[1])]['scene_id']]
            else: targets = sorted(bad_items()) or ([s['id'] for s in scenes if s.get('source_ids')] if head == 'claims' else [])
        elif head == 'packaging' or e['code'] == 'PACKAGING' or head == 'revision_response':
            targets = [None]
        if not targets: other.append(e); continue
        for t in targets: result.setdefault(t, []).append(e)
    return result, other


def assemble(b, revision, bhash, outline, characters, parts, closing):
    scenes, coverage, claims = [], [], []
    for row in outline['outline']:
        part = parts[row['scene_id']]
        scene = copy.deepcopy(part['scene'])
        # Deterministic keys the outline already fixed; narration and visuals stay as written.
        scene.update(id=row['scene_id'], purpose=row['purpose'], requirements=list(row['requirements']))
        scenes.append(scene)
        coverage += [dict(c, scene_id=row['scene_id']) for c in part.get('coverage', [])]
        claims += [dict(c, scene_id=row['scene_id']) for c in part.get('claims', [])]
    content = {'schema_version': '3.0', 'brief_revision': revision, 'brief_hash': bhash, 'topic': b['topic'],
               'duration': b['duration'], 'style': b['style'], 'required_points': [x['text'] for x in b['required_points']],
               'characters': characters, 'scenes': scenes, 'coverage': coverage, 'outline': outline['outline'],
               'claims': claims, 'revision_response': closing.get('revision_response', []),
               'open_questions': closing.get('open_questions', [])}
    if closing.get('packaging'): content['packaging'] = closing['packaging']
    return content


def _scene_part(data, label):
    if not isinstance(data.get('scene'), dict): raise Blocked(f'AGY_PROTOCOL: {label} returned no scene object')
    return {'scene': data['scene'], 'coverage': list(data.get('coverage') or []), 'claims': list(data.get('claims') or [])}


def generate(root, out, prompt, b, revision, bhash, outline, invoke, timeout, rounds=REPAIR_ROUNDS):
    """Return (content, calls). Raises ContractError with the remaining errors after `rounds` repairs."""
    plan = budgets(b, outline); write(out / 'budget.json', plan)
    call = Recorder(out, invoke, timeout)
    one_scene = scene_schema(root)
    characters = call('cast', prompt + CAST, cast_schema(root))['characters']
    parts = {}
    budget = {x['scene_id']: x for x in plan['scenes']}
    rows = outline['outline']
    for i, row in enumerate(rows):
        sid = row['scene_id']
        earlier = [{'scene_id': r['scene_id'], 'chapter': parts[r['scene_id']]['scene'].get('chapter'),
                    'narration': parts[r['scene_id']]['scene'].get('narration'),
                    'narration_en': parts[r['scene_id']]['scene'].get('narration_en')} for r in rows[:i]]
        task = {'scene_id': sid, 'position': f'{i + 1}/{len(rows)}', 'outline_row': row, 'budget': budget[sid],
                'video_budget': {k: plan[k] for k in ('target_seconds', 'units_total', 'beats_total', 'images_total', 'clips_max')},
                'cast': characters, 'earlier_scenes': earlier}
        if i == len(rows) - 1 and len(rows) > 1:
            task['opening_images'] = [{k: im.get(k) for k in ('id', 'description')} for im in parts[rows[0]['scene_id']]['scene'].get('images', [])]
            task['note'] = 'Final scene: close the loop with the opening scene (same setting/image idea redrawn in this scene, not a cross-scene image id).'
        parts[sid] = _scene_part(call(f'scene-{sid}', prompt + RULES + '\nTask data: ' + json.dumps(task, ensure_ascii=False), one_scene), sid)

    def closing_call(label, extra=''):
        summary = [{'scene_id': s, 'chapter': parts[s]['scene'].get('chapter'), 'narration': parts[s]['scene'].get('narration'),
                    'stills': [{'id': im['id'], 'description': im.get('description')} for im in parts[s]['scene'].get('images', [])
                               if im.get('kind', 'still') == 'still']} for s in parts]
        return call(label, prompt + CLOSING + extra + '\nScenes: ' + json.dumps(summary, ensure_ascii=False), closing_schema(root))

    closing = closing_call('packaging')
    for attempt in range(rounds + 1):
        content = assemble(b, revision, bhash, outline, characters, parts, closing)
        errors = contract_errors(root, b, revision, bhash, content) + local_errors(b, content, plan)
        if not errors:
            return content, call.log
        write(out / f'validation-{attempt}.json', errors); write(out / f'assembled-{attempt}.json', content)
        if attempt == rounds:
            raise ContractError(errors)
        targets, other = assign(content, errors)
        if other:
            raise ContractError(errors)  # cast/style/brief errors: no scene-targeted repair can fix them
        for sid, errs in targets.items():
            if sid is None:
                closing = closing_call(f'repair{attempt + 1}-packaging', '\nFix these validation errors: ' + json.dumps(errs, ensure_ascii=False))
                continue
            current = {'scene': next(s for s in content['scenes'] if s['id'] == sid),
                       'coverage': [{k: v for k, v in c.items() if k != 'scene_id'} for c in content['coverage'] if c['scene_id'] == sid],
                       'claims': [{k: v for k, v in c.items() if k != 'scene_id'} for c in content['claims'] if c['scene_id'] == sid]}
            data = {'errors': errs, 'budget': budget[sid], 'outline_row': next(r for r in rows if r['scene_id'] == sid),
                    'cast': characters, 'current': current}
            parts[sid] = _scene_part(call(f'repair{attempt + 1}-{sid}', prompt + RULES + REPAIR + '\nRepair data: ' + json.dumps(data, ensure_ascii=False), one_scene), sid)
