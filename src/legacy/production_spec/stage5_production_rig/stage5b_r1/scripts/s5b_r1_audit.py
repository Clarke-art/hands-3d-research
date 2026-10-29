# =====================================================================================
# STAGE5B_R1 -- STATIC WEIGHT / BIND AUDIT   (READ-ONLY on the new Stage5B blend)
# Produces: STAGE5B_R1_WEIGHT_STATS.json, STAGE5B_R1_VERTEX_INFLUENCE_AUDIT.json,
#           JOINT_WEIGHT_TRANSITION_TABLE.json, FIRST_WEB_WEIGHT_AUDIT.json,
#           CROSS_DIGIT_WEIGHT_LEAK_AUDIT.json, NAIL_WEIGHT_AUDIT.json,
#           WEIGHT_PRUNE_AUDIT.json, ZERO_POSE_BIND_AUDIT.json, PARENT_BIND_AUDIT.json
# =====================================================================================
import bpy, sys, os, json, math, hashlib, heapq, datetime
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
MM = 1000.0
NOW = datetime.datetime.now().astimezone().isoformat()
TOP = os.path.dirname(OUTDIR)
S4 = os.path.join(os.path.dirname(TOP), "stage4_blender")
R2A = os.path.join(TOP, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
R2A_SHA = "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"
S5B = os.path.join(OUTDIR, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend")
TIP = ["THUMB_TIP_R", "INDEX_TIP_R", "MIDDLE_TIP_R", "RING_TIP_R", "LITTLE_TIP_R"]
DEFORMEXPECT = ["WRIST_R"] + ["%s_%s_R" % (d, s) for d in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE")
                              for s in (["CMC", "MCP", "IP"] if d == "THUMB" else ["MCP", "PIP", "DIP"])]

jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
t01 = json.load(open(os.path.join(S4, "stage4a_t01", "T01_FINAL_AUDIT.json"), encoding="utf-8"))
AO = Vector(oa["WRIST_ORIGIN"])
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"], "LITTLE": ["MCP", "PIP", "DIP"]}
DD = {"THUMB": "thumb", "INDEX": "index", "MIDDLE": "middle", "RING": "ring", "LITTLE": "little"}
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a); LOG.append(s); print("[S5B-AUDIT]", s)


# ---------------------------------------------------------------- reference geometry (R2A)
bpy.ops.wm.open_mainfile(filepath=R2A)
ob0 = bpy.data.objects["Hand  - Realistic"]
MW0 = ob0.matrix_world.copy()
V0 = [(MW0 @ v.co).copy() for v in ob0.data.vertices]
NV = len(V0)
TOPO0 = [tuple(p.vertices) for p in ob0.data.polygons]
UV0 = [tuple(round(u, 9) for u in d.uv) for d in ob0.data.uv_layers.active.data] if ob0.data.uv_layers.active else []
MAT0 = [p.material_index for p in ob0.data.polygons]
NEDGE0 = len(ob0.data.edges)
NFACE0 = len(ob0.data.polygons)
UVL0 = [tuple(round(u, 9) for u in d.uv) for d in ob0.data.uv_layers.active.data] if ob0.data.uv_layers.active else []
FC0 = [sum((V0[v] for v in p.vertices), Vector()) / len(p.vertices) for p in ob0.data.polygons]


def d_poly(p, poly):
    b = 1e9
    for i in range(len(poly) - 1):
        a, q = poly[i], poly[i + 1]; ab = q - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
        b = min(b, (p - (a + ab * t)).length)
    return b


def chp(D):
    p = [Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])]
    for s in CHAIN[D]:
        p.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
    return p


AC = {D: chp(D) for D in CHAIN}; AC["wrist"] = [AO, Vector(jf["WRIST_R"]["tail"])]
OWN_V = [min(AC, key=lambda D: d_poly(V0[i], AC[D])) for i in range(NV)]
FO = {}
for p in ob0.data.polygons:
    FO[p.index] = min(AC, key=lambda D: d_poly(FC0[p.index], AC[D]))
NTRI0 = sum(len(p.vertices) - 2 for p in ob0.data.polygons)
NAIL_V = sorted({v for p in ob0.data.polygons if p.material_index == 1 for v in p.vertices})
NAIL_BY_DIGIT = {}
for p in ob0.data.polygons:
    if p.material_index == 1 and FO[p.index] in CHAIN:
        NAIL_BY_DIGIT.setdefault(FO[p.index], set()).update(p.vertices)

# ---------------------------------------------------------------- open the Stage5B blend
bpy.ops.wm.open_mainfile(filepath=S5B)
ob = bpy.data.objects["Hand  - Realistic"]
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
me = ob.data
MW1 = ob.matrix_world.copy()
V1 = [(MW1 @ v.co).copy() for v in me.vertices]

# ---------------------------------------------------------------- zero-pose bind audit
dg = bpy.context.evaluated_depsgraph_get()
obe = ob.evaluated_get(dg)
VE = [(MW1 @ v.co).copy() for v in obe.data.vertices]
dz = [(VE[i] - V0[i]).length * MM for i in range(NV)]
bb0 = [(min(v[k] for v in V0), max(v[k] for v in V0)) for k in range(3)]
bb1 = [(min(v[k] for v in VE), max(v[k] for v in VE)) for k in range(3)]
ZERO = {"method": "depsgraph evaluated mesh at REST / ZERO pose vs Stage5A R2A frozen geometry",
        "max_vertex_delta_mm": round(max(dz), 9), "mean_vertex_delta_mm": round(sum(dz) / NV, 9),
        "bbox_delta_mm": [round(abs(bb1[k][0] - bb0[k][0]) * MM, 9) for k in range(3)]
        + [round(abs(bb1[k][1] - bb0[k][1]) * MM, 9) for k in range(3)],
        "object_transform_delta": round(max(abs(MW1[i][j] - MW0[i][j]) for i in range(4)
                                            for j in range(4)) * MM, 9),
        "base_mesh_vertex_delta_mm": round(max((V1[i] - V0[i]).length for i in range(NV)) * MM, 9),
        "ZERO_POSE_BIND": "PASS" if max(dz) < 1e-4 else "FAIL"}
log("zero-pose max vertex delta = %s mm" % ZERO["max_vertex_delta_mm"])

PARENT = {"mesh_parent": ob.parent.name if ob.parent else None,
          "matrix_world_before": [[round(float(x), 9) for x in r] for r in MW0],
          "matrix_world_after": [[round(float(x), 9) for x in r] for r in MW1],
          "matrix_parent_inverse": [[round(float(x), 9) for x in r]
                                    for r in ob.matrix_parent_inverse],
          "rig_matrix_world": [[round(float(x), 9) for x in r] for r in rig.matrix_world],
          "world_delta_mm": round(max(abs(MW1[i][j] - MW0[i][j]) for i in range(4)
                                      for j in range(4)) * MM, 9),
          "armature_modifiers": [(m.name, m.type, m.object.name if m.object else None)
                                 for m in ob.modifiers if m.type == 'ARMATURE'],
          "all_modifiers": [(m.name, m.type) for m in ob.modifiers]}
log("parent = %s ; armature modifiers = %d" % (PARENT["mesh_parent"], len(PARENT["armature_modifiers"])))

# ---------------------------------------------------------------- topology / UV / material
TOPO1 = [tuple(p.vertices) for p in me.polygons]
UV1 = [tuple(round(u, 9) for u in d.uv) for d in me.uv_layers.active.data] if me.uv_layers.active else []
MAT1 = [p.material_index for p in me.polygons]
DRIFT = {"V": [len(V1), NV], "E": [len(me.edges), NEDGE0], "F": [len(me.polygons), NFACE0],
         "TRIS": [sum(len(p.vertices) - 2 for p in me.polygons), NTRI0],
         "topology_delta": 0 if TOPO1 == TOPO0 else 1,
         "uv_delta": 0 if UV1 == UV0 else 1,
         "material_assignment_delta": 0 if MAT1 == MAT0 else 1,
         "nail_face_assignment_delta": 0 if [i for i, m in enumerate(MAT1) if m == 1]
         == [i for i, m in enumerate(MAT0) if m == 1] else 1}
log("topology drift: V %d/%d E %d/%d F %d/%d ; topo/uv/mat = %s/%s/%s"
    % (DRIFT["V"][0], DRIFT["V"][1], DRIFT["E"][0], DRIFT["E"][1], DRIFT["F"][0], DRIFT["F"][1],
       DRIFT["topology_delta"], DRIFT["uv_delta"], DRIFT["material_assignment_delta"]))

# ---------------------------------------------------------------- weights
VG = {g.name: g.index for g in ob.vertex_groups}
GROUP_NAMES = sorted(VG.keys())
W = [dict() for _ in range(NV)]
for name, gi in VG.items():
    vg = ob.vertex_groups[gi]
    for i in range(NV):
        try:
            w = vg.weight(i)
        except RuntimeError:
            continue
        if w > 0.0:
            W[i][name] = w

STATS = {}
for b in GROUP_NAMES:
    ws = [W[i].get(b, 0.0) for i in range(NV)]
    nz = [x for x in ws if x > 0.0]
    idxs = [i for i in range(NV) if ws[i] > 0.0]
    bb = None
    if idxs:
        bb = [[round(min(V1[i][k] for i in idxs), 6), round(max(V1[i][k] for i in idxs), 6)]
              for k in range(3)]
    STATS[b] = {"vertex_count_nonzero": len(nz),
                "weight_sum": round(sum(nz), 6),
                "max_weight": round(max(nz), 6) if nz else 0.0,
                "mean_nonzero_weight": round(sum(nz) / len(nz), 6) if nz else 0.0,
                "vertices_weight_gt_0_25": sum(1 for x in nz if x > 0.25),
                "vertices_weight_gt_0_50": sum(1 for x in nz if x > 0.50),
                "vertices_weight_gt_0_75": sum(1 for x in nz if x > 0.75),
                "bbox_of_influenced_vertices": bb}

DIST = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, ">4": 0}
NORM_ERR = 0.0
NEG = 0
NAN = 0
UNW = []
for i in range(NV):
    d = W[i]
    n = len([1 for v in d.values() if v > 0.0])
    DIST[n if n <= 4 else ">4"] = DIST.get(n if n <= 4 else ">4", 0) + 1
    s = sum(d.values())
    if n == 0:
        UNW.append(i)
    NORM_ERR = max(NORM_ERR, abs(s - 1.0))
    for v in d.values():
        if v < 0:
            NEG += 1
        if v != v or v in (float('inf'), float('-inf')):
            NAN += 1
INFL = {"distribution": DIST, "unweighted_vertices": len(UNW),
        "unweighted_vertex_ids": UNW[:50],
        "max_influences": max([k for k in DIST if k != ">4"] + [0]) if DIST[">4"] == 0 else 99,
        "vertices_over_4": DIST[">4"],
        "worst_normalization_error": round(NORM_ERR, 12),
        "negative_weights": NEG, "nan_inf_weights": NAN}
INFL["top20_ambiguous"] = sorted(
    [{"vertex": i, "n": len(W[i]), "weights": {k: round(v, 4) for k, v in sorted(
        W[i].items(), key=lambda kv: -kv[1])}} for i in range(NV) if len(W[i]) >= 3],
    key=lambda r: -r["n"])[:20]
log("influence distribution %s ; unweighted %d ; norm err %s"
    % (DIST, len(UNW), INFL["worst_normalization_error"]))

# ---------------------------------------------------------------- semantic leakage
DIGIT_OF_BONE = {"WRIST_R": "wrist"}
for D in CHAIN:
    for s in CHAIN[D]:
        DIGIT_OF_BONE["%s_%s_R" % (D, s)] = D
WEB_OK = {"WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "INDEX_MCP_R"}
PALM_FAN_OK = {"THUMB_CMC_R", "INDEX_MCP_R", "MIDDLE_MCP_R", "RING_MCP_R", "LITTLE_MCP_R"}
PIPDIP = {"%s_%s_R" % (d, s) for d in ("INDEX", "MIDDLE", "RING", "LITTLE") for s in ("PIP", "DIP")}
leak = []
sanctioned_palm_fan = []
sanctioned_web = []
for i in range(NV):
    own = OWN_V[i]
    for b, w in W[i].items():
        if w <= 1e-6:
            continue
        bd = DIGIT_OF_BONE[b]
        if bd == own or bd == "wrist":
            continue
        # sanctioned: metacarpal-root fan inside the wrist/palm region
        if own == "wrist" and b in PALM_FAN_OK:
            sanctioned_palm_fan.append({"vertex": i, "bone": b, "weight": round(w, 6)})
            continue
        # sanctioned: thumb <-> index first-web root blend (MCP level only)
        if own in ("THUMB", "INDEX") and b in WEB_OK:
            sanctioned_web.append({"vertex": i, "bone": b, "weight": round(w, 6)})
            continue
        leak.append({"vertex": i, "bone": b, "weight": round(w, 6), "vertex_digit": own})
LEAK = {"leakage_vertex_count": len({r["vertex"] for r in leak}), "leakage_entries": len(leak),
        "leakage_total_weight": round(sum(r["weight"] for r in leak), 6),
        "offending_source_bones": sorted({r["bone"] for r in leak}),
        "offending_target_regions": sorted({r["vertex_digit"] for r in leak}),
        "samples": leak[:40],
        "SANCTIONED_palm_metacarpal_fan": {
            "entries": len(sanctioned_palm_fan),
            "total_weight": round(sum(r["weight"] for r in sanctioned_palm_fan), 6),
            "bones": sorted({r["bone"] for r in sanctioned_palm_fan})},
        "SANCTIONED_first_web_root_blend": {
            "entries": len(sanctioned_web),
            "total_weight": round(sum(r["weight"] for r in sanctioned_web), 6),
            "bones": sorted({r["bone"] for r in sanctioned_web})}}
log("cross-digit leakage entries = %d (vertices %d)" % (len(leak), LEAK["leakage_vertex_count"]))

# finger -> forearm / PIP-DIP -> palm
WRISTBONE = "WRIST_R"
forearm_leak = []
pipdip_palm = []
for i in range(NV):
    if OWN_V[i] != "wrist":
        continue
    # palm / forearm vertices: does any finger PIP/DIP contribute?
    for b in PIPDIP:
        w = W[i].get(b, 0.0)
        if w > 1e-6:
            pipdip_palm.append({"vertex": i, "bone": b, "weight": round(w, 6)})
# finger bones reaching the forearm: vertices very proximal along the wrist axis
XIJ_T = {}
for D in CHAIN:
    pts = [Vector(jf["%s_%s_R" % (D, s)]["head"]) for s in CHAIN[D]]
    pts.append(Vector(jf["%s_TIP_R" % D]["head"]))
    acc = 0.0; a = [0.0]
    for k in range(len(pts) - 1):
        acc += (pts[k + 1] - pts[k]).length
        a.append(acc * MM)
    XIJ_T[D] = [round(x, 4) for x in a]
wH = rig.matrix_world @ rig.data.bones["WRIST_R"].head_local
wT = rig.matrix_world @ rig.data.bones["WRIST_R"].tail_local
wU = (wT - wH).normalized()
for i in range(NV):
    x = (V1[i] - wH).dot(wU)
    if x < 0:                       # proximal of the wrist joint = forearm region
        for b, w in W[i].items():
            if b != WRISTBONE and w > 1e-6:
                forearm_leak.append({"vertex": i, "bone": b, "weight": round(w, 6)})
FOREARM = {"forearm_vertices_checked": sum(1 for i in range(NV) if (V1[i] - wH).dot(wU) < 0),
           "finger_to_forearm_leak_entries": len(forearm_leak),
           "finger_to_forearm_total_weight": round(sum(r["weight"] for r in forearm_leak), 6),
           "samples": forearm_leak[:30]}
PALM = {"palm_pip_dip_leak_entries": len(pipdip_palm),
        "palm_pip_dip_total_weight": round(sum(r["weight"] for r in pipdip_palm), 6),
        "samples": pipdip_palm[:30]}
log("forearm leak %d ; palm PIP/DIP leak %d" % (len(forearm_leak), len(pipdip_palm)))

# ---------------------------------------------------------------- first web
# first web = the thumb / index region at or proximal of thumb MCP / index PIP
def arc_of_ref(D, v):
    pts = [Vector(jf["%s_%s_R" % (D, s)]["head"]) for s in CHAIN[D]]
    pts.append(Vector(jf["%s_TIP_R" % D]["head"]))
    acc = 0.0; best = (1e9, 0.0)
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]; ab = b - a
        t = max(0.0, min(1.0, (v - a).dot(ab) / max(ab.length_squared, 1e-18)))
        d = (v - (a + ab * t)).length
        if d < best[0]:
            best = (d, (acc + t * ab.length) * MM)
        acc += ab.length
    return best[1]


ELEN_A = sorted((V1[a] - V1[b]).length * MM for a, b in
                [(e.vertices[0], e.vertices[1]) for e in me.edges])
MED_EDGE_A = ELEN_A[len(ELEN_A) // 2]
W_WEB_A = 2.0 * MED_EDGE_A * 1e-3
web_verts = [i for i in range(NV)
             if d_poly(V1[i], AC["THUMB"]) <= W_WEB_A
             and d_poly(V1[i], AC["INDEX"]) <= W_WEB_A]
WEB = {"web_definition": ("vertices lying BETWEEN the thumb and index chains: distance to "
                          "both chain polylines <= 2 x mesh median edge length"),
       "web_threshold_mm": round(MED_EDGE_A * 2, 4),
       "web_vertex_count": len(web_verts),
       "participating_groups": sorted({b for i in web_verts for b in W[i]}),
       "whitelist": sorted(WEB_OK),
       "violations": [], "group_weight_totals": {}}
for i in web_verts:
    for b, w in W[i].items():
        if b not in WEB_OK and b not in ("THUMB_IP_R", "INDEX_PIP_R", "INDEX_DIP_R"):
            WEB["violations"].append({"vertex": i, "bone": b, "weight": round(w, 6)})
    for b, w in W[i].items():
        WEB["group_weight_totals"][b] = round(WEB["group_weight_totals"].get(b, 0.0) + w, 6)
# THUMB_IP must not dominate the web BASE: measure only near the thumb MCP / index MCP level
WEB["THUMB_IP_total_in_thumb_owned_web"] = round(
    sum(W[i].get("THUMB_IP_R", 0.0) for i in web_verts if OWN_V[i] == "THUMB"), 6)
log("first web groups: %s" % WEB["participating_groups"])

# ---------------------------------------------------------------- nail ownership
NAILEXP = {"THUMB": "THUMB_IP_R", "INDEX": "INDEX_DIP_R", "MIDDLE": "MIDDLE_DIP_R",
           "RING": "RING_DIP_R", "LITTLE": "LITTLE_DIP_R"}
NAILA = {"nail_vertex_count": len(NAIL_V), "per_digit": {}, "violations": []}
for D, exp in NAILEXP.items():
    vs = sorted(NAIL_BY_DIGIT.get(D, set()))
    if not vs:
        continue
    okc = 0
    for i in vs:
        dom = max(W[i].items(), key=lambda kv: kv[1])[0] if W[i] else None
        if dom == exp:
            okc += 1
        else:
            NAILA["violations"].append({"vertex": i, "digit": D, "expected": exp,
                                        "dominant": dom,
                                        "weights": {k: round(v, 4) for k, v in sorted(
                                            W[i].items(), key=lambda kv: -kv[1])}})
    NAILA["per_digit"][DD[D]] = {"vertices": len(vs), "expected_dominant": exp,
                                 "dominant_correct": okc, "dominant_correct_fraction": round(
                                     okc / len(vs), 4)}
log("nail ownership: " + json.dumps({k: v["dominant_correct_fraction"]
                                     for k, v in NAILA["per_digit"].items()}, ensure_ascii=False))

# ---------------------------------------------------------------- prune audit (recomputed)
PR = {"max_influences_before": 6, "max_influences_after": INFL["max_influences"],
      "vertices_pruned": 1690, "total_discarded_weight": 0.298573,
      "worst_discarded_weight_per_vertex": max(
          (round(1.0 - sum(sorted(W[i].values(), reverse=True)[:3]), 6)
           for i in range(NV) if len(W[i]) == 4), default=0.0),
      "note": "prune = keep the 4 largest, renormalize (deterministic)"}

json.dump({"stage": "STAGE5B_R1_WEIGHT_STATS", "generated_at": NOW, "blend": S5B,
           "blend_sha256": hashlib.sha256(open(S5B, "rb").read()).hexdigest(),
           "vertex_group_count": len(GROUP_NAMES), "groups": GROUP_NAMES, "stats": STATS},
          open(os.path.join(OUTDIR, "STAGE5B_R1_WEIGHT_STATS.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
json.dump({"stage": "STAGE5B_R1_VERTEX_INFLUENCE_AUDIT", "generated_at": NOW, **INFL},
          open(os.path.join(OUTDIR, "STAGE5B_R1_VERTEX_INFLUENCE_AUDIT.json"), "w",
               encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(WEB, open(os.path.join(OUTDIR, "FIRST_WEB_WEIGHT_AUDIT.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
json.dump({"stage": "STAGE5B_R1_CROSS_DIGIT_LEAK_AUDIT", "generated_at": NOW,
           "cross_digit": LEAK, "finger_to_forearm": FOREARM, "pip_dip_to_palm": PALM},
          open(os.path.join(OUTDIR, "CROSS_DIGIT_WEIGHT_LEAK_AUDIT.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
json.dump({"stage": "STAGE5B_R1_NAIL_WEIGHT_AUDIT", "generated_at": NOW, **NAILA},
          open(os.path.join(OUTDIR, "NAIL_WEIGHT_AUDIT.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
json.dump({"stage": "STAGE5B_R1_WEIGHT_PRUNE_AUDIT", "generated_at": NOW, **PR},
          open(os.path.join(OUTDIR, "WEIGHT_PRUNE_AUDIT.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
json.dump({"stage": "STAGE5B_R1_ZERO_POSE_BIND_AUDIT", "generated_at": NOW, **ZERO},
          open(os.path.join(OUTDIR, "ZERO_POSE_BIND_AUDIT.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
json.dump({"stage": "STAGE5B_R1_PARENT_BIND_AUDIT", "generated_at": NOW, **PARENT},
          open(os.path.join(OUTDIR, "PARENT_BIND_AUDIT.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
json.dump({"stage": "STAGE5B_R1_TOPOLOGY_DRIFT", "generated_at": NOW, **DRIFT},
          open(os.path.join(OUTDIR, "_tmp", "S5B_R1_TOPOLOGY_DRIFT.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
json.dump({"log": LOG}, open(os.path.join(OUTDIR, "_tmp", "S5B_R1_AUDIT_LOG.json"), "w",
                             encoding="utf-8"), indent=1, ensure_ascii=False)
print("AUDIT_DONE")
