# =====================================================================================
# STAGE5B R1E -- READ-ONLY SURVEY  (establishes the facts R1E is designed on)
# =====================================================================================
# Nothing is written to any .blend.  The stale STAGE4B_R2_JOINT_FRAME.json is NEVER read.
# =====================================================================================
import os
import sys
import json
import math
from collections import Counter, deque

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R1E = os.path.abspath(os.path.join(HERE, ".."))
R3D = os.path.join(PROD, "stage6_deformation", "stage6b_r3_thumb_tip_ownership_boundary")
S5 = os.path.join(PROD, "stage5_production_rig")
MM = 1000.0

R1B_MASTER = os.path.join(S5, "stage5b_r1b", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend")
R1B_SHA256 = "cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10"
R2A = os.path.join(S5, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
R2A_SHA256 = "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"
MESH_OBJ = "Hand  - Realistic"
RIG_OBJ = "RIGHT_HAND_PRODUCTION_RIG"


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


OUT = {}
OUT["r1b_sha"] = sha256(R1B_MASTER)
OUT["r1b_sha_ok"] = OUT["r1b_sha"] == R1B_SHA256
OUT["r2a_sha"] = sha256(R2A)
OUT["r2a_sha_ok"] = OUT["r2a_sha"] == R2A_SHA256

# ---------------------------------------------------------------- R3 authority (read only)
lab = json.load(open(os.path.join(R3D, "R3_OWNERSHIP_LABELS.json"), encoding="utf-8"))
R3 = lab["R3"]
R2 = lab["R2"]
R2D = set(lab["R2_domain"])
BND_R3 = list(lab["boundary_edges_R3"])
BND_R2 = list(lab["boundary_edges_R2"])
CAP = set(lab["CAP"])
NAIL_T = set(lab["NAIL_THUMB"])
NAIL_I = set(lab["NAIL_INDEX"])
WEB = set(lab["WEB"])
CHANGED = list(lab["changed"])
OUT["r3_label_len"] = len(R3)
OUT["r3_changed"] = CHANGED
OUT["r3_boundary_edges"] = BND_R3
OUT["anchors"] = {"cap": sorted(CAP), "nail_thumb": sorted(NAIL_T),
                  "nail_index": sorted(NAIL_I), "web": sorted(WEB)}

# ---------------------------------------------------------------- frozen probe sets
PA = os.path.join(PROD, "stage6_deformation", "stage6b_r1a_seam_provenance")
ca = json.load(open(os.path.join(PA, "STAGE6B_R1A_CLASS_A_VALID_WEB_EDGES.json"), encoding="utf-8"))
cb = json.load(open(os.path.join(PA, "STAGE6B_R1A_CLASS_B_OWNERSHIP_MISCLASSIFICATION.json"), encoding="utf-8"))
CLASS_A = [(e["edge_id"], e["endpoints"]["v0"], e["endpoints"]["v1"]) for e in ca["edges"]]
CLASS_B = [(e["edge_id"], e["endpoints"]["v0"], e["endpoints"]["v1"]) for e in cb["edges"]]
OUT["class_a"] = CLASS_A
OUT["class_b_n"] = len(CLASS_B)

# =====================================================================================
bpy.ops.wm.open_mainfile(filepath=R1B_MASTER)
ob = bpy.data.objects[MESH_OBJ]
rig = bpy.data.objects[RIG_OBJ]
MW = ob.matrix_world.copy()
me = ob.data
NV = len(me.vertices)
V0 = [(MW @ v.co).copy() for v in me.vertices]
TOPO = [tuple(p.vertices) for p in me.polygons]
EDGES = [(e.vertices[0], e.vertices[1]) for e in me.edges]
OUT["NV"] = NV
OUT["n_edges"] = len(EDGES)
OUT["n_polys"] = len(TOPO)
OUT["topo_signature"] = [NV, len(me.edges), len(me.polygons),
                         sum(len(p.vertices) - 2 for p in me.polygons)]

# weights
WOLD = [dict() for _ in range(NV)]
for g in ob.vertex_groups:
    for i in range(NV):
        try:
            w = g.weight(i)
        except RuntimeError:
            continue
        if w > 0.0:
            WOLD[i][g.name] = w
OUT["groups"] = sorted(g.name for g in ob.vertex_groups)

# ---------------------------------------------------------------- live joint polylines
bpy.ops.wm.open_mainfile(filepath=R2A)
ob2 = bpy.data.objects[MESH_OBJ]
rig2 = bpy.data.objects[RIG_OBJ]
MW2 = ob2.matrix_world.copy()
V0b = [(MW2 @ v.co).copy() for v in ob2.data.vertices]
OUT["geom_identical_r1b_vs_r2a"] = max((V0[i] - V0b[i]).length for i in range(NV)) * MM

BONE_CHAIN = {"THUMB": ("THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R"),
              "INDEX": ("INDEX_MCP_R", "INDEX_PIP_R", "INDEX_DIP_R"),
              "MIDDLE": ("MIDDLE_MCP_R", "MIDDLE_PIP_R", "MIDDLE_DIP_R"),
              "RING": ("RING_MCP_R", "RING_PIP_R", "RING_DIP_R"),
              "LITTLE": ("LITTLE_MCP_R", "LITTLE_PIP_R", "LITTLE_DIP_R")}


def live_poly(chain):
    p = [MW2 @ Vector(rig2.data.bones[chain[0]].head_local)]
    for nm in chain:
        p.append(MW2 @ Vector(rig2.data.bones[nm].tail_local))
    return p


def arc_of(pts, v):
    bd, bs, acc = 1e18, 0.0, 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (v - a).dot(ab) / max(ab.length_squared, 1e-18)))
        d = (v - (a + ab * t)).length
        if d < bd:
            bd, bs = d, (acc + t * ab.length) * MM
        acc += ab.length
    return bs, bd * MM


LIVE = {}
XIJ = {}
for D, ch in BONE_CHAIN.items():
    pts = live_poly(ch)
    LIVE[D] = pts
    a = [0.0]
    acc = 0.0
    for k in range(len(pts) - 1):
        acc += (pts[k + 1] - pts[k]).length
        a.append(acc * MM)
    XIJ[D] = a
OUT["live_XIJ"] = dict((k, [round(x, 4) for x in v]) for k, v in XIJ.items())

sT = [0.0] * NV
dT = [0.0] * NV
sI = [0.0] * NV
dI = [0.0] * NV
for i in range(NV):
    sT[i], dT[i] = arc_of(LIVE["THUMB"], V0[i])
    sI[i], dI[i] = arc_of(LIVE["INDEX"], V0[i])

# ---------------------------------------------------------------- R3 topology
adj = {}
for a, b in EDGES:
    adj.setdefault(a, set()).add(b)
    adj.setdefault(b, set()).add(a)
adj = dict((k, sorted(v)) for k, v in adj.items())

bnd_set = set(tuple(sorted(EDGES[k])) for k in BND_R3)
OUT["bnd_r3_endpoints"] = [[EDGES[k][0], EDGES[k][1], round((V0[EDGES[k][0]] - V0[EDGES[k][1]]).length * MM, 4)] for k in BND_R3]

# cut the 16 edges -> components
cut = set(bnd_set)
seen = set()
comps = []
for v in range(NV):
    if v in seen:
        continue
    dq = deque([v])
    seen.add(v)
    comp = []
    while dq:
        x = dq.popleft()
        comp.append(x)
        for u in adj[x]:
            if u in seen:
                continue
            if tuple(sorted((x, u))) in cut:
                continue
            seen.add(u)
            dq.append(u)
    comps.append(comp)
comps.sort(key=len, reverse=True)
OUT["cut_components"] = [len(c) for c in comps]
BODY = set(comps[0])
SHEET = set(comps[1]) if len(comps) > 1 else set()
OUT["sheet_has_index_tip_1228"] = 1228 in SHEET
OUT["sheet_has_index_nail"] = len(NAIL_I & SHEET)
OUT["sheet_has_thumb_cap"] = len(CAP & SHEET)
OUT["sheet_has_thumb_nail"] = len(NAIL_T & SHEET)
OUT["sheet_has_web"] = len(WEB & SHEET)
OUT["sheet_R3_label_counts"] = dict(Counter(R3[i] for i in SHEET))
OUT["body_R3_label_counts"] = dict(Counter(R3[i] for i in BODY))
OUT["sheet_s_index_range_mm"] = [round(min(sI[i] for i in SHEET), 3), round(max(sI[i] for i in SHEET), 3)]
OUT["sheet_s_thumb_range_mm"] = [round(min(sT[i] for i in SHEET), 3), round(max(sT[i] for i in SHEET), 3)]
OUT["sheet_d_index_range_mm"] = [round(min(dI[i] for i in SHEET), 3), round(max(dI[i] for i in SHEET), 3)]

# ---------------------------------------------------------------- hard flip census (R1B)
def hard_flip(W, a, b):
    wa, wb = W[a], W[b]
    hi_a = set(g for g, v in wa.items() if v >= 0.95)
    lo_b = set(g for g in wa if wb.get(g, 0.0) <= 0.05)
    hi_b = set(g for g, v in wb.items() if v >= 0.95)
    lo_a = set(g for g in wb if wa.get(g, 0.0) <= 0.05)
    left = hi_a & lo_b
    right = hi_b & lo_a
    if not left or not right or left == right:
        return None
    return (sorted(left), sorted(right))


FLIP = []
for k, (a, b) in enumerate(EDGES):
    r = hard_flip(WOLD, a, b)
    if r:
        FLIP.append((k, a, b, r[0], r[1]))
OUT["r1b_hard_flip_edges"] = len(FLIP)
OUT["r1b_hard_flip_list"] = [{"edge": k, "a": a, "b": b, "l": l, "r": r,
                              "bind_mm": round((V0[a] - V0[b]).length * MM, 4),
                              "a_lab": R3[a], "b_lab": R3[b],
                              "a_dom": (max(WOLD[a].items(), key=lambda kv: kv[1])[0] if WOLD[a] else None),
                              "b_dom": (max(WOLD[b].items(), key=lambda kv: kv[1])[0] if WOLD[b] else None)}
                             for k, a, b, l, r in FLIP]

# ---------------------------------------------------------------- R3 vs R2 / dominant digit
mism = [i for i in range(NV) if R3[i] != R2[i]]
OUT["r3_vs_r2_mismatch"] = len(mism)
OUT["r3_vs_r2_mismatch_list"] = mism
GD = {"WRIST_R": "wrist"}
for D, ch in BONE_CHAIN.items():
    for st in ("MCP", "PIP", "DIP", "CMC", "IP"):
        GD["%s_%s_R" % (D, st)] = D
dom = [None] * NV
for i in range(NV):
    if WOLD[i]:
        dom[i] = GD.get(max(WOLD[i].items(), key=lambda kv: kv[1])[0], "wrist")
dom_mism = [i for i in range(NV) if R3[i] in ("THUMB", "INDEX") and dom[i] != R3[i]]
OUT["r1b_bind_dominant_vs_r3_mismatch"] = len(dom_mism)
OUT["r1b_bind_dominant_vs_r3_mismatch_list"] = dom_mism
OUT["r1b_dominant_digit_counts"] = dict(Counter(dom))

# ---------------------------------------------------------------- thumb distal failure region
s_IP = XIJ["THUMB"][2]
MED = sorted((V0[a] - V0[b]).length for a, b in EDGES)[len(EDGES) // 2] * MM
OUT["MED_mm"] = round(MED, 6)
DISTAL = set(i for i in range(NV) if R3[i] == "THUMB" and sT[i] >= s_IP - MED)
OUT["distal_thumb_count"] = len(DISTAL)
OUT["distal_cap_in_distal"] = len(CAP & DISTAL)
for i in sorted(CAP):
    OUT.setdefault("cap_info", {})[i] = {"sT": round(sT[i], 3), "R3": R3[i], "R2": R2[i],
                                         "W": dict((g, round(v, 4)) for g, v in WOLD[i].items())}
for i in sorted(WEB):
    OUT.setdefault("web_info", {})[i] = {"sT": round(sT[i], 3), "sI": round(sI[i], 3),
                                         "R3": R3[i], "R2": R2[i],
                                         "W": dict((g, round(v, 4)) for g, v in WOLD[i].items())}

# ---------------------------------------------------------------- cmc cage
a4 = json.load(open(os.path.join(PROD, "stage4_blender", "stage4a_r2",
                                 "CMC_LOCAL_RETOPO_AUDIT_R2.json"), encoding="utf-8"))
cmc_centre = Vector(a4["cmc"]["world"])
conf = max(a4["vertex_diff"]["max_dist_from_cmc_of_added_mm"],
           a4["vertex_diff"]["max_dist_from_cmc_of_removed_mm"])
OUT["cmc_confinement_mm"] = conf
cage_r3 = sorted(i for i in range(NV)
                 if (V0[i] - cmc_centre).length * MM <= conf and R3[i] in ("THUMB", "wrist"))
OUT["cmc_cage_count_r3labels"] = len(cage_r3)
OUT["cmc_cage_count"] = len(cage_r3)

# ---------------------------------------------------------------- probe validity
eset = set(tuple(sorted(e)) for e in EDGES)
OUT["class_a_all_valid"] = all(tuple(sorted((a, b))) in eset for _k, a, b in CLASS_A)
OUT["class_b_all_valid"] = all(tuple(sorted((a, b))) in eset for _k, a, b in CLASS_B)
OUT["class_b_still_label_boundary_r3"] = sum(1 for _k, a, b in CLASS_B if R3[a] != R3[b])
OUT["class_a_label_pairs_r3"] = dict(Counter("%s|%s" % tuple(sorted((R3[a], R3[b])))
                                             for _k, a, b in CLASS_A))
OUT["bnd_r3_label_pairs"] = dict(Counter("%s|%s" % tuple(sorted((R3[EDGES[k][0]], R3[EDGES[k][1]])))
                                         for k in BND_R3))

json.dump(OUT, open(os.path.join(R1E, "_tmp", "r1e_survey.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("SURVEY_DONE")
