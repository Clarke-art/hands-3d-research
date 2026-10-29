# STAGE5A_PRODUCTION_RIG_SKELETON_R1 -- READ-ONLY input forensics probe
# Opens the frozen Stage-4C R2 master, measures the current mesh, validates the
# Stage-4B R2 candidate joint frame against the CURRENT approved mesh.
# Saves nothing.
import bpy, json, math, os, sys

MASTER = r"<HANDS_ROOT>\production_spec\stage4_blender\stage4c_r2\RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend"
JOINT_FRAME = r"<HANDS_ROOT>\production_spec\stage4_blender\stage4c_r2\STAGE4B_R2_JOINT_FRAME.json"
NAIL_AUDIT = r"<HANDS_ROOT>\production_spec\stage4_blender\stage4c_r2\NAIL_AUDIT_R2.json"
T01 = r"<HANDS_ROOT>\production_spec\stage4_blender\stage4a_t01\T01_FINAL_AUDIT.json"
CAGE = r"<HANDS_ROOT>\production_spec\stage4_blender\stage4a_r2\R2_CAGE.json"
ORIGIN_AUDIT = r"<HANDS_ROOT>\production_spec\stage4_blender\stage4c_r2\ORIGIN_AUDIT_R2.json"
OUT = r"<HANDS_ROOT>\production_spec\stage5_production_rig\stage5a\_tmp\S5A_INPUT_FORENSICS.json"

MM = 1000.0
rep = {}
rep["mode"] = "READ_ONLY_FORENSICS"
rep["blender"] = bpy.app.version_string
rep["filepath"] = bpy.data.filepath

obj = bpy.data.objects["Hand  - Realistic"]
me = obj.data
MW = obj.matrix_world
V = [MW @ v.co for v in me.vertices]
rep["mesh"] = {
    "object": obj.name,
    "V": len(me.vertices), "E": len(me.edges), "F": len(me.polygons),
    "material_slots": [ms.material.name for ms in obj.material_slots],
}
rep["object_transform"] = {
    "location": list(obj.location), "rotation_euler": list(obj.rotation_euler),
    "scale": list(obj.scale),
}
bb_min = [min(v[i] for v in V) for i in range(3)]
bb_max = [max(v[i] for v in V) for i in range(3)]
rep["world_bbox"] = {"min": bb_min, "max": bb_max,
                     "size_mm": [(bb_max[i] - bb_min[i]) * MM for i in range(3)]}


def v3(v):
    return [v[0], v[1], v[2]]


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    l = math.sqrt(dot(a, a))
    return (a[0] / l, a[1] / l, a[2] / l) if l > 1e-15 else (0.0, 0.0, 0.0)


def centroid(pts):
    n = len(pts)
    return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n, sum(p[2] for p in pts) / n)


# ---------- 1. approved authority values ----------
oa = json.load(open(ORIGIN_AUDIT, encoding="utf-8"))
WRIST_APPROVED = tuple(oa["WRIST_ORIGIN"])
rep["approved_wrist_origin"] = list(WRIST_APPROVED)
stage4b_wrist_head = tuple(oa["stage4b_WRIST_R_head"])
rep["stage4b_wrist_r_head"] = list(stage4b_wrist_head)
rep["wrist_approved_vs_stage4b_mm"] = math.sqrt(sum((WRIST_APPROVED[i] - stage4b_wrist_head[i]) ** 2 for i in range(3))) * MM

cage = json.load(open(CAGE, encoding="utf-8"))
CMC_ANCHOR_VIDX = cage["cmc_vertex"]
CMC_ANCHOR_OLD = tuple(cage["cmc_world"])
CMC_ANCHOR_NOW = V[CMC_ANCHOR_VIDX]
rep["cmc_anchor"] = {
    "vertex_index": CMC_ANCHOR_VIDX,
    "world_unposed_from_R2_CAGE": list(CMC_ANCHOR_OLD),
    "world_current_posed_mesh": v3(CMC_ANCHOR_NOW),
    "R2_CAGE_shift_mm": math.sqrt(sum((CMC_ANCHOR_NOW[i] - CMC_ANCHOR_OLD[i]) ** 2 for i in range(3))) * MM,
    "R2_CAGE_disk_geodesic_radius_mm": cage["disk"]["R_mm"],
    "R2_CAGE_boundary_geodesic_radius_mm": cage["disk"]["boundary_geodesic_radius_mm"],
}

jf = json.load(open(JOINT_FRAME, encoding="utf-8"))
STAGE4B = jf["bones"]
rep["stage4b_frame_source"] = jf["source_blend"]
rep["stage4b_frame_source_sha256"] = jf["source_sha256"]

nail = json.load(open(NAIL_AUDIT, encoding="utf-8"))
t01 = json.load(open(T01, encoding="utf-8"))

# ---------- 2. per-digit dorsal reference from the APPROVED nail face sets ----------
DIGITS = ["thumb", "index", "middle", "ring", "little"]
dorsal = {}
for d in DIGITS:
    faces = nail["per_digit_faces"][d]
    acc = (0.0, 0.0, 0.0)
    for fi in faces:
        n = me.polygons[fi].normal
        acc = add(acc, (n[0], n[1], n[2]))
    dorsal[d] = norm(acc)
rep["per_digit_dorsal_from_approved_nail_faces"] = {d: v3(dorsal[d]) for d in DIGITS}
# pairwise angles (sanity, should reproduce ~11-15 deg)
pair_angles = {}
for i in range(len(DIGITS)):
    for k in range(i + 1, len(DIGITS)):
        a, b = DIGITS[i], DIGITS[k]
        c = max(-1.0, min(1.0, dot(dorsal[a], dorsal[b])))
        pair_angles[f"{a}-{b}"] = math.degrees(math.acos(c))
rep["dorsal_pair_angles_deg"] = pair_angles

# ---------- 3. forearm axis + cross-section profile ----------
zmin = bb_min[2]
ring_cut = [V[i] for i in range(len(V)) if V[i][2] < zmin + 0.002]
c_cut = centroid(ring_cut)
wz = WRIST_APPROVED[2]
ring_w = [V[i] for i in range(len(V)) if abs(V[i][2] - wz) < 0.008]
c_w = centroid(ring_w)
arm_axis = norm(sub(c_w, c_cut))
rep["cut_plane"] = {"z": zmin, "centroid": v3(c_cut), "ring_verts": len(ring_cut)}
rep["wrist_slab"] = {"centroid": v3(c_w), "verts": len(ring_w)}
rep["arm_axis_from_cut_to_wrist"] = v3(arm_axis)


def hull_area_2d(pts2):
    pts = sorted(set(pts2))
    if len(pts) < 3:
        return 0.0
    def half(seq):
        st = []
        for p in seq:
            while len(st) >= 2 and (st[-1][0] - st[-2][0]) * (p[1] - st[-2][1]) - (st[-1][1] - st[-2][1]) * (p[0] - st[-2][0]) <= 0:
                st.pop()
            st.append(p)
        return st
    lo = half(pts)
    hi = half(pts[::-1])
    poly = lo[:-1] + hi[:-1]
    if len(poly) < 3:
        return 0.0
    a = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        a += x1 * y2 - x2 * y1
    return abs(a) * 0.5


# local 2D basis
tmp = (0.0, 0.0, 1.0) if abs(arm_axis[2]) < 0.9 else (1.0, 0.0, 0.0)
e1 = norm(cross(arm_axis, tmp))
e2 = cross(arm_axis, e1)

s_all = [dot(sub(v, c_cut), arm_axis) for v in V]
profile = []
step = 0.002
smax = max(s_all)
s = 0.0 + step * 0.5
while s < min(smax, 0.26):
    slab = [v for i, v in enumerate(V) if abs(s_all[i] - s) < step * 0.6]
    if len(slab) >= 4:
        pts2 = [(dot(sub(p, c_cut), e1), dot(sub(p, c_cut), e2)) for p in slab]
        a = hull_area_2d(pts2) * 1e6
        cs = centroid(slab)
        perp = math.sqrt(sum((sub(cs, c_cut)[i] - dot(sub(cs, c_cut), arm_axis) * arm_axis[i]) ** 2 for i in range(3))) * MM
        profile.append({"s_mm": round(s * MM, 1), "z_mm": round(cs[2] * MM, 3),
                        "hull_area_mm2": round(a, 1), "n": len(slab), "centre_perp_mm": round(perp, 2)})
    s += step
rep["cross_section_profile"] = profile

# local minima of the area profile
lm = []
for i in range(2, len(profile) - 2):
    w = profile[i - 2:i + 3]
    if profile[i]["hull_area_mm2"] == min(x["hull_area_mm2"] for x in w):
        lm.append(profile[i])
rep["profile_local_minima"] = lm

s_wrist = dot(sub(WRIST_APPROVED, c_cut), arm_axis)
rep["wrist_origin_along_arm_axis_mm"] = s_wrist * MM
rep["wrist_origin_perp_from_axis_mm"] = math.sqrt(
    sum((sub(WRIST_APPROVED, c_cut)[i] - s_wrist * arm_axis[i]) ** 2 for i in range(3))) * MM

# ---------- 4. anatomical proportion cross-checks ----------
MCP = {d: tuple(STAGE4B[f"{d.upper()}_MCP_R"]["head"]) for d in DIGITS if d != "thumb"}
mcp_mean = centroid(list(MCP.values()))
rep["proportion_crosscheck"] = {
    "wmcp_mean": v3(mcp_mean),
    "wrist_to_mean_mcp_mm": math.sqrt(sum((WRIST_APPROVED[i] - mcp_mean[i]) ** 2 for i in range(3))) * MM,
    "dist_mm": {d: round(math.sqrt(sum((WRIST_APPROVED[i] - MCP[d][i]) ** 2 for i in range(3))) * MM, 2) for d in MCP},
    "wrist_to_cmc_anchor_mm": round(math.sqrt(sum((WRIST_APPROVED[i] - CMC_ANCHOR_NOW[i]) ** 2 for i in range(3))) * MM, 2),
    "forearm_cut_to_wrist_along_axis_mm": round(s_wrist * MM, 2),
    "wrist_to_middle_tip_landmark_mm": round(math.sqrt(
        sum((WRIST_APPROVED[i] - STAGE4B["MIDDLE_TIP_R"]["head"][i]) ** 2 for i in range(3))) * MM, 2),
    "wrist_to_farthest_mesh_vertex_mm": round(max(
        math.sqrt(sum((WRIST_APPROVED[i] - v[i]) ** 2 for i in range(3))) for v in V) * MM, 2),
    "stage4b_wrist_bone_length_mm": round(math.sqrt(sum(
        (STAGE4B["WRIST_R"]["tail"][i] - STAGE4B["WRIST_R"]["head"][i]) ** 2 for i in range(3))) * MM, 2),
}

# ---------- 5. per-joint validation against the CURRENT mesh ----------
def closest(p):
    ok, loc, nor, idx = obj.closest_point_on_mesh(p)
    return (loc, nor, idx) if ok else (None, None, None)


T01_GROUPS = {}
for k, v in t01.get("T01_MCP", {}).items():
    T01_GROUPS[k] = v
for k, v in t01.get("OTHER_T01_JOINTS", {}).items():
    T01_GROUPS[k] = v


def loop_verts(flat):
    return sorted(set(flat[0::2]))


ring_cache = {}
for jn, jd in T01_GROUPS.items():
    pts = []
    for flat in jd["_verts"]:
        for vi in loop_verts(flat):
            pts.append(V[vi])
    c = centroid(pts)
    # plane normal via covariance
    n = len(pts)
    cov = [[0.0] * 3 for _ in range(3)]
    for p in pts:
        d = sub(p, c)
        for a in range(3):
            for b in range(3):
                cov[a][b] += d[a] * d[b]
    # power iteration for the smallest eigenvector is annoying; use the largest for the ring plane normal
    vec = (1.0, 0.0, 0.0)
    for _ in range(60):
        vec = norm((sum(cov[0][k] * vec[k] for k in range(3)),
                    sum(cov[1][k] * vec[k] for k in range(3)),
                    sum(cov[2][k] * vec[k] for k in range(3))))
    ring_cache[jn] = {"centroid": c, "ring_normal": vec, "n_verts": n,
                      "axial_loops_mm": jd["LOOP_POSITION_axial_from_commissure_mm"],
                      "loop_axial_min": min(jd["LOOP_POSITION_axial_from_commissure_mm"]),
                      "loop_axial_max": max(jd["LOOP_POSITION_axial_from_commissure_mm"]),
                      "zone_half_width_mm": jd["zone_half_width_mm"]}

JOINT_TO_T01 = {
    "THUMB_MCP_R": "THUMB_MCP", "THUMB_IP_R": "THUMB_IP",
    "INDEX_MCP_R": "INDEX_MCP", "INDEX_PIP_R": "INDEX_PIP", "INDEX_DIP_R": "INDEX_DIP",
    "MIDDLE_MCP_R": "MIDDLE_MCP", "MIDDLE_PIP_R": "MIDDLE_PIP", "MIDDLE_DIP_R": "MIDDLE_DIP",
    "RING_MCP_R": "RING_MCP", "RING_PIP_R": "RING_PIP", "RING_DIP_R": "RING_DIP",
    "LITTLE_MCP_R": "LITTLE_MCP", "LITTLE_PIP_R": "LITTLE_PIP", "LITTLE_DIP_R": "LITTLE_DIP",
}

joints = {}
for bone_name, bd in STAGE4B.items():
    if bone_name == "WRIST_R":
        p = WRIST_APPROVED
        src = "STAGE4C_R2_APPROVED_WRIST_ORIGIN"
    else:
        p = tuple(bd["head"])
        src = "Stage4B_R2 candidate joint frame + Stage5A current-mesh validation"
    loc, nor, fidx = closest(p)
    signed = dot(sub(p, loc), nor) if loc else 0.0
    e = {
        "world_position": v3(p), "authority": src,
        "nearest_surface_distance_mm": round(math.sqrt(sum((p[i] - loc[i]) ** 2 for i in range(3))) * MM, 3),
        "inside_mesh_by_normal_sign": bool(signed < 0),
        "signed_offset_mm": round(signed * MM, 3),
    }
    t = JOINT_TO_T01.get(bone_name)
    if t and t in ring_cache:
        rc = ring_cache[t]
        e["t01_ring"] = {
            "ring": t,
            "ring_centroid_world": v3(rc["centroid"]),
            "dist_landmark_to_ring_centroid_mm": round(math.sqrt(
                sum((p[i] - rc["centroid"][i]) ** 2 for i in range(3))) * MM, 3),
            "dist_landmark_to_ring_plane_mm": round(abs(dot(sub(p, rc["centroid"]), rc["ring_normal"])) * MM, 3),
            "ring_axial_loops_mm": rc["axial_loops_mm"],
            "ring_mean_axial_mm": round(sum(rc["axial_loops_mm"]) / len(rc["axial_loops_mm"]), 3),
            "ring_axial_span_mm": round(max(rc["axial_loops_mm"]) - min(rc["axial_loops_mm"]), 3),
            "zone_half_width_mm": rc["zone_half_width_mm"],
            "n_ring_verts": rc["n_verts"],
        }
    joints[bone_name] = e
rep["joint_validation"] = joints

# ---------- 6. CMC discrimination ----------
cmc = tuple(STAGE4B["THUMB_CMC_R"]["head"])
loc, nor, _ = closest(cmc)
rep["cmc_validation"] = {
    "landmark": v3(cmc),
    "axis_approved_anchor_vertex": CMC_ANCHOR_VIDX,
    "anchor_world": v3(CMC_ANCHOR_NOW),
    "landmark_to_anchor_mm": round(math.sqrt(sum((cmc[i] - CMC_ANCHOR_NOW[i]) ** 2 for i in range(3))) * MM, 3),
    "landmark_surface_dist_mm": round(math.sqrt(sum((cmc[i] - loc[i]) ** 2 for i in range(3))) * MM, 3),
    "landmark_inside_mesh": bool(dot(sub(cmc, loc), nor) < 0),
    "cage_disk_R_mm": cage["disk"]["R_mm"],
    "cage_locality_euclid_radius_mm": cage["locality"]["euclidean_radius_mm"],
    "cage_axial_span_mm": cage["locality"]["axial_span_mm"],
    "cage_boundary_loop_first_pts_world": cage["boundary_loop_world"][:4],
}

# ---------- 7. distal phalanx lengths (for TIP rule) ----------
tipctx = {}
for d in DIGITS:
    D = d.upper()
    seg = ["CMC", "MCP", "IP"] if d == "thumb" else ["MCP", "PIP", "DIP"]
    hd = STAGE4B[f"{D}_{seg[-1]}_R"]["head"]
    tl = STAGE4B[f"{D}_{seg[-1]}_R"]["tail"]
    tipctx[f"{D}_DISTAL_PHALANX"] = {
        "bone": f"{D}_{seg[-1]}_R",
        "length_mm": round(math.sqrt(sum((tl[i] - hd[i]) ** 2 for i in range(3))) * MM, 4),
        "dir": v3(norm(sub(tuple(tl), tuple(hd)))),
        "stage4b_tip_helper_length_mm": round(math.sqrt(math.sqrt(
            sum((STAGE4B[f"{D}_TIP_R"]["tail"][i] - STAGE4B[f"{D}_TIP_R"]["head"][i]) ** 2 for i in range(3))) ** 2) * MM, 4),
    }
rep["distal_phalanx"] = tipctx

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(rep, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("PROBE_JSON=" + OUT)
print("IS_DIRTY=" + str(bool(bpy.data.is_dirty)))
