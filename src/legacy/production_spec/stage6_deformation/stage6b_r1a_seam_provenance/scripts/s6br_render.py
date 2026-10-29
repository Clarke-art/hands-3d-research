# =====================================================================================
# STAGE6B_R1A -- diagnostic seam maps (READ-ONLY; the exploded view is a copy only)
# =====================================================================================
# The 67 edges are drawn with their real class colour, together with the THUMB / INDEX /
# FIRST_WEB / NAIL / DISTAL_CAP regions.  Nothing is written back to any blend.
# =====================================================================================
import os
import sys
import json
import math

import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s6br_common as F                                              # noqa: E402

OUTDIR = F.S6B_R1A
REND = os.path.join(OUTDIR, "renders")
os.makedirs(REND, exist_ok=True)
MM = F.MM
LOG = []


def log(s):
    LOG.append(s)
    print("[S6BR-REND] " + s)


ctx = F.B.build_context()
NV = ctx["NV"]
ref = ctx["ref"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
own = ctx["own_r1a"]
ARC = ctx["ARC"]
NAIL, CAP, WEB, THENAR = ctx["nail"], ctx["cap"], ctx["first_web"], ctx["thenar"]
DISTAL, PROXIMAL = ctx["distal"], ctx["proximal"]
SEAM = sorted(k for k, (a, b) in enumerate(EDGES) if {own[a], own[b]} == {"THUMB", "INDEX"})

AUD = json.load(open(os.path.join(OUTDIR, "STAGE6B_R1A_SEAM_EDGE_TOPOLOGY_AUDIT.json"),
                     encoding="utf-8"))
CLS = dict((r["edge_id"], r["classification"]) for r in AUD["edges"])

COL = {
    "CLASS_A": (0.10, 0.85, 0.25),      # green  - anatomical first web transition
    "CLASS_B": (1.00, 0.35, 0.05),      # orange - ownership misclassification
    "CLASS_C": (0.95, 0.05, 0.95),      # magenta- invalid cross link (none present)
    "CLASS_D": (0.20, 0.45, 1.00),      # blue   - ambiguous (none present)
}
BG = (0.09, 0.10, 0.12)
WIRE = (0.30, 0.32, 0.36)
REG_COL = {"THUMB_OWN": (0.62, 0.20, 0.20), "INDEX_OWN": (0.20, 0.42, 0.62),
           "FIRST_WEB": (0.20, 0.95, 0.85), "NAIL": (1.0, 0.85, 0.1),
           "DISTAL_CAP": (0.75, 0.45, 1.0), "THENAR": (0.35, 0.55, 0.35)}
TXT = (0.96, 0.96, 0.96)


def canvas(w, h):
    a = np.zeros((h, w, 4), dtype=np.float32)
    a[:, :, 0], a[:, :, 1], a[:, :, 2], a[:, :, 3] = BG[0], BG[1], BG[2], 1.0
    return a


def px(a, x, y, c, rad=1, alpha=1.0):
    h, w = a.shape[0], a.shape[1]
    xi, yi = int(round(x)), int(round(y))
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if dx * dx + dy * dy > rad * rad + 1:
                continue
            X, Y = xi + dx, yi + dy
            if 0 <= X < w and 0 <= Y < h:
                a[Y, X, 0] = a[Y, X, 0] * (1 - alpha) + c[0] * alpha
                a[Y, X, 1] = a[Y, X, 1] * (1 - alpha) + c[1] * alpha
                a[Y, X, 2] = a[Y, X, 2] * (1 - alpha) + c[2] * alpha


def line(a, p, q, c, rad=1, alpha=1.0):
    d = math.hypot(q[0] - p[0], q[1] - p[1])
    n = max(2, int(d * 1.2) + 1)
    for i in range(n + 1):
        t = i / n
        px(a, p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, c, rad, alpha)


FONT = {}


def text(a, x, y, s, size=16, c=TXT, alpha=1.0):
    """5x7 bitmap font, scaled.  Uppercase only; unknown glyphs fall back to '?'."""
    s = str(s).upper()
    for ch in s:
        glyph = FONT5x7.get(ch, FONT5x7.get("?"))
        for gy in range(7):
            for gx in range(5):
                if glyph[gy][gx] == "1":
                    for dy in range(size):
                        for dx in range(size):
                            px(a, x + gx * size + dx, y + gy * size + dy, c, 0, alpha)
        x += 6 * size
    return x


FONT5x7 = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "11110", "10001", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "11110", "10000", "10000", "10000", "11111"],
    "F": ["11111", "10000", "11110", "10000", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "11111", "10001", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "11100", "10100", "10010", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "_": ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    ":": ["00000", "00100", "00100", "00000", "00100", "00100", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "x": ["00000", "10001", "01010", "00100", "01010", "10001", "00000"],
    "*": ["00000", "10101", "01110", "11111", "01110", "10101", "00000"],
    "?": ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
}


def save(a, name):
    h, w = a.shape[0], a.shape[1]
    img = bpy.data.images.new(name, width=w, height=h, alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(a[::-1]).reshape(-1))
    p = os.path.join(REND, name)
    img.filepath_raw = p
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)
    log("wrote %s" % name)
    return p


# ------------------------------------------------------------------ projection helpers
def make_view(axis, flip_h=False, zoom=None):
    """axis: 'D' dorsal (+Y viewer), 'P' palmar, 'R' radial, 'U' ulnar."""
    def proj(p):
        if axis == "D":
            u, v = p.x, p.z
        elif axis == "P":
            u, v = -p.x, p.z
        elif axis == "R":
            u, v = -p.y, p.z
        else:
            u, v = p.y, p.z
        return (-u if flip_h else u), v
    pts = [proj(v) for v in V0]
    us = [q[0] for q in pts]
    vs = [q[1] for q in pts]
    if zoom is not None:
        cx, cy, hw, hh = zoom
        box = (cx - hw, cx + hw, cy - hh, cy + hh)
    else:
        box = (min(us), max(us), min(vs), max(vs))
    return proj, pts, box


def draw_view(axis, W, H, title, zoom=None, exploded=0.0, flip_h=False, show_wire=True):
    a = canvas(W, H)
    proj, pts, box = make_view(axis, flip_h=flip_h, zoom=zoom)
    u0, u1, v0, v1 = box
    su = (W - 80) / max(1e-6, (u1 - u0))
    sv = (H - 140) / max(1e-6, (v1 - v0))
    s = min(su, sv)
    ox = 40 - u0 * s
    oy = 70 - v0 * s

    def P(i, off=(0.0, 0.0, 0.0)):
        u, v = proj(Vector((V0[i].x + off[0], V0[i].y + off[1], V0[i].z + off[2])))
        return (ox + u * s, oy + v * s)

    # region shading (before the wireframe)
    if exploded == 0.0:
        for nm, ids, col, rad in (("THUMB_OWN", [i for i in range(NV) if own[i] == "THUMB"],
                                  REG_COL["THUMB_OWN"], 1),
                                 ("INDEX_OWN", [i for i in range(NV) if own[i] == "INDEX"],
                                  REG_COL["INDEX_OWN"], 1),
                                 ("THENAR", sorted(THENAR), REG_COL["THENAR"], 1),
                                 ("FIRST_WEB", sorted(WEB), REG_COL["FIRST_WEB"], 3),
                                 ("NAIL", sorted(NAIL), REG_COL["NAIL"], 3),
                                 ("DISTAL_CAP", sorted(CAP), REG_COL["DISTAL_CAP"], 3)):
            for i in ids:
                px(a, *P(i), col, rad, 0.55)

    if show_wire:
        for (x, y) in EDGES:
            line(a, P(x), P(y), WIRE, 0, 0.30)

    # the 67 edges, thick + class coloured
    for k in SEAM:
        x, y = EDGES[k]
        off = (0.0, 0.0, 0.0)
        if exploded:
            # diagnostic only: push the two sheets apart along the local separation axis
            off = (exploded, 0.0, 0.0) if own[x] == "INDEX" else (0.0, 0.0, 0.0)
        line(a, P(x, off), P(y, off), COL[CLS[k]], 3, 1.0)

    text(a, 20, H - 30, title, 3)
    na = sum(1 for k in SEAM if CLS[k] == "CLASS_A")
    nb = sum(1 for k in SEAM if CLS[k] == "CLASS_B")
    nc = sum(1 for k in SEAM if CLS[k] == "CLASS_C")
    nd = sum(1 for k in SEAM if CLS[k] == "CLASS_D")
    legend = [(COL["CLASS_A"], "A ANATOMIC FIRST WEB TRANSITION  N=%d" % na),
              (COL["CLASS_B"], "B SEMANTIC OWNERSHIP MISCLASSIFICATION  N=%d" % nb),
              (COL["CLASS_C"], "C ANATOMICALLY INVALID CROSS LINK  N=%d" % nc),
              (COL["CLASS_D"], "D AMBIGUOUS  N=%d" % nd),
              ((0.75, 0.75, 0.75), "GREY = ALL 6828 MESH EDGES"),
              [(0.62, 0.20, 0.20), "RED = THUMB-OWNED"],
              [(0.20, 0.42, 0.62), "BLUE = INDEX-OWNED"],
              [(0.20, 0.95, 0.85), "CYAN = FIRST WEB"],
              [(1.0, 0.85, 0.1), "YELLOW = NAIL"],
              [(0.75, 0.45, 1.0), "PURPLE = DISTAL CAP"]]
    yy = 20
    for i, (c, ln) in enumerate(legend):
        if i < 4:
            px(a, 26, yy + 6, c, 6, 1.0)
        text(a, 44, yy, ln, 1, c)
        yy += 17
    return a


# ------------------------------------------------------------------ individual views
FULL = None
views = [("D", "STAGE6B_R1A_SEAM_MAP_DORSAL.png", "SEAM MAP - DORSAL VIEW (+Y, right hand)"),
         ("P", "STAGE6B_R1A_SEAM_MAP_PALMAR.png", "SEAM MAP - PALMAR VIEW (-Y, right hand)"),
         ("R", "STAGE6B_R1A_SEAM_MAP_RADIAL.png", "SEAM MAP - RADIAL VIEW (+X, thumb side)"),
         ("U", "STAGE6B_R1A_SEAM_MAP_ULNAR.png", "SEAM MAP - ULNAR VIEW (-X, little side)")]
for axis, name, title in views:
    a = draw_view(axis, 1000, 1000, title)
    save(a, name)

# close-up: thumb distal + index MCP contact zone
mids = [(V0[EDGES[k][0]] + V0[EDGES[k][1]]) * 0.5 for k in SEAM]
cx = sum((p.x for p in mids)) / len(mids)
cy = sum((p.z for p in mids)) / len(mids)
a = draw_view("D", 1000, 1000, "SEAM MAP - THUMB DISTAL / INDEX MCP CONTACT CLOSE-UP",
              zoom=(cx, cy, 0.048, 0.040))
save(a, "STAGE6B_R1A_SEAM_MAP_CLOSEUP.png")

a = draw_view("D", 1000, 1000,
              "SEAM MAP - EXPLODED DIAGNOSTIC ONLY (INDEX sheet offset, NOT real geometry)",
              exploded=0.030)
save(a, "STAGE6B_R1A_SEAM_MAP_EXPLODED.png")

# composite anatomy map: dorsal | palmar | closeup
TW, TH = 760, 1000
tiles = [draw_view("D", TW, TH, "ANATOMY MAP - DORSAL", show_wire=False),
         draw_view("P", TW, TH, "ANATOMY MAP - PALMAR", show_wire=False),
         draw_view("D", TW, TH, "ANATOMY MAP - CONTACT CLOSE-UP", zoom=(cx, cy, 0.048, 0.040),
                   show_wire=False)]
comp = np.zeros((TH, TW * 3, 4), dtype=np.float32)
for i, t in enumerate(tiles):
    comp[:, i * TW:(i + 1) * TW] = t
save(comp, "STAGE6B_R1A_THUMB_INDEX_SEAM_67_EDGE_ANATOMY_MAP.png")

json.dump({"renders": sorted(f for f in os.listdir(REND) if f.endswith(".png")),
           "class_colours": dict((k, list(v)) for k, v in COL.items()),
           "class_counts": dict((c, sum(1 for k in SEAM if CLS[k] == c))
                                for c in ("CLASS_A", "CLASS_B", "CLASS_C", "CLASS_D")),
           "exploded_view": "EXPLODED_DIAGNOSTIC_ONLY - a copy for visualisation, the real mesh "
                            "is untouched",
           "log": LOG},
          open(os.path.join(OUTDIR, "_tmp", "S6BR_RENDER_LOG.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("S6BR_RENDER_DONE")
