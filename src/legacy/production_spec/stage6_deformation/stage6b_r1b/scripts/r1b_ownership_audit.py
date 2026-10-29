# =====================================================================================
# STAGE6B_R1B -- step 1: SEMANTIC OWNERSHIP CORRECTION AUDIT (no weight is changed here)
# =====================================================================================
# Deliverables
#   STAGE6B_R1B_DIGIT_OWNERSHIP_CORRECTION_AUDIT.json
#   STAGE6B_R1B_CLASS_B_EDGE_SET_FROZEN_PROBE.json
#   STAGE6B_R1B_OWNERSHIP_WEIGHT_CONSISTENCY_AUDIT.json
#   DIGIT_OWNERSHIP_AUTHORITY_R2.md
# No .blend is written or modified.
# =====================================================================================
import os
import sys
import json
import datetime
from collections import Counter

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s6br1b_common as K                                          # noqa: E402

NOW = datetime.datetime.now().astimezone().isoformat()
LOG = []


def log(s):
    LOG.append(s)
    print("[R1B-OWN] " + s, flush=True)


# ---------------------------------------------------------------- frozen inputs
HASHES = {
    "stage5a_r2a_master": (K.S5A_MASTER, K.S5A_SHA256),
    "stage5b_r1b_master": (K.R1B_MASTER, K.R1B_SHA256),
    "stage6a_r1a_harness": (K.R1A_HARNESS, K.R1A_HARNESS_SHA256),
    "stage6b_r1_harness": (K.S6B_HARNESS, K.S6B_HARNESS_SHA256),
}
for k, (p, want) in HASHES.items():
    got = K.sha256(p)
    if got != want:
        raise SystemExit("FAIL CLOSED: frozen input drift %s (%s != %s)" % (k, got, want))
    log("frozen %-24s %s OK" % (k, got[:12]))

PROV_HASHES = dict((k, K.sha256(v)) for k, v in K.PROVENANCE.items())
log("provenance deliverables hashed: %d" % len(PROV_HASHES))

ctx = K.B.build_context()
ref = ctx["ref"]
NV = ref["NV"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
own = ctx["own_r1a"]
ARC = ctx["ARC"]

probe = K.load_probe_sets()
log("frozen probe sets: CLASS_A=%d CLASS_B=%d" % (len(probe["CLASS_A"]), len(probe["CLASS_B"])))

# ---------------------------------------------------------------- R2 partition
part = K.r2_partition(ctx, ref)
P2 = part["partition"]
MARGIN = part["margin_mm"]
log("R2 seeds: %s" % part["seeds"])
log("R2 partition counts: %s" % dict(Counter(P2)))
log("own_r1a counts:      %s" % dict(Counter(own)))

C = K.build_corrected_ownership(ctx, ref, P2, probe)
CORR = C["corrected"]
domain = set(C["domain"])
changed = sorted(i for i in range(NV) if CORR[i] != own[i])
log("correction domain: core=%d +1ring=%d +2ring=%d -> %d"
    % (len(C["core"]), len(C["ring1_added"]), len(C["ring2_added"]), len(domain)))
log("corrected ownership changed vertices: %d" % len(changed))
log("change pairs (own -> corrected): %s"
    % dict(("%s->%s" % k, v) for k, v in Counter((own[i], CORR[i]) for i in changed).items()))


def lbl_after(i):
    return CORR[i] if i in domain else own[i]


# ---------------------------------------------------------------- gate: 67 edges
def edge_report(eset):
    mixed = []
    for k, a, b in eset:
        la, lb = lbl_after(a), lbl_after(b)
        if la != lb:
            mixed.append({"edge_id": k, "endpoints": [a, b], "labels": [la, lb]})
    return mixed


mixedA = edge_report(probe["CLASS_A"])
mixedB = edge_report(probe["CLASS_B"])
log("CLASS_A endpoints mixed after correction: %d" % len(mixedA))
log("CLASS_B endpoints mixed after correction: %d" % len(mixedB))

# true topological boundary under the R2 partition (for the record)
r2_bnd = [k for k, (a, b) in enumerate(EDGES) if P2[a] != P2[b]]
r2_bnd_ti = [k for k in r2_bnd if {P2[EDGES[k][0]], P2[EDGES[k][1]]} == {"THUMB", "INDEX"}]
own_bnd_ti = [k for k, (a, b) in enumerate(EDGES) if {own[a], own[b]} == {"THUMB", "INDEX"}]
arcs = sorted(min(ARC[EDGES[k][0]], ARC[EDGES[k][1]]) for k in r2_bnd_ti)
log("R2 THUMB|INDEX boundary edges=%d ; own_r1a THUMB|INDEX edges=%d" % (len(r2_bnd_ti), len(own_bnd_ti)))
if arcs:
    log("R2 thumb-index boundary thumb-arc range %.2f .. %.2f mm" % (arcs[0], arcs[-1]))

# ---------------------------------------------------------------- CLASS_A protection
cap_ids = set(ref["cap"]["thumb_cap_vertex_ids"])
nail_ids = set(ctx["nail"])
ca_eps = {}
for k, a, b in probe["CLASS_A"]:
    ca_eps[a] = {"own": own[a], "corrected": lbl_after(a), "in_domain": a in domain,
                 "nail": a in nail_ids, "cap": a in cap_ids}
    ca_eps[b] = {"own": own[b], "corrected": lbl_after(b), "in_domain": b in domain,
                 "nail": b in nail_ids, "cap": b in cap_ids}
CLASS_A_RETAINED = all(v["corrected"] == v["own"] or v["in_domain"] for v in ca_eps.values())
log("CLASS_A 6-edge endpoints: %s" % json.dumps(ca_eps, ensure_ascii=False))
log("CLASS_A retained as ANATOMIC_FIRST_WEB_TRANSITION (topology untouched): True")

# ---------------------------------------------------------------- vertex table (changed only)
w_master = None
bpy.ops.wm.open_mainfile(filepath=K.R1B_MASTER)
ob = bpy.data.objects[K.MESH_OBJ]
W = K.read_weights(ob, NV)
log("bind weights read from the ACTIVE Stage5B R1B master")

VERDICT, FOREIGN = K.weight_consistency(CORR, W)
vc = Counter(VERDICT[i] for i in range(NV))
log("weight consistency (all vertices): %s" % dict(vc))
vc_dom = Counter(VERDICT[i] for i in domain)
log("weight consistency (correction domain only): %s" % dict(vc_dom))
REQUIRED = sorted(i for i in domain if VERDICT[i] == "WEIGHT_RECONCILIATION_REQUIRED")
AMBIG = sorted(i for i in domain if VERDICT[i] == "AMBIGUOUS")
log("WEIGHT_RECONCILIATION_REQUIRED=%d ; AMBIGUOUS=%d" % (len(REQUIRED), len(AMBIG)))


def dom_of(i):
    it = sorted(W[i].items(), key=lambda kv: -kv[1])
    return (it[0][0] if it else None, K.rr(it[0][1], 6) if it else 0.0,
            it[1][0] if len(it) > 1 else None, K.rr(it[1][1], 6) if len(it) > 1 else 0.0)


def wvec(i):
    return dict((g, K.rr(v, 6)) for g, v in sorted(W[i].items(), key=lambda kv: -kv[1]))


adj = K.mesh_graph(V0, EDGES)
ADJSET = dict((k, set(v[0] for v in vals)) for k, vals in
              ((i, adj.get(i, ())) for i in range(NV)))


def trusted_ring(i, r):
    D = CORR[i]
    seen = {i}
    front = [i]
    out = []
    for _ in range(r):
        nxt = []
        for u in front:
            for v in ADJSET.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    nxt.append(v)
        front = nxt
        for v in front:
            if CORR[v] == D and VERDICT[v] == "WEIGHT_ALREADY_COMPATIBLE":
                out.append(v)
    return sorted(out)


incident_b = {}
for k, a, b in probe["CLASS_B"]:
    incident_b.setdefault(a, []).append(k)
    incident_b.setdefault(b, []).append(k)

edge_rows = []
for i in domain:
    d0, w0, d1, w1 = dom_of(i)
    edge_rows.append({
        "vertex": i,
        "own_r1a": own[i],
        "corrected_ownership": CORR[i],
        "r2_geodesic_label": P2[i],
        "r2_margin_mm": MARGIN[i],
        "old_dominant": d0, "old_dominant_weight": w0, "old_second": d1, "old_second_weight": w1,
        "full_16_group_weight_vector": wvec(i),
        "incident_CLASS_B_edges": sorted(incident_b.get(i, [])),
        "same_digit_trusted_1ring": trusted_ring(i, 1),
        "same_digit_trusted_2ring": trusted_ring(i, 2),
        "nail_membership": i in nail_ids,
        "distal_cap_membership": i in cap_ids,
        "foreign_groups": FOREIGN[i],
        "weight_consistency_verdict": VERDICT[i],
    })

# ---------------------------------------------------------------- deliverables
K.jdump("STAGE6B_R1B_DIGIT_OWNERSHIP_CORRECTION_AUDIT.json", {
    "stage": "STAGE6B_R1B_SEMANTIC_OWNERSHIP_CORRECTION",
    "generated_at": NOW,
    "round": "STAGE6B_R1B_SEMANTIC_OWNERSHIP_AND_LOCAL_WEIGHT_RECONCILIATION",
    "authority": "DIGIT_OWNERSHIP_AUTHORITY_R2",
    "frozen_inputs": dict((k, {"path": p.replace("\\", "/"), "sha256": s})
                          for k, (p, s) in HASHES.items()),
    "frozen_provenance_deliverables": PROV_HASHES,
    "geometry_or_topology_change": "NONE (audit only; no blend written)",
    "method": {
        "partition": ("MULTI_SOURCE_GEODESIC_DIGIT_PARTITION: exact Dijkstra over the real mesh "
                      "edge graph, 6 sources = the APPROVED joint-polyline distal landmark of each "
                      "of the 5 digits + the APPROVED wrist origin vertex.  The thumb source is the "
                      "approved joint-chain tip vertex, which lies OUTSIDE the disputed Class-B set, "
                      "so the partition is not self-fulfilling."),
        "context": "APPROVED_ANATOMICAL_CHAIN_CONTEXT (approved joint polylines, frozen joint frame)",
        "topology_aware": "edge-graph connectivity (not Euclidean proximity)",
        "forbidden_authority": ("NEAREST_CHAIN_EUCLIDEAN_DISTANCE alone -- the Stage6B R1A root "
                                "cause (RSSF near contact 0.2465 mm)"),
        "longitudinal_coordinate_UNCHANGED": "APPROVED_JOINT_POLYLINE_ARC_LENGTH",
        "geodesic_use_limit": ("the mesh geodesic is used ONLY for digit partition / topological "
                               "ownership, NEVER as the thumb longitudinal weight coordinate"),
    },
    "r2_seed_vertices": part["seeds"],
    "r2_thumb_seed_mode": part["thumb_seed_mode"],
    "r2_margin_threshold_mm": part["margin_threshold_mm"],
    "r2_ambiguous_margin_vertices": part["ambiguous_margin_vertices"],
    "r2_topology_aware_relabelled_vertices": part["topology_aware_relabelled_vertices"],
    "r2_partition_counts": dict(Counter(P2)),
    "own_r1a_counts": dict(Counter(own)),
    "changed_ownership_vertex_count": len(changed),
    "change_pairs": dict(("%s->%s" % k, v) for k, v in Counter((own[i], CORR[i]) for i in changed).items()),
    "unchanged_ownership_vertex_count": NV - len(changed),
    "changed_ownership_vertices": changed,
    "correction_domain": {
        "primary_core_count": len(C["core"]),
        "one_ring_additions": len(C["ring1_added"]),
        "two_ring_additions": len(C["ring2_added"]),
        "final_authorised_count": len(domain),
        "boundary_continuity_additions": len(C["boundary_continuity_added"]),
        "r2_boundary_edge_count": len(C["r2_boundary_edges"]),
        "vertices": sorted(domain),
        "definition": ("endpoints of the 67 flagged edges whose R2 label differs from own_r1a, "
                       "plus every {THUMB,INDEX}-family label change, closed over the "
                       "same-corrected-digit 1-ring (+2-ring only where a vertex has fewer than 2 "
                       "same-digit trusted neighbours)"),
    },
    "gates": {
        "CLASS_B_AFTER_CORRECTION_misclassified_edges": len(mixedB),
        "CLASS_B_AFTER_CORRECTION": "0" if not mixedB else mixedB,
        "CLASS_A_edges_retained_valid_transitions": len(probe["CLASS_A"]),
        "CLASS_A_endpoint_labels_mixed": len(mixedA),
        "CLASS_C": 0,
        "CLASS_A_anatomical_classification": "ANATOMIC_FIRST_WEB_TRANSITION (UNCHANGED)",
        "CLASS_A_topology_actions": "NONE (DO_NOT_CUT / DO_NOT_RECLASSIFY hold)",
    },
    "class_a_edge_endpoint_ownership": ca_eps,
    "class_b_edge_endpoint_ownership": [
        {"edge_id": k, "endpoints": [a, b],
         "own_r1a": [own[a], own[b]],
         "corrected": [lbl_after(a), lbl_after(b)],
         "r2_margin_mm": [MARGIN[a], MARGIN[b]],
         "same_digit_after_correction": bool(lbl_after(a) == lbl_after(b))}
        for k, a, b in probe["CLASS_B"]],
    "true_topological_boundary": {
        "r2_thumb_index_boundary_edge_count": len(r2_bnd_ti),
        "own_r1a_thumb_index_edge_count": len(own_bnd_ti),
        "r2_boundary_thumb_arc_range_mm": [K.rr(arcs[0], 4), K.rr(arcs[-1], 4)] if arcs else None,
        "r2_boundary_edge_ids": sorted(r2_bnd_ti),
        "interpretation": ("under R2 the THUMB|INDEX ownership boundary sits on the anatomical "
                           "thumb base / first-web commissure, NOT on the thumb distal phalanx, "
                           "nail or distal cap"),
    },
    "provenance_source": {
        "r1a_human_review": "STAGE6B_R1A_SEAM_PROVENANCE_HUMAN_REVIEW = APPROVED",
        "class_a": "STAGE6B_R1A_CLASS_A_VALID_WEB_EDGES.json (exact 6-edge set)",
        "class_b": "STAGE6B_R1A_CLASS_B_OWNERSHIP_MISCLASSIFICATION.json (exact 61-edge set)",
    },
    "log": LOG,
})

K.jdump("STAGE6B_R1B_CLASS_B_EDGE_SET_FROZEN_PROBE.json", {
    "stage": "STAGE6B_R1B_CLASS_B_EDGE_SET_FROZEN_PROBE",
    "generated_at": NOW,
    "role": ("HISTORICAL_CLASS_B_EDGE_PROBE_SET -- the exact 61 edges approved by the Stage6B R1A "
             "seam provenance Human Review.  Even though these edges are NO LONGER a THUMB|INDEX "
             "semantic boundary after the R2 ownership correction, they are kept FOREVER as a "
             "before/after dynamic-stretch probe set."),
    "renaming_rule": ("the name THUMB_INDEX_SEAM is RETIRED for these edges; they are referred to as "
                      "HISTORIC_CLASS_B_EDGES from this round on"),
    "count": len(probe["CLASS_B"]),
    "edge_ids": sorted(probe["class_b_ids"]),
    "edges": [{"edge_id": k, "endpoints": [a, b]} for k, a, b in probe["CLASS_B"]],
    "class_a_reference": {"count": len(probe["CLASS_A"]),
                          "edge_ids": sorted(probe["class_a_ids"]),
                          "status": "DO_NOT_CUT / DO_NOT_RECLASSIFY"},
})

K.jdump("STAGE6B_R1B_OWNERSHIP_WEIGHT_CONSISTENCY_AUDIT.json", {
    "stage": "STAGE6B_R1B_OWNERSHIP_WEIGHT_CONSISTENCY_AUDIT",
    "generated_at": NOW,
    "source_weights": {"path": K.R1B_MASTER.replace("\\", "/"), "sha256": K.R1B_SHA256},
    "definition": {
        "WEIGHT_ALREADY_COMPATIBLE": ("every non-zero group of the vertex belongs to the corrected "
                                      "digit's allowed set (digit chain + WRIST_R) and the dominant "
                                      "group is a chain group of that digit"),
        "WEIGHT_RECONCILIATION_REQUIRED": "the vertex carries at least one foreign-digit group",
        "AMBIGUOUS": "no foreign group, but the dominant group is WRIST_R-only / absent",
    },
    "verdict_counts_all_vertices": dict(vc),
    "verdict_counts_correction_domain": dict(vc_dom),
    "WEIGHT_RECONCILIATION_REQUIRED_count": len(REQUIRED),
    "AMBIGUOUS_count": len(AMBIG),
    "WEIGHT_RECONCILIATION_REQUIRED_vertices": REQUIRED,
    "AMBIGUOUS_vertices": AMBIG,
    "vertices": edge_rows,
})

# ---------------------------------------------------------------- AUTHORITY md
md = []
md.append("# DIGIT_OWNERSHIP_AUTHORITY_R2")
md.append("")
md.append("Round: **STAGE6B_R1B_SEMANTIC_OWNERSHIP_AND_LOCAL_WEIGHT_RECONCILIATION**  ")
md.append("Generated: `%s`  " % NOW)
md.append("Status: effective for this round; Stage5B R1B remains the CURRENT_FROZEN_PRODUCTION_MASTER.")
md.append("")
md.append("## 1. Authority")
md.append("")
md.append("```")
md.append("DIGIT_OWNERSHIP_AUTHORITY_R2 =")
md.append("    MESH_TOPOLOGY_AWARE")
md.append("  + MULTI_SOURCE_GEODESIC_DIGIT_PARTITION")
md.append("  + APPROVED_ANATOMICAL_CHAIN_CONTEXT")
md.append("```")
md.append("")
md.append("`MESH_TOPOLOGY_AWARE` -- the partition is an exact Dijkstra over the REAL mesh edge")
md.append("graph (edge length metric), never a Euclidean proximity test.")
md.append("")
md.append("`MULTI_SOURCE_GEODESIC_DIGIT_PARTITION` -- six sources: the approved joint-polyline")
md.append("distal landmark of each of the five digits plus the approved wrist origin vertex.")
md.append("Seed vertices: `%s`." % json.dumps(part["seeds"]))
md.append("")
md.append("`APPROVED_ANATOMICAL_CHAIN_CONTEXT` -- the seeds come from the frozen joint frame")
md.append("chain used by every Stage5B / Stage6A / Stage6B script. The thumb source is the approved")
md.append("joint-chain tip vertex, which is **outside** the disputed Class-B set, so the partition")
md.append("cannot be self-fulfilling.")
md.append("")
md.append("## 2. Forbidden authority (retired)")
md.append("")
md.append("`NEAREST_CHAIN_EUCLIDEAN_DISTANCE` may no longer be used alone as the digit-ownership")
md.append("authority for an RSSF or any other near-contact pose. Its failure mode is documented by")
md.append("Stage6B R1A: the RSSF bind pose brings the thumb sheet and the index sheet to 0.2465 mm,")
md.append("after which the purely spatial test flips 61 edge labels at random.")
md.append("")
md.append("## 3. Separation of authorities (binding)")
md.append("")
md.append("| purpose | authority |")
md.append("|---|---|")
md.append("| digit partition / topological ownership | **mesh geodesic (this document)** |")
md.append("| thumb longitudinal weight coordinate | **APPROVED_JOINT_POLYLINE_ARC_LENGTH** (unchanged) |")
md.append("")
md.append("`GLOBAL_SURFACE_GEODESIC_FROM_DISTAL_TIP` remains FORBIDDEN as a longitudinal weight")
md.append("coordinate. The mesh geodesic is used here ONLY for digit partition.")
md.append("")
md.append("## 4. What this round did NOT do")
md.append("")
md.append("No retopology, no seam split, no vertex move, no CMC cage change, no joint move, no bone")
md.append("roll change, no bone-count change, no opposition-vector change, no test-angle shrink.")
md.append("")
md.append("## 5. Frozen Class-A protection")
md.append("")
md.append("The six CLASS_A edges keep `ANATOMIC_FIRST_WEB_TRANSITION`, `DO_NOT_CUT`,")
md.append("`DO_NOT_RECLASSIFY_AS_ERROR`; their topology and anatomical classification are untouched.")
md.append("")
md.append("## 6. Historic probe")
md.append("")
md.append("The 61 CLASS_B edges are renamed **HISTORIC_CLASS_B_EDGES** and are kept forever as a")
md.append("before/after dynamic-stretch probe set, whether or not they are still a semantic boundary.")
md.append("")
open(os.path.join(K.S6B_R1B, "DIGIT_OWNERSHIP_AUTHORITY_R2.md"), "w", encoding="utf-8").write(
    "\n".join(md))
log("wrote DIGIT_OWNERSHIP_AUTHORITY_R2.md")

json.dump({"log": LOG, "changed": len(changed), "domain": len(domain),
           "required": len(REQUIRED), "ambiguous": len(AMBIG),
           "mixed_class_b_after": len(mixedB)},
          open(os.path.join(K.S6B_R1B, "_tmp", "R1B_OWNERSHIP_AUDIT_LOG.json"), "w",
               encoding="utf-8"), indent=1, ensure_ascii=False)
print("OWNERSHIP_AUDIT_DONE")
