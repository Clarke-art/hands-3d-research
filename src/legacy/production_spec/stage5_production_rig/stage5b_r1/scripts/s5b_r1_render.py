# =====================================================================================
# STAGE5B_R1 -- static weight heatmap evidence (REST / ZERO POSE only).  No pose, no anim.
# =====================================================================================
import bpy, sys, os, json, math
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
REND = os.path.join(OUTDIR, "renders")
BLEND = os.path.join(OUTDIR, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend")
TOP = os.path.dirname(OUTDIR)
S4 = os.path.join(os.path.dirname(TOP), "stage4_blender")
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"),
                    encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
cand = json.load(open(os.path.join(TOP, "stage5a_r2", "_tmp", "S5A_R2_CANDIDATES.json"),
                      encoding="utf-8"))
AO = Vector(oa["WRIST_ORIGIN"])
DORSAL = {k: Vector(v) for k, v in cand["dorsal_refs"].items()}

bpy.ops.wm.open_mainfile(filepath=BLEND)
ob = bpy.data.objects["Hand  - Realistic"]
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
me = ob.data
MW = ob.matrix_world
V = [(MW @ v.co).copy() for v in me.vertices]
NV = len(V)
VG = {g.name: g.index for g in ob.vertex_groups}
W = [dict() for _ in range(NV)]
for name, gi in VG.items():
    vg = ob.vertex_groups[gi]
    for i in range(NV):
        try:
            w = vg.weight(i)
        except RuntimeError:
            continue
        if w > 0.0:
            W[i][name] = w

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
OWN = [min(AC, key=lambda D: d_poly(V[i], AC[D])) for i in range(NV)]
ELEN = sorted((V[a] - V[b]).length for a, b in
              [(e.vertices[0], e.vertices[1]) for e in me.edges])
MED_EDGE = ELEN[len(ELEN) // 2] * 1000.0
W_WEB = 2.0 * MED_EDGE * 1e-3

# ---------------------------------------------------------------- heatmap machinery
STOPS = [(0.00, (0.16, 0.16, 0.20)), (0.25, (0.10, 0.35, 0.85)),
         (0.50, (0.10, 0.80, 0.30)), (0.75, (0.95, 0.85, 0.10)), (1.00, (0.95, 0.10, 0.05))]


def ramp(t):
    t = max(0.0, min(1.0, t))
    for i in range(len(STOPS) - 1):
        a, ca = STOPS[i]; b, cb = STOPS[i + 1]
        if a <= t <= b:
            f = 0.0 if b == a else (t - a) / (b - a)
            return tuple(ca[k] + (cb[k] - ca[k]) * f for k in range(3))
    return STOPS[-1][1]


if "wcol" not in me.color_attributes:
    me.color_attributes.new("wcol", 'FLOAT_COLOR', 'POINT')
ca = me.color_attributes["wcol"]


def set_colors(vals):
    for i in range(NV):
        c = ramp(vals[i])
        ca.data[i].color = (c[0], c[1], c[2], 1.0)


mat = bpy.data.materials.new("WMAP")
mat.use_nodes = True
nt = mat.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
att = nt.nodes.new('ShaderNodeVertexColor'); att.layer_name = "wcol"
emi = nt.nodes.new('ShaderNodeEmission')
out = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(att.outputs[0], emi.inputs[0])
nt.links.new(emi.outputs[0], out.inputs[0])
if me.materials:
    me.materials[0] = mat
else:
    me.materials.append(mat)
for p in me.polygons:
    p.material_index = 0

scn = bpy.context.scene
for _e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        scn.render.engine = _e; break
    except Exception:
        continue
scn.render.resolution_x = 1300; scn.render.resolution_y = 1000
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
for _l in range(6):
    lt = bpy.data.lights.new("LL%d" % _l, 'POINT'); lt.energy = 30.0
    scn.collection.objects.link(bpy.data.objects.new("LO%d" % _l, lt))
rig.hide_render = True; rig.hide_viewport = True

C = sum(V, Vector()) / NV
d0 = (Vector(jf["INDEX_TIP_R"]["head"]) - Vector(jf["THUMB_CMC_R"]["head"])).normalized()
n0 = DORSAL["index"].normalized()
l0 = d0.cross(n0).normalized()
if l0.dot(Vector((1, 0, 0))) < 0:
    l0 = -l0
n0 = l0.cross(d0).normalized() * (1 if n0.dot(l0.cross(d0)) > 0 else -1)


def make_legend(cam, title):
    """color bar 0.0 -> 1.0 + title, parented to the camera"""
    bar = bpy.data.materials.new("BAR"); bar.use_nodes = True
    bnt = bar.node_tree
    for nd in list(bnt.nodes):
        bnt.nodes.remove(nd)
    tc = bnt.nodes.new('ShaderNodeTexCoord')
    sep = bnt.nodes.new('ShaderNodeSeparateXYZ')
    cr = bnt.nodes.new('ShaderNodeValToRGB')
    cr.color_ramp.interpolation = 'LINEAR'
    el = list(cr.color_ramp.elements)
    need = 5 - len(el)
    for _ in range(need):
        cr.color_ramp.elements.new(0.5)
    for k, (pos, col) in enumerate(STOPS):
        cr.color_ramp.elements[k].position = pos
        cr.color_ramp.elements[k].color = (col[0], col[1], col[2], 1.0)
    emi = bnt.nodes.new('ShaderNodeEmission'); outn = bnt.nodes.new('ShaderNodeOutputMaterial')
    bnt.links.new(tc.outputs[2], sep.inputs[0])
    bnt.links.new(sep.outputs[0], cr.inputs[0])
    bnt.links.new(cr.outputs[0], emi.inputs[0]); bnt.links.new(emi.outputs[0], outn.inputs[0])
    bpy.ops.mesh.primitive_plane_add(size=1.0)
    pl = bpy.context.object; pl.name = "BAR_OBJ"
    pl.parent = cam
    pl.location = (0.0, -0.62, -1.55)
    pl.rotation_euler = (0.0, 0.0, 0.0)
    pl.scale = (0.95, 0.10, 1.0)
    pl.data.materials.append(bar)
    objs = [pl]
    for txt, x in (("0.0", -0.50), ("0.5", 0.0), ("1.0", 0.50)):
        bpy.ops.object.text_add()
        t = bpy.context.object; t.name = "LT"
        t.data.body = txt; t.data.size = 0.10; t.data.align_x = 'CENTER'
        t.parent = cam
        t.location = (x, -0.62, -1.70)
        t.rotation_euler = (0.0, 0.0, 0.0)
        objs.append(t)
    bpy.ops.object.text_add()
    tt = bpy.context.object; tt.name = "LT"
    tt.data.body = title; tt.data.size = 0.13; tt.data.align_x = 'CENTER'
    tt.parent = cam
    tt.location = (0.0, -0.62, -1.38)
    tt.rotation_euler = (0.0, 0.0, 0.0)
    objs.append(tt)
    return objs


TARGETS = [
    ("STAGE5B_R1_WEIGHT_WRIST", {"WRIST_R": 1.0}, "WRIST_R", "dorsal"),
    ("STAGE5B_R1_WEIGHT_THUMB_CMC", {"THUMB_CMC_R": 1.0}, "THUMB_CMC_R", "dorsal"),
    ("STAGE5B_R1_WEIGHT_THUMB_MCP", {"THUMB_MCP_R": 1.0}, "THUMB_MCP_R", "dorsal"),
    ("STAGE5B_R1_WEIGHT_THUMB_IP", {"THUMB_IP_R": 1.0}, "THUMB_IP_R", "dorsal"),
    ("STAGE5B_R1_WEIGHT_INDEX_MCP", {"INDEX_MCP_R": 1.0}, "INDEX_MCP_R", "dorsal"),
    ("STAGE5B_R1_WEIGHT_INDEX_PIP", {"INDEX_PIP_R": 1.0}, "INDEX_PIP_R", "dorsal"),
    ("STAGE5B_R1_WEIGHT_INDEX_DIP", {"INDEX_DIP_R": 1.0}, "INDEX_DIP_R", "dorsal"),
    ("STAGE5B_R1_WEIGHT_FIRST_WEB", {"WRIST_R": 1.0, "THUMB_CMC_R": 1.0, "THUMB_MCP_R": 1.0,
                                      "INDEX_MCP_R": 1.0}, "FIRST WEB (sanctioned whitelist)", "web"),
    ("STAGE5B_R1_WEIGHT_PALM_FAN", {"INDEX_MCP_R": 1.0, "MIDDLE_MCP_R": 1.0, "RING_MCP_R": 1.0,
                                     "LITTLE_MCP_R": 1.0, "THUMB_CMC_R": 1.0},
     "PALM MCP FAN (WRIST dominant background)", "palm"),
    ("STAGE5B_R1_WEIGHT_CROSS_DIGIT_LEAK", None, "CROSS-DIGIT LEAK (non-sanctioned foreign weight)",
     "dorsal"),
    ("STAGE5B_R1_BIND_OVERVIEW_DORSAL", None, "BIND OVERVIEW (zero pose) - DORSAL", "dorsal"),
    ("STAGE5B_R1_BIND_OVERVIEW_PALMAR", None, "BIND OVERVIEW (zero pose) - PALMAR", "palmar"),
]

CAMV = {"dorsal": (0.35 * l0 + 0.95 * n0 + 0.10 * d0, 0.245),
        "palmar": (0.35 * l0 - 0.95 * n0 + 0.10 * d0, 0.245),
        "web": (0.75 * n0 + 0.55 * l0 + 0.30 * d0, 0.150),
        "palm": (0.60 * n0 + 0.70 * l0 + 0.20 * d0, 0.185)}

for name, spec, title, view in TARGETS:
    if spec is None:
        if "LEAK" in title:
            vals = [0.0] * NV
            for i in range(NV):
                own = OWN[i]
                for b, w in W[i].items():
                    bd = ("wrist" if b == "WRIST_R" else
                          [D for D in CHAIN if b.startswith(D)][0])
                    if bd == own or bd == "wrist":
                        continue
                    if own == "wrist" and b.endswith("_MCP_R"):
                        continue
                    if own in ("THUMB", "INDEX") and b in ("THUMB_CMC_R", "THUMB_MCP_R",
                                                           "INDEX_MCP_R", "WRIST_R"):
                        continue
                    vals[i] += w
            set_colors(vals)
        else:
            set_colors([0.55] * NV)                       # flat overview tint
    else:
        vals = [0.0] * NV
        for i in range(NV):
            vals[i] = sum(W[i].get(b, 0.0) * k for b, k in spec.items())
        set_colors(vals)
    dirv, dist = CAMV[view]
    cd = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cd)
    scn.collection.objects.link(cam)
    cam.location = C + dirv.normalized() * dist
    cam.rotation_euler = (C - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cd.lens = 40; cd.clip_start = 0.001; cd.clip_end = 5.0
    scn.camera = cam
    legend = make_legend(cam, title)
    scn.render.filepath = os.path.join(REND, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("[RENDER]", scn.render.filepath)
    for o in legend:
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.objects.remove(cam, do_unlink=True)
print("RENDER_DONE")
