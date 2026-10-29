# =====================================================================================
# STAGE6B_R1B -- Human Review render set (14 PNGs, read-only)
# =====================================================================================
import os
import sys
import json
import math

import bpy
import numpy as np
from mathutils import Vector, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s6br1b_common as K                                          # noqa: E402

OUT = os.path.join(K.S6B_R1B, "renders")
os.makedirs(OUT, exist_ok=True)
W, H = 1600, 1150
BG = np.array([0.05, 0.055, 0.065], dtype=np.float32)
GREY = (0.34, 0.36, 0.40)
LOG = []


def log(s):
    LOG.append(s)
    print("[REND] " + s, flush=True)


FONT = {
 "A":["01110","10001","10001","11111","10001","10001","10001"],"B":["11110","10001","11110","10001","10001","10001","11110"],
 "C":["01110","10001","10000","10000","10000","10001","01110"],"D":["11110","10001","10001","10001","10001","10001","11110"],
 "E":["11111","10000","11110","10000","10000","10000","11111"],"F":["11111","10000","11110","10000","10000","10000","10000"],
 "G":["01110","10001","10000","10111","10001","10001","01111"],"H":["10001","10001","11111","10001","10001","10001","10001"],
 "I":["11111","00100","00100","00100","00100","00100","11111"],"J":["00111","00010","00010","00010","00010","10010","01100"],
 "K":["10001","10010","11100","10100","10010","10010","10001"],"L":["10000","10000","10000","10000","10000","10000","11111"],
 "M":["10001","11011","10101","10101","10001","10001","10001"],"N":["10001","11001","10101","10011","10001","10001","10001"],
 "O":["01110","10001","10001","10001","10001","10001","01110"],"P":["11110","10001","10001","11110","10000","10000","10000"],
 "Q":["01110","10001","10001","10001","10101","10010","01101"],"R":["11110","10001","10001","11110","10100","10010","10001"],
 "S":["01111","10000","10000","01110","00001","00001","11110"],"T":["11111","00100","00100","00100","00100","00100","00100"],
 "U":["10001","10001","10001","10001","10001","10001","01110"],"V":["10001","10001","10001","10001","10001","01010","00100"],
 "W":["10001","10001","10001","10101","10101","11011","10001"],"X":["10001","10001","01010","00100","01010","10001","10001"],
 "Y":["10001","10001","01010","00100","00100","00100","00100"],"Z":["11111","00001","00010","00100","01000","10000","11111"],
 "0":["01110","10001","10011","10101","11001","10001","01110"],"1":["00100","01100","00100","00100","00100","00100","01110"],
 "2":["01110","10001","00001","00110","01000","10000","11111"],"3":["11111","00010","00100","00010","00001","10001","01110"],
 "4":["00010","00110","01010","10010","11111","00010","00010"],"5":["11111","10000","11110","00001","00001","10001","01110"],
 "6":["00110","01000","10000","11110","10001","10001","01110"],"7":["11111","00001","00010","00100","01000","01000","01000"],
 "8":["01110","10001","10001","01110","10001","10001","01110"],"9":["01110","10001","10001","01111","00001","00010","01100"],
 " ":["00000"]*7,"-":["00000","00000","00000","11111","00000","00000","00000"],"_":["00000"]*6+["11111"],
 ":":["00000","00100","00100","00000","00100","00100","00000"],".":["00000","00000","00000","00000","00000","01100","01100"],
 "/":["00001","00010","00010","00100","01000","01000","10000"],"+":["00000","00100","00100","11111","00100","00100","00000"],
 "=":["00000","00000","11111","00000","11111","00000","00000"],"(":["00010","00100","01000","01000","01000","00100","00010"],
 ")":["01000","00100","00010","00010","00010","00100","01000"],"*":["00000","10101","01110","11111","01110","10101","00000"],
 "%":["11001","11010","00010","00100","01000","01011","10011"],"?":["01110","10001","00001","00110","00100","00000","00100"],
 ",":["00000","00000","00000","00000","01100","00100","01000"],">":["10000","01000","00100","00010","00100","01000","10000"],
 "<":["00001","00010","00100","01000","00100","00010","00001"],"X_":["10001","10001","01010","00100","01010","10001","10001"],
}


def canvas():
    a = np.zeros((H, W, 4), dtype=np.float32)
    a[:, :, :3] = BG
    a[:, :, 3] = 1.0
    return a


def px(a, x, y, c, r=1, alpha=1.0):
    xi, yi = int(round(x)), int(round(y))
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy > r * r + 1:
                continue
            X, Y = xi + dx, yi + dy
            if 0 <= X < a.shape[1] and 0 <= Y < a.shape[0]:
                a[Y, X, :3] = a[Y, X, :3] * (1 - alpha) + np.array(c, dtype=np.float32) * alpha


def line(a, p, q, c, r=1, alpha=1.0):
    n = max(2, int(math.hypot(q[0] - p[0], q[1] - p[1]) * 1.4) + 1)
    for i in range(n + 1):
        t = i / n
        px(a, p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, c, r, alpha)


def text(a, x, y, s, size=2, c=(0.95, 0.95, 0.95), alpha=1.0):
    for ch in str(s).upper():
        g = FONT.get(ch, FONT["?"])
        for gy in range(len(g)):
            for gx in range(len(g[0])):
                if g[gy][gx] == "1":
                    for dy in range(size):
                        for dx in range(size):
                            px(a, x + gx * size + dx, y + gy * size + dy, c, 0, alpha)
        x += 6 * size
    return x


def save(a, name):
    img = bpy.data.images.new(name, width=a.shape[1], height=a.shape[0], alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(a[::-1]).reshape(-1))
    p = os.path.join(OUT, name)
    img.filepath_raw = p
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)
    log("wrote %s" % name)
    return p


class Panel(object):
    def __init__(self, a, x0, y0, w, h, V, axis):
        self.a, self.x0, self.y0, self.w, self.h = a, x0, y0, w, h
        self.V = V
        self.axis = axis
        us, vs = [], []
        for p in V:
            u, v = self.uv(p)
            us.append(u)
            vs.append(v)
        self.u0, self.u1 = min(us), max(us)
        self.v0, self.v1 = min(vs), max(vs)
        pad = 24
        self.s = min((w - 2 * pad) / max(1e-12, self.u1 - self.u0),
                     (h - 2 * pad) / max(1e-12, self.v1 - self.v0))

    def uv(self, p):
        if self.axis == "D":
            return p.x, p.z
        if self.axis == "P":
            return -p.x, p.z
        if self.axis == "R":
            return -p.y, p.z
        return p.y, p.z

    def pt(self, p):
        u, v = self.uv(p)
        return (self.x0 + (self.w - (self.u1 - self.u0) * self.s) / 2 + (u - self.u0) * self.s,
                self.y0 + (self.h - (self.v1 - self.v0) * self.s) / 2 + (v - self.v0) * self.s)

    def frame(self, title, colour=(0.85, 0.88, 0.95)):
        for xx in range(self.x0, self.x0 + self.w, 2):
            px(self.a, xx, self.y0, (0.18, 0.19, 0.22), 0)
            px(self.a, xx, self.y0 + self.h, (0.18, 0.19, 0.22), 0)
        text(self.a, self.x0 + 10, self.y0 + 8, title, 2, colour)


def legend(a, x, y, items, size=2):
    yy = y
    for lab, col in items:
        px(a, x + 6, yy + 7, col, 5)
        text(a, x + 22, yy, lab, size)
        yy += 22
    return yy


def zmap(t, lo, hi):
    t = min(1.0, max(0.0, (t - lo) / max(1e-9, hi - lo)))
    return (min(1.0, 2 * t), 1.0 - abs(2 * t - 1.0), min(1.0, 2 * (1 - t)))


# =====================================================================================
ctx = K.B.build_context()
ref = ctx["ref"]
NV = ref["NV"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
POLY = ctx["poly"]
own = ctx["own_r1a"]
ARC = ctx["ARC"]
probe = K.load_probe_sets()
PART = K.r2_partition(ctx, ref)
P2 = PART["partition"]
C = K.build_corrected_ownership(ctx, ref, P2, probe)
CORR = C["corrected"]
domain = set(C["domain"])
changed = sorted(i for i in range(NV) if CORR[i] != own[i])
cap = set(ref["cap"]["thumb_cap_vertex_ids"])
nail = set(ctx["nail"])
web = set(ctx["first_web"])

DIGCOL = {"THUMB": (0.95, 0.30, 0.20), "INDEX": (0.25, 0.55, 0.95), "MIDDLE": (0.25, 0.85, 0.45),
          "RING": (0.85, 0.35, 0.85), "LITTLE": (0.95, 0.80, 0.25), "wrist": (0.45, 0.47, 0.52)}

# ---- open the R1B weights (for weight maps) and both harnesses
bpy.ops.wm.open_mainfile(filepath=K.R1B_MASTER)
ob_m = bpy.data.objects[K.MESH_OBJ]
W_OLD = K.read_weights(ob_m, NV)
bpy.ops.wm.open_mainfile(filepath=K.R1C_MASTER)
ob_c = bpy.data.objects[K.MESH_OBJ]
W_NEW = K.read_weights(ob_c, NV)


def dom_of(W, i):
    it = sorted(W[i].items(), key=lambda kv: -kv[1])
    return it[0][0] if it else "WRIST_R"


GROUPC = {"WRIST_R": (0.45, 0.47, 0.52)}
for d in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    for n, s in enumerate(K.RC.CHAIN[d]):
        sh = [(1.0, 1.0, 1.0), (0.75, 0.80, 0.95), (0.45, 0.55, 0.95)][n]
        GROUPC["%s_%s_R" % (d, s)] = tuple(0.35 + 0.65 * v for v in
                                           tuple(np.array(DIGCOL[d]) * np.array(sh)))

# ---------------------------------------------------------------- 1. ownership before/after
a = canvas()
pn1 = Panel(a, 20, 60, 760, 1040, V0, "D")
pn1.frame("OWNERSHIP BEFORE (own_r1a)")
pn2 = Panel(a, 820, 60, 760, 1040, V0, "D")
pn2.frame("OWNERSHIP AFTER (CORRECTED_DIGIT_OWNERSHIP_R2)")
for pan, lab in ((pn1, own), (pn2, CORR)):
    for i in range(NV):
        x, y = pan.pt(V0[i])
        px(a, x, y, DIGCOL[lab[i]], 2)
text(a, 20, 22, "STAGE6B_R1B_OWNERSHIP_BEFORE_AFTER   DORSAL VIEW   CORRECTED VERTICES=%d" % len(changed), 3)
text(a, 20, 1122, "RED=THUMB  BLUE=INDEX  GREEN=MIDDLE  MAGENTA=RING  YELLOW=LITTLE  GREY=WRIST", 2)
save(a, "STAGE6B_R1B_OWNERSHIP_BEFORE_AFTER.png")

# ---------------------------------------------------------------- 2. class-B vertex weight before/after
cb_v = sorted(set([v for _k, a_, b_ in probe["CLASS_B"] for v in (a_, b_)]))
a = canvas()
pn1 = Panel(a, 20, 60, 760, 1040, V0, "D")
pn1.frame("DOMINANT BIND GROUP BEFORE (Stage5B R1B)")
pn2 = Panel(a, 820, 60, 760, 1040, V0, "D")
pn2.frame("DOMINANT BIND GROUP AFTER (Stage5B R1C candidate)")
for pan in (pn1, pn2):
    for i in range(NV):
        x, y = pan.pt(V0[i])
        px(a, x, y, (0.22, 0.23, 0.26), 2)
for pan, WW in ((pn1, W_OLD), (pn2, W_NEW)):
    for i in cb_v:
        x, y = pan.pt(V0[i])
        px(a, x, y, GROUPC.get(dom_of(WW, i), (1, 1, 1)), 4)
for pan, WW in ((pn2, W_NEW),):
    for i in changed:
        x, y = pan.pt(V0[i])
        px(a, x, y, (1.0, 1.0, 1.0), 6, 0.35)
text(a, 20, 22, "STAGE6B_R1B_CLASS_B_VERTEX_WEIGHT_BEFORE_AFTER   (%d CLASS_B endpoints)" % len(cb_v), 3)
text(a, 20, 1122, "BIG DOTS = the exact CLASS_B edge endpoint set   WHITE HALO = vertices whose bind weights changed", 2)
save(a, "STAGE6B_R1B_CLASS_B_VERTEX_WEIGHT_BEFORE_AFTER.png")

# ---------------------------------------------------------------- 3. first web protection
a = canvas()
pn = Panel(a, 60, 60, 1000, 1040, V0, "D")
pn.frame("FIRST_WEB PROTECTION (approved mask, verbatim)")
for i in range(NV):
    x, y = pn.pt(V0[i])
    px(a, x, y, GREY, 2)
for i in sorted(cap):
    x, y = pn.pt(V0[i])
    px(a, x, y, (0.85, 0.20, 0.95), 7)
for i in sorted(nail):
    x, y = pn.pt(V0[i])
    px(a, x, y, (0.95, 0.90, 0.25), 5)
for i in sorted(web):
    x, y = pn.pt(V0[i])
    px(a, x, y, (0.15, 0.95, 0.85), 8)
for k, i, j in probe["CLASS_A"]:
    line(a, pn.pt(V0[i]), pn.pt(V0[j]), (0.10, 0.95, 0.25), 3)
for k, i, j in probe["CLASS_B"]:
    line(a, pn.pt(V0[i]), pn.pt(V0[j]), (1.0, 0.35, 0.05), 1)
for i in changed:
    x, y = pn.pt(V0[i])
    px(a, x, y, (1.0, 1.0, 1.0), 3, 0.25)
fwv = json.load(open(os.path.join(K.S5B_R1C, "STAGE5B_R1C_FIRST_WEB_PROTECTION_AUDIT.json"),
                     encoding="utf-8"))
legend(a, 1090, 100, [("FIRST_WEB (21) UNCHANGED", (0.15, 0.95, 0.85)),
                      ("THUMB DISTAL CAP (9) = THUMB", (0.85, 0.20, 0.95)),
                      ("THUMB NAIL (22) = THUMB", (0.95, 0.90, 0.25)),
                      ("CLASS_A 6 = DO_NOT_CUT", (0.10, 0.95, 0.25)),
                      ("HISTORIC CLASS_B 61 probe", (1.0, 0.35, 0.05))])
text(a, 1090, 100 + 22 * 5 + 30,
     "FIRST_WEB REWEIGHTED = %d" % len(fwv["first_web_vertices_reweighted"]), 2)
text(a, 1090, 100 + 22 * 5 + 56,
     "FIRST_WEB THUMB_IP = %.3f" % fwv["FIRST_WEB_THUMB_IP_WEIGHT"], 2)
text(a, 1090, 100 + 22 * 5 + 82,
     "WHITELIST INTACT = %s" % fwv["approved_first_web_whitelist_intact"], 2)
text(a, 20, 22, "STAGE6B_R1B_FIRST_WEB_PROTECTION   DORSAL", 3)
save(a, "STAGE6B_R1B_FIRST_WEB_PROTECTION.png")
json.dump({"log": LOG}, open(os.path.join(K.S6B_R1B, "_tmp", "R1B_RENDER_PART1.json"), "w",
                             encoding="utf-8"), indent=1, ensure_ascii=False)
print("RENDER_PART1_DONE")
