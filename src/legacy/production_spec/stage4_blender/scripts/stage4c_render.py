# STAGE4C_RSSF_ASSET_FINALIZATION_R1 -- evidence renders (read-only).
#
# Renders the hand with MATERIAL colours so the CON-4 nail semantics are actually visible,
# plus a 2D UV-layout drawing that shows the CON-7 local fix.
#
# usage: blender -b <stage4c.blend> --python stage4c_render.py -- <outdir> <run.json>
import bpy, sys, os, json, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR, RUNJSON = argv[0], argv[1]
os.makedirs(OUTDIR, exist_ok=True)
RUN = json.load(open(RUNJSON, encoding="utf-8"))
TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
MW = ob.matrix_world
W = [(MW @ v.co).copy() for v in ob.data.vertices]
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'
sc.display.shading.color_type = 'MATERIAL'
sc.display.render_aa = '8'
sc.render.resolution_x = 1200
sc.render.resolution_y = 1000
w = bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("W")
sc.world = w
w.color = (1.0, 1.0, 1.0)
cd = bpy.data.cameras.new("c"); cd.type = 'ORTHO'; cd.clip_start = 0.001
cam = bpy.data.objects.new("c", cd)
sc.collection.objects.link(cam); sc.camera = cam

# frame: reuse the Stage-4B CAMS.json so DORSAL / PALMAR stay comparable with earlier rounds
CAMS = json.load(open(os.path.join(os.path.dirname(RUNJSON), "..", "stage4b_rssf", "CAMS.json"),
                      encoding="utf-8"))


def shoot(centre, dirv, scale, out, res=(1200, 1000)):
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = out
    cd.ortho_scale = scale
    pos = Vector(centre) + Vector(dirv) * 0.9
    cam.location = pos
    cam.rotation_euler = (Vector(centre) - pos).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.render.render(write_still=True)
    print("RENDERED", os.path.basename(out), os.path.exists(out))


for tag in ("DORSAL", "PALMAR"):
    shoot(CAMS["centre"], CAMS["views"][tag], CAMS["ortho"],
          os.path.join(OUTDIR, "STAGE4C_%s.png" % tag))

# fingertips close-up: view ALONG the mean nail normal of the four fingers.  The fingers are
# semi-flexed, so their nail plates are tilted ~60 deg away from the global dorsal axis and
# read almost edge-on in a straight DORSAL view; the nail normal is the direction that shows
# the plate face-on.
nc = RUN["CON_4_nails"]["per_digit"]


def nail_pts(digits):
    pts = []
    for n in digits:
        for fi in nc[n]["faces"]:
            for v in ob.data.polygons[fi].vertices:
                pts.append(W[v])
    return pts


four = ("index", "middle", "ring", "little")
fpts = nail_pts(four)
fctr = sum(fpts, Vector()) / len(fpts)
fdir = sum((Vector(nc[n]["nail_normal"]) for n in four), Vector()).normalized()
shoot(fctr, fdir, 0.085, os.path.join(OUTDIR, "STAGE4C_FINGERTIPS.png"), res=(1400, 1000))

# thumb nail close-up.  The thumb nail faces almost exactly along the global dorsal axis
# (nail_normal . DORSAL = 0.90), so the nail plate needs no special angle -- but a straight
# DORSAL frame at thumb-tip scale puts the four fingers across the foreground.  The
# The frame is kept tight on the thumb nail (ortho 0.055) so the plate, not the fingers,
# dominates the picture.  RADIAL and OBLIQUE were both tried and are worse: from the radial
# side the thumb nail is edge-on (it faces the dorsal axis).
tpts = nail_pts(("thumb",))
tctr = sum(tpts, Vector()) / len(tpts)
shoot(tctr, CAMS["views"]["DORSAL"], 0.055,
      os.path.join(OUTDIR, "STAGE4C_THUMB_NAIL.png"), res=(1200, 1000))

# ------------------------------------------------------------------ UV layout drawing
# Draw the UV map as 2-D geometry: everything grey, the nail-region faces green, and the
# 64 CON-7 repaired faces orange -- so the local fix is visible at a glance.
uvl = ob.data.uv_layers.active
fixed = set(RUN["CON_7_uv"]["fix"].get("faces", []))
nail_faces = set()
for n in nc:
    nail_faces.update(nc[n]["faces"])
groups = {"other": ([], (0.72, 0.72, 0.74, 1.0)), "nail": ([], (0.10, 0.65, 0.25, 1.0)),
          "fixed": ([], (0.95, 0.45, 0.05, 1.0))}
for fi, p in enumerate(ob.data.polygons):
    key = "fixed" if fi in fixed else ("nail" if fi in nail_faces else "other")
    groups[key][0].append([tuple(uvl.data[li].uv) for li in p.loop_indices])
for key, (polys, col) in groups.items():
    if not polys:
        continue
    verts, faces = [], []
    for poly in polys:
        b = len(verts)
        verts += [(u, v, 0.0) for (u, v) in poly]
        faces.append(tuple(range(b, b + len(poly))))
    m = bpy.data.meshes.new("uv_" + key)
    m.from_pydata(verts, [], faces); m.update()
    o = bpy.data.objects.new("uv_" + key, m)
    sc.collection.objects.link(o)
    o.color = col
    print("UVGROUP", key, len(polys), "faces")
ob.hide_render = True
sc.display.shading.color_type = 'OBJECT'
shoot((0.5, 0.5, 0.0), Vector((0, 0, 1)), 1.06,
      os.path.join(OUTDIR, "STAGE4C_UV_LAYOUT.png"), res=(1100, 1100))
print("DONE")
