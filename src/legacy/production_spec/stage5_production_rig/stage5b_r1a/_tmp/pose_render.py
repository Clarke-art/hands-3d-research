import bpy, sys, os, math, json
sys.path.append(r"<HANDS_ROOT>\production_spec\stage5_production_rig\stage5b_r1a\scripts")
import r1a_common as C
from mathutils import Vector

TOP = r"<HANDS_ROOT>\production_spec\stage5_production_rig"
OUT = os.path.join(TOP, "stage5b_r1a", "_tmp")
ref = C.load_reference(TOP)
NV = ref["NV"]; V0 = ref["V0"]; me = bpy.data.objects["Hand  - Realistic"]
TF = C.thumb_frame(ref); ARC = TF["arc_thumb_mm"]
sMCP, sIP = TF["s_MCP_joint_mm"], TF["s_IP_joint_mm"]
MED = ref["med_edge"]; TAU = MED
own = ref["OWN_V"]
TNAIL = C.thumb_masks(ref, TF, TAU, 13.3, 30.0)["nail_thumb_vertices"]
CAP = set(ref["cap"]["thumb_cap_vertex_ids"])

me2 = me.data
if "dbg2" not in me2.color_attributes:
    me2.color_attributes.new("dbg2", 'FLOAT_COLOR', 'POINT')
ca = me2.color_attributes["dbg2"]
COL = {"THUMB": (0.90, 0.15, 0.15), "INDEX": (0.15, 0.35, 0.90), "MIDDLE": (0.15, 0.75, 0.20),
       "RING": (0.90, 0.75, 0.10), "LITTLE": (0.60, 0.25, 0.75), "wrist": (0.80, 0.80, 0.82)}
for i in range(NV):
    c = COL[own[i]]
    if i in TNAIL: c = (0.05, 0.95, 0.95)          # thumb nail = cyan
    if i in CAP:   c = (1.0, 0.0, 1.0)             # cap = magenta
    if own[i] == "THUMB" and ARC[i] <= sIP - TAU:  # thumb proximal of IP -> brighter red
        c = (0.60, 0.05, 0.05)
    ca.data[i].color = (c[0], c[1], c[2], 1.0)

mat = bpy.data.materials.new("DBG2"); mat.use_nodes = True
nt = mat.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
att = nt.nodes.new('ShaderNodeVertexColor'); att.layer_name = "dbg2"
emi = nt.nodes.new('ShaderNodeEmission'); outn = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(att.outputs[0], emi.inputs[0]); nt.links.new(emi.outputs[0], outn.inputs[0])
me2.materials.clear(); me2.materials.append(mat)
for p in me2.polygons: p.material_index = 0

scn = bpy.context.scene
for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try: scn.render.engine = e; break
    except Exception: pass
scn.render.resolution_x = 1400; scn.render.resolution_y = 1000
scn.render.image_settings.file_format = 'PNG'
scn.view_settings.view_transform = 'Standard'
scn.world.use_nodes = True
bg = scn.world.node_tree.nodes.get("Background")
if bg: bg.inputs[0].default_value = (1,1,1,1); bg.inputs[1].default_value = 1.0
for l in range(6):
    lt = bpy.data.lights.new("L%d"%l, 'POINT'); lt.energy = 30.0
    scn.collection.objects.link(bpy.data.objects.new("A%d"%l, lt))
bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"].hide_render = True

VH = V0[:]
Ctr = sum(VH, Vector()) / NV
R = max((v - Ctr).length for v in VH)
DORS = Vector([0.631289124, 0.775318801, -0.0188387]).normalized()
AX = (Vector(ref["jf"]["MIDDLE_TIP_R"]["head"]) - Vector(ref["jf"]["WRIST_R"]["head"])).normalized()
for nm, dv in (("DORSAL", DORS), ("PALMAR", -DORS), ("SIDE", DORS.cross(AX).normalized())):
    cd = bpy.data.cameras.new(nm); cam = bpy.data.objects.new(nm, cd)
    scn.collection.objects.link(cam)
    cam.location = Ctr + dv.normalized() * (R * 2.6)
    cam.rotation_euler = (Ctr - cam.location).to_track_quat('-Z','Y').to_euler()
    cd.lens = 45; cd.clip_start = 0.001
    scn.camera = cam
    scn.render.filepath = os.path.join(OUT, "POSE_%s.png" % nm)
    bpy.ops.render.render(write_still=True)
print("POSE_DONE")
