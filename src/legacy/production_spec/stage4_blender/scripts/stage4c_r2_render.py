# STAGE4C_R2 -- formal Human Review renders.  READ-ONLY (nothing is written back to the blend).
#
#   STAGE4C_R2_DORSAL / PALMAR / FINGERTIPS / THUMB_NAIL   nail semantics in context
#   STAGE4C_R2_NAIL_MASK_DORSAL                            per-digit diagnostic colours
#   STAGE4C_R2_ORIGIN_SIDE                                 origin evidence, labelled
#   STAGE4C_R2_ORIGIN_DORSAL_OBLIQUE                       origin evidence, in context
#
# usage: blender -b <stage4c_r2.blend> --python stage4c_r2_render.py -- <outdir> <run.json> <frame.json>
import bpy, sys, os, json, importlib.util
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR, RUNJSON, FRAMEJSON = argv[0], argv[1], argv[2]
os.makedirs(OUTDIR, exist_ok=True)
SCRATCH = os.path.join(os.path.dirname(OUTDIR.rstrip("/\\")), "_tmp")
os.makedirs(SCRATCH, exist_ok=True)

RUN = json.load(open(RUNJSON, encoding="utf-8"))
FRJ = json.load(open(FRAMEJSON, encoding="utf-8"))
CAMS = json.load(open(os.path.join(os.path.dirname(RUNJSON), "..", "stage4b_rssf", "CAMS.json"),
                      encoding="utf-8"))
AUDIT = os.path.join(os.path.dirname(RUNJSON), "NAIL_AUDIT_R2.json")
if not os.path.exists(AUDIT):
    raise SystemExit("NAIL_AUDIT_R2.json is required (run stage4c_r2_audits.py first)")
FACE_LISTS = json.load(open(AUDIT, encoding="utf-8"))["per_digit_faces"]

spec = importlib.util.spec_from_file_location(
    "sel", os.path.join(os.path.dirname(os.path.abspath(__file__)), "stage4c_r2_selector.py"))
SELM = importlib.util.module_from_spec(spec); spec.loader.exec_module(SELM)
fr = SELM.build_frame(FRJ["bones"])
DIG = SELM.DIGITS

TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
MW = ob.matrix_world
W = [(MW @ v.co).copy() for v in ob.data.vertices]
O_NOW = Vector(json.load(open(os.path.join(os.path.dirname(RUNJSON), "ORIGIN_AUDIT_R2.json"),
                              encoding="utf-8"))["ORIGIN_AFTER"])
O_S4B = Vector(FRJ["bones"]["WRIST_R"]["head"])

sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'
sc.display.render_aa = '8'
w = bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("W")
sc.world = w
w.color = (1.0, 1.0, 1.0)
cd = bpy.data.cameras.new("c"); cd.type = 'ORTHO'; cd.clip_start = 0.001
cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam


def aim(centre, dirv, scale, res):
    sc.render.resolution_x, sc.render.resolution_y = res
    cd.ortho_scale = scale
    pos = Vector(centre) + Vector(dirv).normalized() * 0.9
    cam.location = pos
    cam.rotation_euler = (Vector(centre) - pos).to_track_quat('-Z', 'Y').to_euler()


def shoot(centre, dirv, scale, out, res=(1200, 1000)):
    aim(centre, dirv, scale, res)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("RENDERED", os.path.basename(out), os.path.exists(out))


def text_obj(body, size, col):
    bpy.ops.object.text_add()
    t = bpy.context.active_object
    t.data.body = body
    t.data.size = size
    t.data.align_x = 'LEFT'
    t.data.align_y = 'CENTER'
    t.color = col
    return t


# =============================================================== 1. nail views
def pts_for(digits):
    p = []
    for n in digits:
        for fi in FACE_LISTS[n]:
            for v in ob.data.polygons[fi].vertices:
                p.append(W[v])
    return p


sc.display.shading.color_type = 'MATERIAL'
ob.color = (0.90, 0.90, 0.92, 1.0)
shoot(CAMS["centre"], CAMS["views"]["DORSAL"], CAMS["ortho"],
      os.path.join(OUTDIR, "STAGE4C_R2_DORSAL.png"))
shoot(CAMS["centre"], CAMS["views"]["PALMAR"], CAMS["ortho"],
      os.path.join(OUTDIR, "STAGE4C_R2_PALMAR.png"))

four = ("index", "middle", "ring", "little")
fpts = pts_for(four)
fctr = sum(fpts, Vector()) / len(fpts)
fdir = sum((fr["nail_normal"][n] for n in four), Vector()).normalized()
shoot(fctr, fdir, 0.085, os.path.join(OUTDIR, "STAGE4C_R2_FINGERTIPS.png"), res=(1400, 1000))

tpts = pts_for(("thumb",))
tctr = sum(tpts, Vector()) / len(tpts)
shoot(tctr, CAMS["views"]["DORSAL"], 0.055,
      os.path.join(OUTDIR, "STAGE4C_R2_THUMB_NAIL.png"), res=(1000, 1000))

# --- per-digit diagnostic mask ------------------------------------------------------------
COLS = {"thumb": (0.95, 0.15, 0.15, 1.0), "index": (0.10, 0.55, 0.95, 1.0),
        "middle": (0.10, 0.75, 0.25, 1.0), "ring": (0.95, 0.70, 0.05, 1.0),
        "little": (0.65, 0.20, 0.85, 1.0)}
ob.color = (0.62, 0.62, 0.64, 1.0)
sc.display.shading.color_type = 'OBJECT'
masks = []
LIFT = 0.00025          # push each mask face 0.25 mm along its own normal, otherwise the
                        # patch is coincident with the skin and z-fights / disappears
for d in DIG:
    vs, fcs = [], []
    for fi in FACE_LISTS[d]:
        n = ob.data.polygons[fi].normal
        b = len(vs)
        vs += [tuple(W[v] + n * LIFT) for v in ob.data.polygons[fi].vertices]
        fcs.append(tuple(range(b, b + len(ob.data.polygons[fi].vertices))))
    m = bpy.data.meshes.new("mask_" + d); m.from_pydata(vs, [], fcs); m.update()
    o = bpy.data.objects.new("mask_" + d, m); sc.collection.objects.link(o); o.color = COLS[d]
    masks.append(o)
shoot(CAMS["centre"], CAMS["views"]["DORSAL"], CAMS["ortho"],
      os.path.join(OUTDIR, "STAGE4C_R2_NAIL_MASK_DORSAL.png"), res=(1400, 1000))
# The dorsal direction is what the brief names, and it is the view that proves the NEGATIVE
# (nothing at the finger roots, nothing in the web, nothing on the palm) -- but the plates are
# ~64 deg oblique to it, so it cannot show their shape.  A second mask view along the mean
# nail normal makes the five footprints directly readable, so "the five regions do not
# intersect" can actually be checked by eye as well as by the pairwise-intersection audit.
fdir2 = sum((fr["nail_normal"][n] for n in ("index", "middle", "ring", "little")),
            Vector()).normalized()
shoot(sum(pts_for(("index", "middle", "ring", "little")), Vector()) /
      len(pts_for(("index", "middle", "ring", "little"))), fdir2, 0.140,
      os.path.join(OUTDIR, "STAGE4C_R2_NAIL_MASK_NAILVIEW.png"), res=(1400, 1000))
# widen the nail-view mask so all four fingers are inside the frame
shoot(sum(pts_for(("thumb",)), Vector()) / len(pts_for(("thumb",))), CAMS["views"]["DORSAL"],
      0.055, os.path.join(OUTDIR, "STAGE4C_R2_NAIL_MASK_THUMBVIEW.png"), res=(1000, 1000))
for o in masks:
    bpy.data.objects.remove(o, do_unlink=True)

# =============================================================== 2. origin evidence
zmin = min(p.z for p in W)
cap = [p for p in W if abs(p.z - zmin) <= 0.004]
cap_c = sum(cap, Vector()) / len(cap)
ext = max(max(p.x for p in W) - min(p.x for p in W), max(p.y for p in W) - min(p.y for p in W))

ob.color = (0.86, 0.86, 0.88, 1.0)


def slab(z, half, col, name, dz=-0.0007, thick=0.0014):
    """a THIN BOX perpendicular to the arm axis.  A zero-thickness plane would be invisible
    edge-on from this camera, so it is given real thickness; from the side it then reads as a
    level bar crossing the arm, which is exactly what marks a joint level."""
    x0, x1 = cap_c.x - half, cap_c.x + half
    y0, y1 = cap_c.y - half, cap_c.y + half
    z0, z1 = z + dz, z + dz + thick
    vs = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
          (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    fs = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    m = bpy.data.meshes.new(name)
    m.from_pydata(vs, [], fs)
    m.update()
    o = bpy.data.objects.new(name, m); sc.collection.objects.link(o); o.color = col
    return o


side = ext * 0.30
cut_o = slab(zmin, side, (0.85, 0.15, 0.15, 1.0), "cutplane")
org_o = slab(O_NOW.z, side, (0.05, 0.30, 0.95, 1.0), "originplane")

# the origin itself is INSIDE the wrist volume, so it is drawn as a sphere and revealed by
# x-ray; the silhouette stays visible, which is what the brief asks for
for p, c in ((O_S4B, (0.05, 0.05, 0.05, 1.0)), (O_NOW, (0.05, 0.30, 0.95, 1.0))):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0026, location=tuple(p))
    bpy.context.active_object.color = c

SIDE_DIR = Vector((-1.0, 0.0, 0.0))     # look along the arm's own side axis
wcent = (O_NOW + O_S4B) / 2
# An explicit look-at basis is used here instead of to_track_quat: we need the basis vectors
# to place the labels reliably, and the forearm is best seen from its side (view along +-X).
fwd = SIDE_DIR.normalized()
Zc = -fwd
Xc = Vector((0, 0, 1)).cross(Zc).normalized()
Yc = Zc.cross(Xc).normalized()


def aim_basis(centre, scale, res, distance=0.9):
    sc.render.resolution_x, sc.render.resolution_y = res
    cd.ortho_scale = scale
    pos = Vector(centre) - fwd * distance
    from mathutils import Matrix as _M
    cam.matrix_world = _M(((Xc.x, Yc.x, Zc.x, pos.x), (Xc.y, Yc.y, Zc.y, pos.y),
                           (Xc.z, Yc.z, Zc.z, pos.z), (0, 0, 0, 1)))
    return Xc, Yc


sc.display.shading.show_xray = True
sc.display.shading.xray_alpha = 0.45
RIGHT_V, UP_V = aim_basis(wcent, 0.135, (1300, 1000))
labels = []


def place(body, anchor, off, size, col):
    t = text_obj(body, size, col)
    t.location = Vector(anchor) + RIGHT_V * off[0] + UP_V * off[1]
    t.rotation_euler = cam.rotation_euler
    labels.append(t)


place("WRIST_ORIGIN  (delivered)", Vector((cap_c.x, cap_c.y, O_NOW.z)), (0.032, 0.008),
      0.0024, (0.05, 0.30, 0.95, 1.0))
place("Stage-4B WRIST_R  (ERRONEOUS)", Vector((cap_c.x, cap_c.y, O_S4B.z)), (0.032, 0.008),
      0.0024, (0.05, 0.05, 0.05, 1.0))
place("forearm cut plane", Vector((cap_c.x, cap_c.y, zmin)), (0.032, -0.010),
      0.0022, (0.85, 0.15, 0.15, 1.0))
sc.render.filepath = os.path.join(OUTDIR, "STAGE4C_R2_ORIGIN_SIDE.png")
bpy.ops.render.render(write_still=True)
print("RENDERED STAGE4C_R2_ORIGIN_SIDE.png", True)
sc.render.filepath = os.path.join(SCRATCH, "_origin_side_unlabelled.png")
bpy.ops.render.render(write_still=True)
for t in labels:
    bpy.data.objects.remove(t, do_unlink=True)
sc.display.shading.show_xray = False

shoot(wcent, Vector(CAMS["views"]["OBLIQUE"]).normalized(), 0.34,
      os.path.join(OUTDIR, "STAGE4C_R2_ORIGIN_DORSAL_OBLIQUE.png"), res=(1300, 1000))
print("DONE")
