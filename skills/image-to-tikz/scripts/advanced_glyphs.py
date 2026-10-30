"""Native projected surfaces and cell grids; no architecture inference."""
import math
from tex_numbers import decimal

KINDS={'polygon','grid-plane','cuboid'}
def finite(value):return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
def dimensions(g):
    w,h=g['face_mm']
    if g['kind']=='cuboid':
        dx,dy=g['depth_mm']
        if not all(finite(v) and v>0 for v in (dx,dy)):raise ValueError('Cuboid depth projection must be positive finite')
        return w+dx,h+dy
    return w,h

def validate(g,scene):
    def style(key):
        if key not in scene['node_styles']:raise ValueError('Unknown surface style')
    def line(key):
        if key is not None and key not in scene['line_styles']:raise ValueError('Unknown surface line style')
    if g['kind']=='cuboid':
        for face in ['front','top','right']:style(g['face_styles'][face])
        grid=g.get('grid',[1,1,1])
        if len(grid)!=3:raise ValueError('Cuboid grid needs columns, rows, depth steps')
        nx,ny,nz=grid
        matrices={key:(matrix,{'front':(ny,nx),'top':(nz,nx),'right':(ny,nz)}.get(key)) for key,matrix in g.get('cell_styles',{}).items()}
    else:
        style(g['face_style']);grid=g.get('grid',[1,1])
        if len(grid)!=2:raise ValueError('Surface grid needs columns and rows')
        corners=g.get('corners_uv') if g['kind']=='grid-plane' else g['points_uv']
        if not corners or (g['kind']=='grid-plane' and len(corners)!=4) or len(corners)<3:raise ValueError('Invalid surface vertices')
        if any(len(p)!=2 or not all(finite(v) and 0<=v<=1 for v in p) for p in corners):raise ValueError('Surface coordinates must be within unit box')
        matrices={'plane':(g['cell_styles'],(grid[1],grid[0]))} if g.get('cell_styles') else {}
    if any(type(v)is not int or not 1<=v<=128 for v in grid):raise ValueError('Grid counts must be integers from1 to128')
    for matrix,shape in matrices.values():
        if shape is None or len(matrix)!=shape[0] or any(len(row)!=shape[1] for row in matrix):raise ValueError('Cell style matrix does not match grid')
        for row in matrix:
            for v in row:
                if v is not None:style(v)
    line(g.get('grid_style'));line(g.get('outline_style'))
    shadow=g.get('shadow')
    if shadow:
        import re
        if not all(finite(shadow.get(k,0)) for k in ['dx_mm','dy_mm']):raise ValueError('Invalid shadow offset')
        if not re.fullmatch('#[0-9a-fA-F]{6}',shadow['color']):raise ValueError('Invalid shadow color')
        if not finite(shadow.get('opacity',.3)) or not 0<=shadow.get('opacity',.3)<=1:raise ValueError('Invalid shadow opacity')

def paint_options(style,color):
    gradient=style.get('gradient')
    if gradient:
        return 'shade,shading=axis,left color=%s,right color=%s,shading angle=%g'%(color(gradient['from']),color(gradient['to']),gradient.get('angle_deg',0))
    return 'fill='+color(style.get('fill','#FFFFFF'))

def xy(p):return '(%s,%s)'%tuple(decimal(v) for v in p)
def shape_path(points):return '--'.join(xy(p) for p in points)+'--cycle'
def interpolate(q,u,v):
    return tuple((1-u)*(1-v)*q[0][i]+u*(1-v)*q[1][i]+u*v*q[2][i]+(1-u)*v*q[3][i] for i in [0,1])

def draw(node,scene,color):
    g=node['glyph'];w,h=g['face_mm'];key=node['id']
    out=[r'\begin{scope}[shift={(%s.west |- %s.north)},x=1mm,y=-1mm]'%(key,key)]
    def fill(points,style):
        st=scene['node_styles'][style]
        out.append(r'\path[%s,draw=none,opacity=%g] %s;'%(paint_options(st,color),st.get('fill_opacity',st.get('opacity',1)),shape_path(points)))
    def face(q,style,nx,ny,cells=None):
        fill(q,style)
        if cells:
            for y,row in enumerate(cells):
                for x,st in enumerate(row):
                    if st:fill([interpolate(q,u,v) for u,v in [(x/nx,y/ny),((x+1)/nx,y/ny),((x+1)/nx,(y+1)/ny),(x/nx,(y+1)/ny)]],st)
        if g.get('grid_style'):
            for x in range(1,nx):out.append(r'\draw[border-%s] %s--%s;'%(g['grid_style'],xy(interpolate(q,x/nx,0)),xy(interpolate(q,x/nx,1))))
            for y in range(1,ny):out.append(r'\draw[border-%s] %s--%s;'%(g['grid_style'],xy(interpolate(q,0,y/ny)),xy(interpolate(q,1,y/ny))))
        if g.get('outline_style'):out.append(r'\draw[border-%s] %s;'%(g['outline_style'],shape_path(q)))
    if g['kind']=='cuboid':
        dx,dy=g['depth_mm'];nx,ny,nz=g.get('grid',[1,1,1]);cells=g.get('cell_styles',{})
        face([(dx,0),(w+dx,0),(w,dy),(0,dy)],g['face_styles']['top'],nx,nz,cells.get('top'))
        face([(w,dy),(w+dx,0),(w+dx,h),(w,dy+h)],g['face_styles']['right'],nz,ny,cells.get('right'))
        face([(0,dy),(w,dy),(w,dy+h),(0,dy+h)],g['face_styles']['front'],nx,ny,cells.get('front'))
    else:
        pts=[(u*w,v*h) for u,v in g['points_uv' if g['kind']=='polygon' else 'corners_uv']]
        if g.get('shadow'):
            sh=g['shadow'];out.append(r'\path[fill=%s,draw=none,opacity=%g] %s;'%(color(sh['color']),sh.get('opacity',.3),shape_path([(x+sh.get('dx_mm',0),y+sh.get('dy_mm',0)) for x,y in pts])))
        if g['kind']=='grid-plane':face(pts,g['face_style'],*g.get('grid',[1,1]),g.get('cell_styles'))
        else:
            fill(pts,g['face_style'])
            if g.get('outline_style'):out.append(r'\draw[border-%s] %s;'%(g['outline_style'],shape_path(pts)))
    out.append(r'\end{scope}');return '\n'.join(out)
