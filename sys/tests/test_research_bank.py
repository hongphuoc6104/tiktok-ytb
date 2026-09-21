"""Isolated catalog, reservation and branch policy checks; no real generation."""
import copy
import datetime as dt
import json
import multiprocessing
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from research import bank, policy, visuals
from research.build_catalog import normalized
from pilot import Blocked

ROOT=Path(__file__).resolve().parents[1]

def worker(root,job,topic_id,q):
    try:bank.reserve(job,topic_id,root=Path(root));q.put('reserved')
    except ValueError:q.put('blocked')

class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        shutil.copytree(ROOT/'research',self.root/'research',ignore=shutil.ignore_patterns('__pycache__','prepared','.ledger.lock'))
        shutil.copytree(ROOT/'schemas',self.root/'schemas')
        bank.atomic(self.root/'research/ledger.json',dict(schema_version=1,entries={},events=[]))
        self.t=bank.available(self.root)[0]
    def evidence(self,t=None):
        return dict(topic_id=(t or self.t)['id'],checked_on=dt.date.today().isoformat(),checked_by='TEST ONLY',verification_note='Synthetic isolated fixture, not production evidence',goal='TEST goal',required_points=['TEST point A','TEST point B','TEST point C'],sources=[dict(id='S1',title='TEST source',reference='https://example.org/test',facts=['TEST fact'])])
    def test_catalog(self):
        rows=bank.topics(self.root)
        self.assertEqual(len(rows),1000);self.assertEqual(len({normalized(t['title']) for t in rows}),1000)
        self.assertEqual(len(list((self.root/'research/topics').glob('*.jsonl'))),40)
        self.assertTrue(all(len(p.read_text().splitlines())==25 for p in (self.root/'research/topics').glob('*.jsonl')))
    def test_reserve_idempotent_and_duplicate_blocked(self):
        t=bank.reserve('a',self.t['id'],root=self.root)
        self.assertEqual(bank.reserve('a',root=self.root),t)
        with self.assertRaises(ValueError):bank.reserve('b',t['id'],root=self.root)
        self.assertEqual(bank.status(self.root)['reserved'],1)
    def test_concurrent_reservation(self):
        ctx=multiprocessing.get_context('fork');q=ctx.Queue()
        jobs=[ctx.Process(target=worker,args=(str(self.root),f'job{i}',self.t['id'],q)) for i in range(2)]
        for p in jobs:p.start()
        for p in jobs:p.join(10);self.assertEqual(p.exitcode,0)
        self.assertEqual(sorted(q.get(timeout=2) for _ in jobs),['blocked','reserved'])
    def test_release_history_and_no_live_release(self):
        bank.reserve('a',self.t['id'],root=self.root);bank.release('a','test',self.root)
        self.assertEqual(bank.status(self.root)['available'],1000)
        bank.reserve('a',self.t['id'],root=self.root);(self.root/'runs/a').mkdir(parents=True)
        with self.assertRaises(ValueError):bank.release('a','test',self.root)
    def test_stale_and_future_evidence(self):
        for offset in [-self.t['refresh_after_days']-1,1]:
            e=self.evidence();e['checked_on']=(dt.date.today()+dt.timedelta(days=offset)).isoformat()
            with self.assertRaises(ValueError):bank.validate_evidence(self.t,e)
    def test_prepare_and_real_policy(self):
        bank.reserve('a',self.t['id'],root=self.root)
        e=self.root/'e.json';bank.atomic(e,self.evidence());path=bank.prepare('a',e,self.root);b=bank.read(path)
        policy.check(self.root,'a',b)
        self.assertEqual(b['duration'],{'min_seconds':90,'max_seconds':180})
        self.assertIsNotNone(visuals.settings(b))
        for field,value in [('topic','changed'),('facts_required',False),('sources',[])]:
            bad=copy.deepcopy(b);bad[field]=value
            with self.assertRaises(Blocked):policy.check(self.root,'a',bad)
        with self.assertRaises(Blocked):policy.check(self.root,'b',b)
        with self.assertRaises(ValueError):bank.prepare('a',e,self.root)
    def test_unreserved_research_blocked_generic_unchanged(self):
        policy.check(self.root,'a',dict(video_type='interpersonal'))
        with self.assertRaises(Blocked):policy.check(self.root,'a',dict(video_type='research-guide'))
    def test_no_mark_without_approved_video(self):
        bank.reserve('a',root=self.root)
        with self.assertRaises(ValueError):bank.mark('a',self.root)
        self.assertEqual(bank.status(self.root)['done'],0)
    def test_mark_uses_verified_completion_and_is_idempotent(self):
        bank.reserve('a',self.t['id'],root=self.root)
        with patch.object(bank,'completion',return_value=(self.t['id'],2)):
            bank.mark('a',self.root);bank.mark('a',self.root)
        self.assertEqual(bank.status(self.root)['done'],1)
        with self.assertRaises(ValueError):bank.reserve('b',self.t['id'],root=self.root)
        self.assertEqual(len([e for e in bank.ledger(self.root)['events'] if e['action']=='done']),1)
    def test_path_rejection(self):
        with self.assertRaises(ValueError):bank.reserve('../bad',root=self.root)
    def test_visual_budget(self):
        v=bank.read(self.root/'research/channel.json')['visuals'];b={'planning':{'domain_requirements':['research-visuals:'+json.dumps(v)]}}
        c={'scenes':[dict(images=[{}]*3,beats=[{}]*4) for _ in range(6)]}
        visuals.validate(b,c)
        c['scenes'][0]['images']=[]
        with self.assertRaises(ValueError):visuals.validate(b,c)
    def test_text_timing_warning(self):
        v=bank.read(self.root/'research/channel.json')['visuals'];b={'planning':{'domain_requirements':['research-visuals:'+json.dumps(v)]}}
        c={'scenes':[dict(images=[dict(id='I1',visible_text=[{'text':'TEST'}])],beats=[dict(id='B1',image_id='I1')])]}
        timing={'vi':[dict(start=0,end=2,images=[dict(id='B1',at=0)])]}
        self.assertEqual(len(visuals.timing_report(b,c,timing)['warnings']),1)

if __name__=='__main__':unittest.main()
