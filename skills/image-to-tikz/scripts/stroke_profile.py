#!/usr/bin/env python3
"""Measure isolated raster strokes using contrast-normalized FWHM cross-sections.
User/agent chooses clean straight ROIs; this is not automatic topology recovery.
"""
import argparse,hashlib,json,math,statistics
from pathlib import Path
from PIL import Image,ImageDraw

def percentile(xs,p):
 s=sorted(xs);x=(len(s)-1)*p;lo=int(x);hi=min(lo+1,len(s)-1);return s[lo]*(hi-x)+s[hi]*(x-lo) if lo!=hi else s[lo]

def width(profile):
 # Use the two outer flanks, avoiding the potentially colored interior background.
 n=len(profile);q=max(1,n//5);bg=max(statistics.median(profile[:q]),statistics.median(profile[-q:]));peak=min(profile);contrast=bg-peak
 if contrast<45:return None
 center=min(range(n),key=profile.__getitem__);cut=peak+contrast/2
 a=b=center
 while a>0 and profile[a-1]<=cut:a-=1
 while b<n-1 and profile[b+1]<=cut:b+=1
 if a==0 or b==n-1:return None
 left=a-1+(profile[a-1]-cut)/(profile[a-1]-profile[a])
 right=b+(cut-profile[b])/(profile[b+1]-profile[b])
 return right-left

def measure(image,samples,width_mm):
 if not math.isfinite(width_mm) or width_mm<=0:raise ValueError('Positive physical width required')
 im=image.convert('L');px=im.load();results=[]
 for spec in samples:
  x0,y0,x1,y1=spec['box_xyxy'];orient=spec['orientation']
  if not all(type(v)is int for v in [x0,y0,x1,y1]) or not(0<=x0<x1<=im.width and 0<=y0<y1<=im.height):raise ValueError('Invalid sample crop')
  if orient not in ['horizontal','vertical']:raise ValueError('Unknown stroke orientation')
  scans=([px[x,y] for y in range(y0,y1)] for x in range(x0,x1)) if orient=='horizontal' else ([px[x,y] for x in range(x0,x1)] for y in range(y0,y1))
  measured=[];peaks=[];backgrounds=[];ink=[]
  for row in scans:
   v=width(row)
   if v is None:continue
   measured.append(v);peaks.append(min(row));q=max(1,len(row)//5)
   left=statistics.median(row[:q]);right=statistics.median(row[-q:]);bg=(left+right)/2;backgrounds.append(bg)
   # Ink-equivalent width is meaningful only on a nearly uniform light background.
   if abs(left-right)<=8 and min(left,right)>=240:ink.append(sum(max(0,(bg-p)/255) for p in row))
  r={**spec,'valid_cross_sections':len(measured),'total_cross_sections':(x1-x0 if orient=='horizontal' else y1-y0)}
  if measured:
   med=statistics.median(measured);r.update(width_px=round(med,4),iqr_px=[round(percentile(measured,p),4) for p in [.25,.75]],width_pt=round(med*width_mm/im.width*72.27/25.4,4))
   r.update(peak_luma=round(statistics.median(peaks),2),background_luma=round(statistics.median(backgrounds),2),equivalent_black_ink_width_px=round(statistics.median(ink),4) if ink else None,equivalent_black_ink_width_pt=round(statistics.median(ink)*width_mm/im.width*72.27/25.4,4) if ink else None)
   r['quality']='stable' if len(measured)>=3 and (percentile(measured,.75)-percentile(measured,.25))/med<.3 else 'review-profile-variation'
  else:r.update(quality='no-clean-cross-sections',width_px=None,width_pt=None)
  results.append(r)
 return {'method':'contrast-normalized FWHM, median of isolated straight-line cross-sections','source_px':list(im.size),'target_width_mm':width_mm,'samples':results,'limitations':'ROI selection must avoid text, corners, arrowheads and crossing lines. Blur/antialiasing affect widths; use several independent samples per style. FWHM separates profile width from peak darkness; equivalent-black-ink width measures visual weight on uniform light backgrounds, not physical stroke width. A blurred raster cannot uniquely recover original line width/color. Neither metric alone classifies font boldness.'}

def run(image,samples,out,width_mm):
 image=Path(image);out=Path(out)
 with Image.open(image) as im:
  report=measure(im,json.loads(Path(samples).read_text()),width_mm);overlay=im.convert('RGB');draw=ImageDraw.Draw(overlay)
  for s in report['samples']:
   draw.rectangle(s['box_xyxy'],outline='#FF0000',width=max(1,im.width//700));draw.text((s['box_xyxy'][0],max(0,s['box_xyxy'][1]-14)),s['id'],fill='#CC0000')
 report['source_sha256']=hashlib.sha256(image.read_bytes()).hexdigest();out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');overlay.save(out.with_suffix('.png'))
 print(json.dumps([{'id':s['id'],'width_px':s['width_px'],'width_pt':s['width_pt'],'quality':s['quality']} for s in report['samples']],ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('image');p.add_argument('samples');p.add_argument('--out',required=True);p.add_argument('--width-mm',type=float,required=True);a=p.parse_args();run(a.image,a.samples,a.out,a.width_mm)
