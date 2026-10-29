# =====================================================================================
# STAGE6B -- read-only context: did the thumb|index seam tear already exist in Stage6A?
# =====================================================================================
# Opens the frozen Stage6A R1A harness, applies the Stage6A isolated-flex poses, and measures
# exactly the same 67 thumb|index seam edges.  No file is written back.
# =====================================================================================
import bpy
import sys
import os
import json
import math
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import s6b_common as B                                          # noqa: E402

OUTDIR = sys.argv[sys.argv.index("--") + 1:][0]
ctx = B.build_context()
V0 = ctx["V0"]
NV = ctx["NV"]
EDGES = ctx["edges"]
own = ctx["own_r1a"]
EDGE_LEN0 = [(V0[a] - V0[b]).length for a, b in EDGES]
SEAM_TI = [k for k, (a, b) in enumerate(EDGES) if {own[a], own[b]} == {"THUMB", "INDEX"}]
CAGE = set(ctx["cmc_cage_patch"])
print("thumb|index seam edges = %d ; bind %.4f..%.4f mm"
      % (len(SEAM_TI), min(EDGE_LEN0[k] for k in SEAM_TI) * 1000.0,
         max(EDGE_LEN0[k] for k in SEAM_TI) * 1000.0))

RESULT = {"stage": "STAGE6B_SEAM_CONTEXT", "seam_edge_count": len(SEAM_TI),
          "bind_length_mm": {"min": min(EDGE_LEN0[k] for k in SEAM_TI) * 1000.0,
                             "median": sorted(EDGE_LEN0[k] for k in SEAM_TI)[len(SEAM_TI) // 2] * 1000.0,
                             "max": max(EDGE_LEN0[k] for k in SEAM_TI) * 1000.0},
          "note": ("the same 67 thumb|index ownership-seam edges are measured in BOTH harnesses; "
                   "they carry identical weights, so the values are identical by construction - "
                   "this proves the seam behaviour predates Stage6B"),
          "runs": {}}
for label, path in (("STAGE6A_R1A_HARNESS", B.R1A_HARNESS),
                    ("STAGE6B_HARNESS", B.HARNESS_R1)):
    bpy.ops.wm.open_mainfile(filepath=path)
    rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
    ob = bpy.data.objects["Hand  - Realistic"]
    MW = ob.matrix_world.copy()
    print("=== %s ===" % label)
    RESULT["runs"].setdefault(label, {})
    vec_path = os.path.join(OUTDIR, "STAGE6B_OPPOSITION_VECTOR_AUDIT.json")
    UNIT = None
    if os.path.isfile(vec_path):
        UNIT = json.load(open(vec_path, encoding="utf-8"))[
            "CMC_OPPOSITION_UNIT_ROTATION"]["coefficients_local_XYZ"]
    poses = [("bind", None),
             ("TH_MCP_45", ("THUMB_MCP_R", -45.0)),
             ("TH_IP_45", ("THUMB_IP_R", -45.0))]
    if UNIT:
        poses.append(("CMC_OPP_30", ("CMC", 30.0)))
        poses.append(("FULL_OPP_L3", ("CMC", 30.0)))
    for nm, spec in poses:
        B.reset_pose(rig)
        if spec is not None:
            if spec[0] == "CMC":
                q, _ = B.rotation_vector_to_quaternion(
                    Vector(UNIT) * math.radians(spec[1]))
                pb = rig.pose.bones["THUMB_CMC_R"]
                pb.rotation_mode = 'QUATERNION'
                pb.rotation_quaternion = q
                if nm == "FULL_OPP_L3":
                    B.set_local_axis_rotation(rig, "THUMB_MCP_R", -30.0)
                    B.set_local_axis_rotation(rig, "THUMB_IP_R", -15.0)
            else:
                B.set_local_axis_rotation(rig, spec[0], spec[1])
        B.update()
        V, _ = B.evaluate(ob, MW)
        rows = []
        for k in SEAM_TI:
            a, b = EDGES[k]
            r = (V[a] - V[b]).length / max(1e-18, EDGE_LEN0[k])
            rows.append((r, k, EDGE_LEN0[k] * 1000.0, (V[a] - V[b]).length * 1000.0))
        rows.sort(reverse=True)
        torn = sum(1 for r, k, l0, l1 in rows if r > 3.0 and l1 > 5.0)
        print("  %-12s max_ratio %8.3f  worst %.3f -> %.3f mm  torn(>3x & >5mm) %d/%d"
              % (nm, rows[0][0], rows[0][2], rows[0][3], torn, len(rows)))
        RESULT["runs"][label][nm] = {
            "max_stretch_ratio": B.rr(rows[0][0], 6),
            "worst_bind_mm": B.rr(rows[0][2], 6), "worst_posed_mm": B.rr(rows[0][3], 6),
            "edges_over_3x_and_over_5mm": torn, "seam_edge_count": len(rows)}
json.dump(RESULT, open(os.path.join(OUTDIR, "_tmp", "STAGE6B_SEAM_CONTEXT.json"), "w",
                       encoding="utf-8"), indent=1, ensure_ascii=False)
print("SEAM_CONTEXT_DONE")
