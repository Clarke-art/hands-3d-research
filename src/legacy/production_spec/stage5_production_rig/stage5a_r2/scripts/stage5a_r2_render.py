# =====================================================================================
# STAGE5A_R2 -- formal Human Review renders.  READ-ONLY.
#   STAGE5A_R2_RIG_{DORSAL,PALMAR,DORSAL_OBLIQUE}.png
#   STAGE5A_R2_WRIST_BEFORE_AFTER.png     INDEX_MCP_BEFORE_AFTER.png     THUMB_CHAIN_BEFORE_AFTER.png
#   STAGE5A_R2_THUMB_{CMC,MCP,TIP}_CLOSEUP.png     STAGE5A_R2_LABELLED.png
# usage: blender -b <R2.blend> --python stage5a_r2_render.py -- <stage5a_r2_dir>
# =====================================================================================
import bpy, sys, os, json, math
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
S5AR2 = argv[0]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
S5A = r"<HANDS_ROOT>\production_spec\stage5_production_rig\stage5a"
RENDERS = os.path.join(S5AR2, "renders")
SCRATCH = os.path.join(S5AR2, "_tmp")
os.makedirs(RENDERS, exist_ok=True)
os.makedirs(SCRATCH, exist_ok=True)
MM = 1000.0
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
cage = json.load(open(os.path.join(S4, "stage4a_r2", "R2_CAGE.json"), encoding="utf-8"))
wprof = json.load(open(os.path.join(S5AR2, "STAGE5A_R2_WRIST_PROFILE.json"), encoding="utf-8"))
cand = json.load(open(os.path.join(S5AR2, "_tmp", "S5A_R2_CANDIDATES.json"), encoding="utf-8"))
jt = json.load(open(os.path.join(S5AR2, "STAGE5A_R2_PRODUCTION_JOINT_TABLE.json"), encoding="utf-8"))["joints"]
CAMS = json.load(open(os.path.join(S4, "stage4b_rssf", "CAMS.json"), encoding="utf-8"))
ASSET_ORIGIN = Vector(oa["WRIST_ORIGIN"])
LEGACY_WRIST = Vector(oa["stage4b_WRIST_R_head"])

TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
MW = ob.matrix_world
W = [(MW @ v.co).copy() for v in ob.data.vertices]
zmin = min(p.z for p in W)
cap = [p for p in W if abs(p.z - zmin) <= 0.004]
cap_c = sum(cap, Vector()) / len(cap)
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
RIGW = rig.matrix_world
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
R1COL = (0.55, 0.55, 0.58, 1.0)          # R1 = diagnostic marker colour
R2COL = (0.95, 0.30, 0.05, 1.0)          # R2 = production candidate colour


def link(m, name, col):
    o = bpy.data.objects.new(name, m)
    sc.collection.objects.link(o)
    o.color = col
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
    vs, fs = [], []
    for i in range(rings + 1):
        th = math.pi * i / rings
        for j in range(segs):
            ph = 2 * math.pi * j / segs
            vs.append((p[0] + r * math.sin(th) * math.cos(ph), p[1] + r * math.sin(th) * math.sin(ph),
                       p[2] + r * math.cos(th)))
    for i in range(rings):
        for j in range(segs):
            a = i * segs + j; b = i * segs + (j + 1) % segs
            c = (i + 1) * segs + (j + 1) % segs; d = (i + 1) * segs + j
            fs.append((a, b, c, d))
    m = bpy.data.meshes.new(name); m.from_pydata(vs, [], fs); m.update()
    return link(m, name, col)


def slab(name, z, half, col, thick=0.0016):
    x0, x1 = cap_c.x - half, cap_c.x + half
    y0, y1 = cap_c.y - half, cap_c.y + half
    vs = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z),
          (x0, y0, z + thick), (x1, y0, z + thick), (x1, y1, z + thick), (x0, y1, z + thick)]
    fs = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    m = bpy.data.meshes.new(name); m.from_pydata(vs, [], fs); m.update()
    return link(m, name, col)


def text_obj(body, size, col, align='LEFT'):
    bpy.ops.object.text_add()
    t = bpy.context.active_object
    t.data.body = body
    t.data.size = size
    t.data.align_x = align
    t.data.align_y = 'CENTER'
    t.color = col
    return t


def place_label(t, loc, Xc, Yc, Zc):
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


TMP = []


def shoot(centre, dirv, scale, out, res=(1300, 1000), label=None, align='LEFT'):
    Xc, Yc, Zc = set_cam(centre, dirv, scale, res)
    if label:
        t = text_obj(label, scale * 0.030, (0.05, 0.05, 0.05, 1.0), align)
        place_label(t, Vector(centre) + Xc * (scale * (-0.47 if align == 'LEFT' else 0.47))
                    + Yc * (scale * 0.42), Xc, Yc, Zc)
        TMP.append(t)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    for t in TMP:
        bpy.data.objects.remove(t, do_unlink=True)
    TMP.clear()
    print("RENDERED", os.path.basename(out), os.path.exists(out))


def fam(name):
    if name == "WRIST_R":
        return "WRIST"
    for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
        if name.startswith(D):
            return "TIP" if name.endswith("_TIP_R") else D
    return "TIP"


# ------------------------- build R2 proxies + R1 diagnostic proxies ------------------
R1H = {n: Vector(jt[n]["R1_authored_position"]) for n in jt}
R2H = {b.name: (RIGW @ b.head_local) for b in ad.bones}
R2T = {b.name: (RIGW @ b.tail_local) for b in ad.bones}

for b in ad.bones:
    bone_proxy("r2bone_" + b.name, R2H[b.name], R2T[b.name], COLS[fam(b.name)])
    sphere("r2jnt_" + b.name, R2H[b.name], 0.0030 if b.name == "WRIST_R" else 0.0022,
           (0.08, 0.08, 0.10, 1.0))

r1objs = []
for n, p in R1H.items():
    r1objs.append(sphere("r1jnt_" + n, p, 0.0022, R1COL))
ob.color = (0.80, 0.82, 0.86, 1.0)

V = CAMS["views"]
C = CAMS["centre"]

# ============================== 1. three rig views ===================================
sc.display.shading.show_xray = True
sc.display.shading.xray_alpha = 0.55
for n in r1objs:
    n.hide_render = True
shoot(C, V["DORSAL"], 0.300, os.path.join(RENDERS, "STAGE5A_R2_RIG_DORSAL.png"),
      label="STAGE5A_R2_RIGHT_HAND_PRODUCTION_RIG   dorsal   21 bones / mesh semi-transparent")
shoot(C, V["PALMAR"], 0.300, os.path.join(RENDERS, "STAGE5A_R2_RIG_PALMAR.png"),
      label="STAGE5A_R2_RIGHT_HAND_PRODUCTION_RIG   palmar")
shoot(C, V["OBLIQUE"], 0.320, os.path.join(RENDERS, "STAGE5A_R2_RIG_DORSAL_OBLIQUE.png"),
      label="STAGE5A_R2_RIGHT_HAND_PRODUCTION_RIG   dorsal oblique")
for n in r1objs:
    n.hide_render = False

# ============================== 2. WRIST before / after ==============================
ext = 0.34 * max(max(p.x for p in W) - min(p.x for p in W), max(p.y for p in W) - min(p.y for p in W))
slab("cp_cut", zmin, ext, (0.85, 0.15, 0.15, 1.0))
slab("cp_asset", ASSET_ORIGIN.z, ext, (0.10, 0.35, 0.95, 1.0))
slab("cp_ws4b", LEGACY_WRIST.z, ext, (0.05, 0.05, 0.05, 1.0))
sphere("mk_asset", ASSET_ORIGIN, 0.0032, (0.10, 0.35, 0.95, 1.0))
sphere("mk_s4b", LEGACY_WRIST, 0.0032, (0.05, 0.05, 0.05, 1.0))
W2 = R2H["WRIST_R"]; PR = R2T["WRIST_R"]; W1 = R1H["WRIST_R"]
sphere("mk_palmref", PR, 0.0026, (0.05, 0.55, 0.35, 1.0))
wcent = (W2 + LEGACY_WRIST) / 2
DIRv = Vector((-1.0, 0.0, 0.0))
Xc, Yc, Zc = set_cam(wcent, DIRv, 0.200, (1700, 1150))
labs = []
for body, anchor, off, col, sz, al in [
        ("PRODUCTION WRIST_R head  (R2)", W2, (-0.008, 0.012), R2COL, 0.0019, 'RIGHT'),
        ("R1 WRIST_R head  (frozen evidence)", W1, (-0.008, -0.002), R1COL, 0.0017, 'RIGHT'),
        ("ASSET OBJECT ORIGIN  (frozen, NOT the wrist joint)", ASSET_ORIGIN, (-0.008, 0.012),
         (0.10, 0.35, 0.95, 1.0), 0.0018, 'RIGHT'),
        ("PALM REFERENCE  (four-MCP centroid, re-derived into the palm)", PR, (-0.008, 0.012),
         (0.05, 0.55, 0.35, 1.0), 0.0017, 'RIGHT'),
        ("forearm cut plane", Vector((cap_c.x, cap_c.y, zmin)), (-0.008, -0.026),
         (0.85, 0.15, 0.15, 1.0), 0.0017, 'RIGHT'),
        ("LEGACY_STAGE4B_WRIST_R -- DO NOT USE", LEGACY_WRIST, (-0.008, 0.010),
         (0.05, 0.05, 0.05, 1.0), 0.0016, 'RIGHT')]:
    t = text_obj(body, sz, col, align=al)
    place_label(t, Vector(anchor) + Xc * off[0] + Yc * off[1], Xc, Yc, Zc)
    labs.append(t)
t = text_obj("ASSET ORIGIN  !=  PRODUCTION WRIST JOINT", 0.0028, (0.85, 0.10, 0.10, 1.0))
place_label(t, Vector(wcent) + Xc * (-0.085) + Yc * (-0.048), Xc, Yc, Zc)
labs.append(t)
sc.render.filepath = os.path.join(RENDERS, "STAGE5A_R2_WRIST_BEFORE_AFTER.png")
bpy.ops.render.render(write_still=True)
print("RENDERED STAGE5A_R2_WRIST_BEFORE_AFTER.png")
for t in labs:
    bpy.data.objects.remove(t, do_unlink=True)
sc.render.filepath = os.path.join(SCRATCH, "_wrist_ba_unlabelled.png")
bpy.ops.render.render(write_still=True)

# ============================== 3. INDEX_MCP before / after ==========================
ic = (R1H["INDEX_MCP_R"] + R2H["INDEX_MCP_R"]) / 2
labs = []
Xc, Yc, Zc = set_cam(ic, V["DORSAL"], 0.075, (1500, 1100))
for body, anchor, off, col, sz in [
        ("R1 INDEX_MCP_R  (0.26 mm outside the skin, rejected)", R1H["INDEX_MCP_R"], (0.014, 0.010), R1COL, 0.0016),
        ("R2 INDEX_MCP_R  (section medial centre, 5.87 mm clearance)", R2H["INDEX_MCP_R"], (0.014, -0.006), R2COL, 0.0016)]:
    t = text_obj(body, sz, col)
    place_label(t, Vector(anchor) + Xc * off[0] + Yc * off[1], Xc, Yc, Zc)
    labs.append(t)
sc.render.filepath = os.path.join(RENDERS, "STAGE5A_R2_INDEX_MCP_BEFORE_AFTER.png")
bpy.ops.render.render(write_still=True)
print("RENDERED STAGE5A_R2_INDEX_MCP_BEFORE_AFTER.png")
for t in labs:
    bpy.data.objects.remove(t, do_unlink=True)

# ============================== 4. THUMB CHAIN before / after ========================
tc = (R1H["THUMB_CMC_R"] + R2H["THUMB_CMC_R"] + R2H["THUMB_TIP_R"]) / 3
labs = []
Xc, Yc, Zc = set_cam(tc, V["DORSAL"], 0.130, (1550, 1150))
for body, anchor, off, col, sz in [
        ("R1 THUMB_CMC/MCP/TIP  (surface-hugging, rejected)", R1H["THUMB_CMC_R"], (0.016, 0.016), R1COL, 0.0015),
        ("R2 THUMB_CMC", R2H["THUMB_CMC_R"], (0.016, 0.005), R2COL, 0.0015),
        ("R2 THUMB_MCP", R2H["THUMB_MCP_R"], (0.016, -0.005), R2COL, 0.0015),
        ("R2 THUMB_TIP", R2H["THUMB_TIP_R"], (0.016, -0.015), R2COL, 0.0015),
        ("THUMB_IP  (kept from R1, unchanged)", R2H["THUMB_IP_R"], (0.016, -0.025), COLS["THUMB"], 0.0014)]:
    t = text_obj(body, sz, col)
    place_label(t, Vector(anchor) + Xc * off[0] + Yc * off[1], Xc, Yc, Zc)
    labs.append(t)
sc.render.filepath = os.path.join(RENDERS, "STAGE5A_R2_THUMB_CHAIN_BEFORE_AFTER.png")
bpy.ops.render.render(write_still=True)
print("RENDERED STAGE5A_R2_THUMB_CHAIN_BEFORE_AFTER.png")
for t in labs:
    bpy.data.objects.remove(t, do_unlink=True)

# ============================== 5. three thumb close-ups =============================
anchor = W[cage["cmc_vertex"]]
R_LOC = max(cage["locality"]["euclidean_radius_mm"]) / 1000.0
for axis in range(3):
    vs, fs = [], []
    segs = 72
    for i in range(segs):
        tt = 2 * math.pi * i / segs
        for jj in range(8):
            ss = 2 * math.pi * jj / 8
            r = R_LOC + 0.0005 * math.cos(ss)
            q = [r * math.cos(tt), r * math.sin(tt), 0.0005 * math.sin(ss)]
            if axis == 0:
                q = [q[2], q[0], q[1]]
            elif axis == 1:
                q = [q[1], q[2], q[0]]
            vs.append((anchor.x + q[0], anchor.y + q[1], anchor.z + q[2]))
    for i in range(segs):
        for jj in range(8):
            a = i * 8 + jj; b = i * 8 + (jj + 1) % 8
            c = ((i + 1) % segs) * 8 + (jj + 1) % 8; d = ((i + 1) % segs) * 8 + jj
            fs.append((a, b, c, d))
    m = bpy.data.meshes.new("cage_ax%d" % axis); m.from_pydata(vs, [], fs); m.update()
    link(m, "cage_ax%d" % axis, (0.90, 0.45, 0.05, 1.0))
sphere("mk_cmcanchor", anchor, 0.0022, (0.90, 0.45, 0.05, 1.0))


def closeup(name, centre, scale, labels, res=(1450, 1080)):
    labs = []
    Xc, Yc, Zc = set_cam(centre, V["DORSAL"], scale, res)
    for body, anch, off, col, sz in labels:
        t = text_obj(body, sz, col)
        place_label(t, Vector(anch) + Xc * off[0] + Yc * off[1], Xc, Yc, Zc)
        labs.append(t)
    sc.render.filepath = os.path.join(RENDERS, name)
    bpy.ops.render.render(write_still=True)
    print("RENDERED", name)
    for t in labs:
        bpy.data.objects.remove(t, do_unlink=True)


closeup("STAGE5A_R2_THUMB_CMC_CLOSEUP.png", (R2H["THUMB_CMC_R"] + anchor) / 2, 0.100, [
    ("R2 THUMB_CMC_R  (thenar interior medial, 12.00 mm clearance)", R2H["THUMB_CMC_R"],
     (-0.060, 0.018), R2COL, 0.0016),
    ("R1 THUMB_CMC_R  (0.17 mm clearance, surface anchor)", R1H["THUMB_CMC_R"],
     (-0.060, 0.008), R1COL, 0.0015),
    ("approved CMC cage anchor (Stage-4A R2 vertex %d)" % cage["cmc_vertex"], anchor,
     (-0.060, -0.004), (0.90, 0.45, 0.05, 1.0), 0.0015),
    ("approved cage locality sphere  R = %.2f mm" % (R_LOC * MM), anchor,
     (-0.060, -0.014), (0.90, 0.45, 0.05, 1.0), 0.0015),
    ("distance to cage anchor = %.2f mm  (inside the approved region)"
     % ((R2H["THUMB_CMC_R"] - anchor).length * MM),
     anchor, (-0.060, -0.024), (0.90, 0.45, 0.05, 1.0), 0.0014)])
closeup("STAGE5A_R2_THUMB_MCP_CLOSEUP.png",
        (R1H["THUMB_MCP_R"] + R2H["THUMB_MCP_R"]) / 2, 0.105, [
    ("R2 THUMB_MCP_R  (thumb tube interior medial, 9.48 mm clearance)", R2H["THUMB_MCP_R"],
     (0.012, 0.012), R2COL, 0.0016),
    ("R1 THUMB_MCP_R  (2.45 mm OUTSIDE the skin, rejected)", R1H["THUMB_MCP_R"],
     (0.012, 0.002), R1COL, 0.0015),
    ("shift 12.51 mm  |  T-01 axial delta +4.59 mm (zone +/-9.61 mm)",
     R2H["THUMB_MCP_R"], (0.012, -0.010), (0.30, 0.30, 0.32, 1.0), 0.0014)])
closeup("STAGE5A_R2_THUMB_TIP_CLOSEUP.png",
        (R1H["THUMB_TIP_R"] + R2H["THUMB_TIP_R"]) / 2, 0.100, [
    ("R2 THUMB_TIP_R  (fingertip landmark on the skin)", R2H["THUMB_TIP_R"],
     (0.012, 0.014), R2COL, 0.0016),
    ("R1 THUMB_TIP_R  (12.08 mm short of the apex, rejected)", R1H["THUMB_TIP_R"],
     (0.012, 0.004), R1COL, 0.0015),
    ("shift 9.39 mm  |  now 6.97 mm from the apex vertex, 0.002 mm off the skin",
     R2H["THUMB_TIP_R"], (0.012, -0.008), (0.30, 0.30, 0.32, 1.0), 0.0014)])

# ============================== 6. labelled all-21 ===================================
sc.display.shading.xray_alpha = 0.50
SCALE = 0.440
shoot(C, V["DORSAL"], SCALE, os.path.join(RENDERS, "STAGE5A_R2_LABELLED.png"), res=(2200, 1500))
Xc, Yc, Zc = set_cam(C, V["DORSAL"], SCALE, (2200, 1500))
TSIZE, ROW, COLX = 0.0034, 0.0165, (-0.205, 0.074)
items = {"left": [], "right": []}
for b in ad.bones:
    mid = (R2H[b.name] + R2T[b.name]) / 2
    sx = (mid - Vector(C)).dot(Xc); sy = (mid - Vector(C)).dot(Yc)
    items["left" if sx < 0 else "right"].append((sy, b.name))
labs = []
for ci, col in enumerate(("left", "right")):
    rows = sorted(items[col], key=lambda t: -t[0]); ys = []
    for sy, name in rows:
        y = sy if not ys or ys[-1] - sy >= ROW else ys[-1] - ROW
        ys.append(y)
    for (sy, name), y in zip(rows, ys):
        t = text_obj(name, TSIZE, COLS[fam(name)])
        place_label(t, Vector(C) + Xc * COLX[ci] + Yc * y, Xc, Yc, Zc)
        labs.append(t)
sc.render.filepath = os.path.join(RENDERS, "STAGE5A_R2_LABELLED.png")
bpy.ops.render.render(write_still=True)
print("RENDERED STAGE5A_R2_LABELLED.png (21 labels)")
for t in labs:
    bpy.data.objects.remove(t, do_unlink=True)
print("DONE", len([f for f in os.listdir(RENDERS) if f.endswith('.png')]))
