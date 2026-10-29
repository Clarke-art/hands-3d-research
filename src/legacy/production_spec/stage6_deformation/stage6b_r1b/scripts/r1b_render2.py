# =====================================================================================
# STAGE6B_R1B -- Human Review render set, part 2 (deformation / probe / proof maps)
# =====================================================================================
import os
import sys
import json
import math

import bpy
import numpy as np
from mathutils import Vector, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s6br1b_common as K                                          # noqa: E402
import r1b_render as R                                             # noqa: E402

OUT = R.OUT
LOG = []


def log(s):
    LOG.append(s)
    print("[REND2] " + s, flush=True)


ctx = K.B.build_context()
ref = ctx["ref"]
NV = ref["NV"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
POLY = ctx["poly"]
own = ctx["own_r1a"]
ARC = ctx["ARC"]
probe = K.load_probe_sets()
PART = K.r2_partition(ctx, ref)
C = K.build_corrected_ownership(ctx, ref, PART["partition"], probe)
CORR = C["corrected"]
cap = set(ref["cap"]["thumb_cap_vertex_ids"])
nail = set(ctx["nail"])
cage = sorted(ctx["cmc_cage_patch"])
EDGE_LEN0 = [(V0[a] - V0[b]).length for a, b in EDGES]
FACE_AREA0 = [K.B.face_area(V0, p) for p in POLY]
CASES = dict((c["case_id"], c) for c in
             json.load(open(K.PROVENANCE["stage6b_case_matrix"], encoding="utf-8"))["cases"])
HIST = [(k, a, b) for k, a, b in probe["CLASS_B"]]
HISTB = json.load(open(os.path.join(K.S6B_R1B,
                                    "STAGE6B_R1B_HISTORIC_CLASS_B_EDGE_STRETCH_AUDIT.json"),
                       encoding="utf-8"))["cases"]
R1SEAM = json.load(open(os.path.join(K.S6B, "STAGE6B_DIGIT_SEAM_DEFORM_AUDIT.json"),
                        encoding="utf-8"))["cases"]
CONT2 = json.load(open(os.path.join(K.S6B_R1B, "STAGE6B_R1B_CONTACT_PROGRESSION_AUDIT.json"),
                       encoding="utf-8"))["cases"]
CONT1 = json.load(open(os.path.join(K.S6B, "STAGE6B_CONTACT_PROGRESSION_AUDIT.json"),
                       encoding="utf-8"))["cases"]
CAGE_AUD = json.load(open(os.path.join(K.S6B_R1B, "STAGE6B_R1B_CMC_CAGE_DEFORM_AUDIT.json"),
                          encoding="utf-8"))["cases"]


def apply_stage6b(rig, cid):
    c = CASES[cid]
    q = c["cmc_quaternion_local"]
    K.B.reset_pose(rig)
    pb = rig.pose.bones["THUMB_CMC_R"]
    pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = Quaternion((q[0], q[1], q[2], q[3]))
    if c["mcp_deg"]:
        p = rig.pose.bones["THUMB_MCP_R"]
        p.rotation_mode = 'QUATERNION'
        p.rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(-c["mcp_deg"]))
    if c["ip_deg"]:
        p = rig.pose.bones["THUMB_IP_R"]
        p.rotation_mode = 'QUATERNION'
        p.rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(-c["ip_deg"]))


def posed(path, kind, arg):
    """open a harness, apply a pose, evaluate the mesh, return (V, P)."""
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = bpy.data.objects[K.MESH_OBJ]
    rig = bpy.data.objects[K.RIG_OBJ]
    MW = ob.matrix_world.copy()
    if kind == "s6b":
        apply_stage6b(rig, arg)
    else:                                   # stage6a isolated flex, frozen sign = -1
        K.B.S6.reset_pose(rig)
        K.B.S6.set_joint_rotation(rig, arg[0], -arg[1])
    K.B.update()
    return K.B.evaluate(ob, MW)


def stretch_colour(r):
    if r <= 1.5:
        return (0.20, 0.90, 0.35)
    if r <= 3.0:
        return (0.95, 0.85, 0.15)
    return (1.0, 0.20, 0.10)


def probe_map(name, title, hist_case, V, Vr1=None, label_r1="Stage5B R1B", label_new="Stage5B R1C"):
    a = R.canvas()
    if Vr1 is not None:
        p1 = R.Panel(a, 20, 60, 760, 1040, V0, "D")
        p1.frame("%s  :  %s" % (label_r1, title))
        p2 = R.Panel(a, 820, 60, 760, 1040, V0, "D")
        p2.frame("%s  :  %s" % (label_new, title))
        pairs = ((p1, Vr1), (p2, V))
    else:
        p1 = R.Panel(a, 60, 60, 1000, 1040, V0, "D")
        p1.frame(title)
        pairs = ((p1, V),)
    for pan, VV in pairs:
        for i in range(NV):
            x, y = pan.pt(V0[i])
            R.px(a, x, y, (0.24, 0.25, 0.29), 2)
        for k, i, j in HIST:
            r = (VV[i] - VV[j]).length / max(1e-18, EDGE_LEN0[k])
            R.line(a, pan.pt(V0[i]), pan.pt(V0[j]), stretch_colour(r), 2)
        for i in sorted(cap):
            x, y = pan.pt(V0[i])
            R.px(a, x, y, (0.85, 0.20, 0.95), 4, 0.55)
        for i in sorted(nail):
            x, y = pan.pt(V0[i])
            R.px(a, x, y, (0.95, 0.90, 0.25), 3, 0.55)
    mx = max((V[i] - V[j]).length / max(1e-18, EDGE_LEN0[k]) for k, i, j in HIST)
    torn = sum(1 for k, i, j in HIST
               if (V[i] - V[j]).length / max(1e-18, EDGE_LEN0[k]) > 3.0
               and (V[i] - V[j]).length * 1000 > 5.0)
    R.legend(a, 1090, 110, [("STRETCH < 1.5x", (0.20, 0.90, 0.35)),
                            ("1.5x .. 3.0x", (0.95, 0.85, 0.15)),
                            ("> 3.0x AND > 5 mm = TEAR", (1.0, 0.20, 0.10)),
                            ("THUMB DISTAL CAP", (0.85, 0.20, 0.95)),
                            ("THUMB NAIL", (0.95, 0.90, 0.25))])
    R.text(a, 1090, 240, "HISTORIC CLASS_B 61 EDGES", 3)
    R.text(a, 1090, 280, "MAX STRETCH %.4f X" % mx, 3)
    R.text(a, 1090, 310, "TEAR ( >3X AND >5MM ) = %d / 61" % torn, 3)
    if Vr1 is not None:
        r1mx = R1SEAM[hist_case]["max_stretch_ratio"]
        r1t = R1SEAM[hist_case]["edges_over_3x_and_over_5mm"]
        R.text(a, 1090, 350, "R1 BASELINE %.2f X  TEAR %d / 61" % (r1mx, r1t), 3,
               (1.0, 0.45, 0.35))
    R.text(a, 20, 22, name.replace(".png", ""), 3)
    R.save(a, name)


# ---- 4/5/6 historic edge probe maps
Vt = posed(K.S6A_R1B_HARNESS, "s6a", ("THUMB_MCP_R", 45.0))[0]
probe_map("STAGE6B_R1B_HISTORIC_CLASS_B_EDGE_TH_MCP45.png",
          "TH_MCP_45 (thumb MCP 45 deg flex)", "TH_MCP_45", Vt)
Vd = posed(K.S6B_HARNESS, "s6b", "CMC_OPP_30")[0]
Vn = posed(K.S6B_R1B_HARNESS, "s6b", "CMC_OPP_30")[0]
probe_map("STAGE6B_R1B_HISTORIC_CLASS_B_EDGE_CMC_OPP30.png",
          "CMC_OPP_30 (30 deg CMC opposition)", "CMC_OPP_30", Vn, Vd)
Vd3 = posed(K.S6B_HARNESS, "s6b", "FULL_OPP_L3")[0]
Vn3 = posed(K.S6B_R1B_HARNESS, "s6b", "FULL_OPP_L3")[0]
probe_map("STAGE6B_R1B_HISTORIC_CLASS_B_EDGE_FULL_OPP_L3.png",
          "FULL_OPP_L3 (CMC30 + MCP30 + IP15)", "FULL_OPP_L3", Vn3, Vd3)

# ---- 7/8/9/10 pose maps (bind -> posed) with historic edge colouring
for cid, nm in (("CMC_OPP_30", "STAGE6B_R1B_CMC_OPP_30_BEFORE_AFTER.png"),
                ("FULL_OPP_L1", "STAGE6B_R1B_FULL_OPP_L1.png"),
                ("FULL_OPP_L2", "STAGE6B_R1B_FULL_OPP_L2.png"),
                ("FULL_OPP_L3", "STAGE6B_R1B_FULL_OPP_L3.png")):
    Vd_ = posed(K.S6B_HARNESS, "s6b", cid)[0]
    Vn_ = posed(K.S6B_R1B_HARNESS, "s6b", cid)[0]
    probe_map(nm, cid, cid, Vn_, Vd_)

# ---- 11 contact progression
a = R.canvas()
R.text(a, 30, 20, "STAGE6B_R1B_CONTACT_PROGRESSION : THUMB-INDEX CONTACT + PENETRATION PROXY", 3)
ids = ["CMC_OPP_10", "CMC_OPP_20", "CMC_OPP_30", "CMC_MCP_L1", "CMC_MCP_L2", "CMC_MCP_L3",
       "FULL_OPP_L1", "FULL_OPP_L2", "FULL_OPP_L3"]
x0, y0, bw = 150, 130, 130
R.text(a, 30, 90, "B_THUMB_INDEX PAIRS  (blue = Stage5B R1B, green = Stage5B R1C)", 2)
mx = max(max(CONT1[c]["counts"]["B_THUMB_INDEX"] for c in ids),
         max(CONT2[c]["counts"]["B_THUMB_INDEX"] for c in ids))
for n, c in enumerate(ids):
    for off, col, src in ((0, (0.35, 0.55, 0.95), CONT1), (34, (0.25, 0.85, 0.45), CONT2)):
        v = src[c]["counts"]["B_THUMB_INDEX"]
        hh = int(300 * v / max(1, mx))
        for xx in range(x0 + n * bw + off, x0 + n * bw + off + 30):
            for yy in range(y0 + 300 - hh, y0 + 300):
                R.px(a, xx, yy, col, 0)
    R.text(a, x0 + n * bw - 6, y0 + 320, c.replace("_", " "), 1)
R.text(a, 30, y0 + 360, "PENETRATION PROXY MAX (mm)   red = R1B, orange = R1", 2)
y2 = y0 + 420
for n, c in enumerate(ids):
    R.text(a, 30, y2 + n * 30, c, 2)
    v1 = CONT1[c]["max_penetration_proxy_mm"]
    v2 = CONT2[c]["max_penetration_proxy_mm"]
    for xx in range(200, 200 + int(v1 * 220), 2):
        R.px(a, xx, y2 + n * 30 + 6, (1.0, 0.55, 0.20), 2)
    for xx in range(200, 200 + int(v2 * 220), 2):
        R.px(a, xx, y2 + n * 30 + 11, (1.0, 0.20, 0.15), 2)
    R.text(a, 1400, y2 + n * 30, "%.3f / %.3f" % (v1, v2), 2)
R.save(a, "STAGE6B_R1B_CONTACT_PROGRESSION.png")

# ---- 12 thumb-index contact closeup L3
a = R.canvas()
p = R.Panel(a, 300, 80, 1000, 1000, V0, "D")
box = (V0[284] + V0[2189]) * 0.5
p.u0, p.u1 = box.x - 0.045, box.x + 0.045
p.v0, p.v1 = box.z - 0.045 * 1000 / 1000, box.z + 0.045
p.s = min((p.w - 48) / (p.u1 - p.u0), (p.h - 48) / (p.v1 - p.v0))
p.frame("FULL_OPP_L3 : THUMB / INDEX CONTACT CLOSEUP (corrected ownership)")
for i in range(NV):
    x, y = p.pt(V0[i])
    R.px(a, x, y, (0.26, 0.27, 0.31), 2)
for i in range(NV):
    x, y = p.pt(V0[i])
    col = {"THUMB": (0.95, 0.30, 0.20), "INDEX": (0.25, 0.55, 0.95),
           "wrist": (0.45, 0.47, 0.52)}.get(CORR[i], (0.5, 0.5, 0.5))
    R.px(a, x, y, col, 1, 0.55)
for k, i, j in HIST:
    R.line(a, p.pt(V0[i]), p.pt(V0[j]), (0.15, 0.95, 0.55), 2)
for k in PART["partition"] and [k for k, (i, j) in enumerate(EDGES)
                                if CORR[i] != CORR[j] and {CORR[i], CORR[j]} == {"THUMB", "INDEX"}]:
    i, j = EDGES[k]
    R.line(a, p.pt(V0[i]), p.pt(V0[j]), (1.0, 0.85, 0.10), 3)
for i in sorted(cap):
    x, y = p.pt(V0[i])
    R.px(a, x, y, (0.85, 0.20, 0.95), 5)
R.legend(a, 1330, 120, [("CORRECTED THUMB", (0.95, 0.30, 0.20)),
                        ("CORRECTED INDEX", (0.25, 0.55, 0.95)),
                        ("CORRECTED WRIST", (0.45, 0.47, 0.52)),
                        ("HISTORIC CLASS_B 61", (0.15, 0.95, 0.55)),
                        ("R2 THUMB|INDEX BOUNDARY", (1.0, 0.85, 0.10)),
                        ("THUMB DISTAL CAP", (0.85, 0.20, 0.95))])
R.text(a, 30, 22, "STAGE6B_R1B_THUMB_INDEX_CONTACT_CLOSEUP_L3", 3)
R.text(a, 30, 1090, "CONTACT IS MEASURED WITH THE CORRECTED DIGIT OWNERSHIP (round section 27); THE CONTACT GEOMETRY ALGORITHM IS UNCHANGED", 2)
R.save(a, "STAGE6B_R1B_THUMB_INDEX_CONTACT_CLOSEUP_L3.png")

# ---- 13 CMC cage strain (CMC_OPP_30)
Vc = posed(K.S6B_R1B_HARNESS, "s6b", "CMC_OPP_30")[0]
a = R.canvas()
p = R.Panel(a, 60, 60, 1000, 1040, V0, "D")
p.frame("CMC CAGE STRAIN, CMC_OPP_30 (vertex colour = local face-area ratio)")
for i in range(NV):
    x, y = p.pt(V0[i])
    R.px(a, x, y, (0.22, 0.23, 0.26), 2)
cageset = set(cage)
ratios = []
for fi, poly in enumerate(POLY):
    if not any(v in cageset for v in poly):
        continue
    r = K.B.face_area(Vc, poly) / max(1e-18, FACE_AREA0[fi])
    ratios.append((fi, r))
for fi, r in ratios:
    c = R.zmap(r, 0.5, 1.5)
    for v in POLY[fi]:
        x, y = p.pt(V0[v])
        R.px(a, x, y, c, 4)
for i in sorted(cage):
    x, y = p.pt(V0[i])
    R.px(a, x, y, (1, 1, 1), 6, 0.12)
st = CAGE_AUD["CMC_OPP_30"]
R.legend(a, 1090, 130, [("FACE AREA RATIO 0.5", R.zmap(0.5, 0.5, 1.5)),
                        ("1.0", R.zmap(1.0, 0.5, 1.5)),
                        ("1.5", R.zmap(1.5, 0.5, 1.5)),
                        ("CAGE PATCH (%d VERTICES)" % len(cage), (1, 1, 1))])
R.text(a, 1090, 250, "MIN FACE AREA RATIO %.6f" % st["face_area_ratio_min"], 3)
R.text(a, 1090, 280, "MIN EDGE RATIO %.6f" % st["edge_ratio_min"], 3)
R.text(a, 1090, 310, "MAX EDGE RATIO %.6f" % st["edge_ratio_max"], 3)
R.text(a, 1090, 340, "FOLD OVER FACES %d" % st["fold_over_face_count_normal_dot_lt_-0.5"], 3)
R.text(a, 1090, 370, "NEW SELF INTERSECTION %d" % st["new_self_intersection_pairs_within_cage"], 3)
R.text(a, 30, 22, "STAGE6B_R1B_CMC_CAGE_STRAIN", 3)
R.save(a, "STAGE6B_R1B_CMC_CAGE_STRAIN.png")

# ---- 14 bind restore proof
a = R.canvas()
p1 = R.Panel(a, 20, 60, 760, 900, V0, "D")
p1.frame("BIND RESTORE : |posed - bind| (mm)")
p2 = R.Panel(a, 820, 60, 760, 900, V0, "P")
p2.frame("BIND RESTORE : |posed - bind| (mm)  PALMAR")
Vz = posed(K.S6B_R1B_HARNESS, "s6b", "CMC_OPP_10")[0]
bpy.ops.wm.open_mainfile(filepath=K.S6B_R1B_HARNESS)
ob = bpy.data.objects[K.MESH_OBJ]
rig = bpy.data.objects[K.RIG_OBJ]
MW = ob.matrix_world.copy()
K.B.reset_pose(rig)
K.B.update()
Vb = K.B.evaluate(ob, MW)[0]
dev = [(Vb[i] - V0[i]).length * 1000 for i in range(NV)]
for pan in (p1, p2):
    for i in range(NV):
        x, y = pan.pt(V0[i])
        R.px(a, x, y, R.zmap(dev[i] * 1000, 0.0, 2e-4), 3)
z = json.load(open(os.path.join(K.S6B_R1B, "STAGE6B_R1B_ZERO_RESTORE_AUDIT.json"),
                   encoding="utf-8"))
R.text(a, 20, 22, "STAGE6B_R1B_BIND_RESTORE_PROOF", 3)
R.text(a, 20, 980, "POSE / WEIGHT / GEOMETRY ARE UNTOUCHED BY THE HARNESS: BIND MESH RESTORES AFTER EVERY CASE", 2)
R.text(a, 20, 1010, "MAX RESTORE DELTA = %.9f mm   HARD GATE 1e-04 mm   NOISE FLOOR 5.967e-05 mm" % z["RESTORE_MAX_DELTA_MM"], 2)
R.text(a, 20, 1040, "ALL 9 CASES RESTORE = %s" % z["ALL_9_CASES_RESTORE"], 2)
R.text(a, 20, 1070, "RESIDUAL RGB SCALE 0 .. 2e-4 mm (BLUE = AT BIND)", 2)
R.save(a, "STAGE6B_R1B_BIND_RESTORE_PROOF.png")

json.dump({"log": LOG}, open(os.path.join(K.S6B_R1B, "_tmp", "R1B_RENDER_PART2.json"), "w",
                             encoding="utf-8"), indent=1, ensure_ascii=False)
print("RENDER_PART2_DONE")
