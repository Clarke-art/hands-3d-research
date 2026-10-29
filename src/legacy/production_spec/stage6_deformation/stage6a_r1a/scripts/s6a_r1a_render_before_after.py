# =====================================================================================
# STAGE6A_R1A -- Human Review renders: same-camera BEFORE / AFTER
# =====================================================================================
# BEFORE = Stage5B R1A weights  + Stage6A R1 pose
#          (../stage6a/RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend)
# AFTER  = Stage5B R1B weights  + Stage6A R1A identical pose
#          (this dir: RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend)
#
# Both harnesses carry an identical diagnostic camera + light set (same deterministic recipe),
# and the mesh geometry / UV / material are identical, so camera, scale, lighting, material
# and angle are the same for every pair.  Nothing is ever written back to either harness.
# =====================================================================================
import bpy
import sys
import os
import json
import math
import numpy as np
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
S5B = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "..", "..", "..", "stage5_production_rig",
                                   "stage5b_r1b", "scripts"))
sys.path.append(S5B)
import s6a_common as S                                          # noqa: E402
import r1b_common as RB                                         # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
REND = os.path.join(OUTDIR, "renders")
TMP = os.path.join(OUTDIR, "_tmp")
STAGE6D = os.path.dirname(OUTDIR)
PROD = os.path.dirname(STAGE6D)
S5 = os.path.join(PROD, "stage5_production_rig")
HARNESS_AFTER = os.path.join(OUTDIR, "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend")
HARNESS_BEFORE = os.path.join(STAGE6D, "stage6a",
                              "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend")
log, LOG = S.log_factory("S6A-R1A-REND")
TILE_W, TILE_H = 900, 630
os.makedirs(TMP, exist_ok=True)

C, ref = S.load_reference(S5)
V0 = ref["V0"]
NV = ref["NV"]
jf = ref["jf"]
MED = ref["med_edge"]
POLY = ref["TOPO0"]
TF = C.thumb_frame(ref)
ARC_T = TF["arc_thumb_mm"]
RG = C.build_regions(ref, TF, MED, *C.thumb_radii(ref, TF))
OWN = RG["own_r1a"]
PTS = {d: C.chp(jf, d) for d in S.DIGITS}
XIJ = {d: C.chain_arc_table(jf, d) for d in S.DIGITS}
ARC = {d: (ARC_T if d == "THUMB" else [C.arc_of(PTS[d], V0[i])[0] for i in range(NV)])
       for d in S.DIGITS}
FACE_AREA0 = [S.face_area(V0, p) for p in POLY]
T01 = json.load(open(os.path.join(PROD, "stage4_blender", "stage4a_t01",
                                  "T01_FINAL_AUDIT.json"), encoding="utf-8"))
PATCH = {}
for (d, seg) in S.TEST_JOINTS:
    a = XIJ[d][S.CHAIN[d].index(seg)]
    k = 2.0 * MED
    if d != "THUMB":
        for grp in ("T01_MCP", "OTHER_T01_JOINTS"):
            key = "%s_%s" % (d, seg)
            if key in T01.get(grp, {}):
                pos = T01[grp][key]["LOOP_POSITION_axial_from_commissure_mm"]
                dd = sorted(round(pos[i + 1] - pos[i], 4) for i in range(len(pos) - 1))
                if dd:
                    k = dd[len(dd) // 2]
                break
    PATCH[(d, seg)] = [i for i in range(NV)
                       if OWN[i] == d and abs(ARC[d][i] - a) <= k]
SIGN = {k: -1.0 for k in S.TEST_JOINTS}
THUMB_FACES = [fi for fi in range(len(POLY)) if ref["FO"].get(fi) == "THUMB"]
BASE_INTRA = RB.intersect_pairs_subset(V0, POLY, THUMB_FACES)

# ---------------------------------------------------------------- reference metrics
R1_STRAIN = json.load(open(os.path.join(STAGE6D, "stage6a",
                                        "STAGE6A_LOCAL_STRAIN_AUDIT.json"),
                           encoding="utf-8"))["cases"]
A_STRAIN = json.load(open(os.path.join(OUTDIR, "STAGE6A_R1A_LOCAL_STRAIN_AUDIT.json"),
                          encoding="utf-8"))["cases"]
R1_SI = json.load(open(os.path.join(STAGE6D, "stage6a",
                                    "STAGE6A_SELF_INTERSECTION_AUDIT.json"),
                       encoding="utf-8"))["cases"]
A_SI = json.load(open(os.path.join(OUTDIR, "STAGE6A_R1A_SELF_INTERSECTION_AUDIT.json"),
                      encoding="utf-8"))["cases"]
CIDS = {"THUMB_IP_30": "TH_IP_30", "THUMB_IP_45": "TH_IP_45", "THUMB_MCP_45": "TH_MCP_45"}
CASES = [("THUMB", "IP", 30.0), ("THUMB", "IP", 45.0), ("THUMB", "MCP", 45.0)]


def cap(cid, key, which):
    if key == "intra":
        return (R1_SI if which == "R1" else A_SI)[cid]["intra_target_digit_pairs"]
    c = (R1_STRAIN if which == "R1" else A_STRAIN)[cid]
    if key == "min_face_area_ratio":
        return c["face_area_ratio"]["min"]
    if key == "face_area_p05":
        return c["face_area_ratio"]["dist"]["p05"]
    return c["edge_length_ratio"]["max"]


def cmp_txt(cid):
    """two short lines (kept short so the label renders large enough to read)"""
    return ["min face-area %.4f -> %.4f     p05 %.4f -> %.4f"
            % (cap(cid, "min_face_area_ratio", "R1"), cap(cid, "min_face_area_ratio", "A"),
               cap(cid, "face_area_p05", "R1"), cap(cid, "face_area_p05", "A")),
            "max stretch %.3f -> %.3f     intra-thumb pairs %d -> %d"
            % (cap(cid, "max_edge_stretch", "R1"), cap(cid, "max_edge_stretch", "A"),
               cap(cid, "intra", "R1"), cap(cid, "intra", "A"))]


# ---------------------------------------------------------------- scene
def setup_scene():
    scn = bpy.context.scene
    scn.render.resolution_x = TILE_W
    scn.render.resolution_y = TILE_H
    scn.render.image_settings.file_format = 'PNG'
    scn.render.film_transparent = False
    for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'):
        try:
            scn.render.engine = eng
            break
        except Exception:
            continue
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
    return scn


def legend(cam, lines, cam_dist):
    """camera-parented text so the label can never overflow the frame"""
    objs = []
    z = -cam_dist * 0.55
    half_w = (0.5 * 36.0 / cam.data.lens) * abs(z)
    half_h = half_w * (float(TILE_H) / float(TILE_W))
    ys = (0.90, 0.75, 0.60, 0.45, 0.30)
    for i, txt in enumerate(lines[:5]):
        if not txt:
            continue
        # Bfont glyph advance is <= 0.75 x font size, so width <= 0.75 * size * len(txt);
        # size = 2.5 * half_w / len therefore keeps every line inside the frame.
        scale = 1.00 if i == 0 else 0.88
        size = scale * 2.50 * half_w / max(16, len(txt))
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
        t.location = (0.0, ys[i] * half_h, z)
        objs.append(t)
    return objs


def strain_material(alpha_blend=False):
    m = bpy.data.materials.new("R1A_STRAIN")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    attr = nt.nodes.new('ShaderNodeAttribute')
    attr.attribute_name = "r1a_strain"
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    outn = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(attr.outputs['Color'], bsdf.inputs['Base Color'])
    if alpha_blend:
        # transparent skin so the intersecting (opaque red) faces are visible inside the mesh
        nt.links.new(attr.outputs['Alpha'], bsdf.inputs['Alpha'])
        for attrname, val in (("surface_render_method", 'BLENDED'), ("blend_method", 'BLEND')):
            try:
                setattr(m, attrname, val)
                break
            except Exception:
                continue
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = 0.78
    for nm in ("Emission Color", "Emission"):
        if nm in bsdf.inputs:
            nt.links.new(attr.outputs['Color'], bsdf.inputs[nm])
            break
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = 0.40
    nt.links.new(bsdf.outputs[0], outn.inputs[0])
    return m


GREEN = (0.30, 0.80, 0.34)
RED = (0.94, 0.10, 0.10)
BLUE = (0.16, 0.34, 0.94)


def colmap(r):
    """shared before/after colour scale: log10(ratio) / 2, clamped to +/-1"""
    if r <= 1e-12:
        return RED
    t = max(-1.0, min(1.0, math.log10(r) / 1.0))   # full red at ratio 0.1, full blue at 10
    tgt = RED if t < 0 else BLUE
    u = abs(t)
    return tuple(GREEN[i] * (1 - u) + tgt[i] * u for i in range(3))


def paint(sess, mode, data):
    me = sess.me
    if "r1a_strain" in me.color_attributes:
        me.color_attributes.remove(me.color_attributes["r1a_strain"])
    att = me.color_attributes.new(name="r1a_strain", type='FLOAT_COLOR', domain='POINT')
    base = (0.22, 0.23, 0.26)          # non-diagnostic surface: dark neutral
    cols = [base] * NV
    alpha_blend = False
    if mode == "strain":
        ratios = data["ratios"]
        dev = {v: -1.0 for v in range(NV)}
        for fi in data["faces"]:
            r = ratios[fi]
            d = 1e9 if r <= 0 else abs(math.log10(r))
            c = colmap(r)
            for v in POLY[fi]:
                if d >= dev[v]:
                    dev[v] = d
                    cols[v] = c
    else:
        alpha_blend = True
        for fi in data["faces"]:
            for v in POLY[fi]:
                cols[v] = (0.98, 0.03, 0.03)
    for i, c in enumerate(cols):
        # intersecting faces are opaque, everything else is translucent so the red shows through
        a = 1.0 if (not alpha_blend or c[0] > 0.9) else 0.16
        att.data[i].color = (c[0], c[1], c[2], a)
    mat = strain_material(alpha_blend=alpha_blend)
    me.materials.append(mat)
    idx = len(me.materials) - 1
    for p in me.polygons:
        p.material_index = idx


VIEWS = {"dorsal": ("S6A_CAM_DORSAL", 0.26), "palmar": ("S6A_CAM_PALMAR", 0.26),
         "closeup": ("S6A_CAM_THUMB_CLOSEUP", 0.115), "side": ("S6A_CAM_SIDE", 0.24)}


class Session(object):
    def __init__(self, path, tag):
        bpy.ops.wm.open_mainfile(filepath=path)
        self.tag = tag
        self.ob = bpy.data.objects["Hand  - Realistic"]
        self.rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
        self.me = self.ob.data
        self.MW = self.ob.matrix_world.copy()
        self.scn = setup_scene()
        self.orig_matindex = [p.material_index for p in self.me.polygons]
        self.camsig, self.lightsig = {}, {}
        for nm in ("S6A_CAM_DORSAL", "S6A_CAM_PALMAR", "S6A_CAM_THUMB_CLOSEUP",
                   "S6A_CAM_SIDE"):
            cam = bpy.data.objects[nm]
            self.camsig[nm] = ([round(float(x), 12) for x in cam.location],
                               [round(float(x), 12) for x in cam.rotation_euler],
                               float(cam.data.lens))
        for nm in ("S6A_KEY", "S6A_FILL", "S6A_RIM"):
            o = bpy.data.objects[nm]
            self.lightsig[nm] = (o.data.type, float(o.data.energy),
                                 [round(float(x), 9) for x in o.rotation_euler])
        self.n = 0

    def bind(self):
        S.reset_pose(self.rig)
        bpy.context.view_layer.update()

    def pose(self, d, seg, ang):
        S.reset_pose(self.rig)
        if ang:
            S.set_joint_rotation(self.rig, "%s_%s_R" % (d, seg), SIGN[(d, seg)] * ang)
        bpy.context.view_layer.update()

    def unpaint(self):
        """restore the pristine material assignment of the master (paint() overrides it)"""
        for i, p in enumerate(self.me.polygons):
            p.material_index = self.orig_matindex[i]

    def render(self, view, lines, mode=None, data=None):
        if mode:
            paint(self, mode, data)
        else:
            self.unpaint()
        camname, dist = VIEWS[view]
        cam = bpy.data.objects[camname]
        self.scn.camera = cam
        lg = legend(cam, lines, dist)
        self.n += 1
        path = os.path.join(TMP, "%s_%04d.png" % (self.tag, self.n))
        self.scn.render.filepath = path
        bpy.ops.render.render(write_still=True)
        for o in lg:
            bpy.data.objects.remove(o, do_unlink=True)
        return path

    def patch_ratios(self, d, seg):
        V, _ = S.evaluate(self.ob, self.MW)
        ids = set(PATCH[(d, seg)])
        faces = [fi for fi, p in enumerate(POLY) if any(v in ids for v in p)]
        ratios = [((S.face_area(V, POLY[fi]) / FACE_AREA0[fi]) if FACE_AREA0[fi] > 1e-18
                   else 0.0) for fi in range(len(POLY))]
        return faces, ratios

    def intra_faces(self):
        V, _ = S.evaluate(self.ob, self.MW)
        newp = RB.intersect_pairs_subset(V, POLY, THUMB_FACES) - BASE_INTRA
        fs = set()
        for a, b in newp:
            fs.add(a)
            fs.add(b)
        return sorted(fs)


def load_px(p):
    img = bpy.data.images.load(p)
    w, h = img.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    bpy.data.images.remove(img)
    return buf.reshape(h, w, 4)


def compose(rows, out_name):
    grids = [[load_px(p) for p in row] for row in rows]
    th, tw = grids[0][0].shape[0], grids[0][0].shape[1]
    nr, nc = len(grids), max(len(r) for r in grids)
    out = np.ones((th * nr, tw * nc, 4), dtype=np.float32)
    # Blender image pixel row 0 is the BOTTOM row, so place grid row 0 (BEFORE) into the LAST
    # array block, which lands at the TOP of the saved image.  Tiles are never flipped, so the
    # baked-in labels stay upright.
    for i, row in enumerate(grids):
        blk = nr - 1 - i
        for j, t in enumerate(row):
            out[blk * th:(blk + 1) * th, j * tw:(j + 1) * tw] = t
    img = bpy.data.images.new(out_name, width=tw * nc, height=th * nr, alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(out).reshape(-1))
    img.filepath_raw = os.path.join(REND, out_name)
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)
    log("rendered %s  (%d x %d)" % (out_name, tw * nc, th * nr))


# =====================================================================================
# job list -- every tile, rendered once per session (only ONE harness may be open at a time)
# =====================================================================================
TAG_B = "BEFORE  Stage5B R1A + Stage6A R1 pose"
TAG_A = "AFTER   Stage5B R1B candidate + Stage6A R1A pose"
JOBS = []


def add(img, row, col, view, pose, lines_fn, mode=None, data_fn=None):
    JOBS.append({"img": img, "row": row, "col": col, "view": view, "pose": pose,
                 "lines": lines_fn, "mode": mode, "data": data_fn})


for (d, seg, ang) in CASES:
    cid = CIDS["THUMB_%s_%d" % (seg, int(ang))]
    img = "STAGE6A_R1A_THUMB_%s_%d_BEFORE_AFTER.png" % (seg, int(ang))
    for col, view in enumerate(("dorsal", "palmar", "closeup", "side")):
        add(img, 0, col, view, (d, seg, ang),
            (lambda data=None, cid=cid, view=view, ang=ang: [
                TAG_B, "%s   %s view   %d deg flex (bone local X)" % (cid, view, int(ang))]))
        add(img, 1, col, view, (d, seg, ang),
            (lambda data=None, cid=cid, view=view, ang=ang: [
                TAG_A, "%s   %s view   identical pose, identical camera" % (cid, view)]))

for (d, seg, ang) in CASES:
    cid = CIDS["THUMB_%s_%d" % (seg, int(ang))]
    img = "STAGE6A_R1A_THUMB_%s_%d_STRAIN.png" % (seg, int(ang))
    for col, view in enumerate(("closeup", "palmar", "dorsal")):
        def dflt(sess, d=d, seg=seg):
            f, r = sess.patch_ratios(d, seg)
            return {"faces": f, "ratios": r}
        for row, tag in ((0, TAG_B), (1, TAG_A)):
            add(img, row, col, view, (d, seg, ang),
                (lambda data=None, cid=cid, tag=tag: [
                    tag + "   STRAIN MAP",
                    "green = rest area   red = compression   blue = stretch"
                    "   (colour = log10 face-area ratio, clipped at +/-1)"] + cmp_txt(cid)),
                mode="strain", data_fn=dflt)

IMG_INT = "STAGE6A_R1A_INTRA_THUMB_INTERSECTION_BEFORE_AFTER.png"
for ci, (d, seg, ang) in enumerate(CASES):
    cid = CIDS["THUMB_%s_%d" % (seg, int(ang))]

    def dfn(sess):
        fs = sess.intra_faces()
        return {"faces": fs, "n_pairs": len(fs)}

    for vi, view in enumerate(("closeup", "palmar")):
        col = ci * 2 + vi
        viewtag = "close-up" if view == "closeup" else "palmar"
        add(IMG_INT, 0, col, view, (d, seg, ang),
            (lambda data=None, cid=cid, viewtag=viewtag: [
                TAG_B + "   INTRA-THUMB INTERSECTION",
                "%s   %s view   red = new intersecting thumb-owned faces" % (cid, viewtag),
                "measured intra-thumb pair count = %d" % cap(cid, "intra", "R1")]),
            mode="intersection", data_fn=dfn)
        add(IMG_INT, 1, col, view, (d, seg, ang),
            (lambda data=None, cid=cid, viewtag=viewtag: [
                TAG_A + "   INTRA-THUMB INTERSECTION",
                "%s   %s view   red = new intersecting thumb-owned faces" % (cid, viewtag),
                "measured intra-thumb pair count = %d  (Stage6A R1 = %d)"
                % (cap(cid, "intra", "A"), cap(cid, "intra", "R1"))]),
            mode="intersection", data_fn=dfn)

FFFF = json.load(open(os.path.join(OUTDIR, "STAGE6A_R1A_FOUR_FINGER_REGRESSION.json"),
                      encoding="utf-8"))
IMG_FF = "STAGE6A_R1A_FOUR_FINGER_REGRESSION.png"
for col, dd in enumerate(("INDEX", "MIDDLE", "RING", "LITTLE")):
    add(IMG_FF, 0, col, "dorsal", (dd, "MCP", 45.0),
        (lambda data=None, dd=dd: [TAG_B + "   four-finger carry-forward",
                                   "%s_MCP   45 deg" % dd]))
    add(IMG_FF, 1, col, "dorsal", (dd, "MCP", 45.0),
        (lambda data=None, dd=dd: [TAG_A + "   four-finger carry-forward",
                                   "%s_MCP   45 deg" % dd,
                                   "max displacement delta vs R1 = %.1e mm   (36 cases, all "
                                   "four-finger vertex groups bit-identical)"
                                   % FFFF["max_target_displacement_delta_mm"]]))

zr = json.load(open(os.path.join(OUTDIR, "STAGE6A_R1A_ZERO_RESTORE_AUDIT.json"),
                    encoding="utf-8"))
IMG_BR = "STAGE6A_R1A_BIND_RESTORE_PROOF.png"
for col, view in enumerate(("dorsal", "closeup")):
    add(IMG_BR, 0, col, view, "bind",
        (lambda data=None: [TAG_B + "   bind rest pose", "no joint flex applied"]))
    add(IMG_BR, 1, col, view, "bind",
        (lambda data=None: [TAG_A + "   bind rest pose",
                  "ZERO_RESTORE = %s   max evaluated vertex delta %.9f mm   (hard gate 1e-4 mm)"
                  % (zr["ZERO_RESTORE_AFTER_EACH_CASE"], zr["max_restore_delta_mm"])]))

log("render jobs = %d tiles in %d composites"
    % (len(JOBS), len(set(j["img"] for j in JOBS))))

# =====================================================================================
# render one harness at a time, then compose
# =====================================================================================
tiles = {}
sig = {}
for tag, path in (("B", HARNESS_BEFORE), ("A", HARNESS_AFTER)):
    SESS = Session(path, "tile%s" % tag)
    sig[tag] = {"camera": SESS.camsig, "light": SESS.lightsig}
    for j in JOBS:
        if (j["row"] == 0) != (tag == "B"):
            continue
        pose = j["pose"]
        if pose == "bind":
            SESS.bind()
        else:
            SESS.pose(pose[0], pose[1], pose[2])
        data = j["data"](SESS) if j["data"] else None
        lines = j["lines"]
        lines = lines(data) if callable(lines) else lines
        p = SESS.render(j["view"], lines, mode=j["mode"], data=data)
        tiles[(j["img"], j["row"], j["col"])] = p
    log("session %s rendered" % tag)
    del SESS

if sig["B"]["camera"] != sig["A"]["camera"]:
    raise SystemExit("FAIL CLOSED: camera sets differ between the two harnesses")
if sig["B"]["light"] != sig["A"]["light"]:
    raise SystemExit("FAIL CLOSED: light sets differ between the two harnesses")
log("camera + light signatures identical across the two harnesses (verified post-render)")

order = []
for j in JOBS:
    if j["img"] not in order:
        order.append(j["img"])
for img in order:
    rows = sorted(set(j["row"] for j in JOBS if j["img"] == img))
    cols = sorted(set(j["col"] for j in JOBS if j["img"] == img))
    grid = [[tiles[(img, r, c)] for c in cols] for r in rows]
    compose(grid, img)

json.dump({"renders_dir": REND,
           "files": sorted(f for f in os.listdir(REND) if f.endswith(".png")),
           "tile_size": [TILE_W, TILE_H],
           "job_count": len(JOBS),
           "layout": {
               "*_BEFORE_AFTER.png": "row1 = BEFORE, row2 = AFTER ; cols = dorsal, palmar, "
                                     "thumb close-up, side",
               "*_STRAIN.png": "row1 = BEFORE, row2 = AFTER ; cols = thumb close-up, dorsal ; "
                               "colour = log10(face-area ratio)/2 (identical scale both rows)",
               "INTRA_THUMB_INTERSECTION": "row1 = BEFORE, row2 = AFTER ; cols = TH_IP_30, "
                                           "TH_IP_45, TH_MCP_45",
               "FOUR_FINGER_REGRESSION": "row1 = BEFORE, row2 = AFTER ; cols = INDEX, MIDDLE, "
                                         "RING, LITTLE at MCP 45 deg",
               "BIND_RESTORE_PROOF": "row1 = BEFORE, row2 = AFTER ; cols = dorsal, close-up"},
           "colour_scale": "green 0 = rest area, red <= -1 = collapse, blue >= +1 = stretch",
           "camera_set": {k: {"location": v[0], "rotation_euler": v[1], "lens": v[2]}
                          for k, v in sig["A"]["camera"].items()},
           "light_set": {k: {"type": v[0], "energy": v[1], "rotation_euler": v[2]}
                         for k, v in sig["A"]["light"].items()},
           "camera_identical_between_before_and_after": True,
           "lighting_identical_between_before_and_after": True,
           "same_scale_material_angle": True,
           "log": LOG},
          open(os.path.join(TMP, "S6A_R1A_RENDER_LOG.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("RENDER_R1A_DONE")
