"""Composite the matched evidence for RIGHT_HAND_FIRST_WEB_TOPOLOGY_CAUSAL_PROBE_R1.

Same camera, same pose, same frame, neutral Workbench solid shading:
  baseline LEFT, probe candidate RIGHT.

Outputs
  EVIDENCE_F130_BASELINE_VS_PROBE.png          F130, both product views, plus an amplified
                                               pixel-difference panel so the reviewer can see
                                               exactly how much changed
  EVIDENCE_SIX_FRAMES_BASELINE_VS_PROBE.png    the six decision frames, both product views
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

OUT = Path(__file__).resolve().parent
RV = OUT / 'renders'
FRAMES = [110, 127, 130, 160, 176, 205]
VIEWS = [('FIRST_WEB_OBLIQUE', 'first-web oblique'),
         ('PALMAR_THENAR_CLOSE', 'palmar / thenar close')]
LABEL = {110: 'F110 baseline smooth', 127: 'F127 folded', 130: 'F130 PEAK',
         160: 'F160 folded', 176: 'F176 smooth / recovery', 205: 'F205 folded'}
VERDICT = {110: 'SMOOTH', 127: 'FOLDED', 130: 'PEAK', 160: 'FOLDED', 176: 'SMOOTH', 205: 'FOLDED'}


def load(a, f, v):
    return Image.open(RV / f'{a}__F{f:03}__{v}.png').convert('RGB')


def pairstrip(frame, view, size=(430, 394)):
    b = load('BASELINE_FROZEN', frame, view)
    p = load('PROBE_TOPOLOGY', frame, view)
    b2 = b.copy(); b2.thumbnail(size)
    p2 = p.copy(); p2.thumbnail(size)
    diff = ImageChops.difference(b, p)
    d2 = Image.eval(diff, lambda x: min(255, x * 6))
    d2.thumbnail(size)
    w = size[0] * 3 + 24
    h = size[1] + 26
    cv = Image.new('RGB', (w, h), (245, 246, 248))
    cv.paste(b2, (0, 26)); cv.paste(p2, (size[0] + 12, 26)); cv.paste(d2, (2 * size[0] + 24, 26))
    dr = ImageDraw.Draw(cv)
    dr.text((4, 4), 'BASELINE (frozen fallback)', fill=(24, 28, 34))
    dr.text((size[0] + 16, 4), 'PROBE candidate topology', fill=(24, 28, 34))
    dr.text((2 * size[0] + 28, 4), 'difference x6', fill=(120, 60, 60))
    return cv


def main():
    # 1. F130, both views
    rows = [pairstrip(130, v[0]) for v in VIEWS]
    w = max(r.size[0] for r in rows)
    h = sum(r.size[1] for r in rows) + 40
    cv = Image.new('RGB', (w, h), (245, 246, 248))
    dr = ImageDraw.Draw(cv)
    dr.text((10, 8), 'F130  PEAK frame  -  same camera / same pose / same shading; only the local first-web topology differs',
            fill=(24, 28, 34))
    y = 30
    for (view, title), r in zip(VIEWS, rows):
        dr.text((10, y + 2), f'{view}', fill=(90, 96, 105))
        cv.paste(r, (0, y + 14))
        y += r.size[1] + 12
    cv.save(OUT / 'EVIDENCE_F130_BASELINE_VS_PROBE.png')

    # 2. six frames x two views
    cells = {}
    size = (300, 275)
    for f in FRAMES:
        for view, _ in VIEWS:
            b = load('BASELINE_FROZEN', f, view); b.thumbnail(size)
            p = load('PROBE_TOPOLOGY', f, view); p.thumbnail(size)
            cell = Image.new('RGB', (size[0] * 2 + 8, size[1]), (238, 239, 242))
            cell.paste(b, (0, 0)); cell.paste(p, (size[0] + 8, 0))
            cells[(f, view)] = cell
    cw = size[0] * 2 + 8
    W = 20 + len(FRAMES) * (cw + 12)
    H = 40 + 2 * (22 + size[1] + 34)
    cv = Image.new('RGB', (W, H), (245, 246, 248))
    dr = ImageDraw.Draw(cv)
    dr.text((10, 8), 'Baseline LEFT / probe candidate RIGHT  -  identical camera per frame',
            fill=(24, 28, 34))
    for ri, (view, title) in enumerate(VIEWS):
        dr.text((10, 34 + ri * (22 + size[1] + 34)), view, fill=(90, 96, 105))
        for ci, f in enumerate(FRAMES):
            x = 10 + ci * (cw + 12)
            y = 34 + ri * (22 + size[1] + 34) + 18
            cv.paste(cells[(f, view)], (x, y))
            col = (24, 120, 60) if VERDICT[f] in ('SMOOTH',) else (170, 40, 40)
            dr.text((x, y + size[1] + 4), f'F{f} {VERDICT[f]}', fill=col)
    cv.save(OUT / 'EVIDENCE_SIX_FRAMES_BASELINE_VS_PROBE.png')
    print('EVIDENCE_READY')


main()
