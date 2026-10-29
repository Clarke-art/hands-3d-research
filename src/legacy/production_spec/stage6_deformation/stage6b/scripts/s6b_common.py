# =====================================================================================
# STAGE6B -- shared authorities for the thumb opposition / combined deformation validation
# =====================================================================================
# READ-ONLY with respect to every frozen blend.  This module
#   * pins the frozen inputs (Stage5A R2A / Stage5B R1B / Stage6A R1A harness),
#   * defines the canonical world direction set used by the opposition diagnostics,
#   * derives the CMC cage deformation patch from the approved Stage4A R2 confinement,
#   * derives the thenar / first-web / nail / distal-cap semantic sets,
#   * provides the deterministic local rotation-vector -> quaternion pose primitives,
#   * provides the metric families shared by the 9 formal cases.
#
# No weight / geometry / topology / bone / parent / modifier change is ever made.
# =====================================================================================
import os
import sys
import json
import math
import hashlib

import bpy
from mathutils import Vector, Quaternion, Matrix
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S5 = os.path.join(PROD, "stage5_production_rig")
S6D = os.path.join(PROD, "stage6_deformation")
S6A = os.path.join(S6D, "stage6a")
S6A_R1A = os.path.join(S6D, "stage6a_r1a")
S6B = os.path.join(S6D, "stage6b")
for _p in (os.path.join(S5, "stage5b_r1b", "scripts"), os.path.join(S6A, "scripts"),
           os.path.join(S5, "stage5b_r1a", "scripts")):
    if _p not in sys.path:
        sys.path.append(_p)

import r1a_common as RC                                          # noqa: E402
import r1b_common as RB                                          # noqa: E402
import s6a_common as S6                                          # noqa: E402

MM = 1000.0
EPS = 1e-8

# ---------------------------------------------------------------- frozen inputs
R1B_MASTER = os.path.join(S5, "stage5b_r1b", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend")
R1B_SHA256 = "cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10"
R1A_HARNESS = os.path.join(S6A_R1A, "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend")
R1A_HARNESS_SHA256 = "c4bb74ea116e7352064c26977a509ed1248aacbe734118e5f9c240fa24b1157b"
S5A_MASTER = os.path.join(S5, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
S5A_SHA256 = "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"
STAGE4A_CMC_R2_AUDIT = os.path.join(PROD, "stage4_blender", "stage4a_r2",
                                    "CMC_LOCAL_RETOPO_AUDIT_R2.json")

HARNESS_R1 = os.path.join(S6B, "RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1.blend")

# ---------------------------------------------------------------- canonical world frame
# +X = RADIAL    +Y = DORSAL    +Z = DISTAL      (right hand)
RADIAL = Vector((1.0, 0.0, 0.0))
DORSAL = Vector((0.0, 1.0, 0.0))
DISTAL = Vector((0.0, 0.0, 1.0))
ULNAR = -RADIAL                       # -X
PALMAR = -DORSAL                      # -Y
T_OPPOSE = (ULNAR + PALMAR).normalized()      # diagnostic across-palm opposition direction

# frozen Stage6A flexion authority
FLEXION_SIGN = {"THUMB_MCP": -1.0, "THUMB_IP": -1.0}
LOCKED_BONES = ["WRIST_R", "THUMB_MCP_R_FROZEN_SENTINEL"]   # wrist really locked; sentinel unused

# Stage6B diagnostic levels (stress-test parameters, NOT teaching values, NOT human ROM)
CMC_OPP_ANGLES = [10.0, 20.0, 30.0]
FULL_CHAIN_IP = [5.0, 10.0, 15.0]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def rr(x, n=9):
    return round(float(x), n)


def v3(v, n=9):
    return [rr(x, n) for x in v]


# =====================================================================================
# context
# =====================================================================================
def build_context():
    ctx = RB.build_context()
    ref = ctx["ref"]
    NV = ctx["NV"]

    # ---- CMC cage deformation patch, derived from the approved Stage4A R2 surgery
    a4 = json.load(open(STAGE4A_CMC_R2_AUDIT, encoding="utf-8"))
    cmc_centre = Vector(a4["cmc"]["world"])
    fm_axis = Vector(a4["cmc"]["first_metacarpal_axis"]).normalized()
    confinement_mm = max(a4["vertex_diff"]["max_dist_from_cmc_of_added_mm"],
                         a4["vertex_diff"]["max_dist_from_cmc_of_removed_mm"])
    dcmc = [(ref["V0"][i] - cmc_centre).length * MM for i in range(NV)]
    cage_patch = sorted(i for i in range(NV)
                        if dcmc[i] <= confinement_mm
                        and ctx["own_r1a"][i] in ("THUMB", "wrist"))
    # ring-locality cross-check (approved ring axial spans)
    ring_spans = [r["axial_span_mm"] for r in a4["cage_ring_locality"]]

    ctx.update({
        "cmc_centre": cmc_centre,
        "first_metacarpal_axis": fm_axis,
        "cmc_confinement_mm": confinement_mm,
        "cmc_cage_patch": cage_patch,
        "cmc_cage_audit": {
            "authority": "stage4_blender/stage4a_r2/CMC_LOCAL_RETOPO_AUDIT_R2.json",
            "T04_CMC_definition": a4["T04_CMC"]["definition"],
            "FINAL_CMC_DEFORMATION_AUTHORITY": a4["VERDICT"]["FINAL_CMC_DEFORMATION_AUTHORITY"],
            "confined_radius_mm": confinement_mm,
            "concentric_rings_total": a4["cage"]["concentric_rings_total"],
            "spokes": a4["cage"]["spokes"], "cage_quads": 64,
            "ring_axial_spans_mm": ring_spans,
            "pole_vertex": a4["cmc_pole_audit"]["vertex"],
            "cmc_pole_audit_vertex": a4["cmc"]["vertex"],
            "derivation": ("vertices whose distance to the approved CMC rotation centre is "
                           "within the R2 surgery confinement radius, restricted to "
                           "thumb/wrist ownership"),
        },
        "thenar": set(ctx["RG"]["THENAR_BASE"]),
        "metacarpal": set(ctx["RG"]["THUMB_FIRST_METACARPAL"]),
        "first_web": set(ctx["RG"]["FIRST_WEB"]),
        "nail_thumb": set(ctx["RG"]["nail_thumb_vertices"]),
        "distal_cap": set(ctx["RG"]["cap_vertices"]),
        "thumb_own": set(ctx["thumb_own"]),
    })
    return ctx


def web_boundary(ctx):
    """the first-web dynamic test uses the APPROVED static mask; we take its topological
    boundary (edges with exactly one endpoint in the mask) as the observable boundary loop."""
    web = ctx["first_web"]
    edges = set()
    for a, b in ctx["edges"]:
        if (a in web) != (b in web):
            edges.add(tuple(sorted((a, b))))
    verts = set()
    for a, b in edges:
        verts.add(a)
        verts.add(b)
    return sorted(verts), sorted(edges)


# =====================================================================================
# pose primitives
# =====================================================================================
def reset_pose(rig):
    S6.reset_pose(rig)


def set_local_axis_rotation(rig, bone, angle_deg, axis=(1.0, 0.0, 0.0)):
    pb = rig.pose.bones[bone]
    pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = Quaternion(Vector(axis).normalized(), math.radians(angle_deg))


def rotation_vector_to_quaternion(rv):
    """exponential map: local rotation vector (radians) -> unit quaternion"""
    v = Vector(rv)
    mag = v.length
    if mag < 1e-12:
        return Quaternion((1.0, 0.0, 0.0, 0.0)), 0.0
    return Quaternion(v.normalized(), mag), mag


def set_local_rotation_vector(rig, bone, rv):
    q, mag = rotation_vector_to_quaternion(rv)
    pb = rig.pose.bones[bone]
    pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = q
    return q, mag


def evaluate(ob, MW):
    return S6.evaluate(ob, MW)


def tip_world(rig, name="THUMB_TIP_R"):
    return rig.matrix_world @ rig.pose.bones[name].head


def update():
    bpy.context.view_layer.update()


# =====================================================================================
# geometry metrics
# =====================================================================================
def face_area(p, poly):
    return S6.face_area(p, poly)


def face_normal(p, poly):
    return S6.face_normal(p, poly)


def face_centroid(p, poly):
    return S6.face_centroid(p, poly)


def stats(vals):
    return S6.stats(vals)


def intersect_pairs(V, P):
    return RB.intersect_pairs(V, P)


def intersect_pairs_subset(V, P, faces):
    return RB.intersect_pairs_subset(V, P, faces)


def region_faces(poly, ids):
    s = set(ids)
    return [fi for fi, p in enumerate(poly) if any(v in s for v in p)]


def region_edges(edges, ids):
    s = set(ids)
    return [k for k, (a, b) in enumerate(edges) if a in s or b in s]


def strain_block(V, V0, poly, edges, face_area0, edge_len0, faces, eids):
    pr = []
    for fi in faces:
        a0 = face_area0[fi]
        pr.append((face_area(V, poly[fi]) / a0) if a0 > 1e-18 else 0.0)
    pe = []
    for k in eids:
        a, b = edges[k]
        l0 = edge_len0[k]
        pe.append(((V[a] - V[b]).length / l0) if l0 > 1e-18 else 0.0)
    surf = (sum(face_area(V, poly[fi]) for fi in faces)
            / max(1e-18, sum(face_area0[fi] for fi in faces)))
    return {
        "min_face_area_ratio": rr(min(pr), 6) if pr else None,
        "face_area_ratio": {k: (rr(v, 6) if isinstance(v, float) else v)
                            for k, v in stats(pr).items()} if pr else {"n": 0},
        "min_edge_ratio": rr(min(pe), 6) if pe else None,
        "max_edge_ratio": rr(max(pe), 6) if pe else None,
        "edge_ratio": {k: (rr(v, 6) if isinstance(v, float) else v)
                       for k, v in stats(pe).items()} if pe else {"n": 0},
        "local_surface_area_ratio": rr(surf, 6),
        "face_count": len(faces), "edge_count": len(eids),
    }


def nail_normal(V, poly, nail_faces):
    """area-weighted mean normal of the approved thumb nail faces"""
    n = Vector((0.0, 0.0, 0.0))
    for fi in nail_faces:
        n += face_normal(V, poly[fi]) * face_area(V, poly[fi])
    return n.normalized() if n.length > 1e-18 else Vector((0.0, 0.0, 1.0))
