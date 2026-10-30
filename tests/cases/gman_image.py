"""GMAN Figure 4 diagram-only reconstruction from raster and real PaddleOCR.
No model code, paper text, original TikZ, or external references were consulted.
Run after workflow prepare/ocr; the crop provenance travels with the run.
"""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'skills/image-to-tikz/scripts'))
from scene_builder import Canvas
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--run',default='outputs/gman-image-only-001')
a=p.parse_args();run=Path(a.run)
c=Canvas(445,170);s=c.scene
c.font('body',12,family='serif',leading=1.06)
c.font('math',14,family='serif',leading=1.02)
c.font('plus',9,family='serif',leading=1)
c.line('plain',.55,arrow='none')
c.line('graph',.6,arrow='none')
c.line('flow',.6,arrow='end')
s['line_styles']['flow'].update(arrow_tip='Stealth',tip_length_mm=2.6,tip_width_mm=2.1)
c.line('pool',.55,'#FF3434','dashed','none')
s['line_styles']['pool']['dash_pattern_mm']=[2.5,1.6]
c.line('inter',.5,'#00A75F',arrow='none')
c.line('intra',.5,'#A65E50',arrow='none')
for name,font in [('label','body'),('math','math')]:c.style(name,shape='text',font=font)
c.style('blue','#00B4E7',shape='text')
c.style('orange','#F27A32',shape='text')
c.style('plane','#D9E2F4',shape='text')
c.style('yellow','#FFFF20',shape='text')
c.style('sum','#FFFFFF',shape='ellipse',font='plus',text_width_ratio=.3)
N=c.node
# A root anchor establishes Figure 4's crop coordinates; no unobserved semantic box.
N('canvas',(0,0,445,205),parent=None,role='group')

def polygon(key,box,points,style,parent='canvas'):
 n=N(key,box,parent=parent,role='group')
 n['glyph']={'kind':'polygon','face_mm':[box[2]*c.k,box[3]*c.k],
             'points_uv':points,'face_style':style}
 if style=='yellow': n['glyph']['outline_style']='plain'
 if style=='plane': n['glyph']['shadow']={'dx_mm':.35,'dy_mm':.5,'color':'#D5E2E8','opacity':.5}
 return n

def plane(key,box,parent='canvas'):
 w,h=box[2:];shear=.57*h
 return polygon(key,box,[[0,1],[shear/w,0],[1,0],[1-shear/w,1]],'plane',parent)

def network(key,box,pts,edges,parent):
 w,h=box[2:]
 return N(key,box,parent=parent,glyph={'kind':'motif','face_mm':[w*c.k,h*c.k],
  'vertices':[{'uv':[(x-box[0])/w,(y-box[1])/h],'radius_mm':5.1*c.k,'style':'blue','shape':'circle'} for x,y in pts],
  'edges':[{'ends':list(ij),'style':'graph'} for ij in edges]})

plane('input-plane',(8,48,172,96))
pts=[(46,90),(67,84),(84,70),(92,84),(118,58),(118,81),(143,97),(118,118),(102,100),(79,114),(55,129),(96,129)]
edges=[(0,1),(0,2),(0,10),(1,2),(1,3),(1,9),(2,3),(2,4),(3,8),(4,5),(4,6),(5,6),(5,8),(6,7),(7,8),(7,11),(8,9),(10,11)]
network('input-graph',(40,52,110,84),pts,edges,'input-plane')
N('input-label',(41,147,62,19),r'$H^{(l-1)}$','math',parent='input-plane',latex=True,ocr_ids=['ocr-001'])
# The partition chevron is a native editable polygon, not an image/icon.
polygon('partition-chevron',(155,93,23,18),[[0,0],[.48,0],[1,.5],[.48,1],[0,1],[.52,.5]],'yellow')
N('partition-label',(137,115,60,16),'Partition',parent='partition-chevron',ocr_ids=['ocr-001'])

for i,(y,dy) in enumerate([(20,0),(79,59),(144,124)]):
 plane(f'local-plane-{i}',(174,y,76,42))
 network(f'local-graph-{i}',(191,y,43,40),[(198,40+dy),(225,26+dy),(218,53+dy)],[(0,1),(0,2),(1,2)],f'local-plane-{i}')
 plane(f'attention-plane-{i}',(259,y,69,42))
 network(f'attention-graph-{i}',(271,y,40,40),[(277,39+dy),(304,26+dy),(297,52+dy)],[(0,1),(0,2),(1,2)],f'attention-plane-{i}')
 # Orange dots are their own graph markers so their local anchors remain editable.
 N(f'pool-{i}',(342,34+dy,12,12),parent=f'attention-plane-{i}',glyph={'kind':'motif','face_mm':[12*c.k,12*c.k],'vertices':[{'uv':[.5,.5],'radius_mm':5.2*c.k,'style':'orange'}],'edges':[]})
 N(f'inter-{i}',(374,34+dy,12,12),parent=f'pool-{i}',glyph={'kind':'motif','face_mm':[12*c.k,12*c.k],'vertices':[{'uv':[.5,.5],'radius_mm':5.2*c.k,'style':'orange'}],'edges':[]})
 # Three visible dashed red connections stop at the pooled circle boundary.
 for j,(x,yy) in enumerate([(282,39+dy),(309,27+dy),(302,51+dy)]):
  c.path([(f'attention-graph-{i}',x,yy),(f'pool-{i}',342,40+dy)],'pool')

N('intra-label',(208,54,94,34),'Intra-group\nspatial attention',parent='local-plane-0',ocr_ids=['ocr-001'])
N('pool-label',(296,37,48,37),'Max\npooling',parent='attention-plane-0',ocr_ids=['ocr-001'])
N('inter-label',(330,55,112,34),'Inter-group\nspatial attention',parent='inter-0',ocr_ids=['ocr-001'])
# Three brown lines are present ONLY for the upper group; no lines in the gaps below.
for x,y in [(203,40),(230,27),(223,52)]:
 c.path([('local-graph-0',x,y),('attention-graph-0',272,39)],'intra')
# Green three-way geometry converges at the top inter-group orange marker.
c.path([('pool-0',353,40),('inter-0',375,40)],'inter')
c.path([('pool-1',353,99),('inter-0',373,40)],'inter')
c.path([('pool-2',353,164),('inter-0',373,40)],'inter')
# Ellipses are native text; they indicate omitted groups, not counted channels.
N('local-ellipsis',(192,127,32,14),r'$\cdots$','math',parent='local-plane-1',latex=True,ocr_ids=['ocr-001'])
N('attention-ellipsis',(277,127,32,14),r'$\cdots$','math',parent='attention-plane-1',latex=True)
for i,y in [(0,15),(1,124),(2,189)]:
 N(f'sum-{i}',(373,y-7,14,14),'','sum',parent=f'inter-{i}')
 c.path([(f'sum-{i}',377,y),(f'sum-{i}',383,y)],'plain')
 c.path([(f'sum-{i}',380,y-3),(f'sum-{i}',380,y+3)],'plain')
# Residual routes visibly attach to plane/card edges (not guessed graph nodes).
c.path([('attention-graph-0',304,21),('attention-graph-0',304,15),('sum-0',372,15)],'flow')
c.path([('attention-plane-1',282,115),('attention-plane-1',282,124),('sum-1',372,124)],'flow')
c.path([('attention-plane-2',282,180),('attention-plane-2',282,189),('sum-2',372,189)],'flow')
c.path([('inter-0',380,35),('sum-0',380,22)],'flow')
c.path([('inter-1',380,104),('sum-1',380,117)],'flow')
c.path([('inter-2',380,169),('sum-2',380,182)],'flow')
N('output-label',(404,113,37,27),r'$H_S^{(l)}$','math',parent='sum-1',latex=True)
c.path([('sum-0',387,15),('sum-0',420,15),('output-label',420,109)],'flow')
c.path([('sum-1',387,124),('output-label',401,124)],'flow')
c.path([('sum-2',387,189),('sum-2',420,189),('output-label',420,140)],'flow')
s['alignments']=[{'axis':'x','nodes':['sum-0','sum-1','sum-2']},{'axis':'x','nodes':['inter-0','inter-1','inter-2']},{'axis':'x','nodes':['pool-0','pool-1','pool-2']}]
# Each allowance refers to a visually inspected blank part of a slanted-card or
# text bounding rectangle; it does not waive visible ink collisions globally.
for u,v,reason in [
 ('input-plane','partition-label','Partition text is right of the main plane sloping edge; rectangular boxes overlap in the blank corner.'),
 ('input-plane','local-plane-0','Slanted-plane bounding rectangles overlap by 6 px, while their visible polygons are separated.'),
 ('input-plane','local-plane-1','Slanted-plane bounding rectangles overlap by 6 px, while their visible polygons are separated.'),
 ('input-graph','partition-label','Input graph upper-right box corner is blank at the Partition text baseline.'),
 ('partition-chevron','local-plane-1','Chevron occupies the blank lower-left corner outside the neighboring slanted polygon.'),
 ('partition-label','local-plane-1','Partition text is left of the neighboring plane at the text baseline.'),
 ('partition-label','local-graph-1','Text ends before the local graph bottom vertex; their broad bounds include empty margins.'),
 ('partition-label','local-ellipsis','Only text-box corners meet; Partition baseline and ellipsis baseline are separate.'),
 ('local-plane-0','intra-label','Intra-group label uses the blank lower-right corner and gap beneath the upper plane.'),
 ('local-graph-0','intra-label','Graph lower vertex is above the visible first text line; box overlap is in empty margins.'),
 ('attention-plane-0','intra-label','Intra-group label occupies blank lower-left space outside the attention plane polygon.'),
 ('attention-graph-0','intra-label','First label line ends left of the graph; second line is below its visible vertices.'),
 ('attention-plane-0','pool-label','Max pooling label sits in the source plane lower-right blank corner.'),
 ('attention-graph-0','pool-label','Pooling text is right/below the visible graph triangle, though bounds overlap.'),
 ('pool-0','pool-label','The Max text line ends left of the orange point; only nominal box corners meet.'),
 ('local-plane-1','intra-label','The second label line sits above the slanted plane; its box overlaps the upper-right blank margin.'),
 ('local-graph-1','intra-label','The local top vertex begins just below the label ink, matching the tight source gap.'),
 ('attention-plane-1','intra-label','Label sits in the blank upper-left corner of the next-row slanted plane bounds.'),
 ('attention-graph-1','intra-label','Second-row graph top-left box corner is blank beneath the attention text.'),
 ('intra-label','pool-label','The two operation-label boxes overlap only in their blank side margins; actual text remains separated.'),
 ('pool-label','inter-label','Pooling lower line and Inter-group upper line are horizontally separated; only their nominal margins overlap.')]:
 c.allow(u,v,reason)
s['evidence']={'mode':'image-only','input':'test-images/GMAN-p04-diagram.png','scope':'Only Figure 4 diagram; source crop [40,315,485,520], no caption or other figures/prose.',
 'visible_graphs':{'input_vertices':12,'groups_shown':3,'vertices_per_group':3,'tensor_channels':None,'note':'Visible graph-node counts are geometric observations, not model channel counts.'},
 'topology_basis':'Only visible raster lines; no architecture/model knowledge used. Upper local-to-attention three lines are drawn; lower gaps are kept empty.',
 'ocr_reconciliation':['Real PaddleOCR-VL no-layout whole-crop recognition returned a single aggregate block, not word boxes. Its geometry does not establish font sizes.','The initial operation-label crop truncated the right phrase; its raw partial result is retained. The later operation-labels-full crop covers all operation labels.','Output formula PaddleOCR H_s^(l) is corrected to H_S^(l) from the visible capital S; upper/lower indices and ellipses were visually checked. Repeated label words are manually reconciled rather than claimed as exact OCR.'],
 'limitations':['Small graph edge centers are traced from a 445×205 crop. Antialiasing and soft source shadows are not identical.','All diagram elements are native editable TikZ. No raster icons are needed for Figure 4.']}
# Attach real region OCR blocks where available, without fabricating coverage.
if (run/'ocr.json').exists():
 for item in json.loads((run/'ocr.json').read_text()).get('lines',[]):
  if item['id'].startswith('crop-operation-labels'):
   for key in ['intra-label','pool-label','inter-label']:
    next(n for n in s['nodes'] if n['id']==key).setdefault('ocr_ids',[]).append(item['id'])
  if item['id'].startswith('crop-output-label'):
   next(n for n in s['nodes'] if n['id']=='output-label').setdefault('ocr_ids',[]).append(item['id'])
c.save(run/'scene.json')
