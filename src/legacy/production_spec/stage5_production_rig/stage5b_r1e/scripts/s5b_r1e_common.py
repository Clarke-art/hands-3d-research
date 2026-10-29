# =====================================================================================
# STAGE5B R1E -- LOCAL WEIGHT RECONCILIATION FROM R1B
#                  shared authorities / geometry / weight-field construction
# -------------------------------------------------------------------------------------
# FROZEN INPUT (the ONLY skin master input) :
#   stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend
#   sha256 cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10
# R1C / R1D are FAILED_CANDIDATE_REFERENCE_ONLY and are never read as a source.
#
# OWNERSHIP AUTHORITY : DIGIT_OWNERSHIP_AUTHORITY_R3  (HUMAN_APPROVED) read BYTE-IDENTICAL
#   from stage6_deformation/stage6b_r3_thumb_tip_ownership_boundary/
#   R3 defines the DIGIT FAMILY DOMAIN ONLY.  It is NOT a skin-weight authority
#   (section 6 of the round spec).  First-web keeps its own approved blend authority.
#
# LONGITUDINAL AUTHORITY : APPROVED_JOINT_POLYLINE_ARC_LENGTH measured on the LIVE
#   Stage5A R2A production rig.  The stale stage4c_r2/STAGE4B_R2_JOINT_FRAME.json is
#   NEVER read anywhere in this round.
# =====================================================================================
import os
import sys
import json
import math
import hashlib
from collections import Counter, deque

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
R1E = os.path.abspath(os.path.join(HERE, ".."))
PROD = os.path.abspath(os.path.join(R1E, "..", ".."))
S5 = os.path.join(PROD, "stage5_production_rig")
S6D = os.path.join(PROD, "stage6_deformation")
R3D = os.path.join(S6D, "stage6b_r3_thumb_tip_ownership_boundary")
PA = os.path.join(S6D, "stage6b_r1a_seam_provenance")
if os.path.join(S6D, "stage6a", "scripts") not in sys.path:
    sys.path.append(os.path.join(S6D, "stage6a", "scripts"))

MM = 1000.0
EPS = 1e-8
MAX_INF = 4
MESH_OBJ = "Hand  - Realistic"
RIG_OBJ = "RIGHT_HAND_PRODUCTION_RIG"

# ------------------------------------------------------------------ frozen inputs
R1B_MASTER = os.path.join(S5, "stage5b_r1b", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend")
R1B_SHA256 = "cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10"
R1C_MASTER = os.path.join(S5, "stage5b_r1c", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1C.blend")
R1C_SHA256 = "396e82207d6afba88d634d7c2c796648fba49b9fbc6b15a7c35f989bc868aef7"
R1D_MASTER = os.path.join(S5, "stage5b_r1d", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1D.blend")
R1D_SHA256 = "bdf69683f19829c3a86986f8c743e2d7290982e53ae632770e2a7d58e56f20eb"
R2A = os.path.join(S5, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
R2A_SHA256 = "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"
S6A_R1B_HARNESS = os.path.join(S6D, "stage6a_r1b", "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1B.blend")
S6A_R1B_HARNESS_SHA256 = "4e669ba720993beb579eef27039c221063d46f9a2ebe31f30d97888282c8c316"
S6B_R1B_HARNESS = os.path.join(S6D, "stage6b_r1b", "RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1B.blend")
S6B_R1B_HARNESS_SHA256 = "295a73944dad1d345e370dd2b12393d4edebcd42a86582e6f307c21a2aaaa612"
S6B_R1_HARNESS = os.path.join(S6D, "stage6b", "RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1.blend")
S6B_R1_HARNESS_SHA256 = "4b6200899fe4d2f5a67e3254aec2a5cb17b734b14acefe381a2ac9c1241f549d"

R3_FILES = {
    "digit_ownership_authority_r3_json": os.path.join(R3D, "DIGIT_OWNERSHIP_AUTHORITY_R3.json"),
    "digit_ownership_authority_r3_md": os.path.join(R3D, "DIGIT_OWNERSHIP_AUTHORITY_R3.md"),
    "thumb_tip_ownership_boundary_r3_status": os.path.join(R3D, "THUMB_TIP_OWNERSHIP_BOUNDARY_R3_STATUS.json"),
    "thumb_tip_ownership_boundary_r3_report": os.path.join(R3D, "THUMB_TIP_OWNERSHIP_BOUNDARY_R3_REPORT.md"),
    "r3_ownership_labels": os.path.join(R3D, "R3_OWNERSHIP_LABELS.json"),
    "r3_boundary_connectedness_audit": os.path.join(R3D, "R3_BOUNDARY_CONNECTEDNESS_AUDIT.json"),
    "r3_class_a_preservation_audit": os.path.join(R3D, "R3_CLASS_A_PRESERVATION_AUDIT.json"),
    "r3_edge498_forensic_audit": os.path.join(R3D, "R3_EDGE498_FORENSIC_AUDIT.json"),
    "r3_island_audit": os.path.join(R3D, "R3_ISLAND_AUDIT.json"),
    "r3_r2_boundary_22_edge_reconciliation": os.path.join(R3D, "R3_R2_BOUNDARY_22_EDGE_RECONCILIATION.json"),
    "r3_reproducibility_audit": os.path.join(R3D, "R3_REPRODUCIBILITY_AUDIT.json"),
    "r3_strong_anchor_audit": os.path.join(R3D, "R3_STRONG_ANCHOR_AUDIT.json"),
    "r3_ambiguous_vertex_audit": os.path.join(R3D, "R3_AMBIGUOUS_VERTEX_AUDIT.json"),
}
PROBE_FILES = {
    "stage6b_r1a_class_a": os.path.join(PA, "STAGE6B_R1A_CLASS_A_VALID_WEB_EDGES.json"),
    "stage6b_r1a_class_b": os.path.join(PA, "STAGE6B_R1A_CLASS_B_OWNERSHIP_MISCLASSIFICATION.json"),
}
CASE_MATRIX = os.path.join(S6D, "stage6b", "STAGE6B_CASE_MATRIX.json")

STALE_JOINT_FRAME = os.path.join(PROD, "stage4_blender", "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json")
CMC_AUDIT = os.path.join(PROD, "stage4_blender", "stage4a_r2", "CMC_LOCAL_RETOPO_AUDIT_R2.json")

DIGITS = ["THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"]
SEGMENTS = {"THUMB": ["CMC", "MCP", "IP"],
            "INDEX": ["MCP", "PIP", "DIP"], "MIDDLE": ["MCP", "PIP", "DIP"],
            "RING": ["MCP", "PIP", "DIP"], "LITTLE": ["MCP", "PIP", "DIP"]}
DEFORM = ["WRIST_R"] + ["%s_%s_R" % (d, s) for d in DIGITS for s in SEGMENTS[d]]
assert len(DEFORM) == 16, DEFORM

BONE_CHAIN = {"THUMB": ("THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R"),
              "INDEX": ("INDEX_MCP_R", "INDEX_PIP_R", "INDEX_DIP_R"),
              "MIDDLE": ("MIDDLE_MCP_R", "MIDDLE_PIP_R", "MIDDLE_DIP_R"),
              "RING": ("RING_MCP_R", "RING_PIP_R", "RING_DIP_R"),
              "LITTLE": ("LITTLE_MCP_R", "LITTLE_PIP_R", "LITTLE_DIP_R")}
GROUP_DIGIT = {"WRIST_R": "wrist"}
for _d, _ch in BONE_CHAIN.items():
    for _b in _ch:
        GROUP_DIGIT[_b] = _d

# ---- allowed deform-group family per R3 digit domain
#      R3 THUMB  : WRIST / CMC / MCP / IP     (INDEX_PIP_R, INDEX_DIP_R strictly forbidden;
#                                               INDEX_MCP_R only under the frozen first-web
#                                               authority, section 7+11 of the round spec)
#      R3 INDEX  : WRIST / INDEX_MCP / INDEX_PIP / INDEX_DIP
ALLOW = {
    "THUMB": ["WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R"],
    "INDEX": ["WRIST_R", "INDEX_MCP_R", "INDEX_PIP_R", "INDEX_DIP_R"],
    "MIDDLE": ["WRIST_R", "MIDDLE_MCP_R", "MIDDLE_PIP_R", "MIDDLE_DIP_R"],
    "RING": ["WRIST_R", "RING_MCP_R", "RING_PIP_R", "RING_DIP_R"],
    "LITTLE": ["WRIST_R", "LITTLE_MCP_R", "LITTLE_PIP_R", "LITTLE_DIP_R"],
    "wrist": ["WRIST_R"],
}

# ------------------------------------------------------------------ defaults
Q_WIDTH_MED = {"W_IP": 5.0, "W_MCP": 5.0, "W_PIP": 5.0, "W_DIP": 5.0, "W_BASE": 3.0}
THUMB_FLEX_SIGN = -1.0
SEVERE_STRETCH_X = 5.0
SEVERE_MIN_BIND_MM = 3.0
TEAR_X = 3.0
TEAR_MIN_POSED_MM = 5.0


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def rr(x, n=9):
    return round(float(x), n)


def jdump(name, obj, where=None):
    p = os.path.join(where or R1E, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    return p


def S(z):
    z = max(0.0, min(1.0, z))
    return z * z * (3.0 - 2.0 * z)


def Q(z):
    z = max(0.0, min(1.0, z))
    return z * z * z * (z * (z * 6.0 - 15.0) + 10.0)


# =====================================================================================
# pose primitives (identical to the Stage6A / Stage6B frozen harness)
# =====================================================================================
def reset_pose(rig):
    from mathutils import Quaternion
    for pb in rig.pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion((1.0, 0.0, 0.0, 0.0))
        pb.location = (0.0, 0.0, 0.0)
        pb.scale = (1.0, 1.0, 1.0)


def set_joint_rotation(rig, bone, angle_deg):
    from mathutils import Quaternion
    pb = rig.pose.bones[bone]
    pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = Quaternion((1.0, 0.0, 0.0), math.radians(angle_deg))


def update():
    bpy.context.view_layer.update()


def evaluate(ob, MW):
    dg = bpy.context.evaluated_depsgraph_get()
    obe = ob.evaluated_get(dg)
    me = obe.data
    return [(MW @ v.co).copy() for v in me.vertices], [tuple(p.vertices) for p in me.polygons]


# =====================================================================================
# object IO
# =====================================================================================
def read_weights(ob, NV):
    W = [dict() for _ in range(NV)]
    for g in ob.vertex_groups:
        for i in range(NV):
            try:
                w = g.weight(i)
            except RuntimeError:
                continue
            if w > 0.0:
                W[i][g.name] = w
    return W


def push_weights(ob, NV, W):
    for vg in list(ob.vertex_groups):
        ob.vertex_groups.remove(vg)
    for g in DEFORM:
        ob.vertex_groups.new(name=g)
    VG = {g.name: g for g in ob.vertex_groups}
    for g in DEFORM:
        for i in range(NV):
            w = W[i].get(g, 0.0)
            if w > 0.0:
                VG[g].add([i], float(w), 'REPLACE')


def vertex_group_stats(W):
    NV = len(W)
    unw = sum(1 for i in range(NV) if not W[i])
    maxinf = max((len(W[i]) for i in range(NV)), default=0)
    nan = sum(1 for i in range(NV) for v in W[i].values() if not math.isfinite(v))
    neg = sum(1 for i in range(NV) for v in W[i].values() if v < 0.0)
    badnorm = sum(1 for i in range(NV)
                  if W[i] and abs(sum(W[i].values()) - 1.0) > 1e-5)
    return {"unweighted_vertices": unw, "max_influences": maxinf, "nan_weights": nan,
            "negative_weights": neg, "non_normalized_vertices": badnorm}


# =====================================================================================
# ARC / POLYLINE
# =====================================================================================
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


# =====================================================================================
# hard 0/1 flip predicate -- round section 20
# =====================================================================================
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


def flip_census(W, edges):
    out = []
    for k, (a, b) in enumerate(edges):
        r = hard_flip(W, a, b)
        if r:
            out.append((k, a, b, r[0], r[1]))
    return out


# =====================================================================================
# geometry metrics
# =====================================================================================
def face_normal(p, poly):
    n = Vector((0.0, 0.0, 0.0))
    for i in range(len(poly)):
        a = p[poly[i]]
        b = p[poly[(i + 1) % len(poly)]]
        n += a.cross(b)
    return n.normalized() if n.length > 1e-18 else Vector((0.0, 0.0, 1.0))


def rings_from(adj, seeds, n):
    seen = set(seeds)
    front = set(seeds)
    dist = dict((v, 0) for v in seeds)
    for d in range(1, n + 1):
        nxt = set()
        for u in front:
            for v in adj.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    dist[v] = d
                    nxt.add(v)
        front = nxt
        if not front:
            break
    return dist
