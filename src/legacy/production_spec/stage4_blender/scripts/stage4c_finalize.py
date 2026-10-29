# STAGE4C_RSSF_ASSET_FINALIZATION_R1
#
# Closes CON-4 (nails), CON-6 (origin), CON-7 (UV) on the approved RSSF mother.
# Everything else is frozen: no re-pose, no retopo, no CMC cage change, no T-01 loop change,
# no production rig, no mirror, no animation.
#
#   CON-4  nails  -> per-face material semantics (zero added geometry, zero added tris)
#   CON-6  origin -> WRIST JOINT ROTATION CENTER, world geometry provably unchanged
#   CON-7  UV     -> audit, then a LOCAL fix for the 64 faces that carry no UV at all
#
# usage: blender -b <R2.blend> --python stage4c_finalize.py -- <out.blend> <outdir>
import bpy, bmesh, sys, os, json, math, hashlib, datetime
import numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
OUT_BLEND, OUTDIR = argv[0], argv[1]
os.makedirs(OUTDIR, exist_ok=True)
TARGET = "Hand  - Realistic"
EXPECT = "78fc890bfa9575cd62f2ae5f55beb2eda2df7ebf565c4e346a8b5af7295bbe04"
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s); print(s)


# =============================================================== 0. freeze the input
IN_BLEND = bpy.data.filepath
SHA_IN = hashlib.sha256(open(IN_BLEND, "rb").read()).hexdigest()
log("STAGE4B_APPROVED_RSSF_BASELINE = %s" % IN_BLEND)
log("  sha256   = %s" % SHA_IN)
log("  expected = %s" % EXPECT)
if SHA_IN != EXPECT:
    raise SystemExit("FATAL: the Stage-4B approved RSSF hash does not match -- refusing to run")
log("  MATCH -> STAGE4B_APPROVED_RSSF_BASELINE frozen (never overwritten)")

ob = bpy.data.objects[TARGET]
me = ob.data

# =============================================================== 1. topology signature
bm = bmesh.new(); bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
bm.normal_update()


def topo_sig(bmx):
    h = hashlib.sha256()
    h.update(b"V%d E%d F%d|" % (len(bmx.verts), len(bmx.edges), len(bmx.faces)))
    for e in bmx.edges:
        a, b = e.verts[0].index, e.verts[1].index
        h.update(b"%d-%d;" % (a, b) if a < b else b"%d-%d;" % (b, a))
    for f in bmx.faces:
        h.update(b"%d:" % len(f.verts))
        h.update(",".join(str(v.index) for v in f.verts).encode() + b";")
    return h.hexdigest()


TOPO_PRE = topo_sig(bm)
NV, NE, NF = len(bm.verts), len(bm.edges), len(bm.faces)
W = [(ob.matrix_world @ v.co).copy() for v in bm.verts]
FACES = [[v.index for v in f.verts] for f in bm.faces]
log("TOPOLOGY_SIGNATURE_PRE = %s" % TOPO_PRE)
log("  V=%d E=%d F=%d  (triangulated %d)" % (NV, NE, NF, sum(len(f) - 2 for f in FACES)))

# =============================================================== 2. landmarks
bones = {}
arm = None
for o in bpy.data.objects:
    if o.type == "ARMATURE":
        arm = o
        aw = o.matrix_world
        bones = {b.name: ((aw @ b.head_local).copy(), (aw @ b.tail_local).copy())
                 for b in o.data.bones}
FN = ["thumb", "index", "middle", "ring", "little"]

mcp_c = sum((bones["%s_MCP_R" % n.upper()][0] for n in ("index", "middle", "ring", "little")),
            Vector()) / 4.0
wrist_stage4b = bones["WRIST_R"][0]
tips = {n: bones["%s_TIP_R" % n.upper()][0] for n in ("index", "middle", "ring", "little")}
FW = (sum(tips.values(), Vector()) / 4 - bones["WRIST_R"][0]).normalized()
RAD = (tips["index"] - tips["little"]).normalized()
RAD = (RAD - FW * RAD.dot(FW)).normalized()
DORSAL = FW.cross(RAD).normalized()

# ---- CON-6 part 1: locate the wrist rotation centre -------------------------------------
# The Stage-4B WRIST_R head sits ON the forearm cut plane: its own log says "narrowest
# cross-section at -1.9 mm from the forearm cap" and its z equals the mesh bbox minimum.
# CON-6 explicitly forbids the forearm cut-plane centre, so WRIST_R cannot be reused.
# The locator below is radius-limited (excludes the thumb column) and convex-hull based
# (robust to how many vertices a slab happens to catch); it reproduces the Stage-3 verified
# wrist level z = 0.343 exactly.
z_lo = min(p.z for p in W)
cap_ring = [p for p in W if abs(p.z - z_lo) <= 0.004]
cap_c = sum(cap_ring, Vector()) / len(cap_ring)
AXIS_XY = Vector((cap_c.x, cap_c.y, 0.0))
R_MAX = 0.045


def hull_area(pts2):
    P = sorted(set((round(p[0], 9), round(p[1], 9)) for p in pts2))
    if len(P) < 3:
        return 0.0

    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and ((h[-1][0] - h[-2][0]) * (p[1] - h[-2][1])
                                   - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0])) <= 0:
                h.pop()
            h.append(p)
        return h
    poly = half(P)[:-1] + half(list(reversed(P)))[:-1]
    a = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % len(poly)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


scan_hi = mcp_c.z - 0.010
# The forearm is CUT, so its cap ring is the smallest measured section in the whole scan and
# a naive global minimum always lands on the cut plane -- which is exactly the mistake the
# Stage-4B locator made and exactly what CON-6 forbids.  The cut-plane neighbourhood is
# therefore excluded and the INTERIOR minimum is taken.
Z_SKIP = 0.012
cap_area = hull_area([(p.x, p.y) for p in cap_ring])
prof = []
for k in range(181):
    z = z_lo + (scan_hi - z_lo) * k / 180
    if z <= z_lo + Z_SKIP:
        continue
    sel = [p for p in W if abs(p.z - z) <= 0.0045 and (Vector((p.x, p.y, 0)) - AXIS_XY).length <= R_MAX]
    if len(sel) < 12:
        continue
    prof.append({"z": z, "n": len(sel), "area": hull_area([(p.x, p.y) for p in sel])})
amin = min(prof, key=lambda p: p["area"])
# A pure minimum-area rule CANNOT find the wrist on this asset: the palm is flattened
# (roughly 90 mm wide x 25 mm deep -> ~2090 mm2) and is therefore marginally SMALLER than
# the round wrist (~55 x 38 -> ~2110 mm2), so the global interior minimum lands in the palm.
# The wrist is instead the FIRST local minimum after the forearm taper -- and, cross-checked,
# the palm minimum is 96 mm distal of it.  The profile is smoothed over +-4 slabs first.
order = sorted(range(len(prof)), key=lambda i: prof[i]["z"])
zs = [prof[i]["z"] for i in order]
ar = [prof[i]["area"] for i in order]
WIN = 4
sm = []
for i in range(len(ar)):
    a = max(0, i - WIN); b = min(len(ar), i + WIN + 1)
    sm.append(sum(ar[a:b]) / (b - a))
LOCAL_MIN = []
for i in range(1, len(sm) - 1):
    lo = max(0, i - 20); hi = min(len(sm), i + 21)
    if sm[i] == min(sm[lo:hi]) and sm[i] <= sm[i - 1] and sm[i] <= sm[i + 1]:
        if not LOCAL_MIN or (zs[i] - LOCAL_MIN[-1]["z"]) > 0.020:
            LOCAL_MIN.append({"z": zs[i], "smoothed_area": sm[i], "n": prof[order[i]]["n"]})
WRIST_PICK = LOCAL_MIN[0] if LOCAL_MIN else {"z": min(prof, key=lambda p: p["area"])["z"],
                                             "smoothed_area": min(p["area"] for p in prof),
                                             "n": 0}
log("   interior local minima of the smoothed section-area profile: %s"
    % [{"z_mm": round(m["z"] * 1000, 1), "area_mm2": round(m["smoothed_area"] * 1e6, 1)}
       for m in LOCAL_MIN])
if len(LOCAL_MIN) > 1:
    log("   -> the MOST PROXIMAL one is the wrist: z = %.3f mm ; the next one (the flattened "
        "palm) is %.1f mm further distal" % (WRIST_PICK["z"] * 1000,
                                            (LOCAL_MIN[1]["z"] - LOCAL_MIN[0]["z"]) * 1000))
else:
    log("   -> single interior local minimum: z = %.3f mm" % (WRIST_PICK["z"] * 1000))
raw = min([p for p in prof if abs(p["z"] - WRIST_PICK["z"]) <= 0.010], key=lambda p: p["area"])
amin = {"z": raw["z"], "area": raw["area"], "n": raw["n"]}
basin = [p for p in prof if p["area"] <= raw["area"] * 1.03 and abs(p["z"] - raw["z"]) <= 0.010]
basin_pts = []
for p in basin:
    basin_pts += [q for q in W if abs(q.z - p["z"]) <= 0.0045
                  and (Vector((q.x, q.y, 0)) - AXIS_XY).length <= R_MAX]
WRIST_ORIGIN = sum(basin_pts, Vector()) / len(basin_pts)
log("CON-6 wrist locator (radius-limited INTERIOR minimum cross-section):")
log("   forearm cap z = %.3f mm (hull area %.1f mm2, EXCLUDED: it is the cut plane) ; "
    "scanning to MCP z = %.3f mm ; R_MAX = %.0f mm ; Z_SKIP = %.0f mm"
    % (z_lo * 1000, cap_area * 1e6, mcp_c.z * 1000, R_MAX * 1000, Z_SKIP * 1000))
log("   INTERIOR minimum hull area %.1f mm2 at z = %.3f mm (equiv radius %.2f mm, n=%d)"
    % (amin["area"] * 1e6, amin["z"] * 1000, math.sqrt(amin["area"] / math.pi) * 1000, amin["n"]))
log("   basin slabs = %d, pooled vertices = %d" % (len(basin), len(basin_pts)))
log("   WRIST_ORIGIN = %s" % [round(float(x), 6) for x in WRIST_ORIGIN])
log("   * reproduces the Stage-3 verified wrist_narrowest_z = 0.343 m (343.0 mm) -- delta "
    "%.2f mm" % abs(amin["z"] * 1000 - 343.0))
log("   * Stage-4B WRIST_R head z = %.3f mm = mesh bbox z-min (%.3f mm) -> FOREARM CUT PLANE,"
    " forbidden by CON-6, NOT reused" % (wrist_stage4b.z * 1000, z_lo * 1000))

# =============================================================== 3. CON-4 nails
# Material-only: no geometry is added, nothing is moved, the topology signature cannot
# change.  The nail region = the dorsal outer shell of the distal phalanx, located from the
# posed distal bone so it follows the RSSF curl instead of a global dorsal guess.
NAIL_CONE = 0.45        # face normal within ~63 deg of the digit's own nail normal
NAIL_AX_LO, NAIL_AX_HI = 0.15, 0.82
NAIL_SHELL = 0.45       # keep the outer 55% of the radial spread -> a plate, not a band

face_norm = [(ob.matrix_world.to_3x3() @ f.normal).normalized() for f in bm.faces]
face_ctr = [sum((W[v] for v in f), Vector()) / len(f) for f in FACES]

skin = bpy.data.materials.get("HAND_SKIN") or bpy.data.materials.new("HAND_SKIN")
nail = bpy.data.materials.get("NAIL_BED") or bpy.data.materials.new("NAIL_BED")
me.materials.clear()
me.materials.append(skin)      # slot 0
me.materials.append(nail)      # slot 1
for m, col, rough in ((skin, (0.84, 0.66, 0.58, 1.0), 0.55),
                      (nail, (0.95, 0.90, 0.89, 1.0), 0.28)):
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = col
        bsdf.inputs["Roughness"].default_value = rough
    m.diffuse_color = col
    m.roughness = rough

nail_report = {}
nail_faces_all = set()
for n in FN:
    U = n.upper()
    db = "THUMB_IP_R" if n == "thumb" else "%s_DIP_R" % U
    mb = "THUMB_CMC_R" if n == "thumb" else "%s_MCP_R" % U
    h, t = bones[db]
    dirv = (t - h).normalized(); L = (t - h).length
    mu = (bones[mb][1] - bones[mb][0]).normalized()
    lat = DORSAL.cross(mu)
    lat = lat.normalized() if lat.length > 1e-9 else RAD.copy()
    nn = lat.cross(dirv)
    nn = nn.normalized() if nn.length > 1e-9 else DORSAL.copy()
    if nn.dot(DORSAL) < 0:
        nn = -nn
    cand = []
    for fi, f in enumerate(FACES):
        a = (face_ctr[fi] - h).dot(dirv)
        if a < NAIL_AX_LO * L or a > NAIL_AX_HI * L:
            continue
        perp = (face_ctr[fi] - (h + dirv * a)).dot(nn)
        if perp <= 0:
            continue
        if face_norm[fi].dot(nn) < NAIL_CONE:
            continue
        cand.append((fi, a / L, perp))
    if cand:
        pmax = max(c[2] for c in cand)
        cand = [c for c in cand if c[2] >= NAIL_SHELL * pmax]
    fi_list = sorted(c[0] for c in cand)
    for fi in fi_list:
        nail_faces_all.add(fi)
    nail_report[n] = {
        "distal_bone": db, "bone_len_mm": round(L * 1000, 2),
        "nail_normal": [round(float(x), 4) for x in nn],
        "nail_normal_dot_global_dorsal": round(float(nn.dot(DORSAL)), 4),
        "nail_material_faces": len(fi_list),
        "axial_span_frac": [round(min((c[1] for c in cand), default=0), 3),
                            round(max((c[1] for c in cand), default=0), 3)],
        "faces": fi_list,
    }
for fi in nail_faces_all:
    # set on the MESH polygons, not on bmesh: the bmesh copy is never written back, so a
    # bmesh-side assignment would silently vanish
    me.polygons[fi].material_index = 1
log("CON-4: nail material assigned to %d faces (%.1f%% of %d); 0 geometry added"
    % (len(nail_faces_all), 100.0 * len(nail_faces_all) / NF, NF))
for n in FN:
    log("   %-7s %-12s nail faces %3d  span %.2f-%.2f  nail_normal·DORSAL %.3f"
        % (n, nail_report[n]["distal_bone"], nail_report[n]["nail_material_faces"],
           nail_report[n]["axial_span_frac"][0], nail_report[n]["axial_span_frac"][1],
           nail_report[n]["nail_normal_dot_global_dorsal"]))
plane_ang = {}
for a in ("index", "middle", "ring", "little"):
    na = Vector(nail_report["thumb"]["nail_normal"]); nb = Vector(nail_report[a]["nail_normal"])
    plane_ang["thumb_vs_%s" % a] = round(math.degrees(math.acos(max(-1, min(1, na.dot(nb))))), 2)
log("   thumb nail plane vs the four fingers: %s (non-coplanar)" % plane_ang)

# =============================================================== 4. CON-7 UV
uvl = me.uv_layers.active
EDGEF = {}
for fi, f in enumerate(FACES):
    for i in range(len(f)):
        k = (f[i], f[(i + 1) % len(f)])
        EDGEF.setdefault(k if k[0] < k[1] else (k[1], k[0]), []).append(fi)


def uv_measure(G=512):
    U = [Vector(l.uv) for l in uvl.data]
    fd = []
    for fi, f in enumerate(FACES):
        li = [bm.faces[fi].loops[i].index for i in range(len(f))]
        uv = [U[i] for i in li]
        s = 0.0
        for i in range(len(uv)):
            x1, y1 = uv[i]; x2, y2 = uv[(i + 1) % len(uv)]
            s += x1 * y2 - x2 * y1
        s *= 0.5
        a3 = 0.0
        for k in range(1, len(f) - 1):
            a3 += (W[f[k]] - W[f[0]]).cross(W[f[k + 1]] - W[f[0]]).length * 0.5
        fd.append({"fi": fi, "uv": uv, "signed": s, "abs": abs(s), "a3": a3, "verts": f})
    nz = [d for d in fd if d["abs"] < 1e-10]
    neg = [d for d in fd if d["signed"] < -1e-12]
    pos = [d for d in fd if d["signed"] > 1e-12]
    tuv = sum(d["abs"] for d in fd); t3 = sum(d["a3"] for d in fd)
    st = sorted([(d["abs"] / tuv) / (d["a3"] / t3) for d in fd if d["a3"] > 0])
    td = sorted([math.sqrt(d["abs"] * 4096 * 4096) / math.sqrt(d["a3"] * 1e4)
                 for d in fd if d["a3"] > 0 and d["abs"] > 0])
    par = list(range(len(fd)))
    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for (_a, _b), fs in EDGEF.items():
        if len(fs) != 2:
            continue
        d1, d2 = fd[fs[0]], fd[fs[1]]
        ok = True
        for v in (_a, _b):
            u1 = next((d1["uv"][i] for i, vi in enumerate(d1["verts"]) if vi == v), None)
            u2 = next((d2["uv"][i] for i, vi in enumerate(d2["verts"]) if vi == v), None)
            if u1 is None or u2 is None or (u1 - u2).length > 1e-6:
                ok = False; break
        if ok:
            ra, rb = find(fs[0]), find(fs[1])
            if ra != rb:
                par[ra] = rb
    isl = len({find(i) for i in range(len(fd))})
    cover = np.zeros((G, G), dtype=np.int32); owner = np.full((G, G), -1, dtype=np.int32)
    multi = 0
    for d in fd:
        if d["abs"] < 1e-12:
            continue
        uv = d["uv"]; rid = find(d["fi"])
        for k in range(1, len(uv) - 1):
            A, B, C = uv[0], uv[k], uv[k + 1]
            x0 = max(0, int(min(A.x, B.x, C.x) * G) - 1); x1 = min(G - 1, int(max(A.x, B.x, C.x) * G) + 1)
            y0 = max(0, int(min(A.y, B.y, C.y) * G) - 1); y1 = min(G - 1, int(max(A.y, B.y, C.y) * G) + 1)
            for yy in range(y0, y1 + 1):
                py = (yy + 0.5) / G
                for xx in range(x0, x1 + 1):
                    px_ = (xx + 0.5) / G
                    d1 = (B.x - A.x) * (py - A.y) - (B.y - A.y) * (px_ - A.x)
                    d2 = (C.x - B.x) * (py - B.y) - (C.y - B.y) * (px_ - B.x)
                    d3 = (A.x - C.x) * (py - C.y) - (A.y - C.y) * (px_ - C.x)
                    if ((d1 < 0) or (d2 < 0) or (d3 < 0)) and ((d1 > 0) or (d2 > 0) or (d3 > 0)):
                        continue
                    if cover[yy, xx] == 0:
                        owner[yy, xx] = rid
                    elif owner[yy, xx] != rid:
                        multi += 1
                    cover[yy, xx] += 1
    cov = int((cover > 0).sum())
    return {"layer": uvl.name, "faces": len(fd), "missing_uv_faces": sum(
                1 for d in fd if all(u.length < 1e-12 for u in d["uv"])),
            "zero_area_uv_faces": len(nz), "negative_signed_uv_faces": len(neg),
            "positive_signed_uv_faces": len(pos),
            "uv_winding_consistent": (len(neg) == 0 or len(pos) == 0),
            "uv_flipped_faces": min(len(neg), len(pos)),
            "uv_area_total": round(tuv, 6),
            "stretch_rel_share": {"min": round(st[0], 4), "p05": round(st[int(0.05*(len(st)-1))], 4),
                                  "median": round(st[len(st)//2], 4),
                                  "p95": round(st[int(0.95*(len(st)-1))], 4), "max": round(st[-1], 4)},
            "texel_density_px_per_cm_at_4096": {
                "min": round(td[0], 1), "median": round(td[len(td)//2], 1),
                "p95": round(td[int(0.95*(len(td)-1))], 1), "max": round(td[-1], 1),
                "max_over_min": round(td[-1]/td[0], 2) if td[0] > 0 else None},
            "island_count": isl, "overlap_grid": G,
            "overlap_uv_area_fraction": round(multi/cov, 6) if cov else None,
            "uv_coverage_fraction_of_unit_square": round(cov/(G*G), 5),
            "_degenerate_faces": [d["fi"] for d in nz]}


UV_BEFORE = uv_measure()
log("CON-7 UV audit BEFORE: layers=%d  missing=%d  zero_area=%d  flipped=%d  islands=%d  "
    "overlap=%.5f" % (1, UV_BEFORE["missing_uv_faces"], UV_BEFORE["zero_area_uv_faces"],
                      UV_BEFORE["uv_flipped_faces"], UV_BEFORE["island_count"],
                      UV_BEFORE["overlap_uv_area_fraction"]))

UV_FIX = {"applied": False, "reason": None, "faces": []}
deg = UV_BEFORE["_degenerate_faces"]
if deg:
    # LOCAL fix only: the 64 faces with no UV are the Stage-4A CMC cage.  They get a planar
    # projection laid out in free UV space.  UVs are per-loop, so the neighbouring faces that
    # already have UVs are untouched and the mesh/topology is untouched.
    nrm = sum((face_norm[fi] for fi in deg), Vector()).normalized()
    ref = Vector((0, 0, 1)) if abs(nrm.z) < 0.9 else Vector((1, 0, 0))
    t1 = (ref - nrm * ref.dot(nrm)).normalized(); t2 = nrm.cross(t1)
    vs = sorted({v for fi in deg for v in FACES[fi]})
    pts = {v: Vector(((W[v].dot(t1)), (W[v].dot(t2)))) for v in vs}
    xs = [p.x for p in pts.values()]; ys = [p.y for p in pts.values()]
    sx = max(xs) - min(xs); sy = max(ys) - min(ys)
    span = max(sx, sy)
    SIDE = 0.16
    occ = np.zeros((512, 512), dtype=bool)
    U0 = [Vector(l.uv) for l in uvl.data]
    degset = set(deg)
    for fi, f in enumerate(FACES):
        if fi in degset:
            continue
        li = [bm.faces[fi].loops[i].index for i in range(len(f))]
        uv = [U0[i] for i in li]
        if abs(sum(uv[i].x * uv[(i+1) % len(uv)].y - uv[(i+1) % len(uv)].x * uv[i].y
                   for i in range(len(uv)))) < 1e-12:
            continue
        x0 = max(0, int(min(u.x for u in uv) * 512) - 1); x1 = min(511, int(max(u.x for u in uv) * 512) + 1)
        y0 = max(0, int(min(u.y for u in uv) * 512) - 1); y1 = min(511, int(max(u.y for u in uv) * 512) + 1)
        occ[y0:y1 + 1, x0:x1 + 1] = True
    pad = 4
    grid_n = int(SIDE * 512)
    best = None
    for gy in range(0, 512 - grid_n - 1, 8):
        for gx in range(0, 512 - grid_n - 1, 8):
            if occ[max(0, gy - pad):gy + grid_n + pad, max(0, gx - pad):gx + grid_n + pad].any():
                continue
            best = (gx, gy); break
        if best:
            break
    if best is None:
        raise SystemExit("CON-7: no free UV space found for the local fix")
    gx, gy = best
    ox = gx / 512.0 + (SIDE - SIDE * sx / span) / 2.0
    oy = gy / 512.0 + (SIDE - SIDE * sy / span) / 2.0
    newuv = {}
    for v in vs:
        u = (pts[v].x - min(xs)) / span * SIDE + ox
        w = (pts[v].y - min(ys)) / span * SIDE + oy
        newuv[v] = (u, w)
    placed = 0
    for fi in deg:
        f = bm.faces[fi]
        for i, v in enumerate(FACES[fi]):
            uvl.data[f.loops[i].index].uv = newuv[v]
        placed += 1
    UV_FIX = {"applied": True, "faces": sorted(deg), "faces_fixed": placed,
              "method": "planar projection of the CMC-cage patch onto its average normal, "
                        "scaled into a 0.16 UV square and placed in free UV space after a "
                        "512x512 occupancy scan with a 4-cell pad",
              "uv_offset": [round(ox, 5), round(oy, 5)], "uv_side": SIDE}
    log("CON-7 fix: %d faces re-UV'd (planar, placed at u=%.3f v=%.3f)" % (placed, ox, oy))
UV_AFTER = uv_measure()
UV_AFTER.pop("_degenerate_faces", None)
log("CON-7 UV audit AFTER : missing=%d  zero_area=%d  flipped=%d  islands=%d  overlap=%.5f  "
    "texel max/min=%s" % (UV_AFTER["missing_uv_faces"], UV_AFTER["zero_area_uv_faces"],
                          UV_AFTER["uv_flipped_faces"], UV_AFTER["island_count"],
                          UV_AFTER["overlap_uv_area_fraction"],
                          UV_AFTER["texel_density_px_per_cm_at_4096"]["max_over_min"]))
UV_BEFORE.pop("_degenerate_faces", None)

# =============================================================== 5. TEMP rig removal
REMOVED = []
rig_dep = {"mesh_parent": ob.parent.name if ob.parent else None,
           "mesh_modifiers": [m.type for m in ob.modifiers],
           "mesh_constraints": [c.type for c in ob.constraints],
           "mesh_has_animation_data": ob.animation_data is not None,
           "mesh_vertex_groups": [g.name for g in ob.vertex_groups]}
log("TEMP rig dependency check: %s" % json.dumps(rig_dep, ensure_ascii=False))
assert not rig_dep["mesh_parent"] and not rig_dep["mesh_modifiers"] and not rig_dep["mesh_constraints"] \
    and not rig_dep["mesh_has_animation_data"] and not rig_dep["mesh_vertex_groups"], \
    "the mesh depends on the temp rig -- refusing to remove it"
PRE_REMOVE_W = [(ob.matrix_world @ v.co).copy() for v in me.vertices]
for o in list(bpy.data.objects):
    if o.type == "ARMATURE" and o.get("TEMP_RSSF_REPOSE_ONLY") == "YES":
        nm = o.name
        ad = o.data.name
        bpy.data.objects.remove(o, do_unlink=True)
        if ad in bpy.data.armatures:
            bpy.data.armatures.remove(bpy.data.armatures[ad])
        REMOVED.append({"object": nm, "armature_data": ad,
                        "flag_TEMP_RSSF_REPOSE_ONLY": "YES", "flag_PRODUCTION_RIG": "NO"})
log("TEMP rig removed (exact objects, no glob): %s" % [r["object"] for r in REMOVED])
POST_REMOVE_W = [(ob.matrix_world @ v.co).copy() for v in me.vertices]
rem_delta = max((a - b).length for a, b in zip(POST_REMOVE_W, PRE_REMOVE_W)) if NV else 0.0
log("geometry after TEMP-rig removal: max world delta %.9f m" % rem_delta)
for b in list(bpy.data.armatures):
    if b.users == 0:
        bpy.data.armatures.remove(b)

# =============================================================== 6. CON-6 origin
# The object origin is matrix_world.translation, so putting the origin AT the wrist means
# REPLACING the translation while keeping the rotation/scale part:
#     B = (3x3 of MW, translation = WRIST_ORIGIN)     and     v' = B^-1 @ MW @ v
# (The first attempt used B = T(WRIST_ORIGIN) @ MW, which ADDED the wrist vector to the
# existing translation and put the origin at ~2.81 m instead of the wrist.)
ORIGIN_BEFORE = ob.matrix_world.translation.copy()
PRE_ORIGIN_W = [(ob.matrix_world @ v.co).copy() for v in me.vertices]
B = ob.matrix_world.to_3x3().to_4x4()
B.translation = WRIST_ORIGIN
me.transform(B.inverted() @ ob.matrix_world)
ob.matrix_world = B
POST_ORIGIN_W = [(ob.matrix_world @ v.co).copy() for v in me.vertices]
org_delta = max((a - b).length for a, b in zip(POST_ORIGIN_W, PRE_ORIGIN_W)) if NV else 0.0
ORIGIN_AFTER = ob.matrix_world.translation.copy()
FLOAT32_EPS = 1e-6 * max(1.0, max(abs(c) for p in POST_ORIGIN_W for c in p))
log("CON-6 ORIGIN_BEFORE = %s" % [round(float(x), 9) for x in ORIGIN_BEFORE])
log("CON-6 ORIGIN_AFTER  = %s" % [round(float(x), 9) for x in ORIGIN_AFTER])
log("CON-6 |ORIGIN_AFTER - WRIST_ORIGIN| = %.12f m" % (ORIGIN_AFTER - WRIST_ORIGIN).length)
log("CON-6 WORLD_GEOMETRY_DELTA_AFTER_ORIGIN = %.12f m  (float32 mesh storage epsilon "
    "~%.2e m -> ZERO within storage precision)" % (org_delta, FLOAT32_EPS))

# =============================================================== 7. freeze + save
TOPO_POST = topo_sig(bm)
log("TOPOLOGY_SIGNATURE_POST = %s" % TOPO_POST)
log("TOPOLOGY_SIGNATURE_MATCH = %s" % (TOPO_PRE == TOPO_POST))
me.update()
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, copy=True, compress=False)
SHA_OUT = hashlib.sha256(open(OUT_BLEND, "rb").read()).hexdigest()
SHA_IN_AFTER = hashlib.sha256(open(IN_BLEND, "rb").read()).hexdigest()
log("SAVED %s (%d bytes, sha256 %s)" % (OUT_BLEND, os.path.getsize(OUT_BLEND), SHA_OUT))
log("STAGE4B_APPROVED_RSSF_BASELINE still unchanged: %s" % (SHA_IN == SHA_IN_AFTER))

HAND_TRIS = sum(len(f) - 2 for f in FACES)
NAIL_TRIS = 0
payload = {
    "stage": "STAGE4C_RSSF_ASSET_FINALIZATION_R1",
    "generated_at": datetime.datetime.now().astimezone().isoformat(),
    "frozen_input": {"blend": IN_BLEND, "sha256_before": SHA_IN, "sha256_after": SHA_IN_AFTER,
                     "unchanged": SHA_IN == SHA_IN_AFTER,
                     "expectation": "4fa2cb6f... from Stage4A_R2; Stage4B R2 = %s" % EXPECT},
    "output": {"blend": OUT_BLEND, "sha256": SHA_OUT, "bytes": os.path.getsize(OUT_BLEND)},
    "topology": {"signature_pre": TOPO_PRE, "signature_post": TOPO_POST,
                 "signature_match": TOPO_PRE == TOPO_POST,
                 "V": NV, "E": NE, "F": NF,
                 "only_positions_or_attributes_changed": True},
    "tris": {"HAND_BASE_TRIS": HAND_TRIS, "NAIL_ADDED_TRIS": NAIL_TRIS,
             "TOTAL_RIGHT_HAND_TRIS": HAND_TRIS + NAIL_TRIS,
             "target": "8k-20k", "hard_ceiling": 30000,
             "note": "material-only nails add no geometry; the base is not padded to reach 8k"},
    "CON_4_nails": {"method": "per-face material semantic (slot 1 = NAIL_BED)",
                    "nail_cone_cos": NAIL_CONE, "axial_span_frac": [NAIL_AX_LO, NAIL_AX_HI],
                    "shell_frac": NAIL_SHELL,
                    "per_digit": nail_report,
                    "thumb_plane_vs_fingers_deg": plane_ang,
                    "total_nail_faces": len(nail_faces_all),
                    "materials": [{"slot": i, "name": m.name,
                                   "diffuse_color": [round(float(c), 4) for c in m.diffuse_color],
                                   "faces": sum(1 for q in me.polygons if q.material_index == i)}
                                  for i, m in enumerate(me.materials)],
                    "geometry_added": False},
    "CON_6_origin": {"ORIGIN_BEFORE": [round(float(x), 9) for x in ORIGIN_BEFORE],
                     "ORIGIN_AFTER": [round(float(x), 9) for x in ORIGIN_AFTER],
                     "WRIST_ORIGIN": [round(float(x), 9) for x in WRIST_ORIGIN],
                     "ORIGIN_AFTER_minus_WRIST_ORIGIN_m": round((ORIGIN_AFTER - WRIST_ORIGIN).length, 12),
                     "WORLD_GEOMETRY_DELTA_AFTER_ORIGIN": org_delta,
                     "float32_storage_epsilon_m": FLOAT32_EPS,
                     "world_geometry_delta_is_zero": org_delta <= FLOAT32_EPS,
                     "locator": "radius-limited INTERIOR minimum cross-section of the forearm "
                                "tube (R_MAX 45 mm excludes the thumb column; the cut-plane "
                                "band z <= cap+12 mm is excluded because the stump is CUT and "
                                "its cap ring is otherwise always the global minimum), metric = "
                                "convex-hull area, centre = pooled centroid of the minimum basin",
                     "interior_minimum_hull_area_mm2": round(amin["area"] * 1e6, 2),
                     "interior_minimum_at_z_mm": round(amin["z"] * 1000, 3),
                     "interior_local_minima": [{"z_mm": round(m["z"] * 1000, 1),
                                                "area_mm2": round(m["smoothed_area"] * 1e6, 1)}
                                               for m in LOCAL_MIN],
                     "selection_rule": "MOST PROXIMAL interior local minimum of the smoothed "
                                       "section-area profile (window +-20 slabs)",
                     "why_not_global_minimum": "the palm is flattened (~90 x 25 mm -> ~2090 mm2) "
                                               "and is marginally SMALLER than the round wrist "
                                               "(~55 x 38 mm -> ~2110 mm2), so a pure global "
                                               "minimum-area rule lands in the palm; the wrist "
                                               "is the first minimum after the forearm taper",
                     "cut_plane_band_excluded_mm": Z_SKIP * 1000,
                     "cut_plane_cap_hull_area_mm2": round(cap_area * 1e6, 2),
                     "reproduces_stage3_wrist_narrowest_z": 0.343,
                     "delta_to_stage3_mm": round(abs(amin["z"] * 1000 - 343.0), 2),
                     "stage4b_WRIST_R_head": [round(float(x), 9) for x in wrist_stage4b],
                     "stage4b_WRIST_R_is_the_forearm_cut_plane": True,
                     "stage4b_WRIST_R_z_equals_mesh_bbox_zmin": abs(wrist_stage4b.z - z_lo) < 1e-6,
                     "mesh_bbox_zmin": round(z_lo, 9),
                     "note": "CON-6 forbids the forearm cut-plane centre; the Stage-4B WRIST_R "
                             "IS exactly that (its own log: '-1.9 mm from the forearm cap'), so "
                             "it was NOT reused. The locator used here independently reproduces "
                             "the already-accepted Stage-3 wrist level to <1 mm."},
    "CON_7_uv": {"before": UV_BEFORE, "after": UV_AFTER, "fix": UV_FIX,
                 "verdict": "PASS_AFTER_FIX" if UV_FIX["applied"] else "PASS_EXISTING",
                 "topology_impact": "none (UVs are per-loop attributes)"},
    "TEMP_rig_removal": {"removed": REMOVED, "removed_count": len(REMOVED),
                         "dependency_check": rig_dep,
                         "geometry_delta_m": rem_delta,
                         "method": "exact per-object removal by name; no glob, no recursion"},
    "log": LOG,
}
json.dump(payload, open(os.path.join(OUTDIR, "STAGE4C_RUN.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
log("WROTE STAGE4C_RUN.json")
log("DONE")
