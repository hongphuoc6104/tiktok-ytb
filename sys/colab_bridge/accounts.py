"""Local account profiles; isolated OAuth, sessions and history."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

STORE = Path.home() / '.config/video-pilot/colab'


def folder(name):
    if not re.fullmatch('[a-z0-9][a-z0-9_-]{0,47}', name):
        raise ValueError('Invalid account ID')
    return STORE / 'profiles' / name


def registry():
    path = STORE / 'accounts.json'
    return json.loads(path.read_text()) if path.exists() else {'preferred': None, 'accounts': []}


def save(data):
    STORE.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(STORE, 0o700)
    path = STORE / 'accounts.json'
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2)+'\n');os.chmod(tmp,0o600);tmp.replace(path)


def add(name, source=None):
    data = registry();dest = folder(name)
    if dest.exists():raise ValueError('Account already exists; refusing to overwrite')
    if source and not (source/'token.json').is_file():raise ValueError('No logged-in account')
    dest.mkdir(parents=True,mode=0o700)
    if source:
        for filename in ['token.json','sessions.json']:
            src=source/filename
            if src.is_file():
                shutil.copyfile(src,dest/filename);os.chmod(dest/filename,0o600)
    data['accounts'].append({'id':name,'enabled':True})
    if data['preferred'] is None:data['preferred']=name
    save(data)


def select(name='auto'):
    data=registry();entries=data['accounts']
    if name!='auto':entries=[x for x in entries if x['id']==name]
    else:entries=sorted(entries,key=lambda x:x['id']!=data['preferred'])
    for item in entries:
        if item['enabled'] and (folder(item['id'])/'token.json').is_file():return item['id']
    raise ValueError('COLAB_LOGIN_REQUIRED: no authenticated account profile')


def command(binary,name,args):
    first=Path(binary).read_text().splitlines()[0]
    if not first.startswith('#!/') or ' ' in first[2:]:raise ValueError('Unsupported colab launcher')
    return [first[2:],str(Path(__file__).with_name('account_cli.py')),str(folder(name)),*args]


def assignment_state(binary, name, session, timeout=45):
    """Read-only exact-account server probe using the installed official runtime."""
    argv=command(binary,name,())
    helper=Path(__file__).with_name('assignment_probe.py')
    try:
        result=subprocess.run([argv[0],str(helper),str(folder(name)),session],capture_output=True,text=True,timeout=timeout)
        if result.returncode:return {'verified':False,'reason':'helper_failed','error_type':'ProcessExit'}
        data=json.loads(result.stdout)
        if not isinstance(data,dict):raise ValueError('Invalid observation')
        return data
    except subprocess.TimeoutExpired:return {'verified':False,'reason':'network_unknown','error_type':'TimeoutExpired'}
    except (OSError,ValueError):return {'verified':False,'reason':'helper_unavailable','error_type':'InvalidObservation'}


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['list','import-current','login','prefer','run','login-many']);p.add_argument('account',nargs='?',default='auto');p.add_argument('args',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.action=='login-many':
        binary=shutil.which('colab') or str(Path.home()/'.local/bin/colab')
        while True:
            d=registry();used={x['id'] for x in d['accounts']};n=1
            while f'account-{n:02d}' in used:n+=1
            name=f'account-{n:02d}';add(name)
            print(f'\nĐăng nhập {name}: mở liên kết Google, chọn tài khoản khác, dán mã vào terminal này.',flush=True)
            result=subprocess.run(command(binary,name,['sessions']))
            if result.returncode or not (folder(name)/'token.json').is_file():
                print('Đăng nhập chưa hoàn tất. Dừng để giữ nguyên trạng thái.');return
            print(f'Đã lưu {name}.',flush=True)
            if input('Thêm tài khoản nữa? [y/N]: ').strip().lower() not in ('y','yes','c','có'):return
    if a.action=='list':
        d=registry()
        print(json.dumps({'store':str(STORE),'preferred':d['preferred'],'accounts':[dict(x,authenticated=(folder(x['id'])/'token.json').is_file()) for x in d['accounts']]},indent=2));return
    if a.action=='import-current':add(a.account,Path.home()/'.config/colab-cli');print(a.account);return
    if a.action=='prefer':
        name=select(a.account);d=registry();d['preferred']=name;save(d);print(name);return
    if a.action=='login':
        if a.account=='auto':p.error('Specify account ID')
        if not folder(a.account).exists():add(a.account)
        name=a.account;args=['sessions']
    else:
        name=select(a.account);args=a.args
        if args[:1]==['--']:args=args[1:]
        if not args:p.error('Specify a Colab command')
    binary=shutil.which('colab') or str(Path.home()/'.local/bin/colab')
    raise SystemExit(subprocess.run(command(binary,name,args)).returncode)


if __name__=='__main__':
    try:main()
    except ValueError as ex:print(str(ex),file=sys.stderr);raise SystemExit(2)
