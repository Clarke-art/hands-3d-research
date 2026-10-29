# STAGE5A -- strict-ownership re-check of the two flagged thumb landmarks.
import bpy, sys, os, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:]
MASTER, OUT = argv[0], argv[1]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
MM = 1000.0
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
bpy.ops.wm.open_mainfile(filepath=MASTER)
ob = bpy.data.objects["Hand  - Realistic"]
me = ob.data
MW = ob.matrix_world
W = [(MW @ v.co).copy() for v in me.vertices]
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"],
         "LITTLE": ["MCP", "PIP", "DIP"]}


def chainpts(D):
    p = [Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])]
    for s in CHAIN[D]:
        p.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
    return p


CH = {D: chainpts(D) for D in CHAIN}
WRIST = [Vector(jf["WRIST_R"]["head"]), Vector(jf["WRIST_R"]["tail"])]


def d_poly(p, poly):
    best = 1e9
    for i in range(len(poly) - 1):
        a, b = poly[i], poly[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
        best = min(best, (p - (a + ab * t)).length)
    return best


owner = {}
for p in me.polygons:
    c = sum((W[v] for v in p.vertices), Vector()) / len(p.vertices)
    dd = {D: d_poly(c, CH[D]) for D in CH}
    dd["wrist"] = d_poly(c, WRIST)
    owner[p.index] = min(dd, key=dd.get)

# STRICT vertex ownership: every incident face belongs to the digit
vown = {}
for v in me.vertices:
    ds = {owner[p.index] for p in me.polygons if v.index in p.vertices}
    vown[v.index] = ds.pop() if len(ds) == 1 else "MIXED"

rep = {"vertex_ownership": {}, "face_ownership": {}}
for k in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE", "wrist", "MIXED"):
    rep["vertex_ownership"][k] = sum(1 for x in vown.values() if x == k)
    rep["face_ownership"][k] = sum(1 for x in owner.values() if x == k)

T = "THUMB"
tv = [i for i in vown if vown[i] == T]
tf = [i for i in owner if owner[i] == T]
tl = Vector(jf["THUMB_TIP_R"]["head"])
apex = max(tv, key=lambda i: (W[i] - Vector(jf["THUMB_CMC_R"]["head"])).length)
rep["thumb_strict"] = {
    "strict_verts": len(tv), "owned_faces": len(tf),
    "apex_vertex": apex,
    "apex_world": [round(float(x), 6) for x in W[apex]],
    "apex_dist_from_cmc_mm": round((W[apex] - Vector(jf["THUMB_CMC_R"]["head"])).length * MM, 3),
    "tip_landmark_world": [round(float(x), 6) for x in tl],
    "tip_landmark_dist_from_cmc_mm": round((tl - Vector(jf["THUMB_CMC_R"]["head"])).length * MM, 3),
    "landmark_to_apex_mm": round((W[apex] - tl).length * MM, 3),
    "landmark_nearest_strict_vert_mm": round(min((W[i] - tl).length for i in tv) * MM, 3),
}

# thumb tube radius profile along the chain axis, and the MCP-level surface radius
db = "THUMB_IP_R"
h = Vector(jf[db]["head"]); t = Vector(jf[db]["tail"])
axI = (t - h).normalized()
prof = []
for s in range(-10, 45, 4):
    p = h + axI * (s * 1e-3)
    rr = [( (W[i] - h - axI * (W[i] - h).dot(axI)).length, i) for i in tv]
    band = sorted((abs((W[i] - h).dot(axI) - s * 1e-3) * MM, (W[i] - h - axI * (W[i] - h).dot(axI)).length * MM)
                  for i in tv)
    band = [b for b in band if b[0] <= 2.0]
    if band:
        prof.append({"s_mm": s, "n": len(band),
                     "r_min_mm": round(min(b[1] for b in band), 3),
                     "r_max_mm": round(max(b[1] for b in band), 3)})
rep["thumb_radius_profile_along_IP_axis"] = prof

cm = Vector(jf["THUMB_MCP_R"]["head"])
cb = "THUMB_CMC_R"
ch_ = Vector(jf[cb]["head"]); ct = Vector(jf[cb]["tail"])
axC = (ct - ch_).normalized()
sM = (cm - ch_).dot(axC) * MM
band = sorted(((abs((W[i] - ch_).dot(axC) * MM - sM), (W[i] - ch_ - axC * (W[i] - ch_).dot(axC)).length * MM)
               for i in tv))
band = [b for b in band if b[0] <= 2.0]
rep["thumb_mcp_level"] = {
    "landmark": [round(float(x), 6) for x in cm],
    "axial_from_cmc_mm": round(sM, 3),
    "landmark_radius_from_CMC_axis_mm": round((cm - ch_ - axC * (cm - ch_).dot(axC)).length * MM, 3),
    "thumb_surface_radius_at_that_level_mm": {"min": round(min(b[1] for b in band), 3),
                                              "max": round(max(b[1] for b in band), 3), "n": len(band)},
}
lb = Vector(jf["THUMB_CMC_R"]["head"])
rep["thumb_cmc_level"] = {
    "landmark_radius_from_own_axis_mm": round((lb - ch_ - axC * (lb - ch_).dot(axC)).length * MM, 3),
}
il = Vector(jf["THUMB_IP_R"]["head"])
i_ch = Vector(jf["THUMB_MCP_R"]["head"]); i_ct = Vector(jf["THUMB_MCP_R"]["tail"])
i_ax = (i_ct - i_ch).normalized()
rep["thumb_ip_level"] = {
    "landmark_radius_from_MCP_axis_mm": round((il - i_ch - i_ax * (il - i_ch).dot(i_ax)).length * MM, 3)}

# finger comparison: apex vs landmark for the four fingers (strict verts)
fp = {}
for D in ("INDEX", "MIDDLE", "RING", "LITTLE"):
    vs = [i for i in vown if vown[i] == D]
    prox = Vector(jf["%s_MCP_R" % D]["head"])
    ap = max(vs, key=lambda i: (W[i] - prox).length)
    lm = Vector(jf["%s_TIP_R" % D]["head"])
    fp[D] = {"strict_verts": len(vs), "apex_vertex": ap,
             "apex_world": [round(float(x), 6) for x in W[ap]],
             "landmark_to_apex_mm": round((W[ap] - lm).length * MM, 3),
             "landmark_nearest_strict_vert_mm": round(min((W[i] - lm).length for i in vs) * MM, 3)}
rep["finger_apex"] = fp
json.dump(rep, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(rep["thumb_strict"], indent=1))
print(json.dumps(rep["thumb_mcp_level"], indent=1))
print(json.dumps(rep["thumb_cmc_level"], indent=1))
print(json.dumps(rep["thumb_ip_level"], indent=1))
