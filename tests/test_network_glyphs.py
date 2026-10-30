import unittest,sys,tempfile,json
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/image-to-tikz/scripts'))
from glyphs import dimensions, validate_glyph,point
from paddle_ocr import normalize
class NetworkGlyphTests(unittest.TestCase):
 def test_stack_envelope_and_visible_count(self):
  g={'kind':'feature-stack','face_mm':[24,24],'visible_count':6,'step_mm':[2,3]}
  self.assertEqual(dimensions(g),(34,39))
  g['visible_count']=16;self.assertEqual(dimensions(g),(54,69))
  g['visible_count']=0
  with self.assertRaises(ValueError):dimensions(g)
 def test_slab_and_local_paths(self):
  self.assertEqual(dimensions({'kind':'slab','face_mm':[7,28],'shear_mm':28}),(35,28))
  s={'nodes':[{'id':'tensor','size':'s'}],'sizes':{'s':[35,28]}}
  self.assertIn('(17.5mm,-14mm)',point({'of':'tensor','uv':[.5,.5]},s))
  s['sizes']['s']=[70,56]
  self.assertIn('(35mm,-28mm)',point({'of':'tensor','uv':[.5,.5]},s))
 def test_aggregate_title_retained_but_not_grouped(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'image.png';Image.new('RGB',(600,200),'white').save(p)
   h=normalize({'parsing_res_list':[{'block_label':'doc_title','block_bbox':[0,0,600,200],'block_content':'A\nB\nC\nD\nE'}]},p,170)
   self.assertEqual(len(h['lines']),1);self.assertTrue(h['lines'][0]['aggregate']);self.assertEqual(h['suggested_size_groups_pt'],{})
if __name__=='__main__':unittest.main()

class ComplexDiagramTests(unittest.TestCase):
 def test_no_layout_ocr_has_no_font_estimate_cluster(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'crop.png';Image.new('RGB',(100,60),'white').save(p)
   h=normalize({'parsing_res_list':[{'block_label':'ocr','block_bbox':[0,0,100,60],'block_content':'H'}]},p,30)
   self.assertEqual(h['lines'][0]['text'],'H');self.assertEqual(h['suggested_size_groups_pt'],{})
   self.assertEqual(h['lines'][0]['font_source'],'unreliable-aggregate')
 def test_ellipse_local_origin_uses_cardinal_bounds(self):
  s={'nodes':[{'id':'ellipse','size':'s'}],'sizes':{'s':[10,20]}}
  self.assertEqual(point({'of':'ellipse','uv':[0,0]},s),'($(ellipse.west |- ellipse.north)+(0mm,0mm)$)')
 def test_invalid_motif_vertex_and_cubic_rejected(self):
  from glyphs import validate_motif,validate_paths
  s={'node_styles':{'blue':{}},'line_styles':{'flow':{}},'nodes':[{'id':'a'}]}
  g={'vertices':[{'uv':[.5,.5],'radius_mm':1,'style':'blue'}],'edges':[{'ends':[0,2],'style':'flow'}]}
  with self.assertRaisesRegex(ValueError,'vertex'):validate_motif(g,s)
  s['component_paths']=[{'style':'flow','kind':'cubic','points':[{'of':'a','uv':[0,0]}]*3}]
  with self.assertRaisesRegex(ValueError,'Cubic'):validate_paths(s)
 def test_group_containment_does_not_hide_crossing(self):
  from scene import geometry_checks
  s={'nodes':[{'id':'group','role':'group'},{'id':'child'}]}
  self.assertEqual(geometry_checks(s,{'group':[0,0,10,10],'child':[2,2,4,4]}),[])
  self.assertTrue(geometry_checks(s,{'group':[0,0,10,10],'child':[8,2,12,4]}))
 def test_relative_group_move_preserves_motif_and_curve(self):
  from scene_builder import Canvas
  from scene import resolve
  from render import generate
  c=Canvas(100,100);c.font('body',8,family='sans');c.line('plain',arrow='none');c.line('flow');c.style('label',shape='text');c.style('blue','#0000FF')
  c.node('root',(0,0,10,10));c.node('child',(15,0,10,10),parent='root',glyph={'kind':'motif','face_mm':[10,10],'vertices':[{'uv':[.5,.5],'radius_mm':1,'style':'blue'}]})
  c.path([('root',5,5),('root',5,20),('child',20,20),('child',20,5)],kind='cubic')
  a=resolve(c.scene);c.scene['nodes'][0]['at_mm'][0]+=5;b=resolve(c.scene)
  self.assertEqual(b['child'][0]-a['child'][0],5)
  tex=generate(c.scene)
  self.assertIn('.. controls',tex['figure.tex']);self.assertIn('circle[radius=',tex['figure.tex']);self.assertIn('\\sffamily',tex['styles.tex']);self.assertNotIn('includegraphics',tex['figure.tex'])
