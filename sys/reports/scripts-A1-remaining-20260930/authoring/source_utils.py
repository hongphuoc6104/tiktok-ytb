from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'reports/scripts-A1-remaining-20260930'
ENTRIES = {e['number']: e for e in json.loads((OUT / 'selection.json').read_text())}

def records():
    result = {}
    for f in sorted((OUT / 'authoring').glob('[0-9]*.txt')):
        for block in f.read_text().split('@')[1:]:
            lines = block.strip().splitlines()
            n, title, objective, setting, plot = lines[0].split('|')
            n = int(n)
            assert n not in result, n
            rows = [r.split('|') for r in lines[1:]]
            assert len(rows) == ENTRIES[n]['scene_count'], (n, len(rows))
            assert all(len(r) == 2 for r in rows), n
            result[n] = dict(number=n, title=title, objective=objective, setting=setting, plot=plot, rows=rows)
    return result

def quotes(text):
    return re.findall(r'"([^"]+)"', text)

IRREGULAR = {
    'be': ['be','am','is','are','was','were','been','being'],
    'have': ['have','has','had','having'], 'get': ['get','gets','got','getting'],
    'find': ['find','finds','found','finding'], 'keep': ['keep','keeps','kept','keeping'],
    'break': ['break','breaks','broke','broken','breaking'], 'hold': ['hold','holds','held','holding'],
    'let': ['let','lets','letting'], 'give': ['give','gives','gave','given','giving'],
    'go': ['go','goes','went','gone','going'], 'come': ['come','comes','came','coming'],
    'begin': ['begin','begins','began','begun','beginning'], 'send': ['send','sends','sent','sending'],
    'put': ['put','puts','putting'], 'lose': ['lose','loses','lost','losing'],
    'choose': ['choose','chooses','chose','chosen','choosing'], 'cut': ['cut','cuts','cutting'],
    'fall': ['fall','falls','fell','fallen','falling'], 'fly': ['fly','flies','flew','flown','flying'],
    'sleep': ['sleep','sleeps','slept','sleeping'], 'hit': ['hit','hits','hitting'],
    'sit': ['sit','sits','sat','sitting'], 'stand': ['stand','stands','stood','standing'],
    'lie': ['lie','lies','lay','lain','lying'], 'meet': ['meet','meets','met','meeting'],
    'write': ['write','writes','wrote','written','writing'], 'read': ['read','reads','reading'],
    'feel': ['feel','feels','felt','feeling'], 'say': ['say','says','said','saying'],
    'tell': ['tell','tells','told','telling'], 'do': ['do','does','did','done','doing'],
    'make': ['make','makes','made','making'], 'take': ['take','takes','took','taken','taking'],
    'bring': ['bring','brings','brought','bringing']
}

def contains_target(text, e):
    word = e['teaching_form'].lower()
    parts = word.split()
    first = parts[0]
    forms = IRREGULAR.get(first, [first])[:]
    if e['pos'] in {'v','phr'} and first not in IRREGULAR:
        forms += [first+'s', first+'es', first+'ed', first+'d', first+'ing', first[:-1]+'ing']
        if first.endswith('y'):
            forms += [first[:-1]+'ies', first[:-1]+'ied']
    if e['pos'] == 'n':
        forms += [word+'s', word+'es']
    if e['pos'] == 'adj':
        forms += [word+'er', word+'est', word[:-1]+'er', word[:-1]+'est']
        if word.endswith('y'):
            forms += [word[:-1]+'ier', word[:-1]+'iest']
    if len(parts) > 1:
        pattern = r'\b(?:'+'|'.join(re.escape(v) for v in forms)+r')\b'
        for part in parts[1:]:
            pattern += r'.*?\b'+re.escape(part)+r'\b'
    else:
        pattern = r'(?<!\w)(?:'+'|'.join(re.escape(v) for v in forms)+r')(?!\w)'
    return bool(re.search(pattern, text.lower()))

def model_indices(count):
    return [1, 2] if count == 5 else [1, 3]

def practice_quotes(text):
    # English instructional phrases before the Vietnamese speaking/completion cue
    # are narration, not the learner's displayed response or options.
    cue = re.search(r'(?:Nói(?: lại)?|Đọc|Hoàn thành|nói(?: lại)?|đọc|hoàn thành|Hãy chọn|hãy chọn|Chọn|chọn)\b', text)
    tail = text[cue.start():] if cue else text
    return quotes(tail)

def pause_for(rec):
    q = practice_quotes(rec['rows'][-2][0])
    utterance = max((len(x.split()) for x in q), default=5)
    if rec['number'] in {626, 627}:
        return 6
    return 4 if utterance <= 4 else 5 if utterance <= 8 else 6 if utterance <= 12 else 7
