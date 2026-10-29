# =====================================================================================
# STAGE6B_R1B -- shared authorities for SEMANTIC OWNERSHIP CORRECTION + LOCAL WEIGHT
#                RECONCILIATION
# =====================================================================================
# READ-ONLY with respect to every frozen input.  This module
#   * pins the frozen inputs (Stage5A R2A / Stage5B R1B / Stage6A R1A harness / Stage6B R1
#     harness / Stage6B R1A provenance deliverables),
#   * implements DIGIT_OWNERSHIP_AUTHORITY_R2:
#         MESH_TOPOLOGY_AWARE + MULTI_SOURCE_GEODESIC_DIGIT_PARTITION
#         + APPROVED_ANATOMICAL_CHAIN_CONTEXT
#     (an exact Dijkstra over the REAL mesh edge graph, multi-source, seeded at the approved
#      joint-polyline distal landmark of each digit + the approved wrist origin),
#   * derives the CORRECTION DOMAIN and the AUTHORISED WEIGHT REGION,
#   * provides the frozen HISTORIC_CLASS_B_EDGE_PROBE_SET (the exact 61 edges approved by the
#     Stage6B R1A seam provenance round) -- these edges are tracked FOREVER, whether or not
#     they are still a semantic boundary,
#   * provides the deterministic same-digit trusted-neighbour constrained interpolation used to
#     reconcile bind weights (NO per-vertex free parameters).
#
# It never writes to a frozen blend.  Writing is done only by explicit build scripts.
# =====================================================================================
import os
import sys
import json
import math
import heapq
import hashlib

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))       # .../production_spec
WORKSPACE = os.path.abspath(os.path.join(PROD, ".."))
S5 = os.path.join(PROD, "stage5_production_rig")
S6D = os.path.join(PROD, "stage6_deformation")
S6B = os.path.join(S6D, "stage6b")
S6B_R1A = os.path.join(S6D, "stage6b_r1a_seam_provenance")
S6B_R1B = os.path.join(S6D, "stage6b_r1b")
S6A_R1A = os.path.join(S6D, "stage6a_r1a")
S6A_R1B = os.path.join(S6D, "stage6a_r1b")
S5B_R1C = os.path.join(S5, "stage5b_r1c")

for _p in (os.path.join(S6B, "scripts"), os.path.join(S6D, "stage6a", "scripts"),
           os.path.join(S5, "stage5b_r1b", "scripts"),
           os.path.join(S5, "stage5b_r1a", "scripts")):
    if _p not in sys.path:
        sys.path.append(_p)

import s6b_common as B                                              # noqa: E402
import r1a_common as RC                                             # noqa: E402
import r1b_common as RB                                             # noqa: E402

MM = 1000.0
EPS = 1e-8

# ---------------------------------------------------------------- frozen inputs
R1B_MASTER = B.R1B_MASTER
R1B_SHA256 = B.R1B_SHA256
R1A_HARNESS = B.R1A_HARNESS
R1A_HARNESS_SHA256 = B.R1A_HARNESS_SHA256
S5A_MASTER = B.S5A_MASTER
S5A_SHA256 = B.S5A_SHA256
S6B_HARNESS = B.HARNESS_R1
S6B_HARNESS_SHA256 = "4b6200899fe4d2f5a67e3254aec2a5cb17b734b14acefe381a2ac9c1241f549d"
S6B_R1B_HARNESS = os.path.join(S6B_R1B, "RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1B.blend")
S6A_R1B_HARNESS = os.path.join(S6A_R1B, "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1B.blend")
R1C_MASTER = os.path.join(S5B_R1C, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1C.blend")

PROVENANCE = {
    "stage6b_r1a_class_a": os.path.join(S6B_R1A, "STAGE6B_R1A_CLASS_A_VALID_WEB_EDGES.json"),
    "stage6b_r1a_class_b": os.path.join(S6B_R1A, "STAGE6B_R1A_CLASS_B_OWNERSHIP_MISCLASSIFICATION.json"),
    "stage6b_r1a_status": os.path.join(S6B_R1A, "STAGE6B_R1A_SEAM_PROVENANCE_STATUS.json"),
    "stage6b_case_matrix": os.path.join(S6B, "STAGE6B_CASE_MATRIX.json"),
    "stage6b_opposition_vector": os.path.join(S6B, "STAGE6B_OPPOSITION_VECTOR_AUDIT.json"),
}

DIGITS5 = ["THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"]
CLASSES = DIGITS5 + ["wrist"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def rr(x, n=9):
    return round(float(x), n)


def jdump(name, obj, where=None):
    p = os.path.join(where or S6B_R1B, name)
    json.dump(obj, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return p


# =====================================================================================
# DIGIT_OWNERSHIP_AUTHORITY_R2
# =====================================================================================
MESH_OBJ = "Hand  - Realistic"
RIG_OBJ = "RIGHT_HAND_PRODUCTION_RIG"


def mesh_graph(V0, EDGES):
    adj = {}
    for a, b in EDGES:
        w = (V0[a] - V0[b]).length
        adj.setdefault(a, []).append((b, w))
        adj.setdefault(b, []).append((a, w))
    return adj


def dijkstra_multi(adj, sources):
    """exact multi-source Dijkstra over the real mesh edge graph (edge length = metric)."""
    d = {}
    pq = []
    for s in sources:
        if s not in d or d[s] > 0.0:
            d[s] = 0.0
        heapq.heappush(pq, (0.0, s))
    while pq:
        du, u = heapq.heappop(pq)
        if du > d.get(u, 1e18) + 1e-15:
            continue
        for v, w in adj.get(u, ()):
            if du + w < d.get(v, 1e18) - 1e-16:
                d[v] = du + w
                heapq.heappush(pq, (du + w, v))
    return d


def nearest_vertex(V0, P):
    return min(range(len(V0)), key=lambda i: (V0[i] - P).length)


def approved_chain_seeds(ref):
    """APPROVED ANATOMICAL CHAIN CONTEXT: one seed per digit, placed at the distal end of the
    APPROVED joint polyline of that digit (the same frozen joint-frame chain that every
    Stage5B / Stage6A / Stage6B script uses to build its arc coordinate), plus the approved
    wrist origin vertex.

    The seeds are deliberately taken from the approved CHAIN, not from any contested
    semantic region, so that the partition is not self-fulfilling.
    """
    V0 = ref["V0"]
    AC = ref["AC"]
    seeds = {}
    for D in DIGITS5:
        seeds[D] = nearest_vertex(V0, AC[D][-1])
    seeds["wrist"] = nearest_vertex(V0, AC["wrist"][0])
    return seeds


def r2_partition(ctx, ref, margin_threshold_mm=None, max_sweeps=40,
                 thumb_seed_mode="approved_distal_cap"):
    """MULTI_SOURCE_GEODESIC_DIGIT_PARTITION (mesh-topology aware).

    Two deterministic stages:
      1. exact multi-source Dijkstra over the real mesh edge graph;
      2. MESH_TOPOLOGY_AWARE disambiguation -- a label flip is only accepted where the
         geodesic evidence is decisive.  A vertex whose nearest-source margin (2nd-nearest
         minus nearest source distance) is below the mesh edge scale tau = one median edge
         length carries NO usable evidence (the two candidate chains are effectively
         equidistant, which is exactly the Stage6B R1A "random flip" signature), so it
         inherits the majority label of its already-decisive neighbours.  Iterated to a
         fixed point; deterministic.
    """
    V0 = ref["V0"]
    EDGES = ref["EDGES"]
    adjw = mesh_graph(V0, EDGES)
    adj = dict((k, [t[0] for t in v]) for k, v in adjw.items())
    seeds = approved_chain_seeds(ref)
    if thumb_seed_mode == "approved_distal_cap":
        seeds["THUMB"] = nearest_vertex(V0, sum(
            (V0[i] for i in ref["cap"]["thumb_cap_vertex_ids"]), Vector()) /
            len(ref["cap"]["thumb_cap_vertex_ids"]))
    gs = dict((k, dijkstra_multi(adjw, [v])) for k, v in seeds.items())
    NV = ref["NV"]
    order_all = []
    for i in range(NV):
        order_all.append(sorted(gs.items(), key=lambda kv: kv[1].get(i, 1e18)))
    raw = [o[0][0] for o in order_all]
    margins = [rr((o[1][1].get(i, 1e18) - o[0][1].get(i, 1e18)) * MM, 6)
               for i, o in enumerate(order_all)]
    tau = ref["med_edge"]                       # mm
    thr = tau if margin_threshold_mm is None else margin_threshold_mm
    part = list(raw)
    decisive = [i for i in range(NV) if margins[i] >= thr]
    ambiguous = [i for i in range(NV) if margins[i] < thr]
    relabelled = []
    fixed = set(decisive)
    for _ in range(max_sweeps):
        nxt = set(fixed)
        changed = 0
        for i in ambiguous:
            cnt = {}
            for u in adj.get(i, ()):
                if u in fixed:
                    cnt[part[u]] = cnt.get(part[u], 0) + 1
            if not cnt:
                continue
            best = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            if best != part[i]:
                part[i] = best
                changed += 1
                relabelled.append(i)
                nxt.add(i)
        fixed = nxt
        if changed == 0:
            break
    return {"partition": part, "raw_partition": raw, "seeds": seeds, "margin_mm": margins,
            "thumb_seed_mode": thumb_seed_mode,
            "margin_threshold_mm": rr(thr, 6),
            "ambiguous_margin_vertices": len(ambiguous),
            "topology_aware_relabelled_vertices": sorted(set(relabelled)),
            "geodesic": dict((k, [rr(v.get(i, -1.0) * MM, 6) for i in range(NV)])
                             for k, v in gs.items())}


# ---------------------------------------------------------------- probe sets
def load_probe_sets():
    """the exact frozen edge sets approved by the Stage6B R1A seam provenance round."""
    ca = json.load(open(PROVENANCE["stage6b_r1a_class_a"], encoding="utf-8"))
    cb = json.load(open(PROVENANCE["stage6b_r1a_class_b"], encoding="utf-8"))
    A = [(e["edge_id"], e["endpoints"]["v0"], e["endpoints"]["v1"]) for e in ca["edges"]]
    B = [(e["edge_id"], e["endpoints"]["v0"], e["endpoints"]["v1"]) for e in cb["edges"]]
    return {"CLASS_A": A, "CLASS_B": B,
            "class_a_ids": [x[0] for x in A], "class_b_ids": [x[0] for x in B]}


# =====================================================================================
# bind weights
# =====================================================================================
def read_weights(ob, NV):
    return RB.read_object_weights(ob, NV)


def push_weights(ob, NV, W):
    RB.push_weights_to_object(ob, NV, W)


# =====================================================================================
# corrected ownership + correction domain
# =====================================================================================
def allowed_groups(digit):
    if digit == "THUMB":
        return ["WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R"]
    if digit in ("INDEX", "MIDDLE", "RING", "LITTLE"):
        return ["WRIST_R"] + ["%s_%s_R" % (digit, s) for s in RC.CHAIN[digit]]
    return ["WRIST_R"]


GROUP_DIGIT = {"WRIST_R": "wrist"}
for _d in DIGITS5:
    for _s in RC.CHAIN[_d]:
        GROUP_DIGIT["%s_%s_R" % (_d, _s)] = _d


def build_corrected_ownership(ctx, ref, part, probe):
    """OPERATIVE CORRECTED_DIGIT_OWNERSHIP_R2.

    own_r1a outside the authorised correction domain; the R2 geodesic partition inside it.
    The correction domain is the union of
      (a) every endpoint of the 67 flagged edges whose R2 label differs from own_r1a,
      (b) every vertex whose label change is inside the {THUMB, INDEX} transition family,
    closed over the same-corrected-digit 1-ring and (only where the trusted-neighbour count is
    insufficient) the 2-ring.
    """
    NV = ref["NV"]
    own = ctx["own_r1a"]
    V0 = ref["V0"]
    EDGES = ref["EDGES"]
    adjw = mesh_graph(V0, EDGES)
    adj = dict((k, [t[0] for t in v]) for k, v in adjw.items())
    flagged = set()
    for _k, a, b in probe["CLASS_A"] + probe["CLASS_B"]:
        flagged.add(a)
        flagged.add(b)
    core = set()
    for i in range(NV):
        if own[i] == part[i]:
            continue
        fam = {own[i], part[i]}
        if i in flagged or fam <= {"THUMB", "INDEX"}:
            core.add(i)
    # closure: same-corrected-digit 1-ring, then 2-ring only where a core vertex has fewer than
    # 2 trusted same-digit neighbours inside/around the domain.
    domain = set(core)
    ring1 = set()
    for i in core:
        for u in adj.get(i, ()):
            if u not in domain and part[u] == part[i]:
                ring1.add(u)
    domain |= ring1
    ring2 = set()
    for i in sorted(domain):
        cnt = sum(1 for u in adj.get(i, ())
                  if u not in domain and part[u] == part[i])
        if cnt < 2:
            for u in adj.get(i, ()):
                if u not in domain and part[u] == part[i]:
                    ring2.add(u)
    domain |= ring2
    # ---- cross-boundary continuity closure: the endpoints of the corrected THUMB|INDEX
    # ownership boundary must be reconciled on BOTH sides, otherwise relocating the boundary
    # would only move the weight discontinuity (round spec sections 13 / 14).
    bnd = []
    for k, (a, b) in enumerate(EDGES):
        if part[a] != part[b] and {part[a], part[b]} == {"THUMB", "INDEX"}:
            bnd.append(k)
    bnd_v = set()
    for k in bnd:
        for v in EDGES[k]:
            bnd_v.add(v)
    boundary_added = sorted(v for v in bnd_v if v not in domain)
    domain |= bnd_v
    corr = [part[i] if i in domain else own[i] for i in range(NV)]
    return {"own_r1a": own, "r2": part, "core": sorted(core), "domain": sorted(domain),
            "ring1_added": sorted(ring1), "ring2_added": sorted(ring2),
            "boundary_continuity_added": boundary_added, "r2_boundary_edges": bnd,
            "corrected": corr, "flagged": sorted(flagged)}


def weight_consistency(corrected, W):
    """(verdict per vertex, foreign groups)."""
    NV = len(corrected)
    verdict = [None] * NV
    foreign = [[] for _ in range(NV)]
    for i in range(NV):
        D = corrected[i]
        allow = set(allowed_groups(D))
        fg = sorted(g for g in W[i] if g not in allow)
        foreign[i] = fg
        if fg:
            verdict[i] = "WEIGHT_RECONCILIATION_REQUIRED"
        else:
            dom = max(W[i].items(), key=lambda kv: kv[1])[0] if W[i] else None
            if dom is None:
                verdict[i] = "AMBIGUOUS"
            elif GROUP_DIGIT.get(dom, "wrist") == "wrist" and D != "wrist":
                verdict[i] = "AMBIGUOUS"
            else:
                verdict[i] = "WEIGHT_ALREADY_COMPATIBLE"
    return verdict, foreign


def trusted_interpolation(ref, W, corrected, domain, rings=(2, 3, 4), max_inf=4, eps=1e-6):
    """DETERMINISTIC same-digit trusted-neighbour constrained interpolation.

    For every vertex of the correction domain: average the bind weights of the nearest
    same-corrected-digit vertices that are NOT in the domain (Dirichlet anchors), restricted to
    the group family allowed for the corrected digit, with inverse-distance weights.  No
    per-vertex free parameter exists.
    """
    NV = ref["NV"]
    V0 = ref["V0"]
    EDGES = ref["EDGES"]
    adj = {}
    for a, b in EDGES:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    dom = set(domain)
    out = [dict(W[i]) for i in range(NV)]
    info = {}
    for i in sorted(dom):
        D = corrected[i]
        allow = set(allowed_groups(D))
        # trusted anchors: same corrected digit, outside the domain, mostly-own-family weights
        cand = []
        seen = {i}
        front = [i]
        for depth in rings:
            nxt = []
            for u in front:
                for v in adj.get(u, ()):
                    if v in seen:
                        continue
                    seen.add(v)
                    nxt.append(v)
            front = nxt
            for v in front:
                if v in dom or corrected[v] != D:
                    continue
                if any(g not in allow for g in W[v]):
                    continue
                cand.append(v)
            if len(cand) >= 3:
                break
        if not cand:                               # last resort: any same-digit neighbour
            for v in list(seen)[1:]:
                if corrected[v] == D:
                    cand.append(v)
        if not cand:
            info[i] = {"anchors": 0, "method": "UNRESOLVED"}
            continue
        acc = dict((g, 0.0) for g in allow)
        tot = 0.0
        for v in cand:
            d = (V0[i] - V0[v]).length
            w = 1.0 / max(d, 1e-4)
            tot += w
            for g, val in W[v].items():
                if g in allow:
                    acc[g] = acc.get(g, 0.0) + w * val
        if tot <= 0.0:
            info[i] = {"anchors": len(cand), "method": "UNRESOLVED"}
            continue
        acc = dict((g, v / tot) for g, v in acc.items() if v / tot > eps)
        items = sorted(acc.items(), key=lambda kv: (-kv[1], kv[0]))[:max_inf]
        s = sum(v for _g, v in items)
        newv = dict((g, v / s) for g, v in items) if s > 0 else {}
        out[i] = newv
        info[i] = {"anchors": len(cand), "method": "SAME_DIGIT_ANCHOR_INTERPOLATION",
                   "influences": len(newv)}
    return out, info


def vertex_group_stats(W):
    NV = len(W)
    unw = sum(1 for i in range(NV) if not W[i])
    maxinf = max((len(W[i]) for i in range(NV)), default=0)
    nan = sum(1 for i in range(NV) for v in W[i].values() if not math.isfinite(v))
    neg = sum(1 for i in range(NV) for v in W[i].values() if v < 0.0)
    badnorm = 0
    for i in range(NV):
        s = sum(W[i].values())
        if W[i] and abs(s - 1.0) > 1e-5:
            badnorm += 1
    return {"unweighted_vertices": unw, "max_influences": maxinf,
            "nan_weights": nan, "negative_weights": neg,
            "non_normalized_vertices": badnorm}
