"""Real isolated Unix sockets/CLI recovery; no Flow/browser/provider actions."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from permissions import Grants, PermissionDenied
from scripts.bootstrap import (control_recover_stale, control_start, control_status,
                               session_socket_path, socket_ownership)

ROOT=Path(__file__).resolve().parents[1]

class BootstrapRecoveryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)/'sys';self.root.mkdir()
  self.path=session_socket_path(self.root);self.path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
  self.addCleanup(lambda:self.path.unlink(missing_ok=True))
  self.grant=Grants(self.root).grant('setup',source='TEST authorized daemon recovery',paths=['experiments/b2_illustrator/session.mjs'])['id']
  self.source='TEST actual recovery instruction'
 def stale(self):
  code='import os,socket,sys;s=socket.socket(socket.AF_UNIX);s.bind(sys.argv[1]);os.chmod(sys.argv[1],0o600);s.close()'
  subprocess.run([sys.executable,'-c',code,str(self.path)],check=True,timeout=5)
  self.assertEqual(control_status(self.root)['state'],'connection_refused')
 def recover(self):return control_recover_stale(self.root,grant=self.grant,source=self.source)
 def test_reproduce_official_start_refusal_then_recover_real_stale_manual_socket(self):
  self.stale();before=self.path.lstat().st_ino
  with patch('scripts.bootstrap.control_dependencies',return_value={'state':'verified','node':'/bin/true','runtime':'/tmp/fixture-runtime'}):
   with self.assertRaisesRegex(RuntimeError,'owner is unresolved'):control_start(self.root,grant=self.grant,source=self.source)
  self.assertEqual(self.path.lstat().st_ino,before);ownership=socket_ownership(self.root);self.assertEqual(ownership['state'],'verified');self.assertEqual(ownership['kernel_inodes'],[])
  result=self.recover();self.assertTrue(result['recovered']);self.assertFalse(self.path.exists());self.assertTrue(result['manual_owner_record_missing']);evidence=json.loads(Path(result['evidence']).read_text());self.assertEqual(evidence['inode'],before);self.assertFalse(evidence['browser_started']);self.assertFalse(evidence['provider_called'])
  self.assertFalse(self.recover()['recovered'])
 def test_public_dependency_free_cli_recovers_only_isolated_exact_socket(self):
  self.stale();(self.root/'scripts').mkdir()
  shutil.copyfile(ROOT/'scripts/bootstrap.py',self.root/'scripts/bootstrap.py')
  for name in ('profile_setup.py','permissions.py','account_catalog.py','session_store.py'):shutil.copyfile(ROOT/name,self.root/name)
  result=subprocess.run([sys.executable,'-I','-S',str(self.root/'scripts/bootstrap.py'),'control-recover-stale','--root',str(self.root),'--grant',self.grant,'--source',self.source],capture_output=True,text=True,timeout=5)
  self.assertEqual(result.returncode,0,result.stdout+result.stderr);self.assertTrue(json.loads(result.stdout)['recovered']);self.assertFalse(self.path.exists())
 def test_live_kernel_socket_refuses_recovery_even_when_not_listening(self):
  live=socket.socket(socket.AF_UNIX);live.bind(str(self.path));os.chmod(self.path,0o600)
  try:
   self.assertEqual(control_status(self.root)['state'],'connection_refused');evidence=socket_ownership(self.root);self.assertEqual(evidence['state'],'live_or_shared_owner');self.assertTrue(evidence['kernel_inodes']);self.assertTrue(any(x['pid']==os.getpid() for x in evidence['inode_owners']))
   with self.assertRaisesRegex(RuntimeError,'ownership unresolved'):self.recover()
   self.assertTrue(self.path.exists())
  finally:live.close()
 def test_exact_same_checkout_daemon_without_record_blocks_cleanup(self):
  self.stale();script=self.root/'experiments/b2_illustrator/session.mjs';script.parent.mkdir(parents=True);script.touch()
  process=subprocess.Popen([sys.executable,'-c','import time;time.sleep(10)',str(script),'serve'])
  try:
   evidence=socket_ownership(self.root);self.assertTrue(any(item['pid']==process.pid for item in evidence['matching_daemons']))
   with self.assertRaisesRegex(RuntimeError,'ownership unresolved'):self.recover()
   self.assertTrue(self.path.exists())
  finally:process.terminate();process.wait(timeout=5)
 def test_public_recovery_then_official_start_new_isolated_listener(self):
  if not shutil.which('node'):self.skipTest('Existing Node required; no installation')
  self.stale();self.recover();shutil.copytree(ROOT/'control',self.root/'control');script=self.root/'experiments/b2_illustrator/session.mjs';script.parent.mkdir(parents=True)
  script.write_text("import net from 'node:net';import fs from 'node:fs';const path="+json.dumps(str(self.path))+";const server=net.createServer(c=>c.on('data',()=>c.end(JSON.stringify({status:'not_connected'})+'\\n')));server.listen(path,()=>fs.chmodSync(path,0o600));")
  launched=[]
  def launch(*args,**kwargs):p=subprocess.Popen(*args,**kwargs);launched.append(p);return p
  dependencies={'state':'verified','node':shutil.which('node'),'runtime':str(self.root/'fixture-control')}
  with patch('scripts.bootstrap.control_dependencies',return_value=dependencies):
   try:
    result=control_start(self.root,grant=self.grant,source=self.source,runner=launch);self.assertEqual(result['state'],'verified');self.assertFalse(result['browser_started']);self.assertFalse(result['provider_called']);owner=json.loads((self.root/'.state/flow-control.json').read_text());self.assertTrue(owner['start_ticks']);self.assertEqual(len(launched),1)
    again=control_start(self.root,grant=self.grant,source=self.source,runner=launch);self.assertTrue(again['reused']);self.assertEqual(len(launched),1)
   finally:
    for process in launched:process.terminate();process.wait(timeout=5)
 def test_timeout_does_not_mean_daemon_terminal_or_allow_cleanup(self):
  self.stale()
  with patch('scripts.bootstrap.socket.socket') as factory:
   factory.return_value.__enter__.return_value.connect.side_effect=TimeoutError('TEST timeout')
   value=control_status(self.root);self.assertEqual(value['state'],'unresponsive_or_invalid');self.assertFalse(value['terminal_transport'])
   with self.assertRaisesRegex(RuntimeError,'connection-refused'):self.recover()
  self.assertTrue(self.path.exists())
 def test_recorded_dead_owner_recovers_but_reused_live_pid_does_not(self):
  self.stale();process=subprocess.Popen([sys.executable,'-c','pass']);pid=process.pid;process.wait(timeout=5)
  owner=self.root/'.state/flow-control.json';owner.write_text(json.dumps({'pid':pid,'root':str(self.root),'socket':str(self.path),'start_ticks':'TEST departed process'}))
  self.assertEqual(socket_ownership(self.root)['recorded_owner']['state'],'dead');self.assertTrue(self.recover()['recovered'])
  self.stale();owner.write_text(json.dumps({'pid':os.getpid(),'root':str(self.root),'socket':str(self.path),'start_ticks':'wrong/reused PID'}))
  with self.assertRaisesRegex(RuntimeError,'ownership unresolved'):self.recover()
  self.assertTrue(self.path.exists())
 def test_unknown_record_foreign_root_and_shared_or_symlink_socket_never_unlinked(self):
  self.stale();owner=self.root/'.state/flow-control.json';owner.write_text(json.dumps({'pid':123,'root':'/foreign/checkout','socket':str(self.path)}))
  with self.assertRaisesRegex(RuntimeError,'ownership unresolved'):self.recover()
  owner.unlink();os.chmod(self.path,0o666)
  with self.assertRaisesRegex(RuntimeError,'Unsafe/shared'):self.recover()
  self.path.unlink();target=self.root/'other';target.write_text('keep');self.path.symlink_to(target)
  with self.assertRaisesRegex(RuntimeError,'connection-refused'):self.recover()
  self.assertEqual(target.read_text(),'keep')
 def test_source_grant_required_before_any_socket_change(self):
  self.stale();other=Grants(self.root).grant('setup',source='TEST wrong path',paths=['unrelated/**'])['id']
  for grant,source in ((other,self.source),(self.grant,''),(None,self.source)):
   with self.assertRaises(PermissionDenied):control_recover_stale(self.root,grant=grant,source=source)
  self.assertTrue(self.path.exists())
 def test_incomplete_proc_audit_preserves_socket(self):
  self.stale()
  with self.assertRaisesRegex(RuntimeError,'ownership unresolved'):control_recover_stale(self.root,grant=self.grant,source=self.source,proc_root=self.root/'no-proc')
  self.assertTrue(self.path.exists())
 def test_inode_replacement_during_check_is_not_unlinked(self):
  self.stale();original=socket_ownership
  def changed(root,**kwargs):
   value=original(root,**kwargs)
   if not getattr(changed,'done',False):
    changed.done=True;self.path.unlink();self.stale()
   return value
  with patch('scripts.bootstrap.socket_ownership',side_effect=changed):
   with self.assertRaisesRegex(RuntimeError,'changed during recovery'):self.recover()
  self.assertTrue(self.path.exists())

if __name__=='__main__':unittest.main()
