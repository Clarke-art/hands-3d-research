# STAGE1C - Pass 9: true edge-loop traversal per finger -> circumferential ring positions (T-01)
import bpy, bmesh, json, math
from mathutils import Vector
TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
bm = bmesh.new(); bm.from_mesh(ob.data)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
W = [(mw @ v.co).copy() for v in bm.verts]

incident = {v.index: [] for v in bm.verts}
for e in bm.edges:
    a, b = e.verts[0].index, e.verts[1].index
    incident[a].append(e.index); incident[b].append(e.index)
edge_v = {e.index: (e.verts[0].index, e.verts[1].index) for e in bm.edges}

def walk(start_edge, start_vert):
    """walk the edge loop starting from start_edge beginning at start_vert"""
    loop = [start_edge]
    cur_edge = start_edge
    cur_vert = start_vert
    prev_dir = None
    while True:
        a, b = edge_v[cur_edge]
        nxt_vert = b if cur_vert == a else a
        dirv = (W[nxt_vert] - W[cur_vert])
        if dirv.length < 1e-9:
            break
        dirv = dirv.normalized()
        cands = [ei for ei in incident[nxt_vert] if ei != cur_edge]
        if len(incident[nxt_vert]) != 4:
            break
        best, bs = None, -2
        for ei in cands:
            x, y = edge_v[ei]
            other = y if x == nxt_vert else x
            d = (W[other] - W[nxt_vert])
            if d.length < 1e-9:
                continue
            s = d.normalized().dot(dirv)
            if s > bs:
                bs, best = s, ei
        if best is None or bs < 0.2:
            break
        if best == start_edge:
            break
        if best in loop:
            break
        loop.append(best)
        cur_vert, cur_edge = nxt_vert, best
        if len(loop) > 400:
            break
    return loop

SEG = {
    "THUMB":  ((1.492, 0.036, 0.243), (1.443, 0.012, 0.298), 0.014),
    "INDEX":  ((1.458, 0.023, 0.163), (1.446, 0.011, 0.245), 0.0115),
    "MIDDLE": ((1.422, 0.023, 0.149), (1.424, 0.010, 0.235), 0.0115),
    "RING":   ((1.3925, 0.029, 0.160), (1.399, 0.014, 0.235), 0.0115),
    "LITTLE": ((1.3545, 0.031, 0.187), (1.372, 0.019, 0.262), 0.0110),
}
def seg_geom(p0s, p1s):
    p0, p1 = Vector(p0s), Vector(p1s)
    ax = p1 - p0; L = ax.length
    return p0, ax / L, L

covered = set()
all_loops = []
for e in bm.edges:
    if e.index in covered:
        continue
    a, b = edge_v[e.index]
    lg = walk(e.index, a)
    lg2 = walk(e.index, b)
    full = list(reversed(lg2[1:])) + lg if len(lg2) > 1 else lg
    if len(full) < 3:
        continue
    for ei in full:
        covered.add(ei)
    all_loops.append(full)

results = {}
loop_store = {}
for name, (p0s, p1s, rad) in SEG.items():
    p0, ax, L = seg_geom(p0s, p1s)
    rings = []
    for lg in all_loops:
        ts = []; aligns = []
        inside = 0
        for ei in lg:
            i0, i1 = edge_v[ei]
            mid = (W[i0] + W[i1]) * 0.5
            d = mid - p0
            t = d.dot(ax)
            perp = (d - ax * t).length
            if -0.006 <= t <= L + 0.006 and perp <= rad + 0.006:
                ts.append(t)
                dd = W[i1] - W[i0]
                if dd.length > 1e-9:
                    aligns.append(abs(dd.normalized().dot(ax)))
            else:
                pass
        if len(ts) < 4 or len(ts) < 0.55 * len(lg):
            continue
        a = sum(aligns) / len(aligns)
        if a < 0.45:
            rings.append({"t": round(sum(ts)/len(ts), 5), "n": len(ts),
                          "tspan": round(max(ts)-min(ts), 5), "align": round(a, 3)})
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
                  "circ_loops_in_window": len(near),
                  "world": [round(v, 4) for v in (p0 + ax*jt)],
                  "loop_t": [r["t"] for r in near]}
    results[name] = {"finger_len_m": round(L, 4),
                     "circ_loops_total": len(rings),
                     "median_gap_m": round(sorted(gaps)[len(gaps)//2], 5) if gaps else None,
                     "gaps_m": gaps,
                     "ring_positions_m": [r["t"] for r in rings],
                     "ring_tspan_m": [r["tspan"] for r in rings],
                     "ring_n_edges": [r["n"] for r in rings],
                     "joints": jr}

out = {"total_edge_loops_found": len(all_loops), "fingers": results}
with open(r"<HANDS_ROOT>/production_spec/runtime_parity/blender_5_1_2/evidence\topology_rings_5_1_2.json", "w") as f:
    json.dump(out, f, indent=1)
for n, d in results.items():
    print(f"{n}: L={d['finger_len_m']} circ_loops={d['circ_loops_total']} medgap={d['median_gap_m']}")
    print("   pos:", d["ring_positions_m"])
    print("   n_edges:", d["ring_n_edges"])
    for jn, jv in d["joints"].items():
        print(f"   {jn}: axial={jv['axial_m']} win={jv['window_m']} loops={jv['circ_loops_in_window']} world={jv['world']}")
print("PASS9_DONE")
