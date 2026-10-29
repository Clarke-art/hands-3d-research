# STAGE1C - Pass 3: finger segmentation, joint loop counting, pose delta measurement, evidence renders
# READ-ONLY on source file; all modifications are in-memory and never saved.
import bpy, bmesh, json, math
from mathutils import Vector, Euler

OUT_JSON = r"<HANDS_ROOT>\production_spec\stage1c_c1_qualification\stats\asset_analysis_pass3.json"
OUT_RENDER = r"<HANDS_ROOT>\production_spec\stage1c_c1_qualification\renders"
OUT_WIRE = r"<HANDS_ROOT>\production_spec\stage1c_c1_qualification\wireframes"

TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world

bm = bmesh.new()
bm.from_mesh(ob.data)
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()
W = [ (mw @ v.co).copy() for v in bm.verts ]
E = [ (e.verts[0].index, e.verts[1].index) for e in bm.edges ]

zmin = min(p.z for p in W); zmax = max(p.z for p in W)
zspan = zmax - zmin

# ---------- slice-based finger tracking ----------
def slice_blobs(c, cluster_tol=0.011):
    pts = []
    for (i0, i1) in E:
        z0, z1 = W[i0].z, W[i1].z
        if (z0 - c) * (z1 - c) < 0:
            t = (c - z0) / (z1 - z0)
            p = W[i0] + (W[i1] - W[i0]) * t
            pts.append(Vector((p.x, p.y)))
    # cluster
    blobs = []
    used = [False] * len(pts)
    for i in range(len(pts)):
        if used[i]:
            continue
        comp = [i]; used[i] = True
        queue = [i]
        while queue:
            j = queue.pop()
            for k in range(len(pts)):
                if not used[k] and (pts[j] - pts[k]).length <= cluster_tol:
                    used[k] = True; comp.append(k); queue.append(k)
        cen = Vector((0, 0))
        for k in comp:
            cen += pts[k]
        cen /= len(comp)
        blobs.append({"center": cen, "n": len(comp), "pts": [pts[k] for k in comp]})
    return blobs

# track fingers from distal tip upward
n_stations = 160
tracks = []  # each: {"samples": [(z, center, n)], "id"}
active = []
prev_blobs = None
for si in range(n_stations):
    c = zmin + (si + 0.5) / n_stations * zspan
    blobs = slice_blobs(c)
    if si < 8:
        continue  # skip the very tip rounding
    if prev_blobs is None:
        if len(blobs) in (4, 5):
            prev_blobs = blobs; active = [{"samples": [(c, b)] } for b in blobs]
        continue
    # match blobs to active tracks by nearest center
    new_active = []
    usedb = set()
    for tr in active:
        last = tr["samples"][-1][1]["center"]
        best, bd = None, 1e9
        for bi, b in enumerate(blobs):
            if bi in usedb: continue
            d = (b["center"] - last).length
            if d < bd: bd, best = d, bi
        if best is not None and bd < 0.05:
            usedb.add(best)
            tr["samples"].append((c, blobs[best]))
            new_active.append(tr)
        else:
            tracks.append(tr)  # finger ended (merged into palm)
    for bi, b in enumerate(blobs):
        if bi not in usedb and len(blobs) > len(active):
            new_active.append({"samples": [(c, b)]})
    active = new_active
    prev_blobs = blobs
    if len(active) == 0:
        break

for tr in active:
    tracks.append(tr)

# classify fingers
cands = []
for tr in tracks:
    s = tr["samples"]
    if len(s) < 10:
        continue
    tipz = s[0][0]
    xavg = sum(x[1]["center"].x for x in s) / len(s)
    cands.append({"track": tr, "tipz": tipz, "xavg": xavg, "nsamp": len(s)})
cands.sort(key=lambda d: -d["tipz"])  # highest tip (largest z) first -> thumb
names_by_rank = ["THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"]
fingers = {}
for i, cd in enumerate(cands[:5]):
    cd["name"] = names_by_rank[i] if i < 5 else f"F{i}"
    fingers[cd["name"]] = cd

# merge z (proximal end) per finger
for n, cd in fingers.items():
    s = cd["track"]["samples"]
    cd["merge_z"] = s[-1][0]
    cd["tip_z"] = s[0][0]
    cd["length_z"] = cd["merge_z"] - cd["tip_z"]

# ---------- assign verts to fingers & count ring levels ----------
def assign_finger_verts(cd, extra=0.006):
    s = cd["track"]["samples"]
    out = []
    for idx, p in enumerate(W):
        if p.z < cd["tip_z"] - 0.002 or p.z > cd["merge_z"] + extra:
            continue
        # find nearest sample
        best = None; bd = 1e9
        for (z, b) in s:
            d = math.hypot(p.x - b["center"].x, p.y - b["center"].y)
            if d < bd:
                bd, best = d, b
        r = max(0.012, (best["n"] ** 0.5) * 0.0022)
        if bd <= r + extra:
            out.append(idx)
    return out

def cluster_levels(vals, tol):
    vals = sorted(vals)
    levels = []
    cur = [vals[0]]
    for v in vals[1:]:
        if v - cur[-1] <= tol:
            cur.append(v)
        else:
            levels.append(sum(cur) / len(cur))
            cur = [v]
    levels.append(sum(cur) / len(cur))
    return levels

ring_data = {}
for n, cd in fingers.items():
    vidx = assign_finger_verts(cd)
    if n == "THUMB":
        # thumb axis oblique: PCA on assigned verts
        pts = [W[i] for i in vidx]
        mean = sum(pts, Vector()) / len(pts)
        cov = [[0.0] * 3 for _ in range(3)]
        for p in pts:
            d = p - mean
            for a in range(3):
                for b in range(3):
                    cov[a][b] += d[a] * d[b]
        # power iteration for principal axis
        vec = Vector((0.0, 0.0, 1.0))
        for _ in range(64):
            nv = Vector((sum(cov[a][b] * vec[b] for b in range(3)) for a in range(3)))
            if nv.length > 0: vec = nv.normalized()
        axial = sorted(((W[i] - mean).dot(vec), W[i].z) for i in vidx)
        tvals = [a[0] for a in axial]
        span_t = tvals[-1] - tvals[0]
        gaps = [tvals[i+1]-tvals[i] for i in range(len(tvals)-1) if tvals[i+1]-tvals[i] > 1e-5]
        med_gap = sorted(gaps)[len(gaps)//2] if gaps else 0.002
        levels = cluster_levels([t for t in tvals], max(0.0012, med_gap * 0.55))
        ring_data[n] = {"verts": len(vidx), "rings_total": len(levels), "median_gap": round(med_gap,5),
                        "axis_vec": [round(v,3) for v in vec], "levels": [round(l,4) for l in levels],
                        "t0": round(tvals[0],4), "t1": round(tvals[-1],4), "mean": [round(v,4) for v in mean]}
    else:
        zvals = [W[i].z for i in vidx]
        gaps = [zvals[i+1]-zvals[i] for i in range(len(zvals)-1) if zvals[i+1]-zvals[i] > 1e-5]
        med_gap = sorted(gaps)[len(gaps)//2] if gaps else 0.002
        levels = cluster_levels(zvals, max(0.0012, med_gap * 0.55))
        ring_data[n] = {"verts": len(vidx), "rings_total": len(levels), "median_gap": round(med_gap,5),
                        "levels": [round(l,4) for l in levels]}

# ---------- joint loop counts (verticals: rings within +-12% of finger length of joint) ----------
joint_report = {}
for n, cd in fingers.items():
    rd = ring_data[n]
    levels = rd["levels"]
    if n == "THUMB":
        t0, t1 = rd["t0"], rd["t1"]; L = t1 - t0
        joints = {"IP": t0 + 0.30 * L, "MCP_T": t0 + 0.58 * L, "CMC": t1}
    else:
        tip_z, merge_z = cd["tip_z"], cd["merge_z"]
        L = merge_z - tip_z
        joints = {"DIP": tip_z + 0.24 * L, "PIP": tip_z + 0.56 * L, "MCP": tip_z + 1.0 * L - 0.02 * L}
    jr = {}
    for jname, jpos in joints.items():
        w = max(0.10 * L, 0.006)
        cnt = sum(1 for l in levels if abs(l - jpos) <= w)
        jr[jname] = {"level": round(jpos, 4), "rings_near": cnt, "window": round(w, 4)}
    # rings per phalanx
    bounds = sorted(set([jv["level"] for jv in jr.values()] + [levels[0], levels[-1]]))
    per_seg = []
    for i in range(len(bounds) - 1):
        cnt = sum(1 for l in levels if bounds[i] < l <= bounds[i+1])
        per_seg.append([round(bounds[i],4), round(bounds[i+1],4), cnt])
    jr["phalanx_ring_segments"] = per_seg
    jr["rings_total"] = len(levels)
    joint_report[n] = jr

# ---------- spread & flexion angles ----------
pose = {}
# spread: angle between finger PCA axes in XY plane (index/middle/ring/little)
axes = {}
for n in ["INDEX", "MIDDLE", "RING", "LITTLE"]:
    cd = fingers[n]
    vidx = assign_finger_verts(cd)
    pts = [Vector((W[i].x, W[i].y)) for i in vidx]
    mean = sum(pts, Vector((0.0, 0.0))) / len(pts)
    cov = [[0.0, 0.0], [0.0, 0.0]]
    for p in pts:
        d = p - mean
        cov[0][0] += d.x*d.x; cov[0][1] += d.x*d.y; cov[1][1] += d.y*d.y
    cov[1][0] = cov[0][1]
    vec = Vector((1.0, 0.0))
    for _ in range(48):
        nv = Vector((cov[0][0]*vec.x + cov[0][1]*vec.y, cov[1][0]*vec.x + cov[1][1]*vec.y))
        if nv.length > 0: vec = nv.normalized()
    axes[n] = vec
def ang(a, b):
    d = max(-1.0, min(1.0, a.dot(b)/(a.length*b.length)))
    return math.degrees(math.acos(d))
pose["spread_deg"] = {f"{a}-{b}": round(ang(axes[a], axes[b]), 1)
                      for a, b in [("INDEX","MIDDLE"),("MIDDLE","RING"),("RING","LITTLE")]}

# flexion: segment direction changes in YZ plane (flexion = rotate toward palm = -Y)
for n in ["INDEX", "MIDDLE", "RING", "LITTLE"]:
    cd = fingers[n]
    tip_z, merge_z = cd["tip_z"], cd["merge_z"]; L = merge_z - tip_z
    zmarks = {"tip": tip_z + 0.03*L, "DIP": tip_z + 0.24*L, "PIP": tip_z + 0.56*L, "MCP": merge_z - 0.04*L}
    centers = {}
    s = cd["track"]["samples"]
    for k, zv in zmarks.items():
        best = min(s, key=lambda t: abs(t[0]-zv))
        centers[k] = best[1]["center"]
    # finger axis is mostly Z; use x for spread direction, y for flexion
    v1 = centers["DIP"] - centers["tip"]
    v2 = centers["PIP"] - centers["DIP"]
    f = {}
    dz1 = zmarks["DIP"] - zmarks["tip"]
    dz2 = zmarks["PIP"] - zmarks["DIP"]
    for nm, (dy, dz) in {"seg1_tip_DIP": (v1.y, dz1), "seg2_DIP_PIP": (v2.y, dz2)}.items():
        a = math.atan2(dy, abs(dz))
        f[nm] = round(math.degrees(a), 1)
    f["delta_seg1_to_seg2_deg"] = round(f["seg2_DIP_PIP"] - f["seg1_tip_DIP"], 1)
    pose[f"flexion_{n}"] = f
# thumb: axis angle vs index axis
th = ring_data["THUMB"]["axis_vec"]
pose["thumb_axis_vec"] = th
pose["thumb_axis_vs_Z_deg"] = round(math.degrees(math.acos(min(1.0, abs(th[2])))), 1)

# ---------- wrist / forearm ----------
# width profile along z above palm merge
allmerge = max(fingers[n]["merge_z"] for n in fingers)
prof = []
for i in range(60):
    z = allmerge + (zmax - allmerge) * (i + 0.5) / 60
    bl = slice_blobs(z, cluster_tol=0.02)
    if bl:
        xs = [b["center"].x for b in bl]
        prof.append((round(z, 4), len(bl), round(max(xs)-min(xs), 4)))
wrist_z = None
bestw = 1e9
for (z, nb, w) in prof:
    if nb == 1 and w < bestw:
        bestw, wrist_z = w, z
forearm_len = zmax - (wrist_z if wrist_z else allmerge)
hand_len = zmax - zmin - forearm_len
pose["forearm"] = {"palm_top_merge_z": round(allmerge,4), "wrist_narrowest_z": round(wrist_z,4) if wrist_z else None,
                   "wrist_width": round(bestw,4) if wrist_z else None,
                   "forearm_len_m": round(forearm_len,4), "hand_len_m": round(hand_len,4),
                   "ratio": round(forearm_len/max(1e-6,hand_len),3)}

result = {
    "n_tracks_found": len(tracks),
    "fingers": {n: {"tip_z": round(fingers[n]["tip_z"],4), "merge_z": round(fingers[n]["merge_z"],4),
                    "length_z": round(fingers[n]["length_z"],4), "x_avg": round(fingers[n]["xavg"],4),
                    "samples": len(fingers[n]["track"]["samples"])} for n in fingers},
    "ring_data": {n: {k: v for k, v in rd.items() if k != "levels"} for n, rd in ring_data.items()},
    "joint_loop_report": joint_report,
    "pose_metrics": pose,
}
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1, default=str)
print("PASS3_ANALYSIS_DONE")
print(json.dumps(result["joint_loop_report"], indent=1, default=str)[:3000])
print(json.dumps(result["pose_metrics"], indent=1, default=str)[:2000])

# =================== RENDERS ===================
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'SINGLE'
scene.display.shading.single_color = (0.65, 0.45, 0.85)
scene.display.shading.show_cavity = True
scene.display.shading.background_type = 'WORLD'
scene.display.render_aa = '8'
world = bpy.data.worlds[0]
bg = world.node_tree.nodes.get('Background')
bg.inputs[0].default_value = (0.92, 0.92, 0.92, 1.0)
scene.render.resolution_x = 1000
scene.render.resolution_y = 1300

for o in bpy.context.view_layer.objects:
    o.hide_render = (o.name != TARGET)

cam_data = bpy.data.cameras.new("ev_cam")
cam_data.type = 'ORTHO'
cam = bpy.data.objects.new("ev_cam", cam_data)
bpy.context.collection.objects.link(cam)
scene.camera = cam

cx = 1.404782 + 0.151189/2
cy = 0.011328
cz = 0.149 + 0.282857/2
ortho = 0.30

def shot(name, loc, rot, scale=ortho, res=(1000,1300)):
    cam.location = loc
    cam.rotation_euler = Euler([math.radians(r) for r in rot], 'XYZ')
    cam_data.ortho_scale = scale
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = OUT_RENDER + "\\" + name + ".png"
    bpy.ops.render.render(write_still=True)

# orientation: fingers -Z, dorsal +Y, palmar -Y, thumb +X, forearm +Z
shot("EVIDENCE_DORSAL",            (cx, cy+10, cz), (90, 0, 180))
shot("EVIDENCE_PALMAR",            (cx, cy-10, cz), (90, 0, 0))
shot("EVIDENCE_RADIAL",            (cx+10, cy, cz), (90, 0, -90))
shot("EVIDENCE_ULNAR",             (cx-10, cy, cz), (90, 0, 90))
shot("EVIDENCE_DISTAL",            (cx, cy, cz-10), (0, 0, 0), scale=0.22)
shot("EVIDENCE_PROXIMAL",          (cx, cy, cz+10), (180, 0, 0), scale=0.22)
shot("EVIDENCE_DORSAL_OBLIQUE_RADIAL", (cx+7.07, cy+7.07, cz), (90, 0, 225))
shot("EVIDENCE_DORSAL_OBLIQUE_ULNAR",  (cx-7.07, cy+7.07, cz), (90, 0, 135))

# wireframes: wireframe modifier trick (in-memory only)
ob.modifiers.new("wf_tmp", 'WIREFRAME')
wfm = ob.modifiers[-1]
wfm.thickness = 0.0012
wfm.use_boundary = True
wfm.use_even_offset = True
scene.display.shading.light = 'FLAT'
scene.display.shading.show_cavity = False
scene.display.shading.single_color = (0.15, 0.15, 0.18)

def shot_wire(name, loc, rot, scale, res=(1200,1200)):
    shot(name, loc, rot, scale, res)

# palm/hand center for closeups
shot_wire("WIREFRAME_DORSAL", (cx, cy+10, cz), (90, 0, 180), 0.30, (1100,1400))
shot_wire("WIREFRAME_PALMAR", (cx, cy-10, cz), (90, 0, 0), 0.30, (1100,1400))

# thumb CMC closeup: CMC near merge of thumb track
th = ring_data["THUMB"]
cmc_t = th["t1"]
# locate world pos of CMC: mean + axis*cmc_t
cmcp = Vector(th["mean"]) + Vector(th["axis_vec"]) * cmc_t
print("CMC_POS", [round(v,4) for v in cmcp])
loc = cmcp + Vector((0.25, 0.25, 0.25))
d = loc - cmcp
# point camera at cmcp: compute rotation via to_track_quat
cam.location = loc
direc = (cmcp - loc).normalized()
cam.rotation_euler = direc.to_track_quat('Z', 'Y').to_euler()
cam_data.ortho_scale = 0.07
scene.render.resolution_x, scene.render.resolution_y = (1200,1200)
scene.render.filepath = OUT_WIRE + "\\" + "WIREFRAME_THUMB_CMC.png"
bpy.ops.render.render(write_still=True)

# finger joints: MCP/PIP/DIP world coords from joint_report
for fn in ["INDEX", "RING"]:
    jr = joint_report[fn]
    s = fingers[fn]["track"]["samples"]
    for jn in ["MCP", "PIP", "DIP"]:
        zv = jr[jn]["level"]
        best = min(s, key=lambda t: abs(t[0]-zv))
        p = Vector((best[1]["center"].x, best[1]["center"].y, zv))
        loc = p + Vector((0.12, 0.18, 0.0))
        cam.location = loc
        direc = (p - loc).normalized()
        cam.rotation_euler = direc.to_track_quat('Z','Y').to_euler()
        cam_data.ortho_scale = 0.045
        scene.render.filepath = OUT_WIRE + "\\" + f"WIREFRAME_{fn}_{jn}.png"
        bpy.ops.render.render(write_still=True)

print("PASS3_DONE")
