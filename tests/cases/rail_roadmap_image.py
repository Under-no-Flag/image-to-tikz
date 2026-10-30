"""Figure 1-2 traced from the supplied raster only, with real PaddleOCR evidence."""
import argparse,json,re,sys,datetime,statistics
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'skills/image-to-tikz/scripts'))
from scene_builder import Canvas
ap=argparse.ArgumentParser();ap.add_argument('--run',default='outputs/rail-roadmap-image-only-001');a=ap.parse_args();run=Path(a.run)
S=3571/1334
c=Canvas(1815,170);s=c.scene
c.font('body',9.25,family='serif',face='Times New Roman',cjk_face='Songti SC',leading=1.06)
# Initial measured ink widths are replaced by the saved measurement report, if present.
widths={'plain':.66,'flow':.30,'dash':.60}
if (run/'line-measurements.json').exists():
 d=json.loads((run/'line-measurements.json').read_text())
 for role in widths:
  vals=[r['width_pt'] for r in d.get('samples',[]) if r.get('role')==role]
  if vals:widths[role]=statistics.median(vals)
c.line('plain',widths['plain'],arrow='none');c.line('flow',widths['flow']);c.line('dash',widths['dash'],dash='dashed',arrow='none')
s['line_styles']['dash']['dash_pattern_mm']=[1.95,.95]
s['line_styles']['flow'].update(arrow_tip='Triangle',tip_length_mm=1.55,tip_width_mm=1.35)
c.style('box',shape='rectangle',padding_mm=0);c.style('group',shape='rectangle',line='dash',fill_opacity=0)
def N(key,box,text='',parent=None,group=False):
 x,y,w,h=box;n=c.node(key,((x*S)-880,(y*S)-510,w*S,h*S),text,style='group' if group else 'box',parent=parent,**({'role':'group'} if group else {}))
 if text:
  n['ocr_ids']=['crop-control-model-ocr-001' if key.startswith('control-leaf-') else 'ocr-001']
  parts=re.split(r'(YOLO11-DeepSort|YOLOv5|v8|v10|11|head|FCM|SketchUp|MassMotion)',text)
  if len(parts)>1:n['text_runs']=[{'text':v,'weight':'bold' if i%2 else 'normal'} for i,v in enumerate(parts) if v]
 return n
# Frame/node bounds observed in a 1334 px wide view of the 3571 px page.
N('intro',(450,197,433,158),group=True)
N('intro-title',(619,222,97,33),'绪论','intro')
for key,x,txt in [('background',482,'研究背景'),('literature',619,'研究现状'),('content',756,'研究内容')]:N(key,(x,298,97,32),txt,'intro')
N('station',(334,386,665,287),parent='intro',group=True)
N('station-title',(544,405,244,33),'城市轨道交通车站客流与承载能力分析','station')
station=[('facilities',373,'车站设施设备分析',['通行类设施设备','停留类设施设备']),('characteristics',590,'车站客流特性分析',['车站高峰客流特性','车站乘客特性']),('capacity',807,'车站承载能力分析',['车站承载能力影响因素','车站承载能力计算模型'])]
for key,x,title,txts in station:
 N(key,(x,491,153,32),title,'station');N(key+'-group',(x-13,543,179,118),parent='station',group=True)
 for i,txt in enumerate(txts):N(key+'-'+str(i),(x+(2 if key=='capacity' else 0),557+58*i,153,32),txt,key+'-group')
N('recognition',(334,704,665,339),parent='station',group=True)
N('recognition-title',(544,721,244,32),'基于深度学习的车站客流状态识别','recognition')
for key,x,txt in [('image-analysis',360,'基于深度学习的车站客流图像\n分析'),('parameter',577,'车站客流特征参数提取'),('state',794,'车站客流状态识别')]:N(key,(x,807,178,32),txt,'recognition')
for key,x,w in [('image-analysis',350,198),('parameter',567,198),('state',784,198)]:N(key+'-group',(x,854,w,172),parent='recognition',group=True)
for key,y,txt in [('head-dataset',864,'车站乘客head数据集构建'),('yolo-training',924,'YOLOv5、v8、v10、11模型训\n练'),('training-results',984,'模型训练结果对比')]:N(key,(358,y,178,32),txt,'image-analysis-group')
N('tracking',(578,864,178,32),'构建YOLO11-DeepSort\n乘客检测与跟踪模型','parameter-group')
for key,x,txt in [('speed',577,'基于乘\n客质心\n的客流\n速度识\n别'),('density',647,'基于实\n验标记\n的客流\n密度识\n别'),('flow-rate',716,'基于乘\n客撞线\n法的客\n流量识\n别')]:N(key,(x,924,41,92),txt,'parameter-group')
for key,y,txt in [('clustering',864,'通道、楼梯、站台\nFCM聚类'),('state-level',924,'客流状态等级划分'),('state-output',984,'客流状态识别')]:N(key,(797,y,178,32),txt,'state-group')
N('control',(334,1074,665,295),parent='recognition',group=True)
N('control-title',(544,1091,244,32),'城市轨道交通车站分级客流控制模型','control')
N('control-overview',(405,1178,178,32),'车站客流控制概述','control');N('control-model',(735,1178,178,32),'车站客流分级控制模型构建','control')
for i,(x,txt) in enumerate([(378,'客流\n控制\n概念'),(442,'车站\n客流\n控制\n思路'),(504,'车站\n客流\n控制\n原则'),(571,'车站\n客流\n控制\n方法'),(678,'模型\n构建\n思路'),(742,'模型\n假设'),(804,'目标\n函数'),(871,'约束\n条件'),(935,'模型\n求解')]):N('control-leaf-'+str(i),(x,1239,41,93),txt,'control')
N('simulation-input',(351,1411,206,211),parent='control',group=True)
for key,y,txt in [('sketchup',1427,'SketchUp三维建模'),('massmotion',1477,'MassMotion场景定义'),('equipment-parameters',1527,'设施设备参数设置'),('passenger-activity',1577,'乘客活动设置')]:N(key,(377,y,159,32),txt,'simulation-input')
N('simulation',(588,1501,159,32),'轨道车站仿真模型','control')
N('simulation-output',(775,1411,206,211),parent='control',group=True)
for key,y,txt in [('current-analysis',1439,'现状模拟分析'),('control-calculation',1503,'客流控制计算'),('simulation-validation',1562,'仿真验证')]:N(key,(800,y,159,32),txt,'simulation-output')
N('conclusion',(589,1622,159,32),'结论与展望','simulation')
# Explicit source-visible junctions; all coordinates use local anchors.
def P(points,style='flow'):
 c.path([(key,x*S-880,y*S-510) for key,x,y in points],style)
def E(key,a,b):c.edge(key,a,b)
def fork(key,source,children,junction_y):
 sx,sy,sw,sh=c.boxes[source];cx=(sx+880+sw/2)/S;bottom=(sy+510+sh)/S
 P([(source,cx,bottom),(source,cx,junction_y)],'plainflow')
 xs=[]
 for child in children:
  x,y,w,h=c.boxes[child];xx=(x+880+w/2)/S;yy=(y+510)/S;xs.append(xx);P([(source,xx,junction_y),(child,xx,yy)])
 P([(source,min(xs),junction_y),(source,max(xs),junction_y)],'plainflow')
c.line('plainflow',widths['flow'],arrow='none')
fork('intro-fork','intro-title',['background','literature','content'],277)
E('intro-station','intro.south','station.north')
fork('station-fork','station-title',['facilities','characteristics','capacity'],465)
for key,_,_,_ in station:E(key+'-sub',key+'.south',key+'-group.north')
E('station-recognition','station.south','recognition.north')
fork('recognition-fork','recognition-title',['image-analysis','parameter','state'],781)
for key in ['image-analysis','parameter','state']:E(key+'-sub',key+'.south',key+'-group.north')
for u,v in [('head-dataset','yolo-training'),('yolo-training','training-results'),('clustering','state-level'),('state-level','state-output')]:E(u+'-'+v,u+'.south',v+'.north')
fork('tracking-fork','tracking',['speed','density','flow-rate'],910)
E('recognition-control','recognition.south','control.north')
fork('control-fork','control-title',['control-overview','control-model'],1151)
fork('overview-fork','control-overview',['control-leaf-'+str(i) for i in range(4)],1225)
fork('model-fork','control-model',['control-leaf-'+str(i) for i in range(4,9)],1225)
E('control-simulation','control.south','simulation.north')
for u,v in [('sketchup','massmotion'),('massmotion','equipment-parameters'),('equipment-parameters','passenger-activity'),('current-analysis','control-calculation'),('control-calculation','simulation-validation'),('simulation','conclusion')]:E(u+'-'+v,u+'.south',v+'.north')
P([('simulation-input',557,1517),('simulation',588,1517)])
P([('simulation',747,1517),('simulation-output',775,1517)])
s['alignments']=[{'axis':'y','nodes':['background','literature','content']},{'axis':'y','nodes':['facilities','characteristics','capacity']},{'axis':'y','nodes':['image-analysis','parameter','state']},{'axis':'y','nodes':['speed','density','flow-rate']},{'axis':'y','nodes':['control-overview','control-model']},{'axis':'y','nodes':['control-leaf-'+str(i) for i in range(9)]}]
s['evidence']={'mode':'image-only','scope':'Figure 1-2 body only','ocr_reconciliation':['Real PaddleOCR no-layout entire crop plus one bottom-control-label crop. Whole-image aggregate is not a complete text-recognition rate.','Corrected 绪论 (OCR 结论), 质心 (OCR 质量), 实验标记 and 撞线 based on native-resolution image crops. Removed spurious duplicated OCR phrases.','Whole-image OCR omitted the lower recognition 客流状态识别 and the five control-model leaf labels; retained source-visible text and one supplemental crop.','English tokens head, YOLOv5, v8, v10, 11, YOLO11-DeepSort, FCM, SketchUp and MassMotion are bold; Chinese uses normal Songti, avoiding blanket bold.'],'line_width_basis':'Black-ink-equivalent width from source pixel profiles, converted at 170 mm, not a uniquely recovered original stroke. Separate FWHM/gray profiles retained; blurred PNG cannot identify geometry and gray level uniquely.','node_inventory':{'text_nodes':sum(bool(n.get('text')) for n in s['nodes']),'group_nodes':sum(n.get('role')=='group' for n in s['nodes']),'edge_records':len(s['edges']),'component_paths':len(s['component_paths'])},'visual_font_basis':'Chinese glyph height about 32-35 source px at 1815 px diagram width, approximately 8.5-9.3 pt at 170 mm. Same body level 9.25 pt; Latin words use source-visible bold runs.'}
def round_numbers(v):
 if isinstance(v,float):return round(v,6)
 if isinstance(v,list):return [round_numbers(x) for x in v]
 if isinstance(v,dict):return {k:round_numbers(x) for k,x in v.items()}
 return v
c.scene=round_numbers(s)
c.save(run/'scene.json')
(run/'prebuild-inventory.json').write_text(json.dumps({'recorded_at':datetime.datetime.now().astimezone().isoformat(),**s['evidence'],'fonts':s['fonts'],'line_styles':s['line_styles']},ensure_ascii=False,indent=2))
print(s['evidence']['node_inventory'])
