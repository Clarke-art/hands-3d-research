# =====================================================================================
# STAGE5A -- formal Human Review renders.  READ-ONLY (nothing is written back to the blend).
#   STAGE5A_RIG_{DORSAL,PALMAR,RADIAL,ULNAR,DORSAL_OBLIQUE}.png
#   STAGE5A_RIG_{WRIST,THUMB_CMC,FINGERS_JOINT}_CLOSEUP.png
#   STAGE5A_RIG_LABELLED.png
# usage: blender -b <stage5a.blend> --python stage5a_render.py -- <stage5a_dir> <master_blend>
# =====================================================================================
import bpy, bmesh, sys, os, json, math
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
S5A, MASTER = argv[0], argv[1]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
RENDERS = os.path.join(S5A, "renders")
SCRATCH = os.path.join(S5A, "_tmp")
os.makedirs(RENDERS, exist_ok=True)
os.makedirs(SCRATCH, exist_ok=True)
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
cage = json.load(open(os.path.join(S4, "stage4a_r2", "R2_CAGE.json"), encoding="utf-8"))
CAMS = json.load(open(os.path.join(S4, "stage4b_rssf", "CAMS.json"), encoding="utf-8"))
WRIST_APPROVED = Vector(oa["WRIST_ORIGIN"])
LEGACY_WRIST = Vector(oa["stage4b_WRIST_R_head"])

TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
MW = ob.matrix_world
W = [(MW @ v.co).copy() for v in ob.data.vertices]
zmin = min(p.z for p in W)
cap = [p for p in W if abs(p.z - zmin) <= 0.004]
cap_c = sum(cap, Vector()) / len(cap)
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
ad = rig.data

sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'
sc.display.render_aa = '8'
sc.display.shading.color_type = 'OBJECT'
w = bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("W")
sc.world = w
w.color = (1.0, 1.0, 1.0)
cd = bpy.data.cameras.new("c"); cd.type = 'ORTHO'; cd.clip_start = 0.001
cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam

COLS = {"THUMB": (0.95, 0.15, 0.15, 1.0), "INDEX": (0.10, 0.55, 0.95, 1.0),
        "MIDDLE": (0.10, 0.75, 0.25, 1.0), "RING": (0.95, 0.70, 0.05, 1.0),
        "LITTLE": (0.65, 0.20, 0.85, 1.0), "WRIST": (0.00, 0.72, 0.82, 1.0),
        "TIP": (0.42, 0.42, 0.48, 1.0)}
ALL_OBJ = []


def link(m, name, col):
    o = bpy.data.objects.new(name, m)
    sc.collection.objects.link(o)
    o.color = col
    ALL_OBJ.append(o)
    return o


def bone_proxy(name, head, tail, col, wf=0.13):
    d = Vector(tail) - Vector(head)
    L = d.length
    if L < 1e-9:
        return None
    y = d / L
    tmp = Vector((0, 0, 1)) if abs(y.z) < 0.9 else Vector((1, 0, 0))
    x = y.cross(tmp).normalized()
    z = x.cross(y).normalized()
    wv = min(wf * L, 0.0050)
    h1 = Vector(head) + y * (0.14 * L)
    vs = [tuple(head), tuple(h1 + x * wv), tuple(h1 + z * wv), tuple(h1 - x * wv), tuple(h1 - z * wv),
          tuple(tail)]
    fs = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (5, 2, 1), (5, 3, 2), (5, 4, 3), (5, 1, 4)]
    m = bpy.data.meshes.new(name); m.from_pydata(vs, [], fs); m.update()
    return link(m, name, col)


def sphere(name, p, r, col, segs=20, rings=12):
    vs = []
    fs = []
    for i in range(rings + 1):
        th = math.pi * i / rings
        for j in range(segs):
            ph = 2 * math.pi * j / segs
            vs.append((p[0] + r * math.sin(th) * math.cos(ph),
                       p[1] + r * math.sin(th) * math.sin(ph),
                       p[2] + r * math.cos(th)))
    for i in range(rings):
        for j in range(segs):
            a = i * segs + j; b = i * segs + (j + 1) % segs
            c = (i + 1) * segs + (j + 1) % segs; d = (i + 1) * segs + j
            fs.append((a, b, c, d))
    m = bpy.data.meshes.new(name); m.from_pydata(vs, [], fs); m.update()
    return link(m, name, col)


def slab(name, z, half, col, thick=0.0016, centre=None):
    c = centre if centre is not None else cap_c
    x0, x1 = c.x - half, c.x + half
    y0, y1 = c.y - half, c.y + half
    z0, z1 = z, z + thick
    vs = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
          (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    fs = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    m = bpy.data.meshes.new(name); m.from_pydata(vs, [], fs); m.update()
    return link(m, name, col)


def ring3(name, centre, R, col, tube=0.0005):
    outs = []
    for axis in range(3):
        vs, fs = [], []
        segs = 96
        for i in range(segs):
            t = 2 * math.pi * i / segs
            for j in range(8):
                s = 2 * math.pi * j / 8
                r = R + tube * math.cos(s)
                q = [r * math.cos(t), r * math.sin(t), tube * math.sin(s)]
                if axis == 0:
                    q = [q[2], q[0], q[1]]
                elif axis == 1:
                    q = [q[1], q[2], q[0]]
                vs.append((centre[0] + q[0], centre[1] + q[1], centre[2] + q[2]))
        for i in range(segs):
            for j in range(8):
                a = i * 8 + j; b = i * 8 + (j + 1) % 8
                c = ((i + 1) % segs) * 8 + (j + 1) % 8; d = ((i + 1) % segs) * 8 + j
                fs.append((a, b, c, d))
        m = bpy.data.meshes.new(name + "_ax%d" % axis); m.from_pydata(vs, [], fs); m.update()
        outs.append(link(m, name + "_ax%d" % axis, col))
    return outs


def text_obj(body, size, col, align='LEFT'):
    bpy.ops.object.text_add()
    t = bpy.context.active_object
    t.data.body = body
    t.data.size = size
    t.data.align_x = align
    t.data.align_y = 'CENTER'
    t.color = col
    t.data.space_character = 0.95
    ALL_OBJ.append(t)
    return t


def place_label(t, loc, Xc, Yc, Zc):
    """orient the text with the camera basis so it always faces the camera unmirrored"""
    t.matrix_world = Matrix(((Xc.x, Yc.x, Zc.x, loc.x), (Xc.y, Yc.y, Zc.y, loc.y),
                             (Xc.z, Yc.z, Zc.z, loc.z), (0, 0, 0, 1)))


def set_cam(centre, dirv, scale, res, distance=0.9):
    sc.render.resolution_x, sc.render.resolution_y = res
    cd.ortho_scale = scale
    Zc = Vector(dirv).normalized()
    Xc = Vector((0, 0, 1)).cross(Zc)
    if Xc.length < 1e-6:
        Xc = Vector((1, 0, 0))
    Xc.normalize()
    Yc = Zc.cross(Xc).normalized()
    pos = Vector(centre) + Zc * distance
    cam.matrix_world = Matrix(((Xc.x, Yc.x, Zc.x, pos.x), (Xc.y, Yc.y, Zc.y, pos.y),
                               (Xc.z, Yc.z, Zc.z, pos.z), (0, 0, 0, 1)))
    return Xc, Yc, Zc


def shoot(centre, dirv, scale, out, res=(1300, 1000), label=None):
    Xc, Yc, Zc = set_cam(centre, dirv, scale, res)
    t = None
    if label:
        t = text_obj(label, scale * 0.030, (0.05, 0.05, 0.05, 1.0))
        place_label(t, Vector(centre) + Xc * (scale * -0.48) + Yc * (scale * 0.33), Xc, Yc, Zc)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    if t:
        bpy.data.objects.remove(t, do_unlink=True)
    print("RENDERED", os.path.basename(out), os.path.exists(out))


# ============================== build the rig proxies ================================
def fam(name):
    if name == "WRIST_R":
        return "WRIST"
    for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
        if name.startswith(D):
            return "TIP" if name.endswith("_TIP_R") else D
    return "TIP"


for b in ad.bones:
    c = COLS[fam(b.name)]
    bone_proxy("bone_" + b.name, b.head_local, b.tail_local, c)
    rr = 0.0030 if b.name == "WRIST_R" else (0.0016 if b.name.endswith("_TIP_R") else 0.0023)
    sphere("jnt_" + b.name, b.head_local, rr,
           (0.08, 0.08, 0.10, 1.0) if not b.name.endswith("_TIP_R") else (0.42, 0.42, 0.48, 1.0))

ob.color = (0.78, 0.80, 0.84, 1.0)
sc.display.shading.show_xray = True
sc.display.shading.xray_alpha = 0.55

# ============================== 1. five standard views ===============================
V = CAMS["views"]
C = CAMS["centre"]
shoot(C, V["DORSAL"], 0.300, os.path.join(RENDERS, "STAGE5A_RIG_DORSAL.png"),
      label="STAGE5A_RIGHT_HAND_PRODUCTION_RIG_R1  dorsal   mesh semi-transparent / 21 bones")
shoot(C, V["PALMAR"], 0.300, os.path.join(RENDERS, "STAGE5A_RIG_PALMAR.png"),
      label="STAGE5A_RIGHT_HAND_PRODUCTION_RIG_R1  palmar")
shoot(C, V["RADIAL"], 0.300, os.path.join(RENDERS, "STAGE5A_RIG_RADIAL.png"),
      label="STAGE5A_RIGHT_HAND_PRODUCTION_RIG_R1  radial (thumb side)")
shoot(C, [-x for x in V["RADIAL"]], 0.300, os.path.join(RENDERS, "STAGE5A_RIG_ULNAR.png"),
      label="STAGE5A_RIGHT_HAND_PRODUCTION_RIG_R1  ulnar (little side)")
shoot(C, V["OBLIQUE"], 0.320, os.path.join(RENDERS, "STAGE5A_RIG_DORSAL_OBLIQUE.png"),
      label="STAGE5A_RIGHT_HAND_PRODUCTION_RIG_R1  dorsal oblique")

# ============================== 2. wrist close-up ====================================
ext = 0.32 * max(max(p.x for p in W) - min(p.x for p in W), max(p.y for p in W) - min(p.y for p in W))
side = ext * 0.34
slab("cp_cut", zmin, side, (0.85, 0.15, 0.15, 1.0))
slab("cp_appr", WRIST_APPROVED.z, side, (0.05, 0.30, 0.95, 1.0))
slab("cp_legacy", LEGACY_WRIST.z, side, (0.05, 0.05, 0.05, 1.0))
sphere("mk_appr", WRIST_APPROVED, 0.0032, (0.05, 0.30, 0.95, 1.0))
sphere("mk_legacy", LEGACY_WRIST, 0.0032, (0.05, 0.05, 0.05, 1.0))
wcent = (WRIST_APPROVED + LEGACY_WRIST) / 2
DIR = Vector((-1.0, 0.0, 0.0))
shoot(wcent, DIR, 0.185, os.path.join(RENDERS, "STAGE5A_RIG_WRIST_CLOSEUP.png"),
      res=(1600, 1100))
Xc, Yc, Zc = set_cam(wcent, DIR, 0.185, (1600, 1100))
lab = [
    ("PRODUCTION WRIST_R head = approved Stage4C R2 origin", WRIST_APPROVED, (-0.006, 0.010),
     (0.05, 0.30, 0.95, 1.0), 0.0019),
    ("approved Stage4C wrist reference plane", Vector((cap_c.x, cap_c.y, WRIST_APPROVED.z)),
     (-0.006, -0.007), (0.05, 0.30, 0.95, 1.0), 0.0018),
    ("forearm cut plane", Vector((cap_c.x, cap_c.y, zmin)), (-0.006, -0.026),
     (0.85, 0.15, 0.15, 1.0), 0.0018),
    ("LEGACY_STAGE4B_WRIST_R -- DO NOT USE (%.2f mm away)"
     % ((WRIST_APPROVED - LEGACY_WRIST).length * 1000), LEGACY_WRIST, (-0.006, 0.010),
     (0.05, 0.05, 0.05, 1.0), 0.0018),
]
labs = []
for body, anchor, off, col, sz in lab:
    t = text_obj(body, sz, col, align='RIGHT')
    t.location = Vector(anchor) + Xc * off[0] + Yc * off[1]
    place_label(t, t.location, Xc, Yc, Zc)
    labs.append(t)
sc.render.filepath = os.path.join(RENDERS, "STAGE5A_RIG_WRIST_CLOSEUP.png")
bpy.ops.render.render(write_still=True)
print("RENDERED STAGE5A_RIG_WRIST_CLOSEUP.png (labelled)")
sc.render.filepath = os.path.join(SCRATCH, "_wrist_closeup_unlabelled.png")
bpy.ops.render.render(write_still=True)
for t in labs:
    bpy.data.objects.remove(t, do_unlink=True)

# ============================== 3. thumb CMC close-up ================================
cmc_anchor = W[ cage["cmc_vertex"] ]
R_LOC = max(cage["locality"]["euclidean_radius_mm"]) / 1000.0
ring3("cage_sphere", cmc_anchor, R_LOC, (0.90, 0.45, 0.05, 1.0), tube=0.0006)
sphere("mk_cmcanchor", cmc_anchor, 0.0022, (0.90, 0.45, 0.05, 1.0))
ccent = (Vector(jf["THUMB_CMC_R"]["head"]) + cmc_anchor) / 2
shoot(ccent, V["DORSAL"], 0.135, os.path.join(RENDERS, "STAGE5A_RIG_THUMB_CMC_CLOSEUP.png"),
      res=(1500, 1100))
Xc, Yc, Zc = set_cam(ccent, V["DORSAL"], 0.135, (1500, 1100))
labs = []
for body, anchor, off, col, sz in [
        ("THUMB_CMC_R  head (production)", Vector(jf["THUMB_CMC_R"]["head"]), (0.022, 0.010),
         (0.95, 0.15, 0.15, 1.0), 0.0019),
        ("approved CMC cage anchor (Stage-4A R2 vertex %d)" % cage["cmc_vertex"], cmc_anchor,
         (-0.014, -0.024), (0.90, 0.45, 0.05, 1.0), 0.0018),
        ("approved CMC cage locality radius  R = %.2f mm  (geodesic disc R = %.0f mm)"
         % (max(cage["locality"]["euclidean_radius_mm"]), cage["disk"]["R_mm"]), cmc_anchor,
         (-0.014, -0.036), (0.90, 0.45, 0.05, 1.0), 0.0017),
        ("CMC -> MCP bone  %.2f mm"
         % ((Vector(jf["THUMB_MCP_R"]["head"]) - Vector(jf["THUMB_CMC_R"]["head"])).length * 1000),
         Vector(jf["THUMB_MCP_R"]["head"]), (0.022, -0.012), (0.95, 0.15, 0.15, 1.0), 0.0018)]:
    t = text_obj(body, sz, col)
    t.location = Vector(anchor) + Xc * off[0] + Yc * off[1]
    place_label(t, t.location, Xc, Yc, Zc)
    labs.append(t)
sc.render.filepath = os.path.join(RENDERS, "STAGE5A_RIG_THUMB_CMC_CLOSEUP.png")
bpy.ops.render.render(write_still=True)
print("RENDERED STAGE5A_RIG_THUMB_CMC_CLOSEUP.png (labelled)")
sc.render.filepath = os.path.join(SCRATCH, "_thumb_cmc_closeup_unlabelled.png")
bpy.ops.render.render(write_still=True)
for t in labs:
    bpy.data.objects.remove(t, do_unlink=True)

# ============================== 4. finger joint close-up =============================
fp = []
for D in ("INDEX", "MIDDLE", "RING", "LITTLE"):
    for s in ("MCP", "PIP", "DIP"):
        fp.append(Vector(jf["%s_%s_R" % (D, s)]["head"]))
fc = sum(fp, Vector()) / len(fp)
shoot(fc, V["DORSAL"], 0.135, os.path.join(RENDERS, "STAGE5A_RIG_FINGERS_JOINT_CLOSEUP.png"),
      res=(1400, 1050))
Xc, Yc, Zc = set_cam(fc, V["DORSAL"], 0.135, (1400, 1050))
labs = []
for D in ("INDEX", "MIDDLE", "RING", "LITTLE"):
    for s in ("MCP", "PIP", "DIP"):
        p = Vector(jf["%s_%s_R" % (D, s)]["head"])
        t = text_obj("%s_%s" % (D[:3], s), 0.0016, COLS[D])
        t.location = p + Xc * 0.019 + Yc * (0.005 if s == "MCP" else (0.0 if s == "PIP" else -0.005))
        labs.append(t)
sc.render.filepath = os.path.join(RENDERS, "STAGE5A_RIG_FINGERS_JOINT_CLOSEUP.png")
bpy.ops.render.render(write_still=True)
print("RENDERED STAGE5A_RIG_FINGERS_JOINT_CLOSEUP.png (labelled)")
sc.render.filepath = os.path.join(SCRATCH, "_fingers_closeup_unlabelled.png")
bpy.ops.render.render(write_still=True)
for t in labs:
    bpy.data.objects.remove(t, do_unlink=True)

# ============================== 5. labelled all-21-bone view =========================
sc.display.shading.xray_alpha = 0.50
SCALE = 0.440
shoot(C, V["DORSAL"], SCALE, os.path.join(RENDERS, "STAGE5A_RIG_LABELLED.png"), res=(2200, 1500))
Xc, Yc, Zc = set_cam(C, V["DORSAL"], SCALE, (2200, 1500))
TSIZE = 0.0034
ROW = 0.0165
COLX = (-0.205, 0.074)          # two label columns, in screen-x (metres, relative to C)
items = {"left": [], "right": []}
for b in ad.bones:
    mid = (Vector(b.head_local) + Vector(b.tail_local)) / 2
    sx = (mid - Vector(C)).dot(Xc)
    sy = (mid - Vector(C)).dot(Yc)
    items["left" if sx < 0 else "right"].append((sy, b.name))
labs = []
for ci, col in enumerate(("left", "right")):
    rows = sorted(items[col], key=lambda t: -t[0])
    ys = []
    for sy, name in rows:
        y = sy
        if ys and ys[-1] - y < ROW:
            y = ys[-1] - ROW
        ys.append(y)
    for (sy, name), y in zip(rows, ys):
        t = text_obj(name, TSIZE, COLS[fam(name)])
        place_label(t, Vector(C) + Xc * COLX[ci] + Yc * y, Xc, Yc, Zc)
        labs.append(t)
sc.render.filepath = os.path.join(RENDERS, "STAGE5A_RIG_LABELLED.png")
bpy.ops.render.render(write_still=True)
print("RENDERED STAGE5A_RIG_LABELLED.png (21 labels, two-column layout)")
for t in labs:
    bpy.data.objects.remove(t, do_unlink=True)

print("DONE")
print("render count:", len([f for f in os.listdir(RENDERS) if f.endswith('.png')]))
