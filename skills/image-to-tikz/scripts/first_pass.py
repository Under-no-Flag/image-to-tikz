#!/usr/bin/env python3
"""Preserve first successful render before visual repairs, without claiming acceptance."""
import argparse,datetime,hashlib,json,shutil
from pathlib import Path
import workflow

def capture(run):
 run=Path(run).resolve();workflow.source_ok(run)
 compile=workflow.read(run/'compile.json')
 if compile.get('signature')!=workflow.signature(run):raise ValueError('Build is stale; cannot capture first render')
 dest=run/'first-pass';dest.mkdir() # never overwrite
 names=['source.png','request.json','ocr.json','scene.json','styles.tex','figure.tex','preview.tex','preview.pdf','preview.png','comparison.png','compile.json','compile.log','figure.positions']
 hashes={}
 for name in names:
  if (run/name).is_file():shutil.copyfile(run/name,dest/name);hashes[name]=workflow.sha(dest/name)
 if (run/'assets').exists():
  shutil.copytree(run/'assets',dest/'assets')
  for f in (dest/'assets').rglob('*'):
   if f.is_file():hashes[str(f.relative_to(dest))]=workflow.sha(f)
 record={'captured_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':'first-successful-render-before-visual-repairs','visual_acceptance':None,'files':hashes,'note':'Retain earlier failed compile attempts separately. This is not an accepted/final snapshot.'}
 workflow.write(dest/'snapshot.json',record);return dest
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('run');a=p.parse_args();print(capture(a.run))
