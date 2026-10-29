# STAGE5A_R2 diagnostic: section construction + thumb apex distribution. READ-ONLY.
import bpy, sys, os, json, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
MASTER, OUT = argv[0], argv[1]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
MM = 1000.0
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
nail = json.load(open(os.path.join(S4, "stage4c_r2", "NAIL_AUDIT_R2.json"), encoding="utf-8"))
bpy.ops.wm.open_mainfile(filepath=MASTER)
ob = bpy.data.objects["Hand  - Realistic"]
me = ob.data
MW = ob.matrix_world
MINV = MW.inverted()
M3 = MW.to_3x3()
V = [(MW @ v.co).copy() for v in me.vertices]
NV = len(V)
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"], "LITTLE": ["MCP", "PIP", "DIP"]}


def closest(p):
    ok, loc, nor, idx = ob.closest_point_on_mesh(MINV @ Vector(p))
    return (MW @ loc, (M3 @ nor).normalized(), idx) if ok else (None, None, None)


def clearance(p):
    loc, nor, idx = closest(p)
    return None if loc is None else (Vector(p) - loc).length


def chainpts(D):
    p = [Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])]
    for s in CHAIN[D]:
        p.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
    return p


def d_poly(p, poly):
    best = 1e9
    for i in range(len(poly) - 1):
        a, b = poly[i], poly[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
        best = min(best, (p - (a + ab * t)).length)
    return best


ACHAIN = {D: chainpts(D) for D in CHAIN}
WRIST = [Vector(jf["WRIST_R"]["head"]), Vector(jf["WRIST_R"]["tail"])]


def owner(p):
    dd = {D: d_poly(p, ACHAIN[D]) for D in ACHAIN}
    dd["wrist"] = d_poly(p, WRIST)
    return min(dd, key=dd.get)


rep = {}

# ---- index MCP section: chain-filtered, generous cap -------------------------------
R1_IM = Vector(jf["INDEX_MCP_R"]["head"])
ax = (Vector(jf["INDEX_PIP_R"]["head"]) - R1_IM).normalized()
dor = Vector((0.283415, 0.025267, 0.958664))
u = (dor - ax * dor.dot(ax)).normalized()
w = ax.cross(u).normalized()
pts = []
for i, p in enumerate(V):
    d = p - R1_IM
    if abs(d.dot(ax)) <= 0.005 and d_poly(p, ACHAIN["INDEX"]) <= 0.012:
        pts.append((d.dot(u), d.dot(w), i))
if pts:
    xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
    rep["INDEX_MCP_section"] = {
        "n": len(pts),
        "u_range_mm": [round(min(xs) * MM, 2), round(max(xs) * MM, 2)],
        "w_range_mm": [round(min(ys) * MM, 2), round(max(ys) * MM, 2)],
        "inplane_centroid_mm": [round(sum(xs) / len(xs) * MM, 2), round(sum(ys) / len(ys) * MM, 2)],
        "r1_point_inplane": [0.0, 0.0],
        "clearance_at_R1_mm": round((clearance(R1_IM) or 0) * MM, 3),
        "clearance_at_inplane_centroid_mm": round(
            (clearance(R1_IM + u * (sum(xs) / len(xs)) + w * (sum(ys) / len(ys))) or 0) * MM, 3),
        "axis_used": [round(float(x), 6) for x in ax],
    }
# scan clearance along u and w through the section centroid
cu = sum(xs) / len(xs); cw = sum(ys) / len(ys)
scan = []
for t in range(-14, 15):
    p = R1_IM + u * (t * 1e-3) + w * cw
    scan.append({"t_mm": t, "dir": "u", "clearance_mm": round((clearance(p) or 0) * MM, 3)})
for t in range(-14, 15):
    p = R1_IM + u * cu + w * (t * 1e-3)
    scan.append({"t_mm": t, "dir": "w", "clearance_mm": round((clearance(p) or 0) * MM, 3)})
rep["INDEX_MCP_clearance_scan"] = scan

# ---- thumb MCP / CMC sections ------------------------------------------------------
for label, p0, axsrc in (("THUMB_MCP", Vector(jf["THUMB_MCP_R"]["head"]),
                          (Vector(jf["THUMB_MCP_R"]["head"]) - Vector(jf["THUMB_CMC_R"]["head"])).normalized()),
                         ("THUMB_CMC", Vector(jf["THUMB_CMC_R"]["head"]),
                          (Vector(jf["THUMB_MCP_R"]["head"]) - Vector(jf["THUMB_CMC_R"]["head"])).normalized())):
    dorT = Vector((0.631289, 0.775319, -0.018839))
    uu = (dorT - axsrc * dorT.dot(axsrc)).normalized()
    ww = axsrc.cross(uu).normalized()
    sel = []
    for i, p in enumerate(V):
        d = p - p0
        if abs(d.dot(axsrc)) <= 0.005 and d_poly(p, ACHAIN["THUMB"]) <= 0.018:
            sel.append((d.dot(uu), d.dot(ww), i))
    if sel:
        xs = [q[0] for q in sel]; ys = [q[1] for q in sel]
        rep[label + "_section"] = {
            "n": len(sel),
            "u_range_mm": [round(min(xs) * MM, 2), round(max(xs) * MM, 2)],
            "w_range_mm": [round(min(ys) * MM, 2), round(max(ys) * MM, 2)],
            "inplane_centroid_mm": [round(sum(xs) / len(xs) * MM, 2), round(sum(ys) / len(ys) * MM, 2)],
            "clearance_at_R1_mm": round((clearance(p0) or 0) * MM, 3),
            "clearance_at_inplane_centroid_mm": round(
                (clearance(p0 + uu * (sum(xs) / len(xs)) + ww * (sum(ys) / len(ys))) or 0) * MM, 3),
        }
        cu = sum(xs) / len(xs); cw = sum(ys) / len(ys)
        sc = []
        for t in range(-16, 17):
            sc.append({"t_mm": t, "dir": "u",
                       "clearance_mm": round((clearance(p0 + uu * (t * 1e-3) + ww * cw) or 0) * MM, 3)})
        for t in range(-16, 17):
            sc.append({"t_mm": t, "dir": "w",
                       "clearance_mm": round((clearance(p0 + uu * cu + ww * (t * 1e-3)) or 0) * MM, 3)})
        rep[label + "_clearance_scan"] = sc

# ---- thumb distal axial distribution ----------------------------------------------
R1_IP = Vector(jf["THUMB_IP_R"]["head"])
R1_TIP = Vector(jf["THUMB_TIP_R"]["head"])
a = (R1_TIP - R1_IP).normalized()
# strict thumb ownership
FACE_OWNER = {}
for p in me.polygons:
    c = sum((V[v] for v in p.vertices), Vector()) / len(p.vertices)
    FACE_OWNER[p.index] = owner(c)
V2F = [[] for _ in range(NV)]
for p in me.polygons:
    for v in p.vertices:
        V2F[v].append(p.index)
thumb_v = []
for v in me.vertices:
    ds = {FACE_OWNER[fi] for fi in V2F[v.index]}
    if len(ds) == 1 and ds.pop() == "THUMB":
        thumb_v.append(v.index)
sv = sorted((( (V[i] - R1_IP).dot(a), i) for i in thumb_v), reverse=True)
rep["thumb_distal"] = {
    "n_strict_thumb_verts": len(thumb_v),
    "IP_head": [round(float(x), 6) for x in R1_IP],
    "axis": [round(float(x), 6) for x in a],
    "top30_axial_mm": [round(s * MM, 3) for s, i in sv[:30]],
    "top30_vertex": [i for s, i in sv[:30]],
    "top30_world": [[round(float(x), 6) for x in V[i]] for s, i in sv[:30]],
    "top30_dist_from_axis_mm": [round((V[i] - R1_IP - a * s).length * MM, 3) for s, i in sv[:30]],
    "band_counts": {str(b): sum(1 for s, i in sv if s * MM >= sv[0][0] * MM - b) for b in (1, 2, 3, 4, 5, 6, 8, 10)},
    "clearance_at_R1_TIP_mm": round((clearance(R1_TIP) or 0) * MM, 3),
}
# cap-band centroid variants
for b in (3.0, 4.0, 5.0, 6.0):
    band = [V[i] for s, i in sv if s * MM >= sv[0][0] * MM - b]
    c = sum(band, Vector()) / len(band)
    pc = R1_IP + a * (c - R1_IP).dot(a)
    dist_apex = (V[sv[0][1]] - pc).length * MM
    rep.setdefault("thumb_cap_variants", []).append(
        {"band_mm": b, "n": len(band),
         "cap_centroid_world": [round(float(x), 6) for x in c],
         "projected_axis_point": [round(float(x), 6) for x in pc],
         "dist_to_apex_vertex_mm": round(dist_apex, 3),
         "clearance_mm": round((clearance(pc) or 0) * MM, 3)})

json.dump(rep, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("OUT=" + OUT)
