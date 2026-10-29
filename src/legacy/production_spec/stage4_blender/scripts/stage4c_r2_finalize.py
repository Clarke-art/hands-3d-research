# STAGE4C_R2_NAIL_SELECTOR_AND_ORIGIN_EVIDENCE_CORRECTION
#
# Narrow revision after the Stage-4C R1 Human Review.  Only three things change:
#   1. CON-4 nail face selector  -> the three-gate selector in stage4c_r2_selector.py
#   2. CON-6 origin               -> NO numeric change; an errata + formal evidence are added
#   3. the R1 NAIL_AUDIT / ORIGIN_AUDIT contradictions -> corrected in R2-side files only
#
# R1 is provenance: it is read, its hash is verified, and it is never written.
#
# usage: blender -b <stage4c_r1.blend> --python stage4c_r2_finalize.py -- <out.blend> <outdir> <frame.json>
import bpy, bmesh, sys, os, json, math, hashlib, datetime
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT_BLEND, OUTDIR, FRAME_JSON = argv[0], argv[1], argv[2]
os.makedirs(OUTDIR, exist_ok=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stage4c_r2_selector as SEL

TARGET = "Hand  - Realistic"
EXPECT = "66fa45325273f38f597f6af78bec603c471a697d6f1798b96eecc231e64bcdb6"
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s); print(s)


# =============================================================== 0. freeze R1
IN_BLEND = bpy.data.filepath
SHA_IN = hashlib.sha256(open(IN_BLEND, "rb").read()).hexdigest()
log("R1 INPUT = %s" % IN_BLEND)
log("  sha256   = %s" % SHA_IN)
log("  expected = %s" % EXPECT)
if SHA_IN != EXPECT:
    raise SystemExit("FAIL CLOSED: the Stage-4C R1 hash does not match -- refusing to run")
log("  MATCH -> R1 frozen as provenance (never written)")

ob = bpy.data.objects[TARGET]
me = ob.data
MW = ob.matrix_world
W = [(MW @ v.co).copy() for v in me.vertices]
NV = len(me.vertices)
FACES = [list(p.vertices) for p in me.polygons]
NF = len(FACES)
FN = [(MW.to_3x3() @ p.normal).normalized() for p in me.polygons]
FC = [sum((W[v] for v in f), Vector()) / len(f) for f in FACES]
UV_BEFORE = [tuple(l.uv) for l in me.uv_layers.active.data]
MAT_BEFORE = [p.material_index for p in me.polygons]

bm = bmesh.new(); bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()


def topo_sig(bmx):
    h = hashlib.sha256()
    h.update(b"V%d E%d F%d|" % (len(bmx.verts), len(bmx.edges), len(bmx.faces)))
    for e in bmx.edges:
        a, b = e.verts[0].index, e.verts[1].index
        h.update(b"%d-%d;" % (a, b) if a < b else b"%d-%d;" % (b, a))
    for f in bmx.faces:
        h.update(b"%d:" % len(f.verts))
        h.update(",".join(str(v.index) for v in f.verts).encode() + b";")
    return h.hexdigest()


TOPO_PRE = topo_sig(bm)
NE = len(bm.edges)
POS_PRE = [tuple(round(float(c), 10) for c in v.co) for v in me.vertices]
log("TOPOLOGY_SIGNATURE_PRE = %s" % TOPO_PRE)
log("  V=%d E=%d F=%d  (triangulated %d)" % (NV, NE, NF, sum(len(f) - 2 for f in FACES)))

# =============================================================== 1. R2 selector
FR = json.load(open(FRAME_JSON, encoding="utf-8"))
log("joint frame: %s" % FRAME_JSON)
log("  source provenance %s @ %s" % (FR["source_object"], FR["source_sha256"]))
fr = SEL.build_frame(FR["bones"])
res = SEL.select(FACES, FC, FN, fr, verbose=True)
sel = res["selection"]
rec = res["records"]
R1 = json.load(open(os.path.join(os.path.dirname(FRAME_JSON), "..", "stage4c", "NAIL_AUDIT.json"),
                    encoding="utf-8"))
R1_SETS = {k: sorted(v) for k, v in R1["per_digit_faces"].items()}

# ---- apply the material assignment ------------------------------------------------------
skin = bpy.data.materials.get("HAND_SKIN")
nail = bpy.data.materials.get("NAIL_BED")
if skin is None or nail is None:
    raise SystemExit("FAIL CLOSED: R1 materials missing")
if [m.name for m in me.materials][:2] != ["HAND_SKIN", "NAIL_BED"]:
    raise SystemExit("FAIL CLOSED: unexpected material slot order in R1: %s"
                     % [m.name for m in me.materials])
for p in me.polygons:
    p.material_index = 0
nail_faces = set()
for d in SEL.DIGITS:
    nail_faces |= sel[d]
for fi in nail_faces:
    me.polygons[fi].material_index = 1
log("CON-4 R2: NAIL_BED on %d faces (R1 had %d assigned; R1 instances %d over %d unique)"
    % (len(nail_faces), sum(1 for x in MAT_BEFORE if x == 1),
       sum(len(v) for v in R1_SETS.values()), len(set().union(*R1_SETS.values()))))

# ---- gates ------------------------------------------------------------------------------
pairs = []
for i in range(len(SEL.DIGITS)):
    for j in range(i + 1, len(SEL.DIGITS)):
        a, b = SEL.DIGITS[i], SEL.DIGITS[j]
        inter = sorted(sel[a] & sel[b])
        pairs.append({"pair": "%s x %s" % (a, b), "intersection_count": len(inter),
                      "faces": inter})
overlap_total = sum(p["intersection_count"] for p in pairs)
sel_all = sorted(nail_faces)
palmar = [fi for fi in sel_all if rec[fi]["radial"] <= 0]
web = [fi for fi in sel_all if rec[fi]["distal_comp_dist"] < SEL.COMP_MIN_M]
root = [fi for fi in sel_all if not (SEL.AX_LO <= rec[fi]["axial_frac"] <= SEL.AX_HI)]
far = [fi for fi in sel_all if rec[fi]["distal_dist"] > 0.012]
ownerv = [fi for fi in sel_all if not (rec[fi]["distal_dist"] < rec[fi]["distal_comp_dist"])]
comps = {d: ([len(c) for c in SEL.connected_components(sel[d], FACES)] if sel[d] else [])
         for d in SEL.DIGITS}
log("GATES: disjoint=%s overlap=%d | palmar=%d web=%d root=%d far>12mm=%d owner-violations=%d"
    % (overlap_total == 0, overlap_total, len(palmar), len(web), len(root), len(far), len(ownerv)))
log("components per digit: %s" % comps)

# =============================================================== 2. freeze verification
POS_POST = [tuple(round(float(c), 10) for c in v.co) for v in me.vertices]
UV_POST = [tuple(l.uv) for l in me.uv_layers.active.data]
pos_delta = max(max(abs(a[i] - b[i]) for i in range(3)) for a, b in zip(POS_PRE, POS_POST))
uv_delta = max(max(abs(a[i] - b[i]) for i in range(2)) for a, b in zip(UV_BEFORE, UV_POST))
obj_delta = (MW.translation - Vector([1.408704638, 0.022395039, 0.335847497])).length
TOPO_POST = topo_sig(bm)
log("VERTEX POSITION max delta = %.3e m (must be 0)" % pos_delta)
log("UV max delta              = %.3e (must be 0)" % uv_delta)
log("origin                    = %s (R1 value; |delta| = %.3e m)"
    % ([round(float(x), 9) for x in MW.translation], obj_delta))
log("TOPOLOGY_SIGNATURE_MATCH  = %s" % (TOPO_PRE == TOPO_POST))
arms = [o.name for o in bpy.data.objects if o.type == "ARMATURE"]
vgs = [g.name for g in ob.vertex_groups]
log("armatures present = %s | vertex groups = %s" % (arms, vgs))

fail = []
if pos_delta != 0.0:
    fail.append("vertex positions changed")
if uv_delta != 0.0:
    fail.append("UV changed")
if TOPO_PRE != TOPO_POST:
    fail.append("topology changed")
if obj_delta > 1e-9:
    fail.append("origin changed")
if arms:
    fail.append("armature present")
if vgs:
    fail.append("vertex groups present")
if (NV, len(bm.edges), NF) != (3416, 6828, 3414):
    fail.append("V/E/F not 3416/6828/3414")
if fail:
    raise SystemExit("FAIL CLOSED: %s" % fail)
log("FREEZE VERIFICATION = PASS")

bm.free()
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, copy=True, compress=False)
SHA_OUT = hashlib.sha256(open(OUT_BLEND, "rb").read()).hexdigest()
SHA_IN_AFTER = hashlib.sha256(open(IN_BLEND, "rb").read()).hexdigest()
log("SAVED %s (%d bytes, sha256 %s)" % (OUT_BLEND, os.path.getsize(OUT_BLEND), SHA_OUT))
log("R1 still unchanged: %s" % (SHA_IN == SHA_IN_AFTER))

payload = {
    "stage": "STAGE4C_R2_NAIL_SELECTOR_AND_ORIGIN_EVIDENCE_CORRECTION",
    "generated_at": datetime.datetime.now().astimezone().isoformat(),
    "r1_input": {"blend": IN_BLEND, "sha256_before": SHA_IN, "sha256_after": SHA_IN_AFTER,
                 "unchanged": SHA_IN == SHA_IN_AFTER, "expected": EXPECT},
    "output": {"blend": OUT_BLEND, "sha256": SHA_OUT, "bytes": os.path.getsize(OUT_BLEND)},
    "joint_frame": {"file": FRAME_JSON, "source": FR["source_blend"],
                    "source_sha256": FR["source_sha256"]},
    "selector_parameters": {"AX_LO": SEL.AX_LO, "AX_HI": SEL.AX_HI, "CONE_MIN": SEL.CONE_MIN,
                            "OWN_MARGIN": SEL.OWN_MARGIN,
                            "RADIAL_FRAC_MIN": SEL.RADIAL_FRAC_MIN,
                            "COMP_MIN_M": SEL.COMP_MIN_M, "SPECK_FRAC": SEL.SPECK_FRAC,
                            "ownership": "FULL bone chain (meta+prox+distal); the brief's "
                                         "literal distal-segment comparison is enforced too"},
    "envelopes_mm": {d: round(res["envelopes_m"][d] * 1000, 2) for d in SEL.DIGITS},
    "r1_vs_r2": {"r1_instances": sum(len(v) for v in R1_SETS.values()),
                 "r1_union": len(set().union(*R1_SETS.values())),
                 "r1_per_digit": {k: len(v) for k, v in R1_SETS.items()},
                 "r2_per_digit": {d: len(sel[d]) for d in SEL.DIGITS},
                 "r2_instances": sum(len(sel[d]) for d in SEL.DIGITS),
                 "r2_union": len(nail_faces),
                 "faces_in_r1_not_in_r2": sorted(set().union(*R1_SETS.values()) - nail_faces),
                 "faces_in_r2_not_in_r1": sorted(nail_faces - set().union(*R1_SETS.values())),
                 "faces_retained": sorted(nail_faces & set().union(*R1_SETS.values()))},
    "gates": {"NAIL_FACE_SET_DISJOINT": overlap_total == 0,
              "NAIL_FACE_OVERLAP_COUNT_TOTAL": overlap_total,
              "pairwise_intersections": pairs,
              "NAIL_FACE_OWNER_DISTANCE_TEST": len(ownerv) == 0,
              "NAIL_FACE_OWNER_DISTANCE_VIOLATIONS": ownerv,
              "NAIL_DISTAL_DOMAIN_TEST": len(root) == 0,
              "NAIL_DISTAL_DOMAIN_VIOLATIONS": root,
              "NAIL_PALMAR_LEAKAGE": len(palmar),
              "NAIL_WEBSPACE_LEAKAGE": len(web),
              "NAIL_FACES_FURTHER_THAN_12MM_FROM_ANY_DISTAL_BONE": len(far),
              "NAIL_CONNECTED_COMPONENTS_PER_DIGIT": comps},
    "per_digit_stats": SEL.stats(FACES, FC, rec, sel),
    "per_digit_faces": {d: sorted(sel[d]) for d in SEL.DIGITS},
    "speck_removal": res["speck"],
    "freeze_verification": {
        "vertex_position_max_delta_m": pos_delta, "uv_max_delta": uv_delta,
        "origin_delta_m": obj_delta, "TOPOLOGY_SIGNATURE_PRE": TOPO_PRE,
        "TOPOLOGY_SIGNATURE_POST": TOPO_POST, "TOPOLOGY_SIGNATURE_MATCH": TOPO_PRE == TOPO_POST,
        "V": NV, "E": NE, "F": NF,
        "TOTAL_RIGHT_HAND_TRIS": sum(len(f) - 2 for f in FACES),
        "armatures": arms, "vertex_groups": vgs},
    "materials": [{"slot": i, "name": m.name,
                   "faces": sum(1 for p in me.polygons if p.material_index == i),
                   "diffuse_color": [round(float(c), 4) for c in m.diffuse_color]}
                  for i, m in enumerate(me.materials)],
    "log": LOG,
}
json.dump(payload, open(os.path.join(OUTDIR, "STAGE4C_R2_RUN.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
log("WROTE STAGE4C_R2_RUN.json")
log("DONE")
