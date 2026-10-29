# =====================================================================================
# STAGE6B_R1A -- shared helpers for the THUMB|INDEX seam topology provenance audit
# =====================================================================================
# READ-ONLY FORENSIC ROUND.  This module
#   * pins every frozen blend it reads and never writes one,
#   * loads an arbitrary historical .blend and extracts plain-python mesh state
#     (a .blend can only be opened one at a time: open_mainfile invalidates RNA refs),
#   * matches edges between stages GEOMETRICALLY (midpoint + length + direction) because
#     edge / vertex indices are NOT stable across the retopo history,
#   * provides the anatomical locators used to classify the 67 THUMB|INDEX seam edges.
#
# No geometry / topology / weight / bone / semantic change is ever made by this file.
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
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))          # .../production_spec
WORKSPACE = os.path.abspath(os.path.join(PROD, ".."))                 # .../hands

S6D = os.path.join(PROD, "stage6_deformation")
S6B = os.path.join(S6D, "stage6b")
S6B_R1A = os.path.join(S6D, "stage6b_r1a_seam_provenance")
S5 = os.path.join(PROD, "stage5_production_rig")
S4 = os.path.join(PROD, "stage4_blender")
S2 = os.path.join(PROD, "stage2_bootstrap")

for _p in (os.path.join(S6B, "scripts"), os.path.join(S5, "stage5b_r1b", "scripts"),
           os.path.join(S5, "stage5b_r1a", "scripts"), os.path.join(S6D, "stage6a", "scripts")):
    if _p not in sys.path:
        sys.path.append(_p)

import s6b_common as B                                              # noqa: E402
import r1a_common as RC                                             # noqa: E402

MM = 1000.0
EPS = 1e-8

# ---------------------------------------------------------------- frozen inputs
R1B_MASTER = os.path.join(S5, "stage5b_r1b", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend")
R1B_SHA256 = "cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10"
R1A_HARNESS = os.path.join(S6D, "stage6a_r1a",
                           "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend")
R1A_HARNESS_SHA256 = "c4bb74ea116e7352064c26977a509ed1248aacbe734118e5f9c240fa24b1157b"
S5A_MASTER = os.path.join(S5, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
S5A_SHA256 = "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"
S6B_HARNESS = os.path.join(S6B, "RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1.blend")
S6B_HARNESS_SHA256 = "4b6200899fe4d2f5a67e3254aec2a5cb17b734b14acefe381a2ac9c1241f549d"

# ---------------------------------------------------------------- lineage (oldest -> newest)
# every entry is read-only; the CMC surgery happened at Stage4A R2.
LINEAGE = [
    ("S0_CC0_SOURCE_BUNDLE",
     os.path.join(WORKSPACE, "references", "licenses", "blender_human_base_meshes", "extracted",
                  "human-base-meshes-bundle-v1.4.1", "human_base_meshes_bundle.blend"),
     "CC0 Blender Human Base Meshes v1.4.1 multi-object bundle"),
    ("S2_BOOTSTRAP_C1", os.path.join(S2, "RIGHT_HAND_BOOTSTRAP_C1.blend"),
     "Route C geometry bootstrap (right hand extracted)"),
    ("S4A_CANDIDATE", os.path.join(S4, "RIGHT_HAND_ENGINEERING_CANDIDATE_STAGE4A.blend"),
     "Stage4A engineering candidate (pre-CMC-surgery reference)"),
    ("S4A_RAW", os.path.join(S4, "RIGHT_HAND_ENGINEERING_STAGE4A.blend"),
     "Stage4A raw engineering mesh"),
    ("S4A_CMC_R1", os.path.join(S4, "RIGHT_HAND_ENGINEERING_STAGE4A_CMC_R1.blend"),
     "Stage4A CMC local retopo R1"),
    ("S4A_R2_BASE", os.path.join(S4, "RIGHT_HAND_ENGINEERING_STAGE4A_R2_BASE.blend"),
     "Stage4A R2 pre-surgery base"),
    ("S4A_R2", os.path.join(S4, "stage4a_r2", "RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend"),
     "Stage4A R2 (APPROVED CMC local retopo)"),
    ("S4B_RSSF_R1", os.path.join(S4, "stage4b_rssf", "RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R1.blend"),
     "Stage4B RSSF re-pose R1"),
    ("S4B_RSSF_R2", os.path.join(S4, "stage4b_rssf", "RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R2.blend"),
     "Stage4B RSSF re-pose R2"),
    ("S4C_R1", os.path.join(S4, "stage4c", "RIGHT_HAND_ENGINEERING_STAGE4C_R1.blend"),
     "Stage4C R1"),
    ("S4C_R2", os.path.join(S4, "stage4c_r2", "RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend"),
     "Stage4C R2 (approved engineering master)"),
    ("S5A_R1", os.path.join(S5, "stage5a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R1.blend"),
     "Stage5A production rig R1"),
    ("S5A_R2", os.path.join(S5, "stage5a_r2", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2.blend"),
     "Stage5A production rig R2"),
    ("S5A_R2A", S5A_MASTER, "Stage5A production rig R2A (FINAL_APPROVED skeleton)"),
    ("S5B_R1", os.path.join(S5, "stage5b_r1", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend"),
     "Stage5B initial skin R1"),
    ("S5B_R1A", os.path.join(S5, "stage5b_r1a", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend"),
     "Stage5B initial skin R1A (superseded for thumb weighting)"),
    ("S5B_R1B", R1B_MASTER, "Stage5B R1B (ACTIVE production skin master)"),
]

MESH_OBJ = "Hand  - Realistic"


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
# generic read-only blend loader
# =====================================================================================
def pick_mesh_object(prefer=MESH_OBJ):
    """the mesh object to audit: the named production mesh if present, else the mesh with
    the most vertices (the source bundle has 407 objects)."""
    if prefer in bpy.data.objects and bpy.data.objects[prefer].type == 'MESH':
        return bpy.data.objects[prefer]
    best = None
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        if best is None or len(ob.data.vertices) > len(best.data.vertices):
            best = ob
    return best


def load_mesh_state(path, prefer=MESH_OBJ, want_uv=False):
    """open `path` read-only and extract plain-python mesh state.  No write of any kind."""
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = pick_mesh_object(prefer)
    if ob is None:
        return None
    me = ob.data
    MW = ob.matrix_world.copy()
    NV = len(me.vertices)
    V = [(MW @ v.co).copy() for v in me.vertices]
    L = [v.co.copy() for v in me.vertices]
    EDGES = [(e.vertices[0], e.vertices[1]) for e in me.edges]
    TOPO = [tuple(p.vertices) for p in me.polygons]
    MAT = [p.material_index for p in me.polygons]
    ntri = sum(len(p.vertices) - 2 for p in me.polygons)
    elen = sorted((V[a] - V[b]).length * MM for a, b in EDGES)
    uv = None
    if want_uv and me.uv_layers.active:
        uv = [tuple(round(u, 9) for u in d.uv) for d in me.uv_layers.active.data]
    return {
        "blend": path, "obj_name": ob.name, "NV": NV, "NE": len(me.edges),
        "NF": len(me.polygons), "NTRIS": ntri,
        "V": V, "L": L, "EDGES": EDGES, "TOPO": TOPO, "MAT": MAT, "UV": uv,
        "MW": MW, "med_edge_mm": (elen[len(elen) // 2] if elen else 0.0),
        "materials": [m.name if m else None for m in me.materials],
        "vertex_groups": sorted(g.name for g in ob.vertex_groups),
        "parent": (ob.parent.name if ob.parent else None),
        "modifiers": [(m.name, m.type) for m in ob.modifiers],
        "bbox_min": v3(Vector((min(v[i] for v in V) for i in range(3))), 9),
        "bbox_max": v3(Vector((max(v[i] for v in V) for i in range(3))), 9),
        "topo_sig": [NV, len(me.edges), len(me.polygons), ntri],
        "ngons": sum(1 for p in me.polygons if len(p.vertices) > 4),
        "tris": sum(1 for p in me.polygons if len(p.vertices) == 3),
        "quads": sum(1 for p in me.polygons if len(p.vertices) == 4),
        "is_closed": (NV - len(me.edges) + len(me.polygons) == 2),
    }


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


# =====================================================================================
# geometric edge matching (ids are NOT stable across the retopo history)
# =====================================================================================
class EdgeIndex(object):
    """spatial index over a mesh's edges, keyed by midpoint."""

    def __init__(self, V, EDGES):
        self.V = V
        self.EDGES = EDGES
        self.mid = [((V[a] + V[b]) * 0.5) for a, b in EDGES]
        self.len_mm = [(V[a] - V[b]).length * MM for a, b in EDGES]
        self.cell = 2.0 / MM                         # 2 mm grid
        self.grid = {}
        for k, m in enumerate(self.mid):
            key = (int(math.floor(m.x / self.cell)), int(math.floor(m.y / self.cell)),
                   int(math.floor(m.z / self.cell)))
            self.grid.setdefault(key, []).append(k)

    def _ring(self, cell_xyz):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    yield (cell_xyz[0] + dx, cell_xyz[1] + dy, cell_xyz[2] + dz)

    def nearest(self, p, max_mm=1.0):
        """nearest edge by midpoint distance; returns (edge_index, midpoint_dist_mm)."""
        c = (int(math.floor(p.x / self.cell)), int(math.floor(p.y / self.cell)),
             int(math.floor(p.z / self.cell)))
        best, bd = None, 1e18
        for key in self._ring(c):
            for k in self.grid.get(key, ()):
                d = (self.mid[k] - p).length * MM
                if d < bd:
                    bd, best = d, k
        if best is None or bd > max_mm:
            return None, (bd if best is not None else None)
        return best, bd


def match_edge(idx, pa, pb, tol_mm=0.05):
    """match an edge (pa,pb) in a historical mesh: nearest midpoint within tol AND matching
    length AND both endpoints present.  Returns dict with evidence."""
    mid = (pa + pb) * 0.5
    k, dmid = idx.nearest(mid, max_mm=max(2.0, tol_mm * 20))
    if k is None:
        return {"matched": False, "reason": "no edge within search radius"}
    a, b = idx.EDGES[k]
    ha, hb = idx.V[a], idx.V[b]
    # endpoint correspondence (either orientation)
    d_direct = max((ha - pa).length, (hb - pb).length) * MM
    d_swap = max((ha - pb).length, (hb - pa).length) * MM
    dend = min(d_direct, d_swap)
    ratio = idx.len_mm[k] / max(1e-9, (pa - pb).length * MM)
    ok = (dmid <= tol_mm * 20) and (dend <= tol_mm * 20) and (0.98 <= ratio <= 1.02)
    return {"matched": bool(ok), "edge_index": k, "midpoint_dist_mm": rr(dmid, 6),
            "endpoint_max_dist_mm": rr(dend, 6), "length_ratio": rr(ratio, 6),
            "endpoint_ids": [a, b],
            "reason": "ok" if ok else "geometry does not correspond"}


# =====================================================================================
# anatomical locators
# =====================================================================================
ANAT_BONES = ["THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R", "THUMB_TIP_R",
              "INDEX_MCP_R", "INDEX_PIP_R", "INDEX_DIP_R", "INDEX_TIP_R"]


def bone_segments(jf):
    """world head/tail for the anatomical locator bones.  TIP helper bones are included as
    point locators (head == tail)."""
    segs = {}
    for n in ANAT_BONES:
        if n in jf:
            h, t = Vector(jf[n]["head"]), Vector(jf[n]["tail"])
            segs[n] = (h, t)
    if "WRIST_R" in jf:
        segs["WRIST_R"] = (Vector(jf["WRIST_R"]["head"]), Vector(jf["WRIST_R"]["tail"]))
    return segs


def seg_dist(p, a, b):
    ab = b - a
    if ab.length_squared < 1e-18:
        return (p - a).length, 0.0
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
    return (p - (a + ab * t)).length, t


def anat_locate(p, segs):
    """distance (mm) to every locator bone + the nearest one."""
    out = {}
    for n, (h, t) in segs.items():
        d, _u = seg_dist(p, h, t)
        out[n] = rr(d * MM, 6)
    nearest = min(out.items(), key=lambda kv: kv[1])
    return out, nearest[0], nearest[1]


def thumb_arc(p, thumb_pts):
    """APPROVED_JOINT_POLYLINE_ARC_LENGTH for the thumb (mm from CMC head)."""
    return RC.arc_of(thumb_pts, p)


def index_arc(p, index_pts):
    return RC.arc_of(index_pts, p)


# =====================================================================================
# topology forensics for a single edge
# =====================================================================================
def build_edge_face_map(TOPO):
    ef = {}
    for fi, vs in enumerate(TOPO):
        n = len(vs)
        for i in range(n):
            a, b = vs[i], vs[(i + 1) % n]
            ef.setdefault(tuple(sorted((a, b))), []).append(fi)
    return ef


def edge_dihedral(face_normals, faces):
    if len(faces) != 2:
        return None
    n0, n1 = face_normals[faces[0]], face_normals[faces[1]]
    c = max(-1.0, min(1.0, n0.dot(n1)))
    return math.degrees(math.acos(c))


def face_normals_of(V, TOPO):
    out = []
    for p in TOPO:
        n = Vector((0.0, 0.0, 0.0))
        for i in range(len(p)):
            a = V[p[i]]
            b = V[p[(i + 1) % len(p)]]
            n += a.cross(b)
        out.append(n.normalized() if n.length > 1e-18 else Vector((0.0, 0.0, 1.0)))
    return out


def coincident_vertices(V, ids, tol_mm=0.02):
    """count near-coincident vertex pairs among `ids` (duplicate / weld forensics)."""
    found = []
    ids = list(ids)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            if (V[ids[i]] - V[ids[j]]).length * MM <= tol_mm:
                found.append([ids[i], ids[j]])
    return found


def connected_face_component(TOPO, seed_face, allowed=None):
    """flood-fill the face sheet through shared edges; returns the component as a set."""
    ef = {}
    for fi, vs in enumerate(TOPO):
        if allowed is not None and fi not in allowed:
            continue
        n = len(vs)
        for i in range(n):
            a, b = vs[i], vs[(i + 1) % n]
            ef.setdefault(tuple(sorted((a, b))), []).append(fi)
    seen = set([seed_face])
    front = [seed_face]
    while front:
        f = front.pop()
        vs = TOPO[f]
        n = len(vs)
        for i in range(n):
            a, b = vs[i], vs[(i + 1) % n]
            for g in ef.get(tuple(sorted((a, b))), ()):
                if g not in seen:
                    seen.add(g)
                    front.append(g)
    return seen
