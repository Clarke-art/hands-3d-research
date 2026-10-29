# STAGE6A -- diagnostic: classify new self-intersections and locate the TH_MCP index-shaft motion
import bpy, sys, os, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import s6a_common as S

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
STAGE6D = os.path.dirname(OUTDIR); PROD = os.path.dirname(STAGE6D)
S5 = os.path.join(PROD, "stage5_production_rig")
HARNESS = os.path.join(OUTDIR, "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend")
log, _ = S.log_factory("S6A-DIAG")

C, ref = S.load_reference(S5)
V0 = ref["V0"]; NV = ref["NV"]; jf = ref["jf"]; MED = ref["med_edge"]
TF = C.thumb_frame(ref); ARC_T = TF["arc_thumb_mm"]
RG = C.build_regions(ref, TF, MED, *C.thumb_radii(ref, TF))
OWN = RG["own_r1a"]; CAP = RG["cap_vertices"]
WEB = RG["FIRST_WEB"]; WEB_IDX = RG["WEB_INDEX_SIDE"]
FO = ref["FO"]
h = S.open_harness(HARNESS)
ob, rig = h["ob"], h["rig"]; MW = h["MW"]; POLY = h["POLY"]

PTS = {d: C.chp(jf, d) for d in S.DIGITS}
XIJ = {d: C.chain_arc_table(jf, d) for d in S.DIGITS}
ARC = {d: (ARC_T if d == "THUMB" else [C.arc_of(PTS[d], V0[i])[0] for i in range(NV)])
       for d in S.DIGITS}


def ipairs(V, P):
    tree = BVHTree.FromPolygons([tuple(v) for v in V], [tuple(p) for p in P],
                                all_triangles=False, epsilon=0.0)
    out = set()
    for a, b in tree.overlap(tree):
        if a >= b or (set(P[a]) & set(P[b])):
            continue
        out.add((a, b))
    return out


S.reset_pose(rig); bpy.context.view_layer.update()
Vb, Pb = S.evaluate(ob, MW)
BASE = ipairs(Vb, Pb)
log("baseline pairs %d" % len(BASE))

SIGN = {("INDEX", "MCP"): -1.0, ("INDEX", "PIP"): -1.0, ("INDEX", "DIP"): -1.0,
        ("THUMB", "MCP"): -1.0, ("THUMB", "IP"): -1.0,
        ("MIDDLE", "MCP"): -1.0, ("MIDDLE", "PIP"): -1.0, ("MIDDLE", "DIP"): -1.0,
        ("RING", "MCP"): -1.0, ("RING", "PIP"): -1.0, ("RING", "DIP"): -1.0,
        ("LITTLE", "MCP"): -1.0, ("LITTLE", "PIP"): -1.0, ("LITTLE", "DIP"): -1.0}

REPORT = {}
for (d, seg, ang) in [("THUMB", "MCP", 45.0), ("THUMB", "IMCP", 0.0), ("THUMB", "IP", 45.0),
                      ("INDEX", "MCP", 45.0), ("MIDDLE", "MCP", 45.0)]:
    if seg == "IMCP":
        continue
    S.reset_pose(rig)
    S.set_joint_rotation(rig, "%s_%s_R" % (d, seg), SIGN[(d, seg)] * ang)
    bpy.context.view_layer.update()
    V, P = S.evaluate(ob, MW)
    new = ipairs(V, P) - BASE
    cls = {}
    samples = []
    for a, b in sorted(new):
        oa, obb = OWN[POLY[a][0]], OWN[POLY[b][0]]
        fa, fb = FO.get(a, "?"), FO.get(b, "?")
        key = "-".join(sorted([str(fa), str(fb)]))
        cls[key] = cls.get(key, 0) + 1
        # is the pair inside the target digit's own surface (fold) or target<->neighbour (contact)?
        same_target = (fa == d and fb == d)
        if len(samples) < 6:
            ca = S.face_centroid(V, POLY[a]); cb = S.face_centroid(V, POLY[b])
            samples.append({"faces": [a, b], "face_owner": [fa, fb],
                            "both_in_target_digit": same_target,
                            "dist_mm": S.rr((ca - cb).length * S.MM, 4),
                            "centroid_mm": [S.rr(x * S.MM, 2) for x in ca]})
    REPORT["%s_%s_%d" % (d, seg, int(ang))] = {
        "new_pairs": len(new), "by_face_owner_pair": dict(sorted(cls.items(), key=lambda kv: -kv[1])),
        "intra_target_digit_pairs": sum(1 for a, b in new if FO.get(a) == d == FO.get(b)),
        "target_vs_other_pairs": sum(1 for a, b in new
                                     if (FO.get(a) == d) != (FO.get(b) == d)),
        "samples": samples}
    log("%s_%s_%d new=%d intra=%d vs_other=%d  %s"
        % (d, seg, int(ang), len(new),
           REPORT["%s_%s_%d" % (d, seg, int(ang))]["intra_target_digit_pairs"],
           REPORT["%s_%s_%d" % (d, seg, int(ang))]["target_vs_other_pairs"],
           dict(sorted(cls.items(), key=lambda kv: -kv[1])[:4])))

# ---- TH_MCP: which INDEX vertices move and where are they?
S.reset_pose(rig)
S.set_joint_rotation(rig, "THUMB_MCP_R", -45.0)
bpy.context.view_layer.update()
V, P = S.evaluate(ob, MW)
mv = []
for i in range(NV):
    if OWN[i] == "INDEX":
        dd = (V[i] - V0[i]).length * S.MM
        if dd > 1e-4:
            mv.append((i, dd, ARC["INDEX"][i], i in WEB_IDX))
mv.sort(key=lambda t: -t[1])
SHAFT_LO = XIJ["INDEX"][1] + 4.02
SHAFT_HI = XIJ["INDEX"][2] - 4.60
in_shaft = [x for x in mv if SHAFT_LO <= x[2] <= SHAFT_HI]
REPORT["TH_MCP_45_index_motion"] = {
    "index_vertices_moving_gt_1e-4mm": len(mv),
    "index_arc_range_mm_of_movers": [S.rr(min(x[2] for x in mv), 3), S.rr(max(x[2] for x in mv), 3)],
    "index_shaft_band_arc_mm": [S.rr(SHAFT_LO, 3), S.rr(SHAFT_HI, 3)],
    "movers_inside_the_declared_shaft_band": len(in_shaft),
    "shaft_band_max_mm": S.rr(max([x[1] for x in in_shaft], default=0.0), 6),
    "movers_that_are_first_web_index_side": sum(1 for x in mv if x[3]),
    "top_movers": [{"vertex": x[0], "disp_mm": S.rr(x[1], 6), "index_arc_mm": S.rr(x[2], 3),
                    "in_first_web_index_side": x[3]} for x in mv[:12]]}
log("TH_MCP_45 : index movers=%d ; inside declared shaft band=%d (max %.6f mm) ; web-side=%d"
    % (len(mv), len(in_shaft), REPORT["TH_MCP_45_index_motion"]["shaft_band_max_mm"],
       sum(1 for x in mv if x[3])))

json.dump(REPORT, open(os.path.join(OUTDIR, "_tmp", "S6A_DIAG_CLASSIFY.json"), "w",
                       encoding="utf-8"), indent=1, ensure_ascii=False)
print("DIAG_DONE")
