"""Explicit generated-icon assets only; diagram structure remains native TikZ."""
import hashlib,re
from tex_numbers import decimal
from pathlib import Path,PurePosixPath
from PIL import Image

def validate(scene):
    assets=scene.get('assets',{})
    for key,a in assets.items():
        if not re.fullmatch('[a-z][a-z0-9-]*',key):raise ValueError('Invalid asset id')
        path=PurePosixPath(a['path'])
        if not re.fullmatch(r'assets/[a-zA-Z0-9_./-]+\.png',a['path']) or '..' in path.parts:raise ValueError('Icon path must be a safe run-relative assets/*.png')
        if a.get('kind')!='generated-icon' or a.get('generator')!='image_gen' or not a.get('prompt'):raise ValueError('Icon requires generated-icon kind, image_gen generator and prompt provenance')
        if not re.fullmatch('[a-f0-9]{64}',a.get('sha256','')):raise ValueError('Icon requires SHA256')
        w,h=a['width_px'],a['height_px']
        if any(type(v)is not int or v<=0 for v in [w,h]):raise ValueError('Invalid icon pixel dimensions')
        x0,y0,x1,y1=a.get('crop_px',[0,0,w,h])
        if not 0<=x0<x1<=w or not 0<=y0<y1<=h:raise ValueError('Icon crop outside asset')
    for n in scene['nodes']:
        if 'asset' in n:
            if n['asset'] not in assets:raise ValueError('Unknown icon asset')
            if n.get('text')!='' or 'latex' in n or 'glyph' in n:raise ValueError('Icon node needs empty text, no glyph/latex; labels must be separate editable nodes')

def verify_files(run,scene):
    for a in scene.get('assets',{}).values():
        path=(run/a['path']).resolve()
        if not path.is_relative_to((run/'assets').resolve()) or not path.is_file():raise ValueError('Missing or escaped icon file')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=a['sha256']:raise ValueError('Icon checksum changed; reconcile asset provenance')
        with Image.open(path) as im:
            if list(im.size)!=[a['width_px'],a['height_px']]:raise ValueError('Icon dimensions mismatch')

def draw(node,scene):
    a=scene['assets'][node['asset']];w,h=scene['sizes'][node['size']];W,H=a['width_px'],a['height_px'];x0,y0,x1,y1=a.get('crop_px',[0,0,W,H]);scale=min(w/(x1-x0),h/(y1-y0));dx=(W/2-(x0+x1)/2)*scale;dy=-(H/2-(y0+y1)/2)*scale;k=node['id']
    return (r'\begin{scope}'+'\n'+r'\clip ($(%s.center)+(%smm,%smm)$) rectangle ($(%s.center)+(%smm,%smm)$);'%(k,decimal(-w/2),decimal(-h/2),k,decimal(w/2),decimal(h/2))+'\n'+r'\node[inner sep=0pt,outer sep=0pt] at ($(%s.center)+(%smm,%smm)$) {\includegraphics[width=%smm]{\detokenize{%s}}};'%(k,decimal(dx),decimal(dy),decimal(W*scale),a['path'])+'\n'+r'\end{scope}')
