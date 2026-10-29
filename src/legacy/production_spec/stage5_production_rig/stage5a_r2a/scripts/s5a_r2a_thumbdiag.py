# STAGE5A_R2A -- thumb distal-phalanx geometry diagnostic (READ-ONLY)
import bpy, sys, os, json, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
S4_ASSET_ORIGIN = Vector(oa["WRIST_ORIGIN"])

ob = bpy.data.objects["Hand  - Realistic"]
me = ob.data
MW = ob.matrix_world
M3 = MW.to_3x3()
V = [(MW @ v.co).copy() for v in me.vertices]
NV = len(V)
FACE_C = [sum((V[v] for v in p.vertices), Vector()) / len(p.vertices) for p in me.polygons]

CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"], "LITTLE": ["MCP", "PIP", "DIP"]}


def d_poly(p, poly):
    best = 1e9
    for i in range(len(poly) - 1):
        a, b = poly[i], poly[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
        best = min(best, (p - (a + ab * t)).length)
    return best


def chainpts(D):
    p = [Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])]
    for s in CHAIN[D]:
        p.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
    return p


ACHAIN = {D: chainpts(D) for D in CHAIN}
ACHAIN["wrist"] = [S4_ASSET_ORIGIN, Vector(jf["WRIST_R"]["tail"])]
FACE_OWNER = {}
for p in me.polygons:
    c = sum((V[v] for v in p.vertices), Vector()) / len(p.vertices)
    FACE_OWNER[p.index] = min({D: d_poly(c, ACHAIN[D]) for D in ACHAIN}, key=lambda k: d_poly(c, ACHAIN[k]))
V2F = [[] for _ in range(NV)]
for p in me.polygons:
    for v in p.vertices:
        V2F[v].append(p.index)
VOWN = {}
for v in me.vertices:
    ds = {FACE_OWNER[fi] for fi in V2F[v.index]}
    VOWN[v.index] = ds.pop() if len(ds) == 1 else "MIXED"

R = {}
for D in ["THUMB", "INDEX", "LITTLE"]:
    dist_seg = "IP" if D == "THUMB" else "DIP"
    P = Vector(jf["%s_%s_R" % (D, dist_seg)]["head"])
    T = Vector(jf["%s_TIP_R" % D]["head"])
    u0 = (T - P).normalized()
    ov = [i for i in range(NV) if VOWN[i] == D]
    d = {}
    d["joint"] = [round(float(x), 9) for x in P]
    d["approved_tip"] = [round(float(x), 9) for x in T]
    d["u0"] = [round(float(x), 9) for x in u0]
    d["bone_len_mm"] = round((T - P).length * 1000, 4)
    # distribution of own verts by axial coordinate along u0
    ss = sorted(((V[i] - P).dot(u0) * 1000, i) for i in ov)
    d["axial_range_mm"] = [round(ss[0][0], 3), round(ss[-1][0], 3)]
    # section centroids along u0 (2 mm slabs, all own verts)
    prof = []
    k = 0
    while k * 2.0 <= ss[-1][0] + 2.0:
        lo, hi = k * 2.0 - 1.0, k * 2.0 + 1.0
        sel = [V[i] for s, i in ss if lo <= s <= hi]
        if len(sel) >= 5:
            c = sum(sel, Vector()) / len(sel)
            perps = [((q - P) - u0 * ((q - P).dot(u0))).length * 1000 for q in sel]
            prof.append({"s_mm": round(k * 2.0, 2), "n": len(sel),
                         "centroid": [round(float(x), 9) for x in c],
                         "centroid_perp_mm": round(((c - P) - u0 * ((c - P).dot(u0))).length * 1000, 3),
                         "r95_mm": round(sorted(perps)[int(0.95 * (len(perps) - 1))], 3),
                         "r_max_mm": round(max(perps), 3)})
        k += 1
    d["sections_along_u0"] = prof
    d["n_own_verts"] = len(ov)
    R[D] = d

json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("[DIAG] written", OUT)
