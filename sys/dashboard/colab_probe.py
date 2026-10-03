"""Private read-only auth probe, executed with the installed official CLI runtime.

Never refresh credentials, launch OAuth, allocate GPU, sync local sessions, or
print credentials/provider bodies. Userinfo endpoint documented by Google:
https://developers.google.com/identity/openid-connect/reference
"""
import hashlib
import json
from pathlib import Path
import sys


def classify(error):
    status = getattr(getattr(error, 'response', None), 'status_code', None)
    message = str(error).lower()
    if status == 401 or any(x in message for x in ('invalid_grant', 'unauthenticated', 'token expired', 'token revoked')):
        return 'login_required'
    if status == 429 or 'quota' in message or 'resource_exhausted' in message:
        return 'quota'
    if status == 503 or 'capacity' in message or 'unavailable' in message:
        return 'capacity'
    if status == 403:
        return 'permission_unknown'
    return 'network_unknown'


def probe(token_path):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import AuthorizedSession
    from colab_cli.common import Client, Prod
    try:
        credentials = Credentials.from_authorized_user_file(str(token_path))
        if not credentials.valid:
            # Expiry of the short-lived access token does not prove logout.
            # Inspection must not refresh or open OAuth on the user's behalf.
            refreshable = bool(getattr(credentials, 'refresh_token', None))
            return {'auth': 'unknown' if refreshable else 'login_required',
                    'capability': 'not_tested',
                    'reason': 'refresh_required' if refreshable else 'missing_valid_credentials',
                    'source': 'local_credential_expiry_no_refresh'}
        session = AuthorizedSession(credentials, max_refresh_attempts=0)
        response = session.get('https://openidconnect.googleapis.com/v1/userinfo', timeout=15, allow_redirects=False)
        if response.status_code == 401:
            return {'auth': 'login_required', 'capability': 'not_tested', 'source': 'google_userinfo_401'}
        if response.status_code != 200:
            reason = {403: 'permission_unknown', 429: 'quota', 503: 'capacity'}.get(response.status_code, 'network_unknown')
            return {'auth': 'unknown', 'capability': 'not_tested', 'source': 'google_userinfo', 'reason': reason}
        claims = response.json()
        if claims.get('email') and claims.get('email_verified') is True:
            email = claims['email'].strip().lower()
            identity = 'google:' + hashlib.sha256(email.encode()).hexdigest()
            identity_source = 'google_userinfo_verified_email'
            account_label = email
        elif isinstance(claims.get('sub'), str):
            identity = 'google-sub:' + hashlib.sha256(claims['sub'].encode()).hexdigest()
            identity_source = 'google_userinfo_subject'
            account_label = None
        else:
            return {'auth': 'unknown', 'capability': 'not_tested', 'source': 'google_userinfo_missing_identity'}
        # Official CLI's exact read-only service call; do not use sync_sessions,
        # which can prune/update local ownership and proxy credentials.
        try:
            assignments = list(Client(Prod(), session).list_assignments())
        except Exception as error:
            reason = classify(error)
            return {'auth': 'login_required' if reason == 'login_required' else 'verified',
                    'capability': reason, 'identity': identity, 'identity_source': identity_source,
                    'account_label': account_label,
                    'source': 'google_userinfo_and_colab_list_assignments'}
        return {'auth': 'verified', 'capability': 'service_access_verified',
                'gpu': 'not_tested', 'session_count': len(assignments), 'identity': identity,
                'account_label': account_label,
                'identity_source': identity_source, 'source': 'google_userinfo_and_colab_list_assignments'}
    except Exception as error:
        reason = classify(error)
        return {'auth': 'login_required' if reason == 'login_required' else 'unknown',
                'capability': 'not_tested', 'reason': reason, 'source': 'read_only_probe'}


if __name__ == '__main__':
    try:
        result = probe(Path(sys.argv[1]))
    except Exception:
        result = {'auth': 'unknown', 'capability': 'unsupported', 'source': 'installed_cli_runtime_unavailable'}
    print(json.dumps(result))
