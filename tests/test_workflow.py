"""Contract and real XeLaTeX smoke tests; no real OCR acceptance is claimed."""
from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/"skills/image-to-tikz"
sys.path.insert(0, str(SKILL/"scripts"))
import paddle_ocr
import render
import scene
import workflow


def fixture():
    data = json.loads((SKILL/"assets/scene-template.json").read_text())
    data["nodes"] = [
        {"id":"title", "style":"label", "size":"title", "text":"技术路线：数据、模型与验证", "at_mm":[0,0]},
        {"id":"collect", "style":"process", "size":"standard", "text":"数据采集\n多源信息", "relative":{"of":"title","dx":-26,"dy":25}, "ocr_ids":["ocr-001"]},
        {"id":"clean", "style":"process", "size":"standard", "text":"预处理\n质量控制", "relative":{"of":"collect","dx":"column-pitch","dy":0}},
        {"id":"model", "style":"process", "size":"standard", "text":"时空特征\n编码与融合", "relative":{"of":"collect","dx":0,"dy":"row-pitch"}},
        {"id":"formula", "style":"process", "size":"standard", "latex":r"$\hat{y}=f_\theta(x)$", "latex_reviewed":True, "relative":{"of":"model","dx":"column-pitch","dy":0}},
        {"id":"result", "style":"process", "size":"wide", "text":"模型评估：MAE & RMSE\n误差_1 / 95%", "relative":{"of":"model","dx":26,"dy":"row-pitch"}}
    ]
    data["edges"] = [
        {"id":"a-b", "from":"collect.east", "to":"clean.west", "style":"normal", "label":"校验", "label_font":"annotation"},
        {"id":"a-c", "from":"collect.south", "to":"model.north", "style":"normal"},
        {"id":"b-d", "from":"clean.south", "to":"formula.north", "style":"normal"},
        {"id":"c-e", "from":"model.south", "to":"result.north west", "style":"normal", "route":"vh"},
        {"id":"d-e", "from":"formula.south", "to":"result.north east", "style":"normal", "route":"vh"}
    ]
    data["containers"] = [{"id":"stage", "members":["collect","clean","model","formula"], "style":"section", "padding_mm":4, "title":"数据与建模"}]
    data["alignments"] = [{"axis":"y","nodes":["collect","clean"]},{"axis":"x","nodes":["collect","model"]}]
    return data


def raw_fixture():
    return {"width":200,"height":100,"parsing_res_list":[
        {"block_label":"text","block_content":"数据采集","block_bbox":[10,10,90,30]},
        {"block_label":"image","block_content":"ignored","block_bbox":[1,1,5,5]}]}


class SceneTests(unittest.TestCase):
    def test_relative_move_propagates_and_alignment_is_checked(self):
        data = fixture()
        before = scene.resolve(data)
        data["nodes"][0]["at_mm"] = [10, 20]
        after = scene.resolve(data)
        for key in before:
            self.assertEqual(after[key], (before[key][0]+10, before[key][1]+20))
        self.assertEqual(scene.structural_checks(data)["warnings"], [])
        data["nodes"][2]["relative"]["dy"] = 2
        self.assertTrue(any("Alignment violated" in v for v in scene.structural_checks(data)["warnings"]))

    def test_cycles_and_unknown_edges_are_rejected(self):
        data = fixture()
        data["nodes"][0].pop("at_mm")
        data["nodes"][0]["relative"] = {"of":"clean"}
        with self.assertRaisesRegex(ValueError, "cycle"):
            scene.validate(data)
        data = fixture(); data["edges"][0]["to"] = "missing.west"
        with self.assertRaisesRegex(ValueError, "endpoint"):
            scene.validate(data)

    def test_overlap_and_shared_style_generation(self):
        data = fixture()
        data["nodes"][2]["relative"]["dx"] = 3
        self.assertTrue(any("overlap" in v for v in scene.structural_checks(data)["warnings"]))
        result = render.generate(fixture())
        self.assertIn(r"\&", result["figure.tex"])
        self.assertIn(r"\_", result["figure.tex"])
        self.assertIn(r"\%", result["figure.tex"])
        self.assertNotIn("includegraphics", result["figure.tex"])
        self.assertIn("node-process/.style", result["styles.tex"])
        self.assertIn("(collect)+(\\GapA,0mm)", result["figure.tex"])

    def test_unreviewed_latex_rejected(self):
        data = fixture(); data["nodes"][4].pop("latex_reviewed")
        with self.assertRaisesRegex(ValueError, "latex_reviewed"):
            scene.validate(data)

    def test_literal_tex_is_escaped(self):
        self.assertEqual(render.escape(r"\input{secret}"), r"\textbackslash{}input\{secret\}")

    def test_actual_shape_bounds_alignment_and_overlap(self):
        data = fixture()
        boxes = scene.structural_checks(data)["nominal_boxes_mm"]
        boxes["clean"][1] += 2
        boxes["clean"][3] += 2
        self.assertTrue(any("Alignment violated" in v for v in scene.geometry_checks(data, boxes)))
        boxes["clean"] = boxes["collect"][:]
        self.assertTrue(any("overlap" in v for v in scene.geometry_checks(data, boxes)))


class OCRTests(unittest.TestCase):
    def test_scaling_multiline_and_unknown_confidence(self):
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp)/"source.png"; Image.new("RGB", (400,200), "white").save(image)
            hints = paddle_ocr.normalize(raw_fixture(), image, 170)
            self.assertEqual(len(hints["lines"]), 1)
            line = hints["lines"][0]
            self.assertEqual(line["box_px"], [20,20,160,40])
            self.assertIsNone(line["confidence"])
            raw = raw_fixture(); raw["parsing_res_list"][0]["block_content"] += "\n第二行"
            self.assertAlmostEqual(paddle_ocr.normalize(raw, image, 170)["lines"][0]["font_pt_estimate"], line["font_pt_estimate"]/2, places=1)

    def test_job_protocol_and_single_submission(self):
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp)/"source.png"; Image.new("RGB", (20,20), "white").save(image)
            submit = Mock(status_code=200); submit.json.return_value={"data":{"jobId":"test"}}
            status = Mock(status_code=200); status.json.return_value={"data":{"state":"done","resultUrl":{"jsonUrl":"https://example.org/result"}}}
            result = Mock(status_code=200, text=json.dumps({"result":{"layoutParsingResults":[{"prunedResult":raw_fixture()}]}}))
            with patch.object(paddle_ocr, "token", return_value="not-a-real-token"), patch.object(paddle_ocr.requests, "post", return_value=submit) as post, patch.object(paddle_ocr.requests, "get", side_effect=[status,result]):
                raw = paddle_ocr.fetch(image)
            self.assertEqual(post.call_count, 1)
            self.assertEqual(raw["backend"], "paddleocr-vl")
            self.assertEqual(raw["page"]["width"], 200)

    def test_missing_token_does_not_send(self):
        with patch.object(paddle_ocr, "token", return_value=""), patch.object(paddle_ocr.requests, "post") as post:
            with self.assertRaisesRegex(ValueError, "Missing PADDLE"):
                paddle_ocr.fetch(Path("unused"))
            post.assert_not_called()


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        image = self.root/"input.png"; Image.new("RGB", (400,200), "white").save(image)
        self.run = self.root/"run"
        with contextlib.redirect_stdout(io.StringIO()):
            workflow.prepare(argparse.Namespace(image=str(image),out=str(self.run),width_mm=170))
        workflow.write(self.run/"scene.json", fixture())

    def test_no_overwrite_and_no_acceptance_without_ocr_render_review(self):
        with self.assertRaisesRegex(ValueError, "already exists"):
            workflow.prepare(argparse.Namespace(image=str(self.root/"input.png"),out=str(self.run),width_mm=170))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(workflow.check(argparse.Namespace(run=str(self.run), final=True)), 1)
        report = workflow.read(self.run/"validation.json")
        self.assertFalse(report["passed"])
        self.assertIn("PaddleOCR has not run", report["issues"])

    @unittest.skipUnless(all(shutil.which(t) for t in ("xelatex","pdftoppm","pdfinfo")), "TeX/Poppler not installed")
    def test_real_cjk_compile_dimensions_and_stale_review(self):
        raw = self.root/"raw.json"; workflow.write(raw, raw_fixture())
        with contextlib.redirect_stdout(io.StringIO()):
            workflow.ocr(argparse.Namespace(run=str(self.run),raw=str(raw),timeout=30,model=paddle_ocr.MODEL))
            workflow.build(argparse.Namespace(run=str(self.run),generate_only=False))
        compiled = workflow.read(self.run/"compile.json")
        self.assertTrue(compiled["passed"])
        self.assertEqual(len(compiled["actual_boxes_mm"]), 6)
        self.assertGreater((self.run/"preview.png").stat().st_size, 1000)
        # Synthetic review fixture tests acceptance mechanics, not real visual judgment.
        workflow.write(self.run/"review.json", {"signature":workflow.signature(self.run),"checks":{
            key:{"passed":True,"evidence":"Synthetic automated fixture; not real image acceptance"} for key in workflow.REVIEW_CHECKS}})
        with contextlib.redirect_stdout(io.StringIO()):
            code = workflow.check(argparse.Namespace(run=str(self.run),final=True))
        self.assertEqual(code, 0, workflow.read(self.run/"validation.json"))
        (self.run/"figure.tex").write_text((self.run/"figure.tex").read_text()+"% changed\n")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(workflow.check(argparse.Namespace(run=str(self.run),final=True)), 1)
        self.assertIn("Visual review missing/stale", workflow.read(self.run/"validation.json")["issues"])

    @unittest.skipUnless(all(shutil.which(t) for t in ("xelatex","pdftoppm","pdfinfo")), "TeX/Poppler not installed")
    def test_ellipse_diamond_and_overflow_measurements(self):
        data = fixture()
        data["node_styles"]["oval"] = {"shape":"ellipse","line":"normal","font":"body","fill":"#FFFFFF","padding_mm":2}
        data["nodes"][1]["style"] = "oval"
        data["nodes"][2]["style"] = "decision"
        data["nodes"][2]["text"] = "通过？"
        data["nodes"][3]["text"] = "\n".join(["溢出测试"]*10)
        workflow.write(self.run/"scene.json", data)
        with contextlib.redirect_stdout(io.StringIO()):
            workflow.build(argparse.Namespace(run=str(self.run),generate_only=False))
            workflow.check(argparse.Namespace(run=str(self.run),final=False))
        boxes = workflow.read(self.run/"compile.json")["actual_boxes_mm"]
        self.assertGreaterEqual(boxes["clean"][2]-boxes["clean"][0], 37.9)
        self.assertGreater(boxes["model"][3]-boxes["model"][1], 14.6)
        issues = workflow.read(self.run/"validation.json")["issues"]
        self.assertTrue(any("Text/shape exceeds shared size: model" in v for v in issues))

    def test_frozen_build_is_rejected_before_mutation(self):
        (self.run/"image-only-frozen").mkdir()
        before=(self.run/"scene.json").read_bytes()
        with self.assertRaisesRegex(ValueError,"Frozen reconstruction"):
            workflow.build(argparse.Namespace(run=str(self.run),generate_only=True))
        self.assertEqual((self.run/"scene.json").read_bytes(),before)

    def test_post_freeze_audit_cannot_report_acceptance(self):
        workflow.write(self.run/"post-freeze-audit.json",{"fidelity_passed":False})
        with contextlib.redirect_stdout(io.StringIO()):
            status=workflow.check(argparse.Namespace(run=str(self.run),final=True))
        self.assertEqual(status,1)
        self.assertTrue(any("Post-freeze audit" in v for v in workflow.read(self.run/"validation.json")["issues"]))


if __name__ == "__main__":
    unittest.main()
