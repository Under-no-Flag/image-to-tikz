#!/usr/bin/env python3
"""Build a reproducible, standalone skill ZIP; no tests, credentials or gallery."""
import argparse
import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]

def package(out):
    skill = ROOT/'skills/image-to-tikz'
    version = (skill/'VERSION').read_text().strip()
    out.mkdir(parents=True, exist_ok=True)
    target = out/f'image-to-tikz-{version}.zip'
    files = sorted(p for p in skill.rglob('*') if p.is_file() and
                   '__pycache__' not in p.parts and p.suffix != '.pyc' and p.name != '.DS_Store')
    with ZipFile(target, 'w', ZIP_DEFLATED) as archive:
        for path in files:
            info = ZipInfo('image-to-tikz/'+path.relative_to(skill).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_text(f'{digest}  {target.name}\n')
    print(f'{target} ({len(files)} files)')
    return target

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT/'dist')
    package(parser.parse_args().out.resolve())
