# =====================================================================================
# STAGE5B R1C -- LOCAL WEIGHT RECONCILIATION candidate (CANDIDATE_FOR_HUMAN_REVIEW)
# =====================================================================================
# INPUT  (frozen, never modified) stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend
#        sha256 cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10
# OUTPUT (new) stage5b_r1c/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1C.blend
#        status = CANDIDATE_FOR_HUMAN_REVIEW  (Stage5B R1B stays the frozen master)
#
# Only vertex-group weights on the AUTHORISED region change.  Geometry, topology, UV,
# materials, nail faces, bones, joints, rolls, object origin and the RSSF pose are untouched.
# =====================================================================================
import os
import sys
import json
import datetime
from collections import Counter

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S6B_R1B_SCRIPTS = os.path.join(PROD, "stage6_deformation", "stage6b_r1b", "scripts")
sys.path.append(S6B_R1B_SCRIPTS)
sys.path.append(HERE)
import s6br1b_common as K                                          # noqa: E402

OUT = K.S5B_R1C
NOW = datetime.datetime.now().astimezone().isoformat()
LOG = []


def log(s):
    LOG.append(s)
    print("[R1C] " + s, flush=True)


# ---------------------------------------------------------------- input gate
s0 = K.sha256(K.R1B_MASTER)
if s0 != K.R1B_SHA256:
    raise SystemExit("FAIL CLOSED: Stage5B R1B master hash mismatch")
log("Stage5B R1B master sha OK %s" % s0[:12])

ctx = K.B.build_context()
ref = ctx["ref"]
NV = ref["NV"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
own = ctx["own_r1a"]

probe = K.load_probe_sets()
part = K.r2_partition(ctx, ref)
P2 = part["partition"]
C = K.build_corrected_ownership(ctx, ref, P2, probe)
CORR = C["corrected"]
domain = set(C["domain"])

# ---------------------------------------------------------------- read R1B
bpy.ops.wm.open_mainfile(filepath=K.R1B_MASTER)
ob = bpy.data.objects[K.MESH_OBJ]
rig = bpy.data.objects[K.RIG_OBJ]
MW = ob.matrix_world.copy()
L0 = [v.co.copy() for v in ob.data.vertices]
TOPO = [tuple(p.vertices) for p in ob.data.polygons]
MAT = [p.material_index for p in ob.data.polygons]
UV = ([tuple(round(u, 9) for u in d.uv) for d in ob.data.uv_layers.active.data]
      if ob.data.uv_layers.active else [])
WOLD = K.read_weights(ob, NV)
BONES_REST = dict((b.name, (tuple(b.head_local), tuple(b.tail_local))) for b in rig.data.bones)
ORIGIN0 = tuple(rig.location)
OB_ORIGIN0 = tuple(ob.location)
log("R1B: groups=%s" % sorted(g.name for g in ob.vertex_groups))

VERDICT, FOREIGN = K.weight_consistency(CORR, WOLD)
web_set = set(ctx["first_web"])
REQ_ALL = sorted(i for i in domain if VERDICT[i] == "WEIGHT_RECONCILIATION_REQUIRED")
# cross-boundary continuity additions (round spec sections 13 / 14): the endpoints of the
# corrected ownership boundary are reconciled on BOTH sides so that relocating the
# boundary does not merely move the weight discontinuity.
BND_ADD = sorted(v for v in C["boundary_continuity_added"] if v not in set(REQ_ALL))
REQ_ALL = sorted(set(REQ_ALL) | set(BND_ADD))
AMBIG = sorted(i for i in domain if VERDICT[i] == "AMBIGUOUS")
# ---- FIRST WEB PROTECTION (round spec §14/§15): the approved first-web vertices are held as
# Dirichlet anchors and are NEVER reweighted, so that no smoothing crosses the first-web
# authority and the approved first-web whitelist keeps holding verbatim.
FW_EXCLUDED = sorted(i for i in REQ_ALL if i in web_set)
PRIMARY = sorted(i for i in REQ_ALL if i not in web_set)
log("primary (reconciliation required) = %d (of which %d are FIRST_WEB -> excluded)"
    % (len(REQ_ALL), len(FW_EXCLUDED)))
log("ambiguous = %d" % len(AMBIG))

# ---------------------------------------------------------------- authorised region (§10)
adj = K.mesh_graph(V0, EDGES)
ADJ = dict((k, [t[0] for t in v]) for k, v in adj.items())
primary = set(PRIMARY)
ring1 = set()
for i in PRIMARY:
    for u in ADJ.get(i, ()):
        if u not in primary and CORR[u] == CORR[i]:
            ring1.add(u)
ring2 = set()
for i in sorted(primary | ring1):
    cnt = sum(1 for u in ADJ.get(i, ()) if u not in (primary | ring1) and CORR[u] == CORR[i])
    if cnt < 2:
        for u in ADJ.get(i, ()):
            if u not in (primary | ring1) and CORR[u] == CORR[i]:
                ring2.add(u)
AUTH = sorted(primary | ring1 | ring2)
log("authorised region: primary=%d +1ring=%d +2ring=%d = %d"
    % (len(primary), len(ring1), len(ring2), len(AUTH)))
forb_thumb = set(i for i in AUTH if CORR[i] == "THUMB")
forb_index = set(i for i in AUTH if CORR[i] == "INDEX")
log("authorised by corrected digit: THUMB=%d INDEX=%d other=%d"
    % (len(forb_thumb), len(forb_index),
       len([i for i in AUTH if CORR[i] not in ("THUMB", "INDEX")])))

# ---------------------------------------------------------------- reconcile weights
# only PRIMARY vertices change; the rest of the authorised region serves as anchor context.
WRAW, INFO = K.trusted_interpolation(ref, WOLD, CORR, set(PRIMARY))
WNEW = [dict(WOLD[i]) for i in range(NV)]
CHANGED = []
for i in PRIMARY:
    newv = WRAW[i]
    if not newv:
        continue
    newv = dict((g, K.rr(v, 9)) for g, v in newv.items() if v > 1e-6)
    items = sorted(newv.items(), key=lambda kv: (-kv[1], kv[0]))[:4]
    s = sum(v for _g, v in items)
    if s <= 0:
        continue
    newv = dict((g, v / s) for g, v in items)
    if newv != WOLD[i]:
        WNEW[i] = newv
        CHANGED.append(i)
log("weights changed on %d vertices" % len(CHANGED))
log("changed group families: %s"
    % dict(Counter(g for i in CHANGED for g in WNEW[i])))

# gate: corrected vertices must not keep a foreign group
resid = [i for i in CHANGED
         if any(g not in set(K.allowed_groups(CORR[i])) for g in WNEW[i])]
if resid:
    raise SystemExit("FAIL CLOSED: foreign group survived on %d vertices" % len(resid))

# ---------------------------------------------------------------- write the candidate
K.push_weights(ob, NV, WNEW)
KG = dict((g.name, g) for g in ob.vertex_groups)
for g in K.RB.ALL_DEFORM:
    if g not in KG:
        raise SystemExit("FAIL CLOSED: deform group missing %s" % g)

bpy.context.preferences.filepaths.save_version = 0
os.makedirs(OUT, exist_ok=True)
CAND = K.R1C_MASTER
bpy.ops.wm.save_as_mainfile(filepath=CAND, copy=True, compress=False)
s1 = K.sha256(CAND)
log("saved %s  sha=%s  bytes=%d" % (CAND, s1[:12], os.path.getsize(CAND)))

# ---------------------------------------------------------------- post-save verification
bpy.ops.wm.open_mainfile(filepath=CAND)
ob2 = bpy.data.objects[K.MESH_OBJ]
rig2 = bpy.data.objects[K.RIG_OBJ]
MW2 = ob2.matrix_world.copy()
NV2 = len(ob2.data.vertices)
L2 = [v.co.copy() for v in ob2.data.vertices]
TOPO2 = [tuple(p.vertices) for p in ob2.data.polygons]
MAT2 = [p.material_index for p in ob2.data.polygons]
UV2 = ([tuple(round(u, 9) for u in d.uv) for d in ob2.data.uv_layers.active.data]
       if ob2.data.uv_layers.active else [])
W2 = K.read_weights(ob2, NV2)
BONES2 = dict((b.name, (tuple(b.head_local), tuple(b.tail_local))) for b in rig2.data.bones)
ORIGIN2 = tuple(rig2.location)
OB_ORIGIN2 = tuple(ob2.location)

geo_delta = max((L2[i] - L0[i]).length for i in range(NV))
K.reset_pose2 = None
K.B.reset_pose(rig2)
K.B.update()
VE = K.RB.evaluate(ob2, MW2)[0]
rssf_delta = max((VE[i] - V0[i]).length * K.MM for i in range(NV))

GATES = {
    "GEOMETRY_DELTA": K.rr(geo_delta, 9),
    "RSSF_GEOMETRY_DELTA_MM": K.rr(rssf_delta, 9),
    "TOPOLOGY_DELTA": 0 if (NV2 == NV and TOPO2 == TOPO) else 1,
    "UV_DELTA": 0 if UV2 == UV else 1,
    "MATERIAL_DELTA": 0 if MAT2 == MAT else 1,
    "BONE_DELTA": 0 if BONES2 == BONES_REST else 1,
    "OBJECT_ORIGIN_DELTA": 0 if (OB_ORIGIN2 == OB_ORIGIN0 and ORIGIN2 == ORIGIN0) else 1,
    "GROUP_SET_UNCHANGED": sorted(g.name for g in ob2.vertex_groups) == sorted(K.RB.ALL_DEFORM),
}
VG = K.vertex_group_stats(W2)
GATES.update({
    "UNWEIGHTED_VERTICES": VG["unweighted_vertices"],
    "MAX_INFLUENCES": VG["max_influences"],
    "MAX_INFLUENCES_LE_4": VG["max_influences"] <= 4,
    "NAN_WEIGHTS": VG["nan_weights"],
    "NEGATIVE_WEIGHTS": VG["negative_weights"],
    "NON_NORMALIZED_VERTICES": VG["non_normalized_vertices"],
})
VGOLD = K.vertex_group_stats(WOLD)
log("gates: %s" % json.dumps(GATES, ensure_ascii=False))
log("R1B baseline group stats: %s" % json.dumps(VGOLD, ensure_ascii=False))

# ---------------------------------------------------------------- drift audit
CH = set(CHANGED)
DRIFT = []
for i in range(NV):
    if i in CH:
        continue
    d = max([abs(WNEW[i].get(g, 0.0) - W2[i].get(g, 0.0))
             for g in set(list(WNEW[i]) + list(W2[i]))] or [0.0])
    DRIFT.append(d)
FOURG = set(["%s_%s_R" % (d, s) for d in ("MIDDLE", "RING", "LITTLE") for s in K.RC.CHAIN[d]])
four_drift = 0.0
idx_drift_outside = 0.0
for i in range(NV):
    if i in CH:
        continue
    for g in FOURG:
        four_drift = max(four_drift, abs(WNEW[i].get(g, 0.0) - W2[i].get(g, 0.0)))
cage = set(ctx["cmc_cage_patch"])
cage_drift = max([max([abs(WNEW[i].get(g, 0.0) - W2[i].get(g, 0.0))
                       for g in set(list(WNEW[i]) + list(W2[i]))] or [0.0])
                  for i in cage if i not in CH] or [0.0])
IDXG = set(["INDEX_%s_R" % s for s in K.RC.CHAIN["INDEX"]])
for i in range(NV):
    if i in CH or CORR[i] != "INDEX":
        continue
    for g in IDXG:
        idx_drift_outside = max(idx_drift_outside, abs(WNEW[i].get(g, 0.0) - W2[i].get(g, 0.0)))
DRIFT_AUDIT = {
    "stage": "STAGE5B_R1C_PROTECTED_WEIGHT_DRIFT_AUDIT",
    "generated_at": NOW,
    "definition": ("every vertex outside the AUTHORISED region must keep its Stage5B R1B bind "
                   "weights bit-for-bit"),
    "OUTSIDE_AUTHORISED_WEIGHT_DRIFT": K.rr(max(DRIFT), 12) if DRIFT else 0.0,
    "MIDDLE_RING_LITTLE_DRIFT": K.rr(four_drift, 12),
    "UNAFFECTED_INDEX_REGION_DRIFT": K.rr(idx_drift_outside, 12),
    "CMC_CAGE_PROTECTED_DRIFT": K.rr(cage_drift, 12),
    "cmc_cage_vertices": len(cage),
    "cmc_cage_inside_authorised": len([i for i in cage if i in CH]),
    "authorised_region_count": len(AUTH),
    "changed_vertex_count": len(CHANGED),
    "verdict": ("PASS" if (max(DRIFT) if DRIFT else 0.0) == 0.0 and four_drift == 0.0
                and idx_drift_outside == 0.0 and cage_drift == 0.0 else "FAIL"),
}

# ---------------------------------------------------------------- first-web protection
web = set(ctx["first_web"])
web_ip = sorted(i for i in web if W2[i].get("THUMB_IP_R", 0.0) > 0.0)
web_changed = sorted(i for i in web if i in CH)
WEB_OK = {"WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "INDEX_MCP_R"}
WEB_FORBIDDEN = {"THUMB_IP_R", "INDEX_PIP_R", "INDEX_DIP_R",
                 "MIDDLE_MCP_R", "MIDDLE_PIP_R", "MIDDLE_DIP_R",
                 "RING_MCP_R", "RING_PIP_R", "RING_DIP_R",
                 "LITTLE_MCP_R", "LITTLE_PIP_R", "LITTLE_DIP_R"}
web_forbidden = sorted((i, sorted(g for g in W2[i] if g in WEB_FORBIDDEN)) for i in web
                       if any(g in WEB_FORBIDDEN for g in W2[i]))
web_whitelist_ok = not web_forbidden
FW = {
    "stage": "STAGE5B_R1C_FIRST_WEB_PROTECTION_AUDIT",
    "generated_at": NOW,
    "first_web_vertex_count": len(web),
    "first_web_vertex_ids": sorted(web),
    "FIRST_WEB_SEMANTIC_REGION_CHANGED": 0,
    "first_web_semantics_authority": "Stage5B R1A/R1B approved FIRST_WEB mask (verbatim)",
    "FIRST_WEB_THUMB_IP_WEIGHT": K.rr(max([W2[i].get("THUMB_IP_R", 0.0) for i in web] or [0.0]), 9),
    "first_web_vertices_carrying_THUMB_IP": web_ip,
    "first_web_vertices_reweighted": web_changed,
    "first_web_vertices_excluded_from_reconciliation": FW_EXCLUDED,
    "approved_first_web_whitelist": sorted(WEB_OK),
    "approved_first_web_forbidden_groups": sorted(WEB_FORBIDDEN),
    "first_web_whitelist_violations": web_forbidden,
    "approved_first_web_whitelist_intact": web_whitelist_ok,
    "CLASS_A_EDGE_ANATOMICAL_STATUS": "UNCHANGED (ANATOMIC_FIRST_WEB_TRANSITION)",
    "verdict": ("PASS" if (not web_ip and not web_changed and web_whitelist_ok) else "REVIEW"),
}
log("first web: n=%d thumb_IP carriers=%d reweighted=%d whitelist_ok=%s"
    % (len(web), len(web_ip), len(web_changed), web_whitelist_ok))

# ---------------------------------------------------------------- authorised region json
AUTH_J = {
    "stage": "STAGE5B_R1C_AUTHORISED_WEIGHT_REGION",
    "generated_at": NOW,
    "corrected_ownership_authority": "DIGIT_OWNERSHIP_AUTHORITY_R2",
    "primary_count": len(primary),
    "one_ring_additions": len(ring1),
    "two_ring_additions": len(ring2),
    "two_ring_justification": ("added only for authorised vertices that have fewer than 2 "
                               "same-corrected-digit trusted neighbours, so that the deterministic "
                               "anchored interpolation always has an anchor set"),
    "final_authorised_count": len(AUTH),
    "vertices_actually_reweighted": len(CHANGED),
    "allowed_groups_by_corrected_digit": {
        "THUMB": K.allowed_groups("THUMB"), "INDEX": K.allowed_groups("INDEX"),
        "wrist": K.allowed_groups("wrist")},
    "forbidden_expansion": ("NO whole-thumb / whole-index / whole-palm reweighting; the authorised "
                            "region is closed over the same-corrected-digit 1-/2-ring only"),
    "primary_vertices": PRIMARY,
    "one_ring_vertices": sorted(ring1),
    "two_ring_vertices": sorted(ring2),
    "authorised_vertices": AUTH,
    "changed_vertices": CHANGED,
    "interpolation_method_counts": dict(Counter(v["method"] for v in INFO.values())),
}
K.jdump("STAGE5B_R1C_AUTHORISED_WEIGHT_REGION.json", AUTH_J, OUT)
K.jdump("STAGE5B_R1C_PROTECTED_WEIGHT_DRIFT_AUDIT.json", DRIFT_AUDIT, OUT)
K.jdump("STAGE5B_R1C_FIRST_WEB_PROTECTION_AUDIT.json", FW, OUT)

# weight delta audit
WD = {"stage": "STAGE5B_R1C_WEIGHT_DELTA_AUDIT", "generated_at": NOW,
      "baseline": {"path": K.R1B_MASTER.replace("\\", "/"), "sha256": K.R1B_SHA256},
      "candidate": {"path": CAND.replace("\\", "/"), "sha256": s1},
      "changed_vertex_count": len(CHANGED),
      "rows": [{"vertex": i, "corrected_ownership": CORR[i], "own_r1a": own[i],
                "before": dict((g, K.rr(v, 9)) for g, v in sorted(WOLD[i].items())),
                "after": dict((g, K.rr(v, 9)) for g, v in sorted(W2[i].items())),
                "verdict_before": VERDICT[i],
                "incident_CLASS_B_edges": sorted(k for k, a, b in probe["CLASS_B"]
                                                 if a == i or b == i)} for i in CHANGED]}
K.jdump("STAGE5B_R1C_WEIGHT_DELTA_AUDIT.json", WD, OUT)

s0_after = K.sha256(K.R1B_MASTER)
STATUS = {
    "stage": "STAGE5B_R1C_LOCAL_WEIGHT_RECONCILIATION",
    "generated_at": NOW,
    "status": "CANDIDATE_FOR_HUMAN_REVIEW",
    "current_frozen_production_master": {
        "path": K.R1B_MASTER.replace("\\", "/"), "sha256": K.R1B_SHA256,
        "unchanged_after": s0_after == K.R1B_SHA256},
    "candidate": {"path": CAND.replace("\\", "/"), "sha256": s1,
                  "bytes": os.path.getsize(CAND)},
    "trigger": ("WEIGHT_RECONCILIATION_REQUIRED > 0 after DIGIT_OWNERSHIP_AUTHORITY_R2 "
                "(Stage6B R1B ownership audit)"),
    "changed_weight_vertice_count": len(CHANGED),
    "authorised_region_count": len(AUTH),
    "gates": GATES,
    "drift": DRIFT_AUDIT,
    "first_web": FW,
    "stage5b_r1b_remains_master_until_human_approval": True,
    "log": LOG[-60:],
}
K.jdump("STAGE5B_R1C_STATUS.json", STATUS, OUT)

md = ["# STAGE5B R1C -- LOCAL WEIGHT RECONCILIATION", "",
      "Status: **CANDIDATE_FOR_HUMAN_REVIEW**  ",
      "Generated: `%s`  " % NOW, "",
      "## 1. Trigger", "",
      "`STAGE6B_R1B_DIGIT_OWNERSHIP_CORRECTION_AUDIT` reported",
      "`WEIGHT_RECONCILIATION_REQUIRED = %d` on the R2 correction domain, therefore the" % len(REQ_ALL),
      "round's branch rule §9 authorises a new Stage5B candidate.", "",
      "## 2. Inputs / outputs", "",
      "| role | path | sha256 |", "|---|---|---|",
      "| input (frozen) | `%s` | `%s` |" % (K.R1B_MASTER.replace("\\", "/"), K.R1B_SHA256),
      "| output (candidate) | `%s` | `%s` |" % (CAND.replace("\\", "/"), s1), "",
      "## 3. Authorised region", "",
      "primary (WEIGHT_RECONCILIATION_REQUIRED) = **%d**, 1-ring additions = **%d**, 2-ring additions = **%d**, final authorised = **%d**, actually reweighted = **%d**."
      % (len(primary), len(ring1), len(ring2), len(AUTH), len(CHANGED)), "",
      "FIRST_WEB-protected vertices kept as Dirichlet anchors: **%d**." % len(FW_EXCLUDED), "",
      "## 4. Method", "",
      "The existing Stage5B parametric authority cannot describe an INDEX-owned vertex",
      "(Stage5B never authored index weights: those are automatic proximity bind weights), so the",
      "round uses the fallback explicitly authorised by the round spec §13/§14: a deterministic",
      "**same-digit trusted-neighbour constrained interpolation** with the frozen vertices outside",
      "the authorised region as Dirichlet anchors. No per-vertex free parameter exists.", "",
      "## 5. Hard gates", ""]
for k, v in GATES.items():
    md.append("- `%s` = `%s`" % (k, v))
md += ["", "## 6. Drift", "",
       "- `OUTSIDE_AUTHORISED_WEIGHT_DRIFT` = `%s`" % DRIFT_AUDIT["OUTSIDE_AUTHORISED_WEIGHT_DRIFT"],
       "- `MIDDLE_RING_LITTLE_DRIFT` = `%s`" % DRIFT_AUDIT["MIDDLE_RING_LITTLE_DRIFT"],
       "- `UNAFFECTED_INDEX_REGION_DRIFT` = `%s`" % DRIFT_AUDIT["UNAFFECTED_INDEX_REGION_DRIFT"],
       "- `CMC_CAGE_PROTECTED_DRIFT` = `%s`" % DRIFT_AUDIT["CMC_CAGE_PROTECTED_DRIFT"], "",
       "## 7. Freeze rule", "",
       "Stage5B R1B remains `CURRENT_FROZEN_PRODUCTION_MASTER` until Human Review approves R1C.",
       ""]
open(os.path.join(OUT, "STAGE5B_R1C_REPORT.md"), "w", encoding="utf-8").write("\n".join(md))
log("wrote STAGE5B_R1C_REPORT.md")

if s0_after != K.R1B_SHA256:
    raise SystemExit("FAIL CLOSED: Stage5B R1B master changed during the round")
print("R1C_BUILD_DONE")
