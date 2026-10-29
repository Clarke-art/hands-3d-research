# =====================================================================================
# STAGE6B_R1B -- EXPLORATORY 3 (read-only): which limb does each blob belong to?
# =====================================================================================
import os
import sys
import json
import heapq

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
import r1a_common as RC                                             # noqa: E402

MM = 1000.0
OUT = os.path.join(S6D, "stage6b_r1b", "_tmp")
LOG = []


def log(s):
    LOG.append(s)
    print("[EX3] " + s)


ctx = B.build_context()
ref = ctx["ref"]
NV = ctx["NV"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
own = ctx["own_r1a"]
jf = ref["jf"]
AC = ref["AC"]
cap = ref["cap"]
dstar = int(cap["thumb"]["distal_most_vertex"])
thumb_cap = sorted(cap["thumb_cap_vertex_ids"])

# ---- is the joint frame's thumb TIP the R2A canonical point?
log("jf THUMB_TIP_R head = %s" % jf["THUMB_TIP_R"]["head"])
log("jf THUMB_TIP_R tail = %s" % jf["THUMB_TIP_R"]["tail"])
log("jf THUMB_IP_R  head = %s  tail = %s" % (jf["THUMB_IP_R"]["head"], jf["THUMB_IP_R"]["tail"]))
log("AC[THUMB] points = %s" % [[round(x, 6) for x in p] for p in AC["THUMB"]])

eadj = {}
for a, b in EDGES:
    w = (V0[a] - V0[b]).length
    eadj.setdefault(a, []).append((b, w))
    eadj.setdefault(b, []).append((a, w))


def dij_prev(src):
    d = {src: 0.0}
    prev = {src: None}
    pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d.get(u, 1e18) + 1e-15:
            continue
        for v, w in eadj.get(u, ()):
            if du + w < d.get(v, 1e18) - 1e-16:
                d[v] = du + w
                prev[v] = u
                heapq.heappush(pq, (du + w, v))
    return d, prev


def path(prev, src, dst):
    p = [dst]
    while p[-1] != src:
        q = prev.get(p[-1])
        if q is None:
            return None
        p.append(q)
    return p


def nv(P):
    return min(range(NV), key=lambda i: (V0[i] - P).length)


wrist = nv(AC["wrist"][0])
iidx = nv(AC["INDEX"][-1])
dW, pW = dij_prev(wrist)
dI, pI = dij_prev(iidx)

ptsT, ptsI = AC["THUMB"], AC["INDEX"]
ptsM = AC["MIDDLE"]


def desc(v):
    aT = RC.arc_of(ptsT, V0[v])
    aI = RC.arc_of(ptsI, V0[v])
    aM = RC.arc_of(ptsM, V0[v])
    return (ref["dchain"][v]["THUMB"], ref["dchain"][v]["INDEX"], aT[0], aI[0], aM[0])


log("")
log("=== geodesic path to WRIST (mm) : dThumb dIndex arcT arcI arcM   [own] ===")
for src in (dstar, 284, iidx):
    p = path(pW, wrist, src)
    log("--- from v%d (own=%s) : geodesic-to-wrist %.2f mm, %d steps"
        % (src, own[src], dW[src] * MM, len(p)))
    step = max(1, len(p) // 20)
    for k in range(0, len(p), step):
        v = p[k]
        x = desc(v)
        log("    v%-5d g=%7.2f  dT=%7.2f dI=%7.2f  aT=%7.2f aI=%7.2f aM=%7.2f  own=%s"
            % (v, dW[v] * MM, x[0], x[1], x[2], x[3], x[4], own[v]))
log("")
log("=== geodesic path from v2189 to INDEX tip (%.2f mm) ===" % (dI[dstar] * MM))
p = path(pI, iidx, dstar)
step = max(1, len(p) // 18)
for k in range(0, len(p), step):
    v = p[k]
    x = desc(v)
    log("    v%-5d g=%7.2f  dT=%7.2f dI=%7.2f  aT=%7.2f aI=%7.2f  own=%s"
        % (v, dI[v] * MM, x[0], x[1], x[2], x[3], own[v]))

# local sheet test: 3-ring around blob B, distances
def rings(src, n):
    seen = set(src)
    front = set(src)
    for _ in range(n):
        nxt = set()
        for u in front:
            for v, _ in eadj.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    nxt.add(v)
        front = nxt
    return seen - set(src)


for tag, seedset in (("BLOB_B(cap)", thumb_cap), ("BLOB_A(v284)", [284])):
    r = rings(seedset, 3)
    dTs = sorted(ref["dchain"][v]["THUMB"] for v in r)
    dIs = sorted(ref["dchain"][v]["INDEX"] for v in r)
    log("%s 3-ring n=%d : median dThumb=%.2f  median dIndex=%.2f"
        % (tag, len(r), dTs[len(dTs) // 2], dIs[len(dIs) // 2]))

json.dump({"log": LOG}, open(os.path.join(OUT, "EXPLORE_SEED3.json"), "w",
                             encoding="utf-8"), indent=1, ensure_ascii=False)
print("EXPLORE3_DONE")
