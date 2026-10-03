"""Opt-in Chromium test with isolated engine/provider fixtures, not live proof."""
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
import unittest
import wave
from unittest.mock import patch
from dashboard.data import Dashboard
from dashboard.server import make_server
from pilot import observe_job, write
import execution as ex
import tests.test_execution_v4 as fixture_module


@unittest.skipUnless(os.environ.get('VP_PLAYWRIGHT_MODULE') and shutil.which('node'), 'Set VP_PLAYWRIGHT_MODULE to an installed Playwright; no implicit browser install')
class DashboardBrowserTests(unittest.TestCase):
 def test_eight_tabs_media_and_exact_engine_review(self):
  f=fixture_module.ExecutionTests(methodName='test_dynamic_scene_count_freezes_from_this_outline');f.setUp()
  try:
   f.new('auto');f.author_inputs()
   def audio(p,j,out):
    file=out/'fixture.wav'
    with wave.open(str(file),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\x00\x00'*8000)
    return {'wav':str(file.relative_to(p.job(j))),'language':'vi'}
   def images(p,j,out):
    file=out/'fixture.png';file.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Zl6AAAAAASUVORK5CYII='))
    gallery=out/'gallery.json';write(gallery,{'items':[{'file':str(file.relative_to(p.job(j)))}],'fixture':True})
    return {'checkpoint':'final','references':[],'items':[{'scene_id':'SC01','image_id':'IM01','ratio':'9:16','path':str(file.relative_to(p.job(j))),'actual_prompt':'TEST synthetic image prompt; no provider generation'}],'proofs':[],'contact_sheet':None,'gallery':str(gallery.relative_to(p.job(j)))}
   with f.providers(),patch('adapters.audio',side_effect=audio),patch('image_pipeline.produce',side_effect=images):ex.advance(f.p,f.job)
   ex.change_mode(f.p,f.job,'review','TEST explicit browser review mode')
   def public(argv):
    if argv[0] in ('status','next'):return observe_job(f.root,argv[1],next_only=argv[0]=='next')
    if argv[0]=='approve':return ex.approve(f.p,argv[1],argv[2],int(argv[4]),argv[6])
    raise AssertionError('Unexpected browser mutation')
   app=Dashboard(f.root,cli=public,home=f.root/'home');server=make_server(f.root,dashboard=app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
   try:
    result=subprocess.run(['node',str(Path(__file__).with_name('dashboard_browser.mjs')),f'http://127.0.0.1:{server.server_port}'],capture_output=True,text=True,timeout=50)
    self.assertEqual(result.returncode,0,result.stderr);report=json.loads(result.stdout);self.assertEqual(len(report['tabs']),8);self.assertTrue(report['fixture_wav_metadata']);self.assertTrue(report['fixture_png_decode']);self.assertTrue(ex.accepted(f.p,f.job,'audio'))
   finally:server.shutdown();server.server_close();thread.join()
  finally:f.doCleanups()

if __name__=='__main__':unittest.main()
