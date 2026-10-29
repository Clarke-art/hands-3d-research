# STAGE1C - Pass 5: topology-based circumferential edge-loop enumeration per finger (T-01/T-02)
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

SEG = {
    "THUMB":  ((1.492, 0.036, 0.243), (1.443, 0.012, 0.298), 0.014),
    "INDEX":  ((1.458, 0.023, 0.163), (1.446, 0.011, 0.245), 0.0115),
    "MIDDLE": ((1.422, 0.023, 0.149), (1.424, 0.010, 0.235), 0.0115),
    "RING":   ((1.3925, 0.029, 0.160), (1.399, 0.014, 0.235), 0.0115),
    "LITTLE": ((1.3545, 0.031, 0.187), (1.372, 0.019, 0.262), 0.0110),
}

# ---------- ring-group traversal (quad opposite-edge) ----------
opp_cache = {}
def opposite_edge(edge, face):
    if len(face.edges) != 4:
        return None
    vs = set(v.index for v in edge.verts)
    for e in face.edges:
        if e.index == edge.index:
            continue
        if not (set(v.index for v in e.verts) & vs):
            return e
    return None

visited = set()
groups = []
for e in bm.edges:
    if e.index in visited:
        continue
    grp = []
    cur = e
    prev_face = None
    closed = True
    while True:
        if cur is None or cur.index in [g.index for g in grp]:
            break
        grp.append(cur)
        visited.add(cur.index)
        faces = [f for f in cur.link_faces]
        if prev_face is None:
            nxt_face = faces[0] if len(faces) > 0 else None
        else:
            other = [f for f in faces if f.index != prev_face.index]
            nxt_face = other[0] if other else None
        if nxt_face is None:
            closed = False
            break
        nxt = opposite_edge(cur, nxt_face)
        if nxt is None:
            closed = False
            break
        if nxt.index == e.index:
            closed = True
            break
        prev_face = nxt_face
        cur = nxt
    groups.append({"edges": [g.index for g in grp], "closed": closed, "len": len(grp)})

# ---------- per finger ----------
def seg_geom(p0s, p1s):
    p0, p1 = Vector(p0s), Vector(p1s)
    ax = (p1 - p0); L = ax.length; ax = ax / L
    return p0, ax, L

def in_finger(p, p0, ax, L, rad, slack=0.003):
    d = p - p0
    t = d.dot(ax)
    if t < -0.006 or t > L + 0.006:
        return None
    perp = (d - ax * t).length
    if perp <= rad + slack:
        return t
    return None

report = {}
for name, (p0s, p1s, rad) in SEG.items():
    p0, ax, L = seg_geom(p0s, p1s)
    circ = []
    longi = []
    for g in groups:
        ts = []
        dirs = []
        for ei in g["edges"]:
            e = bm.edges[ei]
            mid = (W[e.verts[0].index] + W[e.verts[1].index]) / 2
            t = in_finger(mid, p0, ax, L, rad)
            if t is None:
                continue
            ts.append(t)
            d = (W[e.verts[1].index] - W[e.verts[0].index])
            if d.length > 0:
                dirs.append(abs(d.normalized().dot(ax)))
        if len(ts) < 3 or len(ts) < 0.6 * g["len"]:
            continue
        mean_axis_align = sum(dirs) / len(dirs)
        entry = {"t_mean": sum(ts)/len(ts), "n_edges": len(ts), "closed": g["closed"],
                 "align": round(mean_axis_align, 3), "t_min": min(ts), "t_max": max(ts)}
        if mean_axis_align < 0.45:
            circ.append(entry)     # circumferential ring (perpendicular to axis)
        else:
            longi.append(entry)    # longitudinal edge column
    circ.sort(key=lambda d: d["t_mean"])
    # gap stats
    gaps = [round(circ[i+1]["t_mean"] - circ[i]["t_mean"], 5) for i in range(len(circ)-1)]
    if name == "THUMB":
        joints = {"IP": 0.42*L, "MCP_T": 0.72*L, "CMC": L - 0.10*L}
    else:
        joints = {"DIP": 0.26*L, "PIP": 0.58*L, "MCP": L - 0.06*L}
    jr = {}
    for jn, jt in joints.items():
        w = min(0.011, 0.12*L)
        near = [c for c in circ if abs(c["t_mean"] - jt) <= w]
        jr[jn] = {"axial_m": round(jt, 4), "window_m": round(w, 4),
                  "circumferential_loops_in_window": len(near),
                  "world": [round(v, 4) for v in (p0 + ax*jt)],
                  "loop_positions_m": [round(c["t_mean"], 4) for c in near]}
    bounds = sorted(set([0.0] + [joints[k] for k in joints] + [L]))
    seg_cnt = []
    for a, b in zip(bounds, bounds[1:]):
        seg_cnt.append({"from": round(a, 4), "to": round(b, 4),
                        "loops": sum(1 for c in circ if a < c["t_mean"] <= b)})
    report[name] = {
        "finger_len_m": round(L, 4),
        "circumferential_loops_total": len(circ),
        "longitudinal_columns_total": len(longi),
        "mean_loop_spacing_m": round(sum(gaps)/len(gaps), 5) if gaps else None,
        "loop_spacing_list_m": gaps,
        "joints": jr,
        "loops_per_phalanx_segment": seg_cnt,
        "all_circ_loop_positions_m": [round(c["t_mean"], 4) for c in circ],
    }

# ---------- T-02: pole census in joint zones ----------
pole_report = {}
for name, (p0s, p1s, rad) in SEG.items():
    p0, ax, L = seg_geom(p0s, p1s)
    poles = {}
    for v in bm.verts:
        t = in_finger(W[v.index], p0, ax, L, rad)
        if t is None:
            continue
        val = len(v.link_edges)
        if val != 4:
            poles[val] = poles.get(val, 0) + 1
    pole_report[name] = {"non_quad_valence_verts_in_finger_zone": poles,
                         "face_count_check": "n/a"}

full = {"ring_groups_total": len(groups),
        "closed_groups": sum(1 for g in groups if g["closed"]),
        "fingers": report,
        "poles": pole_report}
with open(r"<HANDS_ROOT>\production_spec\stage1c_c1_qualification\stats\topology_rings.json", "w") as f:
    json.dump(full, f, indent=1)
print(json.dumps(full, indent=1))
print("PASS5_DONE")
