"""Authenticated server assignments only; no OAuth, sync, allocation or secret output."""
import hashlib
import json
from pathlib import Path
import sys
import time


def classify(error):
    status=getattr(getattr(error,'response',None),'status_code',None)
    text=str(error).lower()
    if status==401 or any(term in text for term in ('invalid_grant','unauthenticated','token expired','token revoked')):return 'login_required'
    if status==429 or 'quota' in text or 'resource_exhausted' in text:return 'quota'
    if status==503:return 'capacity'
    if status==403:return 'permission_unknown'
    return 'network_unknown'


def probe(profile, session_name):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import AuthorizedSession
    from colab_cli.common import Client, Prod
    profile=Path(profile)
    try:
        credentials=Credentials.from_authorized_user_file(str(profile/'token.json'))
        if not credentials.valid:
            return {'verified':False,'reason':'refresh_required' if getattr(credentials,'refresh_token',None) else 'login_required','source':'credential_check_no_oauth'}
        session=AuthorizedSession(credentials,max_refresh_attempts=0)
        response=session.get('https://openidconnect.googleapis.com/v1/userinfo',timeout=15,allow_redirects=False)
        if response.status_code!=200:
            return {'verified':False,'reason':{401:'login_required',403:'permission_unknown',429:'quota',503:'capacity'}.get(response.status_code,'network_unknown'),'source':'google_userinfo'}
        claims=response.json()
        if claims.get('email') and claims.get('email_verified') is True:
            identity='google:'+hashlib.sha256(claims['email'].strip().lower().encode()).hexdigest()
        elif isinstance(claims.get('sub'),str):identity='google-sub:'+hashlib.sha256(claims['sub'].encode()).hexdigest()
        else:return {'verified':False,'reason':'identity_unknown','source':'google_userinfo'}
        assignments=list(Client(Prod(),session).list_assignments())
        local={}
        if (profile/'sessions.json').is_file():
            try:local=json.loads((profile/'sessions.json').read_text())
            except (OSError,ValueError):pass
        named=local.get(session_name) if isinstance(local,dict) else None
        endpoint=named.get('endpoint') if isinstance(named,dict) else None
        return {'verified':True,'identity':identity,'assignment_count':len(assignments),
                'local_session_present':bool(endpoint),'named_assignment_active':bool(endpoint and any(item.endpoint==endpoint for item in assignments)),
                'source':'google_userinfo_and_official_list_assignments','checked_at':time.time()}
    except Exception as error:
        return {'verified':False,'reason':classify(error),'error_type':type(error).__name__,'source':'official_assignment_probe'}


if __name__=='__main__':
    try:result=probe(Path(sys.argv[1]),sys.argv[2])
    except Exception as error:result={'verified':False,'reason':'helper_unavailable','error_type':type(error).__name__}
    print(json.dumps(result))
