# STAGE4B RSSF evidence renders.  Read-only: the blend is never saved.
#
# The camera spec (position / rotation / ortho scale for every view) is computed ONCE from
# the Stage-4A baseline and written to CAMS.json, then reused verbatim for the BEFORE and
# the AFTER render, so both are the same camera, same scale, same framing.
#
# ==========================================================================================
# OUTPUT POLICY
#   (STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT -> TEMP_OUTPUT_ISOLATION = PATCHED,
#    GLOB_DELETE_POLICY = PROHIBITED)
#
#   TEMP_RENDER_OUTPUT_DIR  = <stage4b_rssf>/_tmp/
#       single-side frames  : _tmp/RSSF_BEF_*.png , _tmp/RSSF_AFT_*.png
#       probe / overlay / debug intermediates : _tmp/
#
#   FINAL_RENDER_OUTPUT_DIR = <stage4b_rssf>/renders/
#       ONLY the Human-Review deliverables:
#         RSSF_BEFORE_AFTER_{DORSAL,PALMAR,RADIAL,OBLIQUE}.png
#         RSSF_CMC_CLOSEUP.png
#         RSSF_SKELETON_OVERLAY.png
#
#   The FINAL directory is protected by an explicit ALLOW-LIST of deliverable file names
#   (see FINAL_ALLOWED below).  Anything else -- every temp frame, every probe output -- is
#   refused with a hard error instead of being written.  An allow-list is used deliberately:
#   the incident was caused by the prefix test "RSSF_BEFORE_*", which also matches the
#   deliverable "RSSF_BEFORE_AFTER_*".  A prefix rule cannot separate those two names;
#   an exact-name allow-list can.
#
#   This script performs NO deletion of any kind: no unlink, no glob delete, no recursive
#   delete, no prefix-wildcard delete.  It only ever creates or overwrites a file it was
#   explicitly asked to create.  Cleanup is a separate, human-approved action.
# ==========================================================================================
#
# usage: blender -b <blend> --python stage4b_render.py -- <final_dir> <tag> <cams.json> <mode> [temp_dir] [tag2] [profile]
#   mode = views -> <TEMP>/RSSF_<TAG>_{DORSAL,PALMAR,RADIAL,OBLIQUE}.png + <TEMP>/RSSF_<TAG>_CMC.png
#   mode = skel  -> <FINAL>/RSSF_SKELETON_OVERLAY.png
#   mode = pairs -> compose the BEFORE/AFTER deliverables into <FINAL> from the <TEMP>
#                   single-side frames (tag = BEFORE side, tag2 = AFTER side).
#                   profile "R1" (default) -> RSSF_BEFORE_AFTER_*.png / RSSF_CMC_CLOSEUP.png
#                   profile "R2"           -> RSSF_R2_* equivalents
#   temp_dir defaults to "<final_dir>/../_tmp"
import bpy, bmesh, sys, os, json, math, heapq
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
FINAL, TAG, CAMJSON, MODE = argv[0], argv[1], argv[2], argv[3]
TMP = argv[4] if len(argv) > 4 else os.path.join(os.path.dirname(os.path.abspath(FINAL)) or ".", "_tmp")
os.makedirs(FINAL, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

# ---- the temp directory must be a genuinely separate scratch location --------------------
if os.path.abspath(TMP) == os.path.abspath(FINAL):
    raise SystemExit("REFUSED: temp_dir == final_dir ('%s').  Temp frames must not be "
                     "written into the FINAL render directory." % FINAL)
if os.path.basename(os.path.normpath(TMP)) == "renders":
    raise SystemExit("REFUSED: temp_dir '%s' is a 'renders' directory.  Temp frames belong "
                     "in a _tmp/ scratch directory." % TMP)

# ---- FINAL directory allow-list -----------------------------------------------------------
FINAL_ALLOWED = {"RSSF_SKELETON_OVERLAY.png", "RSSF_CMC_CLOSEUP.png"}
for _v in ("DORSAL", "PALMAR", "RADIAL", "OBLIQUE"):
    FINAL_ALLOWED.add("RSSF_BEFORE_AFTER_%s.png" % _v)
# R2 pose-semantic-correction deliverables (STAGE4B_RSSF_POSE_SEMANTIC_CORRECTION_R2).
# Added to THIS allow-list explicitly: new deliverables must be named here, the guard must
# never be relaxed into a pattern.
FINAL_ALLOWED.add("RSSF_R2_CMC_CLOSEUP.png")
for _v in ("DORSAL", "PALMAR", "RADIAL", "OBLIQUE"):
    FINAL_ALLOWED.add("RSSF_R2_BEFORE_AFTER_%s.png" % _v)
# The names the incident proved a prefix rule cannot separate from the deliverables above.
TEMP_ONLY_NAMES = ("RSSF_BEF_", "RSSF_AFT_", "RSSF_BEFORE_", "RSSF_AFTER_", "RSSF_R2BEF_",
                   "RSSF_R2AFT_")


def final_path(name):
    """Return a destination inside the FINAL directory, or refuse.

    Refuses any name that is not an exact deliverable, and names the incident prefix rule
    explicitly so a future edit cannot quietly reintroduce it.
    """
    if name not in FINAL_ALLOWED:
        for bad in TEMP_ONLY_NAMES:
            if name.startswith(bad):
                raise SystemExit(
                    "REFUSED: '%s' looks like a temp frame (prefix '%s') but the destination "
                    "is the FINAL render directory '%s'.  Temp frames go to the temp "
                    "directory '%s'.  This is exactly the P0 incident: 'RSSF_BEFORE_*' also "
                    "matches the deliverable 'RSSF_BEFORE_AFTER_*'." % (name, bad, FINAL, TMP))
        raise SystemExit("REFUSED: '%s' is not in the FINAL allow-list for '%s'." % (name, FINAL))
    return os.path.join(FINAL, name)


TARGET = "Hand  - Realistic"
M_NORM = Matrix(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)))
TIP_SEEDS = {
    "little": Vector((1.3515, 0.0319, 0.1879)), "ring": Vector((1.3933, 0.0320, 0.1599)),
    "middle": Vector((1.4231, 0.0251, 0.1490)), "index": Vector((1.4586, 0.0239, 0.1643)),
    "thumb": Vector((1.4977, 0.0358, 0.2421)),
}
FOREARM_SEED = Vector((1.4048, 0.0113, 0.4316))
CMC_APPROVED = Vector((1.448897, 0.011106, 0.393934))

if MODE == "pairs":
    # No blend geometry is needed for the composite step.
    import numpy as np

    def compose(left, right, out, gap_px=14, gap_level=0.10):
        la = bpy.data.images.load(os.path.abspath(left))
        lb = bpy.data.images.load(os.path.abspath(right))
        W, H = la.size
        ga = np.empty(W * H * 4, dtype=np.float32)
        gb = np.empty(W * H * 4, dtype=np.float32)
        la.pixels.foreach_get(ga)
        lb.pixels.foreach_get(gb)
        ga = ga.reshape(H, W, 4)
        gb = gb.reshape(H, W, 4)
        gap = np.ones((H, gap_px, 4), dtype=np.float32)
        gap[:, :, :3] = gap_level
        strip = np.concatenate([ga, gap, gb], axis=1)
        img = bpy.data.images.new("ba", width=strip.shape[1], height=H, alpha=True)
        img.pixels.foreach_set(strip.ravel())
        img.filepath_raw = os.path.abspath(out)
        img.file_format = 'PNG'
        img.save()
        print("WROTE", out)
        for im in (la, lb, img):
            try:
                bpy.data.images.remove(im)
            except Exception:
                pass

    T2 = argv[5] if len(argv) > 5 else "AFT"
    # output naming profile: "R1" -> RSSF_BEFORE_AFTER_*.png / RSSF_CMC_CLOSEUP.png
    #                        "R2" -> RSSF_R2_BEFORE_AFTER_*.png / RSSF_R2_CMC_CLOSEUP.png
    PROFILE = argv[6] if len(argv) > 6 else "R1"
    if PROFILE == "R2":
        PREFIX, CMC_NAME = "RSSF_R2_BEFORE_AFTER_", "RSSF_R2_CMC_CLOSEUP.png"
    else:
        PREFIX, CMC_NAME = "RSSF_BEFORE_AFTER_", "RSSF_CMC_CLOSEUP.png"
    for nm in ("DORSAL", "PALMAR", "RADIAL", "OBLIQUE"):
        compose(os.path.join(TMP, "RSSF_%s_%s.png" % (TAG, nm)),
                os.path.join(TMP, "RSSF_%s_%s.png" % (T2, nm)),
                final_path("%s%s.png" % (PREFIX, nm)))
    compose(os.path.join(TMP, "RSSF_%s_CMC.png" % TAG),
            os.path.join(TMP, "RSSF_%s_CMC.png" % T2),
            final_path(CMC_NAME))
    print("DONE")
    raise SystemExit(0)

ob = bpy.data.objects[TARGET]
MW = ob.matrix_world
LOC0 = MW.translation
canon = lambda p: (M_NORM @ p) + (LOC0 - (M_NORM @ LOC0))
CO = [(MW @ v.co).copy() for v in ob.data.vertices]
NV = len(CO)
nearest = lambda p: min(range(NV), key=lambda i: (CO[i] - p).length_squared)
FOREARM = CO[nearest(canon(FOREARM_SEED))]
TIPV = {n: nearest(canon(s)) for n, s in TIP_SEEDS.items()}
D_DIST = (CO[TIPV["middle"]] - FOREARM).normalized()
R_RAD = (CO[TIPV["index"]] - CO[TIPV["little"]]).normalized()
R_RAD = (R_RAD - D_DIST * R_RAD.dot(D_DIST)).normalized()
DORSAL = D_DIST.cross(R_RAD).normalized()
CMC = CO[nearest(CMC_APPROVED)]

if os.path.exists(CAMJSON):
    CAMS = json.load(open(CAMJSON, encoding="utf-8"))
else:
    lo = Vector((min(p.x for p in CO), min(p.y for p in CO), min(p.z for p in CO)))
    hi = Vector((max(p.x for p in CO), max(p.y for p in CO), max(p.z for p in CO)))
    ctr = (lo + hi) / 2
    ext = (hi - lo).length
    obl = (DORSAL * 0.72 + R_RAD * 0.72).normalized()
    CAMS = {"centre": list(ctr), "ortho": round(ext * 1.05, 5),
            "views": {"DORSAL": list(DORSAL), "PALMAR": list(-DORSAL),
                      "RADIAL": list(R_RAD), "OBLIQUE": list(obl)},
            "cmc": {"centre": list(CMC), "dir": list(DORSAL), "ortho": 0.085}}
    json.dump(CAMS, open(CAMJSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("WROTE", CAMJSON)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'OBJECT'
scene.display.render_aa = '8'
scene.render.resolution_x = 1200
scene.render.resolution_y = 1000
w = bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("W")
scene.world = w
w.color = (1.0, 1.0, 1.0)
cd = bpy.data.cameras.new("c"); cd.type = 'ORTHO'; cd.clip_start = 0.001
cam = bpy.data.objects.new("c", cd)
scene.collection.objects.link(cam); scene.camera = cam
ob.color = (0.90, 0.90, 0.92, 1.0)


def shoot(centre, dirv, scale, out):
    scene.render.filepath = out
    cd.ortho_scale = scale
    pos = Vector(centre) + Vector(dirv) * 0.9
    cam.location = pos
    cam.rotation_euler = (Vector(centre) - pos).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.render.render(write_still=True)
    print("RENDERED", os.path.basename(out), os.path.exists(out))


if MODE == "views":
    # single-side frames ALWAYS go to the temp directory, never to the final directory
    for nm, dv in CAMS["views"].items():
        shoot(CAMS["centre"], dv, CAMS["ortho"],
              os.path.join(TMP, "RSSF_%s_%s.png" % (TAG, nm)))
    shoot(CAMS["cmc"]["centre"], CAMS["cmc"]["dir"], CAMS["cmc"]["ortho"],
          os.path.join(TMP, "RSSF_%s_CMC.png" % TAG))
else:
    arm = bpy.data.objects.get("TEMP_RSSF_REPOSE_ARMATURE")
    if arm is None:
        raise SystemExit("no armature in this blend")


    def tube(points, radius, sides=6):
        verts, faces = [], []
        for i in range(len(points) - 1):
            p, q = points[i], points[i + 1]
            t = (q - p)
            if t.length < 1e-12:
                continue
            t.normalize()
            ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
            n1 = (ref - t * ref.dot(t)).normalized(); n2 = t.cross(n1)
            base = len(verts)
            for c in (p, q):                       # BOTH rings must exist before the faces
                for k in range(sides):
                    a = 2 * math.pi * k / sides
                    verts.append(c + (n1 * math.cos(a) + n2 * math.sin(a)) * radius)
            for k in range(sides):
                k2 = (k + 1) % sides
                faces.append((base + k, base + k2, base + sides + k2, base + sides + k))
        return verts, faces


    def make(name, verts, faces, color):
        m = bpy.data.meshes.new(name)
        m.from_pydata([tuple(v) for v in verts], [], faces)
        m.update()
        o = bpy.data.objects.new(name, m)
        scene.collection.objects.link(o)
        o.color = color
        return o


    for b in arm.data.bones:
        h = arm.matrix_world @ b.head_local
        t = arm.matrix_world @ b.tail_local
        vs, fc = tube([Vector(h), Vector(t)], 0.0011)
        col = (1.0, 0.45, 0.0, 1.0) if b.name.endswith("_TIP_R") else (0.10, 0.35, 0.90, 1.0)
        make("bone_%s" % b.name, vs, fc, col)
        for p, c in ((h, (0.85, 0.10, 0.10, 1.0)),):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0018, location=tuple(p))
            bpy.context.active_object.color = c
    ob.color = (0.93, 0.93, 0.95, 1.0)
    scene.display.shading.show_xray = True
    scene.display.shading.xray_alpha = 0.35
    shoot(CAMS["centre"], CAMS["views"]["DORSAL"], CAMS["ortho"],
          final_path("RSSF_SKELETON_OVERLAY.png"))
print("DONE")
