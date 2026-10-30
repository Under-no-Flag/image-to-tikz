#!/usr/bin/env python3
"""Curate declared local runs for publication; never part of skill inference."""
import argparse, hashlib, json, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/image-to-tikz/scripts'))
from export_preview import render_pdf


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    parser.add_argument('--runs',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    cases=json.loads(args.manifest.read_text())['cases']
    for case in cases:
        src=args.runs/case['run'];dest=args.out/case['id']
        if dest.exists():raise ValueError(f'Refusing to overwrite {dest}')
        dest.mkdir(parents=True)
        shutil.copyfile(src/'source.png', dest/'input.png')
        metadata=render_pdf(src/'preview.pdf',dest/'output.png',600)
        metadata.update({k:v for k,v in case.items() if k!='run'})
        metadata['input_sha256']=hashlib.sha256((dest/'input.png').read_bytes()).hexdigest()
        metadata['note']='README image pair only; not the complete editable/OCR/review bundle.'
        (dest/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
        print(case['id'],metadata['dimensions_px'],flush=True)
if __name__=='__main__':main()
