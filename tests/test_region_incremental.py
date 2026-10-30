"""A later OCR crop must not discard earlier, source-mapped evidence."""
import contextlib,hashlib,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/image-to-tikz/scripts'))
import ocr_regions
class IncrementalCropTests(unittest.TestCase):
 def test_merge_cached_modes_and_frozen_write_guard(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);Image.new('RGB',(100,100),'white').save(p/'source.png')
   (p/'request.json').write_text(json.dumps({'source_sha256':hashlib.sha256((p/'source.png').read_bytes()).hexdigest(),'target_width_mm':100}))
   (p/'ocr-raw.json').write_text(json.dumps({'parsing_res_list':[]}))
   response={'layout_detection_requested':False,'page':{'width':20,'height':20,'parsing_res_list':[{'block_label':'ocr','block_content':'Label','block_bbox':[0,0,20,20]}]}}
   spec=p/'regions.json'
   with patch('ocr_regions.paddle_ocr.fetch',return_value=response) as fetch, contextlib.redirect_stdout(io.StringIO()):
    spec.write_text(json.dumps([{'id':'a','box_xyxy':[0,0,20,20],'layout_detection':False}]))
    ocr_regions.run(p,spec)
    spec.write_text(json.dumps([{'id':'b','box_xyxy':[40,40,60,60],'layout_detection':False}]))
    ocr_regions.run(p,spec)
    self.assertEqual(fetch.call_count,2)
    h=json.loads((p/'ocr.json').read_text());self.assertEqual([r['id'] for r in h['regions']],['a','b']);self.assertEqual([r['id'] for r in h['lines']],['crop-a-ocr-001','crop-b-ocr-001']);self.assertEqual(h['lines'][1]['box_px'][:2],[40,40])
    (p/'image-only-frozen').mkdir()
    with self.assertRaisesRegex(ValueError,'Frozen'):ocr_regions.run(p,spec)
if __name__=='__main__':unittest.main()
