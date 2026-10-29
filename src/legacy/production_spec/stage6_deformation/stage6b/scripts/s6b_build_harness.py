# =====================================================================================
# STAGE6B -- build the opposition test harness from the frozen Stage5B R1B master
# =====================================================================================
# INPUT (frozen, never modified): stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend
#          sha256 cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10
# OUTPUT (new TEST HARNESS COPY, NOT a production master):
#          stage6b/RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1.blend
#
# The harness adds ONLY a diagnostic collection with test cameras + lights.
# No weight / geometry / topology / bone / parent / modifier change.
# Saved with ALL POSE BONES RESET (zero / RSSF bind).
# =====================================================================================
import bpy
import sys
import os
import json
import datetime
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import s6b_common as B                                          # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
NOW = datetime.datetime.now().astimezone().isoformat()
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[S6B-BUILD]", s, flush=True)


# ---------------------------------------------------------------- input gates
s_r1b = B.sha256(B.R1B_MASTER)
s_s5a = B.sha256(B.S5A_MASTER)
s_r1a = B.sha256(B.R1A_HARNESS)
log("Stage5B R1B master   %s" % s_r1b)
log("Stage5A R2A skeleton %s" % s_s5a)
log("Stage6A R1A harness  %s" % s_r1a)
for got, want, nm in ((s_r1b, B.R1B_SHA256, "R1B"), (s_s5a, B.S5A_SHA256, "Stage5A R2A"),
                      (s_r1a, B.R1A_HARNESS_SHA256, "Stage6A R1A harness")):
    if got != want:
        raise SystemExit("FAIL CLOSED: %s hash drift" % nm)

ctx = B.build_context()
V0 = ctx["V0"]
NV = ctx["NV"]
ref = ctx["ref"]
log("CMC cage patch = %d vertices (confinement %.2f mm) ; thenar=%d ; first_web=%d ; nail=%d"
    % (len(ctx["cmc_cage_patch"]), ctx["cmc_confinement_mm"], len(ctx["thenar"]),
       len(ctx["first_web"]), len(ctx["nail_thumb"])))

# ---------------------------------------------------------------- open R1B
bpy.ops.wm.open_mainfile(filepath=B.R1B_MASTER)
ob = bpy.data.objects["Hand  - Realistic"]
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
me = ob.data
MW = ob.matrix_world.copy()

GATES = {}
GATES["bone_count_21"] = len(rig.data.bones) == 21
GATES["deform_bones_16"] = len([b for b in rig.data.bones if b.use_deform]) == 16
GATES["tip_helpers_5"] = sorted(b.name for b in rig.data.bones
                                if not b.use_deform) == sorted(
    "%s_TIP_R" % d for d in B.RC.DIGITS)
GATES["deform_groups_16"] = sorted(g.name for g in ob.vertex_groups) == sorted(B.RB.ALL_DEFORM)
GATES["topology_3416_6828_3414"] = (len(me.vertices), len(me.edges), len(me.polygons)) == \
    (3416, 6828, 3414)
GATES["topology_identical_to_reference"] = \
    [tuple(p.vertices) for p in me.polygons] == ref["TOPO0"]
GATES["uv_identical"] = ([tuple(round(u, 9) for u in d.uv) for d in me.uv_layers.active.data]
                         if me.uv_layers.active else []) == ref["UV0"]
GATES["material_identical"] = [p.material_index for p in me.polygons] == ref["MAT0"]
GATES["parent_binding"] = ob.parent is not None and \
    ob.parent.name == "RIGHT_HAND_PRODUCTION_RIG"
GATES["armature_modifier"] = any(m.type == 'ARMATURE' and m.object is not None and
                                 m.object.name == "RIGHT_HAND_PRODUCTION_RIG"
                                 for m in ob.modifiers)
for k, v in GATES.items():
    log("GATE %-38s %s" % (k, "PASS" if v else "FAIL"))
if not all(GATES.values()):
    raise SystemExit("FAIL CLOSED: structural gate failed")

B.reset_pose(rig)
B.update()
Vb, _ = B.evaluate(ob, MW)
zd = [(Vb[i] - V0[i]).length * 1000.0 for i in range(NV)]
log("zero-pose baseline max = %.9f mm" % max(zd))
if max(zd) > 1e-4:
    raise SystemExit("FAIL CLOSED: zero-pose baseline exceeds 1e-4 mm")

# ---------------------------------------------------------------- diagnostic collection
DC = bpy.data.collections.get("STAGE6B_DIAGNOSTIC")
if DC is None:
    DC = bpy.data.collections.new("STAGE6B_DIAGNOSTIC")
    bpy.context.scene.collection.children.link(DC)


def new_cam(name, loc, target, lens):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_start = 0.001
    cd.clip_end = 10.0
    cam = bpy.data.objects.new(name, cd)
    DC.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return cam


own = ctx["own_r1a"]
thumb_sel = [i for i in range(NV) if own[i] == "THUMB"]
THUMB_CTR = sum((V0[i] for i in thumb_sel), Vector()) / len(thumb_sel)
CTR = sum(V0, Vector()) / NV
T_DORS = Vector((0.631289124, 0.775318801, -0.0188387)).normalized()
T_AXIS = (Vector(ref["jf"]["THUMB_IP_R"]["head"]) -
          Vector(ref["jf"]["THUMB_CMC_R"]["head"])).normalized()
LAT = T_AXIS.cross(T_DORS).normalized()
if LAT.y > 0:
    LAT = -LAT
CMC_C = ctx["cmc_centre"]
THENAR_C = sum((V0[i] for i in sorted(ctx["thenar"])), Vector()) / len(ctx["thenar"])
WEB_C = sum((V0[i] for i in sorted(ctx["first_web"])), Vector()) / len(ctx["first_web"])
# thumb-index nearest approach at bind (the contact region the opposition path drives into)
idx_sel = [i for i in range(NV) if own[i] == "INDEX"]
best = (1e9, None, None)
for i in thumb_sel:
    for j in idx_sel:
        d = (V0[i] - V0[j]).length
        if d < best[0]:
            best = (d, i, j)
CONTACT_C = (V0[best[1]] + V0[best[2]]) * 0.5
log("thumb-index nearest bind distance = %.3f mm between v%d / v%d"
    % (best[0] * 1000.0, best[1], best[2]))

CAMS = [
    ("S6B_CAM_DORSAL", CTR + T_DORS * 0.26, CTR, 45),
    ("S6B_CAM_PALMAR", CTR - T_DORS * 0.26, CTR, 45),
    ("S6B_CAM_THUMB_CLOSEUP", THUMB_CTR + (T_DORS + 0.2 * T_AXIS) * 0.115, THUMB_CTR, 55),
    ("S6B_CAM_SIDE", CTR + LAT * 0.24 + 0.05 * T_DORS, CTR, 55),
    ("S6B_CAM_CMC_CLOSEUP", CMC_C + (T_DORS + 0.45 * ctx["first_metacarpal_axis"]) * 0.085,
     CMC_C, 60),
    # thenar eminence sits on the palmar-radial side of the palm base
    ("S6B_CAM_THENAR_CLOSEUP",
     THENAR_C + (B.PALMAR * 0.75 + B.RADIAL * 0.45).normalized() * 0.10, THENAR_C, 55),
    ("S6B_CAM_WEB_CLOSEUP", WEB_C + (T_DORS - 0.35 * LAT) * 0.085, WEB_C, 60),
    ("S6B_CAM_CONTACT_CLOSEUP", CONTACT_C + (T_DORS + 0.30 * LAT) * 0.075, CONTACT_C, 60),
    ("S6B_CAM_TRAJECTORY", CTR + T_DORS * 0.30 - Vector((0.0, 0.0, 0.06)), CTR, 40),
]
for nm, loc, tgt, lens in CAMS:
    if nm not in bpy.data.objects:
        new_cam(nm, loc, tgt, lens)
log("diagnostic cameras (%d): %s" % (len(CAMS), [c[0] for c in CAMS]))

LIGHTS = [("S6B_KEY", 'SUN', 4.0, (0.6, 0.5, -0.6)),
          ("S6B_FILL", 'SUN', 1.8, (-0.7, 0.35, -0.5)),
          ("S6B_RIM", 'SUN', 2.4, (0.1, -0.9, -0.4))]
for nm, kind, energy, d in LIGHTS:
    if nm not in bpy.data.objects:
        lt = bpy.data.lights.new(nm, kind)
        lt.energy = energy
        o = bpy.data.objects.new(nm, lt)
        DC.objects.link(o)
        o.rotation_euler = Vector(d).normalized().to_track_quat('-Z', 'Y').to_euler()
log("diagnostic lights: %s" % [l[0] for l in LIGHTS])

scn = bpy.context.scene
scn.render.resolution_x = 1000
scn.render.resolution_y = 700
scn.render.image_settings.file_format = 'PNG'
scn.view_settings.view_transform = 'Standard'
scn.camera = bpy.data.objects["S6B_CAM_DORSAL"]

CAM_SIG = {}
for nm, _l, _t, _ln in CAMS:
    o = bpy.data.objects[nm]
    CAM_SIG[nm] = {"location": [round(float(x), 12) for x in o.location],
                   "rotation_euler": [round(float(x), 12) for x in o.rotation_euler],
                   "lens": float(o.data.lens)}
LIGHT_SIG = {}
for nm, _k, _e, _d in LIGHTS:
    o = bpy.data.objects[nm]
    LIGHT_SIG[nm] = {"type": o.data.type, "energy": float(o.data.energy),
                     "rotation_euler": [round(float(x), 9) for x in o.rotation_euler]}

# ---------------------------------------------------------------- save at bind
B.reset_pose(rig)
POSE = B.S6.pose_state(rig)
NON_ID = [k for k, v in POSE.items()
          if v["quat"] != [1.0, 0.0, 0.0, 0.0] or v["loc"] != [0.0, 0.0, 0.0]
          or v["scale"] != [1.0, 1.0, 1.0]]
if NON_ID:
    raise SystemExit("FAIL CLOSED: pose not at bind at save time: %s" % NON_ID)

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=B.HARNESS_R1, copy=True, compress=False)
H_SHA = B.sha256(B.HARNESS_R1)
log("saved harness %s" % B.HARNESS_R1)
log("harness sha256 = %s" % H_SHA)

json.dump({
    "stage": "STAGE6B_HARNESS_BUILD", "generated_at": NOW,
    "input_master": {"path": B.R1B_MASTER.replace(os.sep, "/"), "sha256": s_r1b},
    "frozen_provenance": {
        "stage5a_r2a_skeleton": {"sha256": s_s5a, "unchanged": B.sha256(B.S5A_MASTER) == s_s5a},
        "stage6a_r1a_harness": {"sha256": s_r1a,
                                "unchanged": B.sha256(B.R1A_HARNESS) == s_r1a},
    },
    "harness": {"path": B.HARNESS_R1.replace(os.sep, "/"), "sha256": H_SHA,
                "bytes": os.path.getsize(B.HARNESS_R1),
                "role": "TEST HARNESS COPY - NOT a production master",
                "final_pose": "ZERO / RSSF"},
    "structural_gates": GATES,
    "zero_pose_baseline_max_mm": B.rr(max(zd)),
    "cmc_cage_authority": ctx["cmc_cage_audit"],
    "cmc_cage_patch_vertex_count": len(ctx["cmc_cage_patch"]),
    "diagnostic_cameras": CAM_SIG, "diagnostic_lights": LIGHT_SIG,
    "thumb_index_bind_nearest": {"distance_mm": B.rr(best[0] * 1000.0, 6),
                                 "thumb_vertex": best[1], "index_vertex": best[2]},
    "log": LOG,
}, open(os.path.join(OUTDIR, "_tmp", "S6B_HARNESS_BUILD.json"), "w", encoding="utf-8"),
    indent=1, ensure_ascii=False)

for nm, pth in (("R1B", B.R1B_MASTER), ("Stage5A R2A", B.S5A_MASTER),
                ("Stage6A R1A harness", B.R1A_HARNESS)):
    if B.sha256(pth) != {"R1B": s_r1b, "Stage5A R2A": s_s5a,
                         "Stage6A R1A harness": s_r1a}[nm]:
        raise SystemExit("FAIL CLOSED: %s changed during the harness build" % nm)
log("all frozen inputs unchanged after build")
print("HARNESS_S6B_BUILD_DONE")
print("HARNESS_SHA256=%s" % H_SHA)
