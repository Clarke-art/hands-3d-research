# =====================================================================================
# STAGE6B_R1B -- EXPLORATORY 8 (read-only): where are the ownership changes?
# =====================================================================================
import os
import sys
import json
import heapq
from collections import Counter

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S6D = os.path.join(PROD, "stage6_deformation")
for _p in (os.path.join(S6D, "stage6b", "scripts"),
           os.path.join(PROD, "stage5_production_rig", "stage5b_r1b", "scripts"),
           os.path.join(PROD, "stage5_production_rig", "stage5b_r1a", "scripts")):
    if _p not in sys.path:
        sys.path.append(_p)
import s6b_common as B                                              # noqa: E402

MM = 1000.0
OUT = os.path.join(S6D, "stage6b_r1b", "_tmp")
LOG = []


def log(s):
    LOG.append(s)
    print("[EX8] " + s)


ctx = B.build_context()
ref = ctx["ref"]
NV = ctx["NV"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
own = ctx["own_r1a"]
AC = ref["AC"]
dth = ctx["dth"]

log("own_r1a counts: %s" % dict(Counter(own)))

eadj = {}
for a, b in EDGES:
    w = (V0[a] - V0[b]).length
    eadj.setdefault(a, []).append((b, w))
    eadj.setdefault(b, []).append((a, w))


def dij(s):
    d = {s: 0.0}
    pq = [(0.0, s)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d.get(u, 1e18) + 1e-15:
            continue
        for v, w in eadj.get(u, ()):
            if du + w < d.get(v, 1e18) - 1e-16:
                d[v] = du + w
                heapq.heappush(pq, (du + w, v))
    return d


def nv(P):
    return min(range(NV), key=lambda i: (V0[i] - P).length)


SEEDS = dict((D, nv(AC[D][-1])) for D in ["THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"])
SEEDS["wrist"] = nv(AC["wrist"][0])
GS = dict((k, dij(v)) for k, v in SEEDS.items())
part = [min(GS.items(), key=lambda kv: kv[1][i])[0] for i in range(NV)]
chg = [i for i in range(NV) if part[i] != own[i]]
log("R2 partition counts: %s" % dict(Counter(part)))
log("changed vs own_r1a: %d" % len(chg))
log("change pairs: %s" % dict(Counter((own[i], part[i]) for i in chg)))

# spatial extent of the changes: histogram of dThumb for THUMB-ward changes
thw = [i for i in chg if part[i] == "THUMB"]
idxw = [i for i in chg if part[i] == "INDEX"]
log("THUMB-ward changes %d ; INDEX-ward changes %d" % (len(thw), len(idxw)))
if thw:
    dd = sorted(dth[i] for i in thw)
    log("THUMB-ward: dThumb median %.2f  p95 %.2f  max %.2f" %
        (dd[len(dd) // 2], dd[int(0.95 * (len(dd) - 1))], dd[-1]))
if idxw:
    dd = sorted(dth[i] for i in idxw)
    log("INDEX-ward: dThumb median %.2f  p95 %.2f  max %.2f" %
        (dd[len(dd) // 2], dd[int(0.95 * (len(dd) - 1))], dd[-1]))

# how many changed vertices are inside the "flagged neighbourhood" (6 rings of the 84)?
P = os.path.join(S6D, "stage6b_r1a_seam_provenance")
CB = json.load(open(os.path.join(P, "STAGE6B_R1A_CLASS_B_OWNERSHIP_MISCLASSIFICATION.json"),
                    encoding="utf-8"))
CA = json.load(open(os.path.join(P, "STAGE6B_R1A_CLASS_A_VALID_WEB_EDGES.json"), encoding="utf-8"))
seed84 = set([e["endpoints"]["v0"] for e in CB["edges"]] +
             [e["endpoints"]["v1"] for e in CB["edges"]] +
             [e["endpoints"]["v0"] for e in CA["edges"]] +
             [e["endpoints"]["v1"] for e in CA["edges"]])
seen = set(seed84)
front = set(seed84)
for _ in range(6):
    nxt = set()
    for u in front:
        for v, _w in eadj.get(u, ()):
            if v not in seen:
                seen.add(v)
                nxt.add(v)
    front = nxt
inband = [i for i in chg if i in seen]
outside = [i for i in chg if i not in seen]
log("changed inside 6-ring of the 84 flagged vertices: %d ; outside: %d"
    % (len(inband), len(outside)))
log("outside-change pairs: %s" % dict(Counter((own[i], part[i]) for i in outside)))

# where are the outside changes? bucket by dThumb
if outside:
    for lo, hi in ((0, 10), (10, 20), (20, 30), (30, 60), (60, 200)):
        c = [i for i in outside if lo <= dth[i] < hi]
        log("  dThumb [%d,%d): %d  %s" % (lo, hi, len(c),
                                          dict(Counter((own[i], part[i]) for i in c))))

json.dump({"seeds": SEEDS, "counts": dict(Counter(part)),
           "changed": len(chg), "pairs": dict(("%s->%s" % k, v)
                                              for k, v in Counter((own[i], part[i])
                                                                  for i in chg).items()),
           "outside_changed": len(outside), "inside_changed": len(inband),
           "log": LOG},
          open(os.path.join(OUT, "EXPLORE_CHANGED.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("EXPLORE8_DONE")
