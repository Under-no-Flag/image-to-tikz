#!/usr/bin/env python3
"""One-image workflow; semantic recovery is performed by the invoking agent."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageOps
import requests

import paddle_ocr
import icon_assets
import export_preview
from render import generate
from scene import structural_checks, geometry_checks

SKILL = Path(__file__).resolve().parents[1]
REVIEW_CHECKS = ("text_and_formulas", "topology_and_arrows", "groups_and_containment",
    "alignment_and_spacing", "fonts_borders_and_lines", "no_clipping_or_overlap")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def signature(run):
    names = ("source.png", "scene.json", "ocr.json", "styles.tex", "figure.tex", "preview.tex", "preview.png")
    result={name: sha(run/name) for name in names if (run/name).exists()}
    if (run/"scene.json").exists():
        for a in read(run/"scene.json").get('assets',{}).values():
            p=run/a['path']
            result[a['path']]=sha(p) if p.is_file() else 'missing'
    return result


def source_ok(run):
    request = read(run/"request.json")
    if sha(run/"source.png") != request["source_sha256"]:
        raise ValueError("source.png changed since prepare; create a new task")
    return request


def prepare(args):
    image = Path(args.image).expanduser().resolve()
    if not image.is_file():
        raise ValueError("Supply exactly one image file, not a folder")
    if args.width_mm <= 0:
        raise ValueError("width-mm must be positive")
    run = Path(args.out).expanduser().resolve()
    if run.exists():
        raise ValueError(f"Output already exists: {run}; choose a new task directory")
    # Decode first so invalid input does not create an unusable run directory.
    with Image.open(image) as im:
        rgba = ImageOps.exif_transpose(im).convert("RGBA")
        source = Image.new("RGBA", rgba.size, "white")
        source.alpha_composite(rgba)
        source = source.convert("RGB")
    run.mkdir(parents=True)
    source.save(run/"source.png")
    write(run/"request.json", {"schema_version": 1, "input": str(image),
        "input_sha256": sha(image), "source_sha256": sha(run/"source.png"),
        "source_px": list(source.size), "target_width_mm": args.width_mm,
        "note": "One selected image only. OCR and semantic scene recovery are separate steps."})
    shutil.copyfile(SKILL/"assets/scene-template.json", run/"scene.json")
    print(f"Prepared one image: {run}")


def ocr(args):
    run = Path(args.run).resolve()
    request = source_ok(run)
    if (run/"ocr.json").exists():
        raise ValueError("OCR already exists; reuse it. Create a new task to rerun OCR.")
    raw = read(args.raw) if args.raw else paddle_ocr.fetch(run/"source.png", args.timeout, args.model, layout_detection=not args.no_layout_detection)
    hints = paddle_ocr.normalize(raw, run/"source.png", request["target_width_mm"])
    hints["source_sha256"] = request["source_sha256"]
    hints["provenance"] = "imported-paddle-result" if args.raw else "paddleocr-vl-api"
    write(run/"ocr-raw.json", raw)
    write(run/"ocr.json", hints)
    paddle_ocr.overlay(run/"source.png", hints, run/"ocr-overlay.png")
    print(f"PaddleOCR: {len(hints['lines'])} blocks. Inspect source.png and ocr-overlay.png before writing scene.json.")


def command(argv, cwd, log, timeout=120):
    result = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, timeout=timeout)
    log.write_text(result.stdout, encoding="utf-8")
    if result.returncode:
        raise ValueError(f"{argv[0]} failed; inspect {log}")
    return result.stdout


def actual_boxes(run):
    boxes = {}
    if (run/"figure.positions").exists():
        for line in (run/"figure.positions").read_text().splitlines():
            key, x1, y1, x2, y2 = line.split(",")
            # TeX point = 1/72.27 inch. Return x right, y down, millimetres.
            x1, y1, x2, y2 = [float(v.removesuffix("pt"))*25.4/72.27 for v in (x1, y1, x2, y2)]
            boxes[key] = [x1, -y1, x2, -y2]
    return boxes


def comparison(run):
    images = []
    for name in ("source.png", "preview.png"):
        with Image.open(run/name) as im:
            panel = im.convert("RGB")
        scale=min(1000/panel.width,1100/panel.height)
        panel=panel.resize((round(panel.width*scale),round(panel.height*scale)),Image.Resampling.LANCZOS)
        images.append(panel)
    canvas = Image.new("RGB", (sum(im.width for im in images)+30, max(im.height for im in images)+20), "#ededed")
    x = 10
    for im in images:
        canvas.paste(im, (x, 10))
        x += im.width+10
    canvas.save(run/"comparison.png")


def build(args):
    run = Path(args.run).resolve()
    dpi = getattr(args, "dpi", 300)
    if not 72 <= dpi <= 1200:
        raise ValueError("DPI must be between 72 and 1200")
    if (run/"image-only-frozen").exists():
        raise ValueError("Frozen reconstruction: create a separate run for revisions")
    source_ok(run)
    scene = read(run/"scene.json")
    icon_assets.validate(scene)
    icon_assets.verify_files(run,scene)
    products = generate(scene)
    # Invalidate prior build evidence before starting. Do not remove scene/OCR/review.
    for name in ("preview.pdf", "preview.png", "comparison.png", "figure.positions", "compile.json"):
        (run/name).unlink(missing_ok=True)
    for name, content in products.items():
        (run/name).write_text(content, encoding="utf-8")
    if args.generate_only:
        print("Generated editable sources; compilation and visual review pending")
        return
    for tool in ("xelatex", "pdftoppm", "pdfinfo"):
        if not shutil.which(tool):
            raise ValueError(f"Missing {tool}. Sources are available; compilation is pending.")
    command(["xelatex", "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error", "preview.tex"], run, run/"compile.log")
    info = command(["pdfinfo", "preview.pdf"], run, run/"pdfinfo.log")
    if not any(line.split() == ["Pages:", "1"] for line in info.splitlines()):
        raise ValueError("Expected one PDF page; inspect layout dimensions and compile.log")
    command(["pdftoppm", "-singlefile", "-png", "-r", str(dpi), "preview.pdf", "preview"], run, run/"render.log")
    with Image.open(run/"preview.png") as im:
        im = im.convert("RGB")
        bounds = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
        if not bounds:
            raise ValueError("Blank rendered preview")
        clipped = bounds[0] <= 1 or bounds[1] <= 1 or bounds[2] >= im.width-1 or bounds[3] >= im.height-1
        im = ImageOps.expand(im.crop(bounds), border=round(dpi/8), fill="white")
        im.save(run/"preview.png", dpi=(dpi, dpi))
    comparison(run)
    write(run/"compile.json", {"passed": True, "signature": signature(run), "pdf_sha256": sha(run/"preview.pdf"),
        "positions_sha256": sha(run/"figure.positions"), "log_sha256": sha(run/"compile.log"),
        "possible_page_clipping": clipped, "preview_dpi": dpi, "actual_boxes_mm": actual_boxes(run)})
    print("Compiled one-page preview.pdf; inspect preview.png and comparison.png, then record visual review.")


def review_template(args):
    run = Path(args.run).resolve()
    source_ok(run)
    write(run/"review-template.json", {"signature": signature(run),
        "checks": {key: {"passed": False, "evidence": ""} for key in REVIEW_CHECKS},
        "notes": "Inspect source.png, ocr-overlay.png, preview.png and comparison.png. Save completed assessment as review.json; do not mark unchecked items passed."})
    print(run/"review-template.json")


def check(args):
    run = Path(args.run).resolve()
    request = source_ok(run)
    scene = read(run/"scene.json")
    report = structural_checks(scene)
    issues = report["warnings"]
    try:icon_assets.verify_files(run,scene)
    except ValueError as exc:issues.append(str(exc))
    audit_path=run/"post-freeze-audit.json"
    if audit_path.exists() and read(audit_path).get("fidelity_passed") is False:
        issues.append("Post-freeze audit overturned visual acceptance; see post-freeze-audit.json and corrected separate run")
    issues.extend(f"Unresolved: {v}" for v in scene.get("unresolved", []))
    if not (run/"ocr.json").exists():
        issues.append("PaddleOCR has not run")
    else:
        hints = read(run/"ocr.json")
        if hints.get("backend") != "paddleocr-vl" or hints.get("source_sha256") != request["source_sha256"]:
            issues.append("OCR backend/source mismatch")
        if not hints.get("lines"):
            issues.append("PaddleOCR returned no text blocks; manual reconciliation required")
        known = {line["id"] for line in hints["lines"]}
        accounted = set()
        for item in scene["nodes"]+scene.get("edges", [])+scene.get("containers", []):
            accounted.update(item.get("ocr_ids", []))
        excluded = {v["id"] for v in scene.get("ocr_exclusions", []) if v.get("reason")}
        report["ocr_coverage"] = {"total": len(known), "mapped": len(known & accounted), "excluded": len(known & excluded)}
        if known - accounted - excluded:
            issues.append(f"Unaccounted OCR ids: {sorted(known-accounted-excluded)}")
        if (accounted | excluded) - known:
            issues.append(f"Unknown OCR ids: {sorted((accounted | excluded)-known)}")
    compile_path = run/"compile.json"
    if not compile_path.exists():
        issues.append("Compilation/render pending")
    else:
        compiled = read(compile_path)
        if compiled.get("signature") != signature(run) or not (run/"preview.pdf").exists() or compiled.get("pdf_sha256") != sha(run/"preview.pdf"):
            issues.append("Build is stale; run build again")
        if not (run/"figure.positions").exists() or compiled.get("positions_sha256") != sha(run/"figure.positions"):
            issues.append("Actual node geometry missing or stale")
        if not (run/"compile.log").exists() or compiled.get("log_sha256") != sha(run/"compile.log"):
            issues.append("Compile log missing or stale")
        if compiled.get("possible_page_clipping"):
            issues.append("Rendered ink reaches page edge: inspect clipping")
        actual = compiled.get("actual_boxes_mm", {})
        if all(n["id"] in actual for n in scene["nodes"]):
            issues.extend("Actual geometry: "+v for v in geometry_checks(scene, actual))
        for node in scene["nodes"]:
            box = compiled.get("actual_boxes_mm", {}).get(node["id"])
            w, h = scene["sizes"][node["size"]]
            if not box:
                issues.append(f"Actual bounds missing: {node['id']}")
            elif box[2]-box[0] > w+.6 or box[3]-box[1] > h+.6:
                issues.append(f"Text/shape exceeds shared size: {node['id']}; enlarge size group or revise line breaks")
        log = (run/"compile.log").read_text(errors="replace") if (run/"compile.log").exists() else ""
        if any(term in log for term in ("Overfull", "Missing character:", "LaTeX Font Warning")):
            issues.append("TeX reports overflow or font/glyph warnings; inspect compile.log")
    review = read(run/"review.json") if (run/"review.json").exists() else {}
    if review.get("signature") != signature(run):
        issues.append("Visual review missing/stale")
    for key in REVIEW_CHECKS:
        entry = review.get("checks", {}).get(key, {})
        if entry.get("passed") is not True or not entry.get("evidence", "").strip():
            issues.append(f"Visual check pending/failed: {key}")
    report.update(passed=not issues, status="accepted" if not issues else "needs-review-or-repair", issues=issues)
    write(run/"validation.json", report)
    print(json.dumps({"passed": report["passed"], "issues": issues}, ensure_ascii=False, indent=2))
    return 0 if report["passed"] or not args.final else 1


def doctor(args):
    print(json.dumps({"python": sys.version.split()[0], "paddleocr_token_configured": bool(paddle_ocr.token()),
        "tools": {name: shutil.which(name) for name in ("xelatex", "pdftoppm", "pdfinfo")},
        "ocr_backend": "PaddleOCR-VL cloud jobs", "model": paddle_ocr.MODEL}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="cmd", required=True)
    sub = subs.add_parser("doctor"); sub.set_defaults(func=doctor)
    sub = subs.add_parser("prepare"); sub.add_argument("image"); sub.add_argument("--out", required=True)
    sub.add_argument("--width-mm", type=float, default=170); sub.set_defaults(func=prepare)
    sub = subs.add_parser("ocr"); sub.add_argument("run"); sub.add_argument("--raw", help="Import one cached PaddleOCR JSON result without network")
    sub.add_argument("--no-layout-detection", action="store_true", help="OCR non-document diagrams without layout segmentation"); sub.add_argument("--timeout", type=int, default=300); sub.add_argument("--model", default=paddle_ocr.MODEL); sub.set_defaults(func=ocr)
    sub = subs.add_parser("build"); sub.add_argument("run"); sub.add_argument("--generate-only", action="store_true"); sub.add_argument("--dpi", type=int, default=300); sub.set_defaults(func=build)
    sub = subs.add_parser("export", help="Export a PDF to high-resolution PNG without changing run evidence")
    sub.add_argument("run"); sub.add_argument("--out", required=True); sub.add_argument("--dpi", type=int, default=600); sub.set_defaults(func=export_preview.export_run)
    sub = subs.add_parser("review-template"); sub.add_argument("run"); sub.set_defaults(func=review_template)
    sub = subs.add_parser("check"); sub.add_argument("run"); sub.add_argument("--final", action="store_true"); sub.set_defaults(func=check)
    args = parser.parse_args()
    try:
        return args.func(args) or 0
    except (ValueError, KeyError, OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except requests.RequestException:
        # Request exception strings can contain signed result URLs. Keep them local.
        print("PaddleOCR network request failed. No automatic resubmit; inspect service job before retrying.", file=sys.stderr)
        return 2
if __name__ == "__main__":
    raise SystemExit(main())
