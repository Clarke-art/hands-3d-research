# STAGE5A -- authoritative joint-region validation geometry (ownership based).
# Read-only.  Ownership rule = the SAME rule the approved Stage-4C R2 nail selector uses:
# assign a face to the digit whose FULL bone chain (meta+prox+distal) is nearest.
import bpy, sys, os, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:]
MASTER, OUT = argv[0], argv[1]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
MM = 1000.0
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
t01 = json.load(open(os.path.join(S4, "stage4a_t01", "T01_FINAL_AUDIT.json"), encoding="utf-8"))

bpy.ops.wm.open_mainfile(filepath=MASTER)
ob = bpy.data.objects["Hand  - Realistic"]
me = ob.data
MW = ob.matrix_world
W = [(MW @ v.co).copy() for v in me.vertices]

CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"],
         "LITTLE": ["MCP", "PIP", "DIP"]}
R_ENV = {"THUMB": 11.14, "INDEX": 7.64, "MIDDLE": 7.80, "RING": 7.15, "LITTLE": 6.75}
ORDER = ["WRIST_R"]
for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    ORDER += ["%s_%s_R" % (D, s) for s in CHAIN[D]] + ["%s_TIP_R" % D]


def chains():
    out = {}
    for D, segs in CHAIN.items():
        pts = [Vector(jf["%s_%s_R" % (D, segs[0])]["head"])]
        for s in segs:
            pts.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
        out[D] = pts
    return out


CH = chains()
WRIST_PTS = [Vector(jf["WRIST_R"]["head"]), Vector(jf["WRIST_R"]["tail"])]


def d_poly(p, poly):
    best = 1e9
    for i in range(len(poly) - 1):
        a, b = poly[i], poly[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
        best = min(best, (p - (a + ab * t)).length)
    return best


# ---- face ownership -----------------------------------------------------------------
owner = {}
for p in me.polygons:
    c = sum((W[v] for v in p.vertices), Vector()) / len(p.vertices)
    dd = {D: d_poly(c, CH[D]) for D in CH}
    dd["wrist"] = d_poly(c, WRIST_PTS)
    owner[p.index] = min(dd, key=dd.get)

DIGIT_FACES = {D: [fi for fi, o in owner.items() if o == D] for D in CH}
DIGIT_FACES["wrist"] = [fi for fi, o in owner.items() if o == "wrist"]

BVH = {}
for D, faces in DIGIT_FACES.items():
    if not faces:
        continue
    vs = sorted({v for fi in faces for v in me.polygons[fi].vertices})
    idx = {v: i for i, v in enumerate(vs)}
    verts = [W[v] for v in vs]
    polys = [tuple(idx[v] for v in me.polygons[fi].vertices) for fi in faces]
    BVH[D] = {"bvh": BVHTree.FromPolygons(verts, polys, all_triangles=False),
              "faces": faces, "n_faces": len(faces), "n_verts": len(vs)}


def local(p, D):
    b = BVH[D]
    loc, nor, fi, dist = b["bvh"].find_nearest(p, 0.3)
    if loc is None:
        return {"found": False}
    ofi = b["faces"][fi]
    n = (MW.to_3x3() @ me.polygons[ofi].normal).normalized()
    off = (p - loc).dot(n)
    return {"found": True, "dist_mm": round((p - loc).length * MM, 4),
            "signed_mm": round(off * MM, 4), "inside": bool(off < 0), "nearest_face": ofi}


DIGIT_OF = {"WRIST_R": "wrist", "THUMB_CMC_R": "THUMB", "THUMB_MCP_R": "THUMB",
            "THUMB_IP_R": "THUMB", "THUMB_TIP_R": "THUMB"}
for D in ("INDEX", "MIDDLE", "RING", "LITTLE"):
    for s in ("MCP", "PIP", "DIP", "TIP"):
        DIGIT_OF["%s_%s_R" % (D, s)] = D

rep = {"face_ownership_counts": {D: len(DIGIT_FACES[D]) for D in DIGIT_FACES},
       "total_faces": len(me.polygons)}
joints = {}
for n in ORDER:
    D = DIGIT_OF[n]
    p = Vector(jf[n]["head"])
    e = {"joint": n, "world": [round(float(x), 6) for x in p], "digit": D}
    lis = local(p, D)
    e["digit_local_surface"] = lis
    e["dist_to_own_chain_mm"] = round(d_poly(p, CH[D]) * MM, 4) if D in CH else None
    e["digit_local_radius_mm"] = R_ENV.get(D)
    if D in CH:
        # axial fraction of the digit from the proximal joint
        prox = Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])
        dist = Vector(jf["%s_TIP_R" % D]["head"])
        ax = (dist - prox).normalized()
        e["axial_from_proximal_mm"] = round((p - prox).dot(ax) * MM, 4)
        e["axial_total_mm"] = round((dist - prox).dot(ax) * MM, 4)
    joints[n] = e
rep["joints"] = joints

# T-01 approved axial levels (fingers): axial measured from the web commissure (MCP level)
T01_GROUPS = dict(t01.get("T01_MCP", {})); T01_GROUPS.update(t01.get("OTHER_T01_JOINTS", {}))
AX = {}
for k, v in T01_GROUPS.items():
    AX[k] = {"joint_axial_center_mm": v["joint_axial_center_mm"],
             "axial_finger_length_mm": v["axial_finger_length_mm"],
             "zone_half_width_mm": v["zone_half_width_mm"],
             "loops_mm": v["LOOP_POSITION_axial_from_commissure_mm"]}
rep["t01_axial"] = AX
cmp_ = {}
for D in ("INDEX", "MIDDLE", "RING", "LITTLE"):
    prox = Vector(jf["%s_MCP_R" % D]["head"])
    dist = Vector(jf["%s_TIP_R" % D]["head"])
    ax = (dist - prox).normalized()
    for s in ("PIP", "DIP"):
        k = "%s_%s" % (D, s)
        p = Vector(jf["%s_%s_R" % (D, s)]["head"])
        meas = (p - prox).dot(ax) * MM
        ref = AX[k]["joint_axial_center_mm"]
        cmp_[k] = {"measured_axial_mm": round(meas, 3), "t01_axial_mm": round(ref, 3),
                   "delta_mm": round(meas - ref, 3), "zone_half_width_mm": AX[k]["zone_half_width_mm"],
                   "within_zone": abs(meas - ref) <= AX[k]["zone_half_width_mm"]}
rep["axial_vs_t01"] = cmp_

# ---- fingertip landmark test (ownership based) --------------------------------------
tip = {}
for D in CHAIN:
    prox = Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])
    faces = DIGIT_FACES[D]
    vs = sorted({v for fi in faces for v in me.polygons[fi].vertices})
    best, bd = None, -1
    for v in vs:
        dd = (W[v] - prox).length
        if dd > bd:
            bd, best = dd, v
    tl = Vector(jf["%s_TIP_R" % D]["head"])
    # distal-most along the distal-phalanx axis
    db = "%s_%s_R" % (D, CHAIN[D][-1])
    h = Vector(jf[db]["head"]); t = Vector(jf[db]["tail"])
    ax = (t - h).normalized()
    ex = max((W[v] - h).dot(ax) for v in vs)
    tip[D] = {"own_verts": len(vs), "farthest_vertex_index": best,
              "landmark_to_farthest_vertex_mm": round((W[best] - tl).length * MM, 3),
              "mesh_extent_along_distal_axis_mm": round(ex * MM, 3),
              "landmark_along_distal_axis_mm": round((tl - h).dot(ax) * MM, 3),
              "landmark_beyond_mesh_mm": round(((tl - h).dot(ax) - ex) * MM, 3)}
rep["tip"] = tip

# thumb-specific: is the TIP landmark at the thumb apex?
tv = DIGIT_FACES["THUMB"]
vss = sorted({v for fi in tv for v in me.polygons[fi].vertices})
tl = Vector(jf["THUMB_TIP_R"]["head"])
ds = sorted(((W[v] - tl).length * MM, v) for v in vss)[:8]
rep["thumb_tip_nearest_vertices"] = [{"dist_mm": round(a, 3), "vertex": b} for a, b in ds]
rep["thumb_farthest_vertex_world"] = [round(float(x), 6) for x in W[tip["THUMB"]["farthest_vertex_index"]]]
rep["thumb_tip_landmark_world"] = [round(float(x), 6) for x in tl]
json.dump(rep, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("OUT=" + OUT)
