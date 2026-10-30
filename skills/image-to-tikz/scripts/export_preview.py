"""Render a vector PDF at publication resolution without altering an accepted run."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageOps


def render_pdf(pdf: Path, output: Path, dpi: int = 600) -> dict:
    if not 72 <= dpi <= 1200:
        raise ValueError("DPI must be between 72 and 1200")
    pdf, output = Path(pdf).resolve(), Path(output).resolve()
    if output.exists():
        raise FileExistsError(f"Export exists: {output}; choose a new destination")
    if not pdf.is_file():
        raise ValueError(f"Missing PDF: {pdf}")
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True)
    if not any(line.split() == ["Pages:", "1"] for line in info.stdout.splitlines()):
        raise ValueError("Expected a one-page diagram PDF")
    with tempfile.TemporaryDirectory(prefix="tikz-export-") as td:
        prefix = Path(td)/"page"
        subprocess.run(["pdftoppm", "-singlefile", "-png", "-r", str(dpi), str(pdf), str(prefix)],
                       capture_output=True, text=True, check=True, timeout=180)
        with Image.open(prefix.with_suffix(".png")) as source:
            im = source.convert("RGB")
        bounds = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
        if not bounds:
            raise ValueError("Blank rendered PDF")
        clipped = bounds[0] <= 1 or bounds[1] <= 1 or bounds[2] >= im.width-1 or bounds[3] >= im.height-1
        im = ImageOps.expand(im.crop(bounds), border=round(dpi/8), fill="white")
        output.parent.mkdir(parents=True, exist_ok=True)
        im.save(output, dpi=(dpi, dpi))
    return {"dpi": dpi, "dimensions_px": list(im.size),
            "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
            "png_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "possible_page_clipping": clipped, "method": "direct-vector-pdf-rasterization"}


def export_run(args):
    run, out = Path(args.run).resolve(), Path(args.out).resolve()
    # Do not place exports inside a frozen snapshot or overwrite run evidence.
    if out == run or run in out.parents:
        raise ValueError("Export outside the run directory to preserve its review evidence")
    if out.exists():
        raise ValueError("Export destination already exists; choose a new directory")
    metadata = render_pdf(run/"preview.pdf", out/"preview.png", args.dpi)
    (out/"export.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))
