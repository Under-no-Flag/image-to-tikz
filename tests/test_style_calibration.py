"""Stroke darkness, selective CJK boldness and first-render preservation."""
import argparse,copy,sys,tempfile,unittest,shutil
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/image-to-tikz/scripts'))
from scene_builder import Canvas
import scene,render,workflow,first_pass,stroke_profile

class CalibrationTests(unittest.TestCase):
 def test_fwhm_and_ink_are_distinct_for_gray_strokes(self):
  im=Image.new('L',(80,40),255);d=ImageDraw.Draw(im);d.rectangle((5,10,35,13),fill=0);d.rectangle((45,10,75,13),fill=128)
  spec=[{'id':k,'orientation':'horizontal','box_xyxy':box} for k,box in [('black',[10,5,30,20]),('gray',[50,5,70,20])]]
  a,b=stroke_profile.measure(im,spec,80)['samples'];self.assertAlmostEqual(a['width_px'],4);self.assertAlmostEqual(b['width_px'],4);self.assertAlmostEqual(a['equivalent_black_ink_width_px'],4);self.assertLess(b['equivalent_black_ink_width_px'],2.01)
 def test_runs_preserve_normal_cjk_boundary_and_validate_text(self):
  self.assertEqual(render.text_runs_tex([{'text':'车站'},{'text':'head','weight':'bold'},{'text':'数据'}]),r'车站{\bfseries head}数据')
  c=Canvas(100,100);c.font('body',10);c.line('plain',arrow='none');c.style('label',shape='text');c.node('a',(0,0,80,20),'正文',text_runs=[{'text':'错误'}])
  with self.assertRaisesRegex(ValueError,'concatenate'):scene.validate(c.scene)
 @unittest.skipUnless(all(shutil.which(t) for t in ("xelatex","pdftoppm","pdfinfo")), "TeX/Poppler not installed")
 def test_cjk_weight_tiny_offsets_compile_and_first_pass_immutable(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);src=p/'source.png';Image.new('RGB',(100,100),'white').save(src);run=p/'run';workflow.prepare(argparse.Namespace(image=str(src),out=str(run),width_mm=100))
   c=Canvas(100,100);c.font('body',10,cjk_face='FandolSong-Regular.otf',cjk_bold_face='FandolSong-Bold.otf');c.font('bold',10,cjk_face='FandolSong-Regular.otf',cjk_bold_face='FandolSong-Bold.otf',weight='bold');c.line('plain',arrow='none');c.style('label',shape='text',padding_mm=0);c.style('bold',shape='text',font='bold',padding_mm=0)
   c.node('a',(0,0,90,14),'车站head数据',text_runs=[{'text':'车站'},{'text':'head','weight':'bold'},{'text':'数据'}]);c.node('b',(0,20,90,14),'加粗图注',style='bold');c.scene['nodes'][1]['relative']['dx']=-1.06484e-14;c.save(run/'scene.json')
   workflow.build(argparse.Namespace(run=str(run),generate_only=False));self.assertNotIn('e-14mm',(run/'figure.tex').read_text());log=(run/'compile.log').read_text();self.assertNotIn('Font Warning',log);self.assertNotIn('Overfull',log)
   dest=first_pass.capture(run);initial=(dest/'scene.json').read_bytes()
   with self.assertRaises(FileExistsError):first_pass.capture(run)
   self.assertEqual(initial,(dest/'scene.json').read_bytes())
if __name__=='__main__':unittest.main()
