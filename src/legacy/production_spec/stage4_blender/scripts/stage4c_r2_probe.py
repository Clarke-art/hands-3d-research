# STAGE4C_R2 -- probe / acceptance harness for the nail selector.  READ-ONLY.
#
# usage: blender -b <stage4c_r1.blend> --python stage4c_r2_probe.py -- <frame.json> <out.json>
import bpy, sys, os, json, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
FRAME_JSON, OUT = argv[0], argv[1]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stage4c_r2_selector as SEL

# optional parameter sweep: argv[2] = JSON {CONE_MIN:..., RADIAL_FRAC_MIN:..., ...}
if len(argv) > 2 and os.path.exists(argv[2]):
    for k, v in json.load(open(argv[2], encoding="utf-8")).items():
        setattr(SEL, k, v)
    print("PARAMS FROM", argv[2])

FR = json.load(open(FRAME_JSON, encoding="utf-8"))["bones"]
ob = bpy.data.objects["Hand  - Realistic"]
MW = ob.matrix_world
W = [(MW @ v.co).copy() for v in ob.data.vertices]
FACES = [list(p.vertices) for p in ob.data.polygons]
FN = [(MW.to_3x3() @ p.normal).normalized() for p in ob.data.polygons]
FC = [sum((W[v] for v in f), Vector()) / len(f) for f in FACES]

fr = SEL.build_frame(FR)
res = SEL.select(FACES, FC, FN, fr, verbose=True)
sel = res["selection"]
rec = res["records"]

# ---- disjointness: all 10 pairs ----------------------------------------------------------
pairs = []
for i in range(len(SEL.DIGITS)):
    for j in range(i + 1, len(SEL.DIGITS)):
        a, b = SEL.DIGITS[i], SEL.DIGITS[j]
        inter = sorted(sel[a] & sel[b])
        pairs.append({"pair": "%s x %s" % (a, b), "intersection_count": len(inter),
                      "faces": inter[:20]})
overlap_total = sum(p["intersection_count"] for p in pairs)

# ---- leakage ----------------------------------------------------------------------------
sel_all = sorted(set().union(*sel.values()))
palmar = [fi for fi in sel_all if rec[fi]["radial"] <= 0]
web = [fi for fi in sel_all if rec[fi]["distal_comp_dist"] < SEL.COMP_MIN_M]
far = [fi for fi in sel_all if rec[fi]["distal_dist"] > 0.012]
wrong_owner = [fi for fi in sel_all
               if not (rec[fi]["distal_dist"] < rec[fi]["distal_comp_dist"])]

comps = {d: [len(c) for c in SEL.connected_components(sel[d], FACES)] if sel[d] else []
         for d in SEL.DIGITS}

out = {
    "stage": "STAGE4C_R2_NAIL_SELECTOR_PROBE",
    "mode": "READ-ONLY",
    "parameters": {"AX_LO": SEL.AX_LO, "AX_HI": SEL.AX_HI, "CONE_MIN": SEL.CONE_MIN,
                   "OWN_MARGIN": SEL.OWN_MARGIN, "RADIAL_FRAC_MIN": SEL.RADIAL_FRAC_MIN,
                   "COMP_MIN_M": SEL.COMP_MIN_M, "SPECK_FRAC": SEL.SPECK_FRAC},
    "envelopes_mm": {d: round(res["envelopes_m"][d] * 1000, 2) for d in SEL.DIGITS},
    "per_digit_faces": {d: len(sel[d]) for d in SEL.DIGITS},
    "total_instances": sum(len(sel[d]) for d in SEL.DIGITS),
    "union": len(sel_all),
    "disjoint": overlap_total == 0,
    "NAIL_FACE_OVERLAP_COUNT_TOTAL": overlap_total,
    "pairwise_intersections": pairs,
    "NAIL_PALMAR_LEAKAGE": len(palmar),
    "NAIL_WEBSPACE_LEAKAGE": len(web),
    "faces_further_than_12mm_from_any_distal_bone": len(far),
    "NAIL_FACE_OWNER_DISTANCE_TEST_violations": len(wrong_owner),
    "NAIL_CONNECTED_COMPONENTS_PER_DIGIT": comps,
    "speck": res["speck"],
    "per_digit_stats": SEL.stats(FACES, FC, rec, sel),
}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", OUT)
print("per-digit faces:", out["per_digit_faces"], "| instances", out["total_instances"],
      "| union", out["union"])
print("disjoint:", out["disjoint"], "| overlap total:", out["NAIL_FACE_OVERLAP_COUNT_TOTAL"])
print("palmar leakage:", out["NAIL_PALMAR_LEAKAGE"], "| web leakage:", out["NAIL_WEBSPACE_LEAKAGE"])
print("faces >12mm from any distal bone:", out["faces_further_than_12mm_from_any_distal_bone"])
print("owner-distance violations:", out["NAIL_FACE_OWNER_DISTANCE_TEST_violations"])
print("components per digit:", comps)
