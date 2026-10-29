# STAGE4C_R2 -- READ-ONLY diagnosis of the R1 nail-selector defect.
#
# R1 selected nail faces with: (a) face normal inside a cone around the digit's own nail
# normal, (b) axial position inside [0.15, 0.82] of the distal bone, (c) outside 45% of the
# per-digit radial spread.  There was NO digit-ownership gate.  This script measures exactly
# what that omission bought, before any code is changed.
#
# usage: blender -b <stage4c_r1.blend> --python stage4c_r2_diag.py -- <frame.json> <out.json>
import bpy, bmesh, sys, os, json, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
FRAME_JSON, OUT = argv[0], argv[1]
FR = json.load(open(FRAME_JSON, encoding="utf-8"))["bones"]
R1 = json.load(open(os.path.join(os.path.dirname(FRAME_JSON), "..", "stage4c", "NAIL_AUDIT.json"),
                    encoding="utf-8"))
R1_SETS = {k: set(v) for k, v in R1["per_digit_faces"].items()}

ob = bpy.data.objects["Hand  - Realistic"]
MW = ob.matrix_world
W = [(MW @ v.co).copy() for v in ob.data.vertices]
N = len(ob.data.polygons)
FACES = [list(p.vertices) for p in ob.data.polygons]
FN = [(MW.to_3x3() @ p.normal).normalized() for p in ob.data.polygons]
FC = [sum((W[v] for v in f), Vector()) / len(f) for f in FACES]

DIG = ["thumb", "index", "middle", "ring", "little"]
DISTAL = {"thumb": "THUMB_IP_R", "index": "INDEX_DIP_R", "middle": "MIDDLE_DIP_R",
          "ring": "RING_DIP_R", "little": "LITTLE_DIP_R"}
PROX = {"thumb": "THUMB_MCP_R", "index": "INDEX_PIP_R", "middle": "MIDDLE_PIP_R",
        "ring": "RING_PIP_R", "little": "LITTLE_PIP_R"}
META = {"thumb": "THUMB_CMC_R", "index": "INDEX_MCP_R", "middle": "MIDDLE_MCP_R",
        "ring": "RING_MCP_R", "little": "LITTLE_MCP_R"}


def seg(h, t):
    return Vector(h), Vector(t)


SEG = {}
for d in DIG:
    SEG[d] = seg(FR[DISTAL[d]]["head"], FR[DISTAL[d]]["tail"])
    SEG[d + "_PROX"] = seg(FR[PROX[d]]["head"], FR[PROX[d]]["tail"])
    SEG[d + "_META"] = seg(FR[META[d]]["head"], FR[META[d]]["tail"])

mcp = sum((Vector(FR["%s_MCP_R" % n.upper()]["head"]) for n in ("index", "middle", "ring", "little")),
          Vector()) / 4
wrist = Vector(FR["WRIST_R"]["head"])
tips = {n: Vector(FR["%s_TIP_R" % n.upper()]["head"]) for n in ("index", "middle", "ring", "little")}
FW = (sum(tips.values(), Vector()) / 4 - wrist).normalized()
RAD = (tips["index"] - tips["little"]).normalized()
RAD = (RAD - FW * RAD.dot(FW)).normalized()
DORSAL = FW.cross(RAD).normalized()


def seg_dist(p, s):
    a, b = s
    ab = b - a
    L2 = ab.length_squared
    if L2 < 1e-18:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / L2))
    return (p - (a + ab * t)).length


def nail_normal(d):
    h, t = SEG[d]
    dirv = (t - h).normalized()
    mu = (Vector(FR[META[d]]["tail"]) - Vector(FR[META[d]]["head"])).normalized()
    lat = DORSAL.cross(mu)
    lat = lat.normalized() if lat.length > 1e-9 else RAD.copy()
    nn = lat.cross(dirv)
    nn = nn.normalized() if nn.length > 1e-9 else DORSAL.copy()
    return nn if nn.dot(DORSAL) >= 0 else -nn


NN = {d: nail_normal(d) for d in DIG}

# ---- angles between the digits' nail normals (why one cone catches another digit) --------
pair_ang = {}
for i in range(len(DIG)):
    for j in range(i + 1, len(DIG)):
        a, b = DIG[i], DIG[j]
        pair_ang["%s_vs_%s" % (a, b)] = round(math.degrees(
            math.acos(max(-1, min(1, NN[a].dot(NN[b]))))), 2)

# ---- per-face ownership and R1 selector quantities --------------------------------------
rec = []
for fi in range(N):
    c = FC[fi]
    dd = {d: seg_dist(c, SEG[d]) for d in DIG}
    owner = min(dd, key=dd.get)
    d1 = sorted(dd.values())
    row = {"fi": fi, "owner": owner, "own_dist": dd[owner],
           "comp_dist": d1[1], "comp_digit": sorted(dd, key=dd.get)[1],
           "prox_dist": min(seg_dist(c, SEG[d + "_PROX"]) for d in DIG)}
    ax = {}
    for d in DIG:
        h, t = SEG[d]
        dirv = (t - h).normalized()
        L = (t - h).length
        a = (c - h).dot(dirv)
        perp = (c - (h + dirv * a)).dot(NN[d])
        ax[d] = {"frac": a / L, "perp": perp, "cone": FN[fi].dot(NN[d])}
    row["ax"] = ax
    rec.append(row)

CONE = 0.45
AXLO, AXHI = 0.15, 0.82
SHELL = 0.45

# reconstruct R1's *claim* per digit (which digits would claim each face) and compare with R1's
# recorded sets
claim = {d: set() for d in DIG}
for fi in range(N):
    for d in DIG:
        q = rec[fi]["ax"][d]
        if AXLO <= q["frac"] <= AXHI and q["perp"] > 0 and q["cone"] >= CONE:
            claim[d].add(fi)
for d in DIG:
    pmax = max((rec[fi]["ax"][d]["perp"] for fi in claim[d]), default=0.0)
    claim[d] = {fi for fi in claim[d] if rec[fi]["ax"][d]["perp"] >= SHELL * pmax}

report = {
    "stage": "STAGE4C_R2_NAIL_SELECTOR_ROOT_CAUSE_DIAGNOSIS",
    "mode": "READ-ONLY",
    "r1_counts": {d: len(R1_SETS[d]) for d in DIG},
    "r1_total_instances": sum(len(R1_SETS[d]) for d in DIG),
    "r1_union": len(set().union(*R1_SETS.values())),
    "r1_duplicate_instances": sum(len(R1_SETS[d]) for d in DIG) - len(set().union(*R1_SETS.values())),
    "reconstructed_claim_counts": {d: len(claim[d]) for d in DIG},
    "reconstruction_matches_r1": {d: claim[d] == R1_SETS[d] for d in DIG},
    "nail_normal_pair_angles_deg": pair_ang,
    "root_cause": [],
}

# how many faces pass MORE THAN ONE digit's cone test
multi = {}
for fi in range(N):
    hits = [d for d in DIG if rec[fi]["ax"][d]["cone"] >= CONE]
    if len(hits) > 1:
        multi[fi] = hits
report["faces_inside_more_than_one_cone"] = len(multi)
report["faces_inside_more_than_one_cone_examples"] = [
    {"face": fi, "digits": multi[fi],
     "owning": rec[fi]["owner"],
     "own_dist_mm": round(rec[fi]["own_dist"] * 1000, 2),
     "comp_dist_mm": round(rec[fi]["comp_dist"] * 1000, 2)}
    for fi in sorted(multi)[:12]]

# R1 union: how far are they from the nearest distal segment?  (the "finger-root band")
union = sorted(set().union(*R1_SETS.values()))
dists = sorted(rec[fi]["own_dist"] for fi in union)
report["r1_union_distance_to_nearest_distal_bone_mm"] = {
    "min": round(dists[0] * 1000, 2), "median": round(dists[len(dists) // 2] * 1000, 2),
    "p90": round(dists[int(0.9 * (len(dists) - 1))] * 1000, 2),
    "max": round(dists[-1] * 1000, 2)}
report["r1_union_far_from_any_distal_bone"] = {
    "threshold_mm": 12.0,
    "count": sum(1 for fi in union if rec[fi]["own_dist"] > 0.012),
    "faces": [fi for fi in union if rec[fi]["own_dist"] > 0.012]}
report["r1_union_owned_by_a_different_digit"] = {
    "count": sum(1 for fi in union
                 if not any(fi in R1_SETS[d] and rec[fi]["owner"] == d for d in DIG)),
    "detail": [{"face": fi, "owner": rec[fi]["owner"],
                "claimed_by": [d for d in DIG if fi in R1_SETS[d]],
                "own_dist_mm": round(rec[fi]["own_dist"] * 1000, 2),
                "comp_dist_mm": round(rec[fi]["comp_dist"] * 1000, 2)}
               for fi in union
               if not any(fi in R1_SETS[d] and rec[fi]["owner"] == d for d in DIG)][:20]}

json.dump(report, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", OUT)
print("R1 counts:", report["r1_counts"], "| instances", report["r1_total_instances"],
      "| union", report["r1_union"], "| duplicates", report["r1_duplicate_instances"])
print("reconstruction matches R1:", report["reconstruction_matches_r1"])
print("nail-normal pair angles:", pair_ang)
print("faces inside more than one cone:", report["faces_inside_more_than_one_cone"])
print("R1 union dist to nearest distal bone (mm):",
      report["r1_union_distance_to_nearest_distal_bone_mm"])
print("R1 union faces >12 mm from any distal bone:",
      report["r1_union_far_from_any_distal_bone"]["count"])
print("R1 union faces owned by a different digit:",
      report["r1_union_owned_by_a_different_digit"]["count"])
