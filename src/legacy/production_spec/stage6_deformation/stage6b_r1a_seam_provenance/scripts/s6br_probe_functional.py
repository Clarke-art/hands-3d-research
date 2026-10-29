# =====================================================================================
# STAGE6B_R1A -- focused probe: functional ownership (weights) + geometry + seam topology
# =====================================================================================
import os
import sys
import json
import collections

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s6br_common as F                                              # noqa: E402
import r1a_common as RC                                              # noqa: E402

OUT = os.path.join(F.S6B_R1A, "_tmp")
MM = F.MM
LOG = []


def log(s):
    LOG.append(s)
    print("[S6BR-PROBE] " + s)


ctx = F.B.build_context()
NV = ctx["NV"]
ref = ctx["ref"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
TOPO = ref["TOPO0"]
MAT = ref["MAT0"]
own = ctx["own_r1a"]
OWN_RAW = ref["OWN_V"]
ARC = ctx["ARC"]
jf = ref["jf"]
segs = F.bone_segments(jf)
own_set = collections.Counter(own)

log("ownership census (own_r1a): %s" % dict(own_set))
log("first_web verts=%d ; nail=%d ; cap=%d ; thenar=%d"
    % (len(ctx["first_web"]), len(ctx["nail"]), len(ctx["cap"]), len(ctx["thenar"])))
if ctx["first_web"]:
    fw = sorted(ctx["first_web"])
    log("first_web thumb-arc range: %.3f .. %.3f ; lateral %.3f .. %.3f"
        % (min(ARC[i] for i in fw), max(ARC[i] for i in fw),
           min(ref["dchain"][i]["THUMB"] for i in fw),
           max(ref["dchain"][i]["THUMB"] for i in fw)))

# ---- bone geometry sanity
log("--- locator bones (world head -> tail), mm ---")
for n in ["THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R", "THUMB_TIP_R",
          "INDEX_MCP_R", "INDEX_PIP_R", "INDEX_DIP_R", "INDEX_TIP_R", "WRIST_R"]:
    if n in segs:
        h, t = segs[n]
        log("  %-14s head=%s tail=%s" % (n, F.v3(h * MM, 4), F.v3(t * MM, 4)))
d_tip_i = ((segs["THUMB_TIP_R"][0] - segs["INDEX_MCP_R"][0]).length * MM)
d_tip_ipip = ((segs["THUMB_TIP_R"][0] - segs["INDEX_PIP_R"][0]).length * MM)
log("THUMB_TIP head -> INDEX_MCP head = %.4f mm ; -> INDEX_PIP head = %.4f mm"
    % (d_tip_i, d_tip_ipip))

# ---- read the ACTIVE production skin master weights
bpy.ops.wm.open_mainfile(filepath=F.R1B_MASTER)
ob = bpy.data.objects[F.MESH_OBJ]
W = F.read_weights(ob, NV)
grp_names = sorted(g.name for g in ob.vertex_groups)
log("R1B vertex groups (%d): %s" % (len(grp_names), grp_names))
MAT_NAMES = [m.name if m else None for m in ob.data.materials]
log("material slots: %s" % MAT_NAMES)

S6B = F.B.S6B
seam = json.load(open(os.path.join(S6B, "STAGE6B_DIGIT_SEAM_DEFORM_AUDIT.json"),
                      encoding="utf-8"))


def wvec(v):
    return dict((k, F.rr(x, 6)) for k, x in sorted(W[v].items(), key=lambda kv: -kv[1]))


def dom(v):
    if not W[v]:
        return None, 0.0, None, 0.0
    it = sorted(W[v].items(), key=lambda kv: -kv[1])
    return it[0][0], it[0][1], (it[1][0] if len(it) > 1 else None), (it[1][1] if len(it) > 1 else 0.0)


SEAM_TI = [k for k, (a, b) in enumerate(EDGES)
           if {own[a], own[b]} == {"THUMB", "INDEX"}]

log("")
log("=== per-edge FUNCTIONAL ownership (dominant deform group) ===")
log("%-6s %6s | %-6s %-16s %6s %-16s | %-6s %-16s %6s %-16s"
    % ("edge", "len", "T.v", "T.dom", "T.w", "T.second", "I.v", "I.dom", "I.w", "I.second"))
func = {}
for k in sorted(SEAM_TI):
    a, b = EDGES[k]
    if own[a] != "THUMB":
        a, b = b, a
    da, wa, sa, wsa = dom(a)
    db, wb, sb, wsb = dom(b)
    func[k] = {"T": a, "I": b, "T_dom": da, "T_w": wa, "T_2nd": sa, "T_2ndw": wsa,
               "I_dom": db, "I_w": wb, "I_2nd": sb, "I_2ndw": wsb}
    log("%-6d %6.3f | v%-5d %-16s %6.3f %-16s | v%-5d %-16s %6.3f %-16s"
        % (k, (V0[a] - V0[b]).length * MM, a, str(da), wa, str(sa), b, str(db), wb, str(sb)))

# functional cross-tab: THUMB-owned endpoint whose dominant group is an INDEX group (or vice versa)
mismatch_T = [k for k in SEAM_TI if func[k]["T_dom"] and func[k]["T_dom"].startswith("INDEX")]
mismatch_I = [k for k in SEAM_TI if func[k]["I_dom"] and func[k]["I_dom"].startswith("THUMB")]
log("")
log("T endpoint whose DOMINANT group is an INDEX group : %d edges %s" % (len(mismatch_T), mismatch_T))
log("I endpoint whose DOMINANT group is a THUMB group  : %d edges %s" % (len(mismatch_I), mismatch_I))

# ---- seam graph connectivity among the 67 edges
adj = collections.defaultdict(set)
for k in SEAM_TI:
    a, b = EDGES[k]
    adj[a].add(b)
    adj[b].add(a)
verts = set(adj)
seen = set()
comps = []
for v in sorted(verts):
    if v in seen:
        continue
    stack = [v]
    comp = set()
    while stack:
        u = stack.pop()
        if u in comp:
            continue
        comp.add(u)
        seen.add(u)
        for w in adj[u]:
            if w not in comp:
                stack.append(w)
    comps.append(comp)
log("")
log("seam endpoint graph: %d vertices, %d components" % (len(verts), len(comps)))
for c in sorted(comps, key=lambda c: -len(c)):
    ss = sorted(ARC[i] for i in c)
    nT = sum(1 for i in c if own[i] == "THUMB")
    log("  comp size=%-3d THUMB=%-3d INDEX=%-3d thumb_arc %.2f..%.2f"
        % (len(c), nT, len(c) - nT, ss[0], ss[-1]))
deg = collections.Counter(len(adj[v]) for v in verts)
log("endpoint degree histogram: %s" % dict(deg))

# ---- are the two surfaces actually coincident/welded? nearest opposite-surface distance
from mathutils.kdtree import KDTree
thumb_v = [i for i in range(NV) if own[i] == "THUMB"]
index_v = [i for i in range(NV) if own[i] == "INDEX"]
kt = KDTree(len(thumb_v))
for n, i in enumerate(thumb_v):
    kt.insert(V0[i], n)
kt.balance()
mind = 1e9
mind_i = None
for i in index_v:
    co, n, d = kt.find(V0[i])
    if d * MM < mind:
        mind = d * MM
        mind_i = (i, thumb_v[n])
log("min distance INDEX-owned vertex -> THUMB-owned vertex = %.4f mm (pair %s)" % (mind, mind_i))

json.dump({"per_edge_functional": func,
           "functional_mismatch_THUMB_endpoint_index_driven": mismatch_T,
           "functional_mismatch_INDEX_endpoint_thumb_driven": mismatch_I,
           "seam_components": [sorted(c) for c in comps],
           "degree_hist": dict(deg),
           "min_index_to_thumb_vertex_distance_mm": F.rr(mind, 6),
           "min_distance_pair": list(mind_i) if mind_i else None,
           "weights": dict((str(k), {"T": wvec(EDGES[k][0] if own[EDGES[k][0]] == "THUMB"
                                               else EDGES[k][1]),
                                     "I": wvec(EDGES[k][1] if own[EDGES[k][1]] == "INDEX"
                                               else EDGES[k][0])})
                           for k in SEAM_TI),
           "log": LOG},
          open(os.path.join(OUT, "S6BR_PROBE_FUNCTIONAL.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("S6BR_PROBE_DONE")
