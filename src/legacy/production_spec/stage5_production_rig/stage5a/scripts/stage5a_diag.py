# STAGE5A -- focused diagnostic: ring radii, digit-local surface tests, TIP landmarks.
# Read-only.
import bpy, bmesh, sys, os, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:]
MASTER = argv[0]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
OUT = r"<HANDS_ROOT>\production_spec\stage5_production_rig\stage5a\_tmp\S5A_GEOMETRY_DIAG.json"
MM = 1000.0
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
nail = json.load(open(os.path.join(S4, "stage4c_r2", "NAIL_AUDIT_R2.json"), encoding="utf-8"))
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
DISTAL = {D: "%s_%s_R" % (D, CHAIN[D][-1]) for D in CHAIN}
rep = {}

T01G = dict(t01.get("T01_MCP", {}))
T01G.update(t01.get("OTHER_T01_JOINTS", {}))
rings = {}
for jn, jd in T01G.items():
    vi = set()
    for flat in jd["_verts"]:
        vi.update(flat[0::2])
    pts = [W[i] for i in sorted(vi)]
    c = sum(pts, Vector()) / len(pts)
    rad = [ (p - c).length * MM for p in pts]
    # true ring axis = direction from the previous joint to the next joint of that digit
    rings[jn] = {"centroid": c, "n": len(pts),
                 "mean_ring_radius_mm": round(sum(rad) / len(rad), 3),
                 "min_r": round(min(rad), 3), "max_r": round(max(rad), 3),
                 "zone_half_width_mm": jd["zone_half_width_mm"]}
rep["t01_rings"] = {k: {"centroid": [round(float(x), 6) for x in v["centroid"]],
                        "n": v["n"], "mean_ring_radius_mm": v["mean_ring_radius_mm"],
                        "min_r": v["min_r"], "max_r": v["max_r"],
                        "zone_half_width_mm": v["zone_half_width_mm"]} for k, v in rings.items()}

# ring axis from the joint frame chain (previous joint -> next joint)
AXIS_OF_RING = {
    "INDEX_MCP": ("WRIST_R", "INDEX_PIP_R"), "INDEX_PIP": ("INDEX_MCP_R", "INDEX_DIP_R"),
    "INDEX_DIP": ("INDEX_PIP_R", "INDEX_TIP_R"),
    "MIDDLE_MCP": ("WRIST_R", "MIDDLE_PIP_R"), "MIDDLE_PIP": ("MIDDLE_MCP_R", "MIDDLE_DIP_R"),
    "MIDDLE_DIP": ("MIDDLE_PIP_R", "MIDDLE_TIP_R"),
    "RING_MCP": ("WRIST_R", "RING_PIP_R"), "RING_PIP": ("RING_MCP_R", "RING_DIP_R"),
    "RING_DIP": ("RING_PIP_R", "RING_TIP_R"),
    "LITTLE_MCP": ("WRIST_R", "LITTLE_PIP_R"), "LITTLE_PIP": ("LITTLE_MCP_R", "LITTLE_DIP_R"),
    "LITTLE_DIP": ("LITTLE_PIP_R", "LITTLE_TIP_R"),
    "THUMB_MCP": ("THUMB_CMC_R", "THUMB_IP_R"), "THUMB_IP": ("THUMB_MCP_R", "THUMB_TIP_R"),
}
JOINT_OF_RING = {"THUMB_MCP": "THUMB_MCP_R", "THUMB_IP": "THUMB_IP_R"}
for D in ("INDEX", "MIDDLE", "RING", "LITTLE"):
    for s in ("MCP", "PIP", "DIP"):
        JOINT_OF_RING["%s_%s" % (D, s)] = "%s_%s_R" % (D, s)

# ---- digit-local surface patches + BVH ----
def chain_polyline(D):
    segs = CHAIN[D]
    pts = [Vector(jf["%s_%s_R" % (D, segs[0])]["head"])]
    for s in segs:
        pts.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
    return pts


def dist_to_polyline(p, poly):
    best = 1e9
    for i in range(len(poly) - 1):
        a, b = poly[i], poly[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
        best = min(best, (p - (a + ab * t)).length)
    return best


LOCAL = {}
for D in CHAIN:
    poly = chain_polyline(D)
    R = R_ENV[D] * 1e-3 * 1.45
    faces = []
    for p in me.polygons:
        c = sum((W[v] for v in p.vertices), Vector()) / len(p.vertices)
        if dist_to_polyline(c, poly) <= R:
            faces.append(p.index)
    vs = sorted({v for fi in faces for v in me.polygons[fi].vertices})
    idx = {v: i for i, v in enumerate(vs)}
    verts = [W[v] for v in vs]
    polys = [tuple(idx[v] for v in me.polygons[fi].vertices) for fi in faces]
    LOCAL[D] = {"faces": faces, "n_faces": len(faces), "n_verts": len(vs),
                "bvh": BVHTree.FromPolygons(verts, polys, all_triangles=False),
                "verts": verts, "polys": polys, "R_mm": R * MM}
rep["digit_local_patches"] = {D: {"n_faces": LOCAL[D]["n_faces"], "n_verts": LOCAL[D]["n_verts"],
                                  "R_mm": round(LOCAL[D]["R_mm"], 2)} for D in LOCAL}


def local_test(D, p):
    l = LOCAL[D]
    loc, nor, fi, d = l["bvh"].find_nearest(p, 0.2)
    if loc is None:
        return {"found": False}
    # outward normal from the ORIGINAL mesh polygon
    orig_fi = l["faces"][fi]
    n = (MW.to_3x3() @ me.polygons[orig_fi].normal).normalized()
    off = (p - loc).dot(n)
    return {"found": True, "dist_mm": round((p - loc).length * MM, 4),
            "signed_mm": round(off * MM, 4), "inside": bool(off < 0),
            "nearest_face": orig_fi}


# ---- joint validation, digit-local ----
DIGIT_OF = {"WRIST_R": None, "THUMB_CMC_R": "THUMB", "THUMB_MCP_R": "THUMB", "THUMB_IP_R": "THUMB",
            "THUMB_TIP_R": "THUMB"}
for D in ("INDEX", "MIDDLE", "RING", "LITTLE"):
    for s in ("MCP", "PIP", "DIP", "TIP"):
        DIGIT_OF["%s_%s_R" % (D, s)] = D
ORDER = ["WRIST_R"]
for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    ORDER += ["%s_%s_R" % (D, s) for s in CHAIN[D]] + ["%s_TIP_R" % D]

out = {}
for n in ORDER:
    D = DIGIT_OF[n]
    p = Vector(jf[n]["head"])
    e = {"joint": n, "world": [round(float(x), 4) for x in p]}
    if D:
        e["digit_local_surface"] = local_test(D, p)
        e["digit_r_env_mm"] = R_ENV[D]
        e["dist_to_digit_chain_polyline_mm"] = round(dist_to_polyline(p, chain_polyline(D)) * MM, 4)
    rings_for_joint = [k for k in JOINT_OF_RING if JOINT_OF_RING[k] == n]
    if rings_for_joint:
        k = rings_for_joint[0]
        r = rings[k]
        a, b = AXIS_OF_RING[k]
        ax = (Vector(jf[b]["head"]) - Vector(jf[a]["head"])).normalized()
        # ring plane normal
        vi = set()
        for flat in T01G[k]["_verts"]:
            vi.update(flat[0::2])
        pts = [W[i] for i in sorted(vi)]
        c = r["centroid"]
        M = [[0.0] * 3 for _ in range(3)]
        for q in pts:
            dd = q - c
            for x in range(3):
                for y in range(3):
                    M[x][y] += dd[x] * dd[y]
        tr = M[0][0] + M[1][1] + M[2][2]
        N = [[(tr if x == y else 0.0) - M[x][y] for y in range(3)] for x in range(3)]
        vec = Vector((0.0, 0.0, 1.0))
        for _ in range(200):
            nv = Vector((sum(N[0][t] * vec[t] for t in range(3)),
                         sum(N[1][t] * vec[t] for t in range(3)),
                         sum(N[2][t] * vec[t] for t in range(3))))
            if nv.length < 1e-18:
                break
            vec = nv.normalized()
        d = p - c
        e["ring"] = {
            "ring": k, "centroid": [round(float(x), 6) for x in c],
            "mean_ring_radius_mm": r["mean_ring_radius_mm"],
            "d_centroid_mm": round(d.length * MM, 4),
            "d_plane_mm": round(abs(d.dot(vec)) * MM, 4),
            "d_radial_mm": round(math.sqrt(max(0.0, d.length ** 2 - d.dot(vec) ** 2)) * MM, 4),
            "angle_plane_normal_vs_chain_axis_deg": round(math.degrees(math.acos(
                max(-1.0, min(1.0, abs(vec.dot(ax)))))), 3),
            "zone_half_width_mm": r["zone_half_width_mm"],
        }
        # axial position relative to the chain axis, measured from the ring centre
        e["ring"]["axial_offset_vs_ring_mm"] = round(d.dot(ax) * MM, 4)
    out[n] = e
rep["joints"] = out

# ---- TIP landmark check: digit's farthest vertex from the proximal joint ----
tipchk = {}
for D in CHAIN:
    prox = Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])
    poly = chain_polyline(D)
    R = R_ENV[D] * 1e-3 * 1.45
    best, bd = None, -1
    for i, q in enumerate(W):
        if dist_to_polyline(q, poly) <= R:
            dd = (q - prox).length
            if dd > bd:
                bd, best = dd, i
    tl = Vector(jf["%s_TIP_R" % D]["head"])
    tipchk[D] = {"farthest_vertex_index": best, "farthest_dist_from_proximal_mm": round(bd * MM, 3),
                 "tip_landmark_dist_to_farthest_vertex_mm": round((W[best] - tl).length * MM, 3),
                 "tip_landmark_dist_from_proximal_mm": round((tl - prox).length * MM, 3)}
    # also: along the DISTAL bone axis, how far beyond the landmark does mesh extend?
    db = DISTAL[D]
    h = Vector(jf[db]["head"]); t = Vector(jf[db]["tail"])
    ax = (t - h).normalized()
    ex = None
    for i, q in enumerate(W):
        if dist_to_polyline(q, poly) <= R:
            v = (q - h).dot(ax)
            if ex is None or v > ex:
                ex = v
    tipchk[D]["mesh_extent_along_distal_axis_mm"] = round(ex * MM, 3)
    tipchk[D]["tip_landmark_along_distal_axis_mm"] = round((tl - h).dot(ax) * MM, 3)
rep["tip_check"] = tipchk

# ---- thumb internal structure ----
h = Vector(jf["THUMB_IP_R"]["head"]); t = Vector(jf["THUMB_IP_R"]["tail"])
rep["thumb_note"] = {"THUMB_IP_head": [round(float(x), 6) for x in h],
                     "THUMB_TIP_head": [round(float(x), 6) for x in t]}
json.dump(rep, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("OUT=" + OUT)
