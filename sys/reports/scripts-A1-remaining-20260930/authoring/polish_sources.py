from pathlib import Path
import re, json
from source_utils import ROOT, OUT, ENTRIES

for e in ENTRIES.values():
    assert not (ROOT/'runs'/e['job']/'revisions/content/1/content.json').exists(), 'Never edit an authored source after submission: '+e['job']

def wrap_english(text):
    parts = re.split(r'("[^"]+")', text)
    pattern = r'(?<!\S)([A-Z][A-Za-z0-9 ,:\x27’\-]+[.!?])(?=\s|$)'
    def wrap(m):
        s = m.group(1)
        return '"'+s+'"' if len(re.findall(r'[A-Za-z]+',s)) >= 2 else s
    for i in range(0,len(parts),2):
        parts[i] = re.sub(pattern,wrap,parts[i])
    return ''.join(parts)

def move_practice_to_end(text):
    # Keep the learner's model unchanged; place existing explanation before it.
    m = re.match(r'^(.*?)(Nói lại|Nói|Đọc|Hoàn thành|nói lại|nói|đọc|hoàn thành)\s+"([^"]+)"(.*)$',text)
    if not m:
        return text
    prefix, command, model, tail = m.groups()
    if not tail.strip():
        return text
    modifier, sep, info = tail.partition(';')
    modifier = modifier.strip().rstrip('.')
    info = info.strip().rstrip('.')
    if info:
        prefix += info[:1].upper()+info[1:]+'. '
    if 'Hoàn thành' in command or 'hoàn thành' in command:
        command += ' câu'
    return prefix+command+(' '+modifier if modifier else '')+': "'+model+'"'

changed=0
for f in sorted((OUT/'authoring').glob('[0-9]*.txt')):
    blocks=[]
    for block in f.read_text().split('@')[1:]:
        lines=block.strip().splitlines()
        n=int(lines[0].split('|')[0])
        rows=[r.split('|') for r in lines[1:]]
        for i,r in enumerate(rows):
            original=r[0]
            r[0]=wrap_english(r[0])
            if i==len(rows)-2:
                r[0]=move_practice_to_end(r[0])
            changed+=r[0]!=original
        blocks.append('@'+lines[0]+'\n'+'\n'.join('|'.join(r) for r in rows)+'\n')
    f.write_text(''.join(blocks))
print('Polished',changed,'narration rows before creating anchors; no revision edited')
