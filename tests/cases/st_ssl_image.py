"""ST-SSL raster observations only; no paper/model/source-code lookup."""
import sys,json,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'skills/image-to-tikz/scripts'))
from scene_builder import Canvas
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--run",default="outputs/st-ssl-image-only-001");args=parser.parse_args()
c=Canvas(1065,240);s=c.scene
c.font('body',8,family='sans',leading=1.05);c.font('small',7,family='sans',leading=1.05);c.font('math',9);c.font('caption',10.7);c.font('bold',9,family='sans',weight='bold');c.font('positive',8.4,color='#6DA54D');c.font('negative',8.4,color='#FF0000')
c.line('plain',.5,arrow='none');c.line('flow',.7);c.line('dash',.5,dash='dashed',arrow='none');c.line('dotted',.7,dash='dotted',arrow='none');c.line('soft',.4,'#BABABA',arrow='none');c.line('graph',.3,'#C4CCD2',arrow='none');c.line('yellow',.6,'#F4D846',arrow='none');c.line('lightdash',.35,'#B5B5B5','dashed','none');c.line('wide',2,'#C3CDD3');c.line('widegreen',2,'#D6DFC9')
for k,font in [('label','body'),('small','small'),('math','math'),('caption','caption'),('bold','bold'),('positive','positive'),('negative','negative')]:c.style(k,shape='text',font=font)
c.font('mixed',7.5);c.style('mixed',shape='text',font='mixed')
c.style('frame',shape='rectangle',line='dash',fill_opacity=0)
c.style('encoder','#DDEBF5');c.style('green','#E2EED8',corner_mm=1);c.style('greeninner','#DDE9D0');c.style('b','#FFF1C7',font='bold');c.style('d','#F3C5C5',font='bold');c.style('fusion',font='small');c.style('card',line='soft');c.style('cloud',shape='ellipse',line='lightdash',fill_opacity=0)
for name,col in [('blue','#5799DB'),('orange','#FAC8A9'),('lightgreen','#B4D597'),('red','#E97870')]:c.style(name,col,shape='text')
N=c.node
N('a',(32,17,499,235),style='frame',role='group');N('b',(531,17,249,235),style='frame',role='group',parent='a');N('d',(780,17,235,235),style='frame',role='group',parent='b')
for key,x in [('a',37),('b',536),('d',786)]:N('panel-'+key,(x,233,22,16),'('+('c' if key=='d' else key)+')','bold',parent=key)
N('caption',(24,261,1008,24),'Figure 2: (a): The overall architecture of ST-SSL. (b): Spatial heterogeneity modeling. (c): Temporal heterogeneity modeling.','caption',parent='a')
N('input-label',(38,70,72,18),r'\textsf{Input TFG } $\mathcal G$','mixed',parent='a',latex=True)
N('aug-label',(40,198,65,34),r'\textsf{Augmented}\\\textsf{TFG } $\widetilde{\mathcal G}$','mixed',parent='a',latex=True)
N('encoder',(252,53,76,35),'ST Encoder','encoder',parent='a');N('encoder-aug',(252,183,76,35),'ST Encoder','encoder',parent='a')
N('augment',(38,111,197,56),style='green',role='group',parent='a');N('augment-title',(43,113,187,17),'Adaptive Graph Augmentation',parent='augment')
N('traffic',(45,132,76,30),style='greeninner',role='group',parent='augment');N('topology',(136,132,90,30),style='greeninner',role='group',parent='augment')
N('traffic-label',(47,134,43,25),'Traffic-\nlevel:','small',parent='traffic');N('mask-label',(92,147,26,13),'mask','small',parent='traffic');N('topology-label',(138,134,55,25),'Topology-\nlevel:','small',parent='topology')
N('mlp',(369,58,44,26),'MLP','encoder',parent='a');N('h',(335,52,19,17),'$H$','math',parent='encoder',latex=True);N('h-aug',(333,203,20,19),r'$\widetilde H$','math',parent='encoder-aug',latex=True)
N('ground-label',(346,28,73,18),'Ground Truth','small',parent='a');N('shared',(268,128,57,19),'Shared',parent='a');N('bt',(192,92,38,14),r'$B_{t-T}$','math',parent='augment',latex=True)
N('branch-b',(398,123,45,22),'(b)','b',parent='a');N('branch-c',(398,205,45,20),'(c)','d',parent='a')
for key,box,txt in [('lp',(457,58,21,23),r'$\mathcal L_p$'),('ls',(457,123,21,23),r'$\mathcal L_s$'),('lt',(457,202,21,23),r'$\mathcal L_t$'),('joint',(490,125,39,23),r'$\mathcal L_{joint}$')]:N(key,box,txt,'math',parent='a',latex=True)
# Native graph cards and marker motifs. Micro edges are visually traced approximations.
def motif(key,box,points,edges=(),parent='a',radius=2.3):
 n=N(key,box,parent=parent);w,h=box[2:];n['glyph']={'kind':'motif','face_mm':[w*c.k,h*c.k],'vertices':[{'uv':[x/w,y/h],'radius_mm':r*c.k,'shape':shape,'style':style} for x,y,shape,style,r in points],'edges':[{'ends':[i,j],'style':sty} for i,j,sty in edges]};return n
netxy=[(4,5),(18,2),(31,3),(3,18),(18,13),(33,16),(7,32),(22,32),(29,25)]
links=[(0,1),(0,3),(1,4),(1,2),(2,5),(3,4),(3,6),(4,5),(4,8),(6,7),(7,8),(5,8)]
for family,x,y in [('in',124,38),('aug',120,185)]:
 ids=[]
 for z in [2,1,0]:
  key=family+'-card-'+str(z);xx=x-5*z;yy=y+5*z;ids.append(key)
  n=N(key,(xx,yy,40,45),style='card',parent='a');n['glyph']={'kind':'motif','face_mm':[40*c.k,45*c.k],'vertices':[{'uv':[px/40,(py+4)/45],'radius_mm':1.8*c.k,'style':('red' if family=='aug' and i in [1,3,7] and z==0 else 'blue'),'shape':'circle'} for i,(px,py) in enumerate(netxy)],'edges':[{'ends':[i,j],'style':('yellow' if family=='aug' and z==0 else 'graph')} for i,j in links]}
 for i,u in enumerate(ids):
  for v in ids[i+1:]:c.allow(u,v,'Overlapping temporal graph snapshots, drawn rear to front')
N('time',(91,34,22,25),'Time','small',parent='a',text_rotate_deg=57)
c.path([('a',100,60),('a',119,29)])
N('ground-card',(421,30,29,28),style='card',parent='a',glyph={'kind':'motif','face_mm':[29*c.k,28*c.k],'vertices':[{'uv':[x/36,y/36],'radius_mm':1.5*c.k,'style':'lightgreen'} for x,y in netxy],'edges':[{'ends':[i,j],'style':'graph'} for i,j in links]})
motif('mask-points',(94,135,19,10),[(1,4,'circle','blue',2),(7,4,'circle','red',2),(13,4,'circle','blue',2),(4,9,'circle','blue',2)],parent='traffic')
motif('topo-mini',(197,137,20,20),[(x/2,y/2,'circle','blue',1) for x,y in netxy],[(i,j,'yellow') for i,j in links],parent='topology')
# Main flow, sharing, augmentation feedback and three losses.
c.path([('in-card-0',164,71),('encoder',252,71)]);c.path([('encoder',328,71),('mlp',369,71)]);c.path([('mlp',413,71),('lp',458,71)])
c.path([('ground-card',435,58),('a',435,71)],'plain')
c.path([('a',137,94),('augment',137,111)]);c.path([('augment',137,167),('aug-card-0',137,185)]);c.path([('aug-card-0',160,200),('encoder-aug',252,200)])
c.path([('encoder',265,88),('a',265,109),('a',188,109),('augment',188,111)])
c.path([('encoder',296,88),('shared',296,126)],'dotted');c.path([('shared',296,148),('encoder-aug',296,183)],'dotted')
c.path([('encoder',350,71),('a',350,162),('a',369,162)]);c.path([('encoder-aug',328,200),('a',350,200),('a',350,182),('a',369,182)])
c.path([('a',369,155),('a',369,189)],'plain');c.path([('a',369,171),('a',380,171)],'plain');c.path([('a',380,171),('a',380,134),('branch-b',398,134)]);c.path([('a',380,171),('a',380,214),('branch-c',398,214)])
c.edge('loss-s','branch-b.east','ls.west');c.edge('loss-t','branch-c.east','lt.west')
c.path([('lp',478,67),('a',489,67),('a',484,112),('a',484,135)],'plain','cubic');c.path([('lt',478,214),('a',490,214),('a',484,161),('a',484,135)],'plain','cubic');c.path([('a',484,135),('joint',495,135)])
# Spatial four coordinate plots with native markers and explicit axes.
cloud=[(15,16,'circle'),(29,9,'circle'),(41,13,'square'),(12,32,'square'),(22,28,'triangle'),(40,28,'circle'),(24,44,'circle'),(38,43,'square'),(48,38,'triangle')]
for key,x,y in [('h',545,32),('zhat',688,32),('h-tilde',546,155),('z-tilde',688,157)]:
 c.path([('b',x,y+66),('b',x,y)]);c.path([('b',x-7,y+66),('b',x+80,y+66)])
 if key=='h':pts=[(30,16,'circle'),(56,20,'square'),(12,41,'square'),(25,33,'triangle'),(38,34,'square'),(56,34,'circle'),(25,53,'triangle'),(38,53,'circle'),(55,48,'triangle')]
 elif key=='zhat':pts=[(37,16,'circle'),(24,23,'triangle'),(38,28,'circle'),(9,51,'square'),(22,44,'square'),(23,57,'triangle'),(49,44,'square'),(51,57,'triangle'),(61,51,'circle')]
 elif key=='h-tilde':pts=[(18,20,'circle'),(31,10,'circle'),(52,13,'triangle'),(24,37,'square'),(38,28,'circle'),(51,33,'triangle'),(12,52,'square'),(39,49,'square'),(63,49,'triangle')]
 else:pts=[(30,11,'circle'),(25,20,'circle'),(41,16,'circle'),(16,41,'square'),(12,53,'square'),(25,53,'square'),(60,30,'triangle'),(51,37,'triangle'),(61,45,'triangle')]
 motif('scatter-'+key,(x,y,80,66),[(px,py,sh,'blue',5 if sh!='triangle' else 4.6) for px,py,sh in pts],parent='b')
for key,box,txt in [('label-h',(568,102,23,20),'$H$'),('label-zhat',(717,102,23,20),r'$\hat Z$'),('label-ht',(566,224,26,21),r'$\widetilde H$'),('label-zt',(716,224,26,21),r'$\widetilde Z$')]:N(key,box,txt,'math',parent='b',latex=True)
N('predict',(627,47,51,18),'Predict',parent='b');N('cluster',(628,177,51,18),'Cluster',parent='b');N('self-supervise',(688,130,89,20),'Self-supervise',parent='b')
c.path([('b',625,71),('b',680,71)],'wide');c.path([('b',625,200),('b',680,200)],'widegreen');c.line('orange-arrow',2,'#E8BD9B');c.path([('b',727,157),('b',727,118)],'orange-arrow')
for pts in [[(699,180),(725,194),(760,169)],[(725,194),(733,217)]]:c.path([('b',x,y) for x,y in pts],'dash')
# Temporal positive and negative clouds share measured geometry.
for key,y,col in [('pos',35,'blue'),('neg',158,'orange')]:
 N(key+'-cloud',(834,y,71,70),style='cloud',parent='d',role='group')
 pts=[(29,12,'circle'),(19,26,'circle'),(54,19,'circle'),(11,40,'square'),(24,46,'square'),(37,35,'square'),(37,54,'triangle'),(55,48,'triangle'),(55,34,'triangle')]
 motif(key+'-markers',(834,y,71,70),[(x,yy,sh,col,5 if sh!='triangle' else 4.8) for x,yy,sh in pts],parent=key+'-cloud')
N('time-pos',(846,18,45,15),r'\textsf{time }$t$','math',parent='d',latex=True);N('time-neg',(845,230,50,18),r"\textsf{time }$t'$",'math',parent='d',latex=True)
N('fusion',(789,121,43,19),'Fusion','fusion',parent='d');N('fusion-h',(790,88,18,18),'$H$','math',parent='d',latex=True);N('fusion-ht',(810,87,18,19),r'$\widetilde H$','math',parent='d',latex=True)
c.path([('fusion-h',799,106),('fusion',799,121)]);c.path([('fusion-ht',820,106),('fusion',820,121)]);c.path([('fusion',832,130),('d',869,130),('pos-cloud',869,105)])
N('positive',(922,35,82,21),r'\textit{Positive pair}','positive',parent='d',latex=True);N('negative',(915,190,88,20),r'\textit{Negative pair}','negative',parent='d',latex=True)
N('agg-label',(939,123,75,43),r'\textsf{Aggregated}\\\textsf{Embedding}\\\textsf{at time }$t$','math',parent='d',latex=True)
motif('aggregate',(965,113,23,9),[(3,4,'square','blue',3.4),(10,4,'square','blue',3.4),(17,4,'square','blue',3.4)],parent='d')
c.path([('positive',926,43),('pos-cloud',864,43)]);c.path([('negative',917,200),('neg-cloud',892,200)])
c.path([('agg-label',976,189),('agg-label',976,169)])
c.path([('pos-cloud',871,44),('aggregate',976,113)],'dash');c.path([('pos-cloud',872,105),('aggregate',976,116)],'dash');c.path([('positive',976,56),('aggregate',976,114)])
# Known surrounding label/plot bounds can touch; only intentional cases admitted.
s['alignments']=[{'axis':'x','nodes':['encoder','encoder-aug']},{'axis':'x','nodes':['branch-b','branch-c']}]
s['evidence']={'mode':'image-only','input':'download.png','limitations':['Original raster is only 1065 × 285 px. Tiny graph edges and point centers are traced approximations; no claim of exact topology for illustrative micrographs.','All micrographs, markers, axes and labels are native TikZ; model topology is inferred only from the visible diagram.']}
for key,ocr in {'a':'main','b':'spatial','d':'temporal','caption':'caption'}.items():
 next(n for n in s['nodes'] if n['id']==key)['ocr_ids']=['crop-'+ocr+'-ocr-001']
next(n for n in s['nodes'] if n['id']=='caption')['ocr_ids'].append('ocr-001')
s['evidence']['ocr_reconciliation']=['PaddleOCR recognized whole-image caption and 4 crop aggregate blocks. Aggregate coverage is not a claim of complete word recognition.','Corrected upper spatial label from OCR tilde Z to image hat Z, and lower temporal label to time t-prime.','Loss subscripts p/s/t/joint, B_{t-T}, Time, and panel (a)/(b) are supplied by visual image review; not claimed OCR output.']
c.save(Path(args.run)/'scene.json')
