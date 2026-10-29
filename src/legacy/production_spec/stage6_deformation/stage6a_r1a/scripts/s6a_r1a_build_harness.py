# =====================================================================================
# STAGE6A_R1A -- build the deterministic deformation test harness from the R1B candidate
# =====================================================================================
# INPUT  (frozen, never modified): stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend
#          sha256 c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6
#          -> remains the Stage5B FINAL_APPROVED master; its freeze receipt is NOT touched
# INPUT  (candidate):              stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend
# OUTPUT (new, TEST HARNESS COPY): stage6_deformation/stage6a_r1a/
#                                    RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend
#
# The harness adds ONLY a diagnostic collection with test cameras + lights, created with the
# SAME deterministic recipe as the Stage6A R1 harness so that before/after renders share an
# identical camera, scale, lighting, material and angle.
# No weight / geometry / topology / bone / parent / modifier change.
# Saved with ALL POSE BONES RESET (zero / RSSF bind).
# =====================================================================================
import bpy
import sys
import os
import json
import hashlib
import datetime
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
PROD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
S5 = os.path.join(PROD, "stage5_production_rig")
sys.path.append(os.path.join(S5, "stage5b_r1b", "scripts"))
import r1b_common as C                                          # noqa: E402
RC = C.RC
S6 = C.S6

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
NOW = datetime.datetime.now().astimezone().isoformat()
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[S6A-R1A-BUILD]", s, flush=True)


def sha(p):
    return C.sha256(p)


R1B_STATUS = os.path.join(S5, "stage5b_r1b", "STAGE5B_R1B_STATUS.json")
st = json.load(open(R1B_STATUS, encoding="utf-8"))
R1B = st["output_r1b"]["path"].replace("/", os.sep)
R1B_SHA = st["output_r1b"]["sha256"]
HARNESS = os.path.join(OUTDIR, "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend")
R1_HARNESS = os.path.join(PROD, "stage6_deformation", "stage6a",
                          "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend")

# ---------------------------------------------------------------- input gates
s_r1a = sha(C.R1A_MASTER)
s_r1b = sha(R1B)
log("Stage5B R1A master  %s" % s_r1a)
log("Stage5B R1B candidate %s" % s_r1b)
if s_r1a != C.R1A_SHA256:
    raise SystemExit("FAIL CLOSED: Stage5B R1A provenance hash drift")
if s_r1b != R1B_SHA:
    raise SystemExit("FAIL CLOSED: R1B candidate hash does not match its status")
if st["status"] != "CANDIDATE_FOR_HUMAN_REVIEW":
    raise SystemExit("FAIL CLOSED: R1B is not in the expected candidate state")
freeze = json.load(open(os.path.join(S5, "stage5b_freeze",
                                     "STAGE5B_HUMAN_APPROVAL_FREEZE_R1.json"),
                        encoding="utf-8"))
freeze_untouched = freeze["active_stage5b_master"]["sha256"] == s_r1a
log("Stage5B freeze receipt still binds R1A as FINAL_APPROVED: %s (receipt NOT modified)"
    % freeze_untouched)
if not freeze_untouched:
    raise SystemExit("FAIL CLOSED: the Stage5B freeze receipt no longer binds R1A")

# ---------------------------------------------------------------- reference + open R1B
Ctx = C.build_context()
V0 = Ctx["V0"]
NV = Ctx["NV"]
ref = Ctx["ref"]
bpy.ops.wm.open_mainfile(filepath=R1B)
ob = bpy.data.objects["Hand  - Realistic"]
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
me = ob.data
MW = ob.matrix_world.copy()
h = {"ob": ob, "rig": rig, "me": me, "MW": MW, "NV": len(me.vertices),
     "POLY": [tuple(p.vertices) for p in me.polygons],
     "UV": ([tuple(round(u, 9) for u in d.uv) for d in me.uv_layers.active.data]
            if me.uv_layers.active else []),
     "MAT": [p.material_index for p in me.polygons],
     "E": len(me.edges), "F": len(me.polygons),
     "TRIS": sum(len(p.vertices) - 2 for p in me.polygons),
     "groups": sorted(g.name for g in ob.vertex_groups),
     "parent": ob.parent.name if ob.parent else None,
     "mods": [(m.name, m.type, (m.object.name if getattr(m, "object", None) else None))
              for m in ob.modifiers]}

GATES = {}
GATES["bone_count_21"] = len(rig.data.bones) == 21
GATES["tip_helpers_5"] = sorted(b.name for b in rig.data.bones
                                if not b.use_deform) == sorted(
    "%s_TIP_R" % d for d in RC.DIGITS)
GATES["deform_bones_16"] = len([b for b in rig.data.bones if b.use_deform]) == 16
GATES["deform_groups_16"] = len(h["groups"]) == 16 and sorted(h["groups"]) == \
    sorted(C.ALL_DEFORM)
GATES["armature_modifier"] = any(m[0] == "PRODUCTION_ARMATURE" and m[1] == "ARMATURE" and
                                 m[2] == "RIGHT_HAND_PRODUCTION_RIG" for m in h["mods"])
GATES["parent_binding"] = h["parent"] == "RIGHT_HAND_PRODUCTION_RIG"
GATES["topology_3416_6828_3414_6828"] = (h["NV"], h["E"], h["F"], h["TRIS"]) == \
    (3416, 6828, 3414, 6828)
GATES["topology_identical_to_reference"] = h["POLY"] == ref["TOPO0"]
GATES["uv_identical"] = h["UV"] == ref["UV0"]
GATES["material_identical"] = h["MAT"] == ref["MAT0"]
for k, v in GATES.items():
    log("GATE %-40s %s" % (k, "PASS" if v else "FAIL"))
if not all(GATES.values()):
    raise SystemExit("FAIL CLOSED: structural gate failed")

S6.reset_pose(rig)
Vb, Pb = S6.evaluate(ob, MW)
base_delta = [(Vb[i] - V0[i]).length * 1000.0 for i in range(NV)]
BASE = {"max_vertex_delta_mm": C.rr(max(base_delta)),
        "mean_vertex_delta_mm": C.rr(sum(base_delta) / NV)}
log("zero-pose baseline: max=%.9f mm mean=%.9f mm"
    % (BASE["max_vertex_delta_mm"], BASE["mean_vertex_delta_mm"]))
if BASE["max_vertex_delta_mm"] > 1e-4:
    raise SystemExit("FAIL CLOSED: zero-pose baseline exceeds 1e-4 mm")

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


own_r1a = Ctx["own_r1a"]
THUMB_SEL = [i for i in range(NV) if own_r1a[i] == "THUMB"]
THUMB_CTR = sum((V0[i] for i in THUMB_SEL), Vector()) / len(THUMB_SEL)
CTR = sum(V0, Vector()) / NV
DORS = Vector(ref["cap"]["thumb"]["approved_bone_direction"]).normalized()
T_AXIS = (Vector(ref["jf"]["THUMB_IP_R"]["head"]) -
          Vector(ref["jf"]["THUMB_CMC_R"]["head"])).normalized()
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

# ---------------------------------------------------------------- same-camera proof
CAM_SIG = {}
for nm, _l, _t, _ln in CAMS:
    o = bpy.data.objects[nm]
    CAM_SIG[nm] = {"location": [round(x, 12) for x in o.location],
                   "rotation_euler": [round(x, 12) for x in o.rotation_euler],
                   "lens": o.data.lens, "clip_start": o.data.clip_start,
                   "clip_end": o.data.clip_end}
LIGHT_SIG = {}
for nm, _k, _e, _d in LIGHTS:
    o = bpy.data.objects[nm]
    LIGHT_SIG[nm] = {"type": o.data.type, "energy": o.data.energy,
                     "rotation_euler": [round(x, 12) for x in o.rotation_euler]}

# ---------------------------------------------------------------- save with pose reset
S6.reset_pose(rig)
POSE_AT_SAVE = S6.pose_state(rig)
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

json.dump({"stage": "STAGE6A_R1A_HARNESS_BUILD", "generated_at": NOW,
           "input_r1b_candidate": {"path": R1B.replace(os.sep, "/"), "sha256": s_r1b,
                                   "status": st["status"]},
           "input_r1a_provenance": {"path": C.R1A_MASTER.replace(os.sep, "/"),
                                    "sha256": s_r1a, "unchanged": sha(C.R1A_MASTER) == s_r1a,
                                    "freeze_receipt_untouched": freeze_untouched},
           "harness": {"path": HARNESS.replace(os.sep, "/"), "sha256": H_SHA,
                       "bytes": os.path.getsize(HARNESS),
                       "final_pose": "ZERO / RSSF"},
           "structural_gates": GATES, "zero_pose_baseline": BASE,
           "materials": [m.name for m in bpy.data.materials],
           "diagnostic_cameras": CAM_SIG, "diagnostic_lights": LIGHT_SIG,
           "same_camera_recipe_as_stage6a_r1": True,
           "log": LOG},
          open(os.path.join(OUTDIR, "_tmp", "S6A_R1A_HARNESS_BUILD.json"), "w",
               encoding="utf-8"), indent=1, ensure_ascii=False)

s_r1a_after = sha(C.R1A_MASTER)
s_r1b_after = sha(R1B)
log("after: R1A unchanged=%s ; R1B unchanged=%s"
    % (s_r1a_after == s_r1a, s_r1b_after == s_r1b))
if s_r1a_after != s_r1a or s_r1b_after != s_r1b:
    raise SystemExit("FAIL CLOSED: an input changed during the harness build")
print("HARNESS_R1A_BUILD_DONE")
print("HARNESS_SHA256=%s" % H_SHA)
print("R1_HARNESS=%s" % R1_HARNESS)
