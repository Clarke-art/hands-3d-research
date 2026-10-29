# =====================================================================================
# STAGE5A_R2B -- Human Review evidence renders (Branch B).  READ-ONLY on the inputs.
#   renders/STAGE5A_R2B_THUMB_IP_FEASIBILITY_MAP.png
#   renders/STAGE5A_R2B_THUMB_CHAIN_BEFORE_AFTER.png
#   renders/STAGE5A_R2B_THUMB_IP_CLOSEUP.png
# =====================================================================================
import bpy, sys, os, json, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
REND = os.path.join(OUTDIR, "renders")
TOP = os.path.dirname(OUTDIR)                                   # .../stage5_production_rig
S4 = os.path.join(os.path.dirname(os.path.dirname(OUTDIR)), "stage4_blender")
S5AR2 = os.path.join(TOP, "stage5a_r2")
R2A = os.path.join(TOP, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
DIAG = json.load(open(os.path.join(OUTDIR, "THUMB_STRAIGHT_BONE_COMPATIBILITY_DIAGNOSIS.json"),
                      encoding="utf-8"))
VOL = json.load(open(os.path.join(OUTDIR, "STAGE5A_R2B_THUMB_IP_FEASIBILITY_VOLUME.json"),
                     encoding="utf-8"))
VER = json.load(open(os.path.join(OUTDIR, "_tmp", "S5A_R2B_STRICT_VERIFY.json"), encoding="utf-8"))
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
cand = json.load(open(os.path.join(S5AR2, "_tmp", "S5A_R2_CANDIDATES.json"), encoding="utf-8"))
DORSAL = {k: Vector(v) for k, v in cand["dorsal_refs"].items()}
AO = Vector(oa["WRIST_ORIGIN"])

MCP = Vector((1.454060912, 0.001536574, 0.436873049))
IP0 = Vector((1.450860858, 0.006127121, 0.464001149))
TIP = Vector((1.45281744, 0.019802358, 0.493028343))
CMCv = Vector((1.440895081, 0.001219887, 0.3918145))
BESTZ = Vector(DIAG["best_near_feasible_candidate_in_zone"]["world_position"])
BESTT = Vector(DIAG["wide_scan_maxima"]["max_IP_TO_TIP_position"]["world_position"])
BESTC = Vector(DIAG["wide_scan_maxima"]["best_combined_position"]["world_position"])
CLOUD = [Vector(r["world_position"]) for r in DIAG["all_in_zone_records"]]

bpy.ops.wm.open_mainfile(filepath=R2A)
ob = bpy.data.objects["Hand  - Realistic"]; me = ob.data
MW = ob.matrix_world
V = [(MW @ v.co).copy() for v in me.vertices]
FC = [sum((V[v] for v in p.vertices), Vector()) / len(p.vertices) for p in me.polygons]
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
IPj = Vector(jf["THUMB_IP_R"]["head"])
TIPj = Vector(jf["THUMB_TIP_R"]["head"])
u0 = (TIPj - IPj).normalized()
keep = [p.index for p in me.polygons if FO[p.index] == "THUMB"]


def set_mat(mat, rgba, alpha=1.0):
    nt = mat.node_tree
    bsdf = None
    for nd in nt.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            bsdf = nd; break
    if bsdf is None:
        out = None
        for nd in nt.nodes:
            if nd.type == 'OUTPUT_MATERIAL':
                out = nd; break
        if out is None:
            out = nt.nodes.new('ShaderNodeOutputMaterial')
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        nt.links.new(bsdf.outputs[0], out.inputs[0])
    for nm in ("Base Color", "BaseColour", "Color"):
        if nm in bsdf.inputs:
            bsdf.inputs[nm].default_value = rgba; break
    else:
        bsdf.inputs[0].default_value = rgba
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = 0.7
    if "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha
    try:
        mat.blend_method = 'BLEND' if alpha < 1.0 else 'OPAQUE'
    except Exception:
        pass
    try:
        mat.shadow_method = 'NONE' if alpha < 1.0 else 'OPAQUE'
    except Exception:
        pass
    try:
        mat.use_backface_culling = False
    except Exception:
        pass


km = bpy.data.meshes.new("THUMB")
verts = sorted({v for fi in keep for v in me.polygons[fi].vertices})
idx = {v: i for i, v in enumerate(verts)}
km.from_pydata([tuple(me.vertices[v].co) for v in verts], [],
               [tuple(idx[v] for v in me.polygons[fi].vertices) for fi in keep])
km.update()
kob = bpy.data.objects.new("THUMB_OBJ", km)
kob.matrix_world = MW.copy()
bpy.context.scene.collection.objects.link(kob)
ms = bpy.data.materials.new("shell"); ms.use_nodes = True; set_mat(ms, (0.72, 0.66, 0.60, 1.0), 0.35)
km.materials.append(ms)
for p in km.polygons:
    p.material_index = 0
ob.hide_render = True; ob.hide_viewport = True
for o in bpy.data.objects:
    if o.type == 'ARMATURE':
        o.hide_render = True; o.hide_viewport = True


def marker(name, pos, rgba, r=0.0012):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=tuple(pos), segments=12, ring_count=8)
    m = bpy.context.object; m.name = name
    mm = bpy.data.materials.new(name); mm.use_nodes = True; set_mat(mm, rgba)
    m.data.materials.append(mm)
    return m


def label(txt, pos, rgba, size=0.0032):
    bpy.ops.object.text_add(location=tuple(pos))
    t = bpy.context.object; t.name = "L_" + txt
    t.data.body = txt; t.data.size = size; t.data.align_x = 'LEFT'
    mm = bpy.data.materials.new("LT_" + txt); mm.use_nodes = True; set_mat(mm, rgba)
    t.data.materials.append(mm)
    return t


for i, p in enumerate(CLOUD):
    marker("C%03d" % i, p, (0.30, 0.60, 1.00, 1.0), 0.00055)
marker("M_MCP", MCP, (0.25, 0.25, 0.25, 1.0), 0.0018)
marker("M_IP", IP0, (1.0, 0.10, 0.05, 1.0), 0.0020)
marker("M_TIP", TIP, (0.05, 0.90, 0.15, 1.0), 0.0020)
marker("M_CMC", CMCv, (0.15, 0.15, 0.35, 1.0), 0.0016)
marker("M_BESTZ", BESTZ, (1.0, 0.90, 0.05, 1.0), 0.0026)
marker("M_BESTT", BESTT, (0.10, 0.90, 0.95, 1.0), 0.0022)
marker("M_BESTC", BESTC, (0.95, 0.10, 0.85, 1.0), 0.0022)

LBL = [("CMC", CMCv, (0.10, 0.10, 0.30, 1.0)),
       ("MCP (frozen)", MCP, (0.20, 0.20, 0.20, 1.0)),
       ("current IP (R2A)", IP0, (0.90, 0.05, 0.02, 1.0)),
       ("TIP (R2A frozen)", TIP, (0.02, 0.65, 0.10, 1.0)),
       ("best in zone 36/40", BESTZ, (0.85, 0.78, 0.02, 1.0)),
       ("IP->TIP 40/40 (MCP->IP 20/40)", BESTT, (0.05, 0.75, 0.80, 1.0)),
       ("best combined 35/40 (OUTSIDE zone)", BESTC, (0.80, 0.05, 0.72, 1.0)),
       ("searched T-01 cloud n=%d" % len(CLOUD), CLOUD[0], (0.20, 0.45, 0.85, 1.0))]

scn = bpy.context.scene
for _eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        scn.render.engine = _eng; break
    except Exception:
        continue
scn.display.shading.background_type = 'VIEWPORT'
scn.display.shading.background_color = (1.0, 1.0, 1.0)
scn.display_settings.display_device = 'sRGB'
scn.render.resolution_x = 1500; scn.render.resolution_y = 1150
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
        bg.inputs[0].default_value = (1, 1, 1, 1); bg.inputs[1].default_value = 1.0
except Exception:
    pass
for _l in ("A", "B", "C", "D", "E", "F"):
    lt = bpy.data.lights.new("L" + _l, 'POINT'); lt.energy = 45.0
    lo = bpy.data.objects.new("L" + _l, lt); scn.collection.objects.link(lo)

C = sum((FC[fi] for fi in keep), Vector()) / len(keep)
d = (TIP - CMCv).normalized()
n = DORSAL["thumb"].normalized()
l = d.cross(n).normalized()
if l.dot(Vector((1, 0, 0))) < 0:
    l = -l
n = l.cross(d).normalized() * (1 if n.dot(l.cross(d)) > 0 else -1)

VIEWS = {
    "STAGE5A_R2B_THUMB_IP_FEASIBILITY_MAP": (C, 0.55 * n + 0.60 * l + 0.30 * d, 0.175),
    "STAGE5A_R2B_THUMB_CHAIN_BEFORE_AFTER": (C, 0.20 * n + 1.00 * l, 0.175),
    "STAGE5A_R2B_THUMB_IP_CLOSEUP": (IP0, 0.45 * n + 0.55 * l + 0.45 * d, 0.085),
}
for name, (tgt, dirv, dist) in VIEWS.items():
    dv = dirv.normalized()
    cd = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = tgt + dv * dist
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cd.lens = 45 if dist > 0.1 else 60
    cd.clip_start = 0.001; cd.clip_end = 5.0
    scn.camera = cam
    up = cam.matrix_world.to_3x3().col[1].normalized()
    rt = cam.matrix_world.to_3x3().col[0].normalized()
    for i, (txt, pos, rgba) in enumerate(LBL):
        lb = label(txt, pos + up * (0.004 + 0.0042 * i) - rt * 0.045, rgba)
        lb.rotation_euler = cam.rotation_euler
    scn.render.filepath = os.path.join(REND, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("[RENDER]", scn.render.filepath)
    for o in list(bpy.data.objects):
        if o.name.startswith("L_"):
            bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.objects.remove(cam, do_unlink=True)
print("RENDER_DONE")
