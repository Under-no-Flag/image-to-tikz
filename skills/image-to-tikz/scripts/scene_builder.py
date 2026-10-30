"""Author pixel observations as a relative, physical-unit scene (no recognition)."""
import json
from pathlib import Path
class Canvas:
 def __init__(self,width_px,width_mm):
  self.k=width_mm/width_px;self.boxes={}
  self.scene={'schema_version':1,'fonts':{},'line_styles':{},'node_styles':{},'sizes':{},'nodes':[],'edges':[],'containers':[],'alignments':[],'allowed_overlaps':[],'component_paths':[],'unresolved':[],'layout_tokens_mm':{}}
 def font(self,key,pt,**kw):self.scene['fonts'][key]={'size_pt':pt,'weight':'normal','color':'#000000',**kw}
 def line(self,key,width=.35,color='#000000',dash='solid',arrow='end'):self.scene['line_styles'][key]={'width_pt':width,'color':color,'dash':dash,'arrow':arrow}
 def style(self,key,fill='#FFFFFF',shape='rounded',line='plain',font='body',**kw):self.scene['node_styles'][key]={'shape':shape,'line':line,'font':font,'fill':fill,'padding_mm':.05,'corner_mm':.4,**kw}
 def node(self,key,box,text='',style='label',parent=None,latex=False,**kw):
  x,y,w,h=box;self.boxes[key]=box
  # Identical peer dimensions share a size token.
  dims=[round(w*self.k,6),round(h*self.k,6)]
  size=next((s for s,v in self.scene['sizes'].items() if v==dims),key)
  self.scene['sizes'][size]=dims
  n={'id':key,'style':style,'size':size,**kw}
  if latex:n.update(latex=text,latex_reviewed=True)
  else:n['text']=text
  if not self.scene['nodes']:n['at_mm']=[(x+w/2)*self.k,(y+h/2)*self.k]
  else:
   parent=parent or self.scene['nodes'][0]['id'];a,b,c,d=self.boxes[parent]
   n['relative']={'of':parent,'dx':round((x+w/2-a-c/2)*self.k,6),'dy':round((y+h/2-b-d/2)*self.k,6)}
  self.scene['nodes'].append(n);return n
 def edge(self,key,a,b,style='flow',route='straight',**kw):self.scene['edges'].append({'id':key,'from':a,'to':b,'style':style,'route':route,**kw})
 def pt(self,key,x,y):
  a,b,w,h=self.boxes[key];return {'of':key,'uv':[(x-a)/w,(y-b)/h]}
 def path(self,points,style='flow',kind='polyline',closed=False):self.scene['component_paths'].append({'style':style,'kind':kind,'closed':closed,'points':[self.pt(*p) for p in points]})
 def allow(self,a,b,reason):self.scene['allowed_overlaps'].append({'nodes':[a,b],'reason':reason})
 def save(self,path):
  path=Path(path)
  if (path.parent/'image-only-frozen').exists(): raise ValueError('Frozen reconstruction: create a new run before editing')
  path.write_text(json.dumps(self.scene,ensure_ascii=False,indent=2)+'\n')
