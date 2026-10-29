# =====================================================================================
# STAGE6B_R1A -- geodesic ownership test: is the thumb continuously welded to the index?
# =====================================================================================
# Independent of the proximity-based ownership heuristic: walk the REAL mesh graph
# (edge connectivity) from the thumb tip / index tip landmarks and see which landmark each
# seam endpoint is geodesically closer to.  Also measures the geodesic distance between the
# thumb tip and the index tip, which is the decisive "are the two digits welded" number.
# =====================================================================================
import os
import sys
import json
import heapq

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s6br_common as F                                              # noqa: E402
import r1a_common as RC                                              # noqa: E402

OUT = os.path.join(F.S6B_R1A, "_tmp")
MM = F.MM
LOG = []


def log(s):
    LOG.append(s)
    print("[S6BR-GEO] " + s)


ctx = F.B.build_context()
NV = ctx["NV"]
ref = ctx["ref"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
own = ctx["own_r1a"]
ARC = ctx["ARC"]
jf = ref["jf"]
eadj, dij = ref["eadj"], ref["dij"]

# chain endpoints in world space
thumb_pts = ref["AC"]["THUMB"]
index_pts = ref["AC"]["INDEX"]
thumb_tip_pt = thumb_pts[-1]
index_tip_pt = index_pts[-1]
cmc_pt = thumb_pts[0]


def nearest_vert(P):
    return min(range(NV), key=lambda i: (V0[i] - P).length)


v_thumb_tip = nearest_vert(thumb_tip_pt)
v_index_tip = nearest_vert(index_tip_pt)
v_cmc = nearest_vert(cmc_pt)
log("landmark vertices: thumb_tip=v%d (d=%.4f mm)  index_tip=v%d (d=%.4f mm)  cmc=v%d"
    % (v_thumb_tip, (V0[v_thumb_tip] - thumb_tip_pt).length * MM,
       v_index_tip, (V0[v_index_tip] - index_tip_pt).length * MM, v_cmc))

g_thumb = dij(v_thumb_tip)
g_index = dij(v_index_tip)
g_cmc = dij(v_cmc)

log("GEODESIC thumb_tip -> index_tip = %.4f mm" % (g_index[v_thumb_tip] * MM))
log("GEODESIC thumb_tip -> cmc       = %.4f mm" % (g_cmc[v_thumb_tip] * MM))
log("GEODESIC index_tip -> cmc       = %.4f mm" % (g_cmc[v_index_tip] * MM))
log("GEODESIC index_tip -> thumb_tip = %.4f mm" % (g_thumb[v_index_tip] * MM))

# coherent geodesic ownership: each vertex belongs to the geodesically nearer tip
geo_own = []
for i in range(NV):
    dt, di = g_thumb[i], g_index[i]
    geo_own.append("THUMB" if dt < di else "INDEX")

# the proximity heuristic restricted to thumb|index vertices, for comparison
prox = [(own[i]) for i in range(NV)]
agree = sum(1 for i in range(NV) if (geo_own[i] == "THUMB") == (own[i] == "THUMB"))
log("geodesic-vs-proximity ownership agreement over all %d vertices: %.4f%% (%d)"
    % (NV, 100.0 * agree / NV, agree))

# geodesic boundary topology
def boundary_stats(owner, tag):
    E = [(k, a, b) for k, (a, b) in enumerate(EDGES)
         if {owner[a], owner[b]} == {"THUMB", "INDEX"}]
    adj = {}
    for k, a, b in E:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    deg = {}
    for v, nb in adj.items():
        deg[v] = len(nb)
    from collections import Counter
    hist = Counter(deg.values())
    # components
    seen = set()
    comps = []
    for v in adj:
        if v in seen:
            continue
        stack = [v]
        comp = set()
        while stack:
            u = stack.pop()
            if u in comp:
                continue
            comp.add(u)
            for w in adj[u]:
                if w not in comp:
                    stack.append(w)
        seen |= comp
        comps.append(comp)
    arcs = sorted(ARC[v] for v in adj)
    log("%-22s THUMB|INDEX boundary edges=%-5d vertices=%-4d components=%-3d degree_hist=%s"
        % (tag, len(E), len(adj), len(comps), dict(hist)))
    if arcs:
        log("%-22s   endpoint thumb-arc range %.2f .. %.2f" % ("", arcs[0], arcs[-1]))
    return {"edges": len(E), "vertices": len(adj), "components": len(comps),
            "degree_hist": dict(hist), "arc_min": (arcs[0] if arcs else None),
            "arc_max": (arcs[-1] if arcs else None)}


prox_stats = boundary_stats(prox, "PROXIMITY (own_r1a)")
geo_stats = boundary_stats(geo_own, "GEODESIC (mesh-true)")

# where does the geodesic boundary run? bucket by thumb arc
from collections import Counter
gc = Counter()
for v in range(NV):
    for w in [v]:
        pass
geo_bucket = Counter()
for k, (a, b) in enumerate(EDGES):
    if {geo_own[a], geo_own[b]} == {"THUMB", "INDEX"}:
        geo_bucket["arc<%.0f" % 42.7 if min(ARC[a], ARC[b]) < 42.7 else
                   ("arc 42.7-71.9" if min(ARC[a], ARC[b]) < 71.88 else "arc>71.9")] += 1
log("geodesic boundary by thumb arc: %s" % dict(geo_bucket))

# which seam endpoints are geodesically THUMB vs INDEX
SEAM_TI = [k for k, (a, b) in enumerate(EDGES) if {own[a], own[b]} == {"THUMB", "INDEX"}]
SEAM_TI_LEN0 = dict((k, (V0[EDGES[k][0]] - V0[EDGES[k][1]]).length * MM) for k in SEAM_TI)
rows = []
for k in sorted(SEAM_TI):
    a, b = EDGES[k]
    if own[a] != "THUMB":
        a, b = b, a
    rows.append({
        "edge": k, "len_mm": F.rr(SEAM_TI_LEN0[k], 4),
        "T_v": a, "T_geo": geo_own[a], "T_arc": F.rr(ARC[a], 3),
        "T_g2thumb_tip_mm": F.rr(g_thumb[a] * MM, 3), "T_g2index_tip_mm": F.rr(g_index[a] * MM, 3),
        "I_v": b, "I_geo": geo_own[b], "I_arc": F.rr(ARC[b], 3),
        "I_g2thumb_tip_mm": F.rr(g_thumb[b] * MM, 3), "I_g2index_tip_mm": F.rr(g_index[b] * MM, 3),
        "T_geo_disagrees_with_proximity": bool((geo_own[a] == "THUMB") != (own[a] == "THUMB")),
        "I_geo_disagrees_with_proximity": bool((geo_own[b] == "INDEX") != (own[b] == "INDEX")),
    })
n_dis_T = sum(1 for r in rows if r["T_geo_disagrees_with_proximity"])
n_dis_I = sum(1 for r in rows if r["I_geo_disagrees_with_proximity"])
log("seam endpoints where GEODESIC ownership DISAGREES with proximity ownership: "
    "T-side %d / %d ; I-side %d / %d" % (n_dis_T, len(rows), n_dis_I, len(rows)))
log("")
log("%-6s %6s | %-6s %-7s %7s %8s %8s | %-6s %-7s %7s %8s %8s"
    % ("edge", "len", "T.v", "T.geo", "T.arc", "g→ThTip", "g→IxTip",
       "I.v", "I.geo", "I.arc", "g→ThTip", "g→IxTip"))
for r in rows:
    log("%-6d %6.3f | v%-5d %-7s %7.2f %8.2f %8.2f | v%-5d %-7s %7.2f %8.2f %8.2f"
        % (r["edge"], r["len_mm"], r["T_v"], r["T_geo"], r["T_arc"], r["T_g2thumb_tip_mm"],
           r["T_g2index_tip_mm"], r["I_v"], r["I_geo"], r["I_arc"], r["I_g2thumb_tip_mm"],
           r["I_g2index_tip_mm"]))

json.dump({
    "landmark_vertices": {"thumb_tip": v_thumb_tip, "index_tip": v_index_tip, "cmc": v_cmc},
    "geodesic_thumb_tip_to_index_tip_mm": F.rr(g_index[v_thumb_tip] * MM, 4),
    "geodesic_thumb_tip_to_cmc_mm": F.rr(g_cmc[v_thumb_tip] * MM, 4),
    "geodesic_proximity_ownership_agreement_pct": F.rr(100.0 * agree / NV, 4),
    "proximity_boundary": prox_stats, "geodesic_boundary": geo_stats,
    "geodesic_boundary_by_arc": dict(geo_bucket),
    "seam_endpoint_geodesic_disagreement": {"T_side": n_dis_T, "I_side": n_dis_I,
                                            "total_edges": len(rows)},
    "rows": rows, "log": LOG,
}, open(os.path.join(OUT, "S6BR_GEODESIC.json"), "w", encoding="utf-8"),
    indent=1, ensure_ascii=False)
print("S6BR_GEO_DONE")
