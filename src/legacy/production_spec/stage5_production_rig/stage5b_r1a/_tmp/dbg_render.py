import bpy, sys, os, math
sys.path.append(r"<HANDS_ROOT>\production_spec\stage5_production_rig\stage5b_r1a\scripts")
import r1a_common as C
from mathutils import Vector

TOP = r"<HANDS_ROOT>\production_spec\stage5_production_rig"
OUT = os.path.join(TOP, "stage5b_r1a", "_tmp")
ref = C.load_reference(TOP)
NV = ref["NV"]; V0 = ref["V0"]; me = bpy.data.objects["Hand  - Realistic"]
GEO = ref["dij"](2189)
jf = ref["jf"]
CAP = set(ref["cap"]["thumb_cap_vertex_ids"])
NAILT = set(ref["NAIL_BY_DIGIT"]["THUMB"])

BANDS = [(0.0, 20.0, (0.95, 0.05, 0.05)), (20.0, 100.0, (0.95, 0.80, 0.05)),
         (100.0, 200.0, (0.10, 0.35, 0.95)), (200.0, 1e9, (0.55, 0.55, 0.60))]
def col(g):
    for a, b, c in BANDS:
        if a <= g < b:
            return c
    return BANDS[-1][2]

me2 = me.data
if "dbg" not in me2.color_attributes:
    me2.color_attributes.new("dbg", 'FLOAT_COLOR', 'POINT')
ca = me2.color_attributes["dbg"]
for i in range(NV):
    p = V0[i] * 1000
    dth = ref["dchain"][i]["THUMB"]
    if i in NAILT:
        c = (0.05, 0.95, 0.05)                     # thumb nail verts = green
    elif i in CAP:
        c = (0.85, 0.10, 0.85)                     # cap patch = magenta
    elif dth < 25:
        c = col(GEO[i] * 1000)
    else:
        c = (0.72, 0.72, 0.75)
    ca.data[i].color = (c[0], c[1], c[2], 1.0)

mat = bpy.data.materials.new("DBG"); mat.use_nodes = True
nt = mat.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
att = nt.nodes.new('ShaderNodeVertexColor'); att.layer_name = "dbg"
emi = nt.nodes.new('ShaderNodeEmission')
out = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(att.outputs[0], emi.inputs[0]); nt.links.new(emi.outputs[0], out.inputs[0])
me2.materials.clear(); me2.materials.append(mat)
for p in me2.polygons: p.material_index = 0

scn = bpy.context.scene
for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try: scn.render.engine = e; break
    except Exception: pass
scn.render.resolution_x = 1100; scn.render.resolution_y = 900
scn.render.image_settings.file_format = 'PNG'
scn.view_settings.view_transform = 'Standard'
scn.world.use_nodes = True
bg = scn.world.node_tree.nodes.get("Background")
if bg: bg.inputs[0].default_value = (1,1,1,1); bg.inputs[1].default_value = 1.0
for l in range(6):
    lt = bpy.data.lights.new("L%d"%l, 'POINT'); lt.energy = 30.0
    scn.collection.objects.link(bpy.data.objects.new("A%d"%l, lt))
bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"].hide_render = True

# focus on the thumb
sel = [i for i in range(NV) if ref["dchain"][i]["THUMB"] < 40]
F = sum((V0[i] for i in sel), Vector()) / len(sel)
DORS = Vector([0.631289124, 0.775318801, -0.0188387]).normalized()
AX = (Vector(jf["THUMB_IP_R"]["head"]) - Vector(jf["THUMB_CMC_R"]["head"])).normalized()
LAT = AX.cross(DORS).normalized()
if LAT.dot(Vector((1,0,0))) < 0: LAT = -LAT
DORS = LAT.cross(AX).normalized() * (1 if DORS.dot(LAT.cross(AX)) > 0 else -1)

VIEWS = {"DORSAL": (DORS + 0.15*AX, 0.13), "PALMAR": (-DORS + 0.15*AX, 0.13),
         "SIDE1": (LAT + 0.20*AX, 0.13), "SIDE2": (-LAT + 0.20*AX, 0.13),
         "TIPON": (AX + 0.35*DORS, 0.10)}
for nm, (dv, dist) in VIEWS.items():
    cd = bpy.data.cameras.new(nm); cam = bpy.data.objects.new(nm, cd)
    scn.collection.objects.link(cam)
    cam.location = F + dv.normalized() * dist
    cam.rotation_euler = (F - cam.location).to_track_quat('-Z','Y').to_euler()
    cd.lens = 50; cd.clip_start = 0.001
    scn.camera = cam
    scn.render.filepath = os.path.join(OUT, "DBG_%s.png" % nm)
    bpy.ops.render.render(write_still=True)
    print("[DBG]", scn.render.filepath)
print("DBG_DONE")
