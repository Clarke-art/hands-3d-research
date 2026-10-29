# =====================================================================================
# STAGE5A_FREEZE -- READ-ONLY integrity verification of the R2A production rig master.
# Opens blends, collects facts, NEVER saves anything.
# =====================================================================================
import bpy, sys, os, json, math, hashlib, datetime
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
BASE = r"<HANDS_ROOT>\production_spec"
S4C = os.path.join(BASE, "stage4_blender", "stage4c_r2", "RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend")
R2A = os.path.join(BASE, "stage5_production_rig", "stage5a_r2a",
                   "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
R2B = os.path.join(BASE, "stage5_production_rig", "stage5a_r2")
NOW = datetime.datetime.now().astimezone().isoformat()
MM = 1000.0
R = {"generated_at": NOW, "runtime": {"blender": bpy.app.version_string,
                                      "executable": bpy.app.binary_path}, "read_only": True}

for tag, p in (("stage4c_master", S4C), ("stage5a_r2a", R2A)):
    R[tag + "_sha256"] = hashlib.sha256(open(p, "rb").read()).hexdigest()

EXPECT = {
    # "PRODUCTION_WRIST_R" is the SEMANTIC name of the wrist joint centre that is decoupled
    # from the asset object origin; the actual bone in the rig is WRIST_R.
    "WRIST_R": (1.406007767, 0.016420959, 0.358511657),
    "THUMB_CMC_R": (1.440895081, 0.001219887, 0.3918145),
    "THUMB_MCP_R": (1.454060912, 0.001536574, 0.436873049),
    "THUMB_IP_R": (1.450860858, 0.006127121, 0.464001149),
    "THUMB_TIP_R": (1.45281744, 0.019802358, 0.493028343),
    "INDEX_MCP_R": (1.442374706, 0.017366245, 0.483602315),
}
jt = json.load(open(os.path.join(BASE, "stage5_production_rig", "stage5a_r2",
                                 "STAGE5A_R2_PRODUCTION_JOINT_TABLE.json"), encoding="utf-8"))["joints"]

# ---------------------------------------------------------------- R2A facts
bpy.ops.wm.open_mainfile(filepath=R2A)
R["stage5a_r2a_sha256_after_open"] = hashlib.sha256(open(bpy.data.filepath, "rb").read()).hexdigest()
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
ob = bpy.data.objects["Hand  - Realistic"]
me = ob.data
MW = ob.matrix_world
V = [(MW @ v.co).copy() for v in me.vertices]

bones = {}
for b in rig.data.bones:
    bones[b.name] = {"head_world": [round(float(x), 9) for x in (rig.matrix_world @ b.head_local)],
                     "tail_world": [round(float(x), 9) for x in (rig.matrix_world @ b.tail_local)],
                     "parent": b.parent.name if b.parent else None,
                     "use_connect": bool(b.use_connect),
                     "use_deform": bool(b.use_deform),
                     "length_mm": round((b.tail_local - b.head_local).length * MM, 6),
                     "roll_rad": round(float(b.matrix_local.to_3x3().to_euler().y), 9)}
R["bone_count"] = len(bones)
R["deform_true_count"] = sum(1 for v in bones.values() if v["use_deform"])
R["deform_false_count"] = sum(1 for v in bones.values() if not v["use_deform"])
R["deform_false_bones"] = sorted(n for n, v in bones.items() if not v["use_deform"])
R["bones"] = bones

R["joint_position_check"] = {}
for n, e in EXPECT.items():
    got = bones[n]["head_world"]
    R["joint_position_check"][n] = {"expected": list(e), "measured": got,
                                    "delta_mm": round(math.dist(got, list(e)) * MM, 9)}
R["joint_position_max_delta_mm"] = max(v["delta_mm"] for v in R["joint_position_check"].values())

# local frame orthonormality + 180 flips
orth = {}
for n, b in rig.data.bones.items():
    m = b.matrix_local.to_3x3()
    X, Y, Z = m.col[0], m.col[1], m.col[2]
    orth[n] = {"max_abs_norm_err": round(max(abs(X.length - 1), abs(Y.length - 1),
                                             abs(Z.length - 1)), 9),
               "max_abs_dot": round(max(abs(X.dot(Y)), abs(Y.dot(Z)), abs(X.dot(Z))), 9),
               "handedness_err": round((X - Y.cross(Z)).length, 9)}
R["BONE_LOCAL_FRAME_ORTHONORMAL_max_norm_err"] = max(v["max_abs_norm_err"] for v in orth.values())
R["BONE_LOCAL_FRAME_ORTHONORMAL_max_dot"] = max(v["max_abs_dot"] for v in orth.values())
R["BONE_LOCAL_FRAME_ORTHONORMAL_max_handedness"] = max(v["handedness_err"] for v in orth.values())
R["BONE_LOCAL_FRAME_ORTHONORMAL"] = "PASS" if (R["BONE_LOCAL_FRAME_ORTHONORMAL_max_norm_err"] < 1e-5
                                               and R["BONE_LOCAL_FRAME_ORTHONORMAL_max_dot"] < 1e-5
                                               and R["BONE_LOCAL_FRAME_ORTHONORMAL_max_handedness"] < 1e-5) else "FAIL"
# roll continuity per chain
DORSAL = {k: Vector(v) for k, v in json.load(
    open(os.path.join(R2B, "_tmp", "S5A_R2_CANDIDATES.json"), encoding="utf-8"))["dorsal_refs"].items()}
chains = {"thumb": ["WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R", "THUMB_TIP_R"],
          "index": ["WRIST_R", "INDEX_MCP_R", "INDEX_PIP_R", "INDEX_DIP_R", "INDEX_TIP_R"],
          "middle": ["WRIST_R", "MIDDLE_MCP_R", "MIDDLE_PIP_R", "MIDDLE_DIP_R", "MIDDLE_TIP_R"],
          "ring": ["WRIST_R", "RING_MCP_R", "RING_PIP_R", "RING_DIP_R", "RING_TIP_R"],
          "little": ["WRIST_R", "LITTLE_MCP_R", "LITTLE_PIP_R", "LITTLE_DIP_R", "LITTLE_TIP_R"]}
cont = {}
for cname, seq in chains.items():
    ang = []
    for a, b in zip(seq, seq[1:]):
        m1 = rig.data.bones[a].matrix_local.to_3x3()
        m2 = rig.data.bones[b].matrix_local.to_3x3()
        z1 = m1.col[2].normalized(); z2 = m2.col[2].normalized()
        ang.append(round(math.degrees(math.acos(max(-1, min(1, z1.dot(z2))))), 4))
    cont[cname] = ang
R["roll_continuity_per_chain_deg"] = cont
R["roll_continuity_max_deg"] = max(max(v) for v in cont.values())
R["BONE_ROLL_180_FLIPS"] = sum(1 for v in cont.values() for a in v if a > 120)
R["THUMB_CHAIN_ROLL_CONTINUITY"] = "PASS" if max(cont["thumb"]) <= 60 else "FAIL"

R["rig_object"] = {"name": rig.name,
                   "location": [round(float(x), 9) for x in rig.location],
                   "rotation_euler": [round(float(x), 9) for x in rig.rotation_euler],
                   "scale": [round(float(x), 9) for x in rig.scale]}
R["mesh_object"] = {"name": ob.name, "parent": ob.parent.name if ob.parent else None,
                    "modifiers": [m.type for m in ob.modifiers],
                    "vertex_groups": [g.name for g in ob.vertex_groups]}
R["armature_modifier"] = [m.type for m in ob.modifiers if m.type == 'ARMATURE']
R["PRODUCTION_SKIN_WEIGHT"] = "NOT_STARTED"

# mesh signatures to compare against the Stage4C master
SIG = {"n_verts": len(V),
       "verts": [[round(float(x), 9) for x in p] for p in V],
       "polys": [tuple(p.vertices) for p in me.polygons],
       "uv": [tuple(round(u, 9) for u in d.uv) for d in me.uv_layers.active.data]
       if me.uv_layers.active else [],
       "mat": [p.material_index for p in me.polygons]}

# ---------------------------------------------------------------- Stage4C master comparison
bpy.ops.wm.open_mainfile(filepath=S4C)
R["stage4c_master_sha256_after_open"] = hashlib.sha256(open(bpy.data.filepath, "rb").read()).hexdigest()
ob2 = bpy.data.objects["Hand  - Realistic"]
me2 = ob2.data
MW2 = ob2.matrix_world
V2 = [(MW2 @ v.co).copy() for v in me2.vertices]
vd = max((V2[i] - Vector(SIG["verts"][i])).length for i in range(min(len(V2), len(SIG["verts"])))) * MM
R["mesh_comparison_vs_stage4c_master"] = {
    "n_verts_master": len(V2), "n_verts_r2a": SIG["n_verts"],
    "max_vertex_delta_mm": round(vd, 9),
    "topology_delta": 0 if [tuple(p.vertices) for p in me2.polygons] == SIG["polys"] else 1,
    "uv_delta": 0 if ([tuple(round(u, 9) for u in d.uv) for d in me2.uv_layers.active.data]
                      if me2.uv_layers.active else []) == SIG["uv"] else 1,
    "material_assignment_delta": 0 if [p.material_index for p in me2.polygons] == SIG["mat"] else 1,
}
json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("[FREEZE-VERIFY] bone_count=%d deform_true=%d deform_false=%d max_joint_delta=%s mm"
      % (R["bone_count"], R["deform_true_count"], R["deform_false_count"],
         R["joint_position_max_delta_mm"]))
print("[FREEZE-VERIFY] mesh vertex delta vs master = %s mm ; topo/uv/mat = %s/%s/%s"
      % (R["mesh_comparison_vs_stage4c_master"]["max_vertex_delta_mm"],
         R["mesh_comparison_vs_stage4c_master"]["topology_delta"],
         R["mesh_comparison_vs_stage4c_master"]["uv_delta"],
         R["mesh_comparison_vs_stage4c_master"]["material_assignment_delta"]))
print("FREEZE_VERIFY_DONE")
