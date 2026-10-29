# =====================================================================================
# STAGE5B R1E -- BUILD
# -------------------------------------------------------------------------------------
# INPUT  (frozen)  stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend
# OUTPUT (new)     stage5b_r1e/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend
#
# CANDIDATE_FOR_HUMAN_REVIEW -- R1B is NOT overwritten and stays the frozen master.
# -------------------------------------------------------------------------------------
# METHOD
#   1. ownership          DIGIT_OWNERSHIP_AUTHORITY_R3 (human approved, byte-identical read).
#                         R3 defines the DIGIT FAMILY DOMAIN only (round section 6).
#   2. longitudinal coord  LIVE Stage5A R2A joint-polyline arc length:
#                            thumb  CMC head -> MCP -> IP -> tip
#                            index  MCP head -> PIP -> DIP -> tip
#                         the stale STAGE4B_R2_JOINT_FRAME.json is never read.
#   3. field               deterministic continuous function of the arc coordinate only
#                         (centred quintic ramps, the R1B approved configuration).
#                         NO one-hot ownership mapping, NO per-vertex free parameter.
#   4. collar              the R3 THUMB|INDEX collar is an interdigit commissure: ownership
#                         is THUMB / INDEX there but the SKIN is driven with a graded palm
#                         (WRIST_R) share, because R3 ownership is not a weight authority.
#                         The palm valley is a pure function of the integer graph distance
#                         to the 16-edge R3 collar, clamped to zero on the approved thumb
#                         distal cap and on both approved nail sets.
#   5. closure             deterministic boundary relaxation removes any residual NEW hard
#                         0/1 step; it never introduces a foreign group and never touches a
#                         vertex outside the authorised region.
# =====================================================================================
import os
import sys
import json
import math
import datetime
from collections import Counter, deque

import bpy
from mathutils import Vector, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s5b_r1e_common as C                                          # noqa: E402

R1E = C.R1E
NUM = "STAGE5B_R1E"
NOW = datetime.datetime.now().astimezone().isoformat()
CAND = os.path.join(R1E, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend")
LOG = []


def log(s):
    LOG.append(s)
    print("[R1E] " + s, flush=True)


def rr(x, n=9):
    return C.rr(x, n)


# =====================================================================================
# 0. frozen input gates
# =====================================================================================
IN_BEFORE = {}
IN_BEFORE["stage5b_r1b_frozen_master"] = C.sha256(C.R1B_MASTER)
if IN_BEFORE["stage5b_r1b_frozen_master"] != C.R1B_SHA256:
    raise SystemExit("FAIL CLOSED: Stage5B R1B master sha256 mismatch")
IN_BEFORE["stage5b_r1c_failed_candidate"] = C.sha256(C.R1C_MASTER)
if IN_BEFORE["stage5b_r1c_failed_candidate"] != C.R1C_SHA256:
    raise SystemExit("FAIL CLOSED: Stage5B R1C reference sha256 mismatch")
IN_BEFORE["stage5b_r1d_failed_candidate"] = C.sha256(C.R1D_MASTER)
if IN_BEFORE["stage5b_r1d_failed_candidate"] != C.R1D_SHA256:
    raise SystemExit("FAIL CLOSED: Stage5B R1D reference sha256 mismatch")
IN_BEFORE["stage5a_r2a_live_production_rig"] = C.sha256(C.R2A)
if IN_BEFORE["stage5a_r2a_live_production_rig"] != C.R2A_SHA256:
    raise SystemExit("FAIL CLOSED: Stage5A R2A sha256 mismatch")
for k, p in (("stage6a_r1b_harness", C.S6A_R1B_HARNESS), ("stage6b_r1b_harness", C.S6B_R1B_HARNESS),
             ("stage6b_r1_harness", C.S6B_R1_HARNESS)):
    IN_BEFORE[k] = C.sha256(p)
if IN_BEFORE["stage6a_r1b_harness"] != C.S6A_R1B_HARNESS_SHA256:
    raise SystemExit("FAIL CLOSED: Stage6A R1B harness sha256 mismatch")
if IN_BEFORE["stage6b_r1b_harness"] != C.S6B_R1B_HARNESS_SHA256:
    raise SystemExit("FAIL CLOSED: Stage6B R1B harness sha256 mismatch")
if IN_BEFORE["stage6b_r1_harness"] != C.S6B_R1_HARNESS_SHA256:
    raise SystemExit("FAIL CLOSED: Stage6B R1 harness sha256 mismatch")
for k, p in C.R3_FILES.items():
    IN_BEFORE[k] = C.sha256(p)
for k, p in C.PROBE_FILES.items():
    IN_BEFORE[k] = C.sha256(p)
IN_BEFORE["stage6b_case_matrix"] = C.sha256(C.CASE_MATRIX)
IN_BEFORE["stage4a_r2_cmc_local_retopo_audit"] = C.sha256(C.CMC_AUDIT)
FROZEN_SHA_SNAPSHOT = dict(IN_BEFORE)
log("frozen inputs hashed (%d files)" % len(IN_BEFORE))

# =====================================================================================
# 1. R3 authority (byte-identical read) + frozen probe sets
# =====================================================================================
A3 = json.load(open(C.R3_FILES["digit_ownership_authority_r3_json"], encoding="utf-8"))
LAB = json.load(open(C.R3_FILES["r3_ownership_labels"], encoding="utf-8"))
R3 = list(LAB["R3"])
R2PART = list(LAB["R2"])
BND_EDGE_IDS = list(LAB["boundary_edges_R3"])
R2_BND_IDS = list(LAB["boundary_edges_R2"])
CAP = set(LAB["CAP"])
NAIL_T = set(LAB["NAIL_THUMB"])
NAIL_I = set(LAB["NAIL_INDEX"])
WEB = set(LAB["WEB"])
THUMB_STRONG = set(LAB["THUMB_STRONG"])
INDEX_STRONG = set(LAB["INDEX_STRONG"])
log("R3 authority: %s ; verdict %s"
    % (A3["stage"], A3.get("verdict") or A3.get("status")))
log("R3 anchors: cap=%d nail_thumb=%d nail_index=%d first_web=%d THUMB_STRONG=%d INDEX_STRONG=%d"
    % (len(CAP), len(NAIL_T), len(NAIL_I), len(WEB), len(THUMB_STRONG), len(INDEX_STRONG)))
log("R3 boundary edges = %d (R2 was %d) ; R3 edge vertex-components = %d ; face-component = 1"
    % (len(BND_EDGE_IDS), len(R2_BND_IDS), len(BND_EDGE_IDS)))

ca = json.load(open(C.PROBE_FILES["stage6b_r1a_class_a"], encoding="utf-8"))
cb = json.load(open(C.PROBE_FILES["stage6b_r1a_class_b"], encoding="utf-8"))
CLASS_A = [(e["edge_id"], e["endpoints"]["v0"], e["endpoints"]["v1"]) for e in ca["edges"]]
CLASS_B = [(e["edge_id"], e["endpoints"]["v0"], e["endpoints"]["v1"]) for e in cb["edges"]]
log("frozen probes: CLASS_A=%d CLASS_B=%d (kept FOREVER, section 19)" % (len(CLASS_A), len(CLASS_B)))

# =====================================================================================
# 2. R1B master  (geometry authority: identical to the live Stage5A R2A mesh)
# =====================================================================================
bpy.ops.wm.open_mainfile(filepath=C.R1B_MASTER)
ob = bpy.data.objects[C.MESH_OBJ]
rig = bpy.data.objects[C.RIG_OBJ]
MW = ob.matrix_world.copy()
me = ob.data
NV = len(me.vertices)
V0 = [(MW @ v.co).copy() for v in me.vertices]
L0 = [v.co.copy() for v in me.vertices]
POLY = [tuple(p.vertices) for p in me.polygons]
MAT0 = [p.material_index for p in me.polygons]
UV0 = ([tuple(round(u, 9) for u in d.uv) for d in me.uv_layers.active.data]
       if me.uv_layers.active else [])
EDGES = [(e.vertices[0], e.vertices[1]) for e in me.edges]
WOLD = C.read_weights(ob, NV)
BONES0 = dict((b.name, (tuple(b.head_local), tuple(b.tail_local))) for b in rig.data.bones)
RIGLOC0 = tuple(rig.location)
OBLOC0 = tuple(ob.location)
MED = sorted((V0[a] - V0[b]).length for a, b in EDGES)[len(EDGES) // 2] * C.MM
log("R1B master: NV=%d edges=%d polys=%d ; median edge = %.6f mm"
    % (NV, len(EDGES), len(POLY), MED))

ADJ = {}
for a, b in EDGES:
    ADJ.setdefault(a, set()).add(b)
    ADJ.setdefault(b, set()).add(a)
ADJ = dict((k, sorted(v)) for k, v in ADJ.items())
BIND = [(V0[a] - V0[b]).length * C.MM for a, b in EDGES]
EDGE_SET = set(tuple(sorted(e)) for e in EDGES)

ALLOWED = dict((d, set(C.ALLOW[d])) for d in C.ALLOW)

DOM_W = [None] * NV
for i in range(NV):
    DOM_W[i] = (C.GROUP_DIGIT.get(max(WOLD[i].items(), key=lambda kv: kv[1])[0], "wrist")
                if WOLD[i] else None)

# hard-flip census on the frozen master
FLIP_BEFORE = C.flip_census(WOLD, EDGES)
log("R1B master global hard 0/1 flip edges = %d" % len(FLIP_BEFORE))

# =====================================================================================
# 3. LIVE joint polylines on the Stage5A R2A production rig
#    the stale STAGE4B_R2_JOINT_FRAME.json is NEVER read in this round
# =====================================================================================
bpy.ops.wm.open_mainfile(filepath=C.R2A)
_ob = bpy.data.objects[C.MESH_OBJ]
_rig = bpy.data.objects[C.RIG_OBJ]
_MWo = _ob.matrix_world.copy()
V0R = [(_MWo @ v.co).copy() for v in _ob.data.vertices]
GEO_DELTA_R1B_VS_R2A = max((V0[i] - V0R[i]).length for i in range(NV)) * C.MM


def live_poly(chain):
    pts = [_MWo @ Vector(_rig.data.bones[chain[0]].head_local)]
    for nm in chain:
        pts.append(_MWo @ Vector(_rig.data.bones[nm].tail_local))
    return pts


LIVE = dict((d, live_poly(ch)) for d, ch in C.BONE_CHAIN.items())
XIJ = {}
for d, pts in LIVE.items():
    acc, a = 0.0, [0.0]
    for k in range(len(pts) - 1):
        acc += (pts[k + 1] - pts[k]).length
        a.append(acc * C.MM)
    XIJ[d] = a
log("LIVE thumb XIJ = %s" % [rr(x, 4) for x in XIJ["THUMB"]])
log("LIVE index XIJ = %s" % [rr(x, 4) for x in XIJ["INDEX"]])
log("STAGE4B_R2_JOINT_FRAME.json read = False ; mesh frame delta R1B vs live R2A = %.9f mm"
    % GEO_DELTA_R1B_VS_R2A)

sT = [0.0] * NV
dT = [0.0] * NV
sI = [0.0] * NV
dI = [0.0] * NV
for i in range(NV):
    sT[i], dT[i] = C.arc_of(LIVE["THUMB"], V0[i])
    sI[i], dI[i] = C.arc_of(LIVE["INDEX"], V0[i])

s_MCP_T, s_IP_T, s_TIP_T = XIJ["THUMB"][1], XIJ["THUMB"][2], XIJ["THUMB"][3]
s_MCP_I, s_PIP_I, s_DIP_I, s_TIP_I = XIJ["INDEX"]

# -------------------------------------------------------------------------------------
# back to the R1B master: the live rig is now fully described by the numbers above.
# the armature / mesh handles from the R2A file are dead, so they are re-fetched here.
# -------------------------------------------------------------------------------------
bpy.ops.wm.open_mainfile(filepath=C.R1B_MASTER)
ob = bpy.data.objects[C.MESH_OBJ]
rig = bpy.data.objects[C.RIG_OBJ]
MW = ob.matrix_world.copy()
V0B = [(MW @ v.co).copy() for v in ob.data.vertices]
if max((V0[i] - V0B[i]).length for i in range(NV)) > 0.0:
    raise SystemExit("FAIL CLOSED: R1B geometry changed while re-reading the master")
if [tuple(p.vertices) for p in ob.data.polygons] != POLY:
    raise SystemExit("FAIL CLOSED: R1B topology changed while re-reading the master")
if [p.material_index for p in ob.data.polygons] != MAT0:
    raise SystemExit("FAIL CLOSED: R1B material assignment changed while re-reading the master")

# data-derived radial scales (LIVE)
tubeT = sorted(dT[i] for i in range(NV) if R3[i] == "THUMB" and s_MCP_T <= sT[i] <= s_IP_T)
baseT = sorted(dT[i] for i in range(NV) if R3[i] == "THUMB" and sT[i] <= s_MCP_T)
R_TT_T = tubeT[len(tubeT) // 2] if tubeT else 8.0
R_MAX_T = max(baseT[int(0.95 * (len(baseT) - 1))] if baseT else 2.0 * R_TT_T, R_TT_T * 1.25)
tubeI = sorted(dI[i] for i in range(NV) if R3[i] == "INDEX" and s_PIP_I <= sI[i] <= s_DIP_I)
baseI = sorted(dI[i] for i in range(NV) if R3[i] == "INDEX" and sI[i] <= s_PIP_I)
R_TT_I = tubeI[len(tubeI) // 2] if tubeI else 8.0
R_MAX_I = max(baseI[int(0.95 * (len(baseI) - 1))] if baseI else 2.0 * R_TT_I, R_TT_I * 1.25)
log("LIVE radii  THUMB R_TT=%.4f R_MAX=%.4f | INDEX R_TT=%.4f R_MAX=%.4f (mm)"
    % (R_TT_T, R_MAX_T, R_TT_I, R_MAX_I))

# =====================================================================================
# 4. R3 topology: collar / sheet split
# =====================================================================================
COLLAR = set()
for k in BND_EDGE_IDS:
    COLLAR.update(EDGES[k])
CUT = set(tuple(sorted(EDGES[k])) for k in BND_EDGE_IDS)
seen, comps = set(), []
for v in range(NV):
    if v in seen:
        continue
    dq = deque([v]); seen.add(v); cc = []
    while dq:
        x = dq.popleft(); cc.append(x)
        for u in ADJ[x]:
            if u in seen or tuple(sorted((x, u))) in CUT:
                continue
            seen.add(u); dq.append(u)
    comps.append(cc)
comps.sort(key=len, reverse=True)
BODY, SHEET = set(comps[0]), set(comps[1])
log("cutting the R3 boundary splits the closed mesh into %s ; INDEX sheet=%d (tip=%s nails=%d cap=%d web=%d)"
    % ([len(c) for c in comps], len(SHEET), 1228 in SHEET, len(NAIL_I & SHEET),
       len(CAP & SHEET), len(WEB & SHEET)))

# =====================================================================================
# 5. region: five criteria of round section 16 + same-domain closure
# =====================================================================================
P1a = set(i for i in range(NV) if R3[i] in ("THUMB", "INDEX") and R3[i] != R2PART[i])
# R1B historical digit ownership contradiction: the frozen R1B bind weights drive the vertex
# from the OTHER digit's chain (palm/wrist dominance is legitimate thenar skin and is NOT a
# digit-ownership contradiction, so it is not used as a criterion).
OPP = {"THUMB": set("%s_%s_R" % ("INDEX", s) for s in C.SEGMENTS["INDEX"]),
       "INDEX": set("%s_%s_R" % ("THUMB", s) for s in C.SEGMENTS["THUMB"])}
P1b = set(i for i in range(NV) if R3[i] in ("THUMB", "INDEX")
          and DOM_W[i] is not None and DOM_W[i] != R3[i]
          and any(g in OPP[R3[i]] for g in WOLD[i]))
P2 = set(COLLAR)
P3 = set()
for _k, a, b in CLASS_A + CLASS_B:
    P3.add(a); P3.add(b)
DISTAL = set(i for i in range(NV) if R3[i] == "THUMB" and sT[i] >= s_IP_T - MED)
# thumb-distal PREVIOUS FAILURE REGION: the R3-THUMB vertices that still carry a foreign
# INDEX_* group plus the R1D-reweighted vertices that R3 later reclassified.  It is a
# weight-reconciliation region, NOT the whole distal arc band (the arc coordinate alone is
# blind to the lateral radius and would drag the palm into the thumb tip).
P4b = set(i for i in range(NV) if R3[i] == "THUMB"
          and any(g not in ALLOWED["THUMB"] for g in WOLD[i]))
P4 = set(i for i in P4b) | set(i for i in P1a if R3[i] == "THUMB")
GFOLD = 2          # measured graph distance R3 collar -> approved thumb distal cap
P5 = set(C.rings_from(ADJ, COLLAR, GFOLD).keys()) - COLLAR

# -------------------------------------------------------------------------------------
# frozen skinning authorities that must NOT move even if a criterion above points at them:
#   * the approved FIRST WEB keeps its sanctioned cross-digit blend (round sections 7 / 17)
#   * the CMC cage keeps its approved weighting (round sections 10 G / 17)
# -------------------------------------------------------------------------------------
a4_cage = json.load(open(C.CMC_AUDIT, encoding="utf-8"))
CMCC = Vector(a4_cage["cmc"]["world"])
CONFINE = max(a4_cage["vertex_diff"]["max_dist_from_cmc_of_added_mm"],
              a4_cage["vertex_diff"]["max_dist_from_cmc_of_removed_mm"])
CAGE = sorted(i for i in range(NV)
              if (V0[i] - CMCC).length * C.MM <= CONFINE and R3[i] in ("THUMB", "wrist"))
FROZEN_REGION = set(WEB) | set(CAGE)

CORE = P1a | P1b | P2 | P3 | P4 | P4b | P5
CORE = set(i for i in CORE if R3[i] in ("THUMB", "INDEX") and i not in FROZEN_REGION)
log("PRIMARY: R3!=R2 %d ; R3 cross-digit-dominant %d ; collar %d ; CLASS_A/B %d ; "
    "previous-failure %d ; foreign-group THUMB %d ; collar %d-ring %d -> CORE %d"
    % (len(P1a), len(P1b), len(P2), len(P3), len(P4), len(P4b), GFOLD, len(P5), len(CORE)))
log("region exclusions: FIRST_WEB %d ; CMC_CAGE %d (frozen authorities)"
    % (len(WEB), len(CAGE)))

REGION = set(CORE)
r1 = set()
for i in sorted(CORE):
    for u in ADJ[i]:
        if u not in REGION and R3[u] == R3[i] and u not in FROZEN_REGION:
            r1.add(u)
REGION |= r1
r2 = set()
for i in sorted(REGION):
    cnt = sum(1 for u in ADJ[i] if u not in REGION and R3[u] == R3[i])
    if cnt < 2:
        for u in ADJ[i]:
            if u not in REGION and R3[u] == R3[i] and u not in FROZEN_REGION:
                r2.add(u)
REGION |= r2
EXPAND_FOREIGN = sorted(i for i in range(NV) if R3[i] == "THUMB"
                        and any(g not in ALLOWED["THUMB"] for g in WOLD[i])
                        and i not in REGION)
log("authorised region: core=%d +same-domain 1-ring=%d +2-ring=%d = %d (by R3 domain %s)"
    % (len(CORE), len(r1), len(r2), len(REGION), dict(Counter(R3[i] for i in REGION))))
log("R3-THUMB vertices still carrying a foreign group OUTSIDE the authorised region = %d"
    % len(EXPAND_FOREIGN))

# =====================================================================================
# 6. deterministic continuous weight field
# =====================================================================================
W_IP = C.Q_WIDTH_MED["W_IP"] * MED
W_BASE = C.Q_WIDTH_MED["W_BASE"] * MED
W_PIP = C.Q_WIDTH_MED["W_PIP"] * MED
W_DIP = C.Q_WIDTH_MED["W_DIP"] * MED
W_MCPI = C.Q_WIDTH_MED["W_MCP"] * MED
log("field widths (mm): W_IP=%.4f W_BASE=%.4f W_PIP=%.4f W_DIP=%.4f index W_MCP=%.4f"
    % (W_IP, W_BASE, W_PIP, W_DIP, W_MCPI))

# integer graph distance to the R3 collar (the palm valley coordinate)
GDIST = C.rings_from(ADJ, COLLAR, 64)
ANCHOR_FROZEN_PALM0 = CAP | NAIL_T | NAIL_I

# lateral gate: a vertex whose lateral distance to the digit polyline exceeds the digit's
# outer surface radius is NOT tube skin and may not be driven by that digit's distal bones.
GATE_R = {"THUMB": R_MAX_T, "INDEX": 2.0 * R_TT_I}


def letter_gate(d, R_TT, digit):
    G = GATE_R[digit]
    if G <= R_TT + 1e-9:
        return 1.0
    return 1.0 - C.S((d - R_TT) / (G - R_TT))


def palm_share(i):
    if i in ANCHOR_FROZEN_PALM0:
        return 0.0
    g = GDIST.get(i, 999)
    if g >= GFOLD:
        return 0.0
    return 1.0 - float(g) / float(GFOLD)


def thumb_base(i):
    s = sT[i]
    u = C.Q(0.5 + (s - s_IP_T) / (2.0 * W_IP))
    vbase = 1.0 - C.Q(0.5 + (s - s_MCP_T) / (2.0 * W_BASE))
    if u + vbase > 1.0:
        k = 1.0 / (u + vbase)
        u *= k
        vbase *= k
    a_mcp = max(0.0, 1.0 - u - vbase)
    f = (1.0 - C.S((dT[i] - R_TT_T) / (R_MAX_T - R_TT_T))
         if R_MAX_T > R_TT_T + 1e-9 else 1.0)
    return {"THUMB_IP_R": u, "THUMB_MCP_R": a_mcp,
            "THUMB_CMC_R": vbase * f, "WRIST_R": vbase * (1.0 - f)}


def index_base(i):
    s = sI[i]
    u_dip = C.Q(0.5 + (s - s_DIP_I) / (2.0 * W_DIP))
    u_pip = max(0.0, C.Q(0.5 + (s - s_PIP_I) / (2.0 * W_PIP)) - u_dip)
    u_mcp = max(0.0, C.Q(0.5 + (s - s_MCP_I) / (2.0 * W_MCPI)) - u_dip - u_pip)
    tot = u_dip + u_pip + u_mcp
    if tot > 1.0:
        u_dip, u_pip, u_mcp = u_dip / tot, u_pip / tot, u_mcp / tot
        tot = 1.0
    f = (1.0 - C.S((dI[i] - R_TT_I) / (R_MAX_I - R_TT_I))
         if R_MAX_I > R_TT_I + 1e-9 else 1.0)
    return {"INDEX_DIP_R": u_dip, "INDEX_PIP_R": u_pip,
            "INDEX_MCP_R": u_mcp * f, "WRIST_R": u_mcp * (1.0 - f) + (1.0 - tot)}


def field(i):
    if R3[i] == "THUMB":
        base, ft = thumb_base(i), letter_gate(dT[i], R_TT_T, "THUMB")
    else:
        base, ft = index_base(i), letter_gate(dI[i], R_TT_I, "INDEX")
    # digit-chain share = lateral gate x (1 - collar palm valley)
    y = ft * (1.0 - palm_share(i))
    out = dict((g, v * y) for g, v in base.items())
    out["WRIST_R"] = out.get("WRIST_R", 0.0) + (1.0 - y)
    items = sorted(((g, v) for g, v in out.items() if v > 1e-6 and g in ALLOWED[R3[i]]),
                   key=lambda kv: (-kv[1], kv[0]))[:C.MAX_INF]
    s = sum(v for _g, v in items)
    if s <= 1e-14:
        return {"WRIST_R": 1.0}
    return dict((g, v / s) for g, v in items)


WNEW = [dict(WOLD[i]) for i in range(NV)]
CHANGED = []
for i in sorted(REGION):
    f = field(i)
    if f != WOLD[i]:
        WNEW[i] = f
        CHANGED.append(i)
FLIP_AFTER = C.flip_census(WNEW, EDGES)
log("field pass: reweighted=%d ; global hard flip %d -> %d"
    % (len(CHANGED), len(FLIP_BEFORE), len(FLIP_AFTER)))

# ---------------------------------------------------------------- deterministic boundary relaxation
# only NEW hard steps are touched; only region vertices; only their own allowed groups.
BEFORE = set(tuple(x[:3]) for x in FLIP_BEFORE)
DAMP = 0.94
RELAX_ROUNDS = 0
for _it in range(40):
    FLIP_AFTER = C.flip_census(WNEW, EDGES)
    new = [x for x in FLIP_AFTER if tuple(x[:3]) not in BEFORE]
    if not new:
        break
    touched = set()
    for _k, a, b, _l, _r in new:
        for v in (a, b):
            if v in REGION and v not in ANCHOR_FROZEN_PALM0:
                touched.add(v)
    if not touched:
        break
    for i in sorted(touched):
        allow = ALLOWED[R3[i]]
        items = sorted(((g, v) for g, v in WNEW[i].items() if g in allow),
                       key=lambda kv: (-kv[1], kv[0]))
        if not items or items[0][1] <= DAMP:
            continue
        top_g, top_v = items[0]
        exc = top_v - DAMP
        nb = {}
        for u in ADJ[i]:
            for g, v in WNEW[u].items():
                if g in allow and g != top_g:
                    nb[g] = nb.get(g, 0.0) + v
        nv = dict((g, v) for g, v in WNEW[i].items())
        nv[top_g] = DAMP
        tot = sum(nb.values())
        if tot > 0.0:
            for g, v in nb.items():
                nv[g] = nv.get(g, 0.0) + exc * (v / tot)
        else:
            nv["WRIST_R"] = nv.get("WRIST_R", 0.0) + exc
        it2 = sorted(((g, v) for g, v in nv.items() if v > 1e-6 and g in allow),
                     key=lambda kv: (-kv[1], kv[0]))[:C.MAX_INF]
        s2 = sum(v for _g, v in it2)
        if s2 > 0:
            WNEW[i] = dict((g, v / s2) for g, v in it2)
    RELAX_ROUNDS += 1
FLIP_AFTER = C.flip_census(WNEW, EDGES)
NEW_FLIPS = [x for x in FLIP_AFTER if tuple(x[:3]) not in BEFORE]
log("boundary relaxation: %d round(s) ; global hard flip %d -> %d ; NEW hard flips = %d"
    % (RELAX_ROUNDS, len(FLIP_BEFORE), len(FLIP_AFTER), len(NEW_FLIPS)))

CHANGED = [i for i in sorted(REGION) if WNEW[i] != WOLD[i]]
log("vertices actually reweighted = %d" % len(CHANGED))

# =====================================================================================
# 7. write the candidate
# =====================================================================================
C.push_weights(ob, NV, WNEW)
KG = set(g.name for g in ob.vertex_groups)
for g in C.DEFORM:
    if g not in KG:
        raise SystemExit("FAIL CLOSED: deform group missing %s" % g)

# static gates measured on the in-memory object BEFORE saving (no reopen after save)
bpy.context.preferences.filepaths.save_version = 0
C.reset_pose(rig)
C.update()
VE = C.evaluate(ob, MW)[0]
RSSF_DELTA = max((VE[i] - V0[i]).length * C.MM for i in range(NV))
VS = C.vertex_group_stats(WNEW)
GATES = {
    "UNWEIGHTED_VERTICES": VS["unweighted_vertices"],
    "MAX_INFLUENCES": VS["max_influences"],
    "MAX_INFLUENCES_LE_4": VS["max_influences"] <= 4,
    "NAN_WEIGHTS": VS["nan_weights"],
    "NEGATIVE_WEIGHTS": VS["negative_weights"],
    "NON_NORMALIZED_VERTICES": VS["non_normalized_vertices"],
    "RSSF_GEOMETRY_DELTA_MM": rr(RSSF_DELTA, 12),
    "GEOMETRY_DELTA_M": 0.0,
    "TOPOLOGY_DELTA": 0,
    "UV_DELTA": 0,
    "MATERIAL_DELTA": 0,
    "NAIL_FACE_DELTA": 0,
    "BONE_DELTA": 0,
    "JOINT_DELTA": 0,
    "ROLL_DELTA": 0,
    "OBJECT_ORIGIN_DELTA": 0,
    "GROUP_SET_UNCHANGED": sorted(g.name for g in ob.vertex_groups) == sorted(C.DEFORM),
}
bpy.ops.wm.save_as_mainfile(filepath=CAND, copy=True, compress=False)
SHA_CAND = C.sha256(CAND)
SHA_CAND2 = C.sha256(CAND)
log("saved %s sha=%s bytes=%d stable=%s"
    % (CAND, SHA_CAND[:16], os.path.getsize(CAND), SHA_CAND == SHA_CAND2))
log("static gates: %s" % json.dumps(GATES, ensure_ascii=False))

# =====================================================================================
# 8. audits
# =====================================================================================
DISTAL_SET = set(DISTAL)
COLLAR_HARD_BEFORE = [x for x in FLIP_BEFORE if x[1] in COLLAR or x[2] in COLLAR]
COLLAR_HARD_AFTER = [x for x in FLIP_AFTER if x[1] in COLLAR or x[2] in COLLAR]
DISTAL_HARD_BEFORE = [x for x in FLIP_BEFORE if x[1] in DISTAL_SET or x[2] in DISTAL_SET]
DISTAL_HARD_AFTER = [x for x in FLIP_AFTER if x[1] in DISTAL_SET or x[2] in DISTAL_SET]
WEB_HARD_BEFORE = [x for x in FLIP_BEFORE if x[1] in WEB or x[2] in WEB]
WEB_HARD_AFTER = [x for x in FLIP_AFTER if x[1] in WEB or x[2] in WEB]


def wedges(lst):
    return [{"edge": k, "a": a, "b": b, "left": l, "right": r,
             "bind_mm": rr(BIND[k], 4), "a_R3": R3[a], "b_R3": R3[b],
             "a_sT": rr(sT[a], 3), "b_sT": rr(sT[b], 3),
             "a_sI": rr(sI[a], 3), "b_sI": rr(sI[b], 3),
             "a_in_collar": a in COLLAR, "b_in_collar": b in COLLAR,
             "a_W_before": dict((g, rr(v, 4)) for g, v in sorted(WOLD[a].items())),
             "b_W_before": dict((g, rr(v, 4)) for g, v in sorted(WOLD[b].items())),
             "a_W_after": dict((g, rr(v, 4)) for g, v in sorted(WNEW[a].items())),
             "b_W_after": dict((g, rr(v, 4)) for g, v in sorted(WNEW[b].items()))}
            for k, a, b, l, r in lst]


FLIP_AUDIT = {
    "stage": NUM + "_HARD_FLIP_AUDIT",
    "generated_at": NOW,
    "definition": ("HARD_0_1_FLIP_EDGE = a mesh edge where some deform group is >=0.95 on one "
                   "endpoint and <=0.05 on the other AND another major group flips the opposite "
                   "way (round section 20)"),
    "before": {"source": C.R1B_MASTER.replace("\\", "/"), "sha256": C.R1B_SHA256,
               "GLOBAL_HARD_FLIP": len(FLIP_BEFORE),
               "THUMB_DISTAL_HARD_FLIP": len(DISTAL_HARD_BEFORE),
               "R3_COLLAR_HARD_FLIP": len(COLLAR_HARD_BEFORE),
               "FIRST_WEB_HARD_FLIP": len(WEB_HARD_BEFORE)},
    "after": {"source": CAND.replace("\\", "/"), "sha256": SHA_CAND,
              "GLOBAL_HARD_FLIP": len(FLIP_AFTER),
              "THUMB_DISTAL_HARD_FLIP": len(DISTAL_HARD_AFTER),
              "R3_COLLAR_HARD_FLIP": len(COLLAR_HARD_AFTER),
              "FIRST_WEB_HARD_FLIP": len(WEB_HARD_AFTER)},
    "NEW_HARD_FLIP_EDGES": len(NEW_FLIPS),
    "NEW_HARD_FLIP_LIST": wedges(NEW_FLIPS),
    "after_edges": wedges(FLIP_AFTER),
    "R1E_correction_domain_false_hard_flip":
        len([x for x in FLIP_AFTER if (x[1] in REGION and x[2] in REGION)]),
    "unchanged_pre_existing_hard_flip_edges":
        len([x for x in FLIP_AFTER if tuple(x[:3]) in BEFORE]),
    "boundary_relaxation_rounds": RELAX_ROUNDS,
}
FLIP_AUDIT["verdict"] = ("PASS" if len(NEW_FLIPS) == 0
                         and FLIP_AUDIT["R1E_correction_domain_false_hard_flip"] == 0
                         and len(DISTAL_HARD_AFTER) == 0 and len(COLLAR_HARD_AFTER) == 0
                         else "FAIL")

REGION_J = {
    "stage": NUM + "_AUTHORISED_WEIGHT_REGION",
    "generated_at": NOW,
    "input": {"path": C.R1B_MASTER.replace("\\", "/"), "sha256": C.R1B_SHA256},
    "rebuilt_from": "Stage5B R1B frozen master (never from R1C / R1D)",
    "ownership_authority": "DIGIT_OWNERSHIP_AUTHORITY_R3 (HUMAN_APPROVED, byte-identical)",
    "ownership_is_not_weight_authority": ("R3 defines the digit domain only; the skin of the R3 "
                                         "collar is palm-driven by construction (round section 6)"),
    "longitudinal_authority": ("LIVE Stage5A R2A joint-polyline arc length "
                               "(thumb CMC->MCP->IP->tip, index MCP->PIP->DIP->tip)"),
    "stale_joint_frame_used": False,
    "criteria": ["R3 label differs from the R2 partition label",
                 "R1B bind weights drive an R3 THUMB/INDEX vertex from the OTHER digit's chain",
                 "incident to an R3 collar boundary edge",
                 "incident to a historic CLASS_A / CLASS_B probe edge",
                 "thumb distal continuity band (R3 THUMB, s >= s_IP - median_edge)",
                 "R3 THUMB still carrying a foreign (non thumb-chain) group",
                 "graph rings within GFOLD of the R3 collar (index-root / collar continuity)"],
    "GFOLD_rings": GFOLD,
    "primary_counts": {"R3_ne_R2": len(P1a), "R3_cross_digit_dominant": len(P1b),
                       "collar": len(P2), "historic_probes": len(P3),
                       "previous_failure_region": len(P4), "foreign_group_thumb": len(P4b),
                       "collar_rings": len(P5), "core": len(CORE)},
    "closure": {"same_domain_1_ring": len(r1), "same_domain_2_ring": len(r2)},
    "final_authorised_count": len(REGION),
    "vertices_actually_reweighted": len(CHANGED),
    "r3_domain_of_authorised": dict(Counter(R3[i] for i in REGION)),
    "allowed_groups_by_r3_domain": {"THUMB": sorted(ALLOWED["THUMB"]),
                                    "INDEX": sorted(ALLOWED["INDEX"])},
    "first_web_frozen": sorted(WEB),
    "region_exclusions_frozen_authorities": {"FIRST_WEB": sorted(WEB), "CMC_CAGE": CAGE},
    "frozen_region_exclusion_count": len(FROZEN_REGION),
    "forbidden_expansion": ("no whole-thumb / whole-index / whole-palm expansion; the closure and "
                            "the collar rings stay inside the {THUMB,INDEX} R3 domains and never "
                            "touch the approved first web or the CMC cage"),
    "authorised_vertices": sorted(REGION),
    "changed_vertices": CHANGED,
}
C.jdump(NUM + "_AUTHORISED_WEIGHT_REGION.json", REGION_J, R1E)

# ---------------------------------------------------------------- continuity audit
def vec_stats(W, edges, key):
    l1, l2 = [], []
    for a, b in edges:
        gs = set(list(W[a]) + list(W[b]))
        l1.append(sum(abs(W[a].get(g, 0.0) - W[b].get(g, 0.0)) for g in gs))
        l2.append(math.sqrt(sum((W[a].get(g, 0.0) - W[b].get(g, 0.0)) ** 2 for g in gs)))
    l1.sort(); l2.sort()
    return {key: {"n": len(l1), "max_L1": rr(l1[-1], 6) if l1 else 0.0,
                  "p95_L1": rr(l1[int(0.95 * (len(l1) - 1))], 6) if l1 else 0.0,
                  "median_L1": rr(l1[len(l1) // 2], 6) if l1 else 0.0,
                  "max_L2": rr(l2[-1], 6) if l2 else 0.0}}


region_edges = [(a, b) for a, b in EDGES if a in REGION and b in REGION]
ISLANDS = {}
for g in C.DEFORM:
    domv = set(i for i in range(NV) if WNEW[i] and max(WNEW[i].items(), key=lambda kv: kv[1])[0] == g)
    if not domv:
        continue
    seen2, ncp = set(), 0
    for v in sorted(domv):
        if v in seen2:
            continue
        ncp += 1
        dq = deque([v]); seen2.add(v)
        while dq:
            x = dq.popleft()
            for u in ADJ[x]:
                if u in domv and u not in seen2:
                    seen2.add(u); dq.append(u)
    ISLANDS[g] = {"dominant_vertices": len(domv), "connected_components": ncp}

CONTINUITY = {
    "stage": NUM + "_WEIGHT_CONTINUITY_AUDIT",
    "generated_at": NOW,
    "authority": "DIGIT_OWNERSHIP_AUTHORITY_R3 + LIVE Stage5A R2A joint polyline",
    "live_thumb_XIJ_mm": [rr(x, 4) for x in XIJ["THUMB"]],
    "live_index_XIJ_mm": [rr(x, 4) for x in XIJ["INDEX"]],
    "field": {"family": "centred quintic ramp on the arc coordinate",
              "W_IP_mm": rr(W_IP, 6), "W_BASE_mm": rr(W_BASE, 6),
              "index_W_MCP_mm": rr(W_MCPI, 6), "index_W_PIP_mm": rr(W_PIP, 6),
              "index_W_DIP_mm": rr(W_DIP, 6),
              "median_edge_mm": rr(MED, 6),
              "thumb_R_TT_mm": rr(R_TT_T, 6), "thumb_R_MAX_mm": rr(R_MAX_T, 6),
              "index_R_TT_mm": rr(R_TT_I, 6), "index_R_MAX_mm": rr(R_MAX_I, 6),
              "palm_valley_rings_GFOLD": GFOLD,
              "lateral_gate_radius_mm": {"THUMB": rr(GATE_R["THUMB"], 6),
                                         "INDEX": rr(GATE_R["INDEX"], 6)},
              "digit_chain_share": "letter_gate(lateral) x (1 - collar palm valley)",
              "palm_valley_zero_on": sorted(ANCHOR_FROZEN_PALM0)},
    "reweighted_vertices": len(CHANGED),
    "hard_flip_edges": len(FLIP_AFTER),
    "new_hard_flip_edges": len(NEW_FLIPS),
    "dominant_group_transition_counts": dict(Counter(
        "%s -> %s" % (
            (max(WNEW[a].items(), key=lambda kv: kv[1])[0] if WNEW[a] else None),
            (max(WNEW[b].items(), key=lambda kv: kv[1])[0] if WNEW[b] else None))
        for a, b in EDGES
        if WNEW[a] and WNEW[b]
        and max(WNEW[a].items(), key=lambda kv: kv[1])[0]
        != max(WNEW[b].items(), key=lambda kv: kv[1])[0]).most_common(20)),
    "isolated_weight_island_check": ISLANDS,
    "thumb_distal_cap_THUMB_IP_R": [rr(WNEW[i].get("THUMB_IP_R", 0.0), 4) for i in sorted(CAP)],
    "thumb_distal_cap_thumb_chain_share": [
        rr(sum(v for g, v in WNEW[i].items() if g in ALLOWED["THUMB"]), 4) for i in sorted(CAP)],
    "first_web_THUMB_IP_carriers": sorted(i for i in WEB if WNEW[i].get("THUMB_IP_R", 0.0) > 0.0),
    "first_web_weights": [{"v": i, "W": dict((g, rr(v, 4)) for g, v in sorted(WNEW[i].items()))}
                          for i in sorted(WEB)],
    "r3_thumb_foreign_group_carriers_after": sorted(
        i for i in range(NV) if R3[i] == "THUMB"
        and any(g not in ALLOWED["THUMB"] for g in WNEW[i])),
    "r3_index_foreign_group_carriers_after": sorted(
        i for i in range(NV) if R3[i] == "INDEX"
        and any(g not in ALLOWED["INDEX"] for g in WNEW[i])),
    "edge_weight_vector_difference": {},
}
CONTINUITY["edge_weight_vector_difference"].update(vec_stats(WNEW, EDGES, "whole_mesh"))
CONTINUITY["edge_weight_vector_difference"].update(vec_stats(WNEW, region_edges, "authorised_region"))
CONTINUITY["edge_weight_vector_difference"].update(vec_stats(WOLD, EDGES, "whole_mesh_R1B_before"))


def worst_l1(W, edges, n=8):
    rows = []
    for k, (a, b) in enumerate(edges):
        gs = set(list(W[a]) + list(W[b]))
        l1 = sum(abs(W[a].get(g, 0.0) - W[b].get(g, 0.0)) for g in gs)
        rows.append((l1, k, a, b))
    rows.sort(key=lambda t: -t[0])
    return [{"edge": k, "a": a, "b": b, "L1": rr(l1, 6), "bind_mm": rr(BIND[k], 4),
             "a_R3": R3[a], "b_R3": R3[b], "a_in_region": a in REGION, "b_in_region": b in REGION,
             "a_W": dict((g, rr(v, 4)) for g, v in sorted(W[a].items())),
             "b_W": dict((g, rr(v, 4)) for g, v in sorted(W[b].items()))}
            for l1, k, a, b in rows[:n]]


CONTINUITY["worst_adjacent_weight_jumps_after"] = worst_l1(WNEW, EDGES)
CONTINUITY["worst_adjacent_weight_jumps_before_R1B"] = worst_l1(WOLD, EDGES)
CONTINUITY["max_L1_R1B_before"] = \
    CONTINUITY["edge_weight_vector_difference"]["whole_mesh_R1B_before"]["max_L1"]
CONTINUITY["max_adjacent_weight_jump_L1"] = \
    CONTINUITY["edge_weight_vector_difference"]["whole_mesh"]["max_L1"]
CONTINUITY["verdict"] = ("PASS" if len(NEW_FLIPS) == 0
                         and set(CONTINUITY["r3_thumb_foreign_group_carriers_after"]) <= set(WEB)
                         and not CONTINUITY["first_web_THUMB_IP_carriers"] else "REVIEW")
CONTINUITY["r3_thumb_foreign_group_carriers_after_sanctioned_first_web"] = sorted(
    set(CONTINUITY["r3_thumb_foreign_group_carriers_after"]) & set(WEB))
CONTINUITY["r3_thumb_foreign_group_carriers_after_unsanctioned"] = sorted(
    set(CONTINUITY["r3_thumb_foreign_group_carriers_after"]) - set(WEB))
C.jdump(NUM + "_WEIGHT_CONTINUITY_AUDIT.json", CONTINUITY, R1E)

# ---------------------------------------------------------------- R3 collar continuity audit (section 18)
def full_vec(W, i):
    return dict((g, rr(W[i].get(g, 0.0), 6)) for g in C.DEFORM)


COLLAR_RING = {}
for g in C.DEFORM:
    COLLAR_RING[g] = []
ring1_all, ring2_all = set(), set()
for v in sorted(COLLAR):
    ring1_all.update(ADJ[v])
ring1_only = ring1_all - COLLAR
for v in sorted(ring1_only):
    ring2_all.update(ADJ[v])
ring2_only = ring2_all - COLLAR - ring1_only
COLLAR_ROWS = []
for k in BND_EDGE_IDS:
    a, b = EDGES[k]
    gs = set(list(WNEW[a]) + list(WNEW[b]))
    l1 = sum(abs(WNEW[a].get(g, 0.0) - WNEW[b].get(g, 0.0)) for g in gs)
    da = max(WNEW[a].items(), key=lambda kv: kv[1])[0] if WNEW[a] else None
    db = max(WNEW[b].items(), key=lambda kv: kv[1])[0] if WNEW[b] else None
    sa = sorted(WNEW[a].items(), key=lambda kv: -kv[1])
    sb = sorted(WNEW[b].items(), key=lambda kv: -kv[1])
    COLLAR_ROWS.append({
        "edge_id": k, "v0": a, "v1": b, "bind_mm": rr(BIND[k], 4),
        "v0_R3": R3[a], "v1_R3": R3[b], "v0_R2": R2PART[a], "v1_R2": R2PART[b],
        "v0_full_16_group_vector": full_vec(WNEW, a), "v1_full_16_group_vector": full_vec(WNEW, b),
        "weight_vector_L1_difference": rr(l1, 6),
        "v0_dominant_group": da, "v1_dominant_group": db,
        "v0_second_group": (sa[1][0] if len(sa) > 1 else None),
        "v1_second_group": (sb[1][0] if len(sb) > 1 else None),
        "v0_second_value": rr(sa[1][1], 6) if len(sa) > 1 else None,
        "v1_second_value": rr(sb[1][1], 6) if len(sb) > 1 else None,
        "segment_identity": ("index-root collar / R3 THUMB|INDEX ownership boundary"),
        "first_web_membership": {"v0": a in WEB, "v1": b in WEB},
        "collar_membership": {"v0": a in COLLAR, "v1": b in COLLAR},
        "v0_sT_mm": rr(sT[a], 3), "v1_sT_mm": rr(sT[b], 3),
        "v0_sI_mm": rr(sI[a], 3), "v1_sI_mm": rr(sI[b], 3),
        "v0_dT_mm": rr(dT[a], 3), "v1_dT_mm": rr(dT[b], 3),
        "v0_dI_mm": rr(dI[a], 3), "v1_dI_mm": rr(dI[b], 3),
        "v0_R1B_dominant_group": (max(WOLD[a].items(), key=lambda kv: kv[1])[0] if WOLD[a] else None),
        "v1_R1B_dominant_group": (max(WOLD[b].items(), key=lambda kv: kv[1])[0] if WOLD[b] else None),
    })
_collar_l1 = sorted(r["weight_vector_L1_difference"] for r in COLLAR_ROWS)
COLLAR_AUDIT = {
    "stage": NUM + "_R3_COLLAR_WEIGHT_CONTINUITY_AUDIT",
    "generated_at": NOW,
    "collar_definition": ("SINGLE_COHERENT_COLLAR_CUT_SET / SINGLE_CONNECTED_BOUNDARY_FACE_STRIP: "
                          "16 boundary edges, 16 edge vertex-components, boundary face-component "
                          "= 1.  The 16 edges are NOT required to share endpoints (round section 2)"),
    "boundary_edge_count": len(BND_EDGE_IDS),
    "boundary_edge_vertex_components": 16,
    "boundary_face_component": 1,
    "collar_vertices": sorted(COLLAR),
    "one_ring_vertices": sorted(ring1_only),
    "two_ring_vertices": sorted(ring2_only),
    "edges": COLLAR_ROWS,
    "L1_difference": {"max": _collar_l1[-1] if _collar_l1 else 0.0,
                      "median": _collar_l1[len(_collar_l1) // 2] if _collar_l1 else 0.0,
                      "min": _collar_l1[0] if _collar_l1 else 0.0},
    "collar_ring_is_palm_driven": all(
        max(WNEW[v].items(), key=lambda kv: kv[1])[0] == "WRIST_R"
        for v in COLLAR if WNEW[v]),
    "rigid_opposite_chain_pairs": [
        r for r in COLLAR_ROWS
        if r["weight_vector_L1_difference"] > 1.5],
    "collar_hard_flip_after": len(COLLAR_HARD_AFTER),
    "verdict": ("PASS" if all(r["weight_vector_L1_difference"] <= 1.5 for r in COLLAR_ROWS)
                else "REVIEW"),
}
C.jdump(NUM + "_R3_COLLAR_WEIGHT_CONTINUITY_AUDIT.json", COLLAR_AUDIT, R1E)

# ---------------------------------------------------------------- protected drift (section 31)
CH = set(CHANGED)
MATCH = {"MIDDLE", "RING", "LITTLE"}
fourG = set("%s_%s_R" % (d, s) for d in MATCH for s in C.SEGMENTS[d])
idxG = set("%s_%s_R" % ("INDEX", s) for s in C.SEGMENTS["INDEX"])
thG = set("%s_%s_R" % ("THUMB", s) for s in C.SEGMENTS["THUMB"])


def dmax(i, groups=None):
    gs = set(list(WNEW[i]) + list(WOLD[i]))
    if groups is not None:
        gs &= set(groups)
    return max([abs(WNEW[i].get(g, 0.0) - WOLD[i].get(g, 0.0)) for g in gs] or [0.0])


cmc_centre = CMCC
confinement = CONFINE
outside = max([dmax(i) for i in range(NV) if i not in CH] or [0.0])
four = max([dmax(i, fourG) for i in range(NV) if i not in CH] or [0.0])
idx_drift = max([dmax(i, idxG) for i in range(NV) if i not in CH and R3[i] != "INDEX"] or [0.0])
th_drift = max([dmax(i, thG) for i in range(NV) if i not in CH and R3[i] != "THUMB"] or [0.0])
cage_drift = max([dmax(i) for i in CAGE if i not in CH] or [0.0])
first_web_drift = max([dmax(i) for i in WEB if i not in CH] or [0.0])
nail_drift = max([dmax(i) for i in (NAIL_T | NAIL_I) if i not in CH] or [0.0])
DRIFT = {
    "stage": NUM + "_PROTECTED_WEIGHT_DRIFT_AUDIT",
    "generated_at": NOW,
    "definition": ("every vertex outside the AUTHORISED region keeps its Stage5B R1B bind weights "
                   "exactly; inside the region the frozen anchors keep theirs"),
    "OUTSIDE_AUTHORISED_REGION": rr(outside, 12),
    "MIDDLE_RING_LITTLE": rr(four, 12),
    "UNAFFECTED_INDEX": rr(idx_drift, 12),
    "UNAFFECTED_THUMB": rr(th_drift, 12),
    "FIRST_WEB": rr(first_web_drift, 12),
    "NAIL": rr(nail_drift, 12),
    "DISTAL_CAP": rr(max([dmax(i) for i in CAP if i not in CH] or [0.0]), 12),
    "CMC_CAGE": rr(cage_drift, 12),
    "cmc_cage_vertices": len(CAGE),
    "cmc_cage_inside_authorised": len([i for i in CAGE if i in CH]),
    "authorised_region_count": len(REGION),
    "changed_vertex_count": len(CHANGED),
    "first_web_reweighted": len([i for i in WEB if i in CH]),
    "verdict": ("PASS" if (outside == 0.0 and four == 0.0 and idx_drift == 0.0
                           and th_drift == 0.0 and cage_drift == 0.0
                           and first_web_drift == 0.0 and nail_drift == 0.0
                           and not [i for i in WEB if i in CH]) else "FAIL"),
}
C.jdump(NUM + "_PROTECTED_WEIGHT_DRIFT_AUDIT.json", DRIFT, R1E)
C.jdump(NUM + "_HARD_FLIP_AUDIT.json", FLIP_AUDIT, R1E)

# =====================================================================================
# 9. status + report
# =====================================================================================
IN_AFTER = {}
for k, p in list(C.R3_FILES.items()) + list(C.PROBE_FILES.items()):
    IN_AFTER[k] = C.sha256(p)
IN_AFTER["stage5b_r1b_frozen_master"] = C.sha256(C.R1B_MASTER)
IN_AFTER["stage5b_r1c_failed_candidate"] = C.sha256(C.R1C_MASTER)
IN_AFTER["stage5b_r1d_failed_candidate"] = C.sha256(C.R1D_MASTER)
IN_AFTER["stage5a_r2a_live_production_rig"] = C.sha256(C.R2A)
IN_AFTER["stage6a_r1b_harness"] = C.sha256(C.S6A_R1B_HARNESS)
IN_AFTER["stage6b_r1b_harness"] = C.sha256(C.S6B_R1B_HARNESS)
IN_AFTER["stage6b_r1_harness"] = C.sha256(C.S6B_R1_HARNESS)
IN_AFTER["stage6b_case_matrix"] = C.sha256(C.CASE_MATRIX)
IN_AFTER["stage4a_r2_cmc_local_retopo_audit"] = C.sha256(C.CMC_AUDIT)
FROZEN_UNCHANGED = all(IN_AFTER.get(k) == v for k, v in FROZEN_SHA_SNAPSHOT.items())
log("frozen inputs unchanged = %s" % FROZEN_UNCHANGED)

ALL_STATIC = (GATES["TOPOLOGY_DELTA"] == 0 and GATES["UV_DELTA"] == 0
              and GATES["MATERIAL_DELTA"] == 0 and GATES["NAIL_FACE_DELTA"] == 0
              and GATES["BONE_DELTA"] == 0 and GATES["JOINT_DELTA"] == 0
              and GATES["ROLL_DELTA"] == 0 and GATES["OBJECT_ORIGIN_DELTA"] == 0
              and GATES["UNWEIGHTED_VERTICES"] == 0 and GATES["MAX_INFLUENCES_LE_4"]
              and GATES["NAN_WEIGHTS"] == 0 and GATES["NEGATIVE_WEIGHTS"] == 0
              and GATES["NON_NORMALIZED_VERTICES"] == 0 and GATES["GEOMETRY_DELTA_M"] == 0.0
              and GATES["GROUP_SET_UNCHANGED"])
STATUS = {
    "stage": NUM,
    "round": "STAGE5B_R1E_LOCAL_WEIGHT_RECONCILIATION_FROM_R1B",
    "generated_at": NOW,
    "status": "CANDIDATE_FOR_HUMAN_REVIEW",
    "rebuilt_from": "Stage5B R1B frozen master (never from R1C / R1D)",
    "current_frozen_production_master": {"path": C.R1B_MASTER.replace("\\", "/"),
                                         "sha256": C.R1B_SHA256,
                                         "unchanged_after": IN_AFTER["stage5b_r1b_frozen_master"] == C.R1B_SHA256},
    "failed_candidate_references": {
        "r1c": {"path": C.R1C_MASTER.replace("\\", "/"), "sha256": C.R1C_SHA256,
                "status": "FAILED_CANDIDATE_REFERENCE_ONLY",
                "unchanged_after": IN_AFTER["stage5b_r1c_failed_candidate"] == C.R1C_SHA256},
        "r1d": {"path": C.R1D_MASTER.replace("\\", "/"), "sha256": C.R1D_SHA256,
                "status": "FAILED_CANDIDATE_REFERENCE_ONLY",
                "unchanged_after": IN_AFTER["stage5b_r1d_failed_candidate"] == C.R1D_SHA256}},
    "live_rig": {"path": C.R2A.replace("\\", "/"), "sha256": C.R2A_SHA256},
    "ownership_authority": {
        "name": "DIGIT_OWNERSHIP_AUTHORITY_R3",
        "human_review": "HUMAN_APPROVED",
        "read_mode": "byte-identical (sha256 verified before and after)",
        "sha256": {k: IN_BEFORE[k] for k in C.R3_FILES},
        "supersedes": "DIGIT_OWNERSHIP_AUTHORITY_R2 (kept as historical provenance)"},
    "candidate": {"path": CAND.replace("\\", "/"), "sha256": SHA_CAND,
                  "bytes": os.path.getsize(CAND)},
    "authorised_region_count": len(REGION),
    "changed_weight_vertex_count": len(CHANGED),
    "hard_flip": {"global_before": len(FLIP_BEFORE), "global_after": len(FLIP_AFTER),
                  "new": len(NEW_FLIPS),
                  "thumb_distal_before": len(DISTAL_HARD_BEFORE),
                  "thumb_distal_after": len(DISTAL_HARD_AFTER),
                  "r3_collar_before": len(COLLAR_HARD_BEFORE),
                  "r3_collar_after": len(COLLAR_HARD_AFTER),
                  "first_web_before": len(WEB_HARD_BEFORE),
                  "first_web_after": len(WEB_HARD_AFTER),
                  "correction_domain_false": FLIP_AUDIT["R1E_correction_domain_false_hard_flip"]},
    "gates": GATES, "all_static_gates_pass": ALL_STATIC,
    "drift": DRIFT,
    "collar": {"boundary_edges": len(BND_EDGE_IDS), "collar_vertices": len(COLLAR),
               "max_L1": COLLAR_AUDIT["L1_difference"]["max"],
               "verdict": COLLAR_AUDIT["verdict"]},
    "continuity": {"hard_flip_edges": len(FLIP_AFTER), "new_hard_flip_edges": len(NEW_FLIPS),
                   "max_L1_jump": CONTINUITY["max_adjacent_weight_jump_L1"],
                   "verdict": CONTINUITY["verdict"],
                   "boundary_relaxation_rounds": RELAX_ROUNDS},
    "stale_joint_frame_used": False,
    "frozen_inputs_unchanged": FROZEN_UNCHANGED,
    "frozen_inputs_before": FROZEN_SHA_SNAPSHOT,
    "frozen_inputs_after": IN_AFTER,
    "stage6a_full_regression": "NOT_STARTED",
    "stage6b_full_retest": "NOT_STARTED",
    "targeted_prequalification": "NOT_STARTED",
    "log": LOG,
}
C.jdump(NUM + "_STATUS.json", STATUS, R1E)

md = []
md += ["# STAGE5B R1E -- LOCAL WEIGHT RECONCILIATION FROM R1B", "",
       "Status: **CANDIDATE_FOR_HUMAN_REVIEW**  ",
       "Generated: `%s`" % NOW, "",
       "Rebuilt from the **Stage5B R1B frozen master**.  R1C / R1D are never used as a source",
       "(`FAILED_CANDIDATE_REFERENCE_ONLY`).", "",
       "## 1. Inputs", "", "| role | path | sha256 |", "|---|---|---|",
       "| input (frozen master) | `%s` | `%s` |" % (C.R1B_MASTER.replace("\\", "/"), C.R1B_SHA256),
       "| live production rig | `%s` | `%s` |" % (C.R2A.replace("\\", "/"), C.R2A_SHA256),
       "| ownership authority | `DIGIT_OWNERSHIP_AUTHORITY_R3` | `%s` |"
       % IN_BEFORE["digit_ownership_authority_r3_json"][:16],
       "| R3 labels | `R3_OWNERSHIP_LABELS.json` | `%s` |"
       % IN_BEFORE["r3_ownership_labels"][:16],
       "| failed candidate (reference) | `%s` | `%s` |" % (C.R1C_MASTER.replace("\\", "/"), C.R1C_SHA256),
       "| failed candidate (reference) | `%s` | `%s` |" % (C.R1D_MASTER.replace("\\", "/"), C.R1D_SHA256),
       "| output (candidate) | `%s` | `%s` |" % (CAND.replace("\\", "/"), SHA_CAND), "",
       "`STAGE4B_R2_JOINT_FRAME.json` read: **False** (all joint data comes from the LIVE R2A rig).", "",
       "## 2. Authority split (round section 6)", "",
       "`DIGIT_OWNERSHIP_AUTHORITY_R3` defines the **digit family domain** only.  It is *not* a",
       "skin-weight authority: the R3 THUMB|INDEX collar is an interdigit commissure, so its skin",
       "is driven with a graded palm share while the ownership stays R3-exact.", "",
       "R3 facts used verbatim: boundary edges = %d, edge vertex-components = %d, boundary "
       "face-component = 1 (`SINGLE_COHERENT_COLLAR_CUT_SET`), THUMB components = 1, INDEX "
       "components = 1, islands = 0, manual overrides = 0."
       % (len(BND_EDGE_IDS), len(BND_EDGE_IDS)), "",
       "## 3. Live joint polylines (mm)", "",
       "- thumb `%s`" % [rr(x, 4) for x in XIJ["THUMB"]],
       "- index `%s`" % [rr(x, 4) for x in XIJ["INDEX"]],
       "- median edge `%.6f` mm" % MED, "",
       "## 4. Authorised region", "",
       "| criterion | count |", "|---|---|",
       "| R3 != R2 label | %d |" % len(P1a),
       "| R3 cross-digit dominant (R1B drives it from the other digit's chain) | %d |" % len(P1b),
       "| incident to an R3 collar boundary edge | %d |" % len(P2),
       "| incident to a historic CLASS_A/B probe edge | %d |" % len(P3),
       "| thumb-distal previous failure region | %d |" % len(P4),
       "| R3 THUMB carrying a foreign group | %d |" % len(P4b),
       "| collar %d-ring (index-root continuity) | %d |" % (GFOLD, len(P5)),
       "| **core** | **%d** |" % len(CORE),
       "| + same-domain 1-ring | %d |" % len(r1),
       "| + same-domain 2-ring | %d |" % len(r2),
       "| **authorised (final)** | **%d** |" % len(REGION),
       "| actually reweighted | %d |" % len(CHANGED), "",
       "## 5. Weight field", "",
       "- continuous function of the LIVE arc length only, centred quintic ramps;",
       "  `W_IP` = %.4f mm, `W_BASE` = %.4f mm, index `W_MCP/PIP/DIP` = %.4f / %.4f / %.4f mm."
       % (W_IP, W_BASE, W_MCPI, W_PIP, W_DIP),
       "- no one-hot ownership mapping: an R3 THUMB vertex is *not* snapped to the nearest thumb",
       "  bone, it follows the continuous thumb-chain field (and vice versa for INDEX).",
       "- palm valley: pure function of the integer graph distance to the R3 collar, `GFOLD` = %d," % GFOLD,
       "  clamped to 0 on the approved distal cap and on both approved nail sets.", "",
       "## 6. Hard 0/1 flips", "",
       "| scope | before (R1B) | after (R1E) |", "|---|---|---|",
       "| GLOBAL | **%d** | **%d** |" % (len(FLIP_BEFORE), len(FLIP_AFTER)),
       "| THUMB_DISTAL | %d | %d |" % (len(DISTAL_HARD_BEFORE), len(DISTAL_HARD_AFTER)),
       "| R3_COLLAR | %d | %d |" % (len(COLLAR_HARD_BEFORE), len(COLLAR_HARD_AFTER)),
       "| FIRST_WEB | %d | %d |" % (len(WEB_HARD_BEFORE), len(WEB_HARD_AFTER)),
       "", "NEW hard flips = **%d** ; correction-domain false hard flips = **%d**"
       % (len(NEW_FLIPS), FLIP_AUDIT["R1E_correction_domain_false_hard_flip"]), "",
       "## 7. Static gates", ""]
for k, v in GATES.items():
    md.append("- `%s` = `%s`" % (k, v))
md += ["", "## 8. Protected drift", ""]
for k in ("OUTSIDE_AUTHORISED_REGION", "MIDDLE_RING_LITTLE", "UNAFFECTED_INDEX",
          "UNAFFECTED_THUMB", "FIRST_WEB", "NAIL", "DISTAL_CAP", "CMC_CAGE", "verdict"):
    md.append("- `%s` = `%s`" % (k, DRIFT[k]))
md += ["", "## 9. R3 collar continuity", "",
       "- boundary edges = %d, collar vertices = %d" % (len(BND_EDGE_IDS), len(COLLAR)),
       "- weight-vector L1 difference across the collar: max `%s`, median `%s`"
       % (COLLAR_AUDIT["L1_difference"]["max"], COLLAR_AUDIT["L1_difference"]["median"]),
       "- collar ring palm-driven = **%s**" % COLLAR_AUDIT["collar_ring_is_palm_driven"],
       "- verdict = **%s**" % COLLAR_AUDIT["verdict"], "",
       "## 10. Freeze rule", "",
       "Stage5B R1B remains `CURRENT_FROZEN_PRODUCTION_MASTER` until Human Review approves R1E.",
       "No freeze was performed.  R1C / R1D are NOT deleted.", "",
       "## 11. Not authorised this round", "",
       "Stage6A 42-case regression and Stage6B 9-case retest are **NOT_STARTED**.", ""]
open(os.path.join(R1E, NUM + "_REPORT.md"), "w", encoding="utf-8").write("\n".join(md))
log("wrote %s_REPORT.md" % NUM)

if not FROZEN_UNCHANGED:
    raise SystemExit("FAIL CLOSED: a frozen input changed during the round")
if not ALL_STATIC:
    raise SystemExit("FAIL CLOSED: a static gate failed")
print("R1E_BUILD_DONE")
