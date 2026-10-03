"""Real manifest dependency reuse must not rewrite product provenance."""
import json
from pathlib import Path
import tempfile
import unittest
from dashboard.data import Dashboard


class DashboardProductTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.job=self.root/'runs/shared-product';self.job.mkdir(parents=True)
        (self.job/'brief-current.json').write_text('{}')
        self.wav='revisions/audio/6/narration.wav';self.segment='revisions/audio/6/segment-0000.wav'
        self.srt='revisions/audio/6/subtitles.srt';self.image='revisions/images/4/scene.jpg'
        self.video='revisions/render/1/video.mp4';self.still='revisions/render/1/SC01.png';self.request='revisions/render/1/request-colab-render.json'
        for name in (self.wav,self.segment,self.srt,self.image,self.video,self.still,self.request):
            path=self.job/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'fixture')
        self.manifest('audio',2,[self.wav,self.segment,self.srt],{'wav':self.wav,'srt':self.srt,'segments':[{'path':self.segment}]})
        self.manifest('images',1,[self.image],{'items':[{'path':self.image}]})
        self.manifest('video',1,[self.video,self.still,self.request,self.wav,self.segment,self.image],
                      {'video':self.video,'stills':[self.still]})
        self.app=Dashboard(self.root,home=self.root/'home',cli=lambda argv:{'job':'shared-product','mode':'review',
            'checkpoints':[{'phase':'audio','revision':2,'state':'approved'},{'phase':'images','revision':1,'state':'approved'},
                           {'phase':'video','revision':1,'state':'awaiting_review'}]})

    def manifest(self,phase,revision,assets,payload):
        folder=self.job/'checkpoints'/phase/str(revision);folder.mkdir(parents=True)
        (folder/'manifest.json').write_text(json.dumps({'phase':phase,'revision':revision,'assets':assets,'payload':payload}))

    def test_later_render_dependencies_never_relabel_audio_or_images(self):
        value=self.app.job('shared-product');by_name={x['name']:x for x in value['artifacts']}
        self.assertEqual((by_name[self.wav]['phase'],by_name[self.wav]['revision']),('audio',2))
        self.assertEqual((by_name[self.segment]['phase'],by_name[self.segment]['revision']),('audio',2))
        self.assertEqual((by_name[self.image]['phase'],by_name[self.image]['revision']),('images',1))
        self.assertEqual((by_name[self.video]['phase'],by_name[self.video]['revision']),('video',1))

    def test_media_products_are_primary_audio_captions_images_and_video_separate(self):
        value=self.app.job('shared-product');by_name={x['name']:x for x in value['artifacts']}
        media={x['name'] for x in value['artifacts'] if x.get('display_group')=='media'}
        video={x['name'] for x in value['artifacts'] if x.get('display_group')=='video'}
        self.assertEqual(media,{self.wav,self.srt,self.image})
        self.assertEqual(video,{self.video,self.still})
        self.assertEqual(by_name[self.segment]['display_group'],'details')
        self.assertEqual(by_name[self.request]['display_group'],'details')
        self.assertTrue(by_name[self.video]['current_checkpoint'])
        self.assertEqual(by_name[self.wav]['source_revision'],6)

    def test_early_content_reference_cannot_win_against_actual_audio_owner(self):
        self.manifest('outline',1,[self.wav],{'outline':[]})
        by_name={x['name']:x for x in self.app.job('shared-product')['artifacts']}
        self.assertEqual((by_name[self.wav]['phase'],by_name[self.wav]['revision']),('audio',2))
        self.assertEqual(by_name[self.wav]['owner_manifest_phase'],'audio')

    def test_dependency_without_current_owner_keeps_original_module_revision(self):
        shutil_path=self.job/'checkpoints/audio/2/manifest.json'
        shutil_path.unlink()
        by_name={x['name']:x for x in self.app.job('shared-product')['artifacts']}
        self.assertEqual((by_name[self.wav]['phase'],by_name[self.wav]['revision']),('audio',6))
        self.assertEqual(by_name[self.wav]['display_group'],'details')
        self.assertFalse(by_name[self.wav]['current_checkpoint'])


if __name__=='__main__':unittest.main()
