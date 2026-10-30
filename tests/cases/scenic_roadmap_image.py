"""Scenic roadmap reconstructed from one raster + real PaddleOCR, no source TeX."""
import sys,json,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'skills/image-to-tikz/scripts'))
from scene_builder import Canvas
p=argparse.ArgumentParser();p.add_argument('--run',default='outputs/scenic-roadmap-image-only-001');a=p.parse_args();run=Path(a.run)
c=Canvas(1404,170);s=c.scene;N=c.node
for key,pt in [('body',8.4),('header',10.1),('stage',9.6),('small',8.1),('caption',10.5),('latin',8.0)]:c.font(key,pt,family='serif',face='Times New Roman',cjk_face='Songti SC',leading=1.5 if key=='stage' else 1.15,weight='bold' if key=='caption' else 'normal')
# Line values are source stroke pixel estimates converted with 170/1404 mm/px.
c.line('plain',1.17,arrow='none');c.line('flow',1.17);c.line('frame',1.09,'#64666A','dashed','none');c.line('broad-outline',1.25,arrow='none');c.line('box',1.24,arrow='none')
s['line_styles']['frame']['dash_pattern_mm']=[1.57,1.21]
s['line_styles']['flow'].update(arrow_tip='Triangle',tip_length_mm=2.0,tip_width_mm=1.8)
for k,f in [('label','body'),('small','small'),('caption','caption')]:c.style(k,shape='text',font=f)
c.style('frame',shape='rectangle',line='frame',fill_opacity=0)
colors={'header':'#DDE FCE'.replace(' ',''),'stage-green':'#87CCBB','stage-blue':'#7B90CD','stage-purple':'#A185C4','green':'#BDD FD5'.replace(' ',''),'blue':'#CDD5E9','purple':'#D4BFDF','scheme':'#F4DBCA','method':'#C9EAF0'}
for key,col in colors.items():
 c.style(key,col,shape='rounded' if key in ['header','stage-green','stage-blue','stage-purple','method'] else 'rectangle',font='header' if key=='header' else 'stage' if key.startswith('stage-') else 'body',corner_mm=(3.7 if key.startswith('stage-') else 1.9 if key=='method' else 1.1))
c.style('method-latin',colors['method'],shape='rounded',font='latin',corner_mm=2.2)
c.style('diamond',colors['scheme'],shape='diamond',text_width_ratio=.52,font='stage')
for sty in s['node_styles'].values():
 if sty['shape']!='text' and sty['line']=='plain':sty['line']='box'
for key,col in [('green-root','#ADDBCF'),('blue-root','#AEBBDF'),('purple-root','#B499CE')]:c.style(key,col,shape='rectangle',line='box')
# Three primary columns and three research content sections; original dashed boundaries.
N('path-frame',(82,125,220,1456),style='frame',role='group')
N('content-survey-frame',(353,126,675,449),style='frame',role='group',parent='path-frame')
N('content-simulation-frame',(353,623,675,502),style='frame',role='group',parent='content-survey-frame')
N('content-optimization-frame',(353,1312,675,272),style='frame',role='group',parent='content-simulation-frame')
N('methods-frame',(1089,125,194,1460),style='frame',role='group',parent='path-frame')
for key,box,txt in [('path-title',(80,30,222,64),'研究路径'),('content-title',(355,30,675,64),'研究内容'),('method-title',(1088,30,194,64),'研究方法')]:N(key,box,txt,'header',parent='path-frame')
N('phase-survey',(96,342,186,139),'滨水景区\n调研实测','stage-green',parent='path-frame')
N('phase-simulation',(96,823,186,173),'景区人流\n模拟仿真\n分析','stage-blue',parent='phase-survey')
N('phase-optimization',(96,1349,186,217),'基于仿真\n模拟定制\n景区优化\n方案','stage-purple',parent='phase-simulation')
# Central research components, peer roles share dimensions, font and line styles.
rows=[('site-survey',(424,202,206,56),'滨水景区实测','green'),('crowd-survey',(424,381,206,56),'景区人流实测','green'),('time-selection',(424,506,206,56),'景区时段选取','green'),('fengqiao',(717,146,225,56),'枫桥景区建模','green'),('panmen',(717,202,225,54),'盘门景区建模','green'),('shantang',(717,256,225,56),'山塘街景区建模','green'),('instant-flow',(717,326,225,54),'瞬时间人流量','green'),('route-preference',(717,380,225,54),'游客路径偏好','green'),('dwell-time',(717,434,225,55),'各空间停留时长','green'),('six-periods',(717,506,225,55),'一天中六个时段','green'),('simulation-model',(424,710,235,55),'仿真模拟模型建立','blue'),('scene-model',(717,634,241,57),'景区场景模型构建','blue'),('agent-parameters',(717,710,237,56),'智能体参数设定','blue'),('activity-pattern',(717,766,237,53),'游客活动模式设定','blue'),('congestion-analysis',(424,865,237,56),'景区空间拥堵分析','blue'),('utilization-analysis',(425,1006,258,56),'景区空间利用率分析','blue'),('mean-density',(717,838,225,56),'平均密度图','blue'),('max-density',(717,894,225,54),'最大密度图','blue'),('group-count',(717,948,225,55),'群体计数图','blue'),('occupancy-time',(717,1003,225,54),'占用时间地图','blue'),('individual-count',(717,1057,225,55),'个体计数 \\ 路线图','blue'),('original-plan',(807,1149,143,55),'原方案','scheme'),('optimized-plan',(807,1217,143,55),'优化方案','scheme'),('revise-plan',(475,1322,208,55),'修订优化方案','stage-purple'),('spatial-plan',(475,1425,208,57),'空间优化方案','stage-purple'),('transition-space',(717,1344,225,55),'营造过渡空间','purple'),('new-exits',(717,1399,225,54),'新增出入口','purple'),('widen-paths',(717,1453,225,54),'消障、拓宽道路','purple'),('new-routes',(717,1507,225,55),'新增路径及景点','purple')]
for key,box,txt,style in rows:
 if style=='stage-purple':style='purple-root'
 if key in ['site-survey','crowd-survey','time-selection']:style='green-root'
 if key in ['simulation-model','congestion-analysis','utilization-analysis']:style='blue-root'
 N(key,box,txt,style,parent='content-survey-frame' if box[1]<600 else 'content-simulation-frame' if box[1]<1130 else 'content-optimization-frame')
N('representatives',(589,143,80,55),'遴选典\n型代表','small',parent='site-survey')
c.style('comparison-label',shape='text',font='stage')
N('comparison-bg',(465,1162,221,91),style='label',parent='content-optimization-frame',role='group',glyph={'kind':'polygon','face_mm':[221*c.k,91*c.k],'points_uv':[[0,.5],[.5,0],[1,.5],[.5,1]],'face_style':'scheme','outline_style':'box'})
N('comparison',(465,1162,221,91),'比较分析','comparison-label',parent='comparison-bg')
N('effective',(316,1173,61,34),'有效','small',parent='comparison')
N('ineffective',(446,1266,119,33),'无效/低效','small',parent='comparison')
N('cycle-label',(360,1362,61,80),'循环\n计算','small',parent='revise-plan')
# Research methods: only actually visible directional links get arrowheads.
methods=[('base-drawings',(1107,155,159,98),'基础平立\n剖图纸','method'),('video',(1107,303,159,56),'视频录像','method'),('observe',(1107,365,159,55),'行为观察','method'),('track',(1107,425,159,55),'跟踪记录','method'),('sketchup',(1107,624,159,99),'SketchUp\n模型导入','method-latin'),('massmotion',(1098,863,179,126),'MassMotion\n行为仿真模\n拟分析','method-latin'),('hypothesis',(1107,1156,159,55),'假设方案','method'),('apply',(1107,1233,159,56),'代入模型','method'),('simulate',(1107,1308,159,57),'模拟仿真','method'),('validate',(1107,1384,159,56),'验证成效','method'),('method-optimize',(1107,1463,159,57),'优化方案','method')]
for key,box,txt,sty in methods:N(key,box,txt,sty,parent='methods-frame')
N('caption',(524,1612,315,39),'图 4　研究技术路线','caption',parent='path-frame',text_runs=[{'text':'图 ','weight':'bold'},{'text':'4','weight':'normal'},{'text':'　研究技术路线','weight':'bold'}])
# Thick arrows are native closed polygons with independently measured 3 px outlines.
def polygon(key,pts,fill,parent):
 x0=min(p[0] for p in pts);y0=min(p[1] for p in pts);w=max(p[0] for p in pts)-x0;h=max(p[1] for p in pts)-y0
 n=N(key,(x0,y0,w,h),style='label',parent=parent)
 n['glyph']={'kind':'polygon','face_mm':[w*c.k,h*c.k],'points_uv':[[(x-x0)/w,(y-y0)/h] for x,y in pts],'face_style':fill,'outline_style':'broad-outline'}
for key,y,col,par in [('survey',411,'green','phase-survey'),('simulation',893,'blue','phase-simulation'),('optimization',1454,'purple','phase-optimization')]:polygon('arrow-'+key,[(301,y-9),(338,y-9),(338,y-30),(354,y),(338,y+31),(338,y+10),(301,y+10)],col,par)
for key,y,col in [('survey',340,'green'),('simulation',871,'blue'),('optimization',1444,'purple')]:polygon('method-arrow-'+key,[(1088,y-14),(1047,y-14),(1047,y-49),(1027,y),(1047,y+48),(1047,y+14),(1088,y+14)],col,'methods-frame')
polygon('survey-to-simulation',[(664,575),(695,575),(695,610),(733,610),(680,625),(626,610),(664,610)],'green','content-survey-frame')
polygon('simulation-to-optimization',[(717,1125),(747,1125),(747,1280),(785,1280),(732,1312),(680,1280),(717,1280)],'blue','content-simulation-frame')
# Explicit paths: endpoints are node-relative; shared trunk junctions do not invent edges.
def P(pts,style='plain',root='path-frame'):c.path([(root,x,y) for x,y in pts],style)
# Left research path and per-phase fanout.
c.edge('survey-simulation','phase-survey.south','phase-simulation.north');c.edge('simulation-optimization','phase-simulation.south','phase-optimization.north')
P([(282,411),(301,411)]);P([(354,411),(384,411)]);P([(384,230),(384,534)])
for y in [230,410,534]:P([(384,y),(424,y)],'flow')
P([(282,909),(301,909),(301,893)]);P([(354,893),(384,893)]);P([(384,738),(384,1035)])
for y in [738,893,1035]:P([(384,y),(424,y)],'flow')
P([(282,1454),(301,1454)]);P([(354,1454),(475,1454)],'flow')
# Survey roots to leaves, including explicit left branching buses.
P([(630,230),(717,230)]);P([(672,174),(672,285)]);P([(672,174),(717,174)]);P([(672,285),(717,285)])
P([(630,409),(717,409)]);P([(672,352),(672,464)]);P([(672,352),(717,352)]);P([(672,464),(717,464)])
P([(630,534),(717,534)])
# Two separate survey-feedback trunks, preserving original arrow endpoints.
P([(942,174),(1015,174),(1015,662),(958,662)],'flow');P([(942,230),(1015,230)]);P([(942,285),(1015,285)])
P([(942,352),(997,352),(997,765),(972,765)],'flow');P([(942,409),(997,409)]);P([(942,464),(997,464)]);P([(954,737),(972,737),(972,793),(954,793)])
# Simulation roots and output trees.
P([(659,737),(717,737)]);P([(672,659),(672,793)]);P([(672,659),(717,659)]);P([(672,793),(717,793)])
P([(661,893),(672,893)]);P([(672,866),(672,923)]);P([(672,866),(717,866)]);P([(672,923),(717,923)])
P([(683,1033),(717,1033)]);P([(695,977),(695,1089)]);P([(695,977),(717,977)]);P([(695,1089),(717,1089)])
P([(971,867),(971,1088)])
for y in [867,922,976,1033,1088]:P([(942,y),(971,y)])
P([(971,976),(999,976),(999,1175),(950,1175)],'flow')
# Both schemes feed comparison leftwards. Comparison's two outcome branches.
P([(807,1175),(779,1175),(779,1245),(807,1245)])
P([(779,1210),(686,1210)],'flow');P([(465,1207),(188,1207)],'flow')
c.edge('comparison-revise','comparison.south','revise-plan.north')
P([(475,1348),(422,1348),(422,1454)],'flow')
# Four spatial optimization measures and their visible unheaded feedback loop.
P([(683,1453),(695,1453)]);P([(695,1368),(695,1539)])
for y in [1368,1427,1483,1539]:P([(695,y),(717,y)])
P([(971,1368),(971,1539)])
for y in [1368,1427,1483,1539]:P([(942,y),(971,y)])
P([(971,1453),(999,1453),(999,1245),(950,1245)])
# Right methods links: intentional whitespace between video/observe/track.
for fr,to in [('base-drawings','video'),('track','sketchup'),('sketchup','massmotion'),('massmotion','hypothesis')]:c.edge(fr+'-'+to,fr+'.south',to+'.north')
for fr,to in [('hypothesis','apply'),('apply','simulate'),('simulate','validate'),('validate','method-optimize')]:c.edge(fr+'-'+to,fr+'.south',to+'.north','plain')
for pair in [('path-frame','arrow-survey'),('path-frame','arrow-simulation'),('path-frame','arrow-optimization'),('content-survey-frame','arrow-survey'),('content-survey-frame','method-arrow-survey'),('content-simulation-frame','arrow-simulation'),('content-simulation-frame','method-arrow-simulation'),('content-simulation-frame','survey-to-simulation'),('content-optimization-frame','arrow-optimization'),('content-optimization-frame','method-arrow-optimization')]:c.allow(*pair,'Source thick arrow intentionally crosses dashed section boundary.')
c.allow('comparison-bg','simulation-to-optimization','Bounding boxes overlap, but the diamond vertex is left of the arrow shaft.')
c.allow('comparison','simulation-to-optimization','Polygon bounding boxes intersect, but visible diamond and arrow shaft do not overlap; comparison connector crosses arrow exactly as in source.')
s['alignments']=[{'axis':'x','nodes':['phase-survey','phase-simulation','phase-optimization']},{'axis':'x','nodes':['site-survey','crowd-survey','time-selection']},{'axis':'x','nodes':['fengqiao','panmen','shantang','instant-flow','route-preference','dwell-time','six-periods']},{'axis':'x','nodes':['mean-density','max-density','group-count','occupancy-time','individual-count','transition-space','new-exits','widen-paths','new-routes']}]
s['evidence']={'mode':'image-only','input':'Snipaste_20261030_232726.png','native_structure':'All text, frames, polygons, arrows and paths are editable native TikZ; no raster assets.','line_width_conversion':{'source_width_px':1404,'target_width_mm':170,'pt_per_source_px':170/1404*72.27/25.4,'measurement_file':'stroke-measurements.json','ordinary_measured_px_range':[3.3102,3.4798],'ordinary_pt':1.17,'box_pt':1.24,'frame_pt':1.09,'broad_outline_pt':1.25},'font_roles':'Songti SC normal for Chinese; only caption bold. Times New Roman Latin. Body 8.4 pt, header 10.1 pt, phase 9.6 pt, annotation 8.1 pt, caption 10.5 pt.'}
if (run/'ocr.json').exists():
 ocr=json.loads((run/'ocr.json').read_text())
 for n in s['nodes']:
  if n['id']=='spatial-plan':n['ocr_ids']=['ocr-001']
  if n['id']=='caption':n['ocr_ids']=['crop-optimization-ocr-001']
  if n['id'] in ['fengqiao','panmen','shantang','instant-flow','route-preference','dwell-time','six-periods']:n['ocr_ids']=['crop-critical-nolayout-ocr-001']
 s['evidence']['ocr_reconciliation']=['Seven real PaddleOCR requests yielded only three blocks: whole-image no-layout recognized 空间优化方案; 5 layout-enabled semantic crops yielded 4 zero-text results and caption only; final tight no-layout crop recognized 7 upper-column labels including 枫桥/盘门/山塘街. All remaining labels, including 营造过渡空间, are manual raster transcriptions. This is incomplete OCR coverage; 3/3 mapped blocks is not full text recognition.']
c.save(run/'scene.json')
