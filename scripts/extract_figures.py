"""Extract figures from a PDF by clustering vector drawings and locating
FIGURE/Fig. captions, then emit a manifest usable to patch LaTeX references.

Usage:
    conda run -n education-env python scripts/extract_figures.py \
        --pdf assets/books/ci_example.pdf \
        --out assets/books/pdf_pages/figures \
        --latex-dir assets/books/pdf_pages/latex_pages
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import fitz

CAPTION_RE = re.compile(r"^\s*(?:FIGURE|Figure|Fig\.?)\s+(\d+(?:\.\d+)*)", re.MULTILINE)
REF_RE = re.compile(r"(?:FIGURE|Figure|Fig\.?)\s+(\d+(?:\.\d+)*)")

# Tunables — first-pass heuristics, expect to adjust after eyeballing output.
CLUSTER_GAP_PT = 18.0      # merge drawings whose bboxes are within this distance
MIN_FIG_WIDTH_PT = 90.0
MIN_FIG_HEIGHT_PT = 60.0
CAPTION_SEARCH_PT = 60.0   # caption must sit within this distance below figure
CROP_PADDING_PT = 6.0
RENDER_DPI = 220


@dataclass
class Cluster:
    rect: fitz.Rect
    members: int = 1
    has_raster: bool = False

    def expand_to(self, other: fitz.Rect, raster: bool = False) -> None:
        self.rect |= other
        self.members += 1
        self.has_raster = self.has_raster or raster


def rects_close(a: fitz.Rect, b: fitz.Rect, gap: float) -> bool:
    # Inflate a by gap on all sides; if it intersects b, they cluster.
    inflated = fitz.Rect(a.x0 - gap, a.y0 - gap, a.x1 + gap, a.y1 + gap)
    return inflated.intersects(b)


def cluster_drawings(page: fitz.Page, gap: float) -> list[fitz.Rect]:
    rects: list[fitz.Rect] = []
    for d in page.get_drawings():
        r = d.get("rect")
        if r is None or r.is_empty or r.is_infinite:
            continue
        rects.append(fitz.Rect(r))
    # Also fold in raster images.
    for img in page.get_images(full=True):
        xref = img[0]
        for r in page.get_image_rects(xref):
            rects.append(fitz.Rect(r))

    if not rects:
        return []

    clusters: list[Cluster] = []
    for r in rects:
        hit = None
        for c in clusters:
            if rects_close(c.rect, r, gap):
                hit = c
                break
        if hit is None:
            clusters.append(Cluster(rect=fitz.Rect(r)))
        else:
            hit.expand_to(r)

    # Second pass: clusters can themselves be close after growth; repeat until stable.
    changed = True
    while changed:
        changed = False
        merged: list[Cluster] = []
        for c in clusters:
            for m in merged:
                if rects_close(m.rect, c.rect, gap):
                    m.rect |= c.rect
                    m.members += c.members
                    changed = True
                    break
            else:
                merged.append(c)
        clusters = merged

    out = []
    for c in clusters:
        w, h = c.rect.width, c.rect.height
        if w >= MIN_FIG_WIDTH_PT and h >= MIN_FIG_HEIGHT_PT and c.members >= 3:
            out.append(c.rect)
    return out


def find_caption(page: fitz.Page, fig_rect: fitz.Rect) -> tuple[str, str, fitz.Rect] | None:
    """Return (label, full_caption_text, caption_bbox) for the caption closest
    below fig_rect and starting with FIGURE/Fig."""
    best = None
    best_dy = None
    for x0, y0, x1, y1, txt, *_ in page.get_text("blocks"):
        m = CAPTION_RE.match(txt)
        if not m:
            continue
        # Caption should sit below the figure or at least vertically overlap its bottom.
        dy = y0 - fig_rect.y1
        if dy < -5 or dy > CAPTION_SEARCH_PT:
            continue
        # Horizontal overlap check — caption roughly under figure column.
        if x1 < fig_rect.x0 - 10 or x0 > fig_rect.x1 + 10:
            continue
        if best_dy is None or dy < best_dy:
            best_dy = dy
            best = (m.group(1), txt.strip(), fitz.Rect(x0, y0, x1, y1))
    return best


def extract(pdf_path: Path, out_dir: Path) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    manifest: list[dict] = []
    zoom = RENDER_DPI / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    for pno, page in enumerate(doc, start=1):
        clusters = cluster_drawings(page, CLUSTER_GAP_PT)
        for idx, rect in enumerate(clusters):
            cap = find_caption(page, rect)
            if cap is None:
                label = f"page{pno}_fig{idx + 1}"
                caption_text = ""
            else:
                label, caption_text, cap_rect = cap
                rect = rect | cap_rect  # include caption in crop

            rect = fitz.Rect(
                rect.x0 - CROP_PADDING_PT,
                rect.y0 - CROP_PADDING_PT,
                rect.x1 + CROP_PADDING_PT,
                rect.y1 + CROP_PADDING_PT,
            ) & page.rect

            pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
            fname = f"fig_{label.replace('.', '_')}.png"
            fpath = out_dir / fname
            pix.save(fpath)

            manifest.append({
                "label": label,
                "page": pno,
                "caption": caption_text,
                "bbox": [rect.x0, rect.y0, rect.x1, rect.y1],
                "image": str(fpath.relative_to(out_dir.parent.parent)),
                "captioned": cap is not None,
            })

    return manifest


def scan_latex_refs(latex_dir: Path) -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {}
    for tex in sorted(latex_dir.glob("*.tex")):
        for label in REF_RE.findall(tex.read_text()):
            refs.setdefault(label, []).append(tex.name)
    return refs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--latex-dir", type=Path, default=None)
    args = ap.parse_args()

    manifest = extract(args.pdf, args.out)
    refs = scan_latex_refs(args.latex_dir) if args.latex_dir else {}

    # Cross-index figures against references.
    by_label: dict[str, dict] = {m["label"]: m for m in manifest if m["captioned"]}
    report = {
        "figures": manifest,
        "references": refs,
        "matched": sorted(set(by_label) & set(refs)),
        "figures_without_refs": sorted(set(by_label) - set(refs)),
        "refs_without_figures": sorted(set(refs) - set(by_label)),
        "uncaptioned_clusters": [m["label"] for m in manifest if not m["captioned"]],
    }
    manifest_path = args.out / "manifest.json"
    manifest_path.write_text(json.dumps(report, indent=2))
    print(f"Wrote {len(manifest)} figure crops to {args.out}")
    print(f"Manifest: {manifest_path}")
    print(f"Matched labels: {report['matched']}")
    print(f"Refs without figures: {report['refs_without_figures']}")
    print(f"Figures without refs: {report['figures_without_refs']}")
    print(f"Uncaptioned clusters: {report['uncaptioned_clusters']}")


if __name__ == "__main__":
    main()
