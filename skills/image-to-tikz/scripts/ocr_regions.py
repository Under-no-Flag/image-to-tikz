#!/usr/bin/env python3
"""Read selected text crops with PaddleOCR; cache by crop SHA and remap boxes."""
import argparse, hashlib, json, re
from pathlib import Path
from PIL import Image
import paddle_ocr

def run(directory, regions_path):
    root=Path(directory); specs=json.loads(Path(regions_path).read_text()); source=root/'source.png'
    if (root/'image-only-frozen').exists(): raise ValueError('Frozen reconstruction: use a new run for OCR revisions')
    # Supplemental passes must retain previously mapped crops, not silently drop them.
    prior={}
    if (root/'ocr.json').exists():
        old=json.loads((root/'ocr.json').read_text())
        for region in old.get('regions',[]):
            name=region['id']
            if not re.fullmatch('[a-z][a-z0-9-]*',name): raise ValueError('Unsafe cached region id')
            raw_path=root/'ocr-regions'/name/'raw.json'
            mode=region.get('layout_detection')
            if mode is None and raw_path.exists(): mode=json.loads(raw_path.read_text()).get('layout_detection_requested',True)
            prior[name]={'id':name,'box_xyxy':region['box_xyxy'],'layout_detection':True if mode is None else mode}
    for spec in specs: prior[spec['id']]=spec
    specs=list(prior.values())
    request=json.loads((root/'request.json').read_text())
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if digest!=request['source_sha256']: raise ValueError('Source changed')
    with Image.open(source) as im:
        im.load()
        hints=paddle_ocr.normalize(json.loads((root/'ocr-raw.json').read_text()),source,request['target_width_mm'])
        statuses=[]
        for spec in specs:
            name=spec['id']; box=spec['box_xyxy']
            if not re.fullmatch('[a-z][a-z0-9-]*',name): raise ValueError('Unsafe region id')
            x1,y1,x2,y2=box
            if not 0<=x1<x2<=im.width or not 0<=y1<y2<=im.height: raise ValueError('Crop outside source')
            d=root/'ocr-regions'/name;d.mkdir(parents=True,exist_ok=True)
            crop=im.crop(box); crop_path=d/'source.png'
            # Never overwrite a cached crop from different coordinates.
            if crop_path.exists():
                with Image.open(crop_path) as old:
                    if old.size!=crop.size or old.convert('RGB').tobytes()!=crop.convert('RGB').tobytes(): raise ValueError('Cached crop differs; use a new region id')
            else: crop.save(crop_path)
            raw_path=d/'raw.json'
            if raw_path.exists():
                raw=json.loads(raw_path.read_text())
                if raw.get('layout_detection_requested', True) != spec.get('layout_detection', True): raise ValueError('Cached OCR mode differs; use a new region id')
            else:
                raw=paddle_ocr.fetch(crop_path, layout_detection=spec.get("layout_detection", True))
                raw_path.write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n')
            local=paddle_ocr.normalize(raw,crop_path,request['target_width_mm']*crop.width/im.width)
            statuses.append({'id':name,'box_xyxy':box,'blocks':len(local['lines']),'layout_detection':spec.get('layout_detection',True),'job_id':raw.get('job_id'),'crop_sha256':hashlib.sha256(crop_path.read_bytes()).hexdigest()})
            for line in local['lines']:
                line['id']=f"crop-{name}-{line['id']}";line['box_px'][0]+=x1;line['box_px'][1]+=y1;line['region']=name
                hints['lines'].append(line)
    hints.update(source_sha256=digest,provenance='paddleocr-vl-api-with-cached-regions',regions=statuses)
    (root/'ocr.json').write_text(json.dumps(hints,ensure_ascii=False,indent=2)+'\n')
    paddle_ocr.overlay(source,hints,root/'ocr-overlay.png')
    print(json.dumps(statuses,ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run');p.add_argument('regions');a=p.parse_args();run(a.run,a.regions)
