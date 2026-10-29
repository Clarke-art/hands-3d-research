# =====================================================================================
# STAGE5A_R2A -- Human Review renders (READ-ONLY on the inputs; writes PNGs only)
#   renders/STAGE5A_R2A_THUMB_DISTAL_CAP_AUTHORITY.png
#   renders/STAGE5A_R2A_THUMB_TIP_SIDE.png
#   renders/STAGE5A_R2A_THUMB_TIP_DORSAL.png
# Only the thumb distal phalanx is shown; the other four fingers are hidden.
# =====================================================================================
import bpy, sys, os, json, math, heapq
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
REND = os.path.join(OUTDIR, "renders")
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
S5AR2 = r"<HANDS_ROOT>\production_spec\stage5_production_rig\stage5a_r2"
R2A = os.path.join(OUTDIR, "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")

jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
cand = json.load(open(os.path.join(S5AR2, "_tmp", "S5A_R2_CANDIDATES.json"), encoding="utf-8"))
build = json.load(open(os.path.join(OUTDIR, "_tmp", "S5A_R2A_BUILD_LOG.json"), encoding="utf-8"))
cap_audit = json.load(open(os.path.join(OUTDIR, "THUMB_DISTAL_CAP_AUDIT.json"), encoding="utf-8"))
DORSAL = {k: Vector(v) for k, v in cand["dorsal_refs"].items()}
AO = Vector(oa["WRIST_ORIGIN"])

def set_mat(mat, rgba):
    nt = mat.node_tree
    bsdf = None
    for nd in nt.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            bsdf = nd
            break
    if bsdf is None:
        for nd in nt.nodes:
            if nd.type == 'OUTPUT_MATERIAL':
                out = nd
                break
        else:
            out = nt.nodes.new('ShaderNodeOutputMaterial')
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        nt.links.new(bsdf.outputs[0], out.inputs[0])
    for nm in ("Base Color", "BaseColour", "Color"):
        if nm in bsdf.inputs:
            bsdf.inputs[nm].default_value = rgba
            break
    else:
        bsdf.inputs[0].default_value = rgba
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = 0.75
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = 0.0


bpy.ops.wm.open_mainfile(filepath=R2A)
ob = bpy.data.objects["Hand  - Realistic"]
me = ob.data
MW = ob.matrix_world
V = [(MW @ v.co).copy() for v in me.vertices]
FC = [sum((V[v] for v in p.vertices), Vector()) / len(p.vertices) for p in me.polygons]
IP = Vector(jf["THUMB_IP_R"]["head"])
APP_TIP = Vector(jf["THUMB_TIP_R"]["head"])
u0 = (APP_TIP - IP).normalized()

R1_TIP = APP_TIP.copy()
R2_TIP = Vector([1.456466794, 0.018134484, 0.48759535])
R2A_TIP = Vector(build["new_THUMB_TIP_world"])
STAR = Vector(cap_audit["thumb"]["distal_most_vertex_world"])
CAP_FACES = set(build["cap"]["face_ids"])
CAPC = Vector(build["cap"]["centroid_world"])

# ---------------------------------------------------------------- thumbnail mesh: thumb distal phalanx only
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"], "LITTLE": ["MCP", "PIP", "DIP"]}


def d_poly(p, poly):
    b = 1e9
    for i in range(len(poly) - 1):
        a, q = poly[i], poly[i + 1]; ab = q - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
        b = min(b, (p - (a + ab * t)).length)
    return b


def chp(D):
    p = [Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])]
    for s in CHAIN[D]:
        p.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
    return p


AC = {D: chp(D) for D in CHAIN}; AC["wrist"] = [AO, Vector(jf["WRIST_R"]["tail"])]
FO = {}
for p in me.polygons:
    FO[p.index] = min(AC, key=lambda D: d_poly(FC[p.index], AC[D]))

keep = [p.index for p in me.polygons
        if FO[p.index] == "THUMB" and (FC[p.index] - IP).dot(u0) > -0.004]
km = bpy.data.meshes.new("THUMB_DISTAL")
verts = sorted({v for fi in keep for v in me.polygons[fi].vertices})
idx = {v: i for i, v in enumerate(verts)}
km.from_pydata([tuple(me.vertices[v].co) for v in verts], [],
               [tuple(idx[v] for v in me.polygons[fi].vertices) for fi in keep])
km.update()
kob = bpy.data.objects.new("THUMB_DISTAL_OBJ", km)
kob.matrix_world = MW.copy()
bpy.context.scene.collection.objects.link(kob)

# material 0 = shell, material 1 = cap patch
m0 = bpy.data.materials.new("shell"); m0.use_nodes = True; set_mat(m0, (0.72, 0.66, 0.60, 1.0))
m1 = bpy.data.materials.new("cap"); m1.use_nodes = True; set_mat(m1, (1.0, 0.35, 0.05, 1.0))
km.materials.append(m0); km.materials.append(m1)
for p in km.polygons:
    p.material_index = 1 if keep[p.index] in CAP_FACES else 0

capc_show = [p.index for p in me.polygons if FO[p.index] == "THUMB"
             and (FC[p.index] - IP).dot(u0) > -0.004 and (FC[p.index] - IP).dot(u0) < 0.016]
C0 = sum((FC[fi] for fi in keep), Vector()) / len(keep)
ob.hide_render = True
ob.hide_viewport = True
for o in bpy.data.objects:
    if o.type == 'ARMATURE':
        o.hide_render = True; o.hide_viewport = True


def marker(name, pos, rgba, r=0.0016):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=tuple(pos), segments=16, ring_count=10)
    m = bpy.context.object
    m.name = name
    mm = bpy.data.materials.new(name); mm.use_nodes = True; set_mat(mm, rgba)
    m.data.materials.append(mm)
    return m


def label(txt, pos, rgba, size=0.0026):
    bpy.ops.object.text_add(location=tuple(pos))
    t = bpy.context.object
    t.name = "LBL_" + txt
    t.data.body = txt
    t.data.size = size
    t.data.align_x = 'LEFT'
    mm = bpy.data.materials.new("L_" + txt); mm.use_nodes = True; set_mat(mm, rgba)
    t.data.materials.append(mm)
    return t


marker("M_R2A_TIP", R2A_TIP, (0.05, 0.95, 0.15, 1.0), 0.0020)      # green  = R2A (kept)
marker("M_R2_TIP", R2_TIP, (0.10, 0.30, 1.00, 1.0), 0.0017)        # blue   = R2
marker("M_R1_TIP", R1_TIP, (0.95, 0.10, 0.85, 1.0), 0.0015)        # magenta= R1
marker("M_APEX", STAR, (1.0, 0.10, 0.05, 1.0), 0.0015)             # red    = distal-most vertex
marker("M_CAPREP", CAPC, (1.0, 0.85, 0.05, 1.0), 0.0013)           # yellow = cap centroid
marker("M_IP", IP, (0.25, 0.25, 0.25, 1.0), 0.0018)

LBL = [("R2A TIP", R2A_TIP, (0.05, 0.60, 0.10, 1.0)),
       ("R2 TIP", R2_TIP, (0.08, 0.25, 0.95, 1.0)),
       ("R1 TIP", R1_TIP, (0.85, 0.05, 0.80, 1.0)),
       ("APEX vtx", STAR, (0.95, 0.08, 0.03, 1.0)),
       ("CAP CENTROID", CAPC, (0.85, 0.70, 0.03, 1.0))]

C = sum((FC[fi] for fi in keep), Vector()) / len(keep)
d = (R2A_TIP - IP).normalized()
n = DORSAL["thumb"].normalized()
l = d.cross(n).normalized()
if l.dot(Vector((1, 0, 0))) < 0:
    l = -l
n = l.cross(d).normalized() * (1 if n.dot(l.cross(d)) > 0 else -1)

scn = bpy.context.scene
for _eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        scn.render.engine = _eng
        break
    except Exception:
        continue
print("[ENGINE]", scn.render.engine)
scn.display.shading.color_type = 'MATERIAL'
scn.display.shading.light = 'STUDIO'
scn.display.shading.studiolight_intensity = 1.1
scn.display.shading.show_shadows = False
scn.display.shading.background_type = 'VIEWPORT'
scn.display.shading.background_color = (1.0, 1.0, 1.0)
scn.display_settings.display_device = 'sRGB'
scn.render.resolution_x = 1400
scn.render.resolution_y = 1100
scn.render.image_settings.file_format = 'PNG'
scn.render.film_transparent = False
scn.view_settings.view_transform = 'Standard'
if scn.world is None:
    scn.world = bpy.data.worlds.new("W")
scn.world.color = (1, 1, 1)
try:
    scn.world.use_nodes = True
    bg = scn.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        bg.inputs[1].default_value = 1.0
except Exception as _e:
    print("world", _e)
w = bpy.data.worlds.get("W")
for _l in ("-Z", "-Y", "+X", "-X", "+Y", "+Z"):
    lt = bpy.data.lights.new("L" + _l, 'POINT')
    lt.energy = 40.0
    lo = bpy.data.objects.new("L" + _l, lt)
    scn.collection.objects.link(lo)

VIEWS = {
    "STAGE5A_R2A_THUMB_DISTAL_CAP_AUTHORITY": (0.55 * n + 0.62 * l + 0.35 * d),
    "STAGE5A_R2A_THUMB_TIP_SIDE": (l * 1.0 + 0.18 * n),
    "STAGE5A_R2A_THUMB_TIP_DORSAL": (n * 1.0 + 0.15 * d),
}
DIST = 0.135
for name, dirv in VIEWS.items():
    dv = dirv.normalized()
    cam_d = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cam_d)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = C + dv * DIST
    tgt = C
    direction = tgt - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    cam_d.lens = 42
    cam_d.clip_start = 0.001
    cam_d.clip_end = 5.0
    scn.camera = cam
    up = cam.matrix_world.to_3x3().col[1].normalized()
    rt = cam.matrix_world.to_3x3().col[0].normalized()
    for i, (txt, pos, rgba) in enumerate(LBL):
        lb = label(txt, pos + up * (0.004 + 0.0032 * i) - rt * 0.030, rgba, size=0.0030)
        lb.rotation_euler = cam.rotation_euler
    scn.render.filepath = os.path.join(REND, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("[RENDER]", scn.render.filepath)
    bpy.data.objects.remove(cam, do_unlink=True)
print("RENDER_DONE")
