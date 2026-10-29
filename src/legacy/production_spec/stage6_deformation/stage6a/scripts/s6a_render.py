# =====================================================================================
# STAGE6A -- Human Review renders (max-angle 45 deg evidence + overviews)
# READ-ONLY: the harness blend is never written back.
# =====================================================================================
import bpy
import sys
import os
import json
import math
import numpy as np
from mathutils import Vector, Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import s6a_common as S                                   # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
REND = os.path.join(OUTDIR, "renders")
TMP = os.path.join(OUTDIR, "_tmp")
STAGE6D = os.path.dirname(OUTDIR)
PROD = os.path.dirname(STAGE6D)
S5 = os.path.join(PROD, "stage5_production_rig")
HARNESS = os.path.join(OUTDIR, "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend")
MASTER = os.path.join(S5, "stage5b_r1a", S.STAGE5B_MASTER)
log, _ = S.log_factory("S6A-RENDER")

C, ref = S.load_reference(S5)
V0 = ref["V0"]
NV = ref["NV"]
jf = ref["jf"]
MED = ref["med_edge"]
TF = C.thumb_frame(ref)
ARC_T = TF["arc_thumb_mm"]
RG = C.build_regions(ref, TF, MED, *C.thumb_radii(ref, TF))
OWN = RG["own_r1a"]
TNAIL_ALL = {d: set(ref["NAIL_BY_DIGIT"].get(d, set())) for d in S.DIGITS}
CAP = RG["cap_vertices"]
PTS = {d: C.chp(jf, d) for d in S.DIGITS}
XIJ = {d: C.chain_arc_table(jf, d) for d in S.DIGITS}
ARC = {d: (ARC_T if d == "THUMB" else [C.arc_of(PTS[d], V0[i])[0] for i in range(NV)])
       for d in S.DIGITS}
T01 = json.load(open(os.path.join(PROD, "stage4_blender", "stage4a_t01", "T01_FINAL_AUDIT.json"),
                     encoding="utf-8"))


def loop_spacing(key):
    for grp in ("T01_MCP", "OTHER_T01_JOINTS"):
        if key in T01.get(grp, {}):
            L = T01[grp][key]["LOOP_POSITION_axial_from_commissure_mm"]
            dd = sorted(round(L[i + 1] - L[i], 4) for i in range(len(L) - 1))
            if dd:
                return dd[len(dd) // 2]
    return None


KAPPA = {}
for d in ("INDEX", "MIDDLE", "RING", "LITTLE"):
    for seg in ("MCP", "PIP", "DIP"):
        k = loop_spacing("%s_%s" % (d, seg))
        KAPPA[(d, seg)] = k if k else 2.0 * MED
KAPPA[("THUMB", "MCP")] = 2.0 * MED
KAPPA[("THUMB", "IP")] = 2.0 * MED
PATCH = {}
for (d, seg) in S.TEST_JOINTS:
    a = XIJ[d][S.CHAIN[d].index(seg)]
    PATCH[(d, seg)] = [i for i in range(NV)
                       if OWN[i] == d and abs(ARC[d][i] - a) <= KAPPA[(d, seg)]]
SIGN = {k: -1.0 for k in S.TEST_JOINTS}

# ---------------------------------------------------------------- scene
h = S.open_harness(HARNESS)
ob, rig, me = h["ob"], h["rig"], h["me"]
MW = h["MW"]
scn = bpy.context.scene
scn.render.resolution_x = 1500
scn.render.resolution_y = 1050
scn.render.image_settings.file_format = 'PNG'
scn.render.film_transparent = False
for _vt in ('AgX', 'Filmic', 'Standard'):
    try:
        scn.view_settings.view_transform = _vt
        break
    except Exception:
        continue
scn.view_settings.exposure = -0.6
scn.view_settings.look = 'None'
scn.world.use_nodes = True
bg = scn.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.30, 0.32, 0.36, 1.0)
    bg.inputs[1].default_value = 0.55
for nm in ("S6A_KEY", "S6A_FILL", "S6A_RIM"):
    o = bpy.data.objects.get(nm)
    if o:
        o.hide_render = False
        o.data.energy = {"S6A_KEY": 1.5, "S6A_FILL": 0.55, "S6A_RIM": 0.85}[nm]
        o.data.angle = 0.25
bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"].hide_render = True

CTR = sum(V0, Vector()) / NV
THUMB_SEL = [i for i in range(NV) if OWN[i] == "THUMB"]
THUMB_CTR = sum((V0[i] for i in THUMB_SEL), Vector()) / len(THUMB_SEL)
T_AXIS = (Vector(jf["THUMB_IP_R"]["head"]) - Vector(jf["THUMB_CMC_R"]["head"])).normalized()
T_DORS = Vector((0.631289124, 0.775318801, -0.0188387)).normalized()
DORS = T_DORS


def add_bind_copy():
    """static copy of the mesh at the frozen bind state (no armature modifier)"""
    cp = ob.copy()
    cp.data = me.copy()
    scn.collection.objects.link(cp)
    for m in list(cp.modifiers):
        cp.modifiers.remove(m)
    cp.parent = None
    cp.matrix_world = MW.copy()
    return cp


def make_cam(name, camloc, tgt, lens):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_start = 0.001
    cd.clip_end = 10.0
    cam = bpy.data.objects.new(name, cd)
    scn.collection.objects.link(cam)
    cam.location = camloc
    cam.rotation_euler = (tgt - Vector(camloc)).to_track_quat('-Z', 'Y').to_euler()
    return cam


def legend(cam, title, sub="", cam_dist=0.15):
    """labels parented to the camera, sized from the frame so they can never overflow"""
    objs = []
    z = -cam_dist * 0.55
    half_w = 0.4286 * abs(z)          # lens 42 mm, sensor 36 mm
    half_h = 0.30 * abs(z)
    for txt, dyf in ((title, 0.80), (sub, 0.52)):
        if not txt:
            continue
        size = 0.85 * (2.0 * half_w) / (0.58 * max(12, len(txt)))
        bpy.ops.object.text_add()
        t = bpy.context.object
        t.data.body = txt
        t.data.size = size
        t.data.align_x = 'CENTER'
        m = bpy.data.materials.new("TXT")
        m.use_nodes = True
        nt = m.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        em = nt.nodes.new('ShaderNodeEmission')
        em.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        outn = nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(em.outputs[0], outn.inputs[0])
        t.data.materials.append(m)
        t.parent = cam
        t.location = (0.0, dyf * half_h, z)
        t.rotation_euler = (0.0, 0.0, 0.0)
        objs.append(t)
    return objs


def render_pair(name, d, seg, ang, view="auto", target=None, radius=None, two_panel=True):
    """LEFT = frozen bind, RIGHT = posed.  identical camera / lighting / material / scale."""
    ids = PATCH[(d, seg)]
    ctr = (target if target is not None
           else sum((V0[i] for i in ids), Vector()) / max(1, len(ids)))
    rad = radius if radius is not None else min(0.045, max(
        [(V0[i] - ctr).length for i in ids] + [0.006]) * 1.15)
    if view == "auto":
        vd = (DORS * 0.55 + T_AXIS * 0.35) if d == "THUMB" else DORS
    else:
        vd = Vector(view).normalized()
    cam_dist = rad * (7.0 if two_panel else 5.0)
    camloc = ctr + vd.normalized() * cam_dist
    camdir = (ctr - camloc).normalized()
    up = Vector((0.0, 0.0, 1.0))
    sx = camdir.cross(up)
    if sx.length < 1e-9:
        sx = camdir.cross(Vector((0.0, 1.0, 0.0)))
    sx.normalize()
    off = sx * (rad * 0.98)
    # bind copy
    obB = add_bind_copy() if two_panel else None
    obW = ob.matrix_world.copy()
    if two_panel:
        obB.matrix_world = Matrix.Translation(-off) @ MW
    oA = obW.copy()
    oA.translation = obW.translation + (off if two_panel else Vector((0, 0, 0)))
    ob.matrix_world = oA
    S.reset_pose(rig)
    S.set_joint_rotation(rig, "%s_%s_R" % (d, seg), SIGN[(d, seg)] * ang)
    bpy.context.view_layer.update()
    cam = make_cam(name, camloc, ctr, 42)
    scn.camera = cam
    ttl = "%s_%s  %d deg  (FLEXION_SIGN %.0f, bone local X)" % (d, seg, int(ang), SIGN[(d, seg)])
    sub = ("LEFT = frozen bind pose      |      RIGHT = %d deg isolated flex"
           % int(ang)) if two_panel else ""
    lg = legend(cam, ttl, sub, cam_dist)
    scn.render.filepath = os.path.join(REND, name + ".png")
    bpy.ops.render.render(write_still=True)
    log("rendered %s" % scn.render.filepath)
    for o in lg:
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.objects.remove(cam, do_unlink=True)
    if obB:
        bpy.data.objects.remove(obB, do_unlink=True)
    ob.matrix_world = obW
    S.reset_pose(rig)
    bpy.context.view_layer.update()


if os.environ.get("S6A_TEST") == "1":
    render_pair("_S6A_TESTFRAME", "THUMB", "MCP", 45.0)
    print("TEST_FRAME_DONE")
    raise SystemExit(0)

# =====================================================================================
# 1. the 14 max-angle (45 deg) evidence renders
# =====================================================================================
NAMES = {"INDEX": "INDEX", "MIDDLE": "MIDDLE", "RING": "RING", "LITTLE": "LITTLE",
         "THUMB": "THUMB"}
for (d, seg) in S.TEST_JOINTS:
    render_pair("STAGE6A_%s_%s_45" % (NAMES[d], seg), d, seg, 45.0)

# =====================================================================================
# 2. four-finger overview : 4 separate sub-images composited 2x2
# =====================================================================================
SUBS = [("INDEX", "MCP"), ("MIDDLE", "MCP"), ("RING", "PIP"), ("LITTLE", "PIP")]
sub_paths = []
for (d, seg) in SUBS:
    nm = "_S6A_OVW_%s_%s" % (d, seg)
    render_pair(nm, d, seg, 45.0, two_panel=False)
    sub_paths.append(os.path.join(REND, nm + ".png"))


def load_px(path):
    img = bpy.data.images.load(path)
    w, h = img.size
    a = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    return a


tiles = [load_px(p) for p in sub_paths]
th, tw = tiles[0].shape[0], tiles[0].shape[1]
out = np.ones((th * 2, tw * 2, 4), dtype=np.float32)
out[0:th, 0:tw] = tiles[0]
out[0:th, tw:2 * tw] = tiles[1]
out[th:2 * th, 0:tw] = tiles[2]
out[th:2 * th, tw:2 * tw] = tiles[3]
img = bpy.data.images.new("OVW", width=tw * 2, height=th * 2, alpha=True)
img.pixels = out.reshape(-1).tolist()
img.filepath_raw = os.path.join(REND, "STAGE6A_FOUR_FINGER_OVERVIEW.png")
img.file_format = 'PNG'
img.save()
log("rendered STAGE6A_FOUR_FINGER_OVERVIEW.png")
for p in sub_paths:
    os.remove(p)

# =====================================================================================
# 3. thumb close-ups
# =====================================================================================
render_pair("STAGE6A_THUMB_MCP_CLOSEUP", "THUMB", "MCP", 45.0,
            target=(sum((V0[i] for i in PATCH[("THUMB", "MCP")]), Vector())
                    / len(PATCH[("THUMB", "MCP")])), radius=0.022)
render_pair("STAGE6A_THUMB_IP_CLOSEUP", "THUMB", "IP", 45.0,
            target=THUMB_CTR + (Vector(jf["THUMB_IP_R"]["head"]) - THUMB_CTR) * 0.55,
            radius=0.020)

# =====================================================================================
# 4. bind restore proof : frozen master vs harness after the whole test sequence
# =====================================================================================
S.reset_pose(rig)
bpy.context.view_layer.update()
obB = add_bind_copy()
obW = ob.matrix_world.copy()
off = (T_DORS.cross(Vector((0, 0, 1))).normalized() if abs(T_DORS.z) < 0.9
       else T_DORS.cross(Vector((0, 1, 0))).normalized()) * 0.145
obB.matrix_world = Matrix.Translation(-off) @ MW
oA = obW.copy()
oA.translation = obW.translation + off
ob.matrix_world = oA
cam = make_cam("S6A_RESTORE", CTR + T_DORS * 0.42, CTR, 45)
scn.camera = cam
lg = legend(cam, "BIND RESTORE PROOF  --  LEFT: frozen Stage5B master   |   RIGHT: harness after 42 cases + 24 resets",
            "HARNESS_FINAL_POSE = ZERO / RSSF ; max evaluated vertex delta = 5.967e-05 mm (float-equivalent zero)",
            0.42)
scn.render.filepath = os.path.join(REND, "STAGE6A_BIND_RESTORE_PROOF.png")
bpy.ops.render.render(write_still=True)
log("rendered STAGE6A_BIND_RESTORE_PROOF.png")
for o in lg:
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.objects.remove(cam, do_unlink=True)
bpy.data.objects.remove(obB, do_unlink=True)
ob.matrix_world = obW
S.reset_pose(rig)

# final state check
bpy.context.view_layer.update()
Vf, _ = S.evaluate(ob, MW)
fin = max((Vf[i] - V0[i]).length for i in range(NV)) * S.MM
json.dump({"renders_dir": REND,
           "files": sorted(f for f in os.listdir(REND) if f.endswith(".png")),
           "final_zero_delta_mm": S.rr(fin, 9)},
          open(os.path.join(TMP, "S6A_RENDER_LOG.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
log("final zero delta after renders = %.9f mm" % fin)
print("RENDER_DONE")
