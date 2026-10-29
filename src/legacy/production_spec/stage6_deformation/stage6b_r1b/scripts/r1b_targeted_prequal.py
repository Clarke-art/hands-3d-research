# =====================================================================================
# STAGE6B_R1B -- §21 targeted prequalification (fast screen, read-only)
# =====================================================================================
# usage:  blender -b -P r1b_targeted_prequal.py -- <label> <master.blend> <outdir>
#   label = R1B_BASELINE | R1C_CANDIDATE
#
# Runs TH_MCP_45 / TH_IP_45 / INDEX_MCP_45 (Stage6A isolated flex convention) and the
# STAGE6B opposition CMC_OPP_10 pose, and measures
#   * HISTORIC_CLASS_B 61-edge stretch  (posed/bind, tear = ratio>3 AND posed>5 mm)
#   * the R2 THUMB|INDEX boundary edge stretch (secondary)
#   * the Stage6A region strain of the thumb MCP / thumb IP / index MCP patches
# =====================================================================================
import os
import sys
import json
import math
import datetime
import bpy
from mathutils import Vector, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s6br1b_common as K                                          # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
LABEL, MASTER, OUTDIR = argv[0], argv[1], argv[2]
NOW = datetime.datetime.now().astimezone().isoformat()
LOG = []


def log(s):
    LOG.append(s)
    print("[PQUAL:%s] %s" % (LABEL, s), flush=True)


ctx = K.B.build_context()
ref = ctx["ref"]
NV = ref["NV"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
own = ctx["own_r1a"]
ARC = ctx["ARC"]
MED = ctx["MED"]
s_MCP, s_IP = ctx["s_MCP"], ctx["s_IP"]

probe = K.load_probe_sets()
HIST = [(k, a, b) for k, a, b in probe["CLASS_B"]]
CASEA = [(k, a, b) for k, a, b in probe["CLASS_A"]]

CM = json.load(open(K.PROVENANCE["stage6b_case_matrix"], encoding="utf-8"))
CASES = dict((c["case_id"], c) for c in CM["cases"])

bpy.ops.wm.open_mainfile(filepath=MASTER)
ob = bpy.data.objects[K.MESH_OBJ]
rig = bpy.data.objects[K.RIG_OBJ]
MW = ob.matrix_world.copy()

PTS = dict((d, K.RC.chp(ref["jf"], d)) for d in K.DIGITS5)
ARC_ALL = {}
for d in K.DIGITS5:
    ARC_ALL[d] = ARC if d == "THUMB" else [K.RC.arc_of(PTS[d], V0[i])[0] for i in range(NV)]
TAU = 2.0 * MED
KAPPA = {"THUMB_MCP": TAU, "THUMB_IP": TAU, "INDEX_MCP": TAU}
PATCH_IDS = {}
for d, seg in (("THUMB", "MCP"), ("THUMB", "IP"), ("INDEX", "MCP")):
    own_d = [i for i in range(NV) if own[i] == d]
    key = "%s_%s" % (d, seg)
    joint = K.RC.chain_arc_table(ref["jf"], d)[K.RC.CHAIN[d].index(seg)]
    PATCH_IDS[key] = sorted(i for i in own_d if abs(ARC_ALL[d][i] - joint) <= KAPPA[key])
FACE_AREA0 = [K.B.face_area(V0, p) for p in ref["TOPO0"]]
EDGE_LEN0 = [(V0[a] - V0[b]).length for a, b in EDGES]
POLY = ref["TOPO0"]


def reset():
    K.B.reset_pose(rig)


def evaluate():
    K.B.update()
    return K.B.evaluate(ob, MW)[0]


def patch_faces(ids):
    s = set(ids)
    return [fi for fi, p in enumerate(POLY) if any(v in s for v in p)]


def patch_edges(ids):
    s = set(ids)
    return [k for k, (a, b) in enumerate(EDGES) if a in s or b in s]


PF = dict((k, patch_faces(v)) for k, v in PATCH_IDS.items())
PE = dict((k, patch_edges(v)) for k, v in PATCH_IDS.items())

POSES = [("TH_MCP_45", "THUMB_MCP_R", -45.0), ("TH_IP_45", "THUMB_IP_R", -45.0),
         ("INDEX_MCP_45", "INDEX_MCP_R", -45.0)]
RES = {}
for nm, bone, ang in POSES:
    reset()
    K.B.set_local_axis_rotation(rig, bone, ang)
    V = evaluate()
    rows = []
    for k, a, b in HIST:
        l0 = EDGE_LEN0[k]
        l1 = (V[a] - V[b]).length
        rows.append((l1 / max(l0, 1e-18), k, a, b, l0 * K.MM, l1 * K.MM))
    rows.sort(reverse=True)
    torn = [r for r in rows if r[0] > 3.0 and r[5] > 5.0]
    RES[nm] = {
        "historic_class_b_edge_count": len(HIST),
        "max_stretch_ratio": K.rr(rows[0][0], 6),
        "max_posed_length_mm": K.rr(rows[0][5], 6),
        "edges_over_3x": sum(1 for r in rows if r[0] > 3.0),
        "edges_over_3x_and_over_5mm": len(torn),
        "worst": [{"edge_id": r[1], "endpoints": [r[2], r[3]], "ratio": K.rr(r[0], 6),
                   "bind_mm": K.rr(r[4], 6), "posed_mm": K.rr(r[5], 6)} for r in rows[:5]],
        "patch_strain": {},
    }
    for key, ids in PATCH_IDS.items():
        fi = PF[key]
        pe = PE[key]
        far = [K.B.face_area(V, POLY[i]) / FACE_AREA0[i] for i in fi if FACE_AREA0[i] > 1e-18]
        fer = [((V[a] - V[b]).length / EDGE_LEN0[k]) for k in pe if EDGE_LEN0[k] > 1e-18]
        RES[nm]["patch_strain"][key] = {
            "min_face_area_ratio": K.rr(min(far), 6) if far else None,
            "min_edge_ratio": K.rr(min(fer), 6) if fer else None,
            "max_edge_ratio": K.rr(max(fer), 6) if fer else None}
    log("%-14s historic61 max=%.3fx torn(>3x,>5mm)=%d/%d ; TH_MCP minER=%.4f TH_IP minER=%.4f IDX_MCP minER=%.4f"
        % (nm, RES[nm]["max_stretch_ratio"], len(torn), len(HIST),
           RES[nm]["patch_strain"]["THUMB_MCP"]["min_edge_ratio"],
           RES[nm]["patch_strain"]["THUMB_IP"]["min_edge_ratio"],
           RES[nm]["patch_strain"]["INDEX_MCP"]["min_edge_ratio"]))

# ---- CMC_OPP_10 (the frozen opposition path, reused verbatim)
c = CASES["CMC_OPP_10"]
q = c["cmc_quaternion_local"]
reset()
pb = rig.pose.bones["THUMB_CMC_R"]
pb.rotation_mode = 'QUATERNION'
pb.rotation_quaternion = Quaternion((q[0], q[1], q[2], q[3]))
V = evaluate()
rows = []
for k, a, b in HIST:
    l0 = EDGE_LEN0[k]
    l1 = (V[a] - V[b]).length
    rows.append((l1 / max(l0, 1e-18), k, a, b, l0 * K.MM, l1 * K.MM))
rows.sort(reverse=True)
torn = [r for r in rows if r[0] > 3.0 and r[5] > 5.0]
RES["CMC_OPP_10"] = {
    "historic_class_b_edge_count": len(HIST),
    "max_stretch_ratio": K.rr(rows[0][0], 6),
    "max_posed_length_mm": K.rr(rows[0][5], 6),
    "edges_over_3x": sum(1 for r in rows if r[0] > 3.0),
    "edges_over_3x_and_over_5mm": len(torn),
    "worst": [{"edge_id": r[1], "endpoints": [r[2], r[3]], "ratio": K.rr(r[0], 6),
               "bind_mm": K.rr(r[4], 6), "posed_mm": K.rr(r[5], 6)} for r in rows[:5]],
    "patch_strain": {},
}
log("CMC_OPP_10     historic61 max=%.3fx torn(>3x,>5mm)=%d/%d"
    % (RES["CMC_OPP_10"]["max_stretch_ratio"], len(torn), len(HIST)))

reset()
K.B.update()
Vz = evaluate()
zero = max((Vz[i] - V0[i]).length for i in range(NV)) * K.MM

HARD = ["TH_MCP_45", "TH_IP_45", "CMC_OPP_10"]
out = {
    "stage": "STAGE6B_R1B_TARGETED_PREQUALIFICATION",
    "label": LABEL,
    "generated_at": NOW,
    "master": {"path": MASTER.replace("\\", "/"), "sha256": K.sha256(MASTER)},
    "poses": RES,
    "zero_restore_max_delta_mm": K.rr(zero, 9),
    "hard_gate_poses": HARD,
    "hard_gate_edges_over_3x_and_over_5mm": dict(
        (p, RES[p]["edges_over_3x_and_over_5mm"]) for p in HARD),
    "HISTORIC_CLASS_B_TEAR_GATE": ("PASS" if all(RES[p]["edges_over_3x_and_over_5mm"] == 0
                                                 for p in HARD) else "FAIL"),
    "log": LOG,
}
os.makedirs(OUTDIR, exist_ok=True)
json.dump(out, open(os.path.join(OUTDIR, "PQUAL_%s.json" % LABEL), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("PQUAL_DONE_%s" % LABEL)
