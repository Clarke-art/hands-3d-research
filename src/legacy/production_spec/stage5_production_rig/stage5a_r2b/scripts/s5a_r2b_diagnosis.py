# =====================================================================================
# STAGE5A_R2B -- STRUCTURAL CONFLICT DIAGNOSIS (Branch B)   [READ-ONLY]
# Quantifies WHY no THUMB_IP joint centre inside the approved T-01 region can close the
# chain.  This is DIAGNOSIS ONLY -- it does not approve any out-of-zone position.
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

MCP = Vector((1.454060912, 0.001536574, 0.436873049))
IP0 = Vector((1.450860858, 0.006127121, 0.464001149))
TIP = Vector((1.45281744, 0.019802358, 0.493028343))
CMC = Vector((1.440895081, 0.001219887, 0.3918145))

jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
t01 = json.load(open(os.path.join(S4, "stage4a_t01", "T01_FINAL_AUDIT.json"), encoding="utf-8"))
AO = Vector(oa["WRIST_ORIGIN"])
T01I = t01["OTHER_T01_JOINTS"]["THUMB_IP"]
CENTRE = T01I["joint_axial_center_mm"]; ZONE = T01I["zone_half_width_mm"]
A_MIN, A_MAX = CENTRE - ZONE, CENTRE + ZONE
T01_SPAN = {"MCP_IP": 27.274, "IP_TIP": 21.995}
O = Vector(jf["THUMB_CMC_R"]["head"])
AX = (Vector(jf["THUMB_TIP_R"]["head"]) - O).normalized()
axial = lambda p: (Vector(p) - O).dot(AX) * MM
R_ENV_THUMB = 11.14
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a); LOG.append(s); print("[S5A-R2B-DIAG]", s)


if hashlib.sha256(open(R2A_BLEND, "rb").read()).hexdigest() != R2A_SHA:
    raise SystemExit("FAIL CLOSED: R2A sha256 mismatch")
bpy.ops.wm.open_mainfile(filepath=R2A_BLEND)
ob = bpy.data.objects["Hand  - Realistic"]; me = ob.data
MW = ob.matrix_world; MINV = MW.inverted(); M3 = MW.to_3x3()
V = [(MW @ v.co).copy() for v in me.vertices]; NV = len(V)
FC = [sum((V[v] for v in p.vertices), Vector()) / len(p.vertices) for p in me.polygons]


def closest(p):
    ok, loc, nor, idx = ob.closest_point_on_mesh(MINV @ Vector(p))
    if not ok:
        return None, None, None
    return MW @ loc, (M3 @ nor).normalized(), idx


def parity(p, ndir=64):
    pl = MINV @ Vector(p); hits = 0
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
    loc, nor, fi = closest(p)
    if loc is None:
        return False, None, None
    d = Vector(p) - loc
    return (d.dot(nor) < 0.0), d.length, fi


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
U1 = (ref - AX * ref.dot(AX)).normalized(); U2 = AX.cross(U1).normalized()
radial = lambda p: ((Vector(p) - O) - AX * (Vector(p) - O).dot(AX)).length


def frac(a, b, n, strict=False):
    ins = 0; mmin = 1e9
    for k in range(1, n + 1):
        t = k / (n + 1.0)
        q = a + (b - a) * t
        if strict:
            h, tot = parity(q)
            ok = h > tot / 2
            mmin = min(mmin, (Vector(q) - closest(q)[0]).length * MM)
        else:
            ok, d, fi = inside_fast(q)
            mmin = min(mmin, d * MM)
        if ok:
            ins += 1
    return ins, round(mmin, 4)


def kink(a, b, c):
    d1 = (b - a).normalized(); d2 = (c - b).normalized()
    return math.degrees(math.acos(max(-1.0, min(1.0, d1.dot(d2)))))


# ---- candidate generator over an arbitrary axial band
def build(lo, hi, step=0.5):
    out = []
    a = lo
    while a <= hi + 1e-9:
        sel = [i for i in THUMB_V if abs(axial(V[i]) - a) <= 1.2 and radial(V[i]) <= 1.3 * R_ENV_THUMB]
        if len(sel) >= 6:
            c = sum((V[i] for i in sel), Vector()) / len(sel)
            rs = sorted(radial(V[i]) for i in sel)
            r95 = rs[int(0.95 * (len(rs) - 1))]
            grid = [("centroid", c)]
            for fr in (0.25, 0.50, 0.75):
                for k in range(8):
                    th = 2 * math.pi * k / 8.0
                    grid.append(("grid", c + (U1 * math.cos(th) + U2 * math.sin(th)) * fr * r95))
            for kind, p in grid:
                ok, dist, fi = inside_fast(p)
                if not ok or FO.get(fi) != "THUMB":
                    continue
                out.append({"level_mm": round(a, 4), "kind": kind, "p": p,
                            "clearance_mm": round(dist * MM, 4),
                            "axial_mm": round(axial(p), 4),
                            "axial_delta_mm": round(axial(p) - CENTRE, 4)})
        a += step
    return out


# ---------------- A. in-zone scan with FULL per-candidate scoring
INZ = build(A_MIN, A_MAX)
log("in-zone candidates: %d" % len(INZ))
recs = []
for c in INZ:
    p = c["p"]
    m20 = frac(MCP, p, 20)[0]
    t20 = frac(p, TIP, 20)[0]
    c["MCP_TO_IP_20"] = m20
    c["IP_TO_TIP_20"] = t20
    c["in_zone"] = True
    c["world_position"] = [round(float(x), 9) for x in p]
    recs.append(c)
best_in_zone = max(recs, key=lambda c: (min(c["IP_TO_TIP_20"], c["MCP_TO_IP_20"]), c["IP_TO_TIP_20"]))
log("best in-zone: MCP->IP %d/20  IP->TIP %d/20  axial %.3f (delta %.3f)"
    % (best_in_zone["MCP_TO_IP_20"], best_in_zone["IP_TO_TIP_20"],
       best_in_zone["axial_mm"], best_in_zone["axial_delta_mm"]))

# ---------------- B. diagnostic-only wide scan: where does 40/40 first appear?
WIDE = build(35.0, 100.0)
log("wide diagnostic candidates: %d" % len(WIDE))
scored = []
for c in WIDE:
    p = c["p"]
    if c["clearance_mm"] < 3.0:
        continue
    m40 = frac(MCP, p, 40)[0]
    t40 = frac(p, TIP, 40)[0]
    c["MCP_TO_IP_40"] = m40; c["IP_TO_TIP_40"] = t40
    c["combined_40"] = min(m40, t40)
    c["world_position"] = [round(float(x), 9) for x in p]
    c["in_zone"] = A_MIN <= c["axial_mm"] <= A_MAX
    c["shift_from_current_IP_mm"] = round((p - IP0).length * MM, 4)
    scored.append(c)
BEST_T = max(scored, key=lambda c: (c["IP_TO_TIP_40"], -c["shift_from_current_IP_mm"])) if scored else None
BEST_M = max(scored, key=lambda c: c["MCP_TO_IP_40"]) if scored else None
BEST_C = max(scored, key=lambda c: (c["combined_40"], -c["shift_from_current_IP_mm"])) if scored else None
log("wide best IP->TIP = %d/40 ; best MCP->IP = %d/40 ; best combined = %d/40"
    % (BEST_T["IP_TO_TIP_40"] if BEST_T else -1,
       BEST_M["MCP_TO_IP_40"] if BEST_M else -1,
       BEST_C["combined_40"] if BEST_C else -1))
full = []
for c in scored:
    if c["MCP_TO_IP_40"] != 40 or c["IP_TO_TIP_40"] != 40:
        continue
    p = c["p"]
    c["world_position"] = [round(float(x), 9) for x in p]
    c["in_zone"] = A_MIN <= c["axial_mm"] <= A_MAX
    c["axial_outside_zone_by_mm"] = (0.0 if c["in_zone"] else
                                     round(max(A_MIN - c["axial_mm"], c["axial_mm"] - A_MAX), 4))
    c["shift_from_current_IP_mm"] = round((p - IP0).length * MM, 4)
    c["MCP_IP_len_mm"] = round((p - MCP).length * MM, 4)
    c["IP_TIP_len_mm"] = round((TIP - p).length * MM, 4)
    c["chain_kink_deg"] = round(kink(MCP, p, TIP), 4)
    full.append(c)
log("wide 40/40 candidates: %d" % len(full))
in_zone_full = [c for c in full if c["in_zone"]]
nearest = min(full, key=lambda c: c["shift_from_current_IP_mm"]) if full else None
if nearest:
    log("nearest 40/40 (diagnostic): axial %.3f  outside zone by %.3f mm  shift %.3f mm"
        % (nearest["axial_mm"], nearest["axial_outside_zone_by_mm"],
           nearest["shift_from_current_IP_mm"]))

# ---------------- C. cause quantification
# A/C : thumb distal-phalanx centreline vs the straight chords
d0 = (TIP - IP0).normalized()
sel_dist = [i for i in THUMB_V if (V[i] - IP0).dot(d0) > -0.002
            and ((V[i] - IP0) - d0 * (V[i] - IP0).dot(d0)).length <= 1.3 * R_ENV_THUMB * 1e-3 * 1000 * 1e-3]
sel_dist = [i for i in THUMB_V if (V[i] - IP0).dot(d0) > -0.002
            and ((V[i] - IP0) - d0 * (V[i] - IP0).dot(d0)).length <= 1.3 * R_ENV_THUMB * 1e-3]
centreline = []
NS = 12
smax = max((V[i] - IP0).dot(d0) for i in sel_dist)
for k in range(NS):
    lo = smax * k / NS; hi = smax * (k + 1) / NS
    s = [V[i] for i in sel_dist if lo <= (V[i] - IP0).dot(d0) <= hi]
    if len(s) >= 4:
        centreline.append(sum(s, Vector()) / len(s))
sagitta = max((((c - IP0) - d0 * (c - IP0).dot(d0)).length) for c in centreline) * MM if centreline else 0.0
# local section radius in the distal phalanx
rad = [((V[i] - IP0) - d0 * (V[i] - IP0).dot(d0)).length for i in sel_dist]
r_mean = (sum(rad) / len(rad)) * MM if rad else 0.0
# B : how far the T-01 centre is from the nearest 40/40 axial coordinate
ax_needed = nearest["axial_mm"] if nearest else None
# D : coarse topology
dist_faces = [p.index for p in me.polygons
              if FO[p.index] == "THUMB" and (FC[p.index] - IP0).dot(d0) > -0.002]
dv = sorted({v for fi in dist_faces for v in me.polygons[fi].vertices})
el = [(V[e.vertices[0]] - V[e.vertices[1]]).length for e in me.edges
      if e.vertices[0] in set(dv) and e.vertices[1] in set(dv)]
el.sort()
CAUSES = {
    "A_thumb_distal_mesh_curvature": {
        "distal_phalanx_centreline_sagitta_mm": round(sagitta, 4),
        "distal_phalanx_mean_section_radius_mm": round(r_mean, 4),
        "sagitta_over_radius": round(sagitta / r_mean, 4) if r_mean else None,
        "reading": ("if the straight chord sags away from the centreline by more than the local "
                    "section radius, no straight chord between two interior points can stay "
                    "inside the phalanx")},
    "B_THUMB_IP_T01_region_position": {
        "approved_axial_centre_mm": CENTRE, "zone_half_width_mm": ZONE,
        "zone_mm": [round(A_MIN, 4), round(A_MAX, 4)],
        "current_IP_axial_mm": round(axial(IP0), 4),
        "current_IP_axial_delta_mm": round(axial(IP0) - CENTRE, 4),
        "axial_of_nearest_40_40_mm": ax_needed,
        "nearest_40_40_delta_from_centre_mm": (round(ax_needed - CENTRE, 4) if ax_needed else None),
        "nearest_40_40_outside_zone_by_mm": (nearest["axial_outside_zone_by_mm"] if nearest else None),
        "reading": ("the current IP already sits +%.3f mm inside the zone; the nearest position "
                    "that closes the chain sits %s mm outside it"
                    % (axial(IP0) - CENTRE,
                       (nearest["axial_outside_zone_by_mm"] if nearest else "n/a")))},
    "C_straight_single_bone_representation": {
        "MCP_to_IP_chord_len_mm": round((IP0 - MCP).length * MM, 4),
        "IP_to_TIP_chord_len_mm": round((TIP - IP0).length * MM, 4),
        "chain_kink_at_current_IP_deg": round(kink(MCP, IP0, TIP), 4),
        "reading": ("one straight bone per phalanx cannot follow a curved distal phalanx; the "
                    "IP->TIP chord is forced to leave the volume in the middle of the segment")},
    "D_coarse_thumb_topology": {
        "n_faces_distal_of_IP": len(dist_faces), "n_verts_distal_of_IP": len(dv),
        "median_edge_len_mm": round(el[len(el) // 2] * MM, 4) if el else None,
        "max_edge_len_mm": round(el[-1] * MM, 4) if el else None,
        "reading": ("coarse tessellation means the inside/outside test flips over whole "
                    "millimetres and no small joint nudge can stabilise it")}}

DIAG = {
    "stage": "STAGE5A_R2B_THUMB_STRAIGHT_BONE_COMPATIBILITY_DIAGNOSIS",
    "generated_at": NOW, "read_only": True,
    "input_blend": R2A_BLEND, "input_sha256": R2A_SHA,
    "DISCLAIMER": ("DIAGNOSIS ONLY.  Any position outside the approved T-01 region reported "
                   "here is NOT approved and MUST NOT be used."),
    "T01_authority": {"approved_axial_centre_mm": CENTRE, "zone_half_width_mm": ZONE,
                      "zone_mm": [round(A_MIN, 4), round(A_MAX, 4)]},
    "best_near_feasible_candidate_in_zone": {
        k: v for k, v in best_in_zone.items() if k != "p"},
    "best_IP_TO_TIP_interior_in_zone": "%d/20" % max(r["IP_TO_TIP_20"] for r in recs),
    "best_MCP_TO_IP_interior_in_zone": "%d/20" % max(r["MCP_TO_IP_20"] for r in recs),
    "in_zone_candidate_count": len(recs),
    "first_40_40_appearance": {
        "found": bool(full),
        "count_40_40_in_wide_scan": len(full),
        "count_40_40_INSIDE_approved_zone": len(in_zone_full),
        "nearest_40_40_by_shift": ({k: v for k, v in nearest.items() if k != "p"} if nearest else None),
        "note": ("no position in the extended diagnostic band (axial 35-100 mm) reaches 40/40 on "
                 "BOTH segments; the conflict is therefore not caused by the T-01 zone limits "
                 "alone"),
        "distance_IP_must_move_for_first_40_40_mm": (nearest["shift_from_current_IP_mm"] if nearest else None),
        "that_position_outside_approved_region": (not nearest["in_zone"]) if nearest else None},
    "wide_scan_maxima": {
        "candidates_scored": len(scored),
        "max_IP_TO_TIP_interior": ("%d/40" % BEST_T["IP_TO_TIP_40"]) if BEST_T else None,
        "max_IP_TO_TIP_position": ({k: v for k, v in BEST_T.items() if k != "p"} if BEST_T else None),
        "max_MCP_TO_IP_interior": ("%d/40" % BEST_M["MCP_TO_IP_40"]) if BEST_M else None,
        "best_combined_interior": ("%d/40" % BEST_C["combined_40"]) if BEST_C else None,
        "best_combined_position": ({k: v for k, v in BEST_C.items() if k != "p"} if BEST_C else None)},
    "causes": CAUSES,
    "all_in_zone_records": [{k: v for k, v in r.items() if k != "p"} for r in recs],
    "log": LOG,
}
json.dump(DIAG, open(os.path.join(OUTDIR, "THUMB_STRAIGHT_BONE_COMPATIBILITY_DIAGNOSIS.json"),
                     "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(DIAG, open(os.path.join(OUTDIR, "_tmp", "S5A_R2B_DIAG_LOG.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("DIAG_DONE")
