"""Read-only audit of generated experiment evidence; emits a separate technical report."""
from collections import defaultdict
from pathlib import Path
import math
import soundfile as sf

from lab import DATA, STAGES, read, file_hash, verify_frozen, write, now, meets_threshold


def audit():
    verify_frozen()
    corpus = {x['id']: x for x in read(DATA/'corpus.json')}
    results, errors, sources, holdout_generated = [], [], defaultdict(set), []
    for stage in STAGES:
        folder = DATA/'rounds'/stage
        if not (folder/'plan.json').exists():
            continue
        plan = read(folder/'plan.json')
        for clip in plan['clips']:
            result_file = folder/'clips'/f"{clip['clip_id']}.json"
            if not result_file.exists():
                continue
            result = read(result_file)
            wav = folder/'audio'/f"{clip['clip_id']}.wav"
            if file_hash(wav) != result['wav_sha256']:
                errors.append(f'{stage}/{clip["clip_id"]}: WAV đổi nội dung')
            meta = sf.info(wav)
            if meta.frames != result['technical']['samples'] or meta.samplerate != 48000:
                errors.append(f'{stage}/{clip["clip_id"]}: metadata WAV không khớp')
            source = DATA/'cache'/result['source_key']
            source_meta = read(source/'source.json')
            if file_hash(source/'raw.wav') != source_meta['sha256']:
                errors.append(f'{stage}/{clip["clip_id"]}: nguồn đổi nội dung')
            if source_meta['sha256'] != result['source_sha256']:
                errors.append(f'{stage}/{clip["clip_id"]}: tham chiếu nguồn sai')
            technical = result['technical']
            if not technical['valid'] or abs(technical['lufs'] + 23) > .5:
                errors.append(f'{stage}/{clip["clip_id"]}: kiểm tra kỹ thuật chưa đạt')
            sources[(stage, clip['sample_id'], clip['take'])].add(result['source_key'])
            if corpus[clip['sample_id']]['partition'] == 'holdout':
                holdout_generated.append(dict(stage=stage, sample=clip['sample_id']))
                if stage != 'final': errors.append('Bộ giữ lại bị dùng trước vòng cuối')
            results.append(dict(stage=stage, sample=clip['sample_id'], **technical))
    for (stage, sid, take), keys in sources.items():
        if stage in ('C-speed', 'E') and len(keys) != 1:
            errors.append(f'{stage}/{sid}: các biến thể không dùng chung nguồn')
    summary = dict(created=now(), technical_pass=not errors, errors=errors, clips=len(results),
                   holdout_generated=holdout_generated, protected_files_unchanged=True,
                   listening_status='not_evaluated_by_agent',
                   loudness_range=[min(r['lufs'] for r in results), max(r['lufs'] for r in results)] if results else [],
                   total_listening_seconds=sum(r['seconds'] for r in results))
    write(DATA/'technical-audit.json', summary)
    lines = ['# Kiểm tra kỹ thuật bộ thử Minh Quân Pro', '',
             f'- WAV đã kiểm tra: {len(results)}.',
             f'- File đối chứng/sản xuất giữ nguyên: có.',
             f'- Lỗi kỹ thuật: {len(errors)}.',
             f'- Mẫu giữ lại đã tạo: {len(holdout_generated)}.',
             '- Chất lượng nghe do agent đánh giá: unsupported; không suy từ kết quả này.', '',
             '| Vòng | WAV | Tổng thời lượng nghe | LUFS nhỏ nhất / lớn nhất |', '|---|---:|---:|---:|']
    for stage in STAGES:
        rs = [r for r in results if r['stage'] == stage]
        if rs:
            lines.append(f'| {stage} | {len(rs)} | {sum(r["seconds"] for r in rs):.1f} s | {min(r["lufs"] for r in rs):.1f} / {max(r["lufs"] for r in rs):.1f} |')
    if errors: lines += ['', '## Lỗi'] + ['- '+e for e in errors]
    final_review = DATA/'reviews/final.json'
    if final_review.exists():
        ratings = read(final_review)['ratings']
        stable = read(DATA/'decisions/D.json')['meets_threshold']
        by_id = {c['clip_id']: c for c in read(DATA/'rounds/final/plan.json')['clips']}
        passed = sum(meets_threshold([r]) for r in ratings)
        verdict = 'Đạt' if stable and meets_threshold(ratings) else ('Đạt có giới hạn' if passed else 'Không đạt')
        lines += ['', '## Kết luận từ phiếu nghe thật', f'**{verdict}.** Không tự đưa vào sản xuất.', '',
                  '| Mẫu | Phạm vi đạt trên phiếu | Lỗi / thời điểm |', '|---|---|---|']
        for rating in ratings:
            details = '; '.join(f'{e["seconds"]} s: {e["description"]}' for e in rating['errors']).replace('|','/').replace('\n',' ')
            lines.append(f'| {by_id[rating["clip_id"]]["sample_id"]} | {"Đạt" if meets_threshold([rating]) else "Chưa đạt"} | {details or "Không ghi lỗi cụ thể"} |')
        if not stable: lines += ['', 'Chưa đạt kiểm tra ổn định qua ba lần tạo ở vòng D.']
    else:
        lines += ['', '**Chưa có kết luận chất lượng: còn thiếu đánh giá nghe và các vòng phụ thuộc.**']
    (DATA/'technical-audit.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(summary)
    return not errors


if __name__ == '__main__':
    raise SystemExit(0 if audit() else 1)
