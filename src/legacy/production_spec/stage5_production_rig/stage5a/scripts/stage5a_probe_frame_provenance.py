# STAGE5A -- DECISIVE probe: is STAGE4B_R2_JOINT_FRAME.json REST or POSED, and which one
# matches the CURRENT approved Stage-4C R2 mesh joint regions?
# Read-only. Saves nothing.
import bpy, json, math, os

STAGE4B = r"<HANDS_ROOT>\production_spec\stage4_blender\stage4b_rssf\RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R2.blend"
MASTER = r"<HANDS_ROOT>\production_spec\stage4_blender\stage4c_r2\RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend"
JOINT_FRAME = r"<HANDS_ROOT>\production_spec\stage4_blender\stage4c_r2\STAGE4B_R2_JOINT_FRAME.json"
NAIL_AUDIT = r"<HANDS_ROOT>\production_spec\stage4_blender\stage4c_r2\NAIL_AUDIT_R2.json"
OUT = r"<HANDS_ROOT>\production_spec\stage5_production_rig\stage5a\_tmp\S5A_JOINT_FRAME_PROVENANCE.json"
MM = 1000.0
DIGITS = ["thumb", "index", "middle", "ring", "little"]
rep = {}

# ---------- A. frozen Stage-4B R2 provenance: REST vs POSED ----------
bpy.ops.wm.open_mainfile(filepath=STAGE4B)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
aw = arm.matrix_world
rest, posed = {}, {}
for b in arm.data.bones:
    rest[b.name] = {"head": [float(x) for x in (aw @ b.head_local)],
                    "tail": [float(x) for x in (aw @ b.tail_local)]}
for pb in arm.pose.bones:
    posed[pb.name] = {"head": [float(x) for x in (aw @ pb.head)],
                      "tail": [float(x) for x in (aw @ pb.tail)]}
rep["stage4b_object"] = arm.name
rep["stage4b_rest_vs_posed_head_delta_mm"] = {
    n: round(math.dist(rest[n]["head"], posed[n]["head"]) * MM, 4) for n in rest}
rep["stage4b_rest_frame"] = rest
rep["stage4b_posed_frame"] = posed

# does the rest frame equal the published joint frame JSON?
jf = json.load(open(JOINT_FRAME, encoding="utf-8"))
rep["published_frame_matches_rest_max_mm"] = round(max(
    math.dist(jf["bones"][n]["head"], rest[n]["head"]) for n in rest) * MM, 6)
rep["published_frame_matches_posed_max_mm"] = round(max(
    math.dist(jf["bones"][n]["head"], posed[n]["head"]) for n in rest) * MM, 6)

# ---------- B. current approved master: joint regions ----------
bpy.ops.wm.open_mainfile(filepath=MASTER)
obj = bpy.data.objects["Hand  - Realistic"]
me = obj.data
MW = obj.matrix_world
V = [MW @ v.co for v in me.vertices]
nail = json.load(open(NAIL_AUDIT, encoding="utf-8"))


def centroid(pts):
    n = len(pts)
    return [sum(p[i] for p in pts) / n for i in range(3)]


nail_centroid = {}
for d in DIGITS:
    nail_centroid[d] = centroid([V[me.polygons[fi].vertices[0]] for fi in nail["per_digit_faces"][d]])
rep["nail_centroid_current_mesh"] = nail_centroid

DISTAL = {"thumb": "IP", "index": "DIP", "middle": "DIP", "ring": "DIP", "little": "DIP"}
cmp = {}
for d in DIGITS:
    key = f"{d.upper()}_{DISTAL[d]}_R"
    cmp[key] = {
        "dist_rest_head_to_own_nail_centroid_mm": round(math.dist(jf["bones"][key]["head"], nail_centroid[d]) * MM, 3),
        "dist_posed_head_to_own_nail_centroid_mm": round(math.dist(posed[key]["head"], nail_centroid[d]) * MM, 3),
    }
rep["distal_joint_vs_current_nail_centroid"] = cmp


def closest(p):
    pl = MW.inverted() @ __import__("mathutils").Vector(p)
    ok, loc, nor, idx = obj.closest_point_on_mesh(pl)
    if not ok:
        return None
    wl = MW @ loc
    wn = (MW.to_3x3() @ nor).normalized()
    return [float(x) for x in wl], [float(x) for x in wn]


inside = {}
for frame_name, frame in (("rest_frame", jf["bones"]), ("posed_frame", posed)):
    per = {}
    for d in DIGITS:
        key = f"{d.upper()}_{DISTAL[d]}_R"
        p = frame[key]["head"]
        r = closest(p)
        wl, wn = r
        off = sum((p[i] - wl[i]) * wn[i] for i in range(3))
        per[key] = {"nearest_surface_mm": round(math.dist(p, wl) * MM, 3),
                    "inside": bool(off < 0), "signed_mm": round(off * MM, 3)}
    inside[frame_name] = per
rep["distal_joint_inside_current_mesh"] = inside

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(rep, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("OUT=" + OUT)
print("published matches REST  max mm:", rep["published_frame_matches_rest_max_mm"])
print("published matches POSED max mm:", rep["published_frame_matches_posed_max_mm"])
