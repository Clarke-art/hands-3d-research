# =====================================================================================
# STAGE6B_R1B -- EXPLORATORY 2 (read-only): what are the two geodesic clusters?
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
import r1a_common as RC                                             # noqa: E402

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
dstar = int(cap["thumb"]["distal_most_vertex"])
thumb_cap = sorted(cap["thumb_cap_vertex_ids"])

eadj = {}
for a, b in EDGES:
    w = (V0[a] - V0[b]).length
    eadj.setdefault(a, []).append((b, w))
    eadj.setdefault(b, []).append((a, w))


def dij(srcs):
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
    print("[EX2] " + s)


SEEDS = {}
for D in ["THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"]:
    SEEDS[D] = nv(AC[D][-1])
SEEDS["wrist"] = nv(AC["wrist"][0])
log("seeds: %s" % SEEDS)

# landmark set
LM = [284, 2189, 1076, 151, 1061, 1074, 2192, 2569, 2577, 158,
      SEEDS["INDEX"], SEEDS["MIDDLE"], SEEDS["RING"], SEEDS["LITTLE"], SEEDS["wrist"]]
G = dict((v, dij([v])) for v in LM)
log("")
log("=== spatial (mm) vs geodesic (mm) between landmarks ===")
log("%-8s %-8s %10s %10s" % ("a", "b", "spatial", "geodesic"))
for i in range(len(LM)):
    for j in range(i + 1, len(LM)):
        a, b = LM[i], LM[j]
        if (V0[a] - V0[b]).length * MM < 60.0:
            log("v%-7d v%-7d %10.3f %10.3f" %
                (a, b, (V0[a] - V0[b]).length * MM, G[a][b] * MM))

log("")
log("=== spatial distance / arc coordinate of key vertices ===")
ptsT = AC["THUMB"]
ptsI = AC["INDEX"]
log("%-8s %-6s %-7s %38s | %10s %10s %10s %10s" %
    ("vert", "own", "region", "world_xyz", "|dThumb", "|dIndex", "arcT", "arcI"))
for v in LM + sorted(ctx["nail"])[:6]:
    aT = RC.arc_of(ptsT, V0[v])
    aI = RC.arc_of(ptsI, V0[v])
    rg = []
    if v in ctx["nail"]:
        rg.append("nail")
    if v in ctx["cap"]:
        rg.append("cap")
    if v in ctx["distal"]:
        rg.append("distal")
    log("v%-7d %-6s %-7s %38s | %10.3f %10.3f %10.3f %10.3f" %
        (v, own[v], ",".join(rg) or "-", str([round(x, 5) for x in V0[v]]),
         ref["dchain"][v]["THUMB"] * MM, ref["dchain"][v]["INDEX"] * MM, aT[0], aI[0]))

# ---- 1-ring composition of v284 and v2189
for v in (284, 2189, 1076):
    nb = sorted(w for w, _ in eadj[v])
    log("1-ring of v%d: %s  own=%s" % (v, nb, [own[w] for w in nb]))

# ---- partition under three thumb seed choices, and what the 84 vertices get
CB = json.load(open(os.path.join(S6D, "stage6b_r1a_seam_provenance",
                                 "STAGE6B_R1A_CLASS_B_OWNERSHIP_MISCLASSIFICATION.json"),
                    encoding="utf-8"))
verts84 = sorted(set([e["endpoints"]["v0"] for e in CB["edges"]] +
                     [e["endpoints"]["v1"] for e in CB["edges"]]))
CA = json.load(open(os.path.join(S6D, "stage6b_r1a_seam_provenance",
                                 "STAGE6B_R1A_CLASS_A_VALID_WEB_EDGES.json"),
                    encoding="utf-8"))
vertsA = sorted(set([e["endpoints"]["v0"] for e in CA["edges"]] +
                    [e["endpoints"]["v1"] for e in CA["edges"]]))

VARIANTS = {
    "tiphead": {"THUMB": [SEEDS["THUMB"]]},
    "dstar": {"THUMB": [dstar]},
    "capset": {"THUMB": thumb_cap},
    "tiphead+cap": {"THUMB": [SEEDS["THUMB"]] + thumb_cap},
}
other = dict((D, [SEEDS[D]]) for D in ["INDEX", "MIDDLE", "RING", "LITTLE", "wrist"])

summary = {}
for tag, tseed in VARIANTS.items():
    srcs = dict(other)
    srcs.update(tseed)
    gs = dict((k, dij(v)) for k, v in srcs.items())
    part = [min(gs.items(), key=lambda kv: kv[1][i])[0] for i in range(NV)]
    cnt = dict(Counter(part))
    # 67-edge same-digit check (edges are the union of the 6 CLASS_A + 61 CLASS_B)
    all67 = [(e["edge_id"], e["endpoints"]["v0"], e["endpoints"]["v1"])
             for e in CB["edges"]] + \
            [(e["edge_id"], e["endpoints"]["v0"], e["endpoints"]["v1"])
             for e in CA["edges"]]
    mixed = [(k, part[a], part[b]) for k, a, b in all67 if part[a] != part[b]]
    clsA_mixed = [(k, part[a], part[b]) for k, a, b in
                  [(e["edge_id"], e["endpoints"]["v0"], e["endpoints"]["v1"])
                   for e in CA["edges"]] if part[a] != part[b]]
    # thumb cap / nail assignment
    caplab = Counter(part[v] for v in thumb_cap)
    naillab = Counter(part[v] for v in ctx["nail"])
    log("")
    log("### variant %-12s partition=%s" % (tag, cnt))
    log("    changed vs own_r1a = %d ; mixed-label among 67 edges = %d %s"
        % (sum(1 for i in range(NV) if part[i] != own[i]), len(mixed),
           (mixed[:6] if mixed else "")))
    log("    CLASS_A 6 mixed = %d %s" % (len(clsA_mixed), clsA_mixed))
    log("    thumb cap labels=%s ; thumb nail labels=%s" % (dict(caplab), dict(naillab)))
    summary[tag] = {"partition": cnt, "changed_vs_own_r1a": sum(1 for i in range(NV) if part[i] != own[i]),
                    "mixed67": len(mixed), "mixed_classA": len(clsA_mixed),
                    "cap_labels": dict(caplab), "nail_labels": dict(naillab),
                    "v84_labels": dict((v, part[v]) for v in verts84),
                    "vA_labels": dict((v, part[v]) for v in vertsA)}

json.dump({"log": LOG, "seeds": SEEDS, "summary": summary,
           "dstar": dstar, "thumb_cap": thumb_cap},
          open(os.path.join(OUT, "EXPLORE_SEED2.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("EXPLORE2_DONE")
