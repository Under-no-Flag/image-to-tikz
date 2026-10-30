"""Relocate the release ZIP and render a new scene from an unrelated directory."""
import argparse, hashlib, json, shutil, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'skills/image-to-tikz/scripts'))
from package_skill import package
from PIL import Image
import export_preview

class PortabilityTests(unittest.TestCase):
    @unittest.skipUnless(all(shutil.which(t) for t in ('xelatex','pdftoppm','pdfinfo')), 'TeX/Poppler not installed')
    def test_relocated_skill_new_scene_and_nonmutating_high_resolution_export(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);archive=package(root/'dist')
            with zipfile.ZipFile(archive) as z:
                self.assertFalse(any('tests/' in n or '__pycache__' in n or 'outputs/' in n for n in z.namelist()))
                z.extractall(root/'installed')
            skill=root/'installed/image-to-tikz';cwd=root/'elsewhere';cwd.mkdir();run=root/'work'
            source=root/'new-input.png';Image.new('RGB',(640,320),'white').save(source)
            def call(*args):
                result=subprocess.run([sys.executable,str(skill/'scripts/workflow.py'),*map(str,args)],cwd=cwd,capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            call('prepare',source,'--out',run,'--width-mm','123')
            data=json.loads((run/'scene.json').read_text())
            data['nodes']=[{'id':'sensor','style':'process','size':'standard','text':'信号输入','at_mm':[7,9]},
                {'id':'predict','style':'process','size':'standard','text':'风险预测','relative':{'of':'sensor','dx':'column-pitch','dy':0}}]
            data['edges']=[{'id':'signal','from':'sensor.east','to':'predict.west','style':'normal'}]
            (run/'scene.json').write_text(json.dumps(data))
            call('build',run,'--dpi','150')
            before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in run.iterdir() if p.is_file()}
            (run/'image-only-frozen').mkdir()
            call('export',run,'--out',root/'high-res','--dpi','600')
            after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in run.iterdir() if p.is_file()}
            self.assertEqual(before,after)
            with Image.open(run/'preview.png') as im: low=im.size
            with Image.open(root/'high-res/preview.png') as im: high=im.size
            self.assertAlmostEqual(high[0]/low[0],4,delta=.05)
            metadata=json.loads((root/'high-res/export.json').read_text())
            self.assertEqual(metadata['dpi'],600);self.assertFalse(metadata['possible_page_clipping'])
            with self.assertRaisesRegex(ValueError,'preserve'):
                export_preview.export_run(argparse.Namespace(run=str(run),out=str(run/'extra'),dpi=600))
            with self.assertRaises(FileExistsError):
                export_preview.render_pdf(run/'preview.pdf',root/'high-res/preview.png')
            with self.assertRaises(ValueError):
                export_preview.render_pdf(run/'preview.pdf',root/'invalid.png',0)

if __name__=='__main__':unittest.main()
