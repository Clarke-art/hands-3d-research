# =====================================================================================
# STAGE6A -- shared helpers for the deterministic deformation harness
# =====================================================================================
# READ-ONLY with respect to the Stage5B master: this module only opens the frozen
# Stage5B R1B CANDIDATE blend (and the frozen Stage5A R2A master for reference geometry)
# and poses bones.  It never writes weights / geometry / topology.
# STAGE6A_R1A copy: the only difference from the Stage6A R1 module is the input master.
# =====================================================================================
import os
import sys
import math
import json

import bpy
from mathutils import Vector, Quaternion, Matrix

MM = 1000.0

# ---------------------------------------------------------------- frozen identifiers
STAGE5B_MASTER = "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend"
STAGE5B_MASTER_SHA = "cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10"

DIGITS = ["INDEX", "MIDDLE", "RING", "LITTLE", "THUMB"]
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"],
         "LITTLE": ["MCP", "PIP", "DIP"]}
DD = {"THUMB": "thumb", "INDEX": "index", "MIDDLE": "middle", "RING": "ring",
      "LITTLE": "little"}
DEFORM = ["WRIST_R"] + ["%s_%s_R" % (d, s) for d in DIGITS for s in CHAIN[d]]
TIPBONE = {d: "%s_TIP_R" % d for d in DIGITS}

# the 14 isolated deform joints of Stage6A (CMC and WRIST stay LOCKED)
TEST_JOINTS = [("INDEX", "MCP"), ("INDEX", "PIP"), ("INDEX", "DIP"),
               ("MIDDLE", "MCP"), ("MIDDLE", "PIP"), ("MIDDLE", "DIP"),
               ("RING", "MCP"), ("RING", "PIP"), ("RING", "DIP"),
               ("LITTLE", "MCP"), ("LITTLE", "PIP"), ("LITTLE", "DIP"),
               ("THUMB", "MCP"), ("THUMB", "IP")]
TEST_ANGLES = [15.0, 30.0, 45.0]
PROBE_ANGLE = 5.0
LOCKED_BONES = ["WRIST_R", "THUMB_CMC_R"]


def log_factory(tag):
    out = []

    def log(*a):
        s = " ".join(str(x) for x in a)
        out.append(s)
        print("[%s]" % tag, s, flush=True)
    return log, out


# ---------------------------------------------------------------- pose helpers
def reset_pose(rig):
    for pb in rig.pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion((1.0, 0.0, 0.0, 0.0))
        pb.location = (0.0, 0.0, 0.0)
        pb.scale = (1.0, 1.0, 1.0)


def set_joint_rotation(rig, bone, angle_deg):
    """rotation about the bone LOCAL X axis (Stage5A frozen flexion axis)"""
    pb = rig.pose.bones[bone]
    pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = Quaternion((1.0, 0.0, 0.0), math.radians(angle_deg))


def pose_state(rig):
    st = {}
    for pb in rig.pose.bones:
        q = pb.rotation_quaternion
        st[pb.name] = {"quat": [round(q.w, 12), round(q.x, 12), round(q.y, 12), round(q.z, 12)],
                       "loc": [round(v, 12) for v in pb.location],
                       "scale": [round(v, 12) for v in pb.scale]}
    return st


def evaluate(ob, MW):
    dg = bpy.context.evaluated_depsgraph_get()
    obe = ob.evaluated_get(dg)
    me = obe.data
    V = [(MW @ v.co).copy() for v in me.vertices]
    P = [tuple(p.vertices) for p in me.polygons]
    return V, P


def bone_world(rig, name, head=True):
    b = rig.data.bones[name]
    return rig.matrix_world @ (b.head_local if head else b.tail_local)


# ---------------------------------------------------------------- geometry metrics
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


def rr(x, n=9):
    return round(float(x), n)


# ---------------------------------------------------------------- reference / harness
def add_r1a_path():
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.abspath(os.path.join(here, "..", "..", "..", "stage5_production_rig",
                                     "stage5b_r1a", "scripts"))
    if p not in sys.path:
        sys.path.append(p)
    return p


def load_reference(top_prod):
    """frozen Stage5A R2A reference geometry (V0 / chains / ownership / nail / cap)."""
    add_r1a_path()
    import r1a_common as C
    return C, C.load_reference(top_prod)


def open_harness(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = bpy.data.objects["Hand  - Realistic"]
    rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
    me = ob.data
    MW = ob.matrix_world.copy()
    NV = len(me.vertices)
    V = [(MW @ v.co).copy() for v in me.vertices]
    groups = sorted(g.name for g in ob.vertex_groups)
    W = [dict() for _ in range(NV)]
    for g in ob.vertex_groups:
        for i in range(NV):
            try:
                w = g.weight(i)
            except RuntimeError:
                continue
            if w > 0.0:
                W[i][g.name] = w
    EDGES = [(e.vertices[0], e.vertices[1]) for e in me.edges]
    POLY = [tuple(p.vertices) for p in me.polygons]
    MAT = [p.material_index for p in me.polygons]
    UV = ([tuple(round(u, 9) for u in d.uv) for d in me.uv_layers.active.data]
          if me.uv_layers.active else [])
    return {"ob": ob, "rig": rig, "me": me, "MW": MW, "NV": NV, "V": V, "groups": groups,
            "W": W, "EDGES": EDGES, "POLY": POLY, "MAT": MAT, "UV": UV,
            "E": len(me.edges), "F": len(me.polygons),
            "TRIS": sum(len(p.vertices) - 2 for p in me.polygons),
            "parent": ob.parent.name if ob.parent else None,
            "mods": [(m.name, m.type, (m.object.name if getattr(m, "object", None) else None))
                     for m in ob.modifiers]}
