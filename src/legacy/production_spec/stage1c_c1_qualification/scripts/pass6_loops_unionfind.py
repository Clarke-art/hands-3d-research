# STAGE1C - Pass 6: circumferential loop counting via union-find over the quad opposite-edge graph
import bpy, bmesh, json, math
from mathutils import Vector

TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
bm = bmesh.new()
bm.from_mesh(ob.data)
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()
W = [(mw @ v.co).copy() for v in bm.verts]

# ---- build opposite-edge adjacency (quad rule) ----
nE = len(bm.edges)
parent = list(range(nE))
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[rb] = ra

quad_faces = 0
for f in bm.faces:
    if len(f.edges) != 4:
        continue
    quad_faces += 1
    es = list(f.edges)
    vs = [set(v.index for v in e.verts) for e in es]
    for i in range(4):
        for j in range(4):
            if i == j: continue
            if not (vs[i] & vs[j]):
                union(es[i].index, es[j].index)
                break

comps = {}
for ei in range(nE):
    comps.setdefault(find(ei), []).append(ei)

# ---- finger zones ----
SEG = {
    "THUMB":  ((1.492, 0.036, 0.243), (1.443, 0.012, 0.298), 0.014),
    "INDEX":  ((1.458, 0.023, 0.163), (1.446, 0.011, 0.245), 0.0115),
    "MIDDLE": ((1.422, 0.023, 0.149), (1.424, 0.010, 0.235), 0.0115),
    "RING":   ((1.3925, 0.029, 0.160), (1.399, 0.014, 0.235), 0.0115),
    "LITTLE": ((1.3545, 0.031, 0.187), (1.372, 0.019, 0.262), 0.0110),
}
def seg_geom(p0s, p1s):
    p0, p1 = Vector(p0s), Vector(p1s)
    ax = (p1 - p0); L = ax.length
    return p0, ax / L, L

def axial(p, p0, ax, L, rad, slack=0.004):
    d = p - p0
    t = d.dot(ax)
    if t < -0.006 or t > L + 0.006:
        return None
    if (d - ax * t).length <= rad + slack:
        return t
    return None

report = {}
for name, (p0s, p1s, rad) in SEG.items():
    p0, ax, L = seg_geom(p0s, p1s)
    rings = []   # circumferential
    cols = []    # longitudinal
    for root, eids in comps.items():
        ts = []; aligns = []
        for ei in eids:
            e = bm.edges[ei]
            mid = (W[e.verts[0].index] + W[e.verts[1].index]) * 0.5
            t = axial(mid, p0, ax, L, rad)
            if t is None: continue
            ts.append(t)
            d = W[e.verts[1].index] - W[e.verts[0].index]
            if d.length > 1e-9:
                aligns.append(abs(d.normalized().dot(ax)))
        if len(ts) < 4 or len(ts) < 0.6 * len(eids):
            continue
        a = sum(aligns) / len(aligns)
        rec = {"t": round(sum(ts)/len(ts), 4), "n": len(ts),
               "t_spread": round(max(ts)-min(ts), 4), "align": round(a, 3),
               "strand_len": len(eids)}
        (rings if a < 0.45 else cols).append(rec)
    rings.sort(key=lambda d: d["t"])
    gaps = [round(rings[i+1]["t"] - rings[i]["t"], 5) for i in range(len(rings)-1)]
    if name == "THUMB":
        joints = {"IP": 0.42*L, "MCP_T": 0.72*L, "CMC": L - 0.10*L}
    else:
        joints = {"DIP": 0.26*L, "PIP": 0.58*L, "MCP": L - 0.06*L}
    jr = {}
    for jn, jt in joints.items():
        w = min(0.011, 0.12*L)
        near = [r for r in rings if abs(r["t"] - jt) <= w]
        jr[jn] = {"axial_m": round(jt, 4), "window_m": round(w, 4),
                  "circular_loops_in_window": len(near),
                  "world": [round(v, 4) for v in (p0 + ax*jt)],
                  "loop_positions_m": [r["t"] for r in near]}
    report[name] = {
        "finger_len_m": round(L, 4),
        "circular_loop_count": len(rings),
        "longitudinal_column_count": len(cols),
        "ring_positions_m": [r["t"] for r in rings],
        "ring_t_spread_m": [r["t_spread"] for r in rings],
        "ring_n_edges": [r["n"] for r in rings],
        "gaps_m": gaps,
        "median_gap_m": round(sorted(gaps)[len(gaps)//2], 5) if gaps else None,
        "joints": jr,
    }

# pole census inside finger zones
poles = {}
for v in bm.verts:
    for name, (p0s, p1s, rad) in SEG.items():
        p0, ax, L = seg_geom(p0s, p1s)
        if axial(W[v.index], p0, ax, L, rad) is None:
            continue
        val = len(v.link_edges)
        if val != 4:
            poles.setdefault(name, {})
            poles[name][str(val)] = poles[name].get(str(val), 0) + 1
        break

out = {"quad_opposite_edge_components": len(comps), "quad_faces": quad_faces,
       "fingers": report, "poles_in_finger_zones": poles}
with open(r"<HANDS_ROOT>\production_spec\stage1c_c1_qualification\stats\topology_rings.json", "w") as f:
    json.dump(out, f, indent=1)
# compact print
for n, d in report.items():
    print(f"{n}: len={d['finger_len_m']} rings={d['circular_loop_count']} cols={d['longitudinal_column_count']} medgap={d['median_gap_m']}")
    print("   ring_pos:", d["ring_positions_m"])
    for jn, jv in d["joints"].items():
        print(f"   {jn}: axial={jv['axial_m']} win={jv['window_m']} loops_in_window={jv['circular_loops_in_window']} world={jv['world']}")
print("poles:", json.dumps(poles))
print("PASS6_DONE")
