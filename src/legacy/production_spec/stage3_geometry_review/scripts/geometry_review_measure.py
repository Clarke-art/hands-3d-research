# STAGE3 · Route C GEOMETRY REVIEW -- READ-ONLY measurement pass.
# Never saves, never modifies geometry.
# Corrected source frame (R1.3.1 ERRATA): RADIAL=+X , DORSAL=-Y , PALMAR=+Y , DISTAL=-Z
#
# Method notes
#  * wrist = minimum convex-hull cross-section area over sliding Z slices (z in 0.30..0.40),
#    deliberately excluding the forearm cut cap (z = 0.4316).
#  * each digit's vertex set is grown by a Dijkstra geodesic FROM ITS OWN TIP, so sets never
#    bleed across the interdigital air gap (a 3.4 cm air gap is ~8 cm along the surface).
#  * digit bands: along +X the order is little < ring < middle < index < thumb.
#
# usage: blender -b RIGHT_HAND_BOOTSTRAP_C1.blend --python geometry_review_measure.py -- <out.json>
import bpy, bmesh, json, sys, math, heapq
from mathutils import Vector, Matrix

TARGET = "Hand  - Realistic"
OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else sys.argv[-1]
ob = bpy.data.objects[TARGET]; mw = ob.matrix_world; me = ob.data
V = [mw @ v.co for v in me.vertices]; N = len(V)
R = {}

# ---- topology integrity
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
R["topology_integrity"] = {
    "vertex_count": N, "edge_count": len(me.edges), "face_count": len(me.polygons),
    "boundary_edges": sum(1 for e in bm.edges if len(e.link_faces) == 1),
    "nonmanifold_edges": sum(1 for e in bm.edges if len(e.link_faces) > 2),
    "loose_verts": sum(1 for v in bm.verts if not v.link_edges),
    "loose_edges": sum(1 for e in bm.edges if not e.link_faces),
    "degenerate_faces": sum(1 for f in bm.faces if f.calc_area() < 1e-12),
    "signed_volume_m3": round(bm.calc_volume(signed=True), 12)}
bm.free()
zs = [p.z for p in V]; ZMIN, ZMAX = min(zs), max(zs)

# ---- graph
adj = [[] for _ in range(N)]
for e in me.edges:
    a, b = e.vertices
    d = (V[a]-V[b]).length
    adj[a].append((b, d)); adj[b].append((a, d))
def dijkstra(sources):
    dist = [float('inf')]*N; pq = []
    for s in sources:
        dist[s] = 0.0; pq.append((0.0, s))
    heapq.heapify(pq)
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd; heapq.heappush(pq, (nd, v))
    return dist

# ---- wrist = min convex-hull area over sliding Z slices
def hull_area(pts):
    pts = sorted(set((round(p.x, 7), round(p.y, 7)) for p in pts))
    if len(pts) < 3: return 0.0
    def cr(o, a, b): return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lo = []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    up = []
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    h = lo[:-1] + up[:-1]
    a = 0.0
    for i in range(len(h)):
        x1, y1 = h[i]; x2, y2 = h[(i+1) % len(h)]
        a += x1*y2 - x2*y1
    return abs(a)/2
slices = []
z = 0.298
while z < 0.400:
    ps = [p for p in V if z <= p.z < z+0.010]
    if len(ps) >= 6:
        slices.append({"z": round(z+0.005, 4), "n": len(ps),
                       "hull_area_m2": round(hull_area(ps), 8),
                       "x_span": round(max(p.x for p in ps)-min(p.x for p in ps), 4),
                       "y_span": round(max(p.y for p in ps)-min(p.y for p in ps), 4)})
    z += 0.005
R["wrist_slices"] = slices
WRIST = min(slices, key=lambda s: s["hull_area_m2"])
WRIST_Z = WRIST["z"]
R["wrist_narrowest"] = WRIST

# ---- digit tips
BANDS = {"little": (1.335, 1.381), "ring": (1.381, 1.407),
         "middle": (1.407, 1.439), "index": (1.439, 1.461)}
wrist_ring = [i for i in range(N) if 0.330 <= V[i].z <= 0.360]
wr_centroid = sum((V[i] for i in wrist_ring), Vector((0,0,0)))/len(wrist_ring)
tip = {}
for nm, (xl, xh) in BANDS.items():
    c = [i for i in range(N) if xl <= V[i].x < xh and V[i].z <= 0.22]
    tip[nm] = min(c, key=lambda i: V[i].z)
tc = [i for i in range(N) if V[i].x >= 1.461 and 0.215 <= V[i].z <= 0.305]
tip["thumb"] = max(tc, key=lambda i: (V[i]-wr_centroid).length)

# ---- per-digit geodesic from its own tip
dtip = {nm: dijkstra([i]) for nm, i in tip.items()}
def dset(nm, window):
    return [i for i in range(N) if dtip[nm][i] <= window]

R["digits"] = {nm: {"tip": [round(c, 4) for c in V[tip[nm]]],
                    "tip_z_cm": round(V[tip[nm]].z*100, 2),
                    "geodesic_wrist_ring_to_tip_m": round(dijkstra(wrist_ring)[tip[nm]], 5)}
               for nm in tip}
R["digit_bands"] = {k: list(v) for k, v in BANDS.items()}
R["tip_distal_reach_order_most_to_least"] = sorted(tip, key=lambda k: V[tip[k]].z)
R["tip_pairwise_z_diff_mm"] = {f"{a}-{b}": round(abs(V[tip[a]].z - V[tip[b]].z)*1000, 2)
                               for a in tip for b in tip if a < b}

# ---- web gaps (45 mm own-tip windows -> strictly on each digit)
sets45 = {nm: dset(nm, 0.045) for nm in tip}
R["digit_set_sizes_45mm"] = {k: len(v) for k, v in sets45.items()}
gaps = {}
for a, b in (("little","ring"), ("ring","middle"), ("middle","index"), ("index","thumb")):
    best = None
    for i in sets45[a]:
        for j in sets45[b]:
            d = (V[i]-V[j]).length
            if best is None or d < best[0]:
                best = (d, i)
    gaps[f"{a}-{b}"] = {"min_surface_gap_mm": round(best[0]*1000, 2),
                        "separated_by_real_gap": best[0] > 0.001,
                        "gap_midpoint": [round(c, 4) for c in (V[best[1]]+V[best[1]])/2]}
R["adjacent_web_min_gaps"] = gaps

# ---- fingertip taper (rounded & tapering, not blunt / spiked)
R["fingertip_taper_radius_mm_vs_own_tip_depth"] = {
    nm: {"depth_2_4_6_8_11_14_mm": [
            round(sum((V[i] - sum((V[j] for j in dset(nm, dd)), Vector((0,0,0)))/max(1,len(dset(nm, dd)))).length
                      for i in dset(nm, dd)) / max(1, len(dset(nm, dd))) * 1000, 2)
            for dd in (0.002, 0.004, 0.006, 0.008, 0.011, 0.014)]}
    for nm in tip}

# ---- crease profile (radius along own-tip geodesic) -> phalanx segmentation
def crease(nm, rmax=0.100, nbin=20):
    rows = []
    for k in range(nbin):
        lo = k*rmax/nbin; hi = (k+1)*rmax/nbin
        idx = [i for i in range(N) if lo <= dtip[nm][i] < hi]
        if not idx:
            rows.append({"depth_mm": int((lo+hi)/2*1000), "n": 0, "radius_mm": None}); continue
        c = sum((V[i] for i in idx), Vector((0,0,0)))/len(idx)
        rows.append({"depth_mm": int((lo+hi)/2*1000), "n": len(idx),
                     "radius_mm": round(sum((V[i]-c).length for i in idx)/len(idx)*1000, 2)})
    # 3-bin moving average to suppress low-poly jitter, then count strong minima
    raw = [r["radius_mm"] for r in rows]
    sm = []
    for i in range(len(raw)):
        w = [raw[j] for j in range(max(0, i-1), min(len(raw), i+2)) if raw[j] is not None]
        sm.append(round(sum(w)/len(w), 2) if w else None)
    mins = [rows[i]["depth_mm"] for i in range(1, len(rows)-1)
            if sm[i] and sm[i-1] and sm[i+1] and sm[i] <= sm[i-1]*0.97 and sm[i] <= sm[i+1]*0.97]
    return {"rows": rows, "smoothed_radius_mm": sm,
            "strong_radius_minima_depth_mm": mins, "strong_minima_count": len(mins)}
R["crease_profiles"] = {nm: crease(nm) for nm in ("thumb", "index", "middle", "little")}

# ---- palm arches
def shell(zlo, zhi, xlo, xhi, binw=0.005):
    bins = {}
    for p in V:
        if zlo <= p.z <= zhi and xlo <= p.x <= xhi:
            bins.setdefault(int((p.x-xlo)/binw), []).append(p)
    return [{"x": round(xlo+k*binw+binw/2, 4), "n": len(bins[k]),
             "palmar_max_y": round(max(p.y for p in bins[k]), 4),
             "dorsal_min_y": round(min(p.y for p in bins[k]), 4)} for k in sorted(bins)]
R["metacarpal_shell_palmar_vs_dorsal"] = shell(0.240, 0.300, 1.345, 1.455)
lon = []
z = 0.20
while z < 0.36:
    ps = [p for p in V if z <= p.z < z+0.01 and 1.36 <= p.x <= 1.44]
    if ps:
        lon.append({"z": round(z+0.005,4), "n": len(ps),
                    "palmar_max_y": round(max(p.y for p in ps),4),
                    "dorsal_min_y": round(min(p.y for p in ps),4)})
    z += 0.01
R["longitudinal_palmar_profile"] = lon

# ---- thumb opposition
def plane_normal(pts):
    c = sum(pts, Vector((0,0,0)))/len(pts)
    cov = Matrix(((0.0,0,0),(0,0,0),(0,0,0)))
    for p in pts:
        d = p - c
        for i in range(3):
            for j in range(3):
                cov[i][j] += d[i]*d[j]
    tr = cov[0][0]+cov[1][1]+cov[2][2]
    M = Matrix(((tr,0,0),(0,tr,0),(0,0,tr))) - cov
    v = Vector((0,1,0))
    for _ in range(400):
        w = M @ v
        if w.length < 1e-16: break
        v = w.normalized()
    return c, v
_, thin_t = plane_normal([V[i] for i in dset("thumb", 0.025)])
_, thin_i = plane_normal([V[i] for i in dset("index", 0.025)])
_, thin_m = plane_normal([V[i] for i in dset("middle", 0.025)])
def ang(a, b): return round(math.degrees(math.acos(max(-1.0, min(1.0, abs(a.dot(b)))))), 2)
troot = min((V[i] for i in dset("thumb", 0.095)), key=lambda p: (p-wr_centroid).length)
ax_t = (V[tip["thumb"]] - troot).normalized()
ax_i = (V[tip["index"]] - min((V[i] for i in dset("index", 0.095)), key=lambda p: (p-wr_centroid).length)).normalized()
# digit-only axes (45 mm own-tip windows) -> the true interdigital (虎口) opening angle
troot45 = sum((V[i] for i in dset("thumb", 0.045)), Vector((0,0,0)))/len(dset("thumb", 0.045))
iroot45 = sum((V[i] for i in dset("index", 0.045)), Vector((0,0,0)))/len(dset("index", 0.045))
ax_t45 = (V[tip["thumb"]] - troot45).normalized()
ax_i45 = (V[tip["index"]] - iroot45).normalized()
def flat(v):
    w = Vector((v.x, 0.0, v.z)); return w.normalized() if w.length > 1e-9 else w
R["thumb"] = {
    "distal_thin_axis_thumb": [round(c,4) for c in thin_t],
    "distal_thin_axis_index": [round(c,4) for c in thin_i],
    "distal_thin_axis_middle": [round(c,4) for c in thin_m],
    "opposition_angle_vs_index_deg": ang(thin_t, thin_i),
    "opposition_angle_vs_middle_deg": ang(thin_t, thin_m),
    "thumb_axis": [round(c,4) for c in ax_t],
    "index_axis": [round(c,4) for c in ax_i],
    "thumb_index_axis_angle_3d_deg": ang(ax_t, ax_i),
    "thumb_index_axis_angle_in_palm_plane_deg": ang(flat(ax_t), flat(ax_i)),
    "thumb_index_axis_angle_digit_only_3d_deg": ang(ax_t45, ax_i45),
    "thumb_index_axis_angle_digit_only_in_palm_plane_deg": ang(flat(ax_t45), flat(ax_i45)),
    "thumb_root_point": [round(c,4) for c in troot],
    "thumb_root_distance_to_wrist_centroid_m": round((troot - wr_centroid).length, 4),
    "thumb_tip_offset_vs_finger_axis_dot_PALMAR": round((V[tip["thumb"]] - sum((V[tip[k]] for k in ("index","middle","ring","little")), Vector((0,0,0)))/4).dot(Vector((0,1,0))), 5),
}

# ---- hand / forearm lengths
mt = V[tip["middle"]]
R["wrist_narrowest_z"] = WRIST_Z
R["hand_length_wrist_to_middle_tip_cm"] = round((WRIST_Z - mt.z)*100, 2)
R["forearm_length_wrist_to_cut_cm"] = round((ZMAX - WRIST_Z)*100, 2)
R["forearm_to_hand_ratio"] = round((ZMAX - WRIST_Z)/(WRIST_Z - mt.z), 3)
R["total_asset_length_cm"] = round((ZMAX - mt.z)*100, 2)
R["forearm_cut"] = {"cap_z": round(ZMAX,4),
                    "cap_ngon_vertex_count": next(len(p.vertices) for p in me.polygons if len(p.vertices)>4),
                    "cap_area_m2": round(next(p.area for p in me.polygons if len(p.vertices)>4), 8)}
mcp_band = [p for p in V if 0.235 <= p.z <= 0.265 and p.x <= 1.458]
R["four_metacarpal_span_at_mcp_cm"] = round((max(p.x for p in mcp_band)-min(p.x for p in mcp_band))*100, 2)
R["palm_thickness_at_mcp_cm"] = round((max(p.y for p in mcp_band)-min(p.y for p in mcp_band))*100, 2)
R["wrist_section_span_cm"] = [round(WRIST["x_span"]*100,2), round(WRIST["y_span"]*100,2)]
R["asset_bbox_full"] = [round(min(p.x for p in V),4), round(max(p.x for p in V),4),
                        round(min(p.y for p in V),4), round(max(p.y for p in V),4),
                        round(min(p.z for p in V),4), round(max(p.z for p in V),4)]

# ---- chirality
c_fing = sum((V[tip[k]] for k in ("index","middle","ring","little")), Vector((0,0,0)))/4
core = [p for p in V if 0.23 <= p.z <= 0.32 and 1.34 <= p.x <= 1.45]
c_core = sum(core, Vector((0,0,0)))/len(core)
D = (c_fing - c_core).normalized()
tmp = V[tip["thumb"]] - c_core
Rr = (tmp - D*tmp.dot(D)).normalized()
crs = D.cross(Rr)
R["chirality"] = {"D_distal": [round(c,4) for c in D], "R_radial": [round(c,4) for c in Rr],
                  "DxR": [round(c,4) for c in crs],
                  "triple_DxR_dot_DORSAL(-Y)": round(crs.dot(Vector((0,-1,0))), 4),
                  "triple_DxR_dot_PALMAR(+Y)": round(crs.dot(Vector((0,1,0))), 4),
                  "verdict": "RIGHT_HAND" if crs.dot(Vector((0,-1,0))) > 0.5 else "NOT_RIGHT"}

# ---- islands / face budget
seen = [False]*N; islands = 0
for s in range(N):
    if seen[s]: continue
    islands += 1; st=[s]; seen[s]=True
    while st:
        u = st.pop()
        for v,_ in adj[u]:
            if not seen[v]: seen[v]=True; st.append(v)
R["mesh_islands"] = islands
nq = sum(1 for p in me.polygons if len(p.vertices)==4)
R["face_budget"] = {"base_faces": len(me.polygons), "base_quads": nq,
                    "base_ngons": sum(1 for p in me.polygons if len(p.vertices)>4),
                    "base_tris": sum(len(p.vertices)-2 for p in me.polygons),
                    "multires_total_levels": next((m.total_levels for m in ob.modifiers if m.type=='MULTIRES'),0),
                    "official_L1_faces": 3298, "official_L1_tris_est": 3298*2,
                    "projected_L2_faces": 3298*4, "projected_L2_tris_est": 3298*4*2,
                    "target_tris_single_hand": [8000,20000], "hard_ceiling_tris": 30000}
R["PASS"] = "STAGE3_MEASURE_DONE"
json.dump(R, open(OUT,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
for k in ("topology_integrity","digits","tip_distal_reach_order_most_to_least","adjacent_web_min_gaps",
          "fingertip_taper_radius_mm_vs_own_tip_depth","thumb","chirality","wrist_narrowest",
          "hand_length_wrist_to_middle_tip_cm","forearm_length_wrist_to_cut_cm","forearm_to_hand_ratio",
          "four_metacarpal_span_at_mcp_cm","palm_thickness_at_mcp_cm","mesh_islands","face_budget"):
    print(k, "=", json.dumps(R[k], ensure_ascii=False))
print("crease minima:", json.dumps({k: v["radius_minima_depth_mm"] for k,v in R["crease_profiles"].items()}))
print("WROTE", OUT)
