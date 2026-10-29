# =====================================================================================
# STAGE6B -- Human Review renders (12 required + 4 required close-ups)
# =====================================================================================
# before = frozen Stage5B R1B at RSSF bind ; after = the Stage6B target pose.
# Same camera / scale / lighting / material.  L1/L2/L3 always use the same camera family.
# READ-ONLY: the harness is opened, posed and reset; it is never saved.
# =====================================================================================
import bpy
import sys
import os
import json
import math
import datetime
import numpy as np
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import s6b_common as B                                          # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
REND = os.path.join(OUTDIR, "renders")
TMP = os.path.join(OUTDIR, "_tmp")
NOW = datetime.datetime.now().astimezone().isoformat()
os.makedirs(REND, exist_ok=True)
os.makedirs(TMP, exist_ok=True)
LOG = []
TILE_W, TILE_H = 900, 630


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[S6B-REND]", s, flush=True)


ctx = B.build_context()
V0 = ctx["V0"]
NV = ctx["NV"]
POLY = ctx["poly"]
EDGES = ctx["edges"]
own = ctx["own_r1a"]
FACE_AREA0 = [B.face_area(V0, p) for p in POLY]
MED = ctx["MED"]
veg = json.load(open(os.path.join(OUTDIR, "STAGE6B_OPPOSITION_VECTOR_AUDIT.json"),
                     encoding="utf-8"))
UNIT = np.array(veg["CMC_OPPOSITION_UNIT_ROTATION"]["coefficients_local_XYZ"], dtype=float)
UNIT = UNIT / np.linalg.norm(UNIT)

CAGE = sorted(ctx["cmc_cage_patch"])
THENAR = sorted(ctx["thenar"])
WEB = sorted(ctx["first_web"])
NAIL = sorted(ctx["nail_thumb"])
CAP = sorted(ctx["distal_cap"])
MCP_PATCH = sorted(i for i in ctx["thumb_own"] if abs(ctx["ARC"][i] - ctx["s_MCP"]) <= 2 * MED)
IP_PATCH = sorted(i for i in ctx["thumb_own"] if abs(ctx["ARC"][i] - ctx["s_IP"]) <= 2 * MED)
ADJ = {}
for _a, _b in EDGES:
    ADJ.setdefault(_a, set()).add(_b)
    ADJ.setdefault(_b, set()).add(_a)
FAM = {"CMC_cage": ("THUMB", "wrist"), "thenar": ("THUMB", "wrist"), "first_web": ("THUMB",),
       "thumb_MCP": ("THUMB",), "thumb_IP": ("THUMB",), "nail": ("THUMB",),
       "distal_cap": ("THUMB",)}


def dom(ids, fam):
    d = set(ids)
    for i in list(ids):
        d |= ADJ.get(i, set())
    return set(i for i in d if own[i] in fam)


DOMS = {"CMC_cage": dom(CAGE, FAM["CMC_cage"]), "thenar": dom(THENAR, FAM["thenar"]),
        "first_web": dom(WEB, FAM["first_web"]), "thumb_MCP": dom(MCP_PATCH, ("THUMB",)),
        "thumb_IP": dom(IP_PATCH, ("THUMB",)), "nail": dom(NAIL, ("THUMB",)),
        "distal_cap": dom(CAP, ("THUMB",))}
TRAJ = json.load(open(os.path.join(OUTDIR, "STAGE6B_TIP_PAD_TRAJECTORY_AUDIT.json"),
                      encoding="utf-8"))["cases"]
SEAM = json.load(open(os.path.join(OUTDIR, "STAGE6B_DIGIT_SEAM_DEFORM_AUDIT.json"),
                      encoding="utf-8"))["cases"]
CAGE_A = json.load(open(os.path.join(OUTDIR, "STAGE6B_CMC_CAGE_DEFORM_AUDIT.json"),
                        encoding="utf-8"))["cases"]
CONTACT = json.load(open(os.path.join(OUTDIR, "STAGE6B_CONTACT_PROGRESSION_AUDIT.json"),
                         encoding="utf-8"))["cases"]

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
    for vt in ('AgX', 'Filmic', 'Standard'):
        try:
            scn.view_settings.view_transform = vt
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
    for nm in ("S6B_KEY", "S6B_FILL", "S6B_RIM"):
        o = bpy.data.objects.get(nm)
        if o:
            o.hide_render = False
            o.data.energy = {"S6B_KEY": 1.5, "S6B_FILL": 0.55, "S6B_RIM": 0.85}[nm]
            o.data.angle = 0.25
    bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"].hide_render = True
    return scn


def legend(cam, lines, cam_dist):
    objs = []
    z = -cam_dist * 0.55
    half_w = (0.5 * 36.0 / cam.data.lens) * abs(z)
    half_h = half_w * (float(TILE_H) / float(TILE_W))
    ys = (0.90, 0.75, 0.60, 0.45, 0.30)
    for i, txt in enumerate(lines[:5]):
        if not txt:
            continue
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


GREEN = (0.30, 0.80, 0.34)
RED = (0.94, 0.10, 0.10)
BLUE = (0.16, 0.34, 0.94)


def colmap(r):
    if r <= 1e-12:
        return RED
    t = max(-1.0, min(1.0, math.log10(r) / 1.0))
    tgt = RED if t < 0 else BLUE
    u = abs(t)
    return tuple(GREEN[i] * (1 - u) + tgt[i] * u for i in range(3))


def strain_material(alpha_blend=False):
    m = bpy.data.materials.new("S6B_STRAIN")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    attr = nt.nodes.new('ShaderNodeAttribute')
    attr.attribute_name = "s6b_view"
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    outn = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(attr.outputs['Color'], bsdf.inputs['Base Color'])
    if alpha_blend:
        nt.links.new(attr.outputs['Alpha'], bsdf.inputs['Alpha'])
        for an, av in (("surface_render_method", 'BLENDED'), ("blend_method", 'BLEND')):
            try:
                setattr(m, an, av)
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


class Sess(object):
    def __init__(self):
        bpy.ops.wm.open_mainfile(filepath=B.HARNESS_R1)
        self.ob = bpy.data.objects["Hand  - Realistic"]
        self.rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
        self.me = self.ob.data
        self.MW = self.ob.matrix_world.copy()
        self.scn = setup_scene()
        self.orig = [p.material_index for p in self.me.polygons]
        self.n = 0
        self.cam = {k: [round(float(x), 9) for x in bpy.data.objects[k].location]
                    for k in ("S6B_CAM_DORSAL", "S6B_CAM_PALMAR", "S6B_CAM_THUMB_CLOSEUP",
                              "S6B_CAM_SIDE", "S6B_CAM_CMC_CLOSEUP",
                              "S6B_CAM_THENAR_CLOSEUP", "S6B_CAM_WEB_CLOSEUP",
                              "S6B_CAM_CONTACT_CLOSEUP", "S6B_CAM_TRAJECTORY")}

    def bind(self):
        B.reset_pose(self.rig)
        B.update()

    def pose(self, case):
        B.reset_pose(self.rig)
        if case is None:
            B.update()
            return
        q, _ = B.rotation_vector_to_quaternion(Vector(UNIT) * math.radians(case[0]))
        pb = self.rig.pose.bones["THUMB_CMC_R"]
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = q
        if case[1]:
            B.set_local_axis_rotation(self.rig, "THUMB_MCP_R", -case[1])
        if case[2]:
            B.set_local_axis_rotation(self.rig, "THUMB_IP_R", -case[2])
        B.update()

    def unpaint(self):
        for i, p in enumerate(self.me.polygons):
            p.material_index = self.orig[i]

    def paint(self, mode, data):
        if "s6b_view" in self.me.color_attributes:
            self.me.color_attributes.remove(self.me.color_attributes["s6b_view"])
        att = self.me.color_attributes.new(name="s6b_view", type='FLOAT_COLOR',
                                           domain='POINT')
        cols = [(0.22, 0.23, 0.26)] * NV
        alpha_blend = (mode == "intersection")
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
        elif mode == "intersection":
            for fi in data["faces"]:
                for v in POLY[fi]:
                    cols[v] = (0.98, 0.03, 0.03)
        for i, c in enumerate(cols):
            a = 1.0 if (not alpha_blend or c[0] > 0.9) else 0.16
            att.data[i].color = (c[0], c[1], c[2], a)
        mat = strain_material(alpha_blend=alpha_blend)
        self.me.materials.append(mat)
        idx = len(self.me.materials) - 1
        for p in self.me.polygons:
            p.material_index = idx

    def render(self, camname, dist, lines, mode=None, data=None):
        if mode:
            self.paint(mode, data)
        else:
            self.unpaint()
        cam = bpy.data.objects[camname]
        self.scn.camera = cam
        lg = legend(cam, lines, dist)
        self.n += 1
        path = os.path.join(TMP, "s6btile_%04d.png" % self.n)
        self.scn.render.filepath = path
        bpy.ops.render.render(write_still=True)
        for o in lg:
            bpy.data.objects.remove(o, do_unlink=True)
        return path

    def eval_V(self):
        V, _ = B.evaluate(self.ob, self.MW)
        return V

    def strain_data(self, region):
        V = self.eval_V()
        ids = DOMS[region]
        faces = [fi for fi, p in enumerate(POLY) if all(v in ids for v in p)]
        ratios = [((B.face_area(V, POLY[fi]) / FACE_AREA0[fi]) if FACE_AREA0[fi] > 1e-18
                   else 0.0) for fi in range(len(POLY))]
        return {"faces": faces, "ratios": ratios}

    def intra_faces(self):
        V = self.eval_V()
        tf = [fi for fi in range(len(POLY)) if ctx["FO"].get(fi) == "THUMB"]
        newp = B.intersect_pairs_subset(V, POLY, tf) - B.intersect_pairs_subset(V0, POLY, tf)
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
    grids = [[load_px(p) for p in r] for r in rows]
    th, tw = grids[0][0].shape[0], grids[0][0].shape[1]
    nr, nc = len(grids), max(len(r) for r in grids)
    out = np.ones((th * nr, tw * nc, 4), dtype=np.float32)
    for i, row in enumerate(grids):
        blk = nr - 1 - i          # Blender pixel row 0 is the BOTTOM row
        for j, t in enumerate(row):
            out[blk * th:(blk + 1) * th, j * tw:(j + 1) * tw] = t
    img = bpy.data.images.new(out_name, width=tw * nc, height=th * nr, alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(out).reshape(-1))
    img.filepath_raw = os.path.join(REND, out_name)
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)
    log("rendered %s (%d x %d)" % (out_name, tw * nc, th * nr))


S = Sess()
log("cameras: %s" % json.dumps(S.cam))
BEFORE = "BEFORE  frozen Stage5B R1B @ RSSF bind"
AFTER30 = "AFTER   CMC opposition 30 deg (diagnostic)"
VIEWS = {"dorsal": ("S6B_CAM_DORSAL", 0.26), "palmar": ("S6B_CAM_PALMAR", 0.26),
         "closeup": ("S6B_CAM_THUMB_CLOSEUP", 0.115), "side": ("S6B_CAM_SIDE", 0.24),
         "cmc": ("S6B_CAM_CMC_CLOSEUP", 0.085), "thenar": ("S6B_CAM_THENAR_CLOSEUP", 0.10),
         "web": ("S6B_CAM_WEB_CLOSEUP", 0.085),
         "contact": ("S6B_CAM_CONTACT_CLOSEUP", 0.075),
         "traj": ("S6B_CAM_TRAJECTORY", 0.30)}
C30 = (30.0, 0.0, 0.0)
CML3 = (30.0, 30.0, 0.0)
FL3 = (30.0, 30.0, 15.0)
LEVELS = [("L1", (10.0, 10.0, 5.0)), ("L2", (20.0, 20.0, 10.0)), ("L3", FL3)]
OPP = [("10deg", (10.0, 0.0, 0.0)), ("20deg", (20.0, 0.0, 0.0)), ("30deg", C30)]


def seamline(cid):
    s = SEAM[cid]
    return ("thumb|index seam: %d/%d edges torn (>3x & >5mm) ; worst %.3f -> %.3f mm (x%.1f)"
            % (s["edges_over_3x_and_over_5mm"], s["thumb_index_seam_edge_count"],
               s["worst_edges"][0]["bind_mm"], s["worst_edges"][0]["posed_mm"],
               s["max_stretch_ratio"]))


# ---- 1 CMC_OPP_30 before/after, 4 views
rowB, rowA = [], []
for view in ("dorsal", "palmar", "closeup", "side"):
    cn, d = VIEWS[view]
    S.bind()
    rowB.append(S.render(cn, d, [BEFORE, "CMC_OPP_30   %s view" % view]))
    S.pose(C30)
    rowA.append(S.render(cn, d, [AFTER30, "CMC_OPP_30   %s view   same camera" % view,
                                 seamline("CMC_OPP_30")]))
compose([rowB, rowA], "STAGE6B_CMC_OPP_30_BEFORE_AFTER.png")

# ---- 2 CMC_OPP_30 CMC cage strain
rowB, rowA = [], []
for view in ("cmc", "side"):
    cn, d = VIEWS[view]
    S.bind()
    rowB.append(S.render(cn, d, [BEFORE + "   CMC CAGE STRAIN",
                                 "green=rest  red=compression  blue=stretch "
                                 "(log10 face-area ratio)"],
                         mode="strain", data=S.strain_data("CMC_cage")))
    S.pose(C30)
    c = CAGE_A["CMC_OPP_30"]["strain"]
    rowA.append(S.render(cn, d, [AFTER30 + "   CMC CAGE STRAIN",
                                 "green=rest  red=compression  blue=stretch",
                                 "min face-area %.4f  min edge %.4f  fold-over %d  new pairs %d"
                                 % (c["min_face_area_ratio"], c["min_edge_ratio"],
                                    CAGE_A["CMC_OPP_30"][
                                        "fold_over_face_count_normal_dot_lt_-0.5"],
                                    CAGE_A["CMC_OPP_30"][
                                        "new_self_intersection_pairs_within_cage"])],
                         mode="strain", data=S.strain_data("CMC_cage")))
compose([rowB, rowA], "STAGE6B_CMC_OPP_30_CMC_CAGE_STRAIN.png")

# ---- 3 CMC_MCP_L3 before/after
rowB, rowA = [], []
for view in ("dorsal", "palmar", "closeup", "side"):
    cn, d = VIEWS[view]
    S.bind()
    rowB.append(S.render(cn, d, [BEFORE, "CMC_MCP_L3   %s view" % view]))
    S.pose(CML3)
    rowA.append(S.render(cn, d, ["AFTER   CMC 30 + MCP 30 (diagnostic)",
                                 "CMC_MCP_L3   %s view   same camera" % view,
                                 seamline("CMC_MCP_L3")]))
compose([rowB, rowA], "STAGE6B_CMC_MCP_L3_BEFORE_AFTER.png")

# ---- 4/5/6 FULL_OPP L1/L2/L3
for nm, case in LEVELS:
    rowB, rowA = [], []
    for view in ("closeup", "palmar", "side"):
        cn, d = VIEWS[view]
        S.bind()
        rowB.append(S.render(cn, d, [BEFORE, "FULL_OPP_%s   %s view" % (nm, view)]))
        S.pose(case)
        rowA.append(S.render(cn, d, ["AFTER   CMC %d + MCP %d + IP %d (diagnostic)"
                                     % (case[0], case[1], case[2]),
                                     "FULL_OPP_%s   %s view   same camera family"
                                     % (nm, view)]))
    compose([rowB, rowA], "STAGE6B_FULL_OPP_%s.png" % nm)

# ---- 7 first web L1/L2/L3
rowB, rowA = [], []
for nm, case in LEVELS:
    cn, d = VIEWS["web"]
    S.bind()
    rowB.append(S.render(cn, d, [BEFORE, "first web   %s" % nm]))
    S.pose(case)
    w = json.load(open(os.path.join(OUTDIR, "STAGE6B_FIRST_WEB_DEFORM_AUDIT.json"),
                       encoding="utf-8"))["cases"]["FULL_OPP_%s" % nm]
    rowA.append(S.render(cn, d, ["AFTER   FULL_OPP_%s" % nm,
                                 "opening area ratio vs bind = %.4f"
                                 % w["web_opening_area_ratio_vs_bind"],
                                 "no tear: degenerate faces %d, new self-intersection %d"
                                 % (w["degenerate_face_count"],
                                    w["new_self_intersection_pairs_within_web"])]))
compose([rowB, rowA], "STAGE6B_FIRST_WEB_L1_L2_L3.png")

# ---- 8 thenar L1/L2/L3
rowB, rowA = [], []
TH = json.load(open(os.path.join(OUTDIR, "STAGE6B_THENAR_DEFORM_AUDIT.json"),
                    encoding="utf-8"))["cases"]
for nm, case in LEVELS:
    cn, d = VIEWS["thenar"]
    S.bind()
    rowB.append(S.render(cn, d, [BEFORE, "thenar   %s" % nm]))
    S.pose(case)
    t = TH["FULL_OPP_%s" % nm]
    rowA.append(S.render(cn, d, ["AFTER   FULL_OPP_%s" % nm,
                                 "bbox volume ratio %.4f   surface-area ratio %.4f"
                                 % (t["pca_bbox_volume_ratio_vs_bind"],
                                    t["local_surface_area_ratio"])]))
compose([rowB, rowA], "STAGE6B_THENAR_L1_L2_L3.png")

# ---- 9 contact progression (bind + L1/L2/L3), plain + intersection highlight
rowP, rowI = [], []
cn, d = VIEWS["contact"]
S.bind()
rowP.append(S.render(cn, d, [BEFORE, "thumb-index contact region"]))
fs = S.intra_faces()
rowI.append(S.render(cn, d, [BEFORE + "   INTERSECTION",
                             "red = new intra-thumb intersecting faces (none at bind)"],
                     mode="intersection", data={"faces": fs}))
for nm, case in LEVELS:
    S.pose(case)
    ct = CONTACT["FULL_OPP_%s" % nm]
    rowP.append(S.render(cn, d,
                         ["AFTER   FULL_OPP_%s" % nm,
                          "thumb-index pairs %d   thumb-palm pairs %d"
                          % (ct["counts"]["B_THUMB_INDEX"], ct["counts"]["C_THUMB_PALM"]),
                          "max penetration proxy %.4f mm"
                          % ct["max_penetration_proxy_mm"]]))
    fs = S.intra_faces()
    rowI.append(S.render(cn, d,
                         ["AFTER   FULL_OPP_%s  INTERSECTION" % nm,
                          "red = new intra-thumb intersecting faces",
                          "thumb-index pairs %d" % ct["counts"]["B_THUMB_INDEX"]],
                         mode="intersection", data={"faces": fs}))
compose([rowP, rowI], "STAGE6B_CONTACT_PROGRESSION.png")

# ---- 10 distal cap / nail at L3
rowB, rowA = [], []
for view in ("closeup", "side"):
    cn, d = VIEWS[view]
    S.bind()
    rowB.append(S.render(cn, d, [BEFORE, "distal cap / nail   %s view" % view]))
    S.pose(FL3)
    nd = json.load(open(os.path.join(OUTDIR, "STAGE6B_NAIL_DISTAL_CAP_AUDIT.json"),
                        encoding="utf-8"))["cases"]["FULL_OPP_L3"]
    rowA.append(S.render(cn, d, ["AFTER   FULL_OPP_L3   distal cap / nail",
                                 "nail area %.5f  cap area %.5f" % (nd["nail_area_ratio"],
                                                                    nd["distal_cap_area_ratio"]),
                                 "nail rigid residual %.5f mm (rel %.5f) - no detachment"
                                 % (nd["nail_rigid_fit_residual_mm"],
                                    nd["nail_rigid_fit_relative_residual"])]))
compose([rowB, rowA], "STAGE6B_DISTAL_CAP_NAIL_L3.png")

# ---- 11 tip trajectory
rowP = []
cn, d = VIEWS["traj"]
S.bind()
rowP.append(S.render(cn, d, [BEFORE, "thumb TIP landmark at bind"]))
for nm, case in LEVELS:
    S.pose(case)
    t = TRAJ["FULL_OPP_%s" % nm]
    rowP.append(S.render(cn, d, ["AFTER   FULL_OPP_%s" % nm,
                                 "tip |d| %.2f mm   along T_OPPOSE %+.2f mm"
                                 % (t["displacement_magnitude_mm"],
                                    t["T_OPPOSE_component_mm"]),
                                 "pad alignment with T_OPPOSE %.4f"
                                 % t["pad_alignment_with_T_OPPOSE"]]))
compose([rowP], "STAGE6B_TIP_TRAJECTORY.png")

# ---- 12 bind restore proof
zr = json.load(open(os.path.join(OUTDIR, "STAGE6B_ZERO_RESTORE_AUDIT.json"),
                    encoding="utf-8"))
rowB, rowA = [], []
seq = [("10deg", (10.0, 0.0, 0.0)), ("20deg", (20.0, 0.0, 0.0)), ("30deg", C30), ("L3", FL3)]
for view in ("dorsal", "closeup"):
    cn, d = VIEWS[view]
    S.bind()
    rowB.append(S.render(cn, d, [BEFORE, "bind rest pose   %s view" % view]))
for nm, case in seq:                      # run the whole 9-case pose path with resets
    S.pose(case)
    S.bind()
S.bind()
for view in ("dorsal", "closeup"):
    cn, d = VIEWS[view]
    rowA.append(S.render(cn, d, ["AFTER   bind rest pose after the 9-case sequence",
                                 "ZERO_RESTORE = %s   max delta %.9f mm (gate 1e-4)"
                                 % (zr["ALL_9_CASES_RESTORE"],
                                    zr["RESTORE_MAX_DELTA_MM"])]))
compose([rowB, rowA], "STAGE6B_BIND_RESTORE_PROOF.png")

# ---- 13..16 required close-ups
CLOSEUPS = [("STAGE6B_CMC_CAGE_CLOSEUP_L3.png", "cmc", "CMC cage",
             lambda: "min face-area %.4f   fold-over %s"
             % (CAGE_A["FULL_OPP_L3"]["strain"]["min_face_area_ratio"],
                CAGE_A["FULL_OPP_L3"]["CMC_CAGE_CATASTROPHIC_FOLD_OVER"])),
            ("STAGE6B_FIRST_WEB_CLOSEUP_L3.png", "web", "first web",
             lambda: "opening area ratio %.4f   tear %s"
             % (json.load(open(os.path.join(OUTDIR,
                                            "STAGE6B_FIRST_WEB_DEFORM_AUDIT.json"),
                               encoding="utf-8"))["cases"]["FULL_OPP_L3"][
                 "web_opening_area_ratio_vs_bind"],
                json.load(open(os.path.join(OUTDIR,
                                            "STAGE6B_FIRST_WEB_DEFORM_AUDIT.json"),
                               encoding="utf-8"))["cases"]["FULL_OPP_L3"][
                 "FIRST_WEB_ACTUAL_TEAR"])),
            ("STAGE6B_THENAR_CLOSEUP_L3.png", "thenar", "thenar",
             lambda: "bbox volume ratio %.4f   collapse %s"
             % (TH["FULL_OPP_L3"]["pca_bbox_volume_ratio_vs_bind"],
                TH["FULL_OPP_L3"]["THENAR_CATASTROPHIC_COLLAPSE"])),
            ("STAGE6B_THUMB_INDEX_CONTACT_CLOSEUP_L3.png", "contact", "thumb-index contact",
             lambda: "thumb-index pairs %d   max penetration %.4f mm"
             % (CONTACT["FULL_OPP_L3"]["counts"]["B_THUMB_INDEX"],
                CONTACT["FULL_OPP_L3"]["max_penetration_proxy_mm"]))]
for out_name, view, label, sub in CLOSEUPS:
    cn, d = VIEWS[view]
    S.bind()
    pB = S.render(cn, d, [BEFORE, "%s close-up   L3 comparison" % label])
    S.pose(FL3)
    pA = S.render(cn, d, ["AFTER   FULL_OPP_L3", "%s close-up" % label, sub(),
                          seamline("FULL_OPP_L3")])
    compose([[pB], [pA]], out_name)

S.bind()
json.dump({"stage": "STAGE6B_RENDER_LOG", "generated_at": NOW,
           "files": sorted(f for f in os.listdir(REND) if f.endswith(".png")),
           "tile_size": [TILE_W, TILE_H],
           "layout": {
               "before_after": "row1 = BEFORE (R1B bind), row2 = AFTER ; cols = dorsal, palmar, "
                               "thumb close-up, side",
               "strain": "row1 = BEFORE, row2 = AFTER ; colour = log10 face-area ratio "
                         "(red <= -1 collapse, green 0 rest, blue >= +1 stretch)",
               "full_opp_Lx": "row1 = BEFORE, row2 = AFTER ; cols = thumb close-up, palmar, "
                              "side (same camera family across L1/L2/L3)",
               "first_web / thenar": "row1 = BEFORE, row2 = AFTER ; cols = L1, L2, L3",
               "contact_progression": "row1 = plain material, row2 = translucent skin with red "
                                      "new intersecting faces ; cols = bind, L1, L2, L3",
               "tip_trajectory": "single row: bind, L1, L2, L3"},
           "same_camera_scale_lighting_material": True,
           "cameras": S.cam,
           "log": LOG},
          open(os.path.join(TMP, "S6B_RENDER_LOG.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("RENDER_S6B_DONE")
