# =====================================================================================
# STAGE5A_R2A -- BRANCH B build : THUMB_TIP_R_ONLY_REQUALIFICATION
# =====================================================================================
# INPUT  (frozen, read-only): stage5a_r2/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2.blend
#                             sha256 615367d7fab3e75431fa7171e7e82f3a655c62e29ad7ddca5509b093e9f68c81
#                             stage4c_r2/..._STAGE4C_R2.blend
#                             sha256 fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7
# OUTPUT (new):              stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend
#
# ALLOWED CHANGES ONLY:
#   THUMB_TIP_R.head   = the canonical thumb DISTAL-CAP landmark (recomputed here)
#   THUMB_TIP_R.tail   = TIP helper tail  = head + distal_dir * 0.30 * distal_len
#   THUMB_IP_R.tail    = the same landmark (connected representation)
# THUMB_IP_R.head MUST NOT MOVE.  The other 20 joint heads MUST have 0 drift.
# =====================================================================================
import bpy, sys, os, json, math, hashlib, heapq, datetime
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
MM = 1000.0
NOW = datetime.datetime.now().astimezone().isoformat()
TIP_FRACTION = 0.30
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
S5AR2 = r"<HANDS_ROOT>\production_spec\stage5_production_rig\stage5a_r2"
S5AR2A = OUTDIR
R2_BLEND = os.path.join(S5AR2, "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2.blend")
MASTER = os.path.join(S4, "stage4c_r2", "RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend")
OUT_BLEND = os.path.join(S5AR2A, "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")

R2_SHA = "615367d7fab3e75431fa7171e7e82f3a655c62e29ad7ddca5509b093e9f68c81"
MASTER_SHA = "fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7"
EXPECTED_REP = [1.45281744, 0.019802358, 0.493028343]

jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
cand = json.load(open(os.path.join(S5AR2, "_tmp", "S5A_R2_CANDIDATES.json"), encoding="utf-8"))
STAT = json.load(open(os.path.join(S5AR2, "STAGE5A_R2_STATUS.json"), encoding="utf-8"))
DORSAL = {k: Vector(v) for k, v in cand["dorsal_refs"].items()}
ASSET_ORIGIN = Vector(oa["WRIST_ORIGIN"])
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a); LOG.append(s); print("[S5A-R2A-BUILD]", s)


for p, want in ((MASTER, MASTER_SHA), (R2_BLEND, R2_SHA)):
    got = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if got != want:
        raise SystemExit("FAIL CLOSED: %s sha256 %s != %s" % (p, got, want))
log("input R2    sha256 = %s" % R2_SHA)
log("input master sha256 = %s" % MASTER_SHA)

bpy.ops.wm.open_mainfile(filepath=R2_BLEND)
ob = bpy.data.objects["Hand  - Realistic"]
me = ob.data
MW = ob.matrix_world
MINV = MW.inverted()
M3 = MW.to_3x3()
V = [(MW @ v.co).copy() for v in me.vertices]
NV = len(V); NP = len(me.polygons)
MESH_SIG_BEFORE = [tuple(round(x, 9) for x in p) for p in V]
TOPO_BEFORE = [tuple(p.vertices) for p in me.polygons]
UV_BEFORE = [tuple(round(u, 9) for u in d.uv) for d in me.uv_layers.active.data] if me.uv_layers.active else []
MAT_BEFORE = [p.material_index for p in me.polygons]


def closest(p):
    ok, loc, nor, idx = ob.closest_point_on_mesh(MINV @ Vector(p))
    if not ok:
        return None, None, None
    return MW @ loc, (M3 @ nor).normalized(), idx


def parity(p, ndir=64):
    pl = MINV @ Vector(p)
    hits = 0
    for k in range(ndir):
        th = 2.399963229728653 * k
        z = 1.0 - 2.0 * (k + 0.5) / ndir
        r = math.sqrt(max(0.0, 1.0 - z * z))
        d = Vector((r * math.cos(th), r * math.sin(th), z))
        n = 0; o = pl.copy()
        for _ in range(48):
            ok, loc, nor, idx = ob.ray_cast(o, d, distance=1.0)
            if not ok:
                break
            n += 1
            o = loc + d * 2e-7
        if n % 2 == 1:
            hits += 1
    return hits, ndir


def d_poly(p, poly):
    b = 1e9
    for i in range(len(poly) - 1):
        a, q = poly[i], poly[i + 1]; ab = q - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
        b = min(b, (p - (a + ab * t)).length)
    return b


CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"], "LITTLE": ["MCP", "PIP", "DIP"]}
FACE_C = [sum((V[v] for v in p.vertices), Vector()) / len(p.vertices) for p in me.polygons]


def chainpts(D):
    p = [Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])]
    for s in CHAIN[D]:
        p.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
    return p


AC = {D: chainpts(D) for D in CHAIN}
AC["wrist"] = [ASSET_ORIGIN, Vector(jf["WRIST_R"]["tail"])]
FACE_OWNER = {}
for p in me.polygons:
    FACE_OWNER[p.index] = min(AC, key=lambda D: d_poly(FACE_C[p.index], AC[D]))
V2F = [[] for _ in range(NV)]
for p in me.polygons:
    for v in p.vertices:
        V2F[v].append(p.index)
VOWN = {}
for v in me.vertices:
    ds = {FACE_OWNER[fi] for fi in V2F[v.index]}
    VOWN[v.index] = ds.pop() if len(ds) == 1 else "MIXED"
OF = {D: [p.index for p in me.polygons if FACE_OWNER[p.index] == D] for D in CHAIN}
DV = {D: sorted({v for p in me.polygons if FACE_OWNER[p.index] == D for v in p.vertices}) for D in CHAIN}
EADJ = {}
for e in me.edges:
    a, b = e.vertices[0], e.vertices[1]
    w = (V[a] - V[b]).length
    EADJ.setdefault(a, []).append((b, w)); EADJ.setdefault(b, []).append((a, w))
FADJ = [[] for _ in range(NP)]
ef = {}
for p in me.polygons:
    vs = list(p.vertices)
    for i in range(len(vs)):
        ef.setdefault(tuple(sorted((vs[i], vs[(i + 1) % len(vs)]))), []).append(p.index)
for k, fs in ef.items():
    for a in fs:
        for b in fs:
            if a != b:
                FADJ[a].append(b)


def dij(src):
    d = {src: 0.0}; pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d.get(u, 1e18) + 1e-15:
            continue
        for w, l in EADJ.get(u, ()):
            if du + l < d.get(w, 1e18) - 1e-16:
                d[w] = du + l; heapq.heappush(pq, (du + l, w))
    return d


# ---------------------------------------------------------------- recompute the canonical
# thumb distal-cap landmark (identical method to s5a_r2a_audit.py -> must reproduce)
D = "THUMB"
P = Vector(jf["THUMB_IP_R"]["head"]); T = Vector(jf["THUMB_TIP_R"]["head"])
u0 = (T - P).normalized()
cand_v = [i for i in DV[D] if (V[i] - P).dot(u0) > 0.0]
star = max(cand_v, key=lambda i: (V[i] - P).length)
g = dij(star)
ownf = set(OF[D])
ok = [fi for fi in ownf
      if min((g.get(v, 1e18) for v in me.polygons[fi].vertices), default=1e18) <= 9.0e-3]
near_face = min(ownf, key=lambda fi: (FACE_C[fi] - V[star]).length)
if near_face not in ok:
    ok.append(near_face)
cs = set(ok); capc = set(); stk = [near_face]
while stk:
    f = stk.pop()
    if f in capc or f not in cs:
        continue
    capc.add(f)
    for q in FADJ[f]:
        if q in cs and q not in capc:
            stk.append(q)
capc = sorted(capc)
area = sum(me.polygons[fi].area for fi in capc)
cap_c = sum((FACE_C[fi] * me.polygons[fi].area for fi in capc), Vector()) / max(1e-18, area)
REP, _n, _f = closest(cap_c)
REP = Vector(REP)
log("recomputed cap faces=%d star=v%d rep=%s" % (len(capc), star, [round(float(x), 9) for x in REP]))
if max(abs(REP[i] - EXPECTED_REP[i]) for i in range(3)) > 1e-6:
    raise SystemExit("FAIL CLOSED: recomputed representative differs from the audited value")

# ---------------------------------------------------------------- gating the new landmark
loc, nor, fi = closest(REP)
par, tot = parity(REP)
n_in = 0; n_tot = 0
FAILED_T = []
for k in range(1, 21):
    t = 0.05 + (0.80 * k / 20.0)
    q = P + (REP - P) * t
    p2, t2 = parity(q)
    n_tot += 1
    if p2 > t2 / 2:
        n_in += 1
    else:
        FAILED_T.append(round(t, 3))
GATE = {
    "THUMB_TIP_ON_DISTAL_CAP_PATCH": fi in set(capc),
    "THUMB_TIP_SURFACE_DISTANCE_mm": round((REP - loc).length * MM, 4),
    "THUMB_TIP_SURFACE_DISTANCE_PASS": (REP - loc).length * MM <= 1.5,
    "THUMB_TIP_OWNER": FACE_OWNER.get(fi),
    "THUMB_TIP_OWNER_PASS": FACE_OWNER.get(fi) == "THUMB",
    "THUMB_IP_TO_TIP_INTERIOR": "%d/%d" % (n_in, n_tot),
    "THUMB_IP_TO_TIP_INTERIOR_PASS": n_in == n_tot,
    "THUMB_IP_TO_TIP_INTERIOR_FAILED_T": FAILED_T,
    "THUMB_IP_TO_TIP_INTERIOR_NOTE": ("the frozen THUMB_IP_R.head cannot see the thumb distal "
        "cap through a straight interior chord: the thumb distal phalanx is curved, so every "
        "point of the distal cap fails a strict 20/20 interior test, and the only fully "
        "interior cap sample (vertex 1074) still sits 12.71 mm from the distal-most vertex "
        "-- no better than the rejected R2 point.  This is a declared RESIDUAL for Human "
        "Review; the interior gate cannot be satisfied together with the canonical distal-cap "
        "semantic without moving THUMB_IP_R.head, which this round is forbidden to do."),
    "THUMB_TIP_DIST_TO_DISTAL_MOST_VERTEX_mm": round((REP - V[star]).length * MM, 4),
    "THUMB_TIP_DIST_TO_CAP_CENTROID_mm": round((REP - cap_c).length * MM, 4),
    "THUMB_TIP_GEODESIC_FROM_DISTAL_MOST_VERTEX_mm": round(
        min((g.get(i, 1e18) for i in range(NV) if (V[i] - REP).length < 0.0025), default=-1) * MM, 4),
}
log("gates: %s" % GATE)
for k in ("THUMB_TIP_ON_DISTAL_CAP_PATCH", "THUMB_TIP_SURFACE_DISTANCE_PASS",
          "THUMB_TIP_OWNER_PASS"):
    if not GATE[k]:
        raise SystemExit("FAIL CLOSED: gate %s not satisfied" % k)
if not GATE["THUMB_IP_TO_TIP_INTERIOR_PASS"]:
    log("RESIDUAL: THUMB_IP_TO_TIP_INTERIOR = %s (failing t = %s)"
        % (GATE["THUMB_IP_TO_TIP_INTERIOR"], GATE["THUMB_IP_TO_TIP_INTERIOR_FAILED_T"]))

# ---------------------------------------------------------------- edit ONLY the 3 allowed slots
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
BEFORE = {}
for b in rig.data.bones:
    BEFORE[b.name] = {"head": Vector(b.head_local), "tail": Vector(b.tail_local),
                      "roll": float(b.matrix_local.to_3x3().to_euler().y)}

ip_head = Vector(rig.data.bones["THUMB_IP_R"].head_local)
new_head_local = REP - ASSET_ORIGIN
distal_dir = (REP - P).normalized()
distal_len = (REP - P).length
new_tip_tail_local = REP + distal_dir * TIP_FRACTION * distal_len - ASSET_ORIGIN

bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
eb = rig.data.edit_bones
e_ip = eb["THUMB_IP_R"]; e_tip = eb["THUMB_TIP_R"]
e_ip.tail = REP - ASSET_ORIGIN
e_tip.head = new_head_local
e_tip.tail = new_tip_tail_local
for n, dv in (("THUMB_IP_R", DORSAL["thumb"]), ("THUMB_TIP_R", DORSAL["thumb"])):
    eb[n].align_roll(dv)
bpy.ops.object.mode_set(mode='OBJECT')

prefs = bpy.context.preferences
prefs.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, copy=True, compress=False)
OUT_SHA = hashlib.sha256(open(OUT_BLEND, "rb").read()).hexdigest()
log("SAVED %s" % OUT_BLEND)
log("SAVED sha256 = %s" % OUT_SHA)

# ---------------------------------------------------------------- verification
bpy.ops.wm.open_mainfile(filepath=OUT_BLEND)
rig2 = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
ob2 = bpy.data.objects["Hand  - Realistic"]
V2 = [(ob2.matrix_world @ v.co).copy() for v in ob2.data.vertices]
mesh_delta = max((V2[i] - Vector(MESH_SIG_BEFORE[i])).length for i in range(len(V2))) * MM
topo_same = [tuple(p.vertices) for p in ob2.data.polygons] == TOPO_BEFORE
uv_same = ([tuple(round(u, 9) for u in d.uv) for d in ob2.data.uv_layers.active.data]
           if ob2.data.uv_layers.active else []) == UV_BEFORE
mat_same = [p.material_index for p in ob2.data.polygons] == MAT_BEFORE

DRIFT = {}
for b in rig2.data.bones:
    h = Vector(b.head_local)
    DRIFT[b.name] = {"head_delta_mm": round((h - BEFORE[b.name]["head"]).length * MM, 9),
                     "tail_delta_mm": round((Vector(b.tail_local) - BEFORE[b.name]["tail"]).length * MM, 9),
                     "head_unchanged": (h - BEFORE[b.name]["head"]).length * MM < 1e-6,
                     "authorized": b.name in ("THUMB_TIP_R",)}
unauth = [n for n, v in DRIFT.items() if not v["head_unchanged"] and n != "THUMB_TIP_R"]
log("unauthorized head changes: %s" % unauth)
if unauth:
    raise SystemExit("FAIL CLOSED: unauthorized head drift %s" % unauth)

# thumb chain geometry on the new blend
def parity2(p, ndir=64):
    pl = ob2.matrix_world.inverted() @ Vector(p)
    hits = 0
    for k in range(ndir):
        th = 2.399963229728653 * k
        z = 1.0 - 2.0 * (k + 0.5) / ndir
        r = math.sqrt(max(0.0, 1.0 - z * z))
        d = Vector((r * math.cos(th), r * math.sin(th), z))
        n = 0; o = pl.copy()
        for _ in range(48):
            ok, loc, nor, idx = ob2.ray_cast(o, d, distance=1.0)
            if not ok:
                break
            n += 1
            o = loc + d * 2e-7
        if n % 2 == 1:
            hits += 1
    return hits, ndir


def seg(a, b, span):
    n_in = 0; n_tot = 0
    for k in range(1, 21):
        t = 0.05 + (0.80 * k / 20.0)
        q = a + (b - a) * t
        p2, t2 = parity2(q)
        n_tot += 1
        if p2 > t2 / 2:
            n_in += 1
    return n_in, n_tot


W = lambda n: rig2.matrix_world @ rig2.data.bones[n].head_local
WT = lambda n: rig2.matrix_world @ rig2.data.bones[n].tail_local
segs = [("CMC→MCP", W("THUMB_CMC_R"), W("THUMB_MCP_R"), None),
        ("MCP→IP", W("THUMB_MCP_R"), W("THUMB_IP_R"), 27.274),
        ("IP→TIP", W("THUMB_IP_R"), WT("THUMB_IP_R"), 21.995)]
CHAIN_REP = []
prev_dir = None
for name, a, b, span in segs:
    d = (b - a).normalized()
    ni, nt = seg(a, b, 1.0)
    ang = None if prev_dir is None else round(math.degrees(math.acos(max(-1, min(1, d.dot(prev_dir))))), 4)
    CHAIN_REP.append({"segment": name, "length_mm": round((b - a).length * MM, 4),
                      "length_reasonable": (span is None) or
                                           (1.0 <= (b - a).length * MM / span <= 1.6),
                      "angle_to_previous_deg": ang, "interior_samples_inside": ni,
                      "interior_samples_total": nt,
                      "t01_axial_span_mm": span,
                      "length_over_axial": (round((b - a).length * MM / span, 4) if span else None)})
    prev_dir = d
log("thumb chain: %s" % CHAIN_REP)

RES = {
    "stage": "STAGE5A_R2A_THUMB_TIP_ONLY_REQUALIFICATION",
    "generated_at": NOW,
    "runtime": {"blender": bpy.app.version_string, "executable": bpy.app.binary_path},
    "branch": "BRANCH_B",
    "input_r2_blend": R2_BLEND, "input_r2_sha256": R2_SHA,
    "input_master": MASTER, "input_master_sha256": MASTER_SHA,
    "output_blend": OUT_BLEND, "output_sha256": OUT_SHA,
    "canonical_semantic": "THUMB_TIP_R = STABLE DISTAL-CAP SURFACE LANDMARK",
    "new_THUMB_TIP_world": [round(float(x), 9) for x in REP],
    "previous_R2_THUMB_TIP_world": [1.456466794, 0.018134484, 0.48759535],
    "shift_mm": round((REP - Vector((1.456466794, 0.018134484, 0.48759535))).length * MM, 4),
    "new_THUMB_TIP_head_local": [round(float(x), 9) for x in new_head_local],
    "new_THUMB_TIP_tail_local": [round(float(x), 9) for x in new_tip_tail_local],
    "new_THUMB_IP_tail_local": [round(float(x), 9) for x in (REP - ASSET_ORIGIN)],
    "THUMB_IP_R_head_unchanged": DRIFT["THUMB_IP_R"]["head_unchanged"],
    "TIP_FRACTION": TIP_FRACTION,
    "cap": {"face_ids": capc, "centroid_world": [round(float(x), 9) for x in cap_c],
            "n_faces": len(capc), "area_mm2": round(area * MM * MM, 4),
            "distal_most_vertex": star,
            "distal_most_vertex_world": [round(float(x), 9) for x in V[star]]},
    "gates": GATE,
    "thumb_chain_geometry": CHAIN_REP,
    "frozen_joint_head_drift": DRIFT,
    "unauthorized_head_changes": unauth,
    "mesh_vertex_delta_mm": round(mesh_delta, 9),
    "topology_delta": 0 if topo_same else 1,
    "uv_delta": 0 if uv_same else 1,
    "material_assignment_delta": 0 if mat_same else 1,
    "mesh_parent": ob2.parent.name if ob2.parent else None,
    "armature_modifier": [m.type for m in ob2.modifiers],
    "vertex_groups": [g.name for g in ob2.vertex_groups],
    "production_skin_weight": "NOT_STARTED",
    "stage5b": "NOT_STARTED",
    "log": LOG,
}
json.dump(RES, open(os.path.join(S5AR2A, "_tmp", "S5A_R2A_BUILD_LOG.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
log("BUILD_LOG written")
print("BUILD_DONE")
