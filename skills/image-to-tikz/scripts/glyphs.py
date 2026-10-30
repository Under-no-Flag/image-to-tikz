"""Parametric network glyphs. Dimensions describe visible geometry, not tensor counts."""
import math
from tex_numbers import decimal
import advanced_glyphs

def dimensions(g):
    w,h=g['face_mm']
    if min(w,h)<=0 or not all(math.isfinite(v) for v in (w,h)): raise ValueError('Invalid face dimensions')
    if g['kind'] in advanced_glyphs.KINDS: return advanced_glyphs.dimensions(g)
    if g['kind']=='motif': return w,h
    if g['kind']=='feature-stack':
        n=g['visible_count'];dx,dy=g['step_mm']
        if type(n) is not int or not 1<=n<=256 or min(dx,dy)<0: raise ValueError('Invalid stack count/step')
        return w+(n-1)*dx,h+(n-1)*dy
    if g['kind']=='slab':
        if g['shear_mm']<0: raise ValueError('Negative slab shear unsupported')
        return w+g['shear_mm'],h
    raise ValueError('Unknown network glyph')

def validate_glyph(node,scene):
    g=node['glyph'];expected=dimensions(g)
    if any(abs(a-b)>.01 for a,b in zip(expected,scene['sizes'][node['size']])): raise ValueError('Glyph bounding size must equal its derived geometry: '+node['id'])
    if g['kind'] in advanced_glyphs.KINDS:
        advanced_glyphs.validate(g,scene)
        return
    if g['kind']=='motif':
        validate_motif(g,scene)
        return
    for key in ('light_style','dark_style'):
        if g[key] not in scene['node_styles']: raise ValueError('Unknown glyph palette style')

MACROS=r'''
% Local geometry: x right, y down; one macro call per semantic component.
\newcommand{\FeatureStack}[8]{%
\begin{scope}[shift={(#1.north west)},x=1mm,y=-1mm]
\pgfmathtruncatemacro{\lastface}{#4-1}
\foreach \i in {0,...,\lastface}{%
\ifodd\i\def\facecolor{#8}\else\def\facecolor{#7}\fi
\fill[\facecolor] ({\i*#5},{\i*#6}) rectangle ++(#2,#3);
}
\end{scope}}
\newcommand{\TensorSlab}[5]{%
\begin{scope}[shift={(#1.north west)},x=1mm,y=-1mm]
\fill[#5] (0,0)--(#2,0)--({#2+#4},#3)--(#4,#3)--cycle;
\end{scope}}
'''

def draw(node,scene,color):
    g=node['glyph'];w,h=g['face_mm']; key=node['id']
    if g['kind'] in advanced_glyphs.KINDS: return advanced_glyphs.draw(node,scene,color)
    if g['kind']=='motif': return draw_motif(node,scene,color)
    light=color(scene['node_styles'][g['light_style']]['fill']);dark=color(scene['node_styles'][g['dark_style']]['fill'])
    if g['kind']=='feature-stack':
        dx,dy=g['step_mm']
        return r'\FeatureStack{%s}{%g}{%g}{%d}{%g}{%g}{%s}{%s}'%(key,w,h,g['visible_count'],dx,dy,light,dark)
    return r'\TensorSlab{%s}{%g}{%g}{%g}{%s}'%(key,w,h,g['shear_mm'],dark)

def point(p,scene):
    node=next(n for n in scene['nodes'] if n['id']==p['of']);w,h=scene['sizes'][node['size']];u,v=p['uv']
    return r'($(%s.west |- %s.north)+(%smm,%smm)$)'%(node['id'],node['id'],decimal(u*w),decimal(-v*h))

def validate_paths(scene):
    ids={n['id'] for n in scene['nodes']}
    for path in scene.get('component_paths',[]):
        if path['style'] not in scene['line_styles'] or len(path['points'])<2: raise ValueError('Invalid component path')
        if path.get('kind','polyline') not in ('polyline','cubic'): raise ValueError('Unknown path kind')
        if path.get('kind')=='cubic' and len(path['points'])!=4: raise ValueError('Cubic requires start, two controls, end')
        for p in path['points']:
            if p['of'] not in ids or len(p['uv'])!=2 or not all(isinstance(x,(int,float)) and math.isfinite(x) for x in p['uv']): raise ValueError('Invalid component-local point')


def draw_path(path,scene):
    pts=[point(p,scene) for p in path['points']]
    if path.get('kind')=='cubic':
        content=pts[0]+' .. controls '+pts[1]+' and '+pts[2]+' .. '+pts[3]
    else: content=' -- '.join(pts)
    return r"\draw[edge-%s] %s%s;"%(path['style'],content,' -- cycle' if path.get('closed') else '')

def validate_motif(g,scene):
    for v in g.get('vertices',[]):
        if v.get('shape','circle') not in ('circle','square','triangle'): raise ValueError('Unknown motif marker')
        if len(v['uv'])!=2 or not all(math.isfinite(x) for x in v['uv']): raise ValueError('Invalid marker coordinate')
        if v['radius_mm']<=0 or not math.isfinite(v['radius_mm']): raise ValueError('Invalid marker size')
        if v['style'] not in scene['node_styles']: raise ValueError('Unknown marker style')
    for e in g.get('edges',[]):
        if any(type(i) is not int or not 0<=i<len(g['vertices']) for i in e['ends']): raise ValueError('Unknown motif vertex')
        if len(e['ends'])!=2 or e['style'] not in scene['line_styles']: raise ValueError('Invalid motif edge')

def draw_motif(node,scene,color):
    g=node['glyph'];w,h=g['face_mm'];out=[r"\begin{scope}[shift={(%s.west |- %s.north)},x=1mm,y=-1mm]"%(node['id'],node['id'])]
    vertices=g.get('vertices',[])
    for e in g.get('edges',[]):
        a,b=[vertices[i]['uv'] for i in e['ends']]
        out.append(r"\draw[edge-%s] (%g,%g)--(%g,%g);"%(e['style'],a[0]*w,a[1]*h,b[0]*w,b[1]*h))
    for v in vertices:
        x,y=v['uv'][0]*w,v['uv'][1]*h;r=v['radius_mm'];c=color(scene['node_styles'][v['style']]['fill']);shape=v.get('shape','circle')
        if shape=='circle':out.append(r"\fill[%s] (%g,%g) circle[radius=%gmm];"%(c,x,y,r))
        elif shape=='square':out.append(r"\fill[%s] (%g,%g) rectangle (%g,%g);"%(c,x-r,y-r,x+r,y+r))
        else:out.append(r"\fill[%s] (%g,%g)--(%g,%g)--(%g,%g)--cycle;"%(c,x,y-r,x-r,y+r,x+r,y+r))
    out.append(r"\end{scope}");return '\n'.join(out)
