# STAGE5A_R2 mini diagnostic: index MCP section geometry + clearance map. READ-ONLY.
import bpy, sys, os, json, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
MASTER, OUT = argv[0], argv[1]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
MM = 1000.0
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
bpy.ops.wm.open_mainfile(filepath=MASTER)
ob = bpy.data.objects["Hand  - Realistic"]
me = ob.data
MW = ob.matrix_world
MINV = MW.inverted()
M3 = MW.to_3x3()
V = [(MW @ v.co).copy() for v in me.vertices]
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"]}


def closest(p):
    ok, loc, nor, idx = ob.closest_point_on_mesh(MINV @ Vector(p))
    return (MW @ loc, (M3 @ nor).normalized()) if ok else (None, None)


def clearance(p):
    loc, nor = closest(p)
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


CH = chainpts("INDEX")
R1 = Vector(jf["INDEX_MCP_R"]["head"])
n = (Vector(jf["INDEX_PIP_R"]["head"]) - R1).normalized()
dor = Vector((0.283415, 0.025267, 0.958664))
u = (dor - n * dor.dot(n)).normalized()
w = n.cross(u).normalized()
rep = {"axis": [round(float(x), 6) for x in n], "u": [round(float(x), 6) for x in u],
       "w": [round(float(x), 6) for x in w],
       "axis_vs_pip_tip_dir_deg": round(math.degrees(math.acos(max(-1, min(1,
           n.dot((Vector(jf["INDEX_TIP_R"]["head"]) - Vector(jf["INDEX_PIP_R"]["head"])).normalized()))))), 3)}
for rc in (8.0, 10.0, 12.0, 15.0):
    sel = []
    for p in V:
        d = p - R1
        if abs(d.dot(n)) <= 0.0045 and d_poly(p, CH) <= rc * 1e-3:
            sel.append((d.dot(u) * MM, d.dot(w) * MM))
    rep["chainfilter_%.1f" % rc] = {
        "n": len(sel),
        "u_range": [round(min(x for x, y in sel), 2), round(max(x for x, y in sel), 2)] if sel else None,
        "w_range": [round(min(y for x, y in sel), 2), round(max(y for x, y in sel), 2)] if sel else None,
    }
# 3D clearance map in the (u,w) plane, 2 mm grid
grid = {}
best = (0, 0, 0.0)
for i in range(-14, 15, 2):
    for j in range(-14, 15, 2):
        c = clearance(R1 + u * (i * 1e-3) + w * (j * 1e-3))
        if c is None:
            continue
        grid["%d,%d" % (i, j)] = round(c * MM, 2)
        if c * MM > best[2]:
            best = (i, j, c * MM)
rep["clearance_map_2mm"] = grid
rep["grid_best"] = {"u_mm": best[0], "w_mm": best[1], "clearance_mm": round(best[2], 3)}
# fine scan around the grid best
fine = []
bu, bw = best[0], best[1]
for di in range(-20, 21, 2):
    for dj in range(-20, 21, 2):
        p = R1 + u * ((bu + di / 10.0) * 1e-3) + w * ((bw + dj / 10.0) * 1e-3)
        c = clearance(p)
        if c is not None:
            fine.append((c * MM, bu + di / 10.0, bw + dj / 10.0))
fine.sort(reverse=True)
rep["fine_top5"] = [{"clearance_mm": round(a, 3), "u_mm": b, "w_mm": c} for a, b, c in fine[:5]]
json.dump(rep, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("best", rep["grid_best"])
print("fine top5", rep["fine_top5"])
for k in rep:
    if k.startswith("chainfilter"):
        print(k, rep[k])
