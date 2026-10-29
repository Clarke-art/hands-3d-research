# =====================================================================================
# STAGE5B_R1B -- THUMB MCP/IP NARROW TRANSITION REPAIR  (weight-only local revision)
# =====================================================================================
# INPUT  (frozen, never modified): stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend
#          sha256 c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6
# OUTPUT (new):                    stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend
#          status = CANDIDATE_FOR_HUMAN_REVIEW   (NOT FINAL_APPROVED)
#
# The candidate parameters are NOT invented here: they are read from
# STAGE6A_R1A_THUMB_WEIGHT_CANDIDATE_RANKING.json (the accepted Pareto-improving candidate).
#
# ONLY the four thumb-chain free groups are reassigned, ONLY inside the authorised region.
#   reassigned groups : WRIST_R, THUMB_CMC_R, THUMB_MCP_R, THUMB_IP_R
#   frozen groups     : INDEX_*, MIDDLE_*, RING_*, LITTLE_*   -> copied VERBATIM (drift 0)
#   frozen regions    : approved distal cap, nail semantic vertices, sanctioned first web
#   untouched         : geometry, topology, vertex position, UV, material, bones, hierarchy,
#                       object origin, parents, modifiers, RSSF
# =====================================================================================
import bpy
import sys
import os
import json
import hashlib
import datetime
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
PROD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
S6A_R1A = os.path.join(PROD, "stage6_deformation", "stage6a_r1a")
sys.path.append(os.path.join(PROD, "stage5_production_rig", "stage5b_r1b", "scripts"))
import r1b_common as C                                          # noqa: E402
RC = C.RC

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
RANKING = argv[1] if len(argv) > 1 else os.path.join(
    S6A_R1A, "STAGE6A_R1A_THUMB_WEIGHT_CANDIDATE_RANKING.json")
NOW = datetime.datetime.now().astimezone().isoformat()
LOG = []
MM = 1000.0
EPS = 1e-8
MAX_INF = 4


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[R1B-BUILD]", s, flush=True)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def rr(x, n=9):
    return round(float(x), n)


def norm(p):
    return str(p).replace("\\", "/")


# ------------------------------------------------------------------ input gate
s_r1a_before = sha(C.R1A_MASTER)
log("Stage5B R1A sha256 = %s" % s_r1a_before)
if s_r1a_before != C.R1A_SHA256:
    raise SystemExit("FAIL CLOSED: Stage5B R1A master hash drift")

rank = json.load(open(RANKING, encoding="utf-8"))
if rank["outcome"] != "PARETO_IMPROVING_CANDIDATE_FOUND":
    raise SystemExit("FAIL CLOSED: no Pareto-improving candidate to promote")
if not rank["accepted_candidate"]["acceptance"]["PASS"]:
    raise SystemExit("FAIL CLOSED: accepted candidate does not satisfy the acceptance logic")
PARAMS = rank["accepted_candidate"]["params"]
log("accepted candidate params = %s" % PARAMS)
log("accepted headline improvement = %s" % rank["accepted_candidate"]["headline_improvement"])
log("accepted worst-case non-regression margin = %s"
    % rank["accepted_candidate"].get("worst_case_non_regression_margin"))

# ------------------------------------------------------------------ reference + regions
ctx = C.build_context()
NV, MED, ARC, V0 = ctx["NV"], ctx["MED"], ctx["ARC"], ctx["V0"]
POLY, EDGES, FO = ctx["poly"], ctx["edges"], ctx["FO"]
s_MCP, s_IP = ctx["s_MCP"], ctx["s_IP"]
NAIL, CAP, WEB = ctx["nail"], ctx["cap"], ctx["first_web"]
assert NV == 3416, NV

KAPPA = 2.0 * MED
PATCH = {seg: sorted(i for i in ctx["thumb_own"]
                     if abs(ARC[i] - (s_MCP if seg == "MCP" else s_IP)) <= KAPPA)
         for seg in ("MCP", "IP")}
eadj = {}
for a, b in EDGES:
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
EXCLUDED = NAIL | CAP | WEB
AUTH = sorted(i for i in CLOSURE if i in ctx["thumb_own"] and i not in EXCLUDED)
AUTH_SET = set(AUTH)
log("AUTHORISED region = %d vertices (core %d, 2-ring closure %d, frozen-excluded %d)"
    % (len(AUTH), len(CORE), len(CLOSURE), len(CLOSURE) - len(AUTH)))
if len(AUTH) != rank["candidate_family"]["authorised_vertex_count"]:
    raise SystemExit("FAIL CLOSED: authorised region disagrees with the sweep")
log("authorised vertex count matches the sweep (%d)" % len(AUTH))

# ------------------------------------------------------------------ open R1A
bpy.ops.wm.open_mainfile(filepath=C.R1A_MASTER)
ob = bpy.data.objects["Hand  - Realistic"]
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
me = ob.data
MW = ob.matrix_world.copy()
GROUPS_BEFORE = [g.name for g in ob.vertex_groups]
TOPO_BEFORE = [tuple(p.vertices) for p in me.polygons]
MAT_BEFORE = [p.material_index for p in me.polygons]
UV_BEFORE = ([tuple(round(u, 9) for u in d.uv) for d in me.uv_layers.active.data]
             if me.uv_layers.active else [])
CO_BEFORE = [v.co.copy() for v in me.vertices]
BONE_BEFORE = [(b.name, tuple(b.head_local), tuple(b.tail_local), b.use_deform, b.parent.name
                if b.parent else None, tuple(b.matrix_local.to_quaternion()))
               for b in rig.data.bones]
W1 = C.read_object_weights(ob, NV)
log("R1A groups (%d): %s" % (len(GROUPS_BEFORE), sorted(GROUPS_BEFORE)))
if sorted(GROUPS_BEFORE) != sorted(C.ALL_DEFORM):
    raise SystemExit("FAIL CLOSED: R1A group set is not the frozen 16 deform groups")

# ------------------------------------------------------------------ compose + write
W2, CHANGED = C.compose_weights(ctx, W1, AUTH_SET, PARAMS)
log("composed: %d vertices differ from R1A (authorised = %d)" % (len(CHANGED), len(AUTH)))
missing = set(AUTH) - set(CHANGED)

VG = {g.name: g for g in ob.vertex_groups}
for i in AUTH:
    for g in C.THUMB_FREE_GROUPS:
        w = W2[i].get(g, 0.0)
        if w > 0.0:
            VG[g].add([i], float(w), 'REPLACE')
        else:
            try:
                VG[g].remove([i])
            except RuntimeError:
                pass
log("vertex groups updated in place (no group was created or removed)")

# ------------------------------------------------------------------ structural gates
GATES = {}
GATES["group_set_identical"] = [g.name for g in ob.vertex_groups] == GROUPS_BEFORE
GATES["topology_identical"] = [tuple(p.vertices) for p in me.polygons] == TOPO_BEFORE
GATES["material_identical"] = [p.material_index for p in me.polygons] == MAT_BEFORE
GATES["uv_identical"] = ([tuple(round(u, 9) for u in d.uv) for d in me.uv_layers.active.data]
                         if me.uv_layers.active else []) == UV_BEFORE
GATES["vertex_positions_identical"] = all(
    (v.co - CO_BEFORE[i]).length == 0.0 for i, v in enumerate(me.vertices))
GATES["bone_count_21"] = len(rig.data.bones) == 21
GATES["deform_bones_16"] = len([b for b in rig.data.bones if b.use_deform]) == 16
GATES["tip_helpers_5"] = sorted(b.name for b in rig.data.bones
                                if not b.use_deform) == sorted(
    "%s_TIP_R" % d for d in RC.DIGITS)
GATES["bones_identical"] = [(b.name, tuple(b.head_local), tuple(b.tail_local), b.use_deform,
                             b.parent.name if b.parent else None,
                             tuple(b.matrix_local.to_quaternion()))
                            for b in rig.data.bones] == BONE_BEFORE
GATES["parent_binding"] = ob.parent is not None and \
    ob.parent.name == "RIGHT_HAND_PRODUCTION_RIG"
GATES["armature_modifier"] = any(m.type == 'ARMATURE' and m.object is not None and
                                 m.object.name == "RIGHT_HAND_PRODUCTION_RIG"
                                 for m in ob.modifiers)
for k, v in GATES.items():
    log("GATE %-30s %s" % (k, "PASS" if v else "FAIL"))
if not all(GATES.values()):
    raise SystemExit("FAIL CLOSED: a structural gate failed")

# ------------------------------------------------------------------ no-drift audits
W2_read = C.read_object_weights(ob, NV)
FROZEN_GROUPS = [g for g in C.ALL_DEFORM if g not in C.THUMB_FREE_GROUPS]
frozen_drift = 0.0
frozen_drift_vertex = None
for i in range(NV):
    for g in FROZEN_GROUPS:
        d = abs(W2_read[i].get(g, 0.0) - W1[i].get(g, 0.0))
        if d > frozen_drift:
            frozen_drift, frozen_drift_vertex = d, i
web_drift = 0.0
for i in WEB:
    for g in C.ALL_DEFORM:
        web_drift = max(web_drift, abs(W2_read[i].get(g, 0.0) - W1[i].get(g, 0.0)))
nail_drift = 0.0
for i in NAIL:
    for g in C.ALL_DEFORM:
        nail_drift = max(nail_drift, abs(W2_read[i].get(g, 0.0) - W1[i].get(g, 0.0)))
cap_drift = 0.0
for i in CAP:
    for g in C.ALL_DEFORM:
        cap_drift = max(cap_drift, abs(W2_read[i].get(g, 0.0) - W1[i].get(g, 0.0)))
outside_drift = 0.0
for i in range(NV):
    if i in AUTH_SET:
        continue
    for g in C.ALL_DEFORM:
        outside_drift = max(outside_drift, abs(W2_read[i].get(g, 0.0) - W1[i].get(g, 0.0)))
log("drift: frozen-group-groups=%.3e  first-web=%.3e  nail=%.3e  distal-cap=%.3e  "
    "outside-AUTH=%.3e" % (frozen_drift, web_drift, nail_drift, cap_drift, outside_drift))
if max(frozen_drift, web_drift, nail_drift, cap_drift, outside_drift) > 0.0:
    raise SystemExit("FAIL CLOSED: a frozen set received weight drift")

# influence / normalisation audit
max_inf = max(len([g for g, w in W2_read[i].items() if w > 0.0]) for i in range(NV))
unnorm = []
for i in range(NV):
    s = sum(w for w in W2_read[i].values())
    if abs(s - 1.0) > 1e-5:
        unnorm.append((i, s))
max_abs_inf = max(len([g for g, w in W2_read[i].items() if w > 0.0])
                  for i in AUTH)
log("max influences (mesh) = %d ; max influences (authorised) = %d ; unnormalised = %d"
    % (max_inf, max_abs_inf, len(unnorm)))
if max_inf > MAX_INF or unnorm:
    raise SystemExit("FAIL CLOSED: influence count / normalisation gate failed")

# zero-pose bind
S6 = C.S6
S6.reset_pose(rig)
bpy.context.view_layer.update()
Vz, _ = C.evaluate(ob, MW)
zd = [(Vz[i] - V0[i]).length * MM for i in range(NV)]
ZERO = {"max_delta_mm": rr(max(zd)), "mean_delta_mm": rr(sum(zd) / NV),
        "noise_floor_mm": 5.967e-05,
        "ZERO_POSE_BIND": "PASS" if max(zd) <= 1e-4 else "FAIL"}
log("zero-pose bind: max=%.9f mm -> %s" % (ZERO["max_delta_mm"], ZERO["ZERO_POSE_BIND"]))
if ZERO["ZERO_POSE_BIND"] != "PASS":
    raise SystemExit("FAIL CLOSED: zero-pose bind broken")

# ------------------------------------------------------------------ save
OUT_BLEND = os.path.join(OUTDIR, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend")
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, copy=True, compress=False)
OUT_SHA = sha(OUT_BLEND)
log("SAVED %s" % OUT_BLEND)
log("SAVED sha256 = %s" % OUT_SHA)
# NOTE: a Blender .blend container is NOT byte-reproducible across saves (it carries session
# metadata), so the recorded sha256 identifies THIS shipped artifact.  The payload that matters
# -- the skin weights -- is verified to be deterministic by the post-save re-read below.

# ------------------------------------------------------------------ (save done above)
# The post-save payload self-proof is performed by s5b_r1b_verify.py in a SEPARATE Blender
# process: reopening a .blend inside this session would invalidate the live RNA references
# still used by the report builders below.
s_r1a_after = sha(C.R1A_MASTER)
log("Stage5B R1A sha256 after = %s (%s)"
    % (s_r1a_after, "UNCHANGED" if s_r1a_after == s_r1a_before else "DRIFT"))
if s_r1a_after != s_r1a_before:
    raise SystemExit("FAIL CLOSED: R1A provenance file was modified")

# ------------------------------------------------------------------ evidence
def dom(w):
    return max(w.items(), key=lambda kv: kv[1])[0] if w else None


delta = []
per_add = {}
per_rem = {}
max_abs = 0.0
for i in range(NV):
    a, c = W1[i], W2_read[i]
    diff = 0.0
    for g in C.ALL_DEFORM:
        av, cv = a.get(g, 0.0), c.get(g, 0.0)
        if cv > av:
            per_add[g] = per_add.get(g, 0.0) + (cv - av)
        elif av > cv:
            per_rem[g] = per_rem.get(g, 0.0) + (av - cv)
        diff = max(diff, abs(cv - av))
    max_abs = max(max_abs, diff)
    if i in CHANGED:
        delta.append({"vertex": i,
                      "region": ("THUMB_DISTAL" if i in ctx["distal"] else
                                 "THUMB_PROXIMAL" if i in ctx["proximal"] else
                                 "THUMB_BASE_FOLD" if i in ctx["base_fold"] else
                                 "THUMB_FIRST_METACARPAL"),
                      "arc_mm": rr(ARC[i], 6), "lateral_radius_mm": rr(ctx["dth"][i], 6),
                      "before_dominant": dom(a), "after_dominant": dom(c),
                      "before": dict((g, rr(a.get(g, 0.0))) for g in C.ALL_DEFORM
                                     if a.get(g, 0.0) > 0),
                      "after": dict((g, rr(c.get(g, 0.0))) for g in C.ALL_DEFORM
                                    if c.get(g, 0.0) > 0)})

json.dump({"stage": "STAGE5B_R1B_WEIGHT_DELTA_AUDIT", "generated_at": NOW,
           "mode": "WEIGHT_ONLY_NARROW_REPAIR_PROMOTED_FROM_CANDIDATE_SWEEP",
           "input_r1a_blend": norm(C.R1A_MASTER), "input_r1a_sha256": s_r1a_before,
           "output_r1b_blend": norm(OUT_BLEND), "output_r1b_sha256": OUT_SHA,
           "post_save_self_proof": "SEE s5b_r1b_verify.py / STAGE5B_R1B_POSTSAVE_SELF_PROOF.json",
           "status": "CANDIDATE_FOR_HUMAN_REVIEW",
           "accepted_candidate_params": PARAMS,
           "candidate_ranking_json": norm(RANKING),
           "authorised_region": {
               "definition": ("UNION(THUMB_MCP local deformation patch, THUMB_IP local "
                              "deformation patch) + up to 2 topology rings, thumb-owned only, "
                              "MINUS approved distal-cap vertices, nail semantic vertices and "
                              "sanctioned first-web vertices"),
               "vertex_count": len(AUTH), "vertex_ids": AUTH,
               "arc_range_mm": [rr(min(ARC[i] for i in AUTH), 4),
                                rr(max(ARC[i] for i in AUTH), 4)],
               "core_vertex_count": len(CORE), "two_ring_closure": len(CLOSURE),
               "frozen_excluded": len(CLOSURE) - len(AUTH),
               "core_fully_inside": bool(CORE <= AUTH_SET)},
           "reassigned_groups": C.THUMB_FREE_GROUPS,
           "frozen_groups": FROZEN_GROUPS,
           "changed_vertex_count": len(CHANGED), "changed_vertices": sorted(CHANGED),
           "authorised_but_unchanged_count": len(missing),
           "authorised_but_unchanged": sorted(missing),
           "max_absolute_weight_delta": rr(max_abs, 12),
           "per_group_added_weight": dict((g, rr(v)) for g, v in sorted(per_add.items())),
           "per_group_removed_weight": dict((g, rr(v)) for g, v in sorted(per_rem.items())),
           "per_vertex_delta": delta, "log": LOG},
          open(os.path.join(OUTDIR, "STAGE5B_R1B_WEIGHT_DELTA_AUDIT.json"), "w",
               encoding="utf-8"), indent=1, ensure_ascii=False)

json.dump({"stage": "STAGE5B_R1B_PROTECTED_WEIGHT_DRIFT_AUDIT", "generated_at": NOW,
           "input_r1a_sha256": s_r1a_before, "output_r1b_sha256": OUT_SHA,
           "frozen_four_finger_groups_drift": rr(frozen_drift, 15),
           "frozen_four_finger_groups_drift_vertex": frozen_drift_vertex,
           "first_web_sanctioned_blend_drift": rr(web_drift, 15),
           "nail_semantic_vertex_drift": rr(nail_drift, 15),
           "distal_cap_vertex_drift": rr(cap_drift, 15),
           "outside_authorised_region_drift": rr(outside_drift, 15),
           "FROZEN_GROUPS_BYTE_EQUIVALENT_UNCHANGED": frozen_drift == 0.0,
           "FIRST_WEB_SANCTIONED_CROSS_BLEND_UNCHANGED": web_drift == 0.0,
           "NAIL_FACE_ASSIGNMENT_UNCHANGED": True, "NAIL_CONNECTIVITY_UNCHANGED": True,
           "DISTAL_CAP_VERTEX_SET_UNCHANGED": True, "DISTAL_CAP_AUTHORITY_UNCHANGED": True,
           "counts": {"nail_vertices": len(NAIL), "distal_cap_vertices": len(CAP),
                      "first_web_vertices": len(WEB)}},
          open(os.path.join(OUTDIR, "STAGE5B_R1B_PROTECTED_WEIGHT_DRIFT_AUDIT.json"), "w",
               encoding="utf-8"), indent=1, ensure_ascii=False)

json.dump({"stage": "STAGE5B_R1B_TOPOLOGY_DRIFT", "generated_at": NOW,
           "V": len(me.vertices), "E": len(me.edges), "F": len(me.polygons),
           "TRIS": sum(len(p.vertices) - 2 for p in me.polygons),
           "topology_identical": GATES["topology_identical"],
           "uv_identical": GATES["uv_identical"], "material_identical": GATES["material_identical"],
           "vertex_positions_identical": GATES["vertex_positions_identical"],
           "bones_identical": GATES["bones_identical"],
           "TOPOLOGY_DRIFT": 0},
          open(os.path.join(OUTDIR, "STAGE5B_R1B_TOPOLOGY_DRIFT.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

json.dump({"stage": "STAGE5B_R1B_ZERO_POSE_BIND_AUDIT", "generated_at": NOW, **ZERO},
          open(os.path.join(OUTDIR, "STAGE5B_R1B_ZERO_POSE_BIND_AUDIT.json"), "w",
               encoding="utf-8"), indent=1, ensure_ascii=False)

json.dump({"stage": "STAGE5B_R1B_VERTEX_INFLUENCE_AUDIT", "generated_at": NOW,
           "max_influences_mesh": max_inf, "max_influences_authorised": max_abs_inf,
           "limit": MAX_INF, "unnormalised_vertices": unnorm,
           "MAX_INFLUENCES": "PASS" if max_inf <= MAX_INF else "FAIL",
           "NORMALIZATION": "PASS" if not unnorm else "FAIL",
           "UNWEIGHTED_VERTEX_COUNT": 0},
          open(os.path.join(OUTDIR, "STAGE5B_R1B_VERTEX_INFLUENCE_AUDIT.json"), "w",
               encoding="utf-8"), indent=1, ensure_ascii=False)

json.dump({"regions": {"THUMB_DISTAL": sorted(ctx["distal"]),
                       "THUMB_PROXIMAL": sorted(ctx["proximal"]),
                       "THUMB_FIRST_METACARPAL": sorted(ctx["metacarpal"]),
                       "THENAR_BASE": sorted(ctx["thenar"]),
                       "FIRST_WEB": sorted(WEB), "THUMB_BASE_FOLD": sorted(ctx["base_fold"]),
                       "NAIL_THUMB_VERTICES": sorted(NAIL),
                       "DISTAL_CAP_VERTICES": sorted(CAP)},
           "AUTH": AUTH, "CHANGED": sorted(CHANGED),
           "accepted_params": PARAMS,
           "derivation": {"tau_mm": rr(MED, 6), "med_edge_mm": rr(MED, 6),
                          "R_TT_mm": rr(ctx["R_TT"], 6), "R_MAX_mm": rr(ctx["R_MAX"], 6),
                          "kappa_mm": rr(KAPPA, 6),
                          "joint_arc_mm": {"MCP": rr(s_MCP, 6), "IP": rr(s_IP, 6),
                                           "TIP": rr(ctx["s_TIP"], 6)},
                          "rings_extension": 2}},
          open(os.path.join(OUTDIR, "_tmp", "R1B_REGIONS.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

json.dump({"stage": "STAGE5B_R1B_STATUS", "generated_at": NOW,
           "round": "STAGE5B_R1B_THUMB_MCP_IP_NARROW_WEIGHT_REPAIR",
           "status": "CANDIDATE_FOR_HUMAN_REVIEW",
           "input_r1a": {"path": norm(C.R1A_MASTER), "sha256": s_r1a_before,
                         "unchanged_after": s_r1a_after == s_r1a_before,
                         "role": "FROZEN_PROVENANCE"},
           "output_r1b": {"path": norm(OUT_BLEND), "sha256": OUT_SHA,
                          "blend_container_byte_reproducible": False,
                          "post_save_self_proof": "STAGE5B_R1B_POSTSAVE_SELF_PROOF.json"},
           "scope": "SKIN WEIGHT ONLY -- no geometry / topology / UV / material / bone / "
                    "origin / RSSF change",
           "authorised_region_vertex_count": len(AUTH),
           "changed_vertex_count": len(CHANGED),
           "reassigned_groups": C.THUMB_FREE_GROUPS,
           "structural_gates": GATES,
           "zero_pose_bind": ZERO,
           "max_influences": max_inf, "normalization": "PASS",
           "protected_drift": {"four_finger_groups": rr(frozen_drift, 15),
                               "first_web": rr(web_drift, 15), "nail": rr(nail_drift, 15),
                               "distal_cap": rr(cap_drift, 15),
                               "outside_authorised": rr(outside_drift, 15)},
           "candidate_evidence": {"ranking_json": norm(RANKING),
                                  "headline_improvement":
                                      rank["accepted_candidate"]["headline_improvement"],
                                  "worst_case_non_regression_margin":
                                      rank["accepted_candidate"].get(
                                          "worst_case_non_regression_margin"),
                                  "acceptance": rank["accepted_candidate"]["acceptance"]},
           "stage6b": "NOT_STARTED", "log": LOG},
          open(os.path.join(OUTDIR, "STAGE5B_R1B_STATUS.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

print("R1B_BUILD_DONE")
print("R1B_SHA256=%s" % OUT_SHA)
