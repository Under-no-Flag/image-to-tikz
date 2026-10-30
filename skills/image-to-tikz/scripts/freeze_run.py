#!/usr/bin/env python3
"""Snapshot accepted image-only reconstruction before consulting target source."""
import argparse, datetime, hashlib, json, shutil
from pathlib import Path
import workflow

def freeze(run):
    run=Path(run).resolve()
    if workflow.check(argparse.Namespace(run=str(run),final=True)):
        raise ValueError('Only a current accepted build can be frozen')
    out=run/'image-only-frozen'
    out.mkdir()  # never overwrite a previous blind result
    names=['source.png','request.json','ocr.json','ocr-raw.json','scene.json','styles.tex','figure.tex','preview.tex','preview.pdf','preview.png','comparison.png','review.json','validation.json','compile.json','compile.log','figure.positions']
    hashes={}
    for name in names:
        shutil.copyfile(run/name,out/name)
        hashes[name]=hashlib.sha256((out/name).read_bytes()).hexdigest()
    for extra in ['first-pass','evaluation','independent-review.json','reconstruction-report.md','assets','crop-provenance.json','ocr-regions','regions.json','ocr-no-layout-raw.json','ocr-reconciliation.json']:
        src=run/extra
        if not src.exists(): continue
        if src.is_dir(): shutil.copytree(src,out/extra)
        else: shutil.copyfile(src,out/extra)
        for item in ([out/extra] if src.is_file() else sorted((out/extra).rglob('*'))):
            if item.is_file(): hashes[str(item.relative_to(out))]=hashlib.sha256(item.read_bytes()).hexdigest()
    record={'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':hashes,'rule':'This snapshot precedes target-source inspection; source-assisted changes must be separate.'}
    (out/'freeze.json').write_text(json.dumps(record,indent=2)+'\n')
    print(out)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run');a=p.parse_args();freeze(a.run)
