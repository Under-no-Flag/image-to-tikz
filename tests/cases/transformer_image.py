"""Image-only reconstruction observations; authored before source inspection."""
import sys,json,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'skills/image-to-tikz/scripts'))
from scene_builder import Canvas
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--run",default="outputs/transformer-image-only-001");args=parser.parse_args()
c=Canvas(2048,240);s=c.scene
for key,pt,kw in [('body',9.0,{}),('small',8.5,{}),('heading',10,{'weight':'bold'}),('zoom',9,{'color':'#888888'})]:c.font(key,pt,**kw)
c.font('symbol',7.5)
c.line('plain',.35,arrow='none');c.line('flow',.35);c.line('dots',.3,'#555555','dotted','none');c.line('dash',.35,dash='dashed',arrow='none');c.line('zoom',.35,'#777777','dotted','none')
c.style('label',shape='text');c.style('heading',shape='text',font='heading');c.style('zoomlabel',shape='text',font='zoom')
for key,col in [('embedding','#F6D7D7'),('attention','#FCE9D5'),('feed','#D7D5F6'),('norm','#DAEFDA'),('linear','#E5E5EF'),('softmax','#E5EBE5'),('scaled','#CCCBDD')]:c.style(key,col)
for key,col in [('encoder','#E3F2FF'),('decoder','#E5F5E5'),('preprocessing','#FFF2E5')]:c.style(key,col,shape='rectangle',line='dots')
c.style('repeat',shape='rectangle',line='dash',fill_opacity=0);c.style('detail',shape='rectangle',line='dots',fill_opacity=0);c.style('headlabel',shape='rectangle',line='dots');c.style('sum','#FFF2E5',shape='ellipse',font='symbol');c.style('ghostlinear','#E5E5EF',opacity=.5);c.style('ghostscaled','#CCCBDD',opacity=.5)
N=c.node
N('pre',(248,867,782,324),style='preprocessing',role='group');N('enc',(248,416,393,442),style='encoder',role='group',parent='pre');N('dec',(660,155,370,703),style='decoder',role='group',parent='pre')
N('enc-repeat',(345,480,278,370),style='repeat',role='group',parent='enc');N('dec-repeat',(669,237,278,578),style='repeat',role='group',parent='dec')
N('detail-heads',(1097,115,510,602),style='detail',role='group',parent='dec');N('detail-dot',(1695,581,343,556),style='detail',role='group',parent='detail-heads')
N('enc-title',(254,420,150,35),'Encoder','heading',parent='enc');N('dec-title',(902,157,126,35),'Decoder','heading',parent='dec');N('pre-title',(420,1155,440,32),'Preprocessing stages','heading',parent='pre')
blocks=[('emb-e',(392,962,185,74),'Input\nEmbedding','embedding','pre'),('sum-e',(469,886,30,30),'+','sum','pre'),('mha-e',(392,721,185,74),'Multi-Head\nAttention','attention','enc'),('norm-e-one',(392,675,185,37),'Add & Norm','norm','enc'),('ff-e',(392,545,185,74),'Feed\nForward','feed','enc'),('norm-e-two',(392,499,185,37),'Add & Norm','norm','enc'),('emb-d',(715,962,185,74),'Output\nEmbedding','embedding','pre'),('sum-d',(793,886,30,30),'+','sum','pre'),('mha-d',(715,693,185,102),'Masked\nMulti-Head\nAttention','attention','dec'),('norm-d-one',(715,647,185,37),'Add & Norm','norm','dec'),('cross-d',(715,480,185,74),'Multi-Head\nAttention','attention','dec'),('norm-d-two',(715,434,185,37),'Add & Norm','norm','dec'),('ff-d',(715,305,185,74),'Feed\nForward','feed','dec'),('norm-d-three',(715,258,185,37),'Add & Norm','norm','dec'),('linear-d',(715,175,185,37),'Linear','linear','dec'),('softmax-d',(715,91,185,37),'Softmax','softmax','dec')]
for key,box,label,style,parent in blocks:N(key,box,label,style,parent=parent)
for key,box,label,parent in [('inputs',(420,1077,130,40),'Inputs','emb-e'),('outputs',(704,1077,210,76),'Outputs\n(shifted right)','emb-d'),('prob',(700,0,215,65),'Output\nprobabilities','softmax-d'),('pos-e-label',(249,873,135,60),'Positional\nEncoding','pre'),('pos-d-label',(906,873,124,60),'Positional\nEncoding','pre')]:N(key,box,label,parent=parent)
for key,box in [('sine-e',(386,874,56,56)),('sine-d',(850,874,56,56))]:
 N(key,box,'','sum',parent='pre');x,y,w,h=box
 c.path([(key,x,y+h*.5),(key,x+w*.4,y),(key,x+w*.6,y+h),(key,x+w,y+h*.5)],'plain','cubic')
for key,a,b in [('pos-e','sine-e.east','sum-e.west'),('pos-d','sine-d.west','sum-d.east')]:c.edge(key,a,b,'plain')
for prefix,chain in [('enc',['inputs','emb-e','sum-e','mha-e','norm-e-one','ff-e','norm-e-two']),('dec',['outputs','emb-d','sum-d','mha-d','norm-d-one','cross-d','norm-d-two','ff-d','norm-d-three','linear-d','softmax-d','prob'])]:
 for i,(a,b) in enumerate(zip(chain,chain[1:])):c.edge(prefix+'-chain-'+str(i),a+'.north',b+'.south')
for key,pts in [('er1',[(484,831),(368,831),(368,693),(392,693)]),('er2',[(484,647),(368,647),(368,517),(392,517)])]:c.path([('enc',x,y) for x,y in pts])
for pts in [[(808,831),(923,831),(923,665),(900,665)],[(808,600),(923,600),(923,452),(900,452)],[(808,406),(923,406),(923,276),(900,276)]]:c.path([('dec',x,y) for x,y in pts])
c.path([('norm-e-two',484,499),('enc',484,452),('enc',650,452),('cross-d',650,591),('cross-d',744,591),('cross-d',744,554)])
N('repeat-e',(280,643,50,43),r'$n\times$',parent='enc',latex=True);N('repeat-d',(958,744,60,43),r'$\times n$',parent='dec',latex=True)
N('note-e',(0,580,180,70),'= 6 in the\noriginal paper',parent='enc');N('note-d',(1104,774,185,70),'= 6 in the\noriginal paper',parent='dec')
c.path([('note-e',187,619),('note-e',233,619),('repeat-e',231,666),('repeat-e',278,666)],kind='cubic')
c.path([('note-d',1104,813),('note-d',1057,813),('repeat-d',1062,766),('repeat-d',1014,766)],kind='cubic')
# Multi-head repeated visible layers, drawn rear to front.
for family,x in [('v',1138),('k',1282),('q',1426)]:
 for i in [2,1,0]:
  N('linear-'+family+'-'+str(i),(x+14*i,535-14*i,102,37),'Linear','ghostlinear' if i else 'linear',parent='detail-heads',occlusion_group='heads-'+family)
 N('input-'+family,(x+25,658,52,39),'$'+family.upper()+'$',parent='detail-heads',latex=True)
 c.edge('head-input-'+family,'input-'+family+'.north','linear-'+family+'-0.south')
for i in [2,1,0]:N('attn-head-'+str(i),(1134+14*i,369-14*i,398,74),'Scaled Dot-Product\nAttention','ghostscaled' if i else 'scaled',parent='detail-heads',occlusion_group='heads-attn')
for family,x in [('v',1189),('k',1333),('q',1477)]:c.path([('linear-'+family+'-0',x,535),('attn-head-0',x,443)])
N('concat',(1282,268,102,37),'Concat','norm',parent='detail-heads');N('head-linear',(1282,185,102,37),'Linear','linear',parent='detail-heads');N('head-title',(1213,78,277,74),'Multi-head attention','headlabel',parent='detail-heads')
for i,(a,b) in enumerate([('attn-head-0','concat'),('concat','head-linear')]):c.edge('head-chain-'+str(i),a+'.north',b+'.south')
c.path([('head-linear',1333,185),('head-title',1333,152)])
# Scaled dot-product detail.
for key,box,label,style in [('dot-product',(1737,980,166,37),'MatMul','linear'),('scale',(1737,896,166,37),'Scale','norm'),('mask',(1737,813,166,37),'Mask (opt.)','embedding'),('softmax',(1737,730,166,37),'Softmax','softmax'),('weighted',(1804,647,166,37),'MatMul','linear')]:N(key,box,label,style,parent='detail-dot')
N('dot-title',(1728,545,277,74),'Scaled dot-product\nattention','headlabel',parent='detail-dot')
for key,x in [('q',1776),('k',1865),('v',1953)]:N('dot-'+key,(x-20,1074,40,40),'$'+key.upper()+'$',parent='detail-dot',latex=True)
for key,x in [('q',1776),('k',1865)]:c.path([('dot-'+key,x,1070),('dot-product',x,1017)])
c.path([('dot-v',1953,1070),('weighted',1953,684)])
for i,(a,b) in enumerate([('dot-product','scale'),('scale','mask'),('mask','softmax')]):c.edge('dot-chain-'+str(i),a+'.north',b+'.south')
c.path([('softmax',1820,730),('weighted',1820,684)])
c.path([('cross-d',900,517),('cross-d',984,517),('detail-heads',1024,415),('detail-heads',1097,415)],'zoom','cubic')
c.path([('attn-head-0',1532,411),('detail-heads',1640,411),('detail-dot',1560,858),('detail-dot',1695,858)],'zoom','cubic')
N('zoom-one',(963,405,102,92),'Zoom-in!','zoomlabel',parent='detail-heads',text_rotate_deg=42);N('zoom-two',(1609,635,60,145),'Zoom-in!','zoomlabel',parent='detail-dot',text_rotate_deg=-83)
# Source-supported overlap only: repeated head layers and white group-title cutouts.
for group in ['heads-v','heads-k','heads-q','heads-attn']:
 ids=[n['id'] for n in s['nodes'] if n.get('occlusion_group')==group]
 for i,a in enumerate(ids):
  for b in ids[i+1:]:c.allow(a,b,'Visible overlapping attention heads; rear layers intentionally partially occluded')
for a,b in [('head-title','detail-heads'),('dot-title','detail-dot')]:c.allow(a,b,'White title plate interrupts dotted group border, as in reference image')
c.allow('dec','zoom-one','Rotated diagonal zoom label has an axis-aligned bounding rectangle across an empty group corner; actual glyph ink is outside the group')
s['evidence']={'mode':'image-only','input':'06-transformer.png','notes':['Observed 3 visible layers per head stack; do not infer actual model head count.','Residual, cross-attention and expansion connectors traced from raster; source TeX not read.']}
s['alignments']=[{'axis':'x','nodes':['emb-e','mha-e','norm-e-one','ff-e','norm-e-two']},{'axis':'x','nodes':['emb-d','mha-d','norm-d-one','cross-d','norm-d-two','ff-d','norm-d-three','linear-d','softmax-d']}]
for key,ocr in {'enc':'encoder','dec':'decoder','pre':'preprocess','detail-heads':'heads','detail-dot':'dot'}.items():
 next(n for n in s['nodes'] if n['id']==key)['ocr_ids']=['crop-'+ocr+'-ocr-ocr-001']
s['evidence']['ocr_reconciliation']=['5 panel-level aggregate OCR blocks retained, not treated as per-label bounding boxes or size measurements.','Manual image checks supply Output probabilities, duplicate Output Embedding/Positional Encoding, inputs, V/K/Q and n=6 notes missing or garbled in OCR.','Ghost head text checked visually; 3 visible layers do not imply 3 actual heads.']
c.save(Path(args.run)/'scene.json')
