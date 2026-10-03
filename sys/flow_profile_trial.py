"""Bounded, explicitly authorized setup-image trial, separate from vocabulary.

Inventory/prepare have no browser/provider calls. The coordinating controller
owns browser start/connect/close and explicitly hands the serial lease to submit.
Each source profile receives at most one sent image. Unknown outcomes are kept
for collection, and a provider service stop pauses the entire trial pool.
"""
import hashlib
import json
from pathlib import Path
import re
import time

from account_catalog import discover
from account_budget import Budgets, HARD_STOPS
from profile_setup import inventory, _url, processes, endpoint_status
from permissions import Grants, PermissionDenied
from session_store import Sessions, locked_json
from flow_prompts import create_pin, compile_pinned, validate_pin


DESCRIPTION = ('A simple explanatory diagram on a bright white background: two red apples rest on the left; '
               'one clear curved arrow points from one apple toward an empty woven basket on the right. '
               'The small canonical mascot gestures toward the arrow, showing that one apple moves into the basket. '
               'Use bold dark outlines, flat colors and generous clear space. No lettering.')


class TrialBlocked(RuntimeError):
    pass


def metadata_plan(root, *, home=None):
    """Authoritative metadata inventory; correlations never imply Flow auth."""
    root = Path(root).resolve()
    accounts = discover(home=home, system_root=root)['accounts']
    profiles = inventory(root, home)
    ordinary = [x for x in profiles if x['browser'] == 'Chrome']
    rows = []
    for item in ordinary:
        candidates = [x for x in profiles if item['id'] in x['source_account_candidates']]
        correlated = [x for x in accounts if x['service'] == 'colab' and x.get('auth',{}).get('state') == 'verified'
                      and item['id'] in [p['id'] for p in x.get('matching_browser_profiles',[])]]
        rows.append({'source_account':item['id'], 'source_profile':item['profile'], 'source_root':item['metadata_root'],
            'managed_candidates':[{'runtime_account':x['id'], 'root':x['metadata_root'], 'profile':x['profile'],
                                   'auth_observation':x['auth'], 'capability_observation':x['capability']} for x in candidates],
            'verified_colab_correlations':[{'account':x['id'],'identity_hash':x.get('identity'),
                                            'source':'Chrome Local State user_name matched verified Colab identity; not Flow auth'} for x in correlated],
            'fresh_login_required':not candidates, 'candidate_selection_required':bool(candidates),
            'flow_auth':'not_tested_for_this_trial', 'target_state':'exact_own_project_tool_and_reference_attachment_required',
            'maximum_images':1, 'submission_state':'not_submitted'})
    config_path=root/'experiments/b2_illustrator/machine.local.json'
    current=json.loads(config_path.read_text()) if config_path.is_file() else {}
    return {'version':1,'generated_at':time.time(),'metadata_only':True,'provider_called':False,
        'source_request':'User requested one Flow test image for every existing profile.',
        'purpose':'setup sample, not a finished vocabulary video or bank reservation',
        'serial':True,'maximum_browser_windows':1,'profiles':rows,
        'retained_other_browsers':[{'id':x['id'],'browser':x['browser'],'profile':x['profile'],
                                  'provider_supported':x['provider_supported'],'state':x['setup_state']}
                                 for x in profiles if x['browser'] not in ('Chrome','Chrome managed')],
        'current_configured_target':{'runtime_account':current.get('runtime_account'),'root':current.get('flow_user_data_dir'),
                                    'profile':current.get('flow_profile_directory'),'tool_url':current.get('tool_url'),
                                    'target_reusable_across_accounts':False},
        'constraints':['No cookies/token/profile copying.', 'Metadata correlation is not authentication.',
            'Verify each exact profile and its own accessible project/tool before generation.',
            'Verify/upload canonical reference in the current account; old media UUID is not portable proof.',
            'Quota/CAPTCHA/bot/auth/service block pauses the pool, never switches account to bypass it.',
            'Unknown submitted request is collected/reconciled before any next profile.',
            'Close only the owned test browser and verify closure before starting the next profile.'],
        'prompt_version':'1.0.0','description':DESCRIPTION}


def write_plan(root, *, home=None):
    result=metadata_plan(root,home=home)
    target=Path(root)/'reports/normalization/flow-profile-test-plan.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return target


def _authority(root, grant, source):
    if not source or not source.strip():
        raise PermissionDenied('Actual one-image setup trial instruction required')
    entry=Grants(root).require(grant,'development','tests')
    project=Grants(root).project_root
    relative=(Path(root)/'experiments/b2_illustrator/results/profile-trials').resolve().relative_to(project).as_posix()
    if not any(__import__('fnmatch').fnmatchcase(relative,x) for x in entry['paths']):
        raise PermissionDenied('Setup image trial path is outside the development test grant')
    return entry


class Trials:
    def __init__(self,root,trial_id, *, budget_store=None, home=None):
        if not isinstance(trial_id,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',trial_id):
            raise ValueError('Exact trial ID required')
        self.root=Path(root).resolve();self.trial_id=trial_id;self.home=home
        self.path=self.root/'.state/flow-profile-trials'/f'{trial_id}.json'
        self.budget=Budgets(budget_store)

    def read(self):
        return json.loads(self.path.read_text()) if self.path.is_file() else {'version':1,'profiles':{},'active':None,'blocked':None}

    def prepare(self,source_account,runtime_account, *, tool_url,project,model,session,grant,source,
                reference_media_id,reference_evidence):
        _authority(self.root,grant,source);_url(tool_url)
        items={x['id']:x for x in inventory(self.root,self.home)}
        original=items.get(source_account);runtime=items.get(runtime_account)
        if not original or original['browser']!='Chrome' or not runtime or not runtime['provider_supported']:
            raise TrialBlocked('Exact supported source/runtime profiles required')
        if runtime['launch_requires_nondefault_root']:
            raise TrialBlocked('Use managed runtime after human login; never launch default Chrome root')
        if source_account not in runtime['source_account_candidates']:
            # Fresh roots have no CDP suffix mapping. Accept only the exact
            # official setup configuration tying this source to the managed
            # runtime; it remains metadata, never a Google auth assertion.
            setup_path=self.root/'experiments/b2_illustrator/machine.local.json'
            setup=json.loads(setup_path.read_text()) if setup_path.is_file() else {}
            if (setup.get('source_account')!=source_account or setup.get('runtime_account')!=runtime_account or
                Path(setup.get('flow_user_data_dir','')).resolve()!=Path(runtime['metadata_root']).resolve() or
                setup.get('flow_profile_directory')!=runtime['profile'] or not setup.get('setup_source') or not setup.get('grant')):
                raise TrialBlocked('Explicit source/managed metadata match or official fresh-root setup required')
        if not project or not session or not reference_media_id:
            raise ValueError('Exact project/session and current-account reference ID required')
        reference=self.root/'assets/characters/channel-mascot/reference-v1.png'
        sha=hashlib.sha256(reference.read_bytes()).hexdigest()
        runtime_path=str((Path(runtime['metadata_root'])/runtime['profile']).resolve())
        expected={'account':runtime_account,'profile_path':runtime_path,'media_id':reference_media_id,'sha256':sha}
        if not isinstance(reference_evidence,dict) or any(reference_evidence.get(k)!=v for k,v in expected.items()) or not reference_evidence.get('ui_verified_source'):
            raise TrialBlocked('Current account canonical reference attachment needs real UI evidence')
        pin=create_pin(model,'1.0.0')
        compiled=compile_pinned(pin,'scene',{'description':DESCRIPTION,'aspect_ratio':'9:16','allowed_text':[],
            'character_reference':{'sha256':sha,'media_id':reference_media_id},'mascot_placement':'above-caption-right',
            'caption_clearance':{'edge':'bottom','fraction':.18}})
        key='profiletest-'+hashlib.sha256((self.trial_id+source_account).encode()).hexdigest()[:24]
        record={'source_account':source_account,'runtime_account':runtime_account,'profile_path':runtime_path,
            'tool_url':tool_url,'project':project,'model':compiled['model'],'session':session,'grant':grant,'source':source,
            'reference_path':str(reference),'reference_sha256':sha,'reference_media_id':reference_media_id,
            'reference_evidence':reference_evidence,'prompt_pin':pin,'compiled_prompt':compiled,'request_id':key,'state':'prepared'}
        with locked_json(self.path,self.read) as state:
            if state.get('blocked'):raise TrialBlocked('Pool service block requires explicit reconciliation')
            old=state['profiles'].get(source_account)
            if old:
                comparable={k:old[k] for k in record}
                if comparable!=record:raise TrialBlocked('Existing trial contract is frozen; collect/reconcile it')
                return old
            state['profiles'][source_account]=record
        return record

    def submit(self,source_account, *, handoff_source, probe=None, status=None, generate=None):
        """One image at most; caller must explicitly own the browser serially."""
        if not isinstance(handoff_source,str) or not handoff_source.strip():
            raise TrialBlocked('Coordinator serial ownership handoff required')
        from account_catalog import probe_flow
        import b2_bridge
        record=self.read()['profiles'][source_account]
        _authority(self.root,record['grant'],record['source']);validate_pin(record['prompt_pin'])
        expected=compile_pinned(record['prompt_pin'],'scene',{'description':DESCRIPTION,'aspect_ratio':'9:16','allowed_text':[],
            'character_reference':{'sha256':record['reference_sha256'],'media_id':record['reference_media_id']},
            'mascot_placement':'above-caption-right','caption_clearance':{'edge':'bottom','fraction':.18}})
        if expected!=record['compiled_prompt'] or expected['model']!=record['model']:
            raise TrialBlocked('Frozen trial prompt changed; no implicit adoption')
        with locked_json(self.path,self.read) as state:
            if state.get('blocked'):raise TrialBlocked('Pool service block requires reconciliation, not account rotation')
            active=state.get('active')
            if active and active!=source_account:raise TrialBlocked('Previous profile browser/request is still owned')
            current=state['profiles'][source_account]
            if current['state']=='downloaded':return current['result']
            if current['state']!='prepared':raise TrialBlocked('Already attempted: collect/reconcile; do not submit again')
            current.update(state='checking',handoff_source=handoff_source,checked_at=time.time())
            state['active']=source_account
        provider_probe=probe or (lambda alias:probe_flow(alias,system_root=self.root,home=self.home,budget_store=self.budget.path.parent))
        connection_status=status or b2_bridge.query_status
        send=generate or b2_bridge.generate_b2_image
        charged=False
        try:
            authentication=provider_probe(record['runtime_account'])
            if authentication.get('auth')!='verified' or not authentication.get('identity'):
                raise TrialBlocked('Flow authentication is not verified; login/inspect this profile')
            # Shared identity mapping must come from actual auth observation.
            self.budget.bind_identity(record['runtime_account'],authentication['identity'],authentication.get('identity_source') or 'verified Flow account UI')
            def verify_connection(connection):
                identity=connection.get('identity') or {}
                if connection.get('status')!='connected' or identity.get('observedProfile')!=record['profile_path'] or identity.get('toolUrl')!=record['tool_url']:
                    raise TrialBlocked('Connected profile/tool differs from frozen trial owner')
                live=processes(Path(record['profile_path']).parent)
                if len(live)!=1:raise TrialBlocked('Exact browser root must have one verified owner')
            # Read-only preflight does not allocate a slot, pin a request or
            # mark submission. Recheck at the bridge's actual final boundary.
            verify_connection(connection_status())
            def boundary(connection):
                nonlocal charged
                if charged:
                    raise TrialBlocked('Trial send boundary already executed; never submit twice')
                verify_connection(connection)
                if hashlib.sha256(Path(record['reference_path']).read_bytes()).hexdigest()!=record['reference_sha256']:
                    raise TrialBlocked('Canonical reference changed after trial preparation')
                self.budget.flow_submit(record['runtime_account'],self.trial_id,record['request_id'],1,cap=100,
                                        budget_session=record['session'],evidence='serial setup trial send boundary')
                charged=True
                Sessions(self.root).pin(record['request_id'],job=self.trial_id,service='flow',account=record['runtime_account'],
                                        session=record['session'],identity=authentication['identity'])
                with locked_json(self.path,self.read) as state:
                    state['profiles'][source_account].update(state='submitted',submitted_at=time.time(),identity=authentication['identity'])
            result=send(record['compiled_prompt']['prompt'],ratio='9:16',char_ref_path=record['reference_path'],
                        char_media_id=record['reference_media_id'],out_dir=self.root/'experiments/b2_illustrator/results/profile-trials'/record['request_id'],
                        test_case=record['request_id'],model=record['model'],project=record['project'],tool_url=record['tool_url'],
                        before_submit=boundary)
            if not charged:raise TrialBlocked('Provider did not execute the guarded send boundary')
            path=Path(result['path']).resolve()
            allowed=(self.root/'experiments/b2_illustrator/results/profile-trials'/record['request_id']).resolve()
            if not path.is_relative_to(allowed) or not path.is_file() or path.is_symlink():raise TrialBlocked('Result path does not belong to trial')
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            if result.get('sha256')!=digest:raise TrialBlocked('Result hash differs from provider evidence')
            self.budget.flow_state(record['runtime_account'],self.trial_id,record['request_id'],'collected','verified result '+str(path))
            with locked_json(self.path,self.read) as state:
                state['profiles'][source_account].update(state='downloaded',result={**result,'setup_sample':True,'vocabulary_job':False},completed_at=time.time())
            return result
        except Exception as error:
            text=str(error).lower()
            kind=next((name for name,pattern in [('captcha',r'captcha'),('bot',r'bot.detect|unusual.activity'),('quota',r'quota|limit.exceeded'),
                ('429',r'\b429\b'),('503',r'\b503\b'),('auth',r'login|auth|sign.in')] if re.search(pattern,text)),None)
            submitted=charged and getattr(error,'generation_submitted',None) is not False
            outcome='unknown' if submitted else 'not_submitted'
            if charged:self.budget.flow_state(record['runtime_account'],self.trial_id,record['request_id'],outcome,'trial error: '+type(error).__name__)
            with locked_json(self.path,self.read) as state:
                state['profiles'][source_account].update(state=outcome,error=str(error),error_at=time.time())
                if kind in HARD_STOPS:state['blocked']={'account':record['runtime_account'],'kind':kind,'source_account':source_account,'at':time.time()}
            if kind and charged:
                try:self.budget.recover(record['runtime_account'],'flow',record['request_id'],action='reconcile',error=kind,submit_state=outcome,evidence='setup trial provider error')
                except ValueError:pass
            raise

    def release_profile(self,source_account, *, evidence):
        """Confirm actual close; never close shared browser or delete files."""
        if not evidence:raise ValueError('Actual browser-close observation required')
        record=self.read()['profiles'][source_account]
        root=Path(record['profile_path']).parent
        if record['state'] not in ('downloaded','not_submitted') or processes(root) or endpoint_status(root)['state'] not in ('missing','refused'):
            raise TrialBlocked('Collect/reconcile and confirm exact browser shutdown before next profile')
        with locked_json(self.path,self.read) as state:
            if state['active']!=source_account:raise TrialBlocked('Profile is not the active serial owner')
            state['profiles'][source_account]['release_evidence']=evidence
            state['active']=None
        return self.read()['profiles'][source_account]
