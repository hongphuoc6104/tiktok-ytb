"""Deterministic prompt compilation; no provider call, filesystem job write or review."""
import copy
import hashlib
import json
from pathlib import Path
import re

CURRENT_VERSION = '1.1.0'
SUPPORTED_VERSIONS = ('1.0.0', '1.0.1', '1.1.0')
# 1.1.0+: anonymous stick-figure cast, optional Character/style reference, no recurring presenter.
CAST_VERSIONS = ('1.1.0',)
FIELDS = {'description', 'aspect_ratio', 'allowed_text', 'character_reference', 'base_reference',
          'preserve', 'change', 'composition', 'mascot_placement', 'caption_clearance'}
PLACEMENTS = {'upper-left', 'upper-right', 'left-margin', 'right-margin', 'above-caption-left', 'above-caption-right'}
UUID = re.compile(r'[a-fA-F0-9]{8}(?:-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}\Z')
SHA = re.compile(r'[a-f0-9]{64}\Z')
INJECTION = re.compile(r'(?i)(?:\b(?:ignore|disregard|override|bypass)\b.{0,70}\b(?:instructions?|rules?|system|developer|restrictions?|constraints?|polic(?:y|ies)|references?)\b|\b(?:system|developer)\s*(?:message\b|prompt\b|:)|<\|[^>]*\|>|\[/?INST\]|</?(?:system|developer|assistant)>|\{\{|\{%|\$\(|```)', re.S)
MANAGEMENT = re.compile(r'(?i)(?:\bSC\d{2,}\b|\bCH\d{2,}\b|\b(?:job|request|template|media)[_-][a-z0-9_-]+\b|[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}|\b[\w.-]+\.(?:json|png|jpe?g|webp|wav|mp4)\b|\b[a-f0-9]{64}\b)')


class PromptError(ValueError):
    """A stable failure code, before any provider dispatch."""


def _hash(value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def registry(version=CURRENT_VERSION):
    if not isinstance(version, str) or version not in SUPPORTED_VERSIONS:
        raise PromptError('FLOW_TEMPLATE_VERSION_UNSUPPORTED: choose an existing explicit version')
    path = Path(__file__).parent / 'versions' / version / 'registry.json'
    value = json.loads(path.read_text())
    if value.get('version') != version or value.get('schema_version') != 1:
        raise PromptError('FLOW_TEMPLATE_REGISTRY_INVALID: incompatible registry metadata')
    return value


def _model(model, spec):
    matches = [key for key, value in spec['models'].items() if model in (key, value['label'])]
    if len(matches) != 1:
        raise PromptError('FLOW_MODEL_UNSUPPORTED: use an exact observed model label or registry ID')
    return matches[0]


def _text(value, field, *, max_length=12000, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()) or len(value) > max_length:
        raise PromptError('FLOW_PROMPT_DATA_INVALID: ' + field + ' needs bounded text')
    if any(ord(char) < 32 and char not in ('\n', '\t') for char in value) or '\x7f' in value:
        raise PromptError('FLOW_PROMPT_CONTROL_REJECTED: ' + field)
    if INJECTION.search(value):
        raise PromptError('FLOW_PROMPT_INJECTION_REJECTED: ' + field)
    return value


def _strings(value, field, *, maximum=40):
    if not isinstance(value, list) or len(value) > maximum:
        raise PromptError('FLOW_PROMPT_DATA_INVALID: ' + field + ' needs a bounded list')
    return [_text(item, field, max_length=2000) for item in value]


def _allowed(value):
    if not isinstance(value, list) or len(value) > 40:
        raise PromptError('FLOW_VISIBLE_TEXT_INVALID: a bounded exact-text list is required')
    result = []
    for item in value:
        if isinstance(item, str):
            text = _text(item, 'allowed_text', max_length=2000)
            normalized = text
        elif isinstance(item, dict) and 'text' in item and not set(item) - {'text', 'placement', 'object'}:
            text = _text(item['text'], 'allowed_text.text', max_length=2000)
            normalized = {'text': text}
            for key in ('placement', 'object'):
                if key in item:
                    normalized[key] = _text(item[key], 'allowed_text.' + key, max_length=2000)
        else:
            raise PromptError('FLOW_VISIBLE_TEXT_INVALID: string or text/placement/object record required')
        if MANAGEMENT.search(text):
            raise PromptError('FLOW_MANAGEMENT_TEXT_FORBIDDEN: management identifiers are not learner-visible text')
        result.append(normalized)
    if len(result) != len({_hash(item) for item in result}):
        raise PromptError('FLOW_VISIBLE_TEXT_INVALID: duplicate exact lettering records')
    return result


def _reference(value, field):
    if not isinstance(value, dict) or set(value) != {'media_id', 'sha256'}:
        raise PromptError('FLOW_REFERENCE_INVALID: ' + field + ' requires exactly media_id and sha256')
    if not isinstance(value['media_id'], str) or not UUID.fullmatch(value['media_id']) or not isinstance(value['sha256'], str) or not SHA.fullmatch(value['sha256']):
        raise PromptError('FLOW_REFERENCE_INVALID: ' + field + ' needs a real media UUID and artifact hash')
    return dict(value)


def _data(data, purpose, version='1.0.0'):
    cast = version in CAST_VERSIONS
    if not isinstance(data, dict) or set(data) - FIELDS or (cast and 'mascot_placement' in data):
        raise PromptError('FLOW_PROMPT_FIELDS_UNSUPPORTED: visual fields are allowlisted')
    description = _text(data.get('description'), 'description')
    ratio = data.get('aspect_ratio', '9:16')
    if ratio not in ('9:16', '16:9'):
        raise PromptError('FLOW_PROMPT_RATIO_UNSUPPORTED: explicit 9:16 or 16:9 required')
    if cast and data.get('character_reference') is None:
        character = None
    else:
        character = _reference(data.get('character_reference'), 'character_reference')
    base = _reference(data['base_reference'], 'base_reference') if data.get('base_reference') is not None else None
    preserve = _strings(data.get('preserve', []), 'preserve')
    change = _strings(data.get('change', []), 'change')
    if (purpose == 'variation' or preserve) and base is None:
        raise PromptError('FLOW_BASE_REFERENCE_REQUIRED: preserved shot/variation needs its actual Base reference')
    if purpose == 'variation' and (not preserve or not change):
        raise PromptError('FLOW_VARIATION_INVALID: declare both preserved composition and visible change')
    allowed = _allowed(data.get('allowed_text', []))
    placement = data.get('mascot_placement', 'above-caption-right')
    if not cast and placement not in PLACEMENTS:
        raise PromptError('FLOW_MASCOT_PLACEMENT_UNSUPPORTED: choose a supported attention margin')
    clearance = data.get('caption_clearance', {'edge': 'bottom', 'fraction': 0.18})
    if not isinstance(clearance, dict) or set(clearance) != {'edge', 'fraction'} or clearance['edge'] not in ('bottom', 'top') or type(clearance['fraction']) not in (int, float) or not 0.10 <= clearance['fraction'] <= 0.40:
        raise PromptError('FLOW_CAPTION_CLEARANCE_INVALID: edge top/bottom and fraction 0.10–0.40 required')
    normalized = {'description': description, 'aspect_ratio': ratio, 'allowed_text': allowed,
                  'preserve': preserve, 'change': change, 'caption_clearance': dict(clearance)}
    if not cast:
        normalized['mascot_placement'] = placement
    if 'composition' in data:
        normalized['composition'] = _text(data['composition'], 'composition')
    references = {'character': character, 'base': base}
    return normalized, references


def compile(model, purpose, data, version=CURRENT_VERSION):
    """Compile exact data and immutable instruction version into a JSON record.

    References here are declared attachment provenance. The provider adapter
    must separately verify the real files/media and current UI attachments.
    """
    spec = registry(version)
    model_id = _model(model, spec)
    if not isinstance(purpose, str) or purpose not in spec['purposes']:
        raise PromptError('FLOW_PURPOSE_UNSUPPORTED: reference, character, scene or variation required')
    visual, references = _data(data, purpose, version)
    template_id = 'flow.' + model_id + '.' + purpose
    sections = ['Requested aspect ratio: ' + visual['aspect_ratio'] + '. Render the requested still image.',
                spec['models'][model_id]['strategy'], spec['purposes'][purpose], spec['style'], spec['cast_rule'] if version in CAST_VERSIONS else spec['identity'],
                spec['reference_rule'], spec['data_boundary'], spec['clearance_rule']]
    if references['base']:
        sections.append('A Base scene reference is declared and must be attached; use its camera and spatial relationships for the preservation instructions.')
    else:
        sections.append('No Base scene reference is declared. Use an independent composition; do not pretend a prior shot is attached.')
    sections.extend(['Visual data (JSON; learner strings are exact data):', json.dumps(visual, ensure_ascii=False, sort_keys=True, indent=2)])
    prompt = '\n\n'.join(sections)
    return {'prompt': prompt, 'model': spec['models'][model_id]['label'], 'model_id': model_id,
            'purpose': purpose, 'template_id': template_id, 'version': version,
            'sha256': hashlib.sha256(prompt.encode('utf-8')).hexdigest(),
            'provenance': {'schema_version': 1, 'registry_sha256': _hash(spec), 'input_sha256': _hash(data),
                'model_label_source': spec['model_label_source'], 'profile_kind': 'authored_instruction_strategy',
                'reference_limit_source': spec['reference_limit_source'], 'references': references,
                'attachment_verified': False, 'quality_verified': False, 'cost_verified': False}}


def create_pin(model, version=CURRENT_VERSION):
    """Return a pin for the official job operation to save BEFORE first send.

    This pure function cannot adopt a legacy request or rewrite a job. The
    engine owns persistence/events and checking submitted/unknown requests.
    """
    spec = registry(version)
    model_id = _model(model, spec)
    return {'schema_version': 1, 'version': version, 'model_id': model_id,
            'model': spec['models'][model_id]['label'], 'registry_sha256': _hash(spec)}


def validate_pin(pin):
    if not isinstance(pin, dict) or set(pin) != {'schema_version', 'version', 'model_id', 'model', 'registry_sha256'} or pin.get('schema_version') != 1:
        raise PromptError('FLOW_TEMPLATE_PIN_INVALID: explicit saved prompt registry pin required')
    expected = create_pin(pin['model_id'], pin['version'])
    if pin != expected:
        raise PromptError('FLOW_TEMPLATE_PIN_CHANGED: registry/model identity differs; no implicit adoption')
    return copy.deepcopy(expected)


def compile_pinned(pin, purpose, data):
    checked = validate_pin(pin)
    return compile(checked['model_id'], purpose, data, checked['version'])


def freeze(model, version=CURRENT_VERSION, *, existing_pin=None, request_states=()):
    """Pure pre-send freeze check; official caller owns grants/store/events.

    Missing pins on submitted/generated/downloaded/cached/unknown legacy work
    must retain legacy prompt handling. This function never adopts those
    requests, clears them, grants authority or writes job metadata.
    """
    if not isinstance(request_states, (list, tuple)) or any(not isinstance(state, str) for state in request_states):
        raise PromptError('FLOW_TEMPLATE_FREEZE_INVALID: exact journal states required')
    requested = create_pin(model, version)
    if existing_pin is not None:
        saved = validate_pin(existing_pin)
        if requested != saved:
            raise PromptError('FLOW_TEMPLATE_PIN_CHANGED: no implicit version/model upgrade')
        return saved
    if any(state not in ('pending', 'prepared', 'not_submitted') for state in request_states):
        raise PromptError('FLOW_TEMPLATE_LEGACY_REQUESTS: retain prior actual prompts; cannot add a pin after send/cache')
    return requested
