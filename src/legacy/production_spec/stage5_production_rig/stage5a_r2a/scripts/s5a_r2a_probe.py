# =====================================================================================
# STAGE5A_R2A -- READ-ONLY PROBE
# Opens the frozen Stage5A R2 blend, never saves it, and reports:
#   * object frames (hand mesh + rig armature)
#   * reproduction of the approved T-01 index finger axis / anchor / zone
#   * the R2 INDEX_MCP axial coordinate in the T-01 frame
#   * thumb strict ownership + distal-cap first cut
# usage: blender -b <blend> --python s5a_r2a_probe.py -- <out.json>
# =====================================================================================
import bpy, bmesh, sys, os, json, math, heapq, hashlib, datetime
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
TARGET = "Hand  - Realistic"
RIGNAME = "RIGHT_HAND_PRODUCTION_RIG"
MM = 1000.0

S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
t01 = json.load(open(os.path.join(S4, "stage4a_t01", "T01_FINAL_AUDIT.json"), encoding="utf-8"))

BLEND = bpy.data.filepath
SHA_BEFORE = hashlib.sha256(open(BLEND, "rb").read()).hexdigest()
R = {"blend": BLEND, "sha256_before": SHA_BEFORE}

ob = bpy.data.objects[TARGET]
me = ob.data
MW = ob.matrix_world
R["objects"] = []
for o in bpy.data.objects:
    R["objects"].append({
        "name": o.name, "type": o.type,
        "location": [round(float(x), 9) for x in o.location],
        "matrix_world": [[round(float(MW2), 9) for MW2 in row] for row in o.matrix_world],
    })

W = [(MW @ v.co).copy() for v in me.vertices]
NV = len(me.vertices)
R["hand"] = {"n_verts": NV, "n_polys": len(me.polygons), "name": ob.name,
             "matrix_world": [[round(float(x), 9) for x in row] for row in MW]}

# ---------------------------------------------------------------- rig frame
rig = bpy.data.objects.get(RIGNAME)
R["rig"] = None
if rig:
    R["rig"] = {
        "name": rig.name, "type": rig.type,
        "location": [round(float(x), 9) for x in rig.location],
        "rotation_euler": [round(float(x), 9) for x in rig.rotation_euler],
        "scale": [round(float(x), 9) for x in rig.scale],
        "matrix_world": [[round(float(x), 9) for x in row] for row in rig.matrix_world],
        "matrix_local": [[round(float(x), 9) for x in row] for row in rig.matrix_local],
    }
    key = ["WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R", "THUMB_TIP_R", "INDEX_MCP_R"]
    R["rig"]["bones"] = {}
    for bn in key:
        b = rig.data.bones[bn]
        R["rig"]["bones"][bn] = {
            "head_local_armature": [round(float(x), 9) for x in b.head_local],
            "tail_local_armature": [round(float(x), 9) for x in b.tail_local],
            "head_local_bone": [round(float(x), 9) for x in b.head],
            "tail_local_bone": [round(float(x), 9) for x in b.tail],
            "parent": b.parent.name if b.parent else None,
            "use_connect": bool(b.use_connect),
            "roll": round(float(b.matrix_local.to_3x3().to_euler().y), 9),
            "matrix_local_translation": [round(float(x), 9) for x in b.matrix_local.translation],
        }
        R["rig"]["bones"][bn]["head_world"] = [round(float(x), 9)
                                               for x in (rig.matrix_world @ b.head_local)]

# ---------------------------------------------------------------- T-01 authority reproduction
M_NORM = Matrix(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)))
TIP_SEEDS = {
    "little": Vector((1.3515, 0.0319, 0.1879)), "ring": Vector((1.3933, 0.0320, 0.1599)),
    "middle": Vector((1.4231, 0.0251, 0.1490)), "index": Vector((1.4586, 0.0239, 0.1643)),
    "thumb": Vector((1.4977, 0.0358, 0.2421)),
}
THUMB_ROOT_SEED = Vector((1.4489, 0.0115, 0.3134))
FOREARM_SEED = Vector((1.4048, 0.0113, 0.4316))
WRIST_SEED = Vector((1.4048, 0.0113, 0.3430))
FINGER_ORDER = ["little", "ring", "middle", "index"]
LOC0 = MW.translation
canon = lambda p: (M_NORM @ p) + (LOC0 - (M_NORM @ LOC0))

bm = bmesh.new(); bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
adj = [[] for _ in range(NV)]
for e in bm.edges:
    a, b = e.verts[0].index, e.verts[1].index
    L = (W[a] - W[b]).length
    adj[a].append((b, L)); adj[b].append((a, L))


def dij(src):
    d = [float("inf")] * NV; d[src] = 0.0; pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d[u] + 1e-15:
            continue
        for v, w in adj[u]:
            nd = du + w
            if nd < d[v] - 1e-16:
                d[v] = nd; heapq.heappush(pq, (nd, v))
    return d


nearest = lambda p: min(range(NV), key=lambda i: (W[i] - p).length_squared)
TIPV = {n: nearest(canon(s)) for n, s in TIP_SEEDS.items()}
G = {n: dij(TIPV[n]) for n in TIPV}
WRIST_V = nearest(canon(WRIST_SEED))
FOREARM = W[nearest(canon(FOREARM_SEED))]
D_DIST = (W[TIPV["middle"]] - FOREARM).normalized()
R_RAD = (W[TIPV["index"]] - W[TIPV["little"]]).normalized()
R_RAD = (R_RAD - D_DIST * R_RAD.dot(D_DIST)).normalized()
DORSAL = D_DIST.cross(R_RAD).normalized()

lab = [None] * NV; dd = [float("inf")] * NV
seeds = [("wrist", WRIST_V)] + [(n, TIPV[n]) for n in TIPV]
for nm, s in seeds:
    dd[s] = 0.0; lab[s] = nm
pq = [(0.0, s) for _, s in seeds]; heapq.heapify(pq)
while pq:
    du, u = heapq.heappop(pq)
    if du > dd[u] + 1e-15:
        continue
    for v, w in adj[u]:
        if du + w < dd[v] - 1e-16:
            dd[v] = du + w; lab[v] = lab[u]; heapq.heappush(pq, (dd[v], v))
DIGIT_V = {n: [] for n in TIPV}
for i, l in enumerate(lab):
    if l in DIGIT_V:
        DIGIT_V[l].append(i)

CLEFTS = [("index", "middle"), ("middle", "ring"), ("ring", "little"), ("index", "thumb")]
FINGER_CLEFTS = {"index": ["index-middle"], "middle": ["index-middle", "middle-ring"],
                 "ring": ["middle-ring", "ring-little"], "little": ["ring-little"]}
NOTCH = {}
for a, b in CLEFTS:
    ridge = {u for u in range(NV) if lab[u] in (a, b)
             and any(lab[v] in (a, b) and lab[v] != lab[u] for v, _w in adj[u])}
    if ridge:
        NOTCH["%s-%s" % (a, b)] = max(ridge, key=lambda u: (W[u] - FOREARM).dot(D_DIST))
FUNC_LEN = {}
for nm in FINGER_ORDER:
    vals = [G[nm][NOTCH[c]] for c in FINGER_CLEFTS[nm] if c in NOTCH]
    if vals:
        FUNC_LEN[nm] = sum(vals) / len(vals)
FUNC_LEN["thumb"] = G["thumb"][nearest(canon(THUMB_ROOT_SEED))]


def finger_axis(nm):
    tip = W[TIPV[nm]]
    L = FUNC_LEN[nm]
    ids = DIGIT_V.get(nm, [])
    bandv = [i for i in ids if 0.25 * L <= G[nm][i] <= 0.55 * L]
    c = (sum((W[i] for i in bandv), Vector()) / len(bandv)) if bandv else tip
    axis = (tip - c).normalized()
    ref = W[nearest(canon(THUMB_ROOT_SEED))] if nm == "thumb" else W[NOTCH[FINGER_CLEFTS[nm][0]]]
    anchor = tip + axis * ((ref - tip).dot(axis))
    return axis, anchor, tip, c, len(bandv)


AXIAL_FRAC = {"MCP": 0.0, "PIP": 0.46, "DIP": 0.77, "THUMB_MCP": 0.44, "THUMB_IP": 0.75}
T01_REP = {}
for nm, jn in [("index", "INDEX_MCP"), ("middle", "MIDDLE_MCP"),
               ("ring", "RING_MCP"), ("little", "LITTLE_MCP")]:
    axis, anchor, tip, c, nb = finger_axis(nm)
    L = FUNC_LEN[nm]
    A = (tip - anchor).dot(axis)
    c_ax = A * AXIAL_FRAC["MCP"]
    h = max(0.007, 0.10 * L)
    T01_REP[jn] = {
        "axis": [round(float(x), 9) for x in axis],
        "anchor": [round(float(x), 9) for x in anchor],
        "tip_vertex_index": TIPV[nm],
        "tip_vertex_world": [round(float(x), 9) for x in tip],
        "band_centroid": [round(float(x), 9) for x in c],
        "band_n": nb,
        "axial_finger_length_mm": round(A * MM, 3),
        "joint_axial_center_mm": round(c_ax * MM, 3),
        "zone_half_width_mm": round(h * MM, 3),
        "published_axial_finger_length_mm": t01["T01_MCP"][jn]["axial_finger_length_mm"],
        "published_joint_axial_center_mm": t01["T01_MCP"][jn]["joint_axial_center_mm"],
        "published_zone_half_width_mm": t01["T01_MCP"][jn]["zone_half_width_mm"],
        "published_loop_positions_axial": t01["T01_MCP"][jn]["LOOP_POSITION_axial_from_commissure_mm"],
    }
R["T01_reproduction"] = T01_REP

# ---- index_MCP measured in the T-01 frame, using the R2 rig's own bone
if rig:
    key = ["WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R", "THUMB_TIP_R", "INDEX_MCP_R"]
    R2J = {}
    for bn in key:
        b = rig.data.bones[bn]
        R2J[bn] = (rig.matrix_world @ b.head_local).copy()
    ia = T01_REP["INDEX_MCP"]
    axis = Vector(ia["axis"]); anchor = Vector(ia["anchor"])
    p = R2J["INDEX_MCP_R"]
    axial = (p - anchor).dot(axis) * MM
    # legacy frame 1 (report): axis = index proximal-phalanx axis, origin = Stage4B INDEX_MCP
    prox = Vector(jf["INDEX_MCP_R"]["head"])
    ax_pp = (Vector(jf["INDEX_PIP_R"]["head"]) - prox).normalized()
    leg1 = (p - prox).dot(ax_pp) * MM
    # legacy frame 2 (STATUS json): axis = MCP -> TIP chord, origin = Stage4B INDEX_MCP
    ax_ch = (Vector(jf["INDEX_TIP_R"]["head"]) - prox).normalized()
    leg2 = (p - prox).dot(ax_ch) * MM
    # Stage4B approved index MCP measured in the T-01 frame (should be ~0)
    p4b = Vector(jf["INDEX_MCP_R"]["head"])
    axial_4b = (p4b - anchor).dot(axis) * MM
    R["INDEX_MCP_RECON"] = {
        "R2_point_world": [round(float(x), 9) for x in p],
        "T01_axis": ia["axis"], "T01_anchor": ia["anchor"],
        "T01_frame_axial_mm": round(axial, 4),
        "T01_zone_half_width_mm": ia["zone_half_width_mm"],
        "T01_frame_pass": abs(axial) <= ia["zone_half_width_mm"],
        "legacy_report_frame_proximal_phalanx_axis_mm": round(leg1, 6),
        "legacy_status_frame_mcp_to_tip_chord_mm": round(leg2, 4),
        "stage4b_approved_index_mcp_T01_frame_mm": round(axial_4b, 4),
        "stage4b_point_world": [round(float(x), 9) for x in p4b],
        "distance_R2_vs_stage4b_mm": round((p - p4b).length * MM, 4),
        "T01_anchor_vs_stage4b_point_mm": round((anchor - p4b).length * MM, 4),
        "angle_T01_axis_vs_proximal_phalanx_deg": round(math.degrees(math.acos(
            max(-1.0, min(1.0, axis.dot(ax_pp))))), 4),
        "angle_T01_axis_vs_mcp_tip_chord_deg": round(math.degrees(math.acos(
            max(-1.0, min(1.0, axis.dot(ax_ch))))), 4),
    }

R["sha256_after"] = hashlib.sha256(open(BLEND, "rb").read()).hexdigest()
R["input_unchanged"] = (R["sha256_before"] == R["sha256_after"])
json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("[S5A-R2A-PROBE] written", OUT)
