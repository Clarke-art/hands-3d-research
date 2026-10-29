# STAGE1C - Pass 11: determine palmar vs dorsal side and hand chirality (G-12)
import bpy, bmesh, json
from mathutils import Vector
TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
bm = bmesh.new(); bm.from_mesh(ob.data)
bm.verts.ensure_lookup_table()
W = [(mw @ v.co).copy() for v in bm.verts]

# --- palm region: z in [0.25, 0.30], x within hand core ---
palm = [p for p in W if 0.250 <= p.z <= 0.300 and 1.36 <= p.x <= 1.46]
print("palm region verts:", len(palm))
xs = sorted(set(round(p.x, 4) for p in palm))
print("x range:", min(p.x for p in palm), max(p.x for p in palm))

# for each x bin, split verts into the two sides by y and get hi/lo mean y
import collections
bins = collections.defaultdict(list)
for p in palm:
    bins[round(p.x / 0.005)].append(p)
rows = []
for k in sorted(bins):
    ps = bins[k]
    ys = sorted(p.y for p in ps)
    if len(ys) < 4:
        continue
    hi = sum(ys[len(ys)//2:]) / len(ys[len(ys)//2:])
    lo = sum(ys[:len(ys)//2]) / len(ys[:len(ys)//2])
    rows.append((round(k*0.005, 3), len(ps), round(lo, 4), round(hi, 4)))
print("x_bin  n   y_low   y_high")
for r in rows:
    print(f"{r[0]:<6} {r[1]:<4} {r[2]:<8} {r[3]}")

# curvature of each sheet across x (second difference)
def curv(vals):
    if len(vals) < 3:
        return None
    d2 = [vals[i+1] - 2*vals[i] + vals[i-1] for i in range(1, len(vals)-1)]
    return round(sum(d2)/len(d2), 6)
lo_vals = [r[2] for r in rows]
hi_vals = [r[3] for r in rows]
print("curvature(low side, x):", curv(lo_vals))
print("curvature(high side, x):", curv(hi_vals))

# --- thumb pad direction: compare thumb tip region "flatness" both sides ---
th = [p for p in W if 1.465 <= p.x <= 1.50 and 0.24 <= p.z <= 0.268]
if th:
    ys = sorted(p.y for p in th)
    print("thumb tip y range:", round(ys[0],4), round(ys[-1],4), "mean", round(sum(ys)/len(ys),4))

# --- finger curl direction: MCP->tip lateral offset in y for MIDDLE finger ---
mid = [p for p in W if 1.405 <= p.x <= 1.44 and 0.149 <= p.z <= 0.235]
if mid:
    bot = [p for p in mid if p.z <= 0.16]
    top = [p for p in mid if p.z >= 0.225]
    if bot and top:
        print("middle finger y: tip_mean", round(sum(p.y for p in bot)/len(bot),4),
              " mcp_mean", round(sum(p.y for p in top)/len(top),4))

print("PASS11_DONE")
