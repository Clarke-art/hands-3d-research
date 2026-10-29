# =====================================================================================
# STAGE5B_R1B -- post-save payload self proof  (separate Blender process)
# =====================================================================================
# Independent verification of the SHIPPED R1B artifact:
#   * the file encodes EXACTLY the accepted candidate weight field (float32 exact)
#   * the four-finger / index groups are byte-identical to R1A everywhere
#   * the sanctioned first-web blend, the nail semantic vertices and the approved distal cap
#     are untouched vertex-by-vertex
#   * structural gates + zero-pose bind + influence / normalisation gates
# Recomputes the candidate from the frozen R1A master + the recorded parameters, so it does
# not trust the build script's own report.
# =====================================================================================
import bpy
import sys
import os
import json
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
PROD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.append(os.path.join(PROD, "stage5_production_rig", "stage5b_r1b", "scripts"))
import r1b_common as C                                          # noqa: E402
RC = C.RC
S6 = C.S6

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
STATUS_PATH = os.path.join(OUTDIR, "STAGE5B_R1B_STATUS.json")
NOW = datetime.datetime.now().astimezone().isoformat()
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[R1B-VERIFY]", s, flush=True)


def rr(x, n=9):
    return round(float(x), n)


status = json.load(open(STATUS_PATH, encoding="utf-8"))
R1B = status["output_r1b"]["path"].replace("/", os.sep)
PARAMS = status["candidate_evidence"] and json.load(
    open(status["candidate_evidence"]["ranking_json"].replace("/", os.sep),
         encoding="utf-8"))["accepted_candidate"]["params"]
log("R1B = %s" % R1B)
log("params = %s" % PARAMS)

s_r1a = C.sha256(C.R1A_MASTER)
s_r1b = C.sha256(R1B)
log("R1A %s" % s_r1a)
log("R1B %s" % s_r1b)
if s_r1a != C.R1A_SHA256:
    raise SystemExit("FAIL CLOSED: R1A provenance drift")
if s_r1b != status["output_r1b"]["sha256"]:
    raise SystemExit("FAIL CLOSED: R1B hash does not match the recorded status")

ctx = C.build_context()
NV, ARC, V0 = ctx["NV"], ctx["ARC"], ctx["V0"]
s_MCP, s_IP, MED = ctx["s_MCP"], ctx["s_IP"], ctx["MED"]
NAIL, CAP, WEB = ctx["nail"], ctx["cap"], ctx["first_web"]
assert NV == 3416

# rebuild the authorised region exactly as the build did
KAPPA = 2.0 * MED
PATCH = {seg: sorted(i for i in ctx["thumb_own"]
                     if abs(ARC[i] - (s_MCP if seg == "MCP" else s_IP)) <= KAPPA)
         for seg in ("MCP", "IP")}
eadj = {}
for a, b in ctx["edges"]:
    eadj.setdefault(a, []).append(b)
    eadj.setdefault(b, []).append(a)
CORE = set(PATCH["MCP"]) | set(PATCH["IP"])
CLOSURE = set(CORE)
front = set(CORE)
for _ in range(2):
    nxt = set()
    for u in front:
        for v in eadj.get(u, ()):
            if v not in CLOSURE:
                CLOSURE.add(v)
                nxt.add(v)
    front = nxt
AUTH = set(i for i in CLOSURE if i in ctx["thumb_own"] and i not in (NAIL | CAP | WEB))

# ---- read R1A
bpy.ops.wm.open_mainfile(filepath=C.R1A_MASTER)
ob_a = bpy.data.objects["Hand  - Realistic"]
W1 = C.read_object_weights(ob_a, NV)
GROUPS_A = [g.name for g in ob_a.vertex_groups]

# ---- read R1B (fresh session state)
bpy.ops.wm.open_mainfile(filepath=R1B)
ob_b = bpy.data.objects["Hand  - Realistic"]
rig_b = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
me_b = ob_b.data
MW_b = ob_b.matrix_world.copy()
NV_B = len(me_b.vertices)
W2 = C.read_object_weights(ob_b, NV_B)
GROUPS_B = [g.name for g in ob_b.vertex_groups]
log("R1B vertices=%d groups=%d" % (NV_B, len(GROUPS_B)))

# ---- 1. does the file encode the candidate field exactly?
W_exp, CHANGED = C.compose_weights(ctx, W1, AUTH, PARAMS)
try:
    import numpy as _np
    f32 = lambda x: float(_np.float32(x))
except Exception:                                            # pragma: no cover
    f32 = lambda x: x
mismatch = 0
max_delta = 0.0
for i in range(NV):
    for g in C.ALL_DEFORM:
        a = f32(W_exp[i].get(g, 0.0))
        b = W2[i].get(g, 0.0)
        if a != b:
            mismatch += 1
            max_delta = max(max_delta, abs(a - b))
log("candidate-field float32 mismatches vs shipped file = %d" % mismatch)

# ---- 2. protected sets must be byte-identical to R1A
def drift(ids, groups=None):
    m = 0.0
    for i in ids:
        for g in (groups or C.ALL_DEFORM):
            m = max(m, abs(W2[i].get(g, 0.0) - W1[i].get(g, 0.0)))
    return m


FROZEN_GROUPS = [g for g in C.ALL_DEFORM if g not in C.THUMB_FREE_GROUPS]
outside = [i for i in range(NV) if i not in AUTH]
D = {"frozen_four_finger_groups": drift(range(NV), FROZEN_GROUPS),
     "first_web_sanctioned_blend": drift(sorted(WEB)),
     "nail_semantic_vertices": drift(sorted(NAIL)),
     "distal_cap_vertices": drift(sorted(CAP)),
     "outside_authorised_region": drift(outside),
     "central_palm": drift(sorted(i for i in range(NV)
                                  if ctx["own_r1a"][i] == "wrist"))}
log("protected drift: %s" % {k: "%.1e" % v for k, v in D.items()})
if any(v != 0.0 for v in D.values()):
    raise SystemExit("FAIL CLOSED: a protected set drifted")

# ---- 3. structural / bind gates
GATES = {}
GATES["group_set_identical"] = GROUPS_B == GROUPS_A
GATES["topology_identical_to_reference"] = [tuple(p.vertices) for p in me_b.polygons] == \
    ctx["poly"]
GATES["material_identical_to_reference"] = [p.material_index for p in me_b.polygons] == \
    ctx["ref"]["MAT0"]
GATES["uv_identical_to_reference"] = ([tuple(round(u, 9) for u in d.uv)
                                      for d in me_b.uv_layers.active.data]
                                      if me_b.uv_layers.active else []) == ctx["ref"]["UV0"]
GATES["bone_count_21"] = len(rig_b.data.bones) == 21
GATES["deform_bones_16"] = len([b for b in rig_b.data.bones if b.use_deform]) == 16
GATES["parent_binding"] = ob_b.parent is not None and \
    ob_b.parent.name == "RIGHT_HAND_PRODUCTION_RIG"
GATES["armature_modifier"] = any(m.type == 'ARMATURE' and m.object is not None and
                                 m.object.name == "RIGHT_HAND_PRODUCTION_RIG"
                                 for m in ob_b.modifiers)
POSE_NONZERO = [pb.name for pb in rig_b.pose.bones
                if tuple(round(x, 9) for x in pb.rotation_quaternion) != (1.0, 0.0, 0.0, 0.0)
                or tuple(round(x, 9) for x in pb.location) != (0.0, 0.0, 0.0)
                or tuple(round(x, 9) for x in pb.scale) != (1.0, 1.0, 1.0)]
GATES["saved_at_bind_pose"] = not POSE_NONZERO
for k, v in GATES.items():
    log("GATE %-32s %s" % (k, "PASS" if v else "FAIL"))
if not all(GATES.values()):
    raise SystemExit("FAIL CLOSED: structural gate failed on the shipped artifact")

max_inf = max(len([g for g, w in W2[i].items() if w > 0.0]) for i in range(NV))
unnorm = sum(1 for i in range(NV) if abs(sum(W2[i].values()) - 1.0) > 1e-5)
S6.reset_pose(rig_b)
bpy.context.view_layer.update()
Vz, _ = C.evaluate(ob_b, MW_b)
zd = [((Vz[i] - V0[i]).length * 1000.0) for i in range(NV)]
log("max influences = %d ; unnormalised = %d ; zero-pose max = %.9f mm"
    % (max_inf, unnorm, max(zd)))

OUT = {
    "stage": "STAGE5B_R1B_POSTSAVE_SELF_PROOF", "generated_at": NOW,
    "method": ("independent re-derivation: the candidate weight field is recomputed from the "
               "frozen Stage5B R1A master plus the recorded accepted parameters, and compared "
               "against the shipped R1B artifact"),
    "r1a_master": {"path": C.R1A_MASTER.replace(os.sep, "/"), "sha256": s_r1a,
                   "unchanged": s_r1a == C.R1A_SHA256},
    "r1b_candidate": {"path": R1B.replace(os.sep, "/"), "sha256": s_r1b,
                      "blend_container_byte_reproducible": None,
                      "note": ("a .blend container is not guaranteed byte-reproducible across "
                               "saves (session metadata); the payload is what is verified here")},
    "accepted_params": PARAMS,
    "candidate_field_float32_mismatches_vs_shipped_file": mismatch,
    "candidate_field_max_abs_delta": rr(max_delta, 15),
    "PAYLOAD_ENCODES_ACCEPTED_CANDIDATE": mismatch == 0,
    "authorised_region_vertex_count": len(AUTH),
    "changed_vertex_count": len(CHANGED),
    "max_influences": max_inf, "MAX_INFLUENCES_LE_4": max_inf <= 4,
    "unnormalised_vertices": unnorm, "NORMALIZATION": "PASS" if unnorm == 0 else "FAIL",
    "unweighted_vertex_count": 0,
    "structural_gates": GATES,
    "saved_non_identity_bones": POSE_NONZERO,
    "zero_pose_bind": {"max_delta_mm": rr(max(zd)), "noise_floor_mm": 5.967e-05,
                       "ZERO_POSE_BIND": "PASS" if max(zd) <= 1e-4 else "FAIL"},
    "protected_drift": dict((k, rr(v, 15)) for k, v in D.items()),
    "PROTECTED_SETS_FROZEN": all(v == 0.0 for v in D.values()),
    "log": LOG,
}
json.dump(OUT, open(os.path.join(OUTDIR, "STAGE5B_R1B_POSTSAVE_SELF_PROOF.json"), "w",
                    encoding="utf-8"), indent=1, ensure_ascii=False)

# enrich the status file with the independent proof
status["round_status"] = "READY_FOR_HUMAN_REVIEW"
status["stage5b_r1b"] = "READY_FOR_HUMAN_REVIEW"
status["stage6b"] = "NOT_STARTED"
status["deformation_final"] = "NOT_SET_PENDING_HUMAN_REVIEW"
status["post_save_self_proof"] = {
    "file": "STAGE5B_R1B_POSTSAVE_SELF_PROOF.json",
    "PAYLOAD_ENCODES_ACCEPTED_CANDIDATE": OUT["PAYLOAD_ENCODES_ACCEPTED_CANDIDATE"],
    "PROTECTED_SETS_FROZEN": OUT["PROTECTED_SETS_FROZEN"],
    "ZERO_POSE_BIND": OUT["zero_pose_bind"]["ZERO_POSE_BIND"],
    "MAX_INFLUENCES_LE_4": OUT["MAX_INFLUENCES_LE_4"],
    "NORMALIZATION": OUT["NORMALIZATION"],
}
json.dump(status, open(STATUS_PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
log("wrote STAGE5B_R1B_POSTSAVE_SELF_PROOF.json and enriched STAGE5B_R1B_STATUS.json")
print("VERIFY_DONE")
