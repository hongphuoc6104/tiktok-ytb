"""Authored continuity and a late scene change must survive the real compiler."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import image_pipeline
from flow_prompts import freeze
from pilot import digest


class StoryPromptPreservationTests(unittest.TestCase):
    def test_late_setting_change_and_repair_instructions_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'reference.png').write_bytes(b'fixture-reference')
            p=SimpleNamespace(root=root,path=lambda job,name:root/name)
            description='Preserve the two anonymous people and their clothes. ' * 6 + 'The woman sits behind an interview desk indoors.'
            preserve='Keep only the two scarf colors and appearances; allow a complete change of setting and poses.'
            change='Replace the street with an indoor office; seat the woman behind a desk and place the closed yellow umbrella beside it.'
            correction='Remove rain and make the interview desk visible.'
            content={'characters':[],'scenes':[{'images':[{'id':'IMG_OFFICE','description':description,'preserve':preserve,'change':change}]}]}
            pin=freeze('Nano Banana 2 Lite','1.2.0')
            with patch('flow_management.prompt_pin',return_value=pin),patch('image_pipeline.content',return_value=content),patch('adapters._flow_media_reference',return_value=(str(root/'reference.png'),'11111111-1111-4111-8111-111111111111')):
                prompt,meta=image_pipeline._template_request(p,'story','IMG_OFFICE','fallback',correction,'9:16',[],None,{'path':'reference.png','sha256':digest(root/'reference.png')},{'id':'IMG_OFFICE','image_id':'IMG_OFFICE','visible_text':[]})
            self.assertEqual(meta['data']['description'],description)
            self.assertEqual(meta['data']['preserve'],[preserve])
            self.assertEqual(meta['data']['change'],[change,correction])
            self.assertIn('interview desk indoors',prompt)
