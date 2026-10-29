# =====================================================================================
# STAGE6B_R1A -- reconnaissance dump of the 67 THUMB|INDEX seam edges (read-only)
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
os.makedirs(OUT, exist_ok=True)
LOG = []
MM = F.MM


def log(s):
    LOG.append(s)
    print("[S6BR-RECON] " + s)


ctx = F.B.build_context()
NV = ctx["NV"]
ref = ctx["ref"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
TOPO = ref["TOPO0"]
MAT = ref["MAT0"]
own = ctx["own_r1a"]
OWN_RAW = ref["OWN_V"]
ARC = ctx["ARC"]
jf = ref["jf"]
segs = F.bone_segments(jf)
import r1a_common as RC                                             # noqa: E402

thumb_pts = ref["AC"]["THUMB"]
index_pts = ref["AC"]["INDEX"]
s_MCP, s_IP = ctx["s_MCP"], ctx["s_IP"]
tau = ctx["MED"]
idx_arc = RC.chain_arc_table(jf, "INDEX")
s_mcp_i, s_pip_i, s_dip_i = idx_arc[0], idx_arc[1], idx_arc[2]

log("jf keys sample: %s" % sorted(jf.keys())[:30])
log("locator bones resolved: %s" % sorted(segs.keys()))
log("NV=%d NE=%d NF=%d ; thumb arc MCP=%.4f IP=%.4f TIP=%.4f"
    % (NV, len(EDGES), len(TOPO), s_MCP, s_IP, ctx["s_TIP"]))
log("MED(tau)=%.6f mm ; index arc MCP=%.4f PIP=%.4f DIP=%.4f"
    % (tau, s_mcp_i, s_pip_i, s_dip_i))

# ---- the 67 seam edges
SEAM = [k for k, (a, b) in enumerate(EDGES) if own[a] != own[b]]
SEAM_TI = [k for k in SEAM if {own[EDGES[k][0]], own[EDGES[k][1]]} == {"THUMB", "INDEX"}]
log("ownership-boundary edges total = %d ; THUMB|INDEX = %d" % (len(SEAM), len(SEAM_TI)))

# ownership-boundary composition for context
comp = {}
for k in SEAM:
    a, b = EDGES[k]
    key = tuple(sorted((own[a], own[b])))
    comp[key] = comp.get(key, 0) + 1
log("boundary composition: %s" % json.dumps({"/".join(k): v for k, v in comp.items()}))

EF = F.build_edge_face_map(TOPO)
FN = F.face_normals_of(V0, TOPO)
face_area = [F.B.face_area(V0, p) for p in TOPO]

# material slot names come from the production object itself
MAT_NAMES = []
try:
    _bpy_ob = bpy.data.objects[F.MESH_OBJ]
    MAT_NAMES = [m.name if m else None for m in _bpy_ob.data.materials]
except Exception:
    pass
if not MAT_NAMES:
    MAT_NAMES = ["<unknown>"] * (max(MAT) + 1 if MAT else 0)

NAIL = ctx["nail"]
CAP = ctx["cap"]
WEB = ctx["first_web"]
THENAR = ctx["thenar"]
METACARPAL = ctx["metacarpal"]
DISTAL = ctx["distal"]
PROXIMAL = ctx["proximal"]

regions = {"nail": NAIL, "distal_cap": CAP, "first_web": WEB, "thenar": THENAR,
           "thumb_first_metacarpal": METACARPAL, "THUMB_DISTAL": DISTAL,
           "THUMB_PROXIMAL": PROXIMAL}

rows = []
for k in sorted(SEAM_TI):
    a, b = EDGES[k]
    # ensure a = THUMB endpoint, b = INDEX endpoint for readability
    if own[a] != "THUMB":
        a, b = b, a
    pa, pb = V0[a], V0[b]
    la = F.thumb_arc(pa, thumb_pts)
    lb = F.thumb_arc(pb, thumb_pts)
    ia = F.index_arc(pa, index_pts)
    ib = F.index_arc(pb, index_pts)
    loc_a, na, nda = F.anat_locate(pa, segs)
    loc_b, nb, ndb = F.anat_locate(pb, segs)
    faces = EF.get(tuple(sorted((a, b))), [])
    dih = F.edge_dihedral(FN, faces)
    row = {
        "edge": k, "endpoints": [a, b],
        "bind_length_mm": F.rr((pa - pb).length * MM, 6),
        "thumb_end": {
            "v": a, "own_r1a": own[a], "own_raw_nearest_chain": OWN_RAW[a],
            "promoted": bool(OWN_RAW[a] != own[a]),
            "thumb_arc_mm": F.rr(la[0], 4), "thumb_lateral_mm": F.rr(la[1] * MM, 4),
            "index_arc_mm": F.rr(ia[0], 4), "index_lateral_mm": F.rr(ia[1] * MM, 4),
            "d_to_thumb_chain_mm": F.rr(ref["dchain"][a]["THUMB"], 4),
            "d_to_index_chain_mm": F.rr(ref["dchain"][a]["INDEX"], 4),
            "nearest_locator": na, "nearest_locator_mm": nda,
            "locator_dist_mm": loc_a,
            "in_regions": sorted(r for r, s in regions.items() if a in s),
            "world": F.v3(pa, 6),
        },
        "index_end": {
            "v": b, "own_r1a": own[b], "own_raw_nearest_chain": OWN_RAW[b],
            "promoted": bool(OWN_RAW[b] != own[b]),
            "thumb_arc_mm": F.rr(lb[0], 4), "thumb_lateral_mm": F.rr(lb[1] * MM, 4),
            "index_arc_mm": F.rr(ib[0], 4), "index_lateral_mm": F.rr(ib[1] * MM, 4),
            "d_to_thumb_chain_mm": F.rr(ref["dchain"][b]["THUMB"], 4),
            "d_to_index_chain_mm": F.rr(ref["dchain"][b]["INDEX"], 4),
            "nearest_locator": nb, "nearest_locator_mm": ndb,
            "locator_dist_mm": loc_b,
            "in_regions": sorted(r for r, s in regions.items() if b in s),
            "world": F.v3(pb, 6),
        },
        "incident_face_count": len(faces),
        "is_manifold": bool(len(faces) == 2),
        "is_boundary": bool(len(faces) == 1),
        "is_non_manifold": bool(len(faces) > 2),
        "dihedral_deg": (F.rr(dih, 4) if dih is not None else None),
        "incident_faces": [
            {"face": fi, "material_index": MAT[fi],
             "material": (MAT_NAMES[MAT[fi]] if MAT[fi] < len(MAT_NAMES) else None),
             "area_mm2": F.rr(face_area[fi] * 1e6, 6),
             "centroid": F.v3(ref["FC"][fi], 6),
             "own": ref["FO"][fi],
             "normal": F.v3(FN[fi], 6)} for fi in faces],
    }
    rows.append(row)

json.dump({"n": len(rows), "rows": rows}, open(os.path.join(OUT, "S6BR_RECON_EDGES.json"), "w",
                                               encoding="utf-8"), indent=1, ensure_ascii=False)

# ---------------- summarise the discriminating evidence
def bucket(vals, edges):
    out = {}
    for e in edges:
        out[e] = out.get(e, 0) + 1
    return out

log("--- thumb endpoint: thumb arc s vs joint levels (MCP %.3f IP %.3f) ---" % (s_MCP, s_IP))
for r in sorted(rows, key=lambda r: r["thumb_end"]["thumb_arc_mm"]):
    te, ie = r["thumb_end"], r["index_end"]
    log("e%-5d len=%7.3f | T v%-5d own_raw=%-7s s=%8.3f lat=%7.3f idxAR=%8.3f lat=%7.3f %-28s | I v%-5d own_raw=%-7s s=%8.3f idxAR=%8.3f %-28s | dih=%s"
        % (r["edge"], r["bind_length_mm"], te["v"], te["own_raw_nearest_chain"],
           te["thumb_arc_mm"], te["thumb_lateral_mm"], te["index_arc_mm"],
           te["index_lateral_mm"], ",".join(te["in_regions"]) or "-",
           ie["v"], ie["own_raw_nearest_chain"], ie["thumb_arc_mm"], ie["index_arc_mm"],
           ",".join(ie["in_regions"]) or "-", r["dihedral_deg"]))

json.dump(LOG, open(os.path.join(OUT, "S6BR_RECON_LOG.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("S6BR_RECON_DONE")
