# STAGE5A_R2A -- thumb distal geometry dump (READ-ONLY)
import bpy, sys, os, json, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
AO = Vector(oa["WRIST_ORIGIN"])
ob = bpy.data.objects["Hand  - Realistic"]; me = ob.data
MW = ob.matrix_world
V = [(MW @ v.co).copy() for v in me.vertices]; NV = len(V)
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"], "LITTLE": ["MCP", "PIP", "DIP"]}


def d_poly(p, poly):
    b = 1e9
    for i in range(len(poly) - 1):
        a, q = poly[i], poly[i + 1]; ab = q - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
        b = min(b, (p - (a + ab * t)).length)
    return b


def chp(D):
    p = [Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])]
    for s in CHAIN[D]:
        p.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
    return p


AC = {D: chp(D) for D in CHAIN}; AC["wrist"] = [AO, Vector(jf["WRIST_R"]["tail"])]
FO = {}
for p in me.polygons:
    c = sum((V[v] for v in p.vertices), Vector()) / len(p.vertices)
    FO[p.index] = min(AC, key=lambda D: d_poly(c, AC[D]))
V2F = [[] for _ in range(NV)]
for p in me.polygons:
    for v in p.vertices:
        V2F[v].append(p.index)
VO = {}
for v in me.vertices:
    ds = {FO[fi] for fi in V2F[v.index]}
    VO[v.index] = ds.pop() if len(ds) == 1 else "MIXED"

D = "THUMB"
P = Vector(jf["THUMB_IP_R"]["head"]); T = Vector(jf["THUMB_TIP_R"]["head"])
u0 = (T - P).normalized()
R2 = Vector((1.456466794, 0.018134484, 0.48759535))
own_v = [i for i in range(NV) if VO[i] == D]
sel = sorted(((V[i] - P).dot(u0) * 1000, i) for i in own_v if (V[i] - P).dot(u0) * 1000 > 14)
res = {"u0": [round(float(x), 9) for x in u0],
       "IP": [round(float(x), 9) for x in P], "TIP_approved": [round(float(x), 9) for x in T],
       "R2": [round(float(x), 9) for x in R2],
       "R2_axial_mm": round((R2 - P).dot(u0) * 1000, 4),
       "verts": [], "faces": []}
for s, i in sel:
    res["verts"].append({"i": i, "s_mm": round(s, 3),
                         "p": [round(float(x), 9) for x in V[i]],
                         "dist_to_R2_mm": round((V[i] - R2).length * 1000, 3),
                         "faces": V2F[i]})
own_f = set(fi for fi in FO if FO[fi] == D)
for fi in own_f:
    c = sum((V[v] for v in me.polygons[fi].vertices), Vector()) / len(me.polygons[fi].vertices)
    s = (c - P).dot(u0) * 1000
    if s > 14:
        res["faces"].append({"fi": fi, "s_mm": round(s, 3), "n": len(me.polygons[fi].vertices),
                             "verts": list(me.polygons[fi].vertices),
                             "mat": me.polygons[fi].material_index})
res["faces"].sort(key=lambda f: -f["s_mm"])
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("[THUMBDUMP]", len(res["verts"]), "verts", len(res["faces"]), "faces")
