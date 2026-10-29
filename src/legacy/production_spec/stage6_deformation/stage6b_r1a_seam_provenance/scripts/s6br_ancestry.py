# =====================================================================================
# STAGE6B_R1A -- seam-edge ANCESTRY audit across the frozen lineage (read-only)
# =====================================================================================
# Edge / vertex indices are NOT stable across retopo, and the production mesh is a
# SUBDIVISION of the CC0 source (3416 vs 831 vertices), so an edge is matched by
# putting both endpoints ON the same source edge segment (point-on-segment), never by
# index identity.  Every blend is opened strictly read-only.
# =====================================================================================
import os
import sys
import json
import math

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s6br_common as F                                              # noqa: E402

OUT = os.path.join(F.S6B_R1A, "_tmp")
os.makedirs(OUT, exist_ok=True)
MM = F.MM
LOG = []
RES = {}


def log(s):
    LOG.append(s)
    print("[S6BR-ANC] " + s)


# ---------------------------------------------------------------- targets
ctx = F.B.build_context()
NV = ctx["NV"]
ref = ctx["ref"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
own = ctx["own_r1a"]
ARC = ctx["ARC"]
CMC_CENTRE = ctx["cmc_centre"]
CMC_CONFINE_MM = ctx["cmc_confinement_mm"]
log("CMC rotation centre = %s ; R2 confinement radius = %.4f mm"
    % (F.v3(CMC_CENTRE * MM, 4), CMC_CONFINE_MM))

SEAM_TI = [k for k, (a, b) in enumerate(EDGES) if {own[a], own[b]} == {"THUMB", "INDEX"}]
TARGETS = [(k, EDGES[k][0], EDGES[k][1]) for k in SEAM_TI]
log("target seam edges = %d" % len(TARGETS))

# distance of each target edge to the CMC surgery centre
inside = []
for k, a, b in TARGETS:
    d = min((V0[a] - CMC_CENTRE).length, (V0[b] - CMC_CENTRE).length) * MM
    if d <= CMC_CONFINE_MM:
        inside.append((k, F.rr(d, 4)))
log("seam edges inside the Stage4A R2 CMC surgery confinement radius: %d / %d"
    % (len(inside), len(TARGETS)))
if inside:
    log("  %s" % inside[:10])
# CMC cage patch membership
cage = set(ctx["cmc_cage_patch"])
in_cage = [k for k, a, b in TARGETS if a in cage or b in cage]
log("seam edges touching the CMC cage patch: %d %s" % (len(in_cage), in_cage))


def point_on_edges(p, V, EDGES, tol_mm):
    """nearest edge SEGMENT to p; returns (edge_index, dist_mm, t_param) or (None, best, None)"""
    best, bk, bt = 1e18, None, None
    for k, (a, b) in enumerate(EDGES):
        va, vb = V[a], V[b]
        ab = vb - va
        L2 = ab.length_squared
        t = 0.0 if L2 < 1e-18 else max(0.0, min(1.0, (p - va).dot(ab) / L2))
        d = (p - (va + ab * t)).length
        if d < best:
            best, bk, bt = d, k, t
    return bk, best * MM, bt


def find_hand_object(prefer_nv=None):
    best = None
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        n = len(ob.data.vertices)
        nm = ob.name
        if prefer_nv is not None and abs(n - prefer_nv) <= max(4, 0.02 * prefer_nv):
            if ("Hand" in nm or "hand" in nm) and (best is None or n > len(best.data.vertices)):
                best = ob
    if best is None:
        for ob in bpy.data.objects:
            if ob.type == 'MESH' and ("Hand" in ob.name or "hand" in ob.name):
                if best is None or len(ob.data.vertices) > len(best.data.vertices):
                    best = ob
    return best


# ---------------------------------------------------------------- walk the lineage
for label, path, desc in F.LINEAGE:
    if not os.path.exists(path):
        log("%-18s MISSING on disk" % label)
        RES[label] = {"label": label, "path": path.replace("\\", "/"), "desc": desc,
                      "exists": False}
        continue
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = find_hand_object(prefer_nv=831 if label.startswith("S0") else None)
    if ob is None:
        log("%-18s no hand mesh object found" % label)
        RES[label] = {"label": label, "path": path.replace("\\", "/"), "desc": desc,
                      "exists": True, "hand_object": None}
        continue
    me = ob.data
    MW = ob.matrix_world.copy()
    V = [(MW @ v.co).copy() for v in me.vertices]
    E = [(e.vertices[0], e.vertices[1]) for e in me.edges]
    bpy.context.view_layer.update()
    nv, ne, nf = len(me.vertices), len(me.edges), len(me.polygons)

    per = []
    n_both = 0
    n_same_seg = 0
    n_exact_vert = 0
    for k, a, b in TARGETS:
        pa, pb = V0[a], V0[b]
        ka, da, ta = point_on_edges(pa, V, E, 0.05)
        kb, db, tb = point_on_edges(pb, V, E, 0.05)
        tol = 0.05
        both = (ka is not None and kb is not None and da <= tol and db <= tol)
        same = bool(both and ka == kb and (abs(ta - tb) > 1e-6))
        if both:
            n_both += 1
        if same:
            n_same_seg += 1
        per.append({"edge": k, "endpointA_on_edge": ka, "dA_mm": F.rr(da, 5),
                    "tA": (F.rr(ta, 5) if ta is not None else None),
                    "endpointB_on_edge": kb, "dB_mm": F.rr(db, 5),
                    "tB": (F.rr(tb, 5) if tb is not None else None),
                    "both_on_surface": bool(both), "same_source_segment": same})
    try:
        bbmin = F.v3(Vector((min(v[i] for v in V) for i in range(3))) * MM, 4)
        bbmax = F.v3(Vector((max(v[i] for v in V) for i in range(3))) * MM, 4)
    except Exception:
        bbmin = bbmax = None
    log("%-18s NV=%-6d NE=%-6d NF=%-6d obj=%-22s | seam edges fully on surface %3d/%d "
        "(same source segment %3d)"
        % (label, nv, ne, nf, ob.name[:22], n_both, len(TARGETS), n_same_seg))
    RES[label] = {"label": label, "path": path.replace("\\", "/"), "desc": desc,
                  "exists": True, "hand_object": ob.name, "NV": nv, "NE": ne, "NF": nf,
                  "n_tris": sum(len(p.vertices) - 2 for p in me.polygons),
                  "bbox_min_mm": bbmin, "bbox_max_mm": bbmax,
                  "seam_edges_on_surface": n_both, "seam_edges_same_source_segment": n_same_seg,
                  "per_edge": per}

json.dump({"target_count": len(TARGETS),
           "cmc_confinement_radius_mm": F.rr(CMC_CONFINE_MM, 4),
           "seam_edges_inside_cmc_confinement": inside,
           "seam_edges_touching_cmc_cage_patch": in_cage,
           "stages": RES, "log": LOG},
          open(os.path.join(OUT, "S6BR_ANCESTRY.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("S6BR_ANCESTRY_DONE")
