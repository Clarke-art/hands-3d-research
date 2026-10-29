# =====================================================================================
# STAGE6B_R1B -- EXPLORATORY (read-only): is the R1A 2-source geodesic seed reliable?
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
           os.path.join(S6D, "stage6b_r1a_seam_provenance", "scripts"),
           os.path.join(PROD, "stage5_production_rig", "stage5b_r1b", "scripts"),
           os.path.join(PROD, "stage5_production_rig", "stage5b_r1a", "scripts")):
    if _p not in sys.path:
        sys.path.append(_p)

import s6b_common as B                                              # noqa: E402
import r1a_common as RC                                             # noqa: E402
import r1b_common as RB                                             # noqa: E402

MM = 1000.0
OUT = os.path.join(S6D, "stage6b_r1b", "_tmp")

ctx = B.build_context()
ref = ctx["ref"]
NV = ctx["NV"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
own = ctx["own_r1a"]
ARC = ctx["ARC"]
jf = ref["jf"]
AC = ref["AC"]
cap = ref["cap"]

# ---- adjacency / dijkstra
eadj = {}
for a, b in EDGES:
    w = (V0[a] - V0[b]).length
    eadj.setdefault(a, []).append((b, w))
    eadj.setdefault(b, []).append((a, w))


def dij_multi(srcs):
    d = {}
    pq = []
    for s in srcs:
        d[s] = 0.0
        heapq.heappush(pq, (0.0, s))
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


LOG = []


def log(s):
    LOG.append(s)
    print("[EXPLORE] " + s)


# ---- landmark candidates
res = {}
for D in ["THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"]:
    pts = AC[D]
    v_tipbone = nv(pts[-1])
    res[D] = {"chain_tip_xyz": [round(x, 6) for x in pts[-1]],
              "v_nearest_tiphead": v_tipbone,
              "dist_to_tiphead_mm": round((V0[v_tipbone] - pts[-1]).length * MM, 4)}
v_wrist = nv(AC["wrist"][0])
log("nearest-to-chain-tip vertices: " + json.dumps(res))
log("wrist seed v%d" % v_wrist)

thumb_cap = sorted(cap["thumb_cap_vertex_ids"])
log("thumb cap ids (%d): %s" % (len(thumb_cap), thumb_cap[:12]))
dstar = int(cap["thumb"]["distal_most_vertex"])
log("thumb D* = v%d" % dstar)

g = {}
g["v284_tiphead_T"] = dij_multi([res["THUMB"]["v_nearest_tiphead"]])
g["vDstar_T"] = dij_multi([dstar])
g["vCap_T"] = dij_multi(thumb_cap)
g["vTip_I"] = dij_multi([res["INDEX"]["v_nearest_tiphead"]])
g["vWrist"] = dij_multi([v_wrist])
for D in ["MIDDLE", "RING", "LITTLE"]:
    g["vTip_" + D[:2]] = dij_multi([res[D]["v_nearest_tiphead"]])

tt = res["THUMB"]["v_nearest_tiphead"]
ti = res["INDEX"]["v_nearest_tiphead"]
log("geodesic  vTipHead_T(v%d) <-> vDstar(v%d)   = %.3f mm" % (tt, dstar, g["vDstar_T"][tt] * MM))
log("geodesic  vTipHead_T      <-> thumbCAP(set) = %.3f mm" % (g["vCap_T"][tt] * MM))
log("geodesic  vDstar          <-> thumbCAP(set) = %.3f mm" % (g["vCap_T"][dstar] * MM))
log("geodesic  vTipHead_T      <-> vTipHead_I    = %.3f mm" % (g["vTip_I"][tt] * MM))
log("geodesic  vDstar          <-> vTipHead_I    = %.3f mm" % (g["vTip_I"][dstar] * MM))
log("geodesic  thumbCAP(set)   <-> vTipHead_I    = %.3f mm" % (min(g["vTip_I"][c] for c in thumb_cap) * MM))
log("geodesic  vTipHead_T      <-> wrist         = %.3f mm" % (g["vWrist"][tt] * MM))
log("geodesic  vDstar          <-> wrist         = %.3f mm" % (g["vWrist"][dstar] * MM))

# ---- the 61 CLASS_B edges: what do the two candidate thumb seeds say?
CB = json.load(open(os.path.join(S6D, "stage6b_r1a_seam_provenance",
                                 "STAGE6B_R1A_CLASS_B_OWNERSHIP_MISCLASSIFICATION.json"),
                    encoding="utf-8"))
verts = sorted(set([e["endpoints"]["v0"] for e in CB["edges"]] +
                   [e["endpoints"]["v1"] for e in CB["edges"]]))
log("CLASS_B endpoint vertices: %d" % len(verts))
log("%-6s %-6s %-7s | %10s %10s %10s %10s %10s" %
    ("vert", "own", "region", "g_tipheadT", "g_dstarT", "g_capT", "g_tipI", "g_wrist"))
for v in verts:
    rg = []
    if v in ctx["nail"]:
        rg.append("nail")
    if v in ctx["cap"]:
        rg.append("cap")
    if v in ctx["distal"]:
        rg.append("distal")
    log("v%-5d %-6s %-7s | %10.2f %10.2f %10.2f %10.2f %10.2f" %
        (v, own[v], ",".join(rg) or "-",
         g["v284_tiphead_T"][v] * MM, g["vDstar_T"][v] * MM, g["vCap_T"][v] * MM,
         g["vTip_I"][v] * MM, g["vWrist"][v] * MM))

# ---- how big is the geodesically-detached sheet around vTipHead_T?
# vertices geodesically closer to thumb tiphead than to any other source
all_src = {"THUMB": tt, "INDEX": ti, "MIDDLE": res["MIDDLE"]["v_nearest_tiphead"],
           "RING": res["RING"]["v_nearest_tiphead"], "LITTLE": res["LITTLE"]["v_nearest_tiphead"],
           "wrist": v_wrist}
gs = dict((k, dij_multi([v])) for k, v in all_src.items())
part = []
for i in range(NV):
    best = min(gs.items(), key=lambda kv: kv[1][i])
    part.append(best[0])
from collections import Counter
log("partition (tiphead seeds) counts: %s" % dict(Counter(part)))
# component structure of the THUMB basin
import sys as _s


def components(ids):
    s = set(ids)
    seen = set()
    comps = []
    for v in s:
        if v in seen:
            continue
        st = [v]
        c = set()
        while st:
            u = st.pop()
            if u in c:
                continue
            c.add(u)
            for w, _ in eadj.get(u, ()):
                if w in s and w not in c:
                    st.append(w)
        seen |= c
        comps.append(c)
    return sorted(comps, key=len, reverse=True)


for tag, lab in (("THUMB_tiphead", "THUMB"),):
    ids = [i for i in range(NV) if part[i] == lab]
    comps = components(ids)
    log("%s basin: %d verts in %d components; sizes=%s" %
        (tag, len(ids), len(comps), [len(c) for c in comps[:8]]))

# same with the D* / cap seed for the thumb
all_src2 = dict(all_src)
all_src2["THUMB"] = dstar
gs2 = dict((k, dij_multi([v])) for k, v in all_src2.items())
part2 = [min(gs2.items(), key=lambda kv: kv[1][i])[0] for i in range(NV)]
log("partition (D* thumb seed) counts: %s" % dict(Counter(part2)))
ids2 = [i for i in range(NV) if part2[i] == "THUMB"]
comps2 = components(ids2)
log("THUMB(D*) basin: %d verts in %d components; sizes=%s" %
    (len(ids2), len(comps2), [len(c) for c in comps2[:8]]))

json.dump({"log": LOG, "landmarks": res, "wrist_seed": v_wrist,
           "thumb_cap_ids": thumb_cap, "dstar": dstar,
           "partition_tiphead": dict(Counter(part)),
           "partition_dstar": dict(Counter(part2)),
           "changed_vs_own_r1a_tiphead": sum(1 for i in range(NV) if part[i] != own[i]),
           "changed_vs_own_r1a_dstar": sum(1 for i in range(NV) if part2[i] != own[i]),
           }, open(os.path.join(OUT, "EXPLORE_SEED.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("EXPLORE_DONE")
