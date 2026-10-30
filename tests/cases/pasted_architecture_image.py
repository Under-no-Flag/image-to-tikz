#!/usr/bin/env python3
"""Image-only reconstruction of the one user-selected pasted architecture PNG.

No paper/model/original TikZ source was consulted. Coordinates below are image
observations. PaddleOCR evidence and generated weather icon are stored per run.
"""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'skills/image-to-tikz/scripts'))
from scene_builder import Canvas

PROMPT='Use case: scientific-educational. Asset type: one small monochrome weather pictogram strip for a scientific architecture diagram. Subject: exactly three separate black outline icons, arranged horizontally left to right: a simple sun with eight short straight rays; a small cloud with three raindrops beneath; a slim thermometer with round bulb and three short tick marks to its right. Style: clean thin uniform black outline strokes, no shading, no color, no letters, no text, no numbers, no border. Composition: icons equally sized and tightly arranged with modest gaps, centered in a wide 3:1 composition. Transparent background. Do not make any neural network diagram, flowchart, or other objects.'

def build(out):
 c=Canvas(526,170);s=c.scene;k=c.k
 c.font('body',11,family='serif',leading=1.08)
 c.font('title',11,weight='bold',family='serif',leading=1.08)
 c.font('math',12,family='serif',leading=1.05)
 c.font('time',9.7,family='serif',leading=1.05)
 c.font('tiny',8,weight='bold',color='#DB6E25',family='serif')
 c.font('orange',10,weight='bold',color='#DB6E25',family='serif')
 c.font('caption',16,family='serif',leading=1.1)
 for key,w,color in [('plain',.65,'#111111'),('thin',.35,'#777777'),('panel',.1,'#EEEEEE'),('blue-panel',.1,'#DCE5F6'),('orange-panel',.1,'#FBE6D8'),('grid-blue',.55,'#5DA0D4'),('grid-gray',.45,'#A3A3A3'),('orange-line',.6,'#EB762F'),('texture-blue',.5,'#92BDDF'),('texture-yellow',.5,'#E6C65B')]:c.line(key,w,color,arrow='none')
 for key,dash in [('flow','solid'),('flow-dashed','dashed')]:
  c.line(key,.3,'#8A8A8A',dash=dash,arrow='end');s['line_styles'][key].update(arrow_tip='Triangle',tip_length_mm=.7,tip_width_mm=.55)
 s['line_styles']['flow-dashed']['dash_pattern_mm']=[.45,.35]
 c.style('label',shape='text',line='plain')
 for key,font in [('title','title'),('math','math'),('time','time'),('tiny','tiny'),('orange-label','orange'),('caption','caption')]:c.style(key,shape='text',line='plain',font=font)
 c.style('process',shape='rectangle',line='plain')
 c.style('gt-box',shape='rectangle',line='thin')
 for key,fill,line in [('external-panel','#EEEEEE','panel'),('temporal-panel','#DCE5F6','blue-panel'),('conv-panel','#FBE6D8','orange-panel')]:c.style(key,fill,shape='rounded',line=line,corner_mm=2.2)
 palette={
 'blue-front':('#B7D2EB','#8BB6DF'),'blue-top':('#D8E6F3','#B8D4EB'),'blue-right':('#9EBAD6','#6E9CCD'),
 'gray-front':('#D5D5D5','#BABABA'),'gray-top':('#E8E8E8','#D4D4D4'),'gray-right':('#BBBBBB','#A0A0A0'),
 'orange-cell':('#FBC2A6','#F5A17B'),'rep-vector':('#C2B4B1','#ABA8AD'),'ext-vector':('#D8B99F','#CDA78E')}
 for key,(a,b) in palette.items():
  c.style(key,a,shape='rectangle',line='orange-line' if key in ('orange-cell','ext-vector') else 'grid-blue' if key in ('blue-front','blue-top','blue-right','rep-vector') else 'grid-gray',gradient={'from':a,'to':b,'angle_deg':90})
 c.style('map-fill','#FCFBF5',shape='rectangle',line='plain')
 c.style('selected-map','#F6B588',shape='rectangle',line='orange-line')
 for f in s['fonts'].values():f['face']='Times New Roman'
 # Named panel roots establish relative layout. Exact box measurements are image-derived.
 c.node('external-panel',[107,78,101,103],style='external-panel',role='group')
 c.node('temporal-panel',[223,77,101,106],style='temporal-panel',role='group')
 c.node('conv-panel',[162,258,95,84],style='conv-panel',role='group')
 c.node('external-title',[110,16,101,14],'External Context',style='title')
 c.node('historical-title',[219,16,139,14],'Historical Service Data',style='title',parent='temporal-panel')
 c.node('weather-icons',[117,43,77,28],asset='weather-icons')
 c.node('feature-extraction',[118,85,80,31],'Feature\nExtraction',style='process')
 c.node('replicate',[118,140,80,22],'Replicate',style='process')
 c.node('convlstm-one',[233,85,80,22],'ConvLSTM',style='process',parent='temporal-panel')
 c.node('convlstm-two',[233,124,80,22],'ConvLSTM',style='process',parent='temporal-panel')
 c.node('batchnorm',[233,155,80,18],'BatchNorm',style='process',parent='temporal-panel')
 c.node('history-label',[261,31,32,16],r'$\mathbf{X}_t$',style='math',latex=True,parent='temporal-panel')
 c.node('history-ellipsis',[263,50,14,12],r'$\cdots$',style='time',latex=True,parent='temporal-panel')
 c.node('groundtruth-box',[369,28,54,54],style='gt-box',role='group',parent='temporal-panel')
 c.node('groundtruth-label',[380,30,30,17],r'$y_t$',style='math',latex=True,parent='groundtruth-box')
 def plane(key,box,cols=4,rows=4,parent=None,selected=False):
  x,y,w,h=box;skew=.39
  g={'kind':'grid-plane','face_mm':[w*k,h*k],'corners_uv':[[skew,0],[1,0],[1-skew,1],[0,1]],'grid':[cols,rows],'face_style':'map-fill','grid_style':'plain','outline_style':'plain'}
  if selected:g['cell_styles']=[[None]*cols for _ in range(rows)];g['cell_styles'][-1][0]='selected-map'
  c.node(key,box,glyph=g,parent=parent)
  # Small pale streaks are native texture marks, not inferred semantic connections.
  for r in range(rows):
   for q in range(cols):
    if selected and r==rows-1 and q==0:continue
    u=(q+.18)/cols;v=(r+.4)/rows
    def p(u,v):return c.pt(key,x+w*(skew*(1-v)+(1-skew)*u),y+h*v)
    s['component_paths'].append({'style':'texture-yellow' if (r+q)%2 else 'texture-blue','kind':'polyline','points':[p(u,v+.10/rows),p(u+.19/cols,v-.1/rows),p(u+.47/cols,v+.08/rows)]})
  return key
 plane('history-first',[218,49,43,17],parent='temporal-panel')
 plane('history-previous',[278,48,43,17],parent='temporal-panel')
 plane('history-current',[317,48,41,17],parent='temporal-panel')
 plane('groundtruth-map',[375,48,42,17],parent='groundtruth-box')
 for key,box,txt,parent in [
 ('time-first',[216,66,42,11],r'$t-T+1$','history-first'),('time-previous',[283,65,31,11],r'$t-1$','history-previous'),('time-current',[326,65,24,13],r'$t$','history-current'),('time-truth',[380,66,34,13],r'$t+1$','groundtruth-box')]:c.node(key,box,txt,style='time',latex=True,parent=parent)
 def cube(key,box,face,depth,color,parent=None,selected=False):
  g={'kind':'cuboid','face_mm':[v*k for v in face],'depth_mm':[v*k for v in depth],'grid':[4,1,4],'face_styles':{f:color+'-'+f for f in ('front','top','right')},'grid_style':'grid-'+color,'outline_style':'grid-'+color,'visible_front_columns':4,'visible_depth_rows':4,'tensor_channels':None}
  if selected:
   g['cell_styles']={'front':[['orange-cell',None,None,None]],'top':[[None]*4 for _ in range(4)]}
   g['cell_styles']['top'][-1][0]='orange-cell'
  c.node(key,box,glyph=g,parent=parent)
 cube('external-cube',[120,201,68,36],[51,19],[17,17],'gray')
 cube('representation-cube',[238,193,68,44],[51,27],[17,17],'blue',parent='temporal-panel')
 c.node('external-depth',[96,214,17,20],r'$L_e$',style='math',latex=True,parent='external-cube')
 c.node('rep-depth',[217,214,17,20],r'$L_r$',style='math',latex=True,parent='representation-cube')
 for key,x,y,h in [('external-cube',115,218,19),('representation-cube',233,210,27)]:c.path([(key,x+2,y),(key,x,y),(key,x,y+h),(key,x+2,y+h)],style='plain')
 c.node('external-symbol',[127,241,50,16],r'$\mathbf{X}^{ext}_t$',style='math',latex=True,parent='external-cube')
 c.node('rep-symbol',[247,241,50,16],r'$\mathbf{X}^{rep}_t$',style='math',latex=True,parent='representation-cube')
 c.font('plus',8.5,family='serif');c.style('plus',shape='ellipse',line='plain',font='plus',text_width_ratio=.65)
 c.node('sum',[201,209,15,15],'+',style='plus',parent='conv-panel')
 c.node('conv-one',[169,267,80,22],r'$\mathrm{Conv2D}_{1\times1}$',style='process',latex=True,parent='conv-panel')
 c.node('conv-two',[169,312,80,22],r'$\mathrm{Conv2D}_{1\times1}$',style='process',latex=True,parent='conv-panel')
 plane('prediction-map',[172,351,73,29],parent='conv-panel')
 c.node('prediction-label',[152,346,24,26],r'$\widetilde{y}_t$',style='math',latex=True,parent='prediction-map')
 c.node('loss',[358,347,76,23],'Loss',style='process',parent='groundtruth-box')
 c.node('panel-a',[258,385,34,20],'(a)',parent='conv-panel')
 # Source arrow gaps are retained; tensors do not have visible links to the plus.
 def path(key,xy,style='flow'):c.path([(key,x,y) for x,y in xy],style=style)
 path('external-panel',[(157.5,119),(157.5,137)])
 path('external-panel',[(157.5,164),(157.5,195)])
 path('temporal-panel',[(273,73),(273,83)])
 path('temporal-panel',[(273,109),(273,122)],'flow-dashed')
 path('temporal-panel',[(273,148),(273,153)])
 path('temporal-panel',[(273,176),(273,191)])
 path('conv-panel',[(208.5,231),(208.5,254)])
 path('conv-panel',[(208.5,291),(208.5,310)],'flow-dashed')
 path('conv-panel',[(208.5,336),(208.5,349)])
 path('groundtruth-box',[(395.5,83),(395.5,345)])
 path('prediction-map',[(254,358.5),(356,358.5)])
 # Detail view: matched spatial front-face widths; channel heights intentionally differ.
 c.node('city-title',[132,423,100,20],'Citywide View',style='title',parent='external-panel')
 c.node('region-title',[306,423,96,20],'Region View',style='title',parent='city-title')
 cube('city-gray',[146,477,68,35],[51,19],[17,16],'gray',parent='city-title',selected=True)
 cube('city-blue',[146,450,68,44],[51,28],[17,16],'blue',parent='city-gray',selected=True)
 c.allow('city-gray','city-blue','The blue cuboid sits on the gray cuboid; their oblique bounding rectangles overlap in the hidden gray top face, as in the source.')
 c.node('city-rep-symbol',[107,468,37,24],r'$\mathbf{X}^{rep}_t$',style='math',latex=True,parent='city-blue')
 c.node('city-ext-symbol',[107,496,37,23],r'$\mathbf{X}^{ext}_t$',style='math',latex=True,parent='city-gray')
 plane('city-output',[146,545,74,28],parent='city-gray',selected=True)
 c.node('city-output-label',[114,552,25,27],r'$\widetilde{y}_t$',style='math',latex=True,parent='city-output')
 c.node('city-conv-label',[164,528,55,15],r'Conv2D $1\!\times\!1$',style='tiny',latex=True,parent='city-output')
 path('city-gray',[(146,466),(146,573)],'orange-line')
 path('city-gray',[(158.75,466),(158.75,573)],'orange-line')
 path('city-gray',[(163,512),(163,566)],'orange-line')
 for yy in (466,494,512):path('city-gray',[(146,yy),(158.75,yy)],'orange-line')
 # Hollow double arrow: single editable polygon, not two black filled arrow tips.
 c.node('view-equivalence',[248,497,27,16],parent='city-title')
 path('view-equivalence',[(248,505),(256,497),(256,501),(267,501),(267,497),(275,505),(267,513),(267,509),(256,509),(256,513),(248,505)],'plain')
 c.node('region-rep-label',[288,445,77,21],r'$\mathbf{X}^{rep}_t[1,1,:]$',style='math',latex=True,parent='region-title')
 c.node('region-ext-label',[366,445,68,21],r'$\mathbf{X}^{ext}_t[1,1,:]$',style='math',latex=True,parent='region-title')
 c.node('region-rep-vector',[303,467,60,16],style='rep-vector',parent='region-title')
 c.node('region-ext-vector',[364,467,35,16],style='ext-vector',parent='region-rep-vector')
 c.node('dense-label',[334,516,43,18],'Dense',style='orange-label',parent='region-rep-vector')
 c.node('region-result',[346,540,20,18],style='orange-cell',parent='region-rep-vector')
 path('region-rep-vector',[(303,483),(343,539)],'orange-line')
 path('region-ext-vector',[(399,483),(367,539)],'orange-line')
 c.node('region-result-label',[332,562,48,24],r'$\widetilde{y}_{t}[1,1]$',style='math',latex=True,parent='region-result')
 c.node('panel-b',[260,581,34,20],'(b)',parent='city-title')
 c.node('caption',[124,620,280,28],'Figure 3: Proposed network structure.',style='caption',parent='city-title',ocr_ids=['ocr-001'])
 c.allow('history-previous','history-current','Oblique plane bounding rectangles overlap but the slanted faces have a visible gap.')
 c.allow('prediction-map','prediction-label','The label box extends into the empty upper-left corner outside the oblique grid face; visible text and grid remain separated.')
 s['alignments']=[{'axis':'x','nodes':['feature-extraction','replicate']},{'axis':'x','nodes':['convlstm-one','convlstm-two','batchnorm']},{'axis':'x','nodes':['conv-one','conv-two']},{'axis':'y','nodes':['region-rep-vector','region-ext-vector']},{'axis':'y','nodes':['city-title','region-title']}]
 # Provenance stays with the replaceable raster icon; all other elements are native.
 icon=out/'assets/weather-icons.png'
 s['assets']={'weather-icons':{'path':'assets/weather-icons.png','kind':'generated-icon','sha256':hashlib.sha256(icon.read_bytes()).hexdigest(),'prompt':PROMPT,'generator':'image_gen','source':'built-in image_gen, generated 2026-10-30; no source diagram pixels reused','crop_px':[346,122,1770,586],'width_px':2172,'height_px':724}}
 (out/'assets/weather-icons-provenance.json').write_text(json.dumps(s['assets']['weather-icons'],indent=2)+'\n')
 s['evidence']={'input_scope':'Only selected PNG and PaddleOCR output. No model, paper, or original TikZ source read.','manual_geometry':'Measured visible image geometry only; 4 columns and 4 depth rows on all cuboids, channel dimensions remain symbolic L_e/L_r. City blue/gray heights 28/19 pixels retained.','topology':'No horizontal arrows into plus were visible and none were invented. Two dashed down arrows retained. View equivalence is a hollow polygon.','texture_limit':'Pale blue/yellow marks inside map grids are schematic native strokes. The 526-pixel source does not resolve their exact trajectories. Weather icons are generated approximations, independently replaceable PNG.','manual_text_recovery':['Main-panel OCR omitted X_t and all time labels; L_e/L_r; X_t ext/rep; the second ConvLSTM and second Conv2D; tilde y labels. Detail OCR omitted city tensor labels, Conv2D 1x1, and (b). These were transcribed from source and are not claimed as OCR successes.'],'ocr_reconciliation':[]}
 ocr=json.loads((out/'ocr.json').read_text())
 for block in ocr['lines']:
  if block['id']=='ocr-001':continue
  # Aggregate regional blocks are evidence for the panel; they do not set font sizes.
  owner='external-title' if 'main' in block['id'] else 'city-title'
  next(n for n in s['nodes'] if n['id']==owner).setdefault('ocr_ids',[]).append(block['id'])
  s['evidence']['ocr_reconciliation'].append({'ocr_id':block['id'],'text':block['text'],'note':'Aggregate text manually reconciled against zoomed source; equations, superscripts and layout were reviewed. No character-size measurement inferred from aggregate box.'})
 c.save(out/'scene.json')
 return s
if __name__=='__main__':
 out=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'outputs/pasted-architecture-image-only-001'
 build(out)
 print(out/'scene.json')
