# =====================================================================================
# STAGE6B_R1A -- topology identity / edge ancestry across the frozen lineage (read-only)
# =====================================================================================
# Answers, exactly and pose-independently: does the SAME edge (as a vertex-index pair, and
# as a face connectivity) exist at each historical stage?  Index stability is proven by
# comparing vertex POSITIONS and the edge / face index sets, not assumed.
# =====================================================================================
import os
import sys
import json

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s6br_common as F                                              # noqa: E402

OUT = os.path.join(F.S6B_R1A, "_tmp")
MM = F.MM
LOG = []


def log(s):
    LOG.append(s)
    print("[S6BR-TOPO] " + s)


ctx = F.B.build_context()
NV = ctx["NV"]
EDGES = ctx["edges"]
TOPO = ctx["poly"]
own = ctx["own_r1a"]
ARC = ctx["ARC"]

SEAM_TI = [k for k, (a, b) in enumerate(EDGES) if {own[a], own[b]} == {"THUMB", "INDEX"}]
TARGET_PAIRS = sorted(tuple(sorted(EDGES[k])) for k in SEAM_TI)
log("target THUMB|INDEX seam edges = %d" % len(TARGET_PAIRS))

# reference (R1B = production) index sets
REF_E = set(tuple(sorted(e)) for e in EDGES)
REF_F = set(tuple(sorted(p)) for p in TOPO)


def load_hand(path, prefer_nv=None):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = None
    for cand in bpy.data.objects:
        if cand.type != 'MESH':
            continue
        n = len(cand.data.vertices)
        if prefer_nv is not None and abs(n - prefer_nv) > max(4, 0.02 * prefer_nv):
            continue
        if "Hand" in cand.name:
            if ob is None or n > len(ob.data.vertices):
                ob = cand
    if ob is None:
        for cand in bpy.data.objects:
            if cand.type == 'MESH':
                if ob is None or len(cand.data.vertices) > len(ob.data.vertices):
                    ob = cand
    return ob


RES = {}
for label, path, desc in F.LINEAGE:
    if not os.path.exists(path):
        RES[label] = {"exists": False}
        continue
    ob = load_hand(path, prefer_nv=831 if label.startswith("S0") else None)
    if ob is None:
        RES[label] = {"exists": True, "hand_object": None}
        continue
    me = ob.data
    MW = ob.matrix_world.copy()
    V = [(MW @ v.co).copy() for v in me.vertices]
    E = set(tuple(sorted((e.vertices[0], e.vertices[1]))) for e in me.edges)
    Fs = set(tuple(sorted(p.vertices)) for p in me.polygons)
    nv = len(me.vertices)

    n_seam_present = sum(1 for p in TARGET_PAIRS if p in E)
    entry = {
        "exists": True, "hand_object": ob.name, "NV": nv, "NE": len(me.edges),
        "NF": len(me.polygons),
        "edge_set_equal_to_production": bool(E == REF_E),
        "face_set_equal_to_production": bool(Fs == REF_F),
        "edges_shared_with_production": len(E & REF_E),
        "edges_only_in_stage": len(E - REF_E),
        "edges_only_in_production": len(REF_E - E),
        "seam_index_pairs_present": n_seam_present,
        "seam_index_pairs_total": len(TARGET_PAIRS),
    }
    # vertex-index correspondence (is index i the same surface point?)
    if nv == NV:
        V0r = ctx["ref"]["V0"]
        d = [(V[i] - V0r[i]).length * MM for i in range(NV)]
        ds = sorted(d)
        entry["vertex_index_position_match"] = {
            "max_mm": F.rr(ds[-1], 4), "median_mm": F.rr(ds[len(ds) // 2], 4),
            "n_within_0p05mm": sum(1 for x in d if x <= 0.05),
            "n_total": NV}
    RES[label] = entry
    log("%-18s NV=%-5d NE=%-5d NF=%-5d | edge set == production: %-5s | seam index pairs present "
        "%3d/%d"
        % (label, nv, len(me.edges), len(me.polygons), entry["edge_set_equal_to_production"],
           n_seam_present, len(TARGET_PAIRS)))
    if nv == NV:
        vm = entry["vertex_index_position_match"]
        log("%-18s   vertex-index positional match: same-position vertices %d/%d ; max delta %.4f mm"
            % ("", vm["n_within_0p05mm"], NV, vm["max_mm"]))

json.dump({"target_seam_edge_count": len(TARGET_PAIRS),
           "target_pairs": [list(p) for p in TARGET_PAIRS],
           "reference_topo_sig": [NV, len(EDGES), len(TOPO)],
           "stages": RES, "log": LOG},
          open(os.path.join(OUT, "S6BR_TOPOLOGY_IDENTITY.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("S6BR_TOPO_DONE")
