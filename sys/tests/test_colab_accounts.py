import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from colab_bridge import accounts


class AccountTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.patch=patch.object(accounts,'STORE',self.root/'store');self.patch.start();self.addCleanup(self.patch.stop)
        self.source=self.root/'source';self.source.mkdir()
        (self.source/'token.json').write_text('{"test_only":true}')
        (self.source/'sessions.json').write_text('{}')

    def test_import_is_private_and_does_not_replace_source(self):
        accounts.add('account-01',self.source)
        self.assertEqual(accounts.select(),'account-01')
        token=accounts.folder('account-01')/'token.json'
        self.assertEqual(token.stat().st_mode & 0o777,0o600)
        self.assertEqual(token.parent.stat().st_mode & 0o777,0o700)
        token.write_text('changed')
        self.assertEqual((self.source/'token.json').read_text(),'{"test_only":true}')

    def test_auto_chooses_enabled_authenticated_profile(self):
        accounts.add('one',self.source);accounts.add('two',self.source)
        d=accounts.registry();d['accounts'][0]['enabled']=False;accounts.save(d)
        self.assertEqual(accounts.select(),'two')
        with self.assertRaises(ValueError):accounts.select('one')

    def test_no_overwrite_or_path_escape(self):
        accounts.add('one',self.source)
        with self.assertRaises(ValueError):accounts.add('one',self.source)
        with self.assertRaises(ValueError):accounts.folder('../bad')

    def test_launcher_uses_profile_without_global_token_swap(self):
        binary=self.root/'colab';binary.write_text('#!/usr/bin/python3\n')
        argv=accounts.command(binary,'two',['sessions'])
        self.assertEqual(argv[0],'/usr/bin/python3')
        self.assertEqual(argv[-2:], [str(accounts.folder('two')),'sessions'])
