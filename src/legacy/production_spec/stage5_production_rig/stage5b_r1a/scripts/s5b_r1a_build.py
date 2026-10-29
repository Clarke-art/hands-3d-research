# =====================================================================================
# STAGE5B_R1A -- THUMB CHAIN WEIGHT REBALANCE  (narrow-scope local weight revision)
# =====================================================================================
# INPUT  (frozen):  stage5b_r1/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend
#                   sha256 8f4c6901fdae417e3855d388f9739ebea10863f0ebdbfedf0df8d79a751c308d
# OUTPUT (new):     stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend
#
# ONLY the local skin weights of the authorised thumb region are recomputed.
#   free groups   : WRIST_R, THUMB_CMC_R, THUMB_MCP_R, THUMB_IP_R, INDEX_MCP_R
#   frozen groups : INDEX_PIP_R, INDEX_DIP_R, MIDDLE_*, RING_*, LITTLE_*  (EXACTLY unchanged)
#   every vertex outside the authorised region keeps its full 16-group R1 vector
#
# Method: semantic region  +  joint-local transition along the approved thumb chain arc
#         +  radial tube/base split  +  sanctioned thumb<->index cross blend in the web.
# No bone / geometry / topology / UV / material / RSSF change is made.
# =====================================================================================
import bpy
import sys
import os
import json
import math
import hashlib
import datetime
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import r1a_common as C                                   # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
TOP = os.path.dirname(OUTDIR)
NOW = datetime.datetime.now().astimezone().isoformat()
MM = C.MM

R1 = os.path.join(TOP, "stage5b_r1", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend")
R1_SHA = "8f4c6901fdae417e3855d388f9739ebea10863f0ebdbfedf0df8d79a751c308d"
MASTER = os.path.join(TOP, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
MASTER_SHA = "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"
OUT_BLEND = os.path.join(OUTDIR, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend")
MAX_INF = 4
EPS = 1e-8

LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[R1A-BUILD]", s)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rr(x, n=9):
    return round(float(x), n)


def S(z):
    return C.S(z)


# ---------------------------------------------------------------- input gate
s_master = sha(MASTER)
s_r1 = sha(R1)
log("master sha =", s_master, "OK" if s_master == MASTER_SHA else "DRIFT")
log("r1 sha     =", s_r1, "OK" if s_r1 == R1_SHA else "DRIFT")
if s_master != MASTER_SHA or s_r1 != R1_SHA:
    raise SystemExit("FAIL CLOSED: frozen input hash drift")

# ---------------------------------------------------------------- reference + R1
ref = C.load_reference(TOP)
NV = ref["NV"]
V0 = ref["V0"]
TF = C.thumb_frame(ref)
ARC = TF["arc_thumb_mm"]
s_MCP, s_IP, s_TIP = TF["s_MCP_joint_mm"], TF["s_IP_joint_mm"], TF["s_TIP_mm"]
MED = ref["med_edge"]
TAU = MED
R_TT, R_MAX = C.thumb_radii(ref, TF)
own = ref["OWN_V"]
dth = [ref["dchain"][i]["THUMB"] for i in range(NV)]
didx = [ref["dchain"][i]["INDEX"] for i in range(NV)]

# ---- R1A semantic regions (deterministic, evidence based) -------------------------
RG = C.build_regions(ref, TF, TAU, R_TT, R_MAX)
OWN_R1A = RG["own_r1a"]
THUMB_OWN = set(i for i in range(NV) if OWN_R1A[i] == "THUMB")
DISTAL, PROXIMAL = RG["THUMB_DISTAL"], RG["THUMB_PROXIMAL"]
METACARPAL, BASE_FOLD = RG["THUMB_FIRST_METACARPAL"], RG["THUMB_BASE_FOLD"]
THENAR_BASE, FIRST_WEB = RG["THENAR_BASE"], RG["FIRST_WEB"]
CENTRAL_PALM = RG["CENTRAL_PALM"]
AUTH = RG["AUTH"]
log("regions: DISTAL=%d PROXIMAL=%d METACARPAL=%d BASE_FOLD=%d THENAR_BASE=%d FIRST_WEB=%d "
    "CENTRAL_PALM=%d" % (len(DISTAL), len(PROXIMAL), len(METACARPAL), len(BASE_FOLD),
                         len(THENAR_BASE), len(FIRST_WEB), len(CENTRAL_PALM)))
log("uncovered thumb-owned vertices = %d" % len(RG["uncovered_thumb_owned"]))
log("AUTHORISED modification set = %d vertices (%.2f%% of mesh)"
    % (len(AUTH), 100.0 * len(AUTH) / NV))

# ---------------------------------------------------------------- open Stage5B R1
b = C.load_weights(R1)
W1 = b["W"]
V1 = b["V"]
me = b["me"]
ob = b["ob"]
groups_r1 = b["groups"]
log("R1 groups (%d): %s" % (len(groups_r1), groups_r1))
missing = [g for g in C.DEFORM if g not in groups_r1]
if missing:
    raise SystemExit("FAIL CLOSED: R1 is missing deform groups %s" % missing)

# sanity: which vertices carry THUMB_IP and are they all inside AUTH?
ip_out = [i for i in range(NV) if W1[i].get("THUMB_IP_R", 0.0) > 0.0 and i not in AUTH]
log("THUMB_IP nonzero outside AUTH = %d" % len(ip_out))
if ip_out:
    raise SystemExit("FAIL CLOSED: THUMB_IP_R present outside the authorised region")

# =====================================================================================
# WEIGHT RECOMPUTATION for the authorised region only
# =====================================================================================
W2 = [dict(W1[i]) for i in range(NV)]          # start from R1 everywhere
CHANGED = []
UNCHANGED_AUTH = []

for i in sorted(AUTH):
    Wi = W1[i]
    frozen = dict((g, Wi[g]) for g in C.FROZEN_GROUPS if Wi.get(g, 0.0) > 0.0)
    F = sum(frozen.values())
    budget = MAX_INF - len(frozen)
    if budget <= 0:
        UNCHANGED_AUTH.append(i)
        continue

    s = ARC[i]
    d = dth[i]
    t_IP = S((s - s_IP) / TAU)
    t_MCP = S((s - s_MCP) / TAU)
    A_IP = t_IP
    A_MCP = t_MCP - t_IP
    A_BASE = 1.0 - t_MCP
    ft = RG["f_tube"](d)
    free = {
        "THUMB_IP_R": A_IP,
        "THUMB_MCP_R": A_MCP,
        "THUMB_CMC_R": A_BASE * ft,
        "WRIST_R": A_BASE * (1.0 - ft),
        "INDEX_MCP_R": 0.0,
    }
    if i in FIRST_WEB:
        # sanctioned thumb <-> index cross blend; THUMB_IP is ZERO inside the first web
        share_idx = S((d - didx[i] + TAU) / (2.0 * TAU))
        thumb_side = 1.0 - share_idx
        base = A_MCP + A_BASE * ft + A_BASE * (1.0 - ft)
        if base <= 1e-12:
            free = {"THUMB_IP_R": 0.0, "THUMB_MCP_R": thumb_side, "THUMB_CMC_R": 0.0,
                    "WRIST_R": 0.0, "INDEX_MCP_R": share_idx}
        else:
            free = {"THUMB_IP_R": 0.0,
                    "THUMB_MCP_R": thumb_side * A_MCP / base,
                    "THUMB_CMC_R": thumb_side * (A_BASE * ft) / base,
                    "WRIST_R": thumb_side * (A_BASE * (1.0 - ft)) / base,
                    "INDEX_MCP_R": share_idx}
    # keep at most `budget` free groups, drop epsilon free terms
    items = sorted(((g, w) for g, w in free.items() if w > EPS), key=lambda kv: -kv[1])
    kept = items[:budget]
    tot = sum(w for _g, w in kept)
    if tot <= 1e-14:
        # degenerate: give the free budget to the nearest root bone for this region
        fallback = "THUMB_IP_R" if (s >= s_IP) else ("THUMB_MCP_R" if s >= s_MCP else "THUMB_CMC_R")
        kept = [(fallback, 1.0)]
        tot = 1.0
    # FROZEN GROUPS ARE COPIED VERBATIM AND ARE NEVER SCALED.
    # Only the free part is normalised, into the exact remaining budget (1 - F).
    newv = dict(frozen)
    target = 1.0 - F
    for g, w in kept:
        newv[g] = newv.get(g, 0.0) + (w / tot) * target
    newv = dict((g, v) for g, v in newv.items() if v > EPS or g in frozen)
    s_free = sum(v for g, v in newv.items() if g not in frozen)
    if target > 0 and abs(s_free - target) > 1e-15:
        # rescale the FREE part only (floating point tidy-up; frozen stay bit-identical)
        k = target / s_free
        newv = dict((g, (v * k if g not in frozen else v)) for g, v in newv.items())
    W2[i] = newv
    if newv != Wi:
        CHANGED.append(i)

log("changed vertices = %d ; authorised but unchanged = %d" % (len(CHANGED), len(UNCHANGED_AUTH)))

# ---- prune + normalize ONLY on the vertices that actually changed -------------------
# The construction already emits <= 4 influences, and pruning is applied over the FREE
# groups only so the frozen four-finger groups can never move.
PRUNE = {"vertices_pruned": 0, "total_discarded": 0.0,
         "worst_discarded_weight_per_vertex": 0.0, "worst_vertex": None}
for i in CHANGED:
    w = W2[i]
    frozen = dict((g, v) for g, v in w.items() if g in C.FROZEN_GROUPS)
    free = dict((g, v) for g, v in w.items() if g not in C.FROZEN_GROUPS)
    budget = MAX_INF - len(frozen)
    if len(free) > budget:
        items = sorted(free.items(), key=lambda kv: -kv[1])
        keep = items[:budget]
        disc = sum(kv[1] for kv in items[budget:])
        PRUNE["vertices_pruned"] += 1
        PRUNE["total_discarded"] += disc
        if disc > PRUNE["worst_discarded_weight_per_vertex"]:
            PRUNE["worst_discarded_weight_per_vertex"] = disc
            PRUNE["worst_vertex"] = i
        free = dict(keep)
    sf = sum(free.values())
    if sf > 0:
        tgt = 1.0 - sum(frozen.values())
        free = dict((g, v / sf * tgt) for g, v in free.items())
    nv = dict(frozen)
    nv.update(free)
    W2[i] = nv
log("R1A prune: vertices_pruned=%d discarded=%.9f"
    % (PRUNE["vertices_pruned"], PRUNE["total_discarded"]))

# ---- write the vertex groups -------------------------------------------------------
for vg in list(ob.vertex_groups):
    ob.vertex_groups.remove(vg)
for g in C.DEFORM:
    ob.vertex_groups.new(name=g)
VG = {g.name: g for g in ob.vertex_groups}
for g in C.DEFORM:
    idx = [i for i in range(NV) if W2[i].get(g, 0.0) > 0.0]
    for i in idx:
        VG[g].add([i], float(W2[i][g]), 'REPLACE')
log("vertex groups rewritten: %d" % len(ob.vertex_groups))

# ---- parent / modifier / transform must be untouched --------------------------------
PARENT_OK = (ob.parent is not None and ob.parent.name == "RIGHT_HAND_PRODUCTION_RIG")
MOD_OK = any(m.type == 'ARMATURE' and m.object is not None
             and m.object.name == "RIGHT_HAND_PRODUCTION_RIG" for m in ob.modifiers)
log("parent ok=%s ; armature modifier ok=%s" % (PARENT_OK, MOD_OK))
if not (PARENT_OK and MOD_OK):
    raise SystemExit("FAIL CLOSED: parent / armature modifier structure would change")

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, copy=True, compress=False)
OUT_SHA = sha(OUT_BLEND)
log("SAVED %s" % OUT_BLEND)
log("SAVED sha256 = %s" % OUT_SHA)

# =====================================================================================
# build-time evidence
# =====================================================================================
def dom(w):
    return max(w.items(), key=lambda kv: kv[1])[0] if w else None


delta = []
per_add = {}
per_rem = {}
max_abs = 0.0
for i in range(NV):
    a, c = W1[i], W2[i]
    diff = 0.0
    for g in C.DEFORM:
        av = a.get(g, 0.0)
        cv = c.get(g, 0.0)
        if cv > av:
            per_add[g] = per_add.get(g, 0.0) + (cv - av)
        elif av > cv:
            per_rem[g] = per_rem.get(g, 0.0) + (av - cv)
        diff = max(diff, abs(cv - av))
    max_abs = max(max_abs, diff)
    if i in CHANGED:
        delta.append({"vertex": i, "region": (
            "FIRST_WEB" if i in FIRST_WEB else
            "THENAR_BASE" if i in THENAR_BASE else
            "THUMB_DISTAL" if i in DISTAL else
            "THUMB_PROXIMAL" if i in PROXIMAL else
            "THUMB_BASE_FOLD" if i in BASE_FOLD else "THUMB_FIRST_METACARPAL"),
            "after_dominant": dom(c), "before_dominant": dom(a),
            "before": dict((g, rr(a.get(g, 0.0))) for g in C.DEFORM if a.get(g, 0.0) > 0),
            "after": dict((g, rr(c.get(g, 0.0))) for g in C.DEFORM if c.get(g, 0.0) > 0)})

json.dump({
    "stage": "STAGE5B_R1A_WEIGHT_DELTA_AUDIT", "generated_at": NOW,
    "input_r1_blend": R1, "input_r1_sha256": s_r1,
    "output_r1a_blend": OUT_BLEND, "output_r1a_sha256": OUT_SHA,
    "authorised_region": {
        "vertex_count": len(AUTH),
        "regions": {"THUMB_DISTAL": sorted(DISTAL), "THUMB_PROXIMAL": sorted(PROXIMAL),
                    "THUMB_FIRST_METACARPAL": sorted(METACARPAL),
                    "THENAR_BASE": sorted(THENAR_BASE), "FIRST_WEB": sorted(FIRST_WEB)},
        "central_palm_untouched": sorted(CENTRAL_PALM)},
    "changed_vertex_count": len(CHANGED), "changed_vertices": sorted(CHANGED),
    "unchanged_vertex_count": NV - len(CHANGED),
    "authorised_but_unchanged_count": len(UNCHANGED_AUTH),
    "max_absolute_weight_delta": rr(max_abs, 12),
    "per_group_added_weight": dict((g, rr(v)) for g, v in sorted(per_add.items())),
    "per_group_removed_weight": dict((g, rr(v)) for g, v in sorted(per_rem.items())),
    "frozen_groups_never_touched": C.FROZEN_GROUPS,
    "per_vertex_delta": delta,
    "prune": PRUNE, "log": LOG},
    open(os.path.join(OUTDIR, "STAGE5B_R1A_WEIGHT_DELTA_AUDIT.json"), "w", encoding="utf-8"),
    indent=1, ensure_ascii=False)

json.dump({"regions": {"THUMB_DISTAL": sorted(DISTAL), "THUMB_PROXIMAL": sorted(PROXIMAL),
                       "THUMB_FIRST_METACARPAL": sorted(METACARPAL),
                       "THENAR_BASE": sorted(THENAR_BASE), "FIRST_WEB": sorted(FIRST_WEB),
                       "CENTRAL_PALM_count": len(CENTRAL_PALM),
                       "WEB_INDEX_SIDE": sorted(RG["WEB_INDEX_SIDE"]), "THUMB_BASE_FOLD": sorted(BASE_FOLD)},
           "AUTH": sorted(AUTH), "CHANGED": sorted(CHANGED),
           "derivation": {
               "tau_mm": rr(TAU, 6), "med_edge_mm": rr(MED, 6),
               "R_TT_mm": rr(R_TT, 6), "R_MAX_mm": rr(R_MAX, 6),
               "thumb_joint_arcs_mm": {"CMC_head": 0.0, "MCP": rr(s_MCP, 6),
                                       "IP": rr(s_IP, 6), "TIP": rr(s_TIP, 6)},
               "index_PIP_arc_mm": rr(C.chain_arc_table(ref["jf"], "INDEX")[1], 6),
               "web_band_rings": 2, "R_TUBE_mm": rr(RG["r_tube"], 6)}},
          open(os.path.join(OUTDIR, "_tmp", "R1A_REGIONS.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("BUILD_DONE")
