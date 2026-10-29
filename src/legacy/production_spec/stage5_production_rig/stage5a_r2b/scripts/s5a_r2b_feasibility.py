# =====================================================================================
# STAGE5A_R2B -- THUMB_IP FEASIBILITY SEARCH  (READ-ONLY on the R2A blend)
# =====================================================================================
# Question: inside the APPROVED THUMB_IP T-01 joint region, does a production THUMB_IP
# joint centre exist that satisfies every chain-closure gate at once, WITHOUT moving
# THUMB_CMC_R / THUMB_MCP_R / THUMB_TIP_R / the mesh?
#
# T-01 authority (restored, NOT re-invented) -- stage4a_t01/T01_FINAL_AUDIT.json
#   OTHER_T01_JOINTS.THUMB_IP : joint_axial_center_mm = 65.986, zone_half_width_mm = 8.653
#   locator = AXIAL -- joint centre = the web commissure projected on the finger axis
# Pipeline convention (identical to the already-accepted THUMB_MCP T-01 gate in
# STAGE5A_R2_STATUS.json):  axis = unit(THUMB_TIP_R.head - THUMB_CMC_R.head) of the frozen
# Stage4B frame, origin = THUMB_CMC_R.head of the frozen Stage4B frame.
#   (this convention reproduces the accepted THUMB_MCP value 43.300 mm exactly)
# =====================================================================================
import bpy, sys, os, json, math, hashlib, heapq, datetime
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
MM = 1000.0
NOW = datetime.datetime.now().astimezone().isoformat()
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
S5AR2 = r"<HANDS_ROOT>\production_spec\stage5_production_rig\stage5a_r2"
R2A_BLEND = os.path.join(OUTDIR.replace("stage5a_r2b", "stage5a_r2a"),
                         "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
R2A_SHA = "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"

# ---- frozen positions
MCP = Vector((1.454060912, 0.001536574, 0.436873049))          # THUMB_MCP_R.head  (FROZEN)
IP0 = Vector((1.450860858, 0.006127121, 0.464001149))          # current THUMB_IP_R.head (FROZEN until proven)
TIP = Vector((1.45281744, 0.019802358, 0.493028343))           # approved R2A THUMB_TIP_R.head (FROZEN)
CMC = Vector((1.440895081, 0.001219887, 0.3918145))            # THUMB_CMC_R (FROZEN)

jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
cand = json.load(open(os.path.join(S5AR2, "_tmp", "S5A_R2_CANDIDATES.json"), encoding="utf-8"))
t01 = json.load(open(os.path.join(S4, "stage4a_t01", "T01_FINAL_AUDIT.json"), encoding="utf-8"))
AO = Vector(oa["WRIST_ORIGIN"])
DORSAL = {k: Vector(v) for k, v in cand["dorsal_refs"].items()}
R_ENV_THUMB = 11.14

T01I = t01["OTHER_T01_JOINTS"]["THUMB_IP"]
CENTRE = T01I["joint_axial_center_mm"]
ZONE = T01I["zone_half_width_mm"]
A_MIN, A_MAX = CENTRE - ZONE, CENTRE + ZONE
T01_SPAN = {"MCP_IP": 65.986 - 38.712, "IP_TIP": 87.981 - 65.986}   # R2 audit T01_AX

# ---- T-01 axial frame (frozen Stage4B endpoints, pipeline convention)
O = Vector(jf["THUMB_CMC_R"]["head"])
AX = (Vector(jf["THUMB_TIP_R"]["head"]) - O).normalized()
axial = lambda p: (Vector(p) - O).dot(AX) * MM

LOG = []


def log(*a):
    s = " ".join(str(x) for x in a); LOG.append(s); print("[S5A-R2B]", s)


sha = hashlib.sha256(open(R2A_BLEND, "rb").read()).hexdigest()
if sha != R2A_SHA:
    raise SystemExit("FAIL CLOSED: R2A sha256 mismatch")
log("input R2A sha256 = %s" % sha)

bpy.ops.wm.open_mainfile(filepath=R2A_BLEND)
ob = bpy.data.objects["Hand  - Realistic"]
me = ob.data
MW = ob.matrix_world; MINV = MW.inverted(); M3 = MW.to_3x3()
V = [(MW @ v.co).copy() for v in me.vertices]
NV = len(V)
FC = [sum((V[v] for v in p.vertices), Vector()) / len(p.vertices) for p in me.polygons]
log("blend reopened sha = %s" % hashlib.sha256(open(bpy.data.filepath, "rb").read()).hexdigest())


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


def inside_fast(p):
    """signed nearest-surface side test: inside iff (p - nearest) . outward_normal < 0"""
    loc, nor, fi = closest(p)
    if loc is None:
        return False, None, None
    d = Vector(p) - loc
    return (d.dot(nor) < 0.0), d.length, fi


# ---------------------------------------------------------------- ownership (verbatim R2 method)
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
V2F = [[] for _ in range(NV)]
for p in me.polygons:
    for v in p.vertices:
        V2F[v].append(p.index)
VOWN = {}
for v in me.vertices:
    ds = {FO[fi] for fi in V2F[v.index]}
    VOWN[v.index] = ds.pop() if len(ds) == 1 else "MIXED"
THUMB_V = [i for i in range(NV) if VOWN[i] == "THUMB"]

ref = Vector((0.0, 0.0, 1.0)) if abs(AX.z) < 0.9 else Vector((1.0, 0.0, 0.0))
U1 = (ref - AX * ref.dot(AX)).normalized()
U2 = AX.cross(U1).normalized()


def radial(p):
    d = Vector(p) - O
    return (d - AX * d.dot(AX)).length


# ---------------------------------------------------------------- axial slabs inside the T-01 zone
LEVELS = []
a = A_MIN
while a <= A_MAX + 1e-9:
    LEVELS.append(round(a, 4))
    a += 0.5
log("T-01 zone [%.3f, %.3f] mm -> %d axial levels" % (A_MIN, A_MAX, len(LEVELS)))

SECTIONS = []
CANDS = []
for L in LEVELS:
    sel = [i for i in THUMB_V if abs(axial(V[i]) - L) <= 1.2 and radial(V[i]) <= 1.3 * R_ENV_THUMB]
    if len(sel) < 6:
        SECTIONS.append({"level_mm": L, "n": len(sel), "skipped": True})
        continue
    c = sum((V[i] for i in sel), Vector()) / len(sel)
    rs = sorted(radial(V[i]) for i in sel)
    r95 = rs[int(0.95 * (len(rs) - 1))]
    # projected convex-hull area of the section
    pts = [(V[i].dot(U1), V[i].dot(U2)) for i in sel]
    hull = []
    for pt in sorted(set(pts)):
        while len(hull) >= 2 and ((hull[-1][0] - hull[-2][0]) * (pt[1] - hull[-2][1]) -
                                  (hull[-1][1] - hull[-2][1]) * (pt[0] - hull[-2][0])) <= 0:
            hull.pop()
        hull.append(pt)
    for pt in reversed(sorted(set(pts))):
        while len(hull) >= 2 and ((hull[-1][0] - hull[-2][0]) * (pt[1] - hull[-2][1]) -
                                  (hull[-1][1] - hull[-2][1]) * (pt[0] - hull[-2][0])) <= 0:
            hull.pop()
        hull.append(pt)
    area = 0.0
    for i in range(len(hull)):
        x1, y1 = hull[i]; x2, y2 = hull[(i + 1) % len(hull)]
        area += x1 * y2 - x2 * y1
    area = abs(area) / 2.0
    SECTIONS.append({"level_mm": L, "n": len(sel), "skipped": False,
                     "centroid_world": [round(float(x), 9) for x in c],
                     "r95_mm": round(r95 * MM, 4), "r_max_mm": round(rs[-1] * MM, 4),
                     "hull_area_mm2": round(area * MM * MM, 4)})
    # ---- candidates: section centroid + polar interior grid
    grid = [("centroid", c)]
    for fr in (0.25, 0.50, 0.75):
        for k in range(8):
            th = 2 * math.pi * k / 8.0
            grid.append(("grid", c + (U1 * math.cos(th) + U2 * math.sin(th)) * fr * r95))
    for kind, p in grid:
        ok, dist, fi = inside_fast(p)
        if not ok:
            continue
        owner = FO.get(fi)
        if owner != "THUMB":
            continue
        CANDS.append({"level_mm": L, "kind": kind, "p": p,
                      "clearance_mm": round(dist * MM, 4),
                      "axial_mm": round(axial(p), 4),
                      "axial_delta_mm": round(axial(p) - CENTRE, 4),
                      "radial_mm": round(radial(p) * MM, 4),
                      "owner": owner})

log("candidates passing inside+ownership: %d" % len(CANDS))


# ---------------------------------------------------------------- segment interior scoring
def sample_scores(a, b, n, strict=False):
    """n uniform interior samples on t in (0,1); returns (inside_count, min_margin_mm)"""
    ins = 0
    mmin = 1e9
    for k in range(1, n + 1):
        t = k / (n + 1.0)
        q = a + (b - a) * t
        if strict:
            h, tot = parity(q)
            ok = h > tot / 2
            loc, nor, fi = closest(q)
            mmin = min(mmin, (Vector(q) - loc).length * MM)
        else:
            ok, d, fi = inside_fast(q)
            mmin = min(mmin, d * MM)
        if ok:
            ins += 1
    return ins, round(mmin, 4)


def kink(a, b, c):
    d1 = (b - a).normalized(); d2 = (c - b).normalized()
    return math.degrees(math.acos(max(-1.0, min(1.0, d1.dot(d2)))))


MIN_CLEAR = 3.0
stage1 = [c for c in CANDS if c["clearance_mm"] >= MIN_CLEAR]
log("candidates with clearance >= %.1f mm: %d" % (MIN_CLEAR, len(stage1)))

results = []
for c in stage1:
    p = c["p"]
    i20, m20 = sample_scores(MCP, p, 20)
    if i20 != 20:
        c["fail"] = "MCP_TO_IP_INTERIOR_20=%d/20" % i20
        results.append(c); continue
    t20, mt20 = sample_scores(p, TIP, 20)
    if t20 != 20:
        c["fail"] = "IP_TO_TIP_INTERIOR_20=%d/20" % t20
        results.append(c); continue
    i40, m40 = sample_scores(MCP, p, 40)
    t40, mt40 = sample_scores(p, TIP, 40)
    if i40 != 40:
        c["fail"] = "MCP_TO_IP_INTERIOR_40=%d/40" % i40
        results.append(c); continue
    if t40 != 40:
        c["fail"] = "IP_TO_TIP_INTERIOR_40=%d/40" % t40
        results.append(c); continue
    L1 = (p - MCP).length * MM
    L2 = (TIP - p).length * MM
    r1 = L1 / T01_SPAN["MCP_IP"]
    r2 = L2 / T01_SPAN["IP_TIP"]
    kk = kink(MCP, p, TIP)
    ok_len = (1.0 <= r1 <= 1.6) and (1.0 <= r2 <= 1.6)
    ok_kink = kk <= 60.0
    c.update({"MCP_IP_len_mm": round(L1, 4), "IP_TIP_len_mm": round(L2, 4),
              "MCP_IP_over_T01_axial": round(r1, 4), "IP_TIP_over_T01_axial": round(r2, 4),
              "chain_kink_deg": round(kk, 4),
              "MCP_TO_IP_INTERIOR_20": i20, "MCP_TO_IP_INTERIOR_40": i40,
              "IP_TO_TIP_INTERIOR_20": t20, "IP_TO_TIP_INTERIOR_40": t40,
              "MCP_TO_IP_min_margin_mm": m40, "IP_TO_TIP_min_margin_mm": mt40,
              "min_segment_margin_mm": round(min(m40, mt40), 4),
              "shift_from_current_IP_mm": round((p - IP0).length * MM, 4),
              "length_reasonable": ok_len, "kink_reasonable": ok_kink})
    c["fail"] = None if (ok_len and ok_kink) else (
        ("length_out_of_band" if not ok_len else "") + (" kink>60" if not ok_kink else "")).strip()
    results.append(c)

feasible_fast = [c for c in results if c.get("fail") is None]
log("fast-filter feasible: %d" % len(feasible_fast))

# ---- STRICT 64-ray parity confirmation on every fast-feasible candidate
for c in feasible_fast:
    p = c["p"]
    h, tot = parity(p)
    c["STRICT_point_parity"] = "%d/%d" % (h, tot)
    a20 = sample_scores(MCP, p, 20, strict=True)
    a40 = sample_scores(MCP, p, 40, strict=True)
    b20 = sample_scores(p, TIP, 20, strict=True)
    b40 = sample_scores(p, TIP, 40, strict=True)
    c["STRICT_MCP_TO_IP_20"] = a20[0]; c["STRICT_MCP_TO_IP_40"] = a40[0]
    c["STRICT_IP_TO_TIP_20"] = b20[0]; c["STRICT_IP_TO_TIP_40"] = b40[0]
    c["STRICT_min_margin_mm"] = round(min(a40[1], b40[1]), 4)
    c["STRICT_FEASIBLE"] = (c["STRICT_MCP_TO_IP_20"] == 20 and c["STRICT_MCP_TO_IP_40"] == 40
                            and c["STRICT_IP_TO_TIP_20"] == 20 and c["STRICT_IP_TO_TIP_40"] == 40
                            and h > tot / 2)

strict_ok = [c for c in feasible_fast if c["STRICT_FEASIBLE"]]
log("STRICT feasible: %d" % len(strict_ok))

# ---- current IP baseline (for before/after)
def baseline(p, label):
    i20 = sample_scores(MCP, p, 20)[0]; i40 = sample_scores(MCP, p, 40)[0]
    t20 = sample_scores(p, TIP, 20)[0]; t40 = sample_scores(p, TIP, 40)[0]
    a20s = sample_scores(MCP, p, 20, strict=True)[0]; a40s = sample_scores(MCP, p, 40, strict=True)[0]
    t20s = sample_scores(p, TIP, 20, strict=True)[0]; t40s = sample_scores(p, TIP, 40, strict=True)[0]
    return {"label": label, "point_world": [round(float(x), 9) for x in p],
            "axial_mm": round(axial(p), 4), "axial_delta_mm": round(axial(p) - CENTRE, 4),
            "MCP_TO_IP_INTERIOR_20": i20, "MCP_TO_IP_INTERIOR_40": i40,
            "IP_TO_TIP_INTERIOR_20": t20, "IP_TO_TIP_INTERIOR_40": t40,
            "STRICT_MCP_TO_IP_20": a20s, "STRICT_MCP_TO_IP_40": a40s,
            "STRICT_IP_TO_TIP_20": t20s, "STRICT_IP_TO_TIP_40": t40s,
            "MCP_IP_len_mm": round((p - MCP).length * MM, 4),
            "IP_TIP_len_mm": round((TIP - p).length * MM, 4),
            "chain_kink_deg": round(kink(MCP, p, TIP), 4)}


BASE = baseline(IP0, "R2A_current_THUMB_IP_R.head")
log("baseline current IP: MCP->IP %d/%d  IP->TIP %d/%d (strict)"
    % (BASE["STRICT_MCP_TO_IP_40"], 40, BASE["STRICT_IP_TO_TIP_40"], 40))

# ---- deterministic ranking
def rankkey(c):
    return (round(abs(c["axial_delta_mm"]), 3),
            -round(c.get("STRICT_min_margin_mm", c["min_segment_margin_mm"]), 3),
            round(c["chain_kink_deg"], 2),
            round(c["shift_from_current_IP_mm"], 3))


pool = strict_ok if strict_ok else [c for c in feasible_fast]
ranked = sorted(pool, key=rankkey)


def pack(c, i):
    return {"rank": i, "level_mm": c["level_mm"], "kind": c["kind"],
            "world_position": [round(float(x), 9) for x in c["p"]],
            "axial_mm": c["axial_mm"], "axial_delta_mm": c["axial_delta_mm"],
            "clearance_mm": c["clearance_mm"],
            "MCP_IP_len_mm": c.get("MCP_IP_len_mm"), "IP_TIP_len_mm": c.get("IP_TIP_len_mm"),
            "MCP_IP_over_T01_axial": c.get("MCP_IP_over_T01_axial"),
            "IP_TIP_over_T01_axial": c.get("IP_TIP_over_T01_axial"),
            "chain_kink_deg": c.get("chain_kink_deg"),
            "shift_from_current_IP_mm": c.get("shift_from_current_IP_mm"),
            "STRICT_MCP_TO_IP_20": c.get("STRICT_MCP_TO_IP_20"),
            "STRICT_MCP_TO_IP_40": c.get("STRICT_MCP_TO_IP_40"),
            "STRICT_IP_TO_TIP_20": c.get("STRICT_IP_TO_TIP_20"),
            "STRICT_IP_TO_TIP_40": c.get("STRICT_IP_TO_TIP_40"),
            "STRICT_min_margin_mm": c.get("STRICT_min_margin_mm"),
            "STRICT_FEASIBLE": c.get("STRICT_FEASIBLE", False)}

TOP = [pack(c, i + 1) for i, c in enumerate(ranked[:20])]

VOLUME = {
    "stage": "STAGE5A_R2B_THUMB_IP_FEASIBILITY_SEARCH",
    "generated_at": NOW, "read_only": True,
    "input_blend": R2A_BLEND, "input_sha256": R2A_SHA,
    "T01_authority": {
        "source": "stage4_blender/stage4a_t01/T01_FINAL_AUDIT.json",
        "path": "OTHER_T01_JOINTS.THUMB_IP",
        "locator": T01I["locator"],
        "axial_finger_length_mm": T01I["axial_finger_length_mm"],
        "approved_axial_centre_mm": CENTRE,
        "zone_half_width_mm": ZONE,
        "zone_mm": [round(A_MIN, 4), round(A_MAX, 4)],
        "actual_edge_loops": T01I["ACTUAL_EDGE_LOOPS"],
        "loop_positions_axial_mm": T01I["LOOP_POSITION_axial_from_commissure_mm"],
        "axis_definition": ("unit(THUMB_TIP_R.head - THUMB_CMC_R.head) of the frozen Stage4B "
                            "joint frame; origin = THUMB_CMC_R.head of the same frame.  This is "
                            "the pipeline convention already used for the accepted THUMB_MCP "
                            "T-01 gate (it reproduces 43.300 mm exactly)."),
        "axis_world": [round(float(x), 9) for x in AX],
        "origin_world": [round(float(x), 9) for x in O],
        "T01_axial_spans": {"MCP_IP": T01_SPAN["MCP_IP"], "IP_TIP": T01_SPAN["IP_TIP"]},
    },
    "frozen_positions": {
        "THUMB_CMC_R": [round(float(x), 9) for x in CMC],
        "THUMB_MCP_R_head": [round(float(x), 9) for x in MCP],
        "THUMB_IP_R_head_current": [round(float(x), 9) for x in IP0],
        "THUMB_TIP_R_head_R2A": [round(float(x), 9) for x in TIP]},
    "search_volume": {
        "axial_constraint": "T-01 zone [%.3f, %.3f] mm" % (A_MIN, A_MAX),
        "cross_section_constraint": ("thumb-owned surface vertices within +/-1.2 mm of the slab "
                                     "plane and radial <= 1.3 x R_env(thumb) = %.2f mm; candidates "
                                     "are the section centroid plus a polar interior grid at "
                                     "0.25/0.50/0.75 x r95 (8 directions)" % (1.3 * R_ENV_THUMB)),
        "ownership_constraint": "nearest surface face owner must be THUMB",
        "inside_constraint": "signed nearest-surface side test (prefilter) + 64-ray parity (strict)",
        "axial_levels_sampled": len(LEVELS),
        "levels": [round(l, 3) for l in LEVELS]},
    "current_IP_baseline": BASE,
    "counts": {
        "candidates_total_inside_and_owned": len(CANDS),
        "candidates_after_clearance_prefilter": len(stage1),
        "fast_filter_feasible": len(feasible_fast),
        "strict_parity_feasible": len(strict_ok)},
    "sections": SECTIONS,
    "candidate_records": [{k: v for k, v in c.items() if k != "p"} |
                          {"world_position": [round(float(x), 9) for x in c["p"]]} for c in results],
    "top_ranking_preview": TOP[:5],
}
json.dump(VOLUME, open(os.path.join(OUTDIR, "STAGE5A_R2B_THUMB_IP_FEASIBILITY_VOLUME.json"),
                       "w", encoding="utf-8"), indent=1, ensure_ascii=False)

RANK = {
    "stage": "STAGE5A_R2B_FEASIBLE_CANDIDATE_RANKING",
    "generated_at": NOW, "read_only": True,
    "input_blend": R2A_BLEND, "input_sha256": R2A_SHA,
    "ranking_rule": ("deterministic lexicographic key, declared priority order: "
                     "1) |T-01 axial delta| ascending (closest to the approved axial centre); "
                     "2) minimum segment volume margin descending; 3) chain kink ascending; "
                     "4) shift from the current IP ascending.  Minimum displacement is "
                     "deliberately LAST and cannot override joint correctness."),
    "strict_feasible_count": len(strict_ok),
    "fast_feasible_count": len(feasible_fast),
    "top": TOP[:5] if len(TOP) >= 5 else TOP,
    "listed_count": min(5, len(TOP)),
    "THUMB_IP_FEASIBLE_REGION": ("EXISTS" if strict_ok else "NONE_WITHIN_APPROVED_T01_REGION"),
}
json.dump(RANK, open(os.path.join(OUTDIR, "STAGE5A_R2B_FEASIBLE_CANDIDATE_RANKING.json"),
                     "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump({"log": LOG, "base": BASE, "n_strict": len(strict_ok), "n_fast": len(feasible_fast),
           "n_cands": len(CANDS)},
          open(os.path.join(OUTDIR, "_tmp", "S5A_R2B_SEARCH_LOG.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
log("strict feasible = %d ; fast feasible = %d" % (len(strict_ok), len(feasible_fast)))
print("SEARCH_DONE")
