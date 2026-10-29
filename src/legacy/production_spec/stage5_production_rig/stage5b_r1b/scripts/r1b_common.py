# =====================================================================================
# STAGE5B_R1B -- shared helpers for the narrow THUMB MCP/IP transition weight repair
# =====================================================================================
# READ-ONLY with respect to every existing .blend.  This module
#   * opens the frozen Stage5B R1A master / Stage6A R1 harness to read weights,
#   * rebuilds the R1A semantic regions from the frozen authorities,
#   * defines the deterministic PARAMETRIC local weight field used by the candidate sweep,
#   * evaluates the 6 thumb flex cases and returns the Stage6A metric set.
#
# It never writes weights, geometry, topology, UV or material.
# =====================================================================================
import os
import sys
import json
import math
import hashlib

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # .../production_spec
S5 = os.path.join(PROD, "stage5_production_rig")
S6A = os.path.join(PROD, "stage6_deformation", "stage6a")
if not os.path.isdir(S5) or not os.path.isdir(S6A):
    raise SystemExit("r1b_common: production_spec layout not resolved (PROD=%s)" % PROD)
for _p in (os.path.join(S6A, "scripts"), os.path.join(S5, "stage5b_r1a", "scripts")):
    if _p not in sys.path:
        sys.path.append(_p)

import r1a_common as RC                                          # noqa: E402
import s6a_common as S6                                          # noqa: E402

MM = 1000.0
EPS = 1e-8
MAX_INF = 4

# ---------------------------------------------------------------- frozen inputs (verified)
R1A_MASTER = os.path.join(S5, "stage5b_r1a", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend")
R1A_SHA256 = "c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6"
STAGE6A_R1_HARNESS = os.path.join(S6A, "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend")
STAGE6A_R1_HARNESS_SHA256 = \
    "8f223c979362a8c3414b58e2467c7cda2da60f993245cc95b2a38d76c718d3ef"

# only these groups may be REASSIGNED, and only inside the authorised region
THUMB_FREE_GROUPS = ["WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R"]
ALL_DEFORM = ["WRIST_R"] + ["%s_%s_R" % (d, s) for d in RC.DIGITS for s in RC.CHAIN[d]]
assert len(ALL_DEFORM) == 16

# thumb flexion sign, frozen by the Stage6A R1 sign probe (all five digits = -1)
FLEXION_SIGN_THUMB = -1.0
THUMB_CASES = [("THUMB", "MCP", 15.0), ("THUMB", "MCP", 30.0), ("THUMB", "MCP", 45.0),
               ("THUMB", "IP", 15.0), ("THUMB", "IP", 30.0), ("THUMB", "IP", 45.0)]

# Stage6A R1 measured baseline -- carried forward, must not be lost
R1_BASELINE = {
    "TH_MCP_15": {"min_edge_ratio": 0.465582, "min_face_area_ratio": 0.492276,
                  "face_area_p05": 0.706566, "max_edge_stretch": 1.551121},
    "TH_MCP_30": {"min_edge_ratio": 0.356231, "min_face_area_ratio": 0.324811,
                  "face_area_p05": 0.481305, "max_edge_stretch": 2.078012},
    "TH_MCP_45": {"min_edge_ratio": 0.421283, "min_face_area_ratio": 0.193672,
                  "face_area_p05": 0.523736, "max_edge_stretch": 3.016385},
    "TH_IP_15": {"min_edge_ratio": 0.435307, "min_face_area_ratio": 0.441064,
                 "face_area_p05": 0.634885, "max_edge_stretch": 1.552091},
    "TH_IP_30": {"min_edge_ratio": 0.075150, "min_face_area_ratio": 0.054027,
                 "face_area_p05": 0.322227, "max_edge_stretch": 2.287108},
    "TH_IP_45": {"min_edge_ratio": 0.286202, "min_face_area_ratio": 0.019443,
                 "face_area_p05": 0.436325, "max_edge_stretch": 3.127780},
}

DEFAULT_PARAMS = {
    "form": "centered",       # centered | onesided   (onesided reproduces R1A exactly)
    "W_IP": 1.0,              # IP transition half width, in units of MED
    "W_MCP": 1.0,             # MCP transition half width, in units of MED
    "W_BASE": 1.0,            # base (CMC/WRIST) transition half width, in units of MED
    "shift_IP": 0.0,          # centre offset of the IP ramp, in units of MED
    "shift_MCP": 0.0,         # centre offset of the MCP ramp, in units of MED
    "profile": "smoothstep",  # smoothstep | quintic | cosine
}

# the R1A configuration, expressed in this family: it must reproduce R1A bit-for-bit
R1A_PARAMS = {"form": "onesided", "W_IP": 1.0, "W_MCP": 1.0, "W_BASE": 1.0,
              "shift_IP": 0.0, "shift_MCP": 0.0, "profile": "smoothstep"}

# Stage6A R1 measured intra-thumb self-intersection pair counts (thumb cases only)
R1_INTRA = {"TH_MCP_15": 33, "TH_MCP_30": 49, "TH_MCP_45": 79,
            "TH_IP_15": 13, "TH_IP_30": 35, "TH_IP_45": 51}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rr(x, n=9):
    return round(float(x), n)


# =====================================================================================
# profile functions -- all clamped, monotone, ZERO per-vertex free parameters
# =====================================================================================
def smoothstep(z):
    z = max(0.0, min(1.0, z))
    return z * z * (3.0 - 2.0 * z)


def quintic(z):
    z = max(0.0, min(1.0, z))
    return z * z * z * (z * (z * 6.0 - 15.0) + 10.0)


def cosine(z):
    z = max(0.0, min(1.0, z))
    return 0.5 - 0.5 * math.cos(math.pi * z)


PROFILES = {"smoothstep": smoothstep, "quintic": quintic, "cosine": cosine}


# =====================================================================================
# context -- derived once from the frozen authorities
# =====================================================================================
def build_context():
    ref = RC.load_reference(S5)
    NV = ref["NV"]
    TF = RC.thumb_frame(ref)
    MED = ref["med_edge"]
    R_TT, R_MAX = RC.thumb_radii(ref, TF)
    RG = RC.build_regions(ref, TF, MED, R_TT, R_MAX)
    own_r1a = RG["own_r1a"]
    ARC = TF["arc_thumb_mm"]
    return {
        "ref": ref, "NV": NV, "TF": TF, "MED": MED, "R_TT": R_TT, "R_MAX": R_MAX,
        "RG": RG, "own_r1a": own_r1a, "ARC": ARC,
        "dth": [ref["dchain"][i]["THUMB"] for i in range(NV)],
        "didx": [ref["dchain"][i]["INDEX"] for i in range(NV)],
        "thumb_own": set(i for i in range(NV) if own_r1a[i] == "THUMB"),
        "s_MCP": TF["s_MCP_joint_mm"], "s_IP": TF["s_IP_joint_mm"], "s_TIP": TF["s_TIP_mm"],
        "nail": set(RG["nail_thumb_vertices"]), "cap": set(RG["cap_vertices"]),
        "first_web": set(RG["FIRST_WEB"]),
        "distal": set(RG["THUMB_DISTAL"]), "proximal": set(RG["THUMB_PROXIMAL"]),
        "metacarpal": set(RG["THUMB_FIRST_METACARPAL"]),
        "base_fold": set(RG["THUMB_BASE_FOLD"]), "thenar": set(RG["THENAR_BASE"]),
        "f_tube": RG["f_tube"], "poly": ref["TOPO0"], "edges": ref["EDGES"],
        "FO": ref["FO"], "V0": ref["V0"], "AC": ref["AC"],
    }


def ring_depth(edges, seed, max_depth=8):
    adj = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    depth = dict((i, 0) for i in seed)
    front = set(seed)
    d = 0
    while front and d < max_depth:
        nxt = set()
        for u in front:
            for v in adj.get(u, ()):
                if v not in depth:
                    depth[v] = d + 1
                    nxt.add(v)
        front = nxt
        d += 1
    return depth


def joint_ring_depth(ctx, joint):
    s_j = ctx["s_MCP"] if joint == "MCP" else ctx["s_IP"]
    seeds = [i for i in ctx["thumb_own"] if abs(ctx["ARC"][i] - s_j) <= 0.5 * ctx["MED"]]
    if not seeds:
        seeds = [min(ctx["thumb_own"], key=lambda i: abs(ctx["ARC"][i] - s_j))]
    return ring_depth(ctx["edges"], seeds, max_depth=8)


# =====================================================================================
# the deterministic parametric weight field  (function of the approved arc length only)
# =====================================================================================
def free_weight_field(ctx, params):
    """Deterministic thumb-chain weight field.

    longitudinal coordinate  = APPROVED_JOINT_POLYLINE_ARC_LENGTH  `s` (mm from CMC head)
                    `u`     = IP share
                    `vbase` = base (CMC + WRIST) share
                    `a_mcp` = residual MCP share = 1 - u - vbase  (clamped at 0)

    form "centered"  (candidate family)
        u     = prof(0.5 + (s - s_IP  - shift_IP ) / (2*W_IP ))
        vbase = 1 - prof(0.5 + (s - s_MCP - shift_MCP) / (2*W_BASE))
      -> the ramp STRADDLES the joint: half the blend proximal, half distal.

    form "onesided"  (R1A -- kept only to reproduce the frozen baseline exactly)
        u     = prof((s - s_IP ) / W_IP )
        vbase = 1 - prof((s - s_MCP) / W_BASE)

    There is NO per-vertex free parameter: the whole candidate is (form, W_IP, W_MCP,
    W_BASE, shift_IP, shift_MCP, profile).
    """
    NV = ctx["NV"]
    ARC = ctx["ARC"]
    dth = ctx["dth"]
    s_MCP, s_IP = ctx["s_MCP"], ctx["s_IP"]
    MED = ctx["MED"]
    prof = PROFILES[params["profile"]]
    W_IP = max(1e-6, params["W_IP"] * MED)
    W_MCP = max(1e-6, params["W_MCP"] * MED)
    W_BASE = max(1e-6, params.get("W_BASE", params["W_MCP"]) * MED)
    sh_ip = params.get("shift_IP", 0.0) * MED
    sh_mcp = params.get("shift_MCP", 0.0) * MED
    centered = (params.get("form", "centered") == "centered")
    ft_of = ctx["f_tube"]
    out = [None] * NV
    for i in range(NV):
        s = ARC[i]
        if centered:
            u = prof(0.5 + (s - s_IP - sh_ip) / (2.0 * W_IP))
            vbase = 1.0 - prof(0.5 + (s - s_MCP - sh_mcp) / (2.0 * W_BASE))
        else:
            u = prof((s - s_IP - sh_ip) / W_IP)
            vbase = 1.0 - prof((s - s_MCP - sh_mcp) / W_BASE)
        if u + vbase > 1.0:
            k = 1.0 / (u + vbase)
            u *= k
            vbase *= k
        a_mcp = max(0.0, 1.0 - u - vbase)
        ft = ft_of(dth[i])
        out[i] = {"THUMB_IP_R": u, "THUMB_MCP_R": a_mcp,
                  "THUMB_CMC_R": vbase * ft, "WRIST_R": vbase * (1.0 - ft)}
    _ = W_MCP
    return out


def compose_weights(ctx, W_r1a, auth_region, params):
    """Compose the new 16-group weight vector.  ONLY `auth_region` may change, and inside
    it only the four thumb-chain free groups are reassigned.
    FROZEN (four-finger / index) groups are copied VERBATIM and never rescaled, therefore
    the non-target drift is 0 by construction.
    """
    NV = ctx["NV"]
    field = free_weight_field(ctx, params)
    W2 = [dict(W_r1a[i]) for i in range(NV)]
    FREE = set(THUMB_FREE_GROUPS)
    changed = []
    for i in sorted(auth_region):
        Wi = W_r1a[i]
        frozen = dict((g, w) for g, w in Wi.items() if g not in FREE and w > 0.0)
        F = sum(frozen.values())
        budget = MAX_INF - len(frozen)
        if budget <= 0:
            continue
        free = dict((g, w) for g, w in field[i].items() if w > EPS)
        items = sorted(free.items(), key=lambda kv: -kv[1])
        kept = items[:budget]
        tot = sum(w for _g, w in kept)
        if tot <= 1e-14:
            s = ctx["ARC"][i]
            fb = ("THUMB_IP_R" if s >= ctx["s_IP"]
                  else ("THUMB_MCP_R" if s >= ctx["s_MCP"] else "THUMB_CMC_R"))
            kept = [(fb, 1.0)]
            tot = 1.0
        newv = dict(frozen)
        target = 1.0 - F
        for g, w in kept:
            newv[g] = newv.get(g, 0.0) + (w / tot) * target
        if target > 0.0:
            sf = sum(v for g, v in newv.items() if g not in frozen)
            if sf > 0.0 and abs(sf - target) > 1e-15:
                k = target / sf
                newv = dict((g, (v * k if g not in frozen else v)) for g, v in newv.items())
        newv = dict((g, v) for g, v in newv.items() if v > EPS or g in frozen)
        if newv != Wi:
            changed.append(i)
        W2[i] = newv
    return W2, changed


# =====================================================================================
# object IO
# =====================================================================================
def push_weights_to_object(ob, NV, W):
    for vg in list(ob.vertex_groups):
        ob.vertex_groups.remove(vg)
    for g in ALL_DEFORM:
        ob.vertex_groups.new(name=g)
    VG = {g.name: g for g in ob.vertex_groups}
    for g in ALL_DEFORM:
        idx = [i for i in range(NV) if W[i].get(g, 0.0) > 0.0]
        for i in idx:
            VG[g].add([i], float(W[i][g]), 'REPLACE')


def read_object_weights(ob, NV):
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


def evaluate(ob, MW):
    dg = bpy.context.evaluated_depsgraph_get()
    obe = ob.evaluated_get(dg)
    me = obe.data
    V = [(MW @ v.co).copy() for v in me.vertices]
    P = [tuple(p.vertices) for p in me.polygons]
    return V, P


# =====================================================================================
# geometry metrics -- identical formulation to STAGE6A R1 s6a_run_cases.metrics
# =====================================================================================
def face_area(p, poly):
    n = Vector((0.0, 0.0, 0.0))
    for i in range(len(poly)):
        a = p[poly[i]]
        b = p[poly[(i + 1) % len(poly)]]
        n += a.cross(b)
    return 0.5 * n.length


def face_centroid(p, poly):
    return sum((p[v] for v in poly), Vector()) / len(poly)


def face_normal(p, poly):
    n = Vector((0.0, 0.0, 0.0))
    for i in range(len(poly)):
        a = p[poly[i]]
        b = p[poly[(i + 1) % len(poly)]]
        n += a.cross(b)
    return n.normalized() if n.length > 1e-18 else Vector((0.0, 0.0, 1.0))


def stats(vals):
    v = sorted(vals)
    if not v:
        return {"n": 0}
    return {"n": len(v), "min": v[0], "p05": v[max(0, int(0.05 * len(v)))],
            "median": v[len(v) // 2], "p95": v[min(len(v) - 1, int(0.95 * len(v)))],
            "max": v[-1], "mean": sum(v) / len(v)}


def intersect_pairs(V, P):
    tree = BVHTree.FromPolygons([tuple(v) for v in V], [tuple(p) for p in P],
                                all_triangles=False, epsilon=0.0)
    raw = tree.overlap(tree)
    out = set()
    for a, b in raw:
        if a >= b:
            continue
        if set(P[a]) & set(P[b]):
            continue
        out.add((a, b))
    return out


def intersect_pairs_subset(V, P, face_ids):
    """Same predicate as intersect_pairs, but restricted to `face_ids` (a sub-mesh).

    A pair of faces can only be reported when those two faces actually overlap, therefore
    restricting the BVH to a face subset yields exactly the same pairs among that subset as
    the full-mesh query.  Returns pairs of REAL face indices.
    """
    sub = [tuple(P[i]) for i in face_ids]
    tree = BVHTree.FromPolygons([tuple(v) for v in V], sub, all_triangles=False, epsilon=0.0)
    raw = tree.overlap(tree)
    out = set()
    for a, b in raw:
        if a >= b:
            continue
        if set(sub[a]) & set(sub[b]):
            continue
        out.add((face_ids[a], face_ids[b]))
    return out
