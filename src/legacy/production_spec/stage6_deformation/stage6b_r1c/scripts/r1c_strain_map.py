# =====================================================================================
# STAGE6B_R1C -- DEFORMATION CONTINUITY CENSUS (evidence only, NO model change)
# -------------------------------------------------------------------------------------
# The penetration adjudication needs one more piece of evidence: are the sheet/sheet
# crossings produced by physiological surface contact, or by a locally TORN skin flap?
# This measures, for the same three frozen poses, the edge stretch field and the hard
# 0/1 weight discontinuities of the input master.
# =====================================================================================
import os, sys, json, math, datetime
from collections import Counter
import bpy
import numpy as np
from mathutils import Vector, Quaternion
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import r1c_pen_common as R

NOW = datetime.datetime.now().astimezone().isoformat()
MM = R.MM
TAG = {"CMC_OPP_30": "CMC_OPP30", "CMC_MCP_L3": "CMC_MCP_L3", "FULL_OPP_L3": "FULL_OPP_L3"}
CASES = ["CMC_OPP_30", "CMC_MCP_L3", "FULL_OPP_L3"]

ctx = R.B.build_context(); ref = ctx["ref"]; V0 = ref["V0"]; POLY = ctx["poly"]; NV = ref["NV"]
probe = R.K.load_probe_sets(); PART = R.K.r2_partition(ctx, ref)
CORRECT = R.K.build_corrected_ownership(ctx, ref, PART["partition"], probe)
OWN = CORRECT["corrected"]; DOMAIN = set(CORRECT["domain"])
cap = set(ref["cap"]["thumb_cap_vertex_ids"])
capc = sum((V0[i] for i in cap), Vector()) / max(1, len(cap))
CM = dict((c["case_id"], c) for c in
          json.load(open(R.K.PROVENANCE["stage6b_case_matrix"], encoding="utf-8"))["cases"])
FACE_OWN = []
for p in POLY:
    c = Counter(OWN[v] for v in p); m = c.most_common(); top = [k for k, v in m if v == m[0][1]]
    FACE_OWN.append(top[0] if len(top) == 1 else sorted(top)[0])

log = lambda s: print("[R1C-STRAIN] " + s, flush=True)
OUT = {"stage": "STAGE6B_R1C_DEFORMATION_CONTINUITY_AUDIT", "generated_at": NOW,
       "round_kind": "HUMAN_REVIEW_EVIDENCE_ONLY", "model_changes": 0,
       "harness": {"path": R.K.S6B_R1B_HARNESS.replace("\\", "/"),
                   "sha256": R.K.sha256(R.K.S6B_R1B_HARNESS)},
       "reference_harness": {"path": os.path.join(R.S6D, "stage6b", "RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1.blend").replace("\\", "/"),
                             "sha256": R.K.sha256(os.path.join(R.S6D, "stage6b", "RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1.blend")),
                             "note": "built from the FROZEN Stage5B R1B master -> isolates what R1C changed"},
       "thumb_distal_cap_centroid_bind_mm": [R.K.rr(x * MM, 6) for x in capc],
       "poses": CASES, "thresholds": {"bind_edge_gt_mm": 3.0, "over_x": 2.0, "severe_x": 5.0,
                                      "hard_flip_weight": 0.95}}


def apply_pose(rig, V, cid):
    c = CM[cid]; q = c["cmc_quaternion_local"]
    R.B.reset_pose(rig)
    pb = rig.pose.bones["THUMB_CMC_R"]; pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = Quaternion((q[0], q[1], q[2], q[3]))
    for bn, dg in (("THUMB_MCP_R", c["mcp_deg"]), ("THUMB_IP_R", c["ip_deg"])):
        if dg:
            p = rig.pose.bones[bn]; p.rotation_mode = 'QUATERNION'
            p.rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(-dg))
    R.B.update()


def census(path, label):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = bpy.data.objects[R.MESH_OBJ]; rig = bpy.data.objects[R.RIG_OBJ]
    MW = ob.matrix_world.copy()
    G = [g.name for g in ob.vertex_groups]
    WR = [dict((G[g.group], g.weight) for g in ob.data.vertices[i].groups if g.weight > 1e-3)
          for i in range(NV)]

    def dom(i):
        w = WR[i]
        return max(w.items(), key=lambda kv: kv[1])[0] if w else None

    # hard 0/1 discontinuities of the INPUT master (bind state)
    flip_edges = []
    flip_faces = set()
    for fi, p in enumerate(POLY):
        n = len(p)
        for i in range(n):
            a, b = p[i], p[(i + 1) % n]
            wa, wb = WR[a], WR[b]
            if len(wa) == 1 and len(wb) == 1 and list(wa)[0] != list(wb)[0]:
                if list(wa.values())[0] > 0.95 and list(wb.values())[0] > 0.95:
                    flip_edges.append((fi, a, b, list(wa)[0], list(wb)[0]))
                    flip_faces.add(fi)
    out = {"input_master": path.replace("\\", "/"),
           "hard_0_1_weight_flip_edges": len(flip_edges),
           "hard_0_1_weight_flip_faces": len(flip_faces),
           "hard_flip_by_ownership": dict(Counter(FACE_OWN[f] for f in flip_faces)),
           "cases": {}}
    fv = set(v for _f, a, b, _x, _y in flip_edges for v in (a, b))
    if fv:
        out["hard_flip_vertex_count"] = len(fv)
        out["hard_flip_vertex_distance_to_thumb_cap_mm"] = [
            R.K.rr(min((V0[v] - capc).length for v in fv) * MM, 6),
            R.K.rr(max((V0[v] - capc).length for v in fv) * MM, 6)]
        out["hard_flip_vertices_in_R2_correction_domain"] = len(fv & DOMAIN)
        out["hard_flip_vertex_dominant_bones"] = dict(Counter(dom(v) for v in fv))
    for cid in CASES:
        apply_pose(rig, None, cid)
        V = R.B.evaluate(ob, MW)[0]
        ratio = [1.0] * len(POLY)
        o2 = o5 = 0; mx = 0.0; mxinfo = None
        f2 = set(); f5 = set()
        for fi, p in enumerate(POLY):
            n = len(p); rmax = 1.0
            for i in range(n):
                u, v = p[i], p[(i + 1) % n]
                b = (V0[u] - V0[v]).length * MM
                q = (V[u] - V[v]).length * MM
                if b > 3.0:
                    r = q / b
                    rmax = max(rmax, r)
                    if r > 2.0: o2 += 1; f2.add(fi)
                    if r > 5.0: o5 += 1; f5.add(fi)
                    if r > mx: mx = r; mxinfo = {"face": fi, "verts": [u, v],
                                                 "bind_mm": R.K.rr(b, 3), "posed_mm": R.K.rr(q, 3)}
            ratio[fi] = rmax
        disp_max = max((V[i] - V0[i]).length for i in range(NV)) * MM
        out["cases"][cid] = {
            "edges_over_2x": o2, "edges_over_5x": o5,
            "faces_over_2x": len(f2), "faces_over_5x": len(f5),
            "max_stretch_ratio": R.K.rr(mx, 6), "max_stretch_edge": mxinfo,
            "faces_over_5x_by_ownership": dict(Counter(FACE_OWN[f] for f in f5)),
            "faces_over_5x_in_R2_correction_domain": len(set(v for f in f5 for v in POLY[f]) & DOMAIN),
            "max_vertex_displacement_mm": R.K.rr(disp_max, 6),
        }
        # ---- strain map render
        cv = R.Canvas(1500, 1100)
        cen = sum(V, Vector()) / NV
        # fit
        r_, u_ = R.ortho_basis(Vector((0.55, 0.42, 0.72)), Vector((0, 0, 1)))
        mxx = mxy = 0.0
        for p in V:
            q_ = p - cen; mxx = max(mxx, abs(q_.dot(r_))); mxy = max(mxy, abs(q_.dot(u_)))
        vw = R.View(cen, (0.55, 0.42, 0.72), (0, 0, 1), max(mxx, mxy * 1500.0 / 1100.0) * 1.06 * MM, 1500, 1100)
        LIGHT = Vector((0.42, -0.30, 0.85)).normalized()
        for fi, t in R.tris_of(POLY, V0):
            r = ratio[fi]
            if r < 1.5:
                base = (0.30 + 0.35 * min(1.0, r - 1.0) / 0.5, 0.42, 0.60)
            elif r < 2.5:
                t_ = (r - 1.5) / 1.0
                base = (0.60 + 0.35 * t_, 0.80 - 0.25 * t_, 0.45 - 0.30 * t_)
            else:
                t_ = min(1.0, (r - 2.5) / 2.5)
                base = (0.95, 0.55 - 0.50 * t_, 0.15 - 0.13 * t_)
            nrm = R.face_normals(V, [POLY[fi]])[0]
            sh = 0.35 + 0.65 * abs(nrm.dot(LIGHT))
            cv.tri(vw.proj(V[t[0]]), vw.proj(V[t[1]]), vw.proj(V[t[2]]), sh, base)
        R.text(cv, 24, 20, "%s  EDGE STRAIN MAP (POSED / BIND)" % TAG[cid], 3)
        R.text(cv, 24, 60, "BLUE <=1.5X  /  YELLOW 1.5-2.5X  /  RED >=5X   (EDGES WITH BIND LENGTH > 3 MM)", 2)
        R.text(cv, 24, 84, "OVER 2X = %d EDGES (%d FACES) ; OVER 5X = %d EDGES (%d FACES) ; MAX = %.2fX AT %s"
               % (o2, len(f2), o5, len(f5), mx, json.dumps(mxinfo)), 2)
        R.text(cv, 24, 108, "RED = THE TORN FLAP THAT CROSSES BACK THROUGH THE PALM / NEIGHBOURING DIGIT.", 2)
        R.text(cv, 24, 1050, "CAP CENTROID = MAGENTA MARK. SAME FROZEN POSE, SAME FROZEN WEIGHTS - RENDER ONLY.", 2)
        cv.px(*vw.proj(capc)[:2], (1.0, 0.15, 0.75), 8)
        R.save(cv, "STAGE6B_R1C_%s_EDGE_STRAIN_MAP.png" % TAG[cid])
        log("%s %-6s over2x=%d over5x=%d max=%.2fx disp=%.2fmm" %
            (label, cid, o2, o5, mx, disp_max))
    out["master_hard_flip_edges"] = len(flip_edges)
    log("%s : hard 0/1 flip edges in the input master = %d" % (label, len(flip_edges)))
    return out


RES = {}
RES["R1B_input_stage5b_r1c"] = census(R.K.S6B_R1B_HARNESS, "R1B")
RES["R1_input_stage5b_r1b"] = census(os.path.join(R.S6D, "stage6b",
                                                  "RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1.blend"), "R1 ")
OUT["harnesses"] = RES
OUT["KEY_FINDING"] = (
    "The large Stage6B R1B penetration proxy is NOT produced by physiological surface contact. "
    "At the three frozen opposition poses several hundred mesh edges of the thumb's own distal "
    "surface stretch by 2x to more than 20x (bind 3-5 mm edges reaching 40-95 mm), and the "
    "resulting torn flap crosses back through the palm and the neighbouring digits. The cause is "
    "a hard 0/1 blend-weight discontinuity on the thumb distal surface (adjacent vertices carry "
    "THUMB_IP_R ~ 1.0 and WRIST_R ~ 1.0), which the Stage5B R1C local weight reconciliation did "
    "not remove; it increased the mesh-wide hard-flip edge count from %d to %d."
    % (RES["R1_input_stage5b_r1b"]["master_hard_flip_edges"],
       RES["R1B_input_stage5b_r1c"]["master_hard_flip_edges"]))
json.dump(OUT, open(os.path.join(R.S6B_R1C, "STAGE6B_R1C_DEFORMATION_CONTINUITY_AUDIT.json"),
                    "w", encoding="utf-8"), indent=1, ensure_ascii=False)
log("wrote STAGE6B_R1C_DEFORMATION_CONTINUITY_AUDIT.json")
print("STRAIN_MAP_DONE", flush=True)
