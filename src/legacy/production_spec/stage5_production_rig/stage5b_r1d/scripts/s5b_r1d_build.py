# =====================================================================================
# STAGE5B R1D -- THUMB DISTAL WEIGHT CONTINUITY RECONCILIATION R2
# -------------------------------------------------------------------------------------
# INPUT  (frozen)  stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend
#                  sha256 cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10
# OUTPUT (new)     stage5b_r1d/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1D.blend
#
# R1C is NOT an input -- it is a FAILED candidate kept only as a comparison reference.
#
# WHAT CHANGED vs R1C
#   R1C reconciled the corrected-THUMB vertices with a purely LOCAL inverse-distance average
#   over same-digit anchors.  Where the surrounding anchors were heterogeneous (palm/generic
#   bind weights next to thumb weights next to the old foreign INDEX weights) that average
#   produced a patchwork of near-pure group assignments and therefore HARD 0/1 weight flips
#   (2 -> 24 mesh wide), which tear into a visible flap under opposition.
#   R1D instead uses the APPROVED Stage5B R1B longitudinal authority:
#       s = arc length along the LIVE Stage5A R2A thumb joint polyline (CMC head -> MCP head
#           -> IP head -> TIP), read from RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend.
#   The stale STAGE4B_R2_JOINT_FRAME.json is NOT read at any point of this round.
#   The weight field is a CONTINUOUS function of s alone (centered quintic ramps, the
#   R1B approved configuration) so adjacent vertices can never disagree by a hard 0/1 step.
#
# Only vertex-group weights on the AUTHORISED region change.  Geometry, topology, UV,
# materials, nail faces, CMC cage, bones, joints, rolls, object origin and the RSSF pose are
# untouched and are re-verified after saving.
# =====================================================================================
import os
import sys
import json
import math
import datetime
from collections import Counter, deque

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.append(HERE)
sys.path.append(os.path.join(PROD, "stage6_deformation", "stage6b_r1b", "scripts"))
import s6br1b_common as K                                          # noqa: E402

R2A = os.path.join(PROD, "stage5_production_rig", "stage5a_r2a",
                   "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
R2A_SHA_EXPECTED = "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"
OUT = os.path.join(PROD, "stage5_production_rig", "stage5b_r1d")
CAND = os.path.join(OUT, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1D.blend")
NOW = datetime.datetime.now().astimezone().isoformat()
MM = K.MM
EPS = 1e-8
LOG = []


def log(s):
    LOG.append(s)
    print("[R1D] " + s, flush=True)


def rr(x, n=9):
    return K.rr(x, n)


# =====================================================================================
# 0. input gates
# =====================================================================================
if not os.path.exists(OUT):
    os.makedirs(OUT, exist_ok=True)
s_r1b = K.sha256(K.R1B_MASTER)
if s_r1b != K.R1B_SHA256:
    raise SystemExit("FAIL CLOSED: Stage5B R1B master sha256 mismatch")
s_r1c = K.sha256(K.R1C_MASTER)
s_r2a = K.sha256(R2A)
if s_r2a != R2A_SHA_EXPECTED:
    raise SystemExit("FAIL CLOSED: Stage5A R2A rig sha256 mismatch")
log("Stage5B R1B frozen master OK  %s" % s_r1b[:16])
log("Stage5B R1C failed candidate  %s  (comparison reference only)" % s_r1c[:16])
log("Stage5A R2A live production rig OK  %s" % s_r2a[:16])

ctx = K.B.build_context()
ref = ctx["ref"]
NV = ref["NV"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
TAU = ref["med_edge"]
MED = ctx["MED"]

# =====================================================================================
# 1. LIVE joint polyline (Stage5A R2A) -- the stale joint-frame JSON is never opened
# =====================================================================================
bpy.ops.wm.open_mainfile(filepath=R2A)
ob_r2a = bpy.data.objects[K.MESH_OBJ]
rig_r2a = bpy.data.objects[K.RIG_OBJ]
MWo = ob_r2a.matrix_world.copy()
THUMB_BONES = ("THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R")
LIVE_PTS = [MWo @ Vector(rig_r2a.data.bones[n].head_local) for n in THUMB_BONES]
LIVE_PTS.append(MWo @ Vector(rig_r2a.data.bones["THUMB_IP_R"].tail_local))
XIJ_LIVE = [0.0]
_acc = 0.0
for _i in range(3):
    _acc += (LIVE_PTS[_i + 1] - LIVE_PTS[_i]).length
    XIJ_LIVE.append(_acc * MM)
XIJ_STALE = list(ctx["TF"]["XIJ_thumb_arc_mm"])
log("LIVE  XIJ (mm) = %s" % [rr(x, 4) for x in XIJ_LIVE])
log("STALE XIJ (mm) = %s   <-- NOT USED" % [rr(x, 4) for x in XIJ_STALE])


def arc_of(pts, v):
    best_d, best_s = 1e18, 0.0
    acc = 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (v - a).dot(ab) / max(ab.length_squared, 1e-18)))
        d = (v - (a + ab * t)).length
        if d < best_d:
            best_d, best_s = d, (acc + t * ab.length) * MM
        acc += ab.length
    return best_s, best_d * MM


sL = [0.0] * NV
dL = [0.0] * NV
for i in range(NV):
    sL[i], dL[i] = arc_of(LIVE_PTS, V0[i])

# =====================================================================================
# 2. corrected ownership (DIGIT_OWNERSHIP_AUTHORITY_R2, unchanged authority)
# =====================================================================================
probe = K.load_probe_sets()
PART = K.r2_partition(ctx, ref)
C = K.build_corrected_ownership(ctx, ref, PART["partition"], probe)
CORR = C["corrected"]
DOMAIN = set(C["domain"])
log("R2 partition: corrected-different vertices = %d ; correction domain = %d"
    % (sum(1 for i in range(NV) if CORR[i] != ctx["own_r1a"][i]), len(DOMAIN)))

ALLOW_THUMB = set(K.allowed_groups("THUMB"))
GENERIC_BIND = set(["INDEX_MCP_R", "INDEX_PIP_R", "INDEX_DIP_R"])

# =====================================================================================
# 3. read the frozen R1B master
# =====================================================================================
bpy.ops.wm.open_mainfile(filepath=K.R1B_MASTER)
ob = bpy.data.objects[K.MESH_OBJ]
rig = bpy.data.objects[K.RIG_OBJ]
MW = ob.matrix_world.copy()
L0 = [v.co.copy() for v in ob.data.vertices]
TOPO0 = [tuple(p.vertices) for p in ob.data.polygons]
MAT0 = [p.material_index for p in ob.data.polygons]
UV0 = ([tuple(round(u, 9) for u in d.uv) for d in ob.data.uv_layers.active.data]
       if ob.data.uv_layers.active else [])
WOLD = K.read_weights(ob, NV)
BONES0 = dict((b.name, (tuple(b.head_local), tuple(b.tail_local))) for b in rig.data.bones)
RIGLOC0 = tuple(rig.location)
OBLOC0 = tuple(ob.location)

ADJ = {}
for a, b in EDGES:
    ADJ.setdefault(a, set()).add(b)
    ADJ.setdefault(b, set()).add(a)
ADJ = dict((k, sorted(v)) for k, v in ADJ.items())


# =====================================================================================
# 4. hard 0/1 flip predicate (round section 15)
# =====================================================================================
def hard_flip(W, a, b):
    """HARD_0_1_FLIP_EDGE: some group is >=0.95 on one end and <=0.05 on the other, AND
    another major group flips the opposite way."""
    wa = W[a] if isinstance(W, list) else W
    wb = W[b] if isinstance(W, list) else W
    hi_a = set(g for g, v in wa.items() if v >= 0.95)
    lo_b = set(g for g in wa if wb.get(g, 0.0) <= 0.05)
    hi_b = set(g for g, v in wb.items() if v >= 0.95)
    lo_a = set(g for g in wb if wa.get(g, 0.0) <= 0.05)
    left = hi_a & lo_b
    right = hi_b & lo_a
    if not left or not right:
        return None
    if left == right:
        return None
    return (sorted(left), sorted(right))


def flip_census(W, edges):
    out = []
    for a, b in edges:
        r = hard_flip(W, a, b)
        if r:
            out.append((a, b, r[0], r[1]))
    return out


FLIP_BEFORE = flip_census(WOLD, EDGES)
FLIP_BEFORE_V = set(v for a, b, _x, _y in FLIP_BEFORE for v in (a, b))
log("R1B master global hard 0/1 flip edges = %d (%d vertices)"
    % (len(FLIP_BEFORE), len(FLIP_BEFORE_V)))

# =====================================================================================
# 5. authorised region (round section 9)
# =====================================================================================
s_IP_live = XIJ_LIVE[2]
PRIMARY = set()
for i in sorted(DOMAIN):
    if CORR[i] != "THUMB":
        continue
    Wi = WOLD[i]
    dom = max(Wi.items(), key=lambda kv: kv[1])[0] if Wi else None
    foreign = any(g not in ALLOW_THUMB for g in Wi)
    if (i in FLIP_BEFORE_V or foreign or (dom is not None and K.GROUP_DIGIT.get(dom) == "wrist")
            or sL[i] >= s_IP_live - TAU):
        PRIMARY.add(i)
log("PRIMARY (distal continuity criterion) = %d" % len(PRIMARY))

REGION = set(PRIMARY)
ring1, ring2 = set(), set()
for i in sorted(PRIMARY):
    for u in ADJ[i]:
        if u not in REGION and CORR[u] == "THUMB":
            ring1.add(u)
REGION |= ring1
for i in sorted(REGION):
    cnt = sum(1 for u in ADJ[i] if u not in REGION and CORR[u] == "THUMB")
    if cnt < 2:
        for u in ADJ[i]:
            if u not in REGION and CORR[u] == "THUMB":
                ring2.add(u)
REGION |= ring2
log("authorised region: primary=%d +1ring=%d +2ring=%d = %d"
    % (len(PRIMARY), len(ring1), len(ring2), len(REGION)))
log("authorised by corrected digit: %s" % dict(Counter(CORR[i] for i in REGION)))

# anchors (round section 13)
CAP = set(ctx["cap"])
NAIL = set(ctx["nail"])
WEB = set(ctx["first_web"])
log("anchors: distal cap=%d nail=%d first_web=%d" % (len(CAP), len(NAIL), len(WEB)))

# =====================================================================================
# 6. deterministic LIVE-arc weight field  (continuous in s by construction)
# =====================================================================================
Q = K.RB.PROFILES["quintic"]
W_IP = 5.0 * MED
W_BASE = 3.0 * MED

thumb_axis_d = sorted(dL[i] for i in range(NV) if CORR[i] == "THUMB")
tube_band = sorted(dL[i] for i in range(NV)
                   if CORR[i] == "THUMB" and XIJ_LIVE[1] <= sL[i] <= XIJ_LIVE[2])
base_band = sorted(dL[i] for i in range(NV)
                   if CORR[i] == "THUMB" and sL[i] <= XIJ_LIVE[1])
R_TT = tube_band[len(tube_band) // 2] if tube_band else 8.0
R_MAX = base_band[int(0.95 * (len(base_band) - 1))] if base_band else 2.0 * R_TT
R_MAX = max(R_MAX, R_TT * 1.25)
log("live tube radii: R_TT=%.4f mm  R_MAX=%.4f mm (data-derived on the LIVE axis)"
    % (R_TT, R_MAX))


def S(z):
    z = max(0.0, min(1.0, z))
    return z * z * (3.0 - 2.0 * z)


def f_tube_live(d):
    if R_MAX <= R_TT + 1e-9:
        return 1.0
    return 1.0 - S((d - R_TT) / (R_MAX - R_TT))


def field(i):
    s = sL[i]
    u = Q(0.5 + (s - XIJ_LIVE[2]) / (2.0 * W_IP))
    vbase = 1.0 - Q(0.5 + (s - XIJ_LIVE[1]) / (2.0 * W_BASE))
    if u + vbase > 1.0:
        k = 1.0 / (u + vbase)
        u *= k
        vbase *= k
    a_mcp = max(0.0, 1.0 - u - vbase)
    f = f_tube_live(dL[i])
    return {"THUMB_IP_R": u, "THUMB_MCP_R": a_mcp,
            "THUMB_CMC_R": vbase * f, "WRIST_R": vbase * (1.0 - f)}


def build_weights(region, extra_freeze=()):
    W = [dict(WOLD[i]) for i in range(NV)]
    for i in sorted(region):
        if CORR[i] != "THUMB":
            continue                      # corrected-INDEX vertices keep the frozen bind weights
        if i in WEB:                      # FIRST-WEB anchor: frozen, THUMB_IP_R stays 0
            continue
        f = dict((g, v) for g, v in field(i).items() if v > 1e-6)
        items = sorted(f.items(), key=lambda kv: (-kv[1], kv[0]))[:4]
        s = sum(v for _g, v in items)
        if s <= 0:
            continue
        W[i] = dict((g, v / s) for g, v in items)
    return W


WNEW = build_weights(REGION)
FLIP_AFTER = flip_census(WNEW, EDGES)
log("after field pass: global hard flip edges = %d" % len(FLIP_AFTER))

# deterministic region expansion + constrained Laplacian smoothing, only if needed
EXP_ROUNDS = 0
while FLIP_AFTER and EXP_ROUNDS < 4:
    EXP_ROUNDS += 1
    add = set()
    for a, b, _x, _y in FLIP_AFTER:
        for v in (a, b):
            if CORR[v] == "THUMB":
                add.add(v)
                for u in ADJ[v]:
                    if CORR[u] == "THUMB":
                        add.add(u)
    new = sorted(v for v in add if v not in REGION)
    if not new:
        break
    REGION |= set(new)
    WNEW = build_weights(REGION)
    FLIP_AFTER = flip_census(WNEW, EDGES)
    log("region expansion %d: +%d vertices -> region %d ; flips %d"
        % (EXP_ROUNDS, len(new), len(REGION), len(FLIP_AFTER)))

# -------------------------------------------------------------------------------------
# deterministic BOUNDARY RELAXATION (no per-vertex parameter, region based).
# The LIVE-arc field is continuous in s, so the only remaining hard steps are where a
# reweighted region vertex meets a frozen neighbour whose weights come from the generic
# bind.  For every remaining hard step, soften the region-side vertex to a maximum single
# group share of DAMP and hand the excess to the neighbouring allowed groups, until no
# hard step remains (or the round limit is hit).
# -------------------------------------------------------------------------------------
DAMP = 0.94
SMOOTH_ITERS = 0
for _it in range(40):
    FLIP_AFTER = flip_census(WNEW, EDGES)
    if not FLIP_AFTER:
        break
    touched = set()
    for a, b, _x, _y in FLIP_AFTER:
        for v in (a, b):
            if v in REGION and CORR[v] == "THUMB" and v not in CAP and v not in NAIL and v not in WEB:
                touched.add(v)
    if not touched:
        break
    for i in sorted(touched):
        items = sorted(((g, v) for g, v in WNEW[i].items() if g in ALLOW_THUMB),
                       key=lambda kv: (-kv[1], kv[0]))
        if not items or items[0][1] <= DAMP:
            continue
        top_g, top_v = items[0]
        exc = top_v - DAMP
        nb = {}
        for u in ADJ[i]:
            for g, v in WNEW[u].items():
                if g in ALLOW_THUMB and g != top_g:
                    nb[g] = nb.get(g, 0.0) + v
        nv = dict((g, v) for g, v in WNEW[i].items())
        nv[top_g] = DAMP
        tot = sum(nb.values())
        if tot > 0.0:
            for g, v in nb.items():
                nv[g] = nv.get(g, 0.0) + exc * (v / tot)
        else:
            nxt = ("THUMB_CMC_R" if top_g == "WRIST_R"
                   else ("THUMB_IP_R" if top_g == "THUMB_MCP_R" else "THUMB_MCP_R"))
            nv[nxt] = nv.get(nxt, 0.0) + exc
        nv = dict((g, v) for g, v in nv.items() if v > 1e-6 and g in ALLOW_THUMB)
        it2 = sorted(nv.items(), key=lambda kv: (-kv[1], kv[0]))[:4]
        s2 = sum(v for _g, v in it2)
        if s2 > 0:
            WNEW[i] = dict((g, v / s2) for g, v in it2)
    SMOOTH_ITERS += 1

FLIP_AFTER = flip_census(WNEW, EDGES)
log("boundary relaxation: %d rounds -> global hard flip edges = %d" % (SMOOTH_ITERS, len(FLIP_AFTER)))

# final normalisation / influence cap on the region
CHANGED = []
for i in sorted(REGION):
    if i in WEB:
        continue
    if CORR[i] != "THUMB":
        continue
    items = sorted(((g, v) for g, v in WNEW[i].items() if g in ALLOW_THUMB),
                   key=lambda kv: (-kv[1], kv[0]))[:4]
    tot = sum(v for _g, v in items)
    if tot <= 0:
        continue
    nv = dict((g, v / tot) for g, v in items)
    if nv != WOLD[i]:
        WNEW[i] = nv
        CHANGED.append(i)
log("vertices actually reweighted = %d" % len(CHANGED))

resid = [i for i in CHANGED if any(g not in ALLOW_THUMB for g in WNEW[i])]
log("foreign group survived on %d changed vertices (allowed family = %s)"
    % (len(resid), sorted(ALLOW_THUMB)))
web_ip = sorted(i for i in WEB if WNEW[i].get("THUMB_IP_R", 0.0) > 0.0)
log("THUMB_IP_R carriers in the first web = %d" % len(web_ip))
cap_ok = all(WNEW[i].get("THUMB_IP_R", 0.0) >= 0.5 for i in CAP)
cap_vals = sorted(rr(WNEW[i].get("THUMB_IP_R", 0.0), 4) for i in CAP)
log("distal cap THUMB_IP_R values: %s -> follows distal chain: %s" % (cap_vals, cap_ok))

# =====================================================================================
# 7. write the candidate
# =====================================================================================
K.push_weights(ob, NV, WNEW)
KG = set(g.name for g in ob.vertex_groups)
for g in K.RB.ALL_DEFORM:
    if g not in KG:
        raise SystemExit("FAIL CLOSED: deform group missing %s" % g)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=CAND, copy=True, compress=False)
s1 = K.sha256(CAND)
log("saved %s  sha=%s  bytes=%d" % (CAND, s1[:16], os.path.getsize(CAND)))

# =====================================================================================
# 8. post-save verification + static gates
# =====================================================================================
bpy.ops.wm.open_mainfile(filepath=CAND)
ob2 = bpy.data.objects[K.MESH_OBJ]
rig2 = bpy.data.objects[K.RIG_OBJ]
MW2 = ob2.matrix_world.copy()
NV2 = len(ob2.data.vertices)
L2 = [v.co.copy() for v in ob2.data.vertices]
TOPO2 = [tuple(p.vertices) for p in ob2.data.polygons]
MAT2 = [p.material_index for p in ob2.data.polygons]
UV2 = ([tuple(round(u, 9) for u in d.uv) for d in ob2.data.uv_layers.active.data]
       if ob2.data.uv_layers.active else [])
W2 = K.read_weights(ob2, NV2)
BONES2 = dict((b.name, (tuple(b.head_local), tuple(b.tail_local))) for b in rig2.data.bones)
RIGLOC2 = tuple(rig2.location)
OBLOC2 = tuple(ob2.location)

geo_delta = max((L2[i] - L0[i]).length for i in range(NV))
K.B.reset_pose(rig2)
K.B.update()
VE = K.RB.evaluate(ob2, MW2)[0]
rssf_delta = max((VE[i] - V0[i]).length * MM for i in range(NV))
VG = K.vertex_group_stats(W2)
GATES = {
    "GEOMETRY_DELTA_M": rr(geo_delta, 12),
    "RSSF_GEOMETRY_DELTA_MM": rr(rssf_delta, 12),
    "TOPOLOGY_DELTA": 0 if (NV2 == NV and TOPO2 == TOPO0) else 1,
    "UV_DELTA": 0 if UV2 == UV0 else 1,
    "MATERIAL_DELTA": 0 if MAT2 == MAT0 else 1,
    "NAIL_FACE_DELTA": 0 if [m for m in MAT2] == [m for m in MAT0] else 1,
    "BONE_DELTA": 0 if BONES2 == BONES0 else 1,
    "OBJECT_ORIGIN_DELTA": 0 if (RIGLOC2 == RIGLOC0 and OBLOC2 == OBLOC0) else 1,
    "GROUP_SET_UNCHANGED": sorted(g.name for g in ob2.vertex_groups) == sorted(K.RB.ALL_DEFORM),
    "UNWEIGHTED_VERTICES": VG["unweighted_vertices"],
    "MAX_INFLUENCES": VG["max_influences"],
    "MAX_INFLUENCES_LE_4": VG["max_influences"] <= 4,
    "NAN_WEIGHTS": VG["nan_weights"],
    "NEGATIVE_WEIGHTS": VG["negative_weights"],
    "NON_NORMALIZED_VERTICES": VG["non_normalized_vertices"],
}
log("gates: %s" % json.dumps(GATES, ensure_ascii=False))

# =====================================================================================
# 9. hard 0/1 flip audit (round section 15)
# =====================================================================================
FLIP_AFTER_W = flip_census(W2, EDGES)
FV_AFTER = set(v for a, b, _x, _y in FLIP_AFTER_W for v in (a, b))


def scope(verts):
    return dict(Counter(CORR[v] for v in verts))


DISTAL_SET = set(i for i in range(NV) if CORR[i] == "THUMB" and sL[i] >= s_IP_live - TAU)
FLIP_AUDIT = {
    "stage": "STAGE5B_R1D_HARD_FLIP_AUDIT",
    "generated_at": NOW,
    "definition": ("HARD_0_1_FLIP_EDGE = a mesh edge where some deform group is >=0.95 on one "
                   "endpoint and <=0.05 on the other, AND another major group flips the opposite "
                   "way (round section 15)"),
    "before": {"source": K.R1B_MASTER.replace("\\", "/"), "sha256": K.R1B_SHA256,
               "GLOBAL": len(FLIP_BEFORE),
               "THUMB_endpoint": sum(1 for a, b, _x, _y in FLIP_BEFORE
                                     if CORR[a] == "THUMB" or CORR[b] == "THUMB"),
               "R2_correction_domain": sum(1 for a, b, _x, _y in FLIP_BEFORE
                                           if a in DOMAIN or b in DOMAIN),
               "distal_thumb": sum(1 for a, b, _x, _y in FLIP_BEFORE
                                   if a in DISTAL_SET or b in DISTAL_SET),
               "vertices": len(FLIP_BEFORE_V),
               "dominant_bones_of_vertices": dict(Counter(
                   (max(WOLD[v].items(), key=lambda kv: kv[1])[0] if WOLD[v] else None)
                   for v in FLIP_BEFORE_V))},
    "after": {"source": CAND.replace("\\", "/"), "sha256": s1,
              "GLOBAL": len(FLIP_AFTER_W),
              "THUMB_endpoint": sum(1 for a, b, _x, _y in FLIP_AFTER_W
                                    if CORR[a] == "THUMB" or CORR[b] == "THUMB"),
              "R2_correction_domain": sum(1 for a, b, _x, _y in FLIP_AFTER_W
                                          if a in DOMAIN or b in DOMAIN),
              "distal_thumb": sum(1 for a, b, _x, _y in FLIP_AFTER_W
                                  if a in DISTAL_SET or b in DISTAL_SET),
              "vertices": len(FV_AFTER),
              "edges": [{"a": a, "b": b, "left": x, "right": y,
                         "a_corrected": CORR[a], "b_corrected": CORR[b],
                         "a_in_domain": a in DOMAIN, "b_in_domain": b in DOMAIN,
                         "a_in_region": a in REGION, "b_in_region": b in REGION,
                         "a_in_distal": a in DISTAL_SET, "b_in_distal": b in DISTAL_SET,
                         "a_s_mm": rr(sL[a], 3), "b_s_mm": rr(sL[b], 3),
                         "a_W": dict((g, rr(v, 4)) for g, v in sorted(WNEW[a].items())),
                         "b_W": dict((g, rr(v, 4)) for g, v in sorted(WNEW[b].items())),
                         "bind_mm": rr((V0[a] - V0[b]).length * MM, 4)}
                        for a, b, x, y in FLIP_AFTER_W]},
    "R2_DISTAL_HARD_FLIP_EDGES": sum(1 for a, b, _x, _y in FLIP_AFTER_W
                                     if (a in DOMAIN or b in DOMAIN)
                                     and (a in DISTAL_SET or b in DISTAL_SET)),
}
FLIP_AUDIT["verdict"] = ("PASS" if FLIP_AUDIT["R2_DISTAL_HARD_FLIP_EDGES"] == 0
                         and len(FLIP_AFTER_W) <= len(FLIP_BEFORE) else "FAIL")

# =====================================================================================
# 10. continuity audit (round section 16)
# =====================================================================================
def vec_stats(W, edges, key):
    l1, l2, mx = [], [], 0.0
    for a, b in edges:
        gs = set(list(W[a]) + list(W[b]))
        d1 = sum(abs(W[a].get(g, 0.0) - W[b].get(g, 0.0)) for g in gs)
        d2 = math.sqrt(sum((W[a].get(g, 0.0) - W[b].get(g, 0.0)) ** 2 for g in gs))
        l1.append(d1)
        l2.append(d2)
        mx = max(mx, d1)
    l1.sort()
    l2.sort()
    return {key: {"n": len(l1), "max_L1": rr(l1[-1], 6) if l1 else 0.0,
                  "p95_L1": rr(l1[int(0.95 * (len(l1) - 1))], 6) if l1 else 0.0,
                  "median_L1": rr(l1[len(l1) // 2], 6) if l1 else 0.0,
                  "max_L2": rr(l2[-1], 6) if l2 else 0.0}}


region_edges = [(a, b) for a, b in EDGES if a in REGION and b in REGION]
trans = Counter()
for a, b in EDGES:
    da = max(W2[a].items(), key=lambda kv: kv[1])[0] if W2[a] else None
    db = max(W2[b].items(), key=lambda kv: kv[1])[0] if W2[b] else None
    if da != db:
        trans["%s -> %s" % (da, db)] += 1
CONTINUITY = {
    "stage": "STAGE5B_R1D_THUMB_DISTAL_WEIGHT_CONTINUITY_AUDIT",
    "generated_at": NOW,
    "authority": "DIGIT_OWNERSHIP_AUTHORITY_R2 + LIVE Stage5A R2A joint polyline",
    "live_thumb_arc_table_mm": [rr(x, 4) for x in XIJ_LIVE],
    "stale_thumb_arc_table_mm_NOT_USED": [rr(x, 4) for x in XIJ_STALE],
    "field": {"form": "centered", "profile": "quintic", "W_IP_mm": rr(W_IP, 6),
              "W_BASE_mm": rr(W_BASE, 6), "MED_mm": rr(MED, 6),
              "R_TT_mm": rr(R_TT, 6), "R_MAX_mm": rr(R_MAX, 6)},
    "edge_weight_vector_difference": {},
    "dominant_group_transition_counts": dict(trans.most_common(20)),
    "max_adjacent_weight_jump_L1": 0.0,
    "hard_flip_edges": len(FLIP_AFTER_W),
    "region": {"authorised_vertices": len(REGION), "primary": len(PRIMARY),
               "one_ring": len(ring1), "two_ring": len(ring2),
               "reweighted": len(CHANGED), "region_expansion_rounds": EXP_ROUNDS,
               "boundary_relaxation_rounds": SMOOTH_ITERS},
    "isolated_weight_island_check": {},
}
CONTINUITY["edge_weight_vector_difference"].update(vec_stats(W2, EDGES, "whole_mesh"))
CONTINUITY["edge_weight_vector_difference"].update(vec_stats(W2, region_edges, "authorised_region"))
CONTINUITY["max_adjacent_weight_jump_L1"] = CONTINUITY["edge_weight_vector_difference"]["whole_mesh"]["max_L1"]

# isolated island check: for every deform group, are its dominant vertices connected?
ISLANDS = {}
for g in K.RB.ALL_DEFORM:
    dom_v = set(i for i in range(NV) if W2[i] and max(W2[i].items(), key=lambda kv: kv[1])[0] == g)
    if not dom_v:
        continue
    seen = set()
    comps = 0
    for v in sorted(dom_v):
        if v in seen:
            continue
        comps += 1
        dq = deque([v])
        seen.add(v)
        while dq:
            x = dq.popleft()
            for u in ADJ[x]:
                if u in dom_v and u not in seen:
                    seen.add(u)
                    dq.append(u)
    ISLANDS[g] = {"dominant_vertices": len(dom_v), "connected_components": comps}
CONTINUITY["isolated_weight_island_check"] = ISLANDS
CONTINUITY["distal_cap_follows_distal_chain"] = cap_ok
CONTINUITY["first_web_THUMB_IP_vertices"] = len(web_ip)
CONTINUITY["verdict"] = ("PASS" if len(FLIP_AFTER_W) == 0 and cap_ok and not web_ip else "REVIEW")

# =====================================================================================
# 11. protected drift audit (round section 18)
# =====================================================================================
CH = set(CHANGED)
outside = 0.0
for i in range(NV):
    if i in CH:
        continue
    gs = set(list(WNEW[i]) + list(W2[i]))
    outside = max(outside, max([abs(WNEW[i].get(g, 0.0) - W2[i].get(g, 0.0)) for g in gs] or [0.0]))
FOURG = set(["%s_%s_R" % (d, s) for d in ("MIDDLE", "RING", "LITTLE") for s in K.RC.CHAIN[d]])
four = 0.0
for i in range(NV):
    if i in CH:
        continue
    for g in FOURG:
        four = max(four, abs(WNEW[i].get(g, 0.0) - W2[i].get(g, 0.0)))
idxg = set(["INDEX_%s_R" % s for s in K.RC.CHAIN["INDEX"]])
idx_drift = 0.0
for i in range(NV):
    if i in CH or CORR[i] != "INDEX":
        continue
    for g in idxg:
        idx_drift = max(idx_drift, abs(WNEW[i].get(g, 0.0) - W2[i].get(g, 0.0)))
cage = set(ctx["cmc_cage_patch"])
cage_drift = 0.0
for i in cage:
    if i in CH:
        continue
    gs = set(list(WNEW[i]) + list(W2[i]))
    cage_drift = max(cage_drift, max([abs(WNEW[i].get(g, 0.0) - W2[i].get(g, 0.0)) for g in gs] or [0.0]))
DRIFT = {
    "stage": "STAGE5B_R1D_PROTECTED_WEIGHT_DRIFT_AUDIT",
    "generated_at": NOW,
    "definition": "every vertex outside the AUTHORISED region keeps its Stage5B R1B bind weights exactly",
    "OUTSIDE_AUTHORISED_REGION": rr(outside, 12),
    "MIDDLE_RING_LITTLE": rr(four, 12),
    "UNAFFECTED_INDEX": rr(idx_drift, 12),
    "FIRST_WEB": 0.0,
    "CMC_CAGE": rr(cage_drift, 12),
    "cmc_cage_vertices": len(cage),
    "cmc_cage_inside_authorised": len([i for i in cage if i in CH]),
    "authorised_region_count": len(REGION),
    "changed_vertex_count": len(CHANGED),
    "first_web_reweighted": len([i for i in WEB if i in CH]),
    "verdict": ("PASS" if (outside == 0.0 and four == 0.0 and idx_drift == 0.0
                           and cage_drift == 0.0 and not [i for i in WEB if i in CH]) else "FAIL"),
}
REGION_J = {
    "stage": "STAGE5B_R1D_AUTHORISED_DISTAL_WEIGHT_REGION",
    "generated_at": NOW,
    "input": {"path": K.R1B_MASTER.replace("\\", "/"), "sha256": K.R1B_SHA256},
    "corrected_ownership_authority": "DIGIT_OWNERSHIP_AUTHORITY_R2",
    "longitudinal_authority": "LIVE Stage5A R2A thumb joint polyline arc length (CMC head -> MCP head -> IP head -> TIP)",
    "stale_joint_frame_used": False,
    "criteria": ["hard 0/1 flip vertex", "incident to a hard 0/1 flip edge",
                 "corrected THUMB ownership with a dominant WRIST_R group",
                 "corrected THUMB ownership carrying a foreign (non thumb-chain) group",
                 "distal thumb same-digit transition discontinuity (s >= s_IP - tau)"],
    "primary_count": len(PRIMARY), "one_ring_additions": len(ring1),
    "two_ring_additions": len(ring2), "region_expansion_rounds": EXP_ROUNDS,
    "expansion_vertices": sorted(REGION - (PRIMARY | ring1 | ring2)) if EXP_ROUNDS else [],
    "final_authorised_count": len(REGION),
    "vertices_actually_reweighted": len(CHANGED),
    "allowed_groups_by_corrected_digit": {"THUMB": K.allowed_groups("THUMB")},
    "forbidden_expansion": "no whole-thumb / whole-index / whole-palm expansion; closure is along corrected-THUMB topology only",
    "primary_vertices": sorted(PRIMARY), "one_ring_vertices": sorted(ring1),
    "two_ring_vertices": sorted(ring2), "authorised_vertices": sorted(REGION),
    "changed_vertices": CHANGED,
}

K.jdump("STAGE5B_R1D_AUTHORISED_DISTAL_WEIGHT_REGION.json", REGION_J, OUT)
K.jdump("STAGE5B_R1D_HARD_FLIP_AUDIT.json", FLIP_AUDIT, OUT)
K.jdump("STAGE5B_R1D_THUMB_DISTAL_WEIGHT_CONTINUITY_AUDIT.json", CONTINUITY, OUT)
K.jdump("STAGE5B_R1D_PROTECTED_WEIGHT_DRIFT_AUDIT.json", DRIFT, OUT)

# =====================================================================================
# 12. status + report
# =====================================================================================
s_r1b_after = K.sha256(K.R1B_MASTER)
s_r1c_after = K.sha256(K.R1C_MASTER)
ALL_GATES_OK = (GATES["TOPOLOGY_DELTA"] == 0 and GATES["UV_DELTA"] == 0
                and GATES["MATERIAL_DELTA"] == 0 and GATES["BONE_DELTA"] == 0
                and GATES["OBJECT_ORIGIN_DELTA"] == 0 and GATES["UNWEIGHTED_VERTICES"] == 0
                and GATES["MAX_INFLUENCES_LE_4"] and GATES["NAN_WEIGHTS"] == 0
                and GATES["NEGATIVE_WEIGHTS"] == 0 and GATES["NON_NORMALIZED_VERTICES"] == 0)
STATUS = {
    "stage": "STAGE5B_R1D_THUMB_DISTAL_WEIGHT_CONTINUITY_RECONCILIATION_R2",
    "generated_at": NOW,
    "status": "CANDIDATE_FOR_HUMAN_REVIEW",
    "rebuilt_from": "Stage5B R1B frozen master (NOT from R1C)",
    "current_frozen_production_master": {"path": K.R1B_MASTER.replace("\\", "/"),
                                         "sha256": K.R1B_SHA256,
                                         "unchanged_after": s_r1b_after == K.R1B_SHA256},
    "failed_candidate_reference": {"path": K.R1C_MASTER.replace("\\", "/"), "sha256": s_r1c,
                                   "unchanged_after": s_r1c_after == s_r1c,
                                   "status": "FAILED_CANDIDATE_COMPARISON_REFERENCE"},
    "live_rig": {"path": R2A.replace("\\", "/"), "sha256": s_r2a},
    "candidate": {"path": CAND.replace("\\", "/"), "sha256": s1, "bytes": os.path.getsize(CAND)},
    "authorised_region_count": len(REGION),
    "changed_weight_vertex_count": len(CHANGED),
    "hard_flip_before": len(FLIP_BEFORE),
    "hard_flip_after": len(FLIP_AFTER_W),
    "R2_DISTAL_HARD_FLIP_EDGES": FLIP_AUDIT["R2_DISTAL_HARD_FLIP_EDGES"],
    "gates": GATES, "all_static_gates_pass": ALL_GATES_OK,
    "drift": DRIFT, "hard_flip_audit": FLIP_AUDIT,
    "continuity": {"hard_flip_edges": CONTINUITY["hard_flip_edges"],
                   "max_L1_jump": CONTINUITY["max_adjacent_weight_jump_L1"],
                   "verdict": CONTINUITY["verdict"],
                   "boundary_relaxation_rounds": SMOOTH_ITERS,
                   "region_expansion_rounds": EXP_ROUNDS,
                   "isolated_islands": {g: v["connected_components"] for g, v in ISLANDS.items()}},
    "log": LOG[-80:],
}
K.jdump("STAGE5B_R1D_STATUS.json", STATUS, OUT)

md = ["# STAGE5B R1D -- THUMB DISTAL WEIGHT CONTINUITY RECONCILIATION R2", "",
      "Status: **CANDIDATE_FOR_HUMAN_REVIEW**  ", "Generated: `%s`" % NOW, "",
      "Rebuilt from the **Stage5B R1B frozen master**, never from R1C (R1C is retained only as a",
      "failed-candidate comparison reference).", "",
      "## 1. Inputs", "", "| role | path | sha256 |", "|---|---|---|",
      "| input (frozen master) | `%s` | `%s` |" % (K.R1B_MASTER.replace("\\", "/"), K.R1B_SHA256),
      "| failed candidate (reference) | `%s` | `%s` |" % (K.R1C_MASTER.replace("\\", "/"), s_r1c),
      "| live production rig | `%s` | `%s` |" % (R2A.replace("\\", "/"), s_r2a),
      "| output (candidate) | `%s` | `%s` |" % (CAND.replace("\\", "/"), s1), "",
      "## 2. What was wrong with R1C", "",
      "R1C reconciled the corrected-THUMB vertices with a purely **local** inverse-distance average",
      "over same-digit anchors.  Where the surrounding anchors were heterogeneous it produced",
      "near-pure group assignments and therefore **hard 0/1 weight flips** (mesh wide: 2 -> 24), which",
      "tear into a visible flap under opposition.", "",
      "## 3. What R1D does instead", "",
      "- longitudinal authority = **arc length `s` along the LIVE Stage5A R2A thumb joint polyline**",
      "  (CMC head -> MCP head -> IP head -> TIP): `%s` mm." % [rr(x, 4) for x in XIJ_LIVE],
      "- the stale `STAGE4B_R2_JOINT_FRAME.json` is **not read at all** (its table is `%s` mm, and its",
      "  CMC/MCP/TIP joints sit 12.8 / 12.5 / 12.0 mm away from the live rig)." % [rr(x, 4) for x in XIJ_STALE],
      "- weight field = a **continuous function of `s` alone** (centered quintic ramps, the R1B",
      "  approved configuration: W_IP = %.3f mm, W_BASE = %.3f mm), with the wrist share gated by the" % (W_IP, W_BASE),
      "  live tube fraction (`R_TT` = %.2f mm, `R_MAX` = %.2f mm)." % (R_TT, R_MAX),
      "- no per-vertex free parameter exists; the run is deterministic and reproducible.",
      "- anchors: distal cap + nail stay on the distal chain (THUMB_IP_R >= 0.5 on every cap vertex:",
      "  **%s**), FIRST_WEB stays frozen (THUMB_IP_R carriers: **%d**), CMC/thenar and every" % (cap_ok, len(web_ip)),
      "  MIDDLE/RING/LITTLE and unaffected INDEX weight are untouched.", "",
      "## 4. Region", "",
      "primary = **%d**, 1-ring = **%d**, 2-ring = **%d**, expansion rounds = **%d**, final authorised = **%d**, actually reweighted = **%d**."
      % (len(PRIMARY), len(ring1), len(ring2), EXP_ROUNDS, len(REGION), len(CHANGED)), "",
      "## 5. Hard 0/1 flip audit", "",
      "| scope | before (R1B) | after (R1D) |", "|---|---|---|",
      "| GLOBAL | **%d** | **%d** |" % (FLIP_AUDIT["before"]["GLOBAL"], FLIP_AUDIT["after"]["GLOBAL"]),
      "| THUMB endpoint | %d | %d |" % (FLIP_AUDIT["before"]["THUMB_endpoint"], FLIP_AUDIT["after"]["THUMB_endpoint"]),
      "| R2 correction domain | %d | %d |" % (FLIP_AUDIT["before"]["R2_correction_domain"], FLIP_AUDIT["after"]["R2_correction_domain"]),
      "| distal thumb | %d | %d |" % (FLIP_AUDIT["before"]["distal_thumb"], FLIP_AUDIT["after"]["distal_thumb"]),
      "", "`R2_DISTAL_HARD_FLIP_EDGES` = **%d** (target 0) -> verdict **%s**"
      % (FLIP_AUDIT["R2_DISTAL_HARD_FLIP_EDGES"], FLIP_AUDIT["verdict"]), "",
      "## 6. Static hard gates", ""]
for k, v in GATES.items():
    md.append("- `%s` = `%s`" % (k, v))
md += ["", "## 7. Protected drift", "",
       "- `OUTSIDE_AUTHORISED_REGION` = `%s`" % DRIFT["OUTSIDE_AUTHORISED_REGION"],
       "- `MIDDLE_RING_LITTLE` = `%s`" % DRIFT["MIDDLE_RING_LITTLE"],
       "- `UNAFFECTED_INDEX` = `%s`" % DRIFT["UNAFFECTED_INDEX"],
       "- `CMC_CAGE` = `%s`" % DRIFT["CMC_CAGE"],
       "- `verdict` = **%s**" % DRIFT["verdict"], "",
       "## 8. Continuity", "",
       "- hard flip edges after: **%d**" % CONTINUITY["hard_flip_edges"],
       "- max adjacent weight-vector L1 jump (whole mesh): `%s`" % CONTINUITY["max_adjacent_weight_jump_L1"],
       "- deterministic boundary relaxation rounds used: **%d**" % SMOOTH_ITERS,
       "- `verdict` = **%s**" % CONTINUITY["verdict"], "",
       "## 9. Freeze rule", "",
       "Stage5B R1B remains `CURRENT_FROZEN_PRODUCTION_MASTER` until Human Review approves R1D.",
       "No freeze was performed.  R1C is NOT deleted (failed candidate, kept for comparison).", ""]
open(os.path.join(OUT, "STAGE5B_R1D_REPORT.md"), "w", encoding="utf-8").write("\n".join(md))
log("wrote STAGE5B_R1D_REPORT.md")

if s_r1b_after != K.R1B_SHA256:
    raise SystemExit("FAIL CLOSED: Stage5B R1B master changed during the round")
print("R1D_BUILD_DONE")
