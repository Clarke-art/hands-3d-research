# =====================================================================================
# STAGE6A -- build the deterministic deformation test harness
# =====================================================================================
# INPUT  (frozen, never modified): stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend
#          sha256 c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6
# OUTPUT (new, TEST HARNESS COPY - not a production master):
#          stage6_deformation/stage6a/RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend
#
# The harness adds ONLY a diagnostic collection with test cameras + lights.
# No weight / geometry / topology / bone / parent / modifier change.
# Saved with ALL POSE BONES RESET (zero / RSSF bind).
# =====================================================================================
import bpy
import sys
import os
import json
import math
import hashlib
import datetime
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import s6a_common as S                                   # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]                       # .../stage6_deformation/stage6a
STAGE6D = os.path.dirname(OUTDIR)      # .../stage6_deformation
PROD = os.path.dirname(STAGE6D)        # .../production_spec
S5 = os.path.join(PROD, "stage5_production_rig")
MASTER = os.path.join(S5, "stage5b_r1a", S.STAGE5B_MASTER)
HARNESS = os.path.join(OUTDIR, "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend")
NOW = datetime.datetime.now().astimezone().isoformat()
log, LOG = S.log_factory("S6A-BUILD")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ---------------------------------------------------------------- input gate
s_master = sha(MASTER)
log("Stage5B master sha =", s_master)
if s_master != S.STAGE5B_MASTER_SHA:
    raise SystemExit("FAIL CLOSED: Stage5B master sha256 mismatch")
freeze = json.load(open(os.path.join(S5, "stage5b_freeze", "STAGE5B_HUMAN_APPROVAL_FREEZE_R1.json"),
                        encoding="utf-8"))
if freeze["active_stage5b_master"]["sha256"] != s_master:
    raise SystemExit("FAIL CLOSED: freeze receipt sha mismatch")
if freeze["zeroth_final_state"]["STAGE5B"] != "FINAL_APPROVED":
    raise SystemExit("FAIL CLOSED: Stage5B not FINAL_APPROVED")
log("freeze receipt OK (STAGE5B = %s, STAGE6 = %s)"
    % (freeze["zeroth_final_state"]["STAGE5B"], freeze["zeroth_final_state"]["STAGE6"]))

# ---------------------------------------------------------------- reference + open master
C, ref = S.load_reference(S5)   # r1a_common expects the stage5_production_rig dir
V0 = ref["V0"]
NV = ref["NV"]
h = S.open_harness(MASTER)
ob, rig, me = h["ob"], h["rig"], h["me"]
MW = h["MW"]

# ---------------------------------------------------------------- structural gates
GATES = {}
GATES["bone_count_21"] = len(rig.data.bones) == 21
TIPH = [b.name for b in rig.data.bones if not b.use_deform]
GATES["tip_helpers_5"] = sorted(TIPH) == sorted(S.TIPBONE.values())
GATES["deform_bones_16"] = len([b for b in rig.data.bones if b.use_deform]) == 16
GATES["deform_groups_16"] = len(h["groups"]) == 16 and sorted(h["groups"]) == sorted(S.DEFORM)
GATES["tip_helper_no_group"] = not [g for g in h["groups"] if g.endswith("_TIP_R")]
GATES["armature_modifier"] = any(m[0] == "PRODUCTION_ARMATURE" and m[1] == "ARMATURE"
                                 and m[2] == "RIGHT_HAND_PRODUCTION_RIG" for m in h["mods"])
GATES["parent_binding"] = h["parent"] == "RIGHT_HAND_PRODUCTION_RIG"
GATES["topology_3416_6828_3414_6828"] = (h["NV"], h["E"], h["F"], h["TRIS"]) == (3416, 6828, 3414, 6828)
GATES["topology_identical_to_reference"] = h["POLY"] == ref["TOPO0"]
GATES["uv_identical"] = h["UV"] == ref["UV0"]
GATES["material_identical"] = h["MAT"] == ref["MAT0"]
for k, v in GATES.items():
    log("GATE %-40s %s" % (k, "PASS" if v else "FAIL"))
if not all(GATES.values()):
    raise SystemExit("FAIL CLOSED: structural gate failed")

# ---------------------------------------------------------------- zero-pose baseline
S.reset_pose(rig)
Vb, Pb = S.evaluate(ob, MW)
base_delta = [(Vb[i] - V0[i]).length * S.MM for i in range(NV)]
BASE = {"max_vertex_delta_mm": S.rr(max(base_delta), 9),
        "mean_vertex_delta_mm": S.rr(sum(base_delta) / NV, 9),
        "base_mesh_vertex_delta_mm": S.rr(max((h["V"][i] - V0[i]).length
                                              for i in range(NV)) * S.MM, 9)}
log("zero-pose baseline: max=%.9f mm mean=%.9f mm" % (BASE["max_vertex_delta_mm"],
                                                      BASE["mean_vertex_delta_mm"]))
if BASE["max_vertex_delta_mm"] > 1e-4:
    raise SystemExit("FAIL CLOSED: zero-pose baseline exceeds 1e-4 mm")

log("materials in master: %s" % [(m.name, m.use_nodes) for m in me.materials])

# ---------------------------------------------------------------- diagnostic collection
DC = bpy.data.collections.get("STAGE6A_DIAGNOSTIC")
if DC is None:
    DC = bpy.data.collections.new("STAGE6A_DIAGNOSTIC")
    bpy.context.scene.collection.children.link(DC)


def new_cam(name, loc, target, lens):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_start = 0.001
    cd.clip_end = 10.0
    cam = bpy.data.objects.new(name, cd)
    DC.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (target - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return cam


THUMB_SEL = [i for i in range(NV)
             if C.build_regions(ref, C.thumb_frame(ref), ref["med_edge"],
                                *C.thumb_radii(ref, C.thumb_frame(ref)))["own_r1a"][i] == "THUMB"]
THUMB_CTR = sum((V0[i] for i in THUMB_SEL), Vector()) / len(THUMB_SEL)
CTR = sum(V0, Vector()) / NV
DORS = Vector(ref["cap"]["thumb"]["approved_bone_direction"]).normalized()
T_AXIS = (Vector(ref["jf"]["THUMB_IP_R"]["head"]) - Vector(ref["jf"]["THUMB_CMC_R"]["head"])).normalized()
T_DORS = Vector((0.631289124, 0.775318801, -0.0188387)).normalized()
LAT = T_AXIS.cross(T_DORS).normalized()
if LAT.y > 0:
    LAT = -LAT

CAMS = [("S6A_CAM_DORSAL", CTR + T_DORS * 0.26, CTR, 45),
        ("S6A_CAM_PALMAR", CTR - T_DORS * 0.26, CTR, 45),
        ("S6A_CAM_THUMB_CLOSEUP", THUMB_CTR + (T_DORS + 0.2 * T_AXIS) * 0.115, THUMB_CTR, 55),
        ("S6A_CAM_SIDE", CTR + LAT * 0.24 + 0.05 * DORS, CTR, 55)]
for nm, loc, tgt, lens in CAMS:
    if nm not in bpy.data.objects:
        new_cam(nm, loc, tgt, lens)
log("diagnostic cameras: %s" % [c[0] for c in CAMS])

LIGHTS = [("S6A_KEY", 'SUN', 4.0, (0.6, 0.5, -0.6)),
          ("S6A_FILL", 'SUN', 1.8, (-0.7, 0.35, -0.5)),
          ("S6A_RIM", 'SUN', 2.4, (0.1, -0.9, -0.4))]
for nm, kind, energy, d in LIGHTS:
    if nm not in bpy.data.objects:
        lt = bpy.data.lights.new(nm, kind)
        lt.energy = energy
        o = bpy.data.objects.new(nm, lt)
        DC.objects.link(o)
        o.rotation_euler = Vector(d).normalized().to_track_quat('-Z', 'Y').to_euler()
log("diagnostic lights: %s" % [l[0] for l in LIGHTS])

scn = bpy.context.scene
scn.render.resolution_x = 1500
scn.render.resolution_y = 1050
scn.render.image_settings.file_format = 'PNG'
scn.view_settings.view_transform = 'Standard'
scn.camera = bpy.data.objects["S6A_CAM_DORSAL"]

# ---------------------------------------------------------------- save with pose reset
S.reset_pose(rig)
POSE_AT_SAVE = S.pose_state(rig)
NON_IDENTITY = [k for k, v in POSE_AT_SAVE.items()
                if v["quat"] != [1.0, 0.0, 0.0, 0.0] or v["loc"] != [0.0, 0.0, 0.0]
                or v["scale"] != [1.0, 1.0, 1.0]]
if NON_IDENTITY:
    raise SystemExit("FAIL CLOSED: pose not at bind at save time: %s" % NON_IDENTITY)

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=HARNESS, copy=True, compress=False)
H_SHA = sha(HARNESS)
log("saved harness: %s" % HARNESS)
log("harness sha256 = %s" % H_SHA)

# ---------------------------------------------------------------- post-save verification
bpy.ops.wm.open_mainfile(filepath=HARNESS)
ob2 = bpy.data.objects["Hand  - Realistic"]
rig2 = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
MW2 = ob2.matrix_world.copy()
POSE_AFTER = S.pose_state(rig2)
NON_ID2 = [k for k, v in POSE_AFTER.items()
           if v["quat"] != [1.0, 0.0, 0.0, 0.0] or v["loc"] != [0.0, 0.0, 0.0]
           or v["scale"] != [1.0, 1.0, 1.0]]
Vh, _ = S.evaluate(ob2, MW2)
post_delta = [(Vh[i] - V0[i]).length * S.MM for i in range(NV)]
HARNESS_STATE = {
    "HARNESS_FINAL_POSE": "ZERO / RSSF" if not NON_ID2 else "NON_ZERO",
    "non_identity_bones_after_reopen": NON_ID2,
    "post_save_zero_delta_max_mm": S.rr(max(post_delta), 9),
    "post_save_zero_delta_mean_mm": S.rr(sum(post_delta) / NV, 9),
    "mesh_objects": [o.name for o in bpy.data.objects if o.type == 'MESH'],
    "diagnostic_collection": "STAGE6A_DIAGNOSTIC" in bpy.data.collections}
log("harness final pose = %s ; post-save zero delta max = %.9f mm"
    % (HARNESS_STATE["HARNESS_FINAL_POSE"], HARNESS_STATE["post_save_zero_delta_max_mm"]))

s_master_after = sha(MASTER)
log("Stage5B master sha after =", s_master_after)
if s_master_after != S.STAGE5B_MASTER_SHA:
    raise SystemExit("FAIL CLOSED: Stage5B master changed")

json.dump({"stage": "STAGE6A_HARNESS_BUILD", "generated_at": NOW,
           "input_master": {"path": MASTER, "sha256": s_master, "unchanged_after": True},
           "harness": {"path": HARNESS, "sha256": H_SHA,
                       "bytes": os.path.getsize(HARNESS)},
           "structural_gates": GATES, "zero_pose_baseline": BASE,
           "harness_final_state": HARNESS_STATE,
           "materials": [m.name for m in bpy.data.materials],
           "diagnostic_cameras": [c[0] for c in CAMS],
           "diagnostic_lights": [l[0] for l in LIGHTS],
           "log": LOG},
          open(os.path.join(OUTDIR, "_tmp", "S6A_HARNESS_BUILD.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("HARNESS_BUILD_DONE")
