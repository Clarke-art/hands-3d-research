# =====================================================================================
# STAGE5B_R1A -- static weight / region evidence renders (REST / ZERO POSE only)
#   * identical camera basis, lighting, legend and 0.0-1.0 range for every image,
#     so R1 and R1A heatmaps are directly comparable
#   * before/after panels render BOTH states in ONE frame (two mesh copies) so the
#     camera / lighting / legend are provably identical
#   * nothing is written back to any .blend
# =====================================================================================
import bpy
import sys
import os
import json
import math
from mathutils import Vector, Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import r1a_common as C                                   # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
TOP = os.path.dirname(OUTDIR)
REND = os.path.join(OUTDIR, "renders")
R1 = os.path.join(TOP, "stage5b_r1", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend")
R1A = os.path.join(OUTDIR, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend")

LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[R1A-RENDER]", s)


# ---- read the R1 weights first (opening a blend resets the session) -----------------
b1 = C.load_weights(R1)
W1 = b1["W"]
NV = b1["NV"]
bA = C.load_weights(R1A)
WA = bA["W"]
ob = bA["ob"]
me = ob.data
MW = bA["MW"]
V = [(MW @ v.co).copy() for v in me.vertices]
log("loaded R1 + R1A ; NV=%d" % NV)

# ---- reference frame (identical to the Stage5B_R1 render script) --------------------
ref = C.load_reference(TOP)                              # NOTE: re-opens the master!
bA = C.load_weights(R1A)
ob = bA["ob"]
me = ob.data
MW = bA["MW"]
V = [(MW @ v.co).copy() for v in me.vertices]
jf = ref["jf"]
oa = ref["oa"]
TD = C.thumb_frame(ref)
ARC = TD["arc_thumb_mm"]
TAU = ref["med_edge"]
RG = C.build_regions(ref, TD, TAU, *C.thumb_radii(ref, TD))
AUTH = set(i for i in range(NV) if i in RG["AUTH"]) if False else set(RG["AUTH"])
DOM = {}
for i in range(NV):
    DOM[i] = max(WA[i].items(), key=lambda kv: kv[1])[0] if WA[i] else None

# ---- heatmap machinery (STOPS / ramp identical to Stage5B_R1) -----------------------
STOPS = [(0.00, (0.16, 0.16, 0.20)), (0.25, (0.10, 0.35, 0.85)),
         (0.50, (0.10, 0.80, 0.30)), (0.75, (0.95, 0.85, 0.10)), (1.00, (0.95, 0.10, 0.05))]


def ramp(t):
    t = max(0.0, min(1.0, t))
    for i in range(len(STOPS) - 1):
        a, ca = STOPS[i]
        b, cb = STOPS[i + 1]
        if a <= t <= b:
            f = 0.0 if b == a else (t - a) / (b - a)
            return tuple(ca[k] + (cb[k] - ca[k]) * f for k in range(3))
    return STOPS[-1][1]


def add_color_attr(m, name):
    if name not in m.color_attributes:
        m.color_attributes.new(name, 'FLOAT_COLOR', 'POINT')
    return m.color_attributes[name]


ca = add_color_attr(me, "wcol")


def set_colors(m, attr, vals):
    for i in range(len(m.vertices)):
        c = ramp(vals[i])
        attr.data[i].color = (c[0], c[1], c[2], 1.0)


def set_colors_rgb(m, attr, rgbs):
    for i in range(len(m.vertices)):
        c = rgbs[i]
        attr.data[i].color = (c[0], c[1], c[2], 1.0)


def flat_mat(name="WMAP", layer="wcol"):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    att = nt.nodes.new('ShaderNodeVertexColor')
    att.layer_name = layer
    emi = nt.nodes.new('ShaderNodeEmission')
    outn = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(att.outputs[0], emi.inputs[0])
    nt.links.new(emi.outputs[0], outn.inputs[0])
    return mat


scn = bpy.context.scene
for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        scn.render.engine = e
        break
    except Exception:
        continue
scn.render.resolution_x = 1500
scn.render.resolution_y = 1050
scn.render.image_settings.file_format = 'PNG'
scn.render.film_transparent = False
scn.view_settings.view_transform = 'Standard'
if scn.world is None:
    scn.world = bpy.data.worlds.new("W")
scn.world.use_nodes = True
bg = scn.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (1, 1, 1, 1)
    bg.inputs[1].default_value = 1.0
for _l in range(6):
    lt = bpy.data.lights.new("LL%d" % _l, 'POINT')
    lt.energy = 30.0
    scn.collection.objects.link(bpy.data.objects.new("LO%d" % _l, lt))
bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"].hide_render = True
bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"].hide_viewport = True

Ctr = sum(V, Vector()) / NV
d0 = (Vector(jf["INDEX_TIP_R"]["head"]) - Vector(jf["THUMB_CMC_R"]["head"])).normalized()
cand = json.load(open(os.path.join(TOP, "stage5a_r2", "_tmp", "S5A_R2_CANDIDATES.json"),
                      encoding="utf-8"))
DORSAL = {k: Vector(v) for k, v in cand["dorsal_refs"].items()}
n0 = DORSAL["thumb"].normalized()
l0 = d0.cross(n0).normalized()
if l0.dot(Vector((1, 0, 0))) < 0:
    l0 = -l0
n0 = l0.cross(d0).normalized() * (1 if n0.dot(l0.cross(d0)) > 0 else -1)

_wm = flat_mat("WMAP", "wcol")
me.materials.clear()
me.materials.append(_wm)
for p in me.polygons:
    p.material_index = 0


def make_legend(cam, title):
    bar = flat_mat("BAR", "wcol")
    bnt = bar.node_tree
    for nd in list(bnt.nodes):
        bnt.nodes.remove(nd)
    tc = bnt.nodes.new('ShaderNodeTexCoord')
    sep = bnt.nodes.new('ShaderNodeSeparateXYZ')
    cr = bnt.nodes.new('ShaderNodeValToRGB')
    cr.color_ramp.interpolation = 'LINEAR'
    need = 5 - len(list(cr.color_ramp.elements))
    for _ in range(max(0, need)):
        cr.color_ramp.elements.new(0.5)
    for k, (pos, col) in enumerate(STOPS):
        cr.color_ramp.elements[k].position = pos
        cr.color_ramp.elements[k].color = (col[0], col[1], col[2], 1.0)
    emi = bnt.nodes.new('ShaderNodeEmission')
    outn = bnt.nodes.new('ShaderNodeOutputMaterial')
    bnt.links.new(tc.outputs[2], sep.inputs[0])
    bnt.links.new(sep.outputs[0], cr.inputs[0])
    bnt.links.new(cr.outputs[0], emi.inputs[0])
    bnt.links.new(emi.outputs[0], outn.inputs[0])
    bpy.ops.mesh.primitive_plane_add(size=1.0)
    pl = bpy.context.object
    pl.name = "BAR_OBJ"
    pl.parent = cam
    pl.location = (0.0, -0.62, -1.55)
    pl.scale = (0.95, 0.10, 1.0)
    pl.data.materials.append(bar)
    objs = [pl]
    for txt, x in (("0.0", -0.50), ("0.5", 0.0), ("1.0", 0.50)):
        bpy.ops.object.text_add()
        t = bpy.context.object
        t.data.body = txt
        t.data.size = 0.10
        t.data.align_x = 'CENTER'
        t.parent = cam
        t.location = (x, -0.62, -1.70)
        objs.append(t)
    bpy.ops.object.text_add()
    tt = bpy.context.object
    tt.data.body = title
    tt.data.size = 0.125
    tt.data.align_x = 'CENTER'
    tt.parent = cam
    tt.location = (0.0, -0.62, -1.36)
    objs.append(tt)
    return objs


THUMB_SEL = [i for i in range(NV) if RG["own_r1a"][i] == "THUMB"]
THUMB_CTR = sum((V[i] for i in THUMB_SEL), Vector()) / len(THUMB_SEL)
T_DORS = DORSAL["thumb"].normalized()
T_AXIS = (Vector(jf["THUMB_IP_R"]["head"]) - Vector(jf["THUMB_CMC_R"]["head"])).normalized()
T_LAT = T_AXIS.cross(T_DORS).normalized()
_WEB_IDS = sorted(RG["FIRST_WEB"])
WEB_DIR = (sum((V[i] for i in _WEB_IDS), Vector()) / len(_WEB_IDS) - THUMB_CTR).normalized()

CAMV = {"dorsal": (0.35 * l0 + 0.95 * n0 + 0.10 * d0, 0.245),
        "palmar": (0.35 * l0 - 0.95 * n0 + 0.10 * d0, 0.245),
        "thumb": (T_DORS + 0.22 * T_AXIS + 0.10 * T_LAT, 0.170),
        "thumb_side": (-WEB_DIR * 0.95 + T_DORS * 0.30 + 0.12 * T_AXIS, 0.185),
        "thumb_web": (WEB_DIR * 1.00 + 0.16 * T_AXIS, 0.300),
        "thumb_web_near": (WEB_DIR * 1.00 + 0.22 * T_AXIS, 0.165),
        "thumb_tip": (T_AXIS + 0.40 * T_DORS, 0.100),
        "palm": (0.60 * n0 + 0.70 * l0 + 0.20 * d0, 0.185)}


def render(name, vals, title, view, world=None, extra=None, dist_ov=None):
    if vals is not None:
        set_colors(me, ca, vals)
    dirv, dist = CAMV[view]
    if dist_ov is not None:
        dist = dist_ov
    cd = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cd)
    scn.collection.objects.link(cam)
    tgt = (THUMB_CTR if view.startswith("thumb") else Ctr) if world is None else world
    cam.location = tgt + dirv.normalized() * dist
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cd.lens = 42
    cd.clip_start = 0.001
    cd.clip_end = 5.0
    scn.camera = cam
    legend = make_legend(cam, title)
    scn.render.filepath = os.path.join(REND, name + ".png")
    bpy.ops.render.render(write_still=True)
    log("rendered %s" % scn.render.filepath)
    for o in (extra or []):
        bpy.data.objects.remove(o, do_unlink=True)
    for o in legend:
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.objects.remove(cam, do_unlink=True)


def spec_vals(W, spec):
    return [sum(W[i].get(b, 0.0) * k for b, k in spec.items()) for i in range(NV)]


# =====================================================================================
# 1. single-group weight maps (after)
# =====================================================================================
TARGETS = [
    ("STAGE5B_R1A_WEIGHT_THUMB_CMC", {"THUMB_CMC_R": 1.0}, "THUMB_CMC_R  (R1A)", "thumb_side"),
    ("STAGE5B_R1A_WEIGHT_THUMB_MCP", {"THUMB_MCP_R": 1.0}, "THUMB_MCP_R  (R1A)", "thumb_side"),
    ("STAGE5B_R1A_WEIGHT_THUMB_IP", {"THUMB_IP_R": 1.0}, "THUMB_IP_R  (R1A)", "thumb"),
    ("STAGE5B_R1A_WEIGHT_FIRST_WEB", {"WRIST_R": 1.0, "THUMB_CMC_R": 1.0, "THUMB_MCP_R": 1.0,
                                      "INDEX_MCP_R": 1.0},
     "FIRST WEB whitelist (WRIST/CMC/MCP/INDEX_MCP)  (R1A)", "thumb_web_near"),
    ("STAGE5B_R1A_WEIGHT_THENAR", {"WRIST_R": 1.0, "THUMB_CMC_R": 1.0},
     "THENAR: WRIST_R + THUMB_CMC_R  (R1A)", "thumb_web"),
]
FOCUS = set(RG["FIRST_WEB"]) | set(RG["WEB_INDEX_SIDE"]) | C.rings(ref["eadj"], set(RG["FIRST_WEB"]), 4) \
    | C.rings(ref["eadj"], set(RG["WEB_INDEX_SIDE"]), 3)


def focus_vals(W, spec):
    return [(sum(W[i].get(b, 0.0) * k for b, k in spec.items()) if i in FOCUS else 0.0)
            for i in range(NV)]


for name, spec, title, view in TARGETS:
    if name.endswith("FIRST_WEB"):
        render(name, focus_vals(WA, spec), title, view)
    else:
        render(name, spec_vals(WA, spec), title, view)

# cross digit leak (non-sanctioned foreign influence)
leakv = [0.0] * NV
for i in range(NV):
    own_i = RG["own_r1a"][i]
    for b, w in WA[i].items():
        bd = C.DIGIT_OF_BONE[b]
        if bd == own_i or bd == "wrist":
            continue
        if own_i == "wrist" and b.endswith("_MCP_R") and b != "WRIST_R":
            continue
        if own_i in ("THUMB", "INDEX") and b in ("THUMB_CMC_R", "THUMB_MCP_R", "INDEX_MCP_R", "WRIST_R"):
            continue
        leakv[i] += w
render("STAGE5B_R1A_WEIGHT_CROSS_DIGIT_LEAK", leakv,
       "CROSS-DIGIT LEAK (non-sanctioned foreign weight)  (R1A)", "dorsal")

# overviews (flat tint)
render("STAGE5B_R1A_BIND_OVERVIEW_DORSAL", [0.55] * NV, "BIND OVERVIEW (zero pose) - DORSAL  (R1A)", "dorsal")
render("STAGE5B_R1A_BIND_OVERVIEW_PALMAR", [0.55] * NV, "BIND OVERVIEW (zero pose) - PALMAR  (R1A)", "palmar")

# =====================================================================================
# 2. thumb region dominance map (categorical)
# =====================================================================================
REGCOL = [("CENTRAL_PALM", (0.62, 0.62, 0.66)), ("THUMB_DISTAL", (0.90, 0.15, 0.15)),
          ("THUMB_PROXIMAL", (1.00, 0.62, 0.10)), ("THUMB_FIRST_METACARPAL", (0.95, 0.90, 0.15)),
          ("THUMB_BASE_FOLD", (0.05, 0.80, 0.80)), ("THENAR_BASE", (0.15, 0.75, 0.25)),
          ("FIRST_WEB", (0.85, 0.10, 0.85))]
region_rgb = []
for i in range(NV):
    c = (0.97, 0.97, 0.97)
    for k, cc in REGCOL:
        if i in RG[k]:
            c = cc
            break
    region_rgb.append(c)
for i in range(NV):                       # mark the two nail-border vertices
    if i in (1383, 2740):
        region_rgb[i] = (0.0, 0.0, 0.0)
set_colors_rgb(me, ca, region_rgb)
render("STAGE5B_R1A_THUMB_REGION_DOMINANCE", None,
       "R1A THUMB SEMANTIC REGIONS (red=distal, orange=proximal, yellow=metacarpal, cyan=base fold, "
       "green=thenar, magenta=first web, black=1383/2740)", "thumb_side")

# =====================================================================================
# 3. first web mask qualification (selected verts + both boundaries + excluded zones)
# =====================================================================================
rgb = []
for i in range(NV):
    if i in RG["FIRST_WEB"]:
        rgb.append((0.90, 0.05, 0.90))            # selected first-web vertices
    elif i in RG["WEB_INDEX_SIDE"]:
        rgb.append((0.10, 0.35, 0.95))            # index side of the same interface
    elif i in set(RG["nail_thumb_vertices"]) or i in RG["cap_vertices"]:
        rgb.append((0.05, 0.75, 0.05))            # thumb nail / distal cap  (excluded)
    elif i in RG["THUMB_DISTAL"]:
        rgb.append((0.95, 0.55, 0.55))            # thumb distal phalanx (excluded)
    elif i in RG["THENAR_BASE"]:
        rgb.append((1.00, 0.90, 0.35))            # large thenar region (excluded)
    elif ref["OWN_V"][i] == "wrist" and i in C.rings(ref["eadj"], set(RG["FIRST_WEB"]), 1):
        rgb.append((0.15, 0.65, 0.90))            # palm-side boundary of the web
    else:
        rgb.append((0.93, 0.93, 0.95))
set_colors_rgb(me, ca, rgb)
render("STAGE5B_R1A_FIRST_WEB_MASK", None,
       "R1A FIRST WEB MASK: magenta=selected web, blue=index side, cyan=palm side, "
       "green=nail/cap (excluded), pink=thumb distal (excluded), yellow=thenar (excluded)", "thumb_web_near")

# =====================================================================================
# 4. v1383 / v2740 marker render
# =====================================================================================
PATCH = {}
for vid in (1383, 2740):
    PATCH[vid] = C.rings(ref["eadj"], set([vid]), 1) | set([vid])
MKCOL = {1383: (0.02, 0.02, 0.02), 2740: (1.0, 0.0, 0.85)}
_mrgb = [(0.62, 0.80, 0.45)] * NV
for vid in (1383, 2740):
    for i in PATCH[vid]:
        _mrgb[i] = MKCOL[vid]
set_colors_rgb(me, ca, _mrgb)
_mid = (V[1383] + V[2740]) / 2.0
render("STAGE5B_R1A_NAIL_VERTEX_1383_2740", None,
       "THUMB NAIL BORDER VERTICES: v1383 (black patch) and v2740 (magenta patch)", "thumb",
       world=_mid, dist_ov=0.070)
render("STAGE5B_R1A_NAIL_VERTEX_1383_2740_CONTEXT", None,
       "THUMB NAIL BORDER VERTICES: v1383 (black patch) and v2740 (magenta patch) - context",
       "thumb", world=_mid, dist_ov=0.170)

# =====================================================================================
# 5. BEFORE / AFTER panels (both states in ONE frame -> identical camera/light/legend)
# =====================================================================================
def before_after(name, spec, title, view, obj_w=0.15, tgt=None):
    dirv, dist = CAMV[view]
    if tgt is None:
        tgt = THUMB_CTR if view.startswith("thumb") else Ctr
    frame_w = 2.0 * obj_w * 1.10
    cam_dist = frame_w * (42.0 / 36.0)
    camloc = tgt + dirv.normalized() * cam_dist
    camdir = (tgt - camloc).normalized()
    up = Vector((0.0, 0.0, 1.0))
    screen_x = camdir.cross(up)
    if screen_x.length < 1e-9:
        screen_x = camdir.cross(Vector((0.0, 1.0, 0.0)))
    screen_x.normalize()
    off = screen_x * (frame_w * 0.25)
    obW = ob.matrix_world.copy()
    obA = obW.copy()
    obA.translation = obW.translation + off
    ob.matrix_world = obA
    obB = ob.copy()
    obB.data = me.copy()
    scn.collection.objects.link(obB)
    for m in list(obB.modifiers):
        obB.modifiers.remove(m)
    obB.parent = None
    obBb = obW.copy()
    obBb.translation = obW.translation - off
    obB.matrix_world = obBb
    mb = obB.data
    mb.materials.clear()
    mb.materials.append(flat_mat("WB" + name, "wcol"))
    for p in mb.polygons:
        p.material_index = 0
    attrB = add_color_attr(mb, "wcol")
    if "FIRST_WEB" in name:
        _ws = set(RG["FIRST_WEB"]) | set(RG["WEB_INDEX_SIDE"])
        fv = lambda W, sp: [(W[i].get("THUMB_IP_R", 0.0) if i in _ws else 0.0) for i in range(NV)]
    else:
        fv = spec_vals
    set_colors(mb, attrB, fv(W1, spec))
    set_colors(me, ca, fv(WA, spec))
    cd = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cd)
    scn.collection.objects.link(cam)
    cam.location = camloc
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cd.lens = 42
    cd.clip_start = 0.001
    scn.camera = cam
    legend = make_legend(cam, title)
    scn.render.filepath = os.path.join(REND, name + ".png")
    bpy.ops.render.render(write_still=True)
    log("rendered %s" % scn.render.filepath)
    for o in legend:
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.objects.remove(cam, do_unlink=True)
    ob.matrix_world = obW
    bpy.data.objects.remove(obB, do_unlink=True)


before_after("STAGE5B_R1A_THUMB_IP_BEFORE_AFTER", {"THUMB_IP_R": 1.0},
             "THUMB_IP_R  --  LEFT = R1 (before)   |   RIGHT = R1A (after)", "thumb", 0.15)
before_after("STAGE5B_R1A_FIRST_WEB_BEFORE_AFTER", {"THUMB_IP_R": 1.0},
             "FIRST WEB: THUMB_IP_R LEAK  --  LEFT = R1 (before)   |   RIGHT = R1A (after)",
             "thumb", 0.15)

json.dump({"renders": LOG, "count": len(LOG)}, open(os.path.join(OUTDIR, "_tmp", "R1A_RENDER_LOG.json"),
                                                    "w", encoding="utf-8"), indent=1,
          ensure_ascii=False)
print("RENDER_DONE")
