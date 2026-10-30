"""Projected surfaces, typed arrows and explicit icon integrity regressions."""
import argparse,copy,hashlib,json,sys,tempfile,unittest,shutil
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/image-to-tikz/scripts'))
import scene,render,workflow,icon_assets
from scene_builder import Canvas
from glyphs import dimensions

def example():
 c=Canvas(100,100);c.font('body',8);c.line('plain',.3,arrow='none');c.line('flow',.4)
 c.style('label',shape='text');c.style('front','#88AAFF',gradient={'from':'#CCDDFF','to':'#4488CC','angle_deg':0});c.style('top','#BBDDEE');c.style('right','#5588CC');c.style('accent','#FF9944')
 c.node('cube',(0,0,24,20),glyph={'kind':'cuboid','face_mm':[20,15],'depth_mm':[4,5],'grid':[4,3,2],'face_styles':{'front':'front','top':'top','right':'right'},'grid_style':'plain','outline_style':'plain','cell_styles':{'front':[['accent',None,None,None],[None]*4,[None]*4]}})
 c.node('plane',(30,0,20,15),glyph={'kind':'grid-plane','face_mm':[20,15],'corners_uv':[[.2,0],[1,0],[.8,1],[0,1]],'grid':[4,3],'face_style':'front','grid_style':'plain','outline_style':'plain'})
 c.node('arrow',(58,3,18,10),glyph={'kind':'polygon','face_mm':[18,10],'points_uv':[[0,0],[.5,0],[1,.5],[.5,1],[0,1],[.5,.5]],'face_style':'accent','outline_style':'plain','shadow':{'dx_mm':.3,'dy_mm':.3,'color':'#888888','opacity':.3}})
 return c
class ProjectedGlyphTests(unittest.TestCase):
 def test_envelope_and_matrix_constraints(self):
  c=example();self.assertEqual(dimensions(c.scene['nodes'][0]['glyph']),(24,20));scene.validate(c.scene)
  c.scene['nodes'][0]['glyph']['cell_styles']['front'][0].pop()
  with self.assertRaisesRegex(ValueError,'matrix'):scene.validate(c.scene)
  c=example();c.scene['nodes'][0]['glyph']['depth_mm'][0]=-1
  with self.assertRaisesRegex(ValueError,'projection'):scene.validate(c.scene)
 def test_surface_and_arrow_parameters_are_not_raw_tex(self):
  c=example();c.scene['line_styles']['flow']['arrow_tip']='Latex] bad'
  with self.assertRaisesRegex(ValueError,'arrow tip'):scene.validate(c.scene)
  c=example();c.scene['node_styles']['front']['gradient']['from']='red'
  with self.assertRaisesRegex(ValueError,'gradient'):scene.validate(c.scene)
 def test_cardinal_local_origin_and_native_shading(self):
  tex=render.generate(example().scene)
  self.assertIn('cube.west |- cube.north',tex['figure.tex']);self.assertIn('shading=axis',tex['figure.tex']);self.assertNotIn('includegraphics',tex['figure.tex'])
 @unittest.skipUnless(all(shutil.which(t) for t in ("xelatex","pdftoppm","pdfinfo")), "TeX/Poppler not installed")
 def test_compile_surfaces_icon_and_all_tip_types(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td);src=d/'input.png';Image.new('RGB',(100,70),'white').save(src);run=d/'run'
   workflow.prepare(argparse.Namespace(image=str(src),out=str(run),width_mm=100))
   c=example()
   c.scene['nodes'][1]['glyph']['corners_uv'][0][1]=1e-15
   for i,tip in enumerate(['Latex','Stealth','Triangle','To','Bar','Circle']):
    key='line-'+str(i);c.line(key,.4,arrow='both');c.scene['line_styles'][key].update(arrow_tip=tip,tip_length_mm=2,tip_width_mm=1.5,tip_open=(i%2==0),double=i==2,rounded_mm=.5)
    c.path([('cube',1e-15,26+i*5),('plane',48,26+i*5)],key)
   (run/'assets').mkdir();icon=run/'assets/test.png';Image.new('RGBA',(40,30),(255,100,0,255)).save(icon)
   c.scene['assets']={'test':{'kind':'generated-icon','generator':'image_gen','prompt':'Synthetic unit-test fixture, NOT a real generation.','path':'assets/test.png','sha256':hashlib.sha256(icon.read_bytes()).hexdigest(),'width_px':40,'height_px':30,'crop_px':[5,5,30,25]}}
   c.node('icon',(60,25,18,14),asset='test');c.save(run/'scene.json')
   workflow.build(argparse.Namespace(run=str(run),generate_only=False))
   self.assertTrue((run/'preview.pdf').exists());log=(run/'compile.log').read_text();self.assertNotIn('Overfull',log);self.assertNotIn('LaTeX Font Warning',log)
   sig=workflow.signature(run);self.assertIn('assets/test.png',sig)
   icon.write_bytes(b'changed')
   self.assertNotEqual(sig,workflow.signature(run))
   with self.assertRaisesRegex(ValueError,'checksum'):icon_assets.verify_files(run,c.scene)
 def test_icon_invariants_reject_escape_and_text_flattening(self):
  c=example();c.scene['assets']={'icon':{'path':'assets/../escape.png'}}
  with self.assertRaisesRegex(ValueError,'safe'):scene.validate(c.scene)
  c=example();c.node('icon',(65,25,10,10),text='must remain editable',asset='unknown')
  with self.assertRaisesRegex(ValueError,'Unknown icon'):scene.validate(c.scene)
if __name__=='__main__':unittest.main()
