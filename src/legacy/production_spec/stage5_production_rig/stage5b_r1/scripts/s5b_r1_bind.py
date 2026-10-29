# =====================================================================================
# STAGE5B_R1 -- PRODUCTION SKIN BINDING  (deterministic hybrid weighting)
# =====================================================================================
# INPUT  (frozen):  stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend
#                   sha256 c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845
# OUTPUT (new):     stage5b_r1/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend
#
# Weighting method: SEMANTIC REGION + BONE LOCAL DISTANCE + JOINT TRANSITION BLEND
#                   + GEODESIC / OWNERSHIP GUARD
#   * longitudinal coordinate = MESH GEODESIC distance from the digit's distal-most vertex
#     (this follows the CURVED distal segment -- it is NOT the straight bone chord, so the
#      THUMB_IP distal authority is respected);
#   * transition half-width tau per joint is DERIVED from the approved T-01 deformation
#     loop spacing (interior joints) and from the approved T-01 zone half-width (MCP root
#     fan) -- no hand-picked 5/10 mm constants;
#   * lateral term = exp(-(d/L0)^2) with L0 derived from the mesh;
#   * allowed-bone whitelist per semantic region: cross-digit influence is FORBIDDEN
#     except the sanctioned thumb/index first-web root blend.
# =====================================================================================
import bpy, sys, os, json, math, hashlib, heapq, datetime
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
MM = 1000.0
NOW = datetime.datetime.now().astimezone().isoformat()
TOP = os.path.dirname(OUTDIR)                      # .../stage5_production_rig
S4 = os.path.join(os.path.dirname(TOP), "stage4_blender")
S5AR2 = os.path.join(TOP, "stage5a_r2")
R2A = os.path.join(TOP, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
R2A_SHA = "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"
OUT_BLEND = os.path.join(OUTDIR, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend")
MAX_INF = 4

jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
nail = json.load(open(os.path.join(S4, "stage4c_r2", "NAIL_AUDIT_R2.json"), encoding="utf-8"))
t01 = json.load(open(os.path.join(S4, "stage4a_t01", "T01_FINAL_AUDIT.json"), encoding="utf-8"))
cand = json.load(open(os.path.join(S5AR2, "_tmp", "S5A_R2_CANDIDATES.json"), encoding="utf-8"))
AO = Vector(oa["WRIST_ORIGIN"])
DORSAL = {k: Vector(v) for k, v in cand["dorsal_refs"].items()}
R_ENV = {"thumb": 11.14, "index": 7.64, "middle": 7.80, "ring": 7.15, "little": 6.75}
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a); LOG.append(s); print("[S5B]", s)


sha_in = hashlib.sha256(open(R2A, "rb").read()).hexdigest()
if sha_in != R2A_SHA:
    raise SystemExit("FAIL CLOSED: Stage5A master sha256 drift")
log("input Stage5A master sha256 = %s" % sha_in)

bpy.ops.wm.open_mainfile(filepath=R2A)
ob = bpy.data.objects["Hand  - Realistic"]
me = ob.data
MW0 = ob.matrix_world.copy()
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
V0 = [(MW0 @ v.co).copy() for v in me.vertices]
NV = len(me.vertices)
TOPO0 = [tuple(p.vertices) for p in me.polygons]
UV0 = [tuple(round(u, 9) for u in d.uv) for d in me.uv_layers.active.data] if me.uv_layers.active else []
MAT0 = [p.material_index for p in me.polygons]
NW0 = ob.matrix_world.copy()

MINV = MW0.inverted(); M3 = MW0.to_3x3()


def closest(p):
    ok, loc, nor, idx = ob.closest_point_on_mesh(MINV @ Vector(p))
    return (MW0 @ loc, (M3 @ nor).normalized(), idx) if ok else (None, None, None)


CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"], "LITTLE": ["MCP", "PIP", "DIP"]}
DDIGIT = {"THUMB": "thumb", "INDEX": "index", "MIDDLE": "middle", "RING": "ring", "LITTLE": "little"}
DEFORM = ["WRIST_R"] + ["%s_%s_R" % (d, s) for d in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE")
                        for s in CHAIN[d]]
assert len(DEFORM) == 16, len(DEFORM)
TIPB = ["%s_TIP_R" % d for d in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE")]


def d_poly(p, poly):
    b = 1e9
    for i in range(len(poly) - 1):
        a, q = poly[i], poly[i + 1]; ab = q - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
        b = min(b, (p - (a + ab * t)).length)
    return b


def chainpts(D):
    p = [Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])]
    for s in CHAIN[D]:
        p.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
    return p


AC = {D: chainpts(D) for D in CHAIN}
AC["wrist"] = [AO, Vector(jf["WRIST_R"]["tail"])]
FC = [sum((V0[v] for v in p.vertices), Vector()) / len(p.vertices) for p in me.polygons]
FO = {}
for p in me.polygons:
    FO[p.index] = min(AC, key=lambda D: d_poly(FC[p.index], AC[D]))
V2F = [[] for _ in range(NV)]
for p in me.polygons:
    for v in p.vertices:
        V2F[v].append(p.index)
# vertex-level ownership (continuous: nearest chain polyline)
OWN_V = [min(AC, key=lambda D: d_poly(V0[i], AC[D])) for i in range(NV)]

EADJ = {}
EDGES = [(e.vertices[0], e.vertices[1]) for e in me.edges]
for a, b in EDGES:
    w = (V0[a] - V0[b]).length
    EADJ.setdefault(a, []).append((b, w)); EADJ.setdefault(b, []).append((a, w))


def dij(src):
    d = {src: 0.0}; pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d.get(u, 1e18) + 1e-15:
            continue
        for v, w in EADJ.get(u, ()):
            if du + w < d.get(v, 1e18) - 1e-16:
                d[v] = du + w; heapq.heappush(pq, (du + w, v))
    return d


# ---------------------------------------------------------------- geodesic per digit
GEO = {}
DSTAR = {}
for D in CHAIN:
    dn = DDIGIT[D]
    dseg = "IP" if D == "THUMB" else "DIP"
    P = Vector(jf["%s_%s_R" % (D, dseg)]["head"])
    T = Vector(jf["%s_TIP_R" % D]["head"])
    u0 = (T - P).normalized()
    dv = [i for i in range(NV) if OWN_V[i] == D]
    cvd = [i for i in dv if (V0[i] - P).dot(u0) > 0.0]
    star = max(cvd, key=lambda i: (V0[i] - P).length)
    DSTAR[D] = star
    GEO[D] = dij(star)
    log("geodesic seed %s D*=v%d" % (D, star))


def gval(D, p):
    """geodesic distance of a point from the digit's distal-most vertex"""
    g = GEO[D]
    best = None; bi = None
    for i in range(NV):
        if (V0[i] - p).length < 0.0025:
            v = g.get(i)
            if v is not None and (best is None or v < best):
                best = v; bi = i
    if bi is None:
        bi = min(range(NV), key=lambda i: (V0[i] - p).length)
        best = g.get(bi)
    return best, bi


# ---------------------------------------------------------------- tau table (derived)
def loop_median(key):
    for grp in ("T01_MCP", "OTHER_T01_JOINTS"):
        if key in t01.get(grp, {}):
            L = t01[grp][key]["LOOP_POSITION_axial_from_commissure_mm"]
            s = sorted(round(L[i + 1] - L[i], 4) for i in range(len(L) - 1))
            if s:
                return s[len(s) // 2], t01[grp][key]["zone_half_width_mm"]
    return None, None


ELEN = sorted((V0[a] - V0[b]).length * MM for a, b in EDGES)
MED_EDGE = ELEN[len(ELEN) // 2]
W_WEB = 2.0 * MED_EDGE * 1e-3
log("mesh median edge length = %.4f mm" % MED_EDGE)

TAU = {}
JOINT_TAU = {}
for D in ("INDEX", "MIDDLE", "RING", "LITTLE"):
    med, zhw = loop_median("%s_MCP" % D)
    JOINT_TAU["%s_MCP" % D] = {"tau_interior_mm": round(0.5 * (med or MED_EDGE), 4),
                               "tau_root_mm": round(zhw or (2 * MED_EDGE), 4),
                               "derived_from": "T-01 %s_MCP loop spacing / zone half width" % D}
    for s in ("PIP", "DIP"):
        m2, _ = loop_median("%s_%s" % (D, s))
        JOINT_TAU["%s_%s" % (D, s)] = {"tau_interior_mm": round(0.5 * (m2 or MED_EDGE), 4),
                                       "tau_root_mm": None,
                                       "derived_from": "T-01 %s_%s loop spacing" % (D, s)}
for k, nm in (("THUMB_MCP", "THUMB_MCP"), ("THUMB_IP", "THUMB_IP")):
    med, zhw = loop_median(k)
    JOINT_TAU[k] = {"tau_interior_mm": round(0.5 * (med or MED_EDGE), 4),
                    "tau_root_mm": (round(zhw, 4) if k == "THUMB_MCP" else None),
                    "derived_from": "T-01 %s loop spacing / zone half width" % k}
JOINT_TAU["THUMB_CMC"] = {"tau_interior_mm": round(0.5 * MED_EDGE, 4),
                          "tau_root_mm": round(MED_EDGE, 4),
                          "derived_from": "no T-01 CMC loops -> local mesh median edge length"}
TAU_WRIST_PROX = 60.0
med_mcp = [JOINT_TAU["%s_MCP" % D]["tau_root_mm"] for D in ("INDEX", "MIDDLE", "RING", "LITTLE")]
TAU_WRIST_DIST = round(sum(med_mcp) / len(med_mcp), 4)
log("tau table built; wrist dist tau = %.4f mm" % TAU_WRIST_DIST)

# ---------------------------------------------------------------- bone geometry
BH = {}
BT = {}
for b in rig.data.bones:
    BH[b.name] = rig.matrix_world @ b.head_local
    BT[b.name] = rig.matrix_world @ b.tail_local


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
    return (p - (a + ab * t)).length


DIGIT_OF_BONE = {}
for D in CHAIN:
    for s in CHAIN[D]:
        DIGIT_OF_BONE["%s_%s_R" % (D, s)] = D
DIGIT_OF_BONE["WRIST_R"] = "wrist"

# longitudinal coordinate: ARC LENGTH along the chain polyline (robust + monotone).
# NOTE: deliberately NOT the straight bone chord -- see the thumb distal guard below.
POLY = {}
for D in CHAIN:
    pts = [Vector(jf["%s_%s_R" % (D, s)]["head"]) for s in CHAIN[D]]
    pts.append(Vector(jf["%s_TIP_R" % D]["head"]))
    POLY[D] = pts
    log("chain %s arc: %s" % (D, [round((pts[i + 1] - pts[i]).length * MM, 3)
                                  for i in range(len(pts) - 1)]))


XIJ = {}
for D in CHAIN:
    pts = POLY[D]
    acc = 0.0
    a = [0.0]
    for k in range(len(pts) - 1):
        acc += (pts[k + 1] - pts[k]).length
        a.append(acc * MM)
    XIJ[D] = [round(x, 4) for x in a]
    log("chain %s joint arc (mm): %s" % (D, XIJ[D]))


def arc_of(D, v):
    pts = POLY[D]
    best = (1e9, None, None)
    acc = 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (v - a).dot(ab) / max(ab.length_squared, 1e-18)))
        d = ((v - (a + ab * t))).length
        if d < best[0]:
            best = (d, acc + t * ab.length, i)
        acc += ab.length
    return best[1], best[0]      # arc length (mm-scale in m), perpendicular distance


# WRIST uses its own straight axis
wH = BH["WRIST_R"]; wT = BT["WRIST_R"]
wU = (wT - wH).normalized(); wL = (wT - wH).length


def S(z):
    z = max(0.0, min(1.0, z))
    return z * z * (3.0 - 2.0 * z)


# ---------------------------------------------------------------- lateral scale per bone
# L0(bone) = median distance from that bone's segment to the vertices of its own semantic
# digit.  Data derived, per bone (the palm is wide, a finger shaft is narrow).
BONE_DIGIT_VERTS = {}
for b in DEFORM:
    D = DIGIT_OF_BONE[b]
    BONE_DIGIT_VERTS[b] = [i for i in range(NV) if OWN_V[i] == D] or list(range(NV))
L0B = {}
for b in DEFORM:
    ds = sorted(seg_dist(V0[i], BH[b], BT[b]) for i in BONE_DIGIT_VERTS[b][::3])
    L0B[b] = max(0.002, ds[len(ds) // 2])
log("lateral scales (mm): " + ", ".join("%s=%.2f" % (b, L0B[b] * MM) for b in DEFORM))

# ---------------------------------------------------------------- weights
NAIL_THUMB_V = set()
for _p in me.polygons:
    if _p.material_index == 1 and FO[_p.index] == "THUMB":
        NAIL_THUMB_V.update(_p.vertices)
log("thumb NAIL_BED vertices: %d" % len(NAIL_THUMB_V))
WEI = [dict() for _ in range(NV)]
for i in range(NV):
    v = V0[i]
    own = OWN_V[i]
    allowed = set(["WRIST_R"])
    if own in CHAIN:
        for s in CHAIN[own]:
            allowed.add("%s_%s_R" % (own, s))
    else:
        # palm / forearm: WRIST dominant + the metacarpal-root fan
        allowed.add("THUMB_CMC_R")
        for D in ("INDEX", "MIDDLE", "RING", "LITTLE"):
            allowed.add("%s_MCP_R" % D)
    # --- first web sanctioned cross blend (thumb <-> index, ROOT LEVEL ONLY)
    if own in ("THUMB", "INDEX"):
        # FIRST WEB: the region lying BETWEEN the thumb and the index chains.
        # W = 2 x the mesh median edge length (data derived).
        if d_poly(v, AC["THUMB"]) <= W_WEB and d_poly(v, AC["INDEX"]) <= W_WEB:
            # first-web SEMANTIC WHITELIST: only root-level groups may enter.
            # THUMB_IP, INDEX_PIP, INDEX_DIP are explicitly forbidden here (brief s18).
            if i not in NAIL_THUMB_V:
                allowed -= {"THUMB_IP_R", "INDEX_PIP_R", "INDEX_DIP_R"}
            if own == "THUMB":
                allowed.add("INDEX_MCP_R")
            else:
                allowed.add("THUMB_CMC_R"); allowed.add("THUMB_MCP_R")
    elif own == "MIDDLE":
        pass
    raw = {}
    for b in allowed:
        D = DIGIT_OF_BONE[b]
        if D == "wrist":
            x = (v - wH).dot(wU) * MM
            wLmm = wL * MM
            lam = 1.0 if x <= wLmm else math.exp(-((x - wLmm) / TAU_WRIST_DIST) ** 2)
        else:
            segname = b.split("_")[1]
            idx = CHAIN[D].index(segname)
            xi, _perp = arc_of(D, v)
            xi *= MM
            xh = XIJ[D][idx]; xt = XIJ[D][idx + 1]
            Lj = xt - xh
            mj = 0.5 * (xh + xt)
            tk = "%s_%s" % (D, segname)
            tau_h = (JOINT_TAU[tk]["tau_root_mm"]
                     if (JOINT_TAU[tk].get("tau_root_mm") and idx == 0)
                     else JOINT_TAU[tk]["tau_interior_mm"])
            nxt = CHAIN[D][idx + 1] if idx + 1 < len(CHAIN[D]) else None
            tau_t = (JOINT_TAU["%s_%s" % (D, nxt)]["tau_interior_mm"] if nxt
                     else JOINT_TAU[tk]["tau_interior_mm"])
            kappa = 0.5 * Lj + 0.5 * (tau_h + tau_t)
            lam = math.exp(-((xi - mj) / kappa) ** 2)
        d = seg_dist(v, BH[b], BT[b]) * MM
        mu = math.exp(-(d / (L0B[b] * MM)) ** 2)
        raw[b] = lam * mu
    # ---- FOREARM GUARD: proximal of the WRIST_R head, WRIST_R is ABSOLUTE
    if (v - wH).dot(wU) < 0.0:
        raw = {"WRIST_R": 1.0}
    # ---- THUMB DISTAL OWNERSHIP GUARD (arc-length along the thumb chain + ownership,
    #      NOT the straight bone chord)
    elif own == "THUMB" and "THUMB_IP_R" in raw:
        xi, _p = arc_of("THUMB", v)
        if (i in NAIL_THUMB_V or xi * MM <= XIJ["THUMB"][2]
                + JOINT_TAU["THUMB_IP"]["tau_interior_mm"]):
            others = sum(vv for k, vv in raw.items() if k != "THUMB_IP_R")
            raw["THUMB_IP_R"] = max(raw["THUMB_IP_R"], 2.0 * others)
    tot = sum(raw.values())
    if tot <= 1e-14:
        nb = min(allowed, key=lambda b: seg_dist(v, BH[b], BT[b]))
        raw = {nb: 1.0}
        tot = 1.0
    WEI[i] = {k: vv / tot for k, vv in raw.items()}

log("raw weights computed for %d vertices" % NV)

# ---------------------------------------------------------------- prune + normalize
PRUNE = {"max_influences_before": 0, "vertices_pruned": 0, "total_discarded_weight": 0.0,
         "worst_discarded_weight_per_vertex": 0.0, "worst_vertex": None}
for i in range(NV):
    w = WEI[i]
    PRUNE["max_influences_before"] = max(PRUNE["max_influences_before"], len(w))
    if len(w) > MAX_INF:
        items = sorted(w.items(), key=lambda kv: -kv[1])
        keep = items[:MAX_INF]
        disc = sum(kv[1] for kv in items[MAX_INF:])
        PRUNE["vertices_pruned"] += 1
        PRUNE["total_discarded_weight"] += disc
        if disc > PRUNE["worst_discarded_weight_per_vertex"]:
            PRUNE["worst_discarded_weight_per_vertex"] = disc
            PRUNE["worst_vertex"] = i
        s = sum(kv[1] for kv in keep)
        w = {k: (vv / s if s > 0 else 1.0 / len(keep)) for k, vv in keep}
        WEI[i] = w
# final normalization
NORM_ERR = 0.0
for i in range(NV):
    w = WEI[i]
    s = sum(w.values())
    if s <= 0:
        continue
    NORM_ERR = max(NORM_ERR, abs(s - 1.0))
    if abs(s - 1.0) > 1e-12:
        WEI[i] = {k: vv / s for k, vv in w.items()}
PRUNE["max_influences_after"] = max(len(w) for w in WEI)
log("prune: before %d after %d, vertices_pruned %d, discarded %.6f"
    % (PRUNE["max_influences_before"], PRUNE["max_influences_after"],
       PRUNE["vertices_pruned"], PRUNE["total_discarded_weight"]))

# ---------------------------------------------------------------- write vertex groups
for vg in list(ob.vertex_groups):
    ob.vertex_groups.remove(vg)
for b in DEFORM:
    ob.vertex_groups.new(name=b)
VG = {g.name: g for g in ob.vertex_groups}
for b in DEFORM:
    idx = [i for i in range(NV) if WEI[i].get(b, 0.0) > 0.0]
    if not idx:
        continue
    for i in idx:
        VG[b].add([i], float(WEI[i][b]), 'REPLACE')
GROUP_NAMES = sorted(g.name for g in ob.vertex_groups)
log("vertex groups written: %d -> %s" % (len(GROUP_NAMES), GROUP_NAMES))

# ---------------------------------------------------------------- parent + armature modifier
PARENT_BEFORE = [list(r) for r in ob.matrix_world]
ob.parent = rig
ob.matrix_parent_inverse = rig.matrix_world.inverted()
PARENT_AFTER = [list(r) for r in ob.matrix_world]
mod = ob.modifiers.new("PRODUCTION_ARMATURE", 'ARMATURE')
mod.object = rig
mod.use_vertex_groups = True
log("parent + ARMATURE modifier created")

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, copy=True, compress=False)
OUT_SHA = hashlib.sha256(open(OUT_BLEND, "rb").read()).hexdigest()
log("SAVED %s" % OUT_BLEND)
log("SAVED sha256 = %s" % OUT_SHA)

json.dump({"log": LOG, "L0_per_bone_mm": {b: round(L0B[b] * MM, 4) for b in DEFORM}, "tau": JOINT_TAU, "tau_wrist_prox": TAU_WRIST_PROX,
           "tau_wrist_dist": TAU_WRIST_DIST, "med_edge_mm": MED_EDGE,
           "deform_bones": DEFORM, "out_sha": OUT_SHA},
          open(os.path.join(OUTDIR, "_tmp", "S5B_R1_BUILD_LOG.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("BIND_DONE")
