"""PaddleOCR-VL jobs adapter and reusable, source-coordinate text hints.

Protocol adapted from ningzimu/image-to-editable-ppt-skill (MIT),
commit b7be494e31a0ed56ef98716891db5474606b8cdf. See THIRD_PARTY_NOTICES.md.
"""
from __future__ import annotations

import json
import os
import statistics
import time
from pathlib import Path

import requests
import yaml
from PIL import Image, ImageDraw

JOB_URL = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
MODEL = "PaddleOCR-VL-1.6"


def token() -> str:
    value = os.environ.get("PADDLE_OCR_TOKEN", "").strip()
    if value:
        return value
    # Read only the relevant key; never log config or borrow image API keys.
    for path in (Path.home() / ".image-to-tikz/config.yaml", Path.home() / ".editppt/config.yaml"):
        if path.is_file():
            data = yaml.safe_load(path.read_text()) or {}
            value = str(data.get("PADDLE_OCR_TOKEN", "")).strip()
            if value:
                return value
    return ""


def fetch(image: Path, timeout: int = 300, model: str = MODEL, layout_detection: bool = True) -> dict:
    credential = token()
    if not credential:
        raise ValueError("Missing PADDLE_OCR_TOKEN. Set the environment variable or user-level ~/.image-to-tikz/config.yaml; no OCR request was sent.")
    headers = {"Authorization": f"bearer {credential}"}
    started = time.monotonic()
    with image.open("rb") as handle:
        response = requests.post(JOB_URL, headers=headers,
            data={"model": model, "optionalPayload": json.dumps({
                "useDocOrientationClassify": False, "useDocUnwarping": False,
                "useChartRecognition": False, "useLayoutDetection": layout_detection})}, files={"file": handle}, timeout=min(60, timeout))
    if response.status_code != 200:
        raise RuntimeError(f"PaddleOCR submit HTTP {response.status_code}; response body omitted to protect credentials.")
    job_id = response.json()["data"]["jobId"]
    # Do not retry submit automatically: a timeout may still have created a job.
    while True:
        remaining = timeout - (time.monotonic() - started)
        if remaining <= 0:
            raise RuntimeError(f"PaddleOCR job {job_id} timed out; do not resubmit blindly.")
        response = requests.get(f"{JOB_URL}/{job_id}", headers=headers, timeout=min(60, remaining))
        if response.status_code != 200:
            raise RuntimeError(f"PaddleOCR polling HTTP {response.status_code}; job={job_id}")
        status = response.json()["data"]
        if status["state"] == "done":
            break
        if status["state"] == "failed":
            raise RuntimeError(f"PaddleOCR job {job_id} failed; inspect service console.")
        print(f"PaddleOCR job {job_id}: {status['state']}", flush=True)
        time.sleep(min(3, max(0, timeout - (time.monotonic() - started))))
    remaining = timeout - (time.monotonic() - started)
    if remaining <= 0:
        raise RuntimeError(f"PaddleOCR job {job_id}: result download deadline exceeded")
    response = requests.get(status["resultUrl"]["jsonUrl"], timeout=min(60, remaining))
    if response.status_code != 200:
        raise RuntimeError(f"PaddleOCR result HTTP {response.status_code}; job={job_id}")
    pages = []
    for line in response.text.splitlines():
        if line.strip():
            pages.extend(item["prunedResult"] for item in json.loads(line)["result"]["layoutParsingResults"])
    if len(pages) != 1:
        raise ValueError(f"Expected one image/one page, got {len(pages)} PaddleOCR pages")
    return {"backend": "paddleocr-vl", "model": model, "job_id": job_id, "layout_detection_requested": layout_detection, "page": pages[0]}


def normalize(raw: dict, image: Path, width_mm: float) -> dict:
    """OCR boxes are xyxy; public hints use xywh. Font sizes are estimates.

    OCR confidence and ink height are not interchangeable; unknown confidence
    remains null. Multiline paragraphs must not be treated as a single glyph.
    """
    page = raw.get("page", raw)
    with Image.open(image) as im:
        width, height = im.size
    sx = width / float(page.get("width", width))
    sy = height / float(page.get("height", height))
    lines = []
    for block in page.get("parsing_res_list", []):
        label = block.get("block_label", "")
        if label not in {"ocr", "text", "doc_title", "figure_title", "paragraph_title", "vision_footnote", "formula", "formula_number"}:
            continue
        text = str(block.get("block_content", "")).strip()
        if not text:
            continue
        x1, y1, x2, y2 = map(float, block["block_bbox"])
        x1, x2 = max(0, x1 * sx), min(width, x2 * sx)
        y1, y2 = max(0, y1 * sy), min(height, y2 * sy)
        if x2 <= x1 or y2 <= y1:
            continue
        line_count = max(1, len(text.splitlines()))
        glyph = (y2 - y1) / (line_count * 1.2)
        aggregate = label == "ocr" or (x2-x1)*(y2-y1) > width*height*.4 and line_count > 3
        lines.append({"text": text, "aggregate": aggregate, "box_px": [round(v, 2) for v in (x1, y1, x2-x1, y2-y1)],
            "font_pt_estimate": round(glyph * width_mm / width * 72.27 / 25.4, 2),
            "font_source": "unreliable-aggregate" if aggregate else "bbox-estimate", "confidence": block.get("block_score"),
            "kind": label, "needs_review": True})
    lines.sort(key=lambda x: (x["box_px"][1], x["box_px"][0]))
    # Height clusters are suggestions only. Semantic level is determined by agent.
    groups: list[list[dict]] = []
    for line in sorted((v for v in lines if not v['aggregate']), key=lambda x: x["font_pt_estimate"]):
        group = next((g for g in groups if abs(line["font_pt_estimate"] / statistics.median(
            v["font_pt_estimate"] for v in g) - 1) <= .12), None)
        if group is None:
            groups.append([line])
        else:
            group.append(line)
    size_groups = {}
    for index, group in enumerate(groups, 1):
        group_id = f"size-{index}"
        size_groups[group_id] = round(statistics.median(v["font_pt_estimate"] for v in group), 2)
        for line in group:
            line["suggested_size_group"] = group_id
    for index, line in enumerate(lines, 1):
        line["id"] = f"ocr-{index:03d}"
    return {"schema_version": 1, "backend": "paddleocr-vl", "source_px": [width, height],
        "target_width_mm": width_mm, "lines": lines, "suggested_size_groups_pt": size_groups,
        "note": "Estimated from OCR boxes, not measured font metrics. Check source; reconcile semantic levels and formulas. OCR does not recover nodes or topology."}


def overlay(image: Path, hints: dict, output: Path):
    with Image.open(image) as source:
        im = source.convert("RGB")
    draw = ImageDraw.Draw(im)
    for line in hints["lines"]:
        x, y, w, h = line["box_px"]
        draw.rectangle((x, y, x+w, y+h), outline="#dd3333", width=2)
        draw.text((x, max(0, y-12)), line["id"], fill="#dd3333")
    im.save(output)
