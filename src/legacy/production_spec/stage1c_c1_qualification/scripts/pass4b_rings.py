# STAGE1C - Pass 4b: per-finger ring counting with hand-specified axis segments
import bpy, bmesh, json, math
from mathutils import Vector

TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
bm = bmesh.new()
bm.from_mesh(ob.data)
bm.verts.ensure_lookup_table()
W = [(mw @ v.co).copy() for v in bm.verts]

# hand-specified finger axis segments (tip -> base), from pass4a slice data
SEG = {
    "THUMB":  ((1.492, 0.036, 0.243), (1.443, 0.012, 0.298), 0.014),
    "INDEX":  ((1.458, 0.023, 0.163), (1.446, 0.011, 0.245), 0.0115),
    "MIDDLE": ((1.422, 0.023, 0.149), (1.424, 0.010, 0.235), 0.0115),
    "RING":   ((1.3925, 0.029, 0.160), (1.399, 0.014, 0.235), 0.0115),
    "LITTLE": ((1.3545, 0.031, 0.187), (1.372, 0.019, 0.262), 0.0110),
}

def seg_frame(p0, p1):
    p0, p1 = Vector(p0), Vector(p1)
    ax = (p1 - p0)
    L = ax.length
    ax.normalize()
    return p0, p1, ax, L

out = {}
assign_summary = {}
for name, (p0s, p1s, rad) in SEG.items():
    p0, p1, ax, L = seg_frame(p0s, p1s)
    # assign vertices: perpendicular distance to segment < rad, axial within [-0.3*rad, L+0.3*rad]
    ids = []
    for i, p in enumerate(W):
        d = p - p0
        t = d.dot(ax)
        if t < -0.004 or t > L + 0.004:
            continue
        perp = (d - ax * t).length
        if perp <= rad:
            ids.append((t, i))
    ts = sorted(t for t, i in ids)
    gaps = [ts[k+1]-ts[k] for k in range(len(ts)-1) if ts[k+1]-ts[k] > 2e-5]
    gaps.sort()
    med = gaps[len(gaps)//2] if gaps else 0.0015
    tol = max(0.0009, med*0.5)
    levels = []
    cur = [ts[0]]
    for v in ts[1:]:
        if v - cur[-1] <= tol:
            cur.append(v)
        else:
            levels.append(sum(cur)/len(cur)); cur=[v]
    levels.append(sum(cur)/len(cur))
    # phalanx joints (adult ratio estimates)
    if name == "THUMB":
        joints = {"IP": 0.42*L, "MCP_T": 0.72*L, "CMC": L - 0.10*L}
    else:
        joints = {"DIP": 0.26*L, "PIP": 0.58*L, "MCP": L - 0.06*L}
    jr = {"finger_len_m": round(L, 4), "rings_total": len(levels), "median_ring_gap_m": round(med, 5),
          "verts_assigned": len(ids)}
    for jn, jt in joints.items():
        w = max(0.10*L, 0.008)
        cnt = sum(1 for lv in levels if abs(lv - jt) <= w)
        # world pos of joint center
        wp = p0 + ax * jt
        jr[jn] = {"axial_m": round(jt, 4), "rings_within_window": cnt,
                  "window_m": round(w, 4),
                  "world": [round(v, 4) for v in wp]}
    # rings per segment between joints
    bounds = [0.0] + [joints[k] for k in sorted(joints, key=lambda k: joints[k])] + [L]
    bounds = sorted(set(bounds))
    segs = []
    for a, b in zip(bounds, bounds[1:]):
        segs.append([round(a,4), round(b,4), sum(1 for lv in levels if a < lv <= b)])
    jr["rings_per_segment"] = segs
    out[name] = jr
    assign_summary[name] = len(ids)

with open(r"<HANDS_ROOT>\production_spec\stage1c_c1_qualification\stats\ring_analysis.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
print("PASS4B_DONE")
