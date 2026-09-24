"""Topic-independent story contracts, image prompts and narration-bound visual beats."""
import copy
import json
import re


def normalize_brief(brief):
    if brief.get('schema_version') not in ('2.0','3.0'):
        raise ValueError('Unsupported brief schema version')
    b = copy.deepcopy(brief)
    b['schema_version'] = '3.0'
    b.setdefault('planning', {
        'success_criteria': [b['goal']], 'avoid': [],
        'prior_knowledge': 'Chưa xác định; không giả định kiến thức chuyên môn.',
        'pacing': 'Theo lời dẫn tự nhiên; đủ thời gian quan sát hình và đọc chữ.',
        'domain_requirements': [],
        'assumptions': ['Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.',
                        'Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.'],
        'text_style': {'font': 'sans-serif rõ nét, cùng kiểu và độ đậm xuyên suốt',
                       'color': '#172033', 'outline': 'nền sáng tương phản',
                       'size': 'dễ đọc trên điện thoại',
                       'placement': 'cách mép ít nhất 10%; tránh mặt và vùng phụ đề dưới cùng 18%'},
        'speech_rates': {lang: {'units_per_second': rate, 'uncertainty': .25,
                              'includes_pauses': False, 'source': 'initial estimate; replace with measured voice rate'}
                         for lang, rate in [('vi', 3.6), ('en', 2.5)]}})
    return b


def occurrence(text, anchor):
    start = 0
    for _ in range(anchor['occurrence']):
        pos = text.find(anchor['quote'], start)
        if pos < 0:
            raise ValueError('Anchor quote/occurrence not in narration')
        start = pos + len(anchor['quote'])
    return pos


def validate_plan(b, c):
    from content_contract import ContractError, error
    errors = []
    def fail(code, path, message):
        errors.append(error(code, path, message, 'Sửa bản nháp; không sửa revision đã lưu.'))
    scenes = c['scenes']; ids = [s['id'] for s in scenes]
    if [x['scene_id'] for x in c['outline']] != ids:
        fail('OUTLINE', 'outline', 'Dàn ý không khớp thứ tự cảnh')
    all_images = set(); all_beats = set()
    internal = ids + [x['id'] for x in c['characters']]
    internal += [im['id'] for s in scenes for im in s['images']]
    internal += [bt['id'] for s in scenes for bt in s['beats']]
    global_visible = c['style']+' '+json.dumps(b['planning']['text_style'],ensure_ascii=False)+' '+' '.join(x['appearance']+' '+x['outfit']+' '+x['name'] for x in c['characters'])
    if any(re.search(r'(?<!\w)'+re.escape(code)+r'(?!\w)', global_visible, re.I) for code in internal):
        fail('INTERNAL_LABEL','characters/style','Mã quản lý xuất hiện trong mô tả dùng tạo hình')
    for s, outline in zip(scenes, c['outline']):
        if outline['purpose'] != s['purpose'] or outline['requirements'] != s['requirements']:
            fail('OUTLINE', s['id'], 'Mục đích hoặc ý của cảnh khác dàn ý')
        seen = set()
        for im in s['images']:
            if im['id'] in all_images: fail('IMAGE_ID', s['id'], 'Mã ảnh trùng')
            all_images.add(im['id'])
            if im['based_on'] is not None and im['based_on'] not in seen:
                fail('IMAGE_BASE', im['id'], 'Ảnh nền phải là ảnh trước đó trong cùng cảnh')
            if im['based_on'] and not im['preserve'].strip():
                fail('IMAGE_BASE', im['id'], 'Thiếu nội dung cần giữ nguyên')
            if not set(im['character_ids']) <= set(s['character_ids']):
                fail('CHARACTER_REF', im['id'], 'Nhân vật ảnh không thuộc cảnh')
            visible = ' '.join(im[k] for k in ['description','preserve','change'])
            visible += ' ' + ' '.join(x['text']+' '+x['placement']+' '+x['object'] for x in im['visible_text'])
            if any(re.search(r'(?<!\w)'+re.escape(code)+r'(?!\w)', visible, re.I) for code in internal):
                fail('INTERNAL_LABEL', im['id'], 'Mã nội bộ không được đưa vào mô tả hình/chữ')
            seen.add(im['id'])
        used = {x['image_id'] for x in s['beats']}
        if used != seen: fail('IMAGE_USAGE', s['id'], 'Mỗi ảnh phải được sử dụng, không tham chiếu ảnh ngoài cảnh')
        for lang in ['vi'] + (['en'] if b['aspect_ratio'] in ('dual','16:9') else []):
            text = s.get('narration_en' if lang == 'en' else 'narration', '')
            positions = []
            for beat in s['beats']:
                try: positions.append(occurrence(text, beat['anchor'][lang]))
                except (ValueError, KeyError): fail('ANCHOR', beat['id'], 'Thiếu/sai điểm neo '+lang)
            if positions and (positions[0] != 0 or any(a >= z for a,z in zip(positions,positions[1:]))):
                fail('ANCHOR_ORDER', s['id'], 'Nhịp đầu bắt đầu lời dẫn; các nhịp sau tăng dần theo từng ngôn ngữ')
        for beat in s['beats']:
            if beat['id'] in all_beats: fail('BEAT_ID', s['id'], 'Mã nhịp trùng')
            all_beats.add(beat['id'])
    source = {x['id']: x for x in b['sources']}
    scene_by_id = {x['id']: x for x in scenes}
    for claim in c['claims']:
        sc = scene_by_id.get(claim['scene_id'], {})
        text = sc.get('narration_en' if claim['language']=='en' else 'narration','')
        src = source.get(claim['source_id'], {})
        if claim['quote'] not in text or claim['fact'] not in src.get('facts',[]) or claim['source_id'] not in sc.get('source_ids',[]):
            fail('CLAIM_SOURCE','claims','Phát biểu/nguồn/dữ kiện không khớp; đúng nghĩa vẫn cần đánh giá')
    if b['facts_required'] and not c['claims']:
        fail('CLAIM_SOURCE','claims','Nội dung yêu cầu dữ kiện phải có liên kết phát biểu và nguồn')
    valid_scenes=set(ids)
    for response in c['revision_response']:
        if not set(response['scene_ids'])<=valid_scenes: fail('REVISION_RESPONSE','revision_response','Phản hồi trỏ tới cảnh không tồn tại')
    if errors: raise ContractError(errors)


def image_units(c):
    if c.get('schema_version') != '3.0': return c['scenes']
    chars = {x['id']: x for x in c['characters']}
    units = []
    for scene in c['scenes']:
        for im in scene['images']:
            # Never serialize IDs or metadata into visible prompt prose.
            people = [chars[x]['appearance'] + '; trang phục: ' + chars[x]['outfit'] for x in im['character_ids']]
            prompt = '\n'.join([c['style'], im['description'], 'Nhân vật: '+'; '.join(people),
                                'Giữ nguyên: '+im['preserve'], 'Thay đổi: '+im['change']])
            units.append({'id': im['id'], 'scene_id': scene['id'], 'prompt': prompt,
                          'character_ids': im['character_ids'], 'based_on': im['based_on'],
                          'visible_text': im['visible_text']})
    return units


def text_prompt(prompt, allowed, style):
    policy = ('Chỉ được vẽ đúng các chữ trong danh sách này: '+json.dumps(allowed, ensure_ascii=False)
              if allowed else 'Không có bất kỳ chữ hoặc số nào trong hình.')
    return prompt + '\n' + policy + '\nKhông thêm nhãn, mã quản lý, logo, watermark, tiêu đề hay chữ trang trí ngoài danh sách.\nPhong cách chữ chung: '+json.dumps(style,ensure_ascii=False)


def estimates(b, c):
    result = {'languages': {}, 'warnings': [], 'status': 'estimated_not_measured'}
    for lang in ['vi'] + (['en'] if b['aspect_ratio'] in ('dual','16:9') else []):
        rate = b['planning']['speech_rates'][lang]; rows = []
        for sc in c['scenes']:
            text = sc['narration_en' if lang=='en' else 'narration']
            units = len(text.split())
            seconds = units/rate['units_per_second'] + (0 if rate.get('includes_pauses') else len(re.findall(r'[.!?;,]',text))*.15 + .3)
            learner_pause = sc.get('audio_direction', {}).get(lang, {}).get('learner_pause_seconds', 0)
            seconds += learner_pause
            rows.append({'scene_id':sc['id'], 'units':units, 'seconds':round(seconds,2),
                         'min':round(seconds*(1-rate['uncertainty']),2), 'max':round(seconds*(1+rate['uncertainty']),2)})
            if seconds/len(sc['beats']) < 1.5:
                result['warnings'].append(sc['id']+': nhịp hình có thể quá nhanh ('+lang+')')
        lo=sum(x['min'] for x in rows);hi=sum(x['max'] for x in rows)
        result['languages'][lang]={'scenes':rows,'min':round(lo,2),'max':round(hi,2),'rate':rate}
        if lo>b['duration']['max_seconds'] or hi<b['duration']['min_seconds']:
            result['warnings'].append(lang+': khoảng ước tính không giao với thời lượng yêu cầu')
    return result


def feedback(p, job):
    rows = p.db.execute("SELECT id,detail FROM events WHERE job=? AND module='content' AND event='rejected' ORDER BY id", (job,)).fetchall()
    return [{'request_id':str(row['id']), 'note':row['detail']} for row in rows]


def check_revision(p, job, payload):
    if payload.get('schema_version') != '3.0': return
    from pilot import Blocked, read
    requests = feedback(p,job)
    responses = payload['revision_response']
    if {x['request_id'] for x in responses} != {x['request_id'] for x in requests} or len(responses)!=len(requests):
        raise Blocked('REVISION_RESPONSE: phải xử lý đúng phản hồi hiện tại')
    if requests:
        old = p.rows(job)['content']['envelope']
        if old:
            previous = read(p.path(job,old))['payload']
            if all(previous.get(k)==v for k,v in payload.items() if k not in ('revision_response','open_questions')):
                raise Blocked('UNCHANGED_DRAFT: có yêu cầu sửa nhưng nội dung chưa thay đổi')


def review_plan(b, c, previous=None, requests=()):
    timing=estimates(b,c); plan=b['planning']
    def bullets(values): return '\n'.join('- '+str(x) for x in values) or 'Không có.'
    lines=['## Mục tiêu và người xem', b['goal'], 'Người xem: '+b['audience'],
           'Kiến thức đầu vào: '+plan['prior_knowledge'], 'Tiêu chí đạt:\n'+bullets(plan['success_criteria']),
           'Cần tránh:\n'+bullets(plan['avoid']), 'Yêu cầu chuyên biệt:\n'+bullets(plan['domain_requirements']),
           'Nhịp kể: '+plan['pacing'], 'Giả định cần kiểm tra:\n'+bullets(plan['assumptions']),
           f"{len(c['scenes'])} cảnh · {sum(len(s['images']) for s in c['scenes'])} hình logic · {sum(len(s['beats']) for s in c['scenes'])} nhịp",
           'Dual tạo hai bộ hình riêng cho hai tỷ lệ.' if b['aspect_ratio']=='dual' else 'Tỷ lệ: '+b['aspect_ratio'],
           '## Thời lượng dự kiến (chưa phải WAV)']
    for lang, data in timing['languages'].items():
        lines.append(f"{lang.upper()}: {data['min']}–{data['max']} giây. Cơ sở: {data['rate']['source']}")
        lines.append('| Cảnh | Khoảng giây dự kiến |\n|---|---|\n'+'\n'.join(f"| {r['scene_id']} | {r['min']}–{r['max']} |" for r in data['scenes']))
    lines.append('Cảnh báo thời lượng/nhịp:\n'+bullets(timing['warnings']))
    style=plan['text_style']
    lines += ['## Chữ tạo cùng hình', f"Kiểu: {style['font']}. Màu: {style['color']}. Viền/nền: {style['outline']}. Cỡ: {style['size']}. Vị trí: {style['placement']}.",
              'Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.']
    for scene in c['scenes']:
        lines += ['## '+scene['id']+' — '+scene['title'], 'Mục đích: '+scene['purpose'], scene['narration']]
        if scene.get('narration_en'): lines.append('EN: '+scene['narration_en'])
        for lang, direction in scene.get('audio_direction', {}).items():
            lines.append(f"Chỉ đạo âm thanh {lang}: {direction['intent']} · Lưu ý phát âm: {direction['pronunciation_notes'] or 'Không có'} · Khoảng chờ học viên cuối cảnh: {direction['learner_pause_seconds']} giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.")
        for im in scene['images']:
            words='; '.join('“'+x['text']+'” — '+x['placement']+'; đối tượng: '+x['object'] for x in im['visible_text']) or 'Không có chữ/số'
            lines.append('**Hình '+im['id']+'** — '+im['description']+'\n\nẢnh gốc: '+str(im['based_on'] or 'Tạo mới')+'; giữ: '+(im['preserve'] or 'Không áp dụng')+'; đổi: '+im['change']+'\n\nLý do: '+im['reason']+'\n\nChữ được phép: '+words)
        for beat in scene['beats']:
            anchors='; '.join(lang+': “'+a['quote']+'” (lần '+str(a['occurrence'])+')' for lang,a in beat['anchor'].items())
            lines.append('Nhịp '+beat['id']+' → '+beat['image_id']+' · '+beat['effect']+' · '+anchors+' · '+beat['purpose'])
    lines += ['## Nhân vật', bullets(x['name']+': '+x['appearance']+'; '+x['outfit'] for x in c['characters'])]
    if any(x.get('quote_en') for x in c['coverage']):
        lines += ['## Đối chiếu ý bắt buộc (Việt / Anh)',
                  '| Ý | Cảnh | Lời dẫn Việt | Lời dẫn Anh |\n|---|---|---|---|\n' +
                  '\n'.join(f"| {x['requirement_id']} | {x['scene_id']} | {x['quote']} | {x.get('quote_en','—')} |" for x in c['coverage'])]
    else:
        lines += ['## Đối chiếu ý bắt buộc', bullets(x['requirement_id']+' → '+x['scene_id']+': '+x['quote'] for x in c['coverage'])]
    lines += ['## Phát biểu và nguồn', bullets(x['scene_id']+': “'+x['quote']+'” → '+x['source_id']+': '+x['fact'] for x in c['claims']),
              '## Nguồn', bullets(x['id']+' — '+x['title']+'; '+x['reference'] for x in b['sources']),
              '## Phản hồi cần xử lý', bullets(x['request_id']+': '+x['note'] for x in requests),
              '## Kết quả sửa', bullets(x['request_id']+' — '+x['status']+': '+x['explanation']+'; cảnh: '+', '.join(x['scene_ids']) for x in c['revision_response']),
              '## Vấn đề còn lại', bullets(c['open_questions'])]
    if previous:
        changed=[s['id'] for s in c['scenes'] if s not in previous.get('scenes',[])]
        lines += ['## Thay đổi so với bản trước', 'Cảnh thay đổi: '+', '.join(changed),
                  'Trường thay đổi: '+', '.join(k for k in c if c[k]!=previous.get(k))]
    return '\n\n'.join(lines)


def timeline(c, images, audio, language, ratio):
    """Anchor interpolation is explicit, not a claim of forced word alignment."""
    by_id={(im.get('image_id',im['scene_id']),im.get('ratio',ratio)):im for im in images['items']}
    output=[]
    for sc in c['scenes']:
        spans = [x for x in (audio['en']['scenes'] if language=='en' else audio['segments']) if x['scene_id']==sc['id']]
        start=spans[0]['start'];end=spans[-1]['end']
        if c.get('schema_version')!='3.0':
            im=by_id[(sc['id'],ratio)];output.append({'id':sc['id'],'title':sc['title'],'image':im['path'],'start':start,'end':end});continue
        text=sc['narration_en' if language=='en' else 'narration'];beats=[]
        for bt in sc['beats']:
            offset=occurrence(text,bt['anchor'][language])
            # Use actual chunk bounds when available; interpolate within the chunk.
            at=start+offset/max(1,len(text))*(spans[-1].get('content_end',end)-start)
            if language=='vi':
                cursor=0
                for seg in spans:
                    pos=text.find(seg['text'],cursor)
                    if pos<0: continue
                    if pos<=offset<pos+len(seg['text']):
                        at=seg['start']+(offset-pos)/max(1,len(seg['text']))*(seg.get('content_end',seg['end'])-seg['start']);break
                    cursor=pos+len(seg['text'])
            im=by_id[(bt['image_id'],ratio)]
            beats.append({'id':bt['id'],'src':im['path'],'at':round(at-start,4),'effect':bt['effect'],'focus':bt['focus']})
        beats[0]['at']=0
        if any(round(a['at']*30)>=round(z['at']*30) for a,z in zip(beats,beats[1:])):
            raise ValueError('Visual beats collide at 30 fps; revise content anchors')
        output.append({'id':sc['id'],'title':sc['title'],'start':start,'end':end,'image':beats[0]['src'],'images':beats,
                       'timing_method':'narration_anchor_interpolated; verify against audio at media review'})
    return output


def calibrate_rates(c, audio, source):
    """Measured narration units per WAV second, including the actual voice pauses."""
    rates = {}
    for lang, duration in [('vi',audio['duration'])] + ([('en',audio['en']['duration'])] if audio.get('en') else []):
        units = sum(len(sc['narration_en' if lang=='en' else 'narration'].split()) for sc in c['scenes'])
        rates[lang] = {'units_per_second':round(units/duration,4), 'uncertainty':.2,
                       'includes_pauses':True, 'source':source+'; measured WAV including pauses'}
    return rates


def safe_corrections(c, note):
    """Keep verbatim feedback in journals; translate management IDs only for the model prompt."""
    if c.get('schema_version') != '3.0': return note
    replacements={x['id']:x['name'] for x in c['characters']}
    for sc in c['scenes']:
        replacements[sc['id']]='cảnh đang được sửa'
        replacements.update({x['id']:'the specified image' for x in sc['images']})
        replacements.update({x['id']:'nhịp đang được sửa' for x in sc['beats']})
    pattern=r'(?<!\w)('+ '|'.join(re.escape(k) for k in sorted(replacements,key=len,reverse=True))+r')(?!\w)'
    return re.sub(pattern,lambda m:replacements[m.group()],note) if replacements else note
