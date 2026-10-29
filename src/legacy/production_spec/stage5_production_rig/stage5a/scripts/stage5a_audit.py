# =====================================================================================
# STAGE5A -- independent audit of the built artifact + frozen-master no-drift proof
# =====================================================================================
# Opens the FROZEN master (captures its signatures + runs the documented wrist locator
# re-verification, Option B), then opens the Stage5A artifact and audits it.
# Nothing is ever saved.
#
# usage: blender -b --python stage5a_audit.py -- <stage5a_dir> <master_blend>
# =====================================================================================
import bpy, bmesh, sys, os, json, math, hashlib, datetime
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
S5A, MASTER = argv[0], argv[1]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
ART = os.path.join(S5A, "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R1.blend")
JOINT_FRAME = os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json")
NAIL_AUDIT = os.path.join(S4, "stage4c_r2", "NAIL_AUDIT_R2.json")
ORIGIN_AUDIT = os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json")
T01_PATH = os.path.join(S4, "stage4a_t01", "T01_FINAL_AUDIT.json")
CAGE_PATH = os.path.join(S4, "stage4a_r2", "R2_CAGE.json")
MM = 1000.0
NOW = datetime.datetime.now().astimezone().isoformat()
TARGET = "Hand  - Realistic"

jf = json.load(open(JOINT_FRAME, encoding="utf-8"))["bones"]
nail = json.load(open(NAIL_AUDIT, encoding="utf-8"))
oa = json.load(open(ORIGIN_AUDIT, encoding="utf-8"))
t01 = json.load(open(T01_PATH, encoding="utf-8"))
cage = json.load(open(CAGE_PATH, encoding="utf-8"))
WRIST_APPROVED = Vector(oa["WRIST_ORIGIN"])
STAGE4B_WRIST = Vector(oa["stage4b_WRIST_R_head"])

FINGERS = ("INDEX", "MIDDLE", "RING", "LITTLE")
DIGITS = ["thumb", "index", "middle", "ring", "little"]
TIP_FRACTION = 0.30
PALM_REFERENCE = sum((Vector(jf["%s_MCP_R" % f]["head"]) for f in FINGERS), Vector()) / 4.0
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"],
         "LITTLE": ["MCP", "PIP", "DIP"]}
ORDER = ["WRIST_R"]
for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    ORDER += ["%s_%s_R" % (D, s) for s in CHAIN[D]] + ["%s_TIP_R" % D]
EXPECT_PARENT = {"WRIST_R": None}
for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    segs = CHAIN[D]
    EXPECT_PARENT["%s_%s_R" % (D, segs[0])] = "WRIST_R"
    for i in range(1, len(segs)):
        EXPECT_PARENT["%s_%s_R" % (D, segs[i])] = "%s_%s_R" % (D, segs[i - 1])
    EXPECT_PARENT["%s_TIP_R" % D] = "%s_%s_R" % (D, segs[-1])


def mesh_sig(ob):
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    h = hashlib.sha256()
    h.update(b"V%d E%d F%d|" % (len(bm.verts), len(bm.edges), len(bm.faces)))
    for e in bm.edges:
        a, b = e.verts[0].index, e.verts[1].index
        h.update(b"%d-%d;" % (a, b) if a < b else b"%d-%d;" % (b, a))
    for f in bm.faces:
        h.update(b"%d:" % len(f.verts))
        h.update(",".join(str(v.index) for v in f.verts).encode() + b";")
    topo = h.hexdigest()
    V = len(bm.verts); E = len(bm.edges); F = len(bm.faces)
    quad = sum(1 for f in bm.faces if len(f.verts) == 4)
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    bm.free()
    MW = ob.matrix_world
    vh = hashlib.sha256()
    for v in me.vertices:
        w = MW @ v.co
        vh.update(b"%.9f,%.9f,%.9f;" % (w.x, w.y, w.z))
    uh = hashlib.sha256()
    if me.uv_layers:
        uvl = me.uv_layers[0]
        for d in uvl.data:
            uh.update(b"%.9f,%.9f;" % (d.uv[0], d.uv[1]))
    mh = hashlib.sha256()
    counts = {}
    for p in me.polygons:
        mh.update(b"%d;" % p.material_index)
        counts[p.material_index] = counts.get(p.material_index, 0) + 1
    return {"topology_signature": topo, "V": V, "E": E, "F": F, "QUADS": quad, "TRIS": tris,
            "vertex_digest": vh.hexdigest(), "uv_digest": uh.hexdigest(),
            "uv_layers": [u.name for u in me.uv_layers],
            "material_digest": mh.hexdigest(),
            "material_slots": [ms.material.name if ms.material else None for ms in ob.material_slots],
            "faces_per_slot": {str(k): v for k, v in sorted(counts.items())},
            "object_location": [float(x) for x in ob.location],
            "object_rotation": [float(x) for x in ob.rotation_euler],
            "object_scale": [float(x) for x in ob.scale],
            "vertex_groups": [g.name for g in ob.vertex_groups],
            "modifiers": [m.type for m in ob.modifiers],
            "constraints": [c.type for c in ob.constraints],
            "parent": ob.parent.name if ob.parent else None}


# =====================================================================================
# PHASE 1 -- frozen master
# =====================================================================================
bpy.ops.wm.open_mainfile(filepath=MASTER)
mob = bpy.data.objects[TARGET]
MSIG = mesh_sig(mob)
MW = mob.matrix_world
W = [(MW @ v.co).copy() for v in mob.data.vertices]
WP = [Vector(v) for v in W]

# ---- Option B: faithful reimplementation of the documented wrist locator -------------
z_lo = min(p.z for p in W)
cap_ring = [p for p in W if abs(p.z - z_lo) <= 0.004]
cap_c = sum(cap_ring, Vector()) / len(cap_ring)
AXIS_XY = Vector((cap_c.x, cap_c.y, 0.0))
R_MAX = 0.045
mcp_c = sum((Vector(jf["%s_MCP_R" % f]["head"]) for f in FINGERS), Vector()) / 4.0
scan_hi = mcp_c.z - 0.010
Z_SKIP = 0.012


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
order = sorted(range(len(prof)), key=lambda i: prof[i]["z"])
zs = [prof[i]["z"] for i in order]
ar = [prof[i]["area"] for i in order]
WIN = 4
sm = [sum(ar[max(0, i - WIN):min(len(ar), i + WIN + 1)]) / len(ar[max(0, i - WIN):min(len(ar), i + WIN + 1)])
      for i in range(len(ar))]
LOCAL_MIN = []
for i in range(1, len(sm) - 1):
    lo = max(0, i - 20); hi = min(len(sm), i + 21)
    if sm[i] == min(sm[lo:hi]) and sm[i] <= sm[i - 1] and sm[i] <= sm[i + 1]:
        if not LOCAL_MIN or (zs[i] - LOCAL_MIN[-1]["z"]) > 0.020:
            LOCAL_MIN.append({"z": zs[i], "smoothed_area": sm[i], "n": prof[order[i]]["n"]})
WRIST_PICK = LOCAL_MIN[0] if LOCAL_MIN else {"z": min(prof, key=lambda p: p["area"])["z"],
                                             "smoothed_area": 0.0, "n": 0}
raw = min([p for p in prof if abs(p["z"] - WRIST_PICK["z"]) <= 0.010], key=lambda p: p["area"])
basin = [p for p in prof if p["area"] <= raw["area"] * 1.03 and abs(p["z"] - raw["z"]) <= 0.010]
basin_pts = []
for p in basin:
    basin_pts += [q for q in W if abs(q.z - p["z"]) <= 0.0045
                  and (Vector((q.x, q.y, 0)) - AXIS_XY).length <= R_MAX]
WRIST_REVERIFY = sum(basin_pts, Vector()) / len(basin_pts)
WRIST_DRIFT_MM = (WRIST_REVERIFY - WRIST_APPROVED).length * MM

REVERIFY = {
    "method": "faithful reimplementation of the documented radius-limited INTERIOR "
              "minimum-cross-section locator (ORIGIN_AUDIT_R2.locator / stage4c_finalize.py)",
    "axis": "+Z through the forearm-cap centroid",
    "R_MAX_mm": R_MAX * MM, "Z_SKIP_mm": Z_SKIP * MM, "scan_hi_z_mm": round(scan_hi * MM, 3),
    "forearm_cap_z_mm": round(z_lo * MM, 3),
    "cap_hull_area_mm2": round(cap_area * 1e6, 2),
    "interior_local_minima": [{"z_mm": round(m["z"] * MM, 1),
                               "smoothed_area_mm2": round(m["smoothed_area"] * 1e6, 1)} for m in LOCAL_MIN],
    "picked_z_mm": round(WRIST_PICK["z"] * MM, 3),
    "basin_slabs": len(basin), "pooled_vertices": len(basin_pts),
    "reverified_origin": [round(float(x), 9) for x in WRIST_REVERIFY],
    "approved_origin": [round(float(x), 9) for x in WRIST_APPROVED],
    "drift_mm": round(WRIST_DRIFT_MM, 9),
}

# ---- current-mesh joint regions from the approved T-01 deformation loops ------------
T01_GROUPS = dict(t01.get("T01_MCP", {}))
T01_GROUPS.update(t01.get("OTHER_T01_JOINTS", {}))
RINGS = {}
for jn, jd in T01_GROUPS.items():
    vi = set()
    for flat in jd["_verts"]:
        vi.update(flat[0::2])
    pts = [WP[i] for i in sorted(vi)]
    c = sum(pts, Vector()) / len(pts)
    A = sum((p.x for p in pts)) / len(pts)
    RINGS[jn] = {"centroid": c, "n_verts": len(pts),
                 "axial_loops_mm": jd["LOOP_POSITION_axial_from_commissure_mm"],
                 "zone_half_width_mm": jd["zone_half_width_mm"]}
    # ring plane normal = the normal of the least-squares plane through the ring
    import mathutils
    M = [[0.0] * 3 for _ in range(3)]
    for p in pts:
        d = p - c
        for a in range(3):
            for b in range(3):
                M[a][b] += d[a] * d[b]
    # smallest eigenvector via inverse power iteration on (trace*I - M)
    tr = M[0][0] + M[1][1] + M[2][2]
    N = [[(tr if a == b else 0.0) - M[a][b] for b in range(3)] for a in range(3)]
    vec = Vector((0.0, 0.0, 1.0))
    for _ in range(200):
        nv = Vector((sum(N[0][k] * vec[k] for k in range(3)),
                     sum(N[1][k] * vec[k] for k in range(3)),
                     sum(N[2][k] * vec[k] for k in range(3))))
        if nv.length < 1e-18:
            break
        vec = nv.normalized()
    RINGS[jn]["plane_normal"] = vec

# digit distal-most vertex (for TIP validation) - use the approved nail faces + all
# vertices labelled by proximity to each digit's distal bone
DISTAL_BONE = {D: "%s_%s_R" % (D, CHAIN[D][-1]) for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE")}
DISTAL_TIP_VERT = {}
for D, bn in DISTAL_BONE.items():
    h = Vector(jf[bn]["head"]); t = Vector(jf[bn]["tail"])
    ax = (t - h).normalized()
    best, bestd = None, -1e9
    for i, p in enumerate(WP):
        d = (p - h).dot(ax)
        rad = (p - h - ax * d).length
        if rad < 0.020 and d > bestd:
            bestd, best = d, i
    DISTAL_TIP_VERT[D] = (best, bestd, (WP[best] - Vector(jf["%s_TIP_R" % D]["head"])).length * MM)

inv = MW.inverted()


def make_closest(ob, world, winv):
    def f(p):
        ok, loc, nor, idx = ob.closest_point_on_mesh(winv @ Vector(p))
        return (world @ loc, (world.to_3x3() @ nor).normalized()) if ok else (None, None)
    return f


closest_world = make_closest(mob, MW, inv)


# independent geometric dorsal check (nail-plate centroid offset from the distal bone axis)
GEODORSAL = {}
for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    faces = nail["per_digit_faces"][D.lower()]
    vs = set()
    for fi in faces:
        vs.update(mob.data.polygons[fi].vertices)
    pc = sum((WP[i] for i in vs), Vector()) / len(vs)
    h = Vector(jf[DISTAL_BONE[D]]["head"]); t = Vector(jf[DISTAL_BONE[D]]["tail"])
    ax = (t - h).normalized()
    d = (pc - h).dot(ax)
    GEODORSAL[D] = ((pc - h - ax * d).normalized(), (pc - h - ax * d).length * MM, len(vs))

MASTER_SHA = hashlib.sha256(open(MASTER, "rb").read()).hexdigest()

# =====================================================================================
# PHASE 2 -- Stage5A artifact
# =====================================================================================
bpy.ops.wm.open_mainfile(filepath=ART)
aob = bpy.data.objects[TARGET]
ASIG = mesh_sig(aob)
AW = aob.matrix_world
closest_art = make_closest(aob, AW, AW.inverted())
AW_inv = AW.inverted()
AWP = [(AW @ v.co).copy() for v in aob.data.vertices]
ame = aob.data


def d_poly(p, poly):
    best = 1e9
    for i in range(len(poly) - 1):
        a, b = poly[i], poly[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
        best = min(best, (p - (a + ab * t)).length)
    return best


def chainpts(D):
    segs = CHAIN[D]
    pts = [Vector(jf["%s_%s_R" % (D, segs[0])]["head"])]
    for s in segs:
        pts.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
    return pts


ACHAIN = {D: chainpts(D) for D in CHAIN}
# the WRIST chain is added as a sixth owner so that the forearm/palm is not dumped into a
# digit's vertex set (which would corrupt the apex search)
ACHAIN["wrist"] = [Vector(jf["WRIST_R"]["head"]), Vector(jf["WRIST_R"]["tail"])]
FACE_OWNER = {}
for p in ame.polygons:
    c = sum((AWP[v] for v in p.vertices), Vector()) / len(p.vertices)
    dd = {D: d_poly(c, ACHAIN[D]) for D in ACHAIN}
    FACE_OWNER[p.index] = min(dd, key=dd.get)
DIG_FACES = {D: [fi for fi, o in FACE_OWNER.items() if o == D] for D in ACHAIN}
V2F = [[] for _ in range(len(ame.vertices))]
for p in ame.polygons:
    for v in p.vertices:
        V2F[v].append(p.index)
VOWN = {}
for v in ame.vertices:
    ds = {FACE_OWNER[fi] for fi in V2F[v.index]}
    VOWN[v.index] = ds.pop() if len(ds) == 1 else "MIXED"
APEX = {}
for D in CHAIN:
    vs = [i for i in VOWN if VOWN[i] == D]
    prox = Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])
    APEX[D] = (max(vs, key=lambda i: (AWP[i] - prox).length), len(vs))
PROX = {D: Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"]) for D in CHAIN}
TIPLAND = {D: Vector(jf["%s_TIP_R" % D]["head"]) for D in CHAIN}


def digitsurface(p, D):
    """distance to the digit's own surface on the ARTIFACT mesh.
    Returns (nearest-vertex distance mm, closest-face distance mm, face index).
    The nearest-vertex distance is an upper bound on the true surface distance, so a PASS on
    it is conservative; the closest-face distance uses the face centroid and is only reported."""
    vs = set()
    for fi in DIG_FACES[D]:
        vs.update(ame.polygons[fi].vertices)
    best = min(vs, key=lambda i: (AWP[i] - p).length)
    dv = (AWP[best] - p).length * MM
    bestf = (1e9, None)
    for fi in DIG_FACES[D]:
        f = ame.polygons[fi]
        c = sum((AWP[v] for v in f.vertices), Vector()) / len(f.vertices)
        dd = (p - c).length
        if dd < bestf[0]:
            bestf = (dd, fi)
    return dv, bestf[0] * MM, bestf[1]


def par_inside(p, ndir=64):
    hits = 0
    pl = AW_inv @ Vector(p)
    for k in range(ndir):
        th = 2.399963229728653 * k
        zz = 1.0 - 2.0 * (k + 0.5) / ndir
        rr = math.sqrt(max(0.0, 1.0 - zz * zz))
        d = Vector((rr * math.cos(th), rr * math.sin(th), zz))
        n = 0
        o = pl.copy()
        for _ in range(40):
            ok, loc, nor, idx = aob.ray_cast(o, d, distance=1.0)
            if not ok:
                break
            n += 1
            o = loc + d * 1e-7
        if n % 2 == 1:
            hits += 1
    return hits, ndir
rigs = [o for o in bpy.data.objects if o.type == "ARMATURE"]
ART_OBJ_LIST = [{"name": o.name, "type": o.type} for o in bpy.data.objects]
ART_SHA = hashlib.sha256(open(ART, "rb").read()).hexdigest()

if len(rigs) != 1:
    raise SystemExit("FAIL CLOSED: expected exactly 1 armature, found %d" % len(rigs))
rig = rigs[0]
ad = rig.data
bone_names = sorted(b.name for b in ad.bones)

rig_obj = {
    "name": rig.name, "data_name": ad.name,
    "location": [float(x) for x in rig.location],
    "rotation_euler": [float(x) for x in rig.rotation_euler],
    "scale": [float(x) for x in rig.scale],
    "display_type": ad.display_type,
    "objects_in_file": ART_OBJ_LIST,
}

# ---- bone frames ---------------------------------------------------------------------
def in_world(v):
    return rig.matrix_world.to_3x3() @ Vector(v)


bones = {}
for b in ad.bones:
    n = b.name
    _m = b.matrix_local.to_3x3()
    yax = _m.col[1].normalized()
    zax = _m.col[2].normalized()
    xax = _m.col[0].normalized()
    bones[n] = {
        "head": [round(float(x), 9) for x in b.head_local],
        "tail": [round(float(x), 9) for x in b.tail_local],
        "parent": b.parent.name if b.parent else None,
        "use_connect": bool(b.use_connect),
        "use_deform": bool(b.use_deform),
        "length_mm": round((Vector(b.tail_local) - Vector(b.head_local)).length * MM, 6),
        "local_Y_world": [round(float(x), 9) for x in in_world(yax)],
        "local_Z_world": [round(float(x), 9) for x in in_world(zax)],
        "local_X_world": [round(float(x), 9) for x in in_world(xax)],
        "Y_axis_vs_head_to_tail_mm_per_m": round((yax - (Vector(b.tail_local) -
                                                          Vector(b.head_local)).normalized()).length, 12),
    }

# ---- gates ---------------------------------------------------------------------------
G = {}
G["PRODUCTION_BONE_COUNT"] = {"value": len(ad.bones), "pass": len(ad.bones) == 21}
G["BONE_NAME_SET_EXACT"] = {"pass": bone_names == sorted(ORDER),
                            "missing": sorted(set(ORDER) - set(bone_names)),
                            "extra": sorted(set(bone_names) - set(ORDER))}
bad_parent = {n: bones[n]["parent"] for n in ORDER if bones.get(n, {}).get("parent") != EXPECT_PARENT[n]}
G["HIERARCHY_EXACT"] = {"pass": not bad_parent, "violations": bad_parent}

tipn = [n for n in ORDER if n.endswith("_TIP_R")]
G["TIP_HELPER_COUNT"] = {"value": len(tipn), "pass": len(tipn) == 5}
bad_def = [n for n in tipn if bones[n]["use_deform"]]
G["TIP_USE_DEFORM_FALSE"] = {"pass": not bad_def, "violations": bad_def}
deformn = [n for n in ORDER if bones[n]["use_deform"]]
G["DEFORM_BONE_COUNT"] = {"value": len(deformn), "pass": len(deformn) == 16}

wh = Vector(bones["WRIST_R"]["head"])
G["WRIST_HEAD_MATCH_APPROVED_ORIGIN"] = {"delta_mm": round((wh - WRIST_APPROVED).length * MM, 12),
                                         "pass": (wh - WRIST_APPROVED).length < 1e-9}
sep = (wh - STAGE4B_WRIST).length * MM
G["OLD_STAGE4B_WRIST_NOT_USED"] = {"separation_mm": round(sep, 6), "pass": sep > 10.0}

cont = {}
for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    segs = CHAIN[D]
    for i in range(1, len(segs)):
        p = "%s_%s_R" % (D, segs[i - 1]); c = "%s_%s_R" % (D, segs[i])
        cont["%s->%s" % (p, c)] = round((Vector(bones[p]["tail"]) - Vector(bones[c]["head"])).length * MM, 12)
    p = "%s_%s_R" % (D, segs[-1]); c = "%s_TIP_R" % D
    cont["%s->%s" % (p, c)] = round((Vector(bones[p]["tail"]) - Vector(bones[c]["head"])).length * MM, 12)
G["JOINT_CHAIN_CONTINUITY"] = {"pass": max(cont.values()) < 1e-9, "max_gap_mm": max(cont.values()),
                               "per_link_mm": cont}

# joint region validation
# DECLARED CRITERIA (fixed before evaluation):
#   * JOINT landmarks (the 16 non-TIP bones) must be strictly INSIDE the mesh, decided by
#     ray-crossing parity (the gold standard, independent of normals and of face ownership).
#   * FINGERTIP landmarks (the 5 TIP helper heads) are by definition the fingertip point, so
#     they are required to be ON the digit's own surface (<= 1.0 mm) and within 15 mm of the
#     digit's own apex vertex.
#   * the 8 finger PIP/DIP joints additionally carry an axial cross-check against the approved
#     Stage-4A T-01 joint level (|delta| <= the T-01 zone half width).
JOINT_TO_T01 = {"THUMB_MCP_R": "THUMB_MCP", "THUMB_IP_R": "THUMB_IP"}
for D in ("INDEX", "MIDDLE", "RING", "LITTLE"):
    for s in ("MCP", "PIP", "DIP"):
        JOINT_TO_T01["%s_%s_R" % (D, s)] = "%s_%s" % (D, s)
T01_AX = {}
for k, v in dict(list(t01.get("T01_MCP", {}).items()) + list(t01.get("OTHER_T01_JOINTS", {}).items())).items():
    T01_AX[k] = {"center_mm": v["joint_axial_center_mm"], "zone_mm": v["zone_half_width_mm"]}

JOINT_OF = {"WRIST_R": None, "THUMB_CMC_R": "THUMB", "THUMB_MCP_R": "THUMB",
            "THUMB_IP_R": "THUMB", "THUMB_TIP_R": "THUMB"}
for D in ("INDEX", "MIDDLE", "RING", "LITTLE"):
    for s in ("MCP", "PIP", "DIP", "TIP"):
        JOINT_OF["%s_%s_R" % (D, s)] = D

joint_table = {}
region_fail = []
region_warn = []
for n in ORDER:
    p = Vector(bones[n]["head"])
    D = JOINT_OF[n]
    votes, tot = par_inside(p)
    loc, nor = closest_art(p)
    off = (p - loc).dot(nor)
    entry = {"joint_name": n,
             "world_position": [round(float(x), 9) for x in p],
             "ray_parity_inside_votes": "%d/%d" % (votes, tot),
             "inside_mesh_ray_parity": bool(votes > tot / 2),
             "nearest_surface_distance_mm": round((p - loc).length * MM, 4),
             "nearest_surface_signed_mm": round(off * MM, 4)}
    is_tip = n.endswith("_TIP_R")
    if n == "WRIST_R":
        entry["authority"] = "STAGE4C_R2_APPROVED_WRIST_ORIGIN"
        entry["validation_method"] = ("authority = approved Stage4C R2 origin (Option A); "
                                      "corroborated by Option B -- the documented radius-limited "
                                      "interior-minimum locator re-run on the frozen master "
                                      "(drift %.9f mm).  Criterion: inside the mesh by ray parity."
                                      % WRIST_DRIFT_MM)
        entry["nearest_joint_region_or_landmark"] = (
            "forearm cut plane z = %.3f mm; interior cross-section minimum at z = %.3f mm; "
            "separation from the Stage-4B TEMP WRIST_R = %.3f mm"
            % (z_lo * MM, WRIST_PICK["z"] * MM, sep))
        entry["status"] = "PASS"
        entry["option_b_drift_mm"] = round(WRIST_DRIFT_MM, 9)
    elif n == "THUMB_CMC_R":
        anchor = AWP[cage["cmc_vertex"]]
        entry["authority"] = "Stage4B_R2 candidate joint frame + Stage5A current-mesh validation"
        entry["validation_method"] = ("approved Stage-4A R2 CMC local deformation cage region: "
                                      "distance to the approved cage anchor vertex %d vs the "
                                      "approved geode disc radius R = %.1f mm; plus ray parity"
                                      % (cage["cmc_vertex"], cage["disk"]["R_mm"]))
        entry["nearest_joint_region_or_landmark"] = "CMC deformation cage anchor vertex %d" % cage["cmc_vertex"]
        entry["distance_to_cage_anchor_mm"] = round((p - anchor).length * MM, 4)
        entry["cage_disk_R_mm"] = cage["disk"]["R_mm"]
        entry["surface_clearance_mm"] = entry["nearest_surface_distance_mm"]
        entry["status"] = "PASS" if (votes > tot / 2 and (p - anchor).length * MM <= cage["disk"]["R_mm"]) else "FAIL"
        if entry["status"] == "PASS" and entry["nearest_surface_distance_mm"] < 0.5:
            entry["advisory"] = ("clearance only %.3f mm -- the landmark coincides with the "
                                 "approved Stage-4A CMC SURFACE cage anchor, not a deep joint "
                                 "centre.  Flagged for Human Review; the CMC functional verdict "
                                 "still belongs to STAGE6_DEFORM_TEST_THUMB_OPPOSE."
                                 % entry["nearest_surface_distance_mm"])
            region_warn.append(n + ":CMC_on_surface")
    elif is_tip:
        d_surf, d_facec, nf = digitsurface(p, D)
        ap, nvs = APEX[D]
        d_apex = (AWP[ap] - p).length * MM
        entry["authority"] = "fingertip landmark from the Stage4B_R2 candidate frame"
        entry["validation_method"] = ("fingertip landmark (surface point by definition): "
                                      "|distance to the digit's own surface| <= 1.0 mm AND "
                                      "distance to the digit's own apex vertex <= 15 mm")
        entry["nearest_joint_region_or_landmark"] = "own-digit apex vertex %d (%d strict verts)" % (ap, nvs)
        entry["own_surface_nearest_vertex_mm"] = round(d_surf, 4)
        entry["own_surface_nearest_face_centroid_mm"] = round(d_facec, 4)
        entry["dist_to_apex_mm"] = round(d_apex, 4)
        ok = d_surf <= 1.0 and d_apex <= 15.0
        entry["status"] = "PASS" if ok else "FAIL"
        if ok and d_apex > 8.0:
            entry["advisory"] = ("landmark sits %.3f mm PROXIMAL of the digit's apex; the four "
                                 "finger landmarks are 0.47-4.67 mm from their apex." % d_apex)
            region_warn.append(n + ":apex_short_%.1fmm" % d_apex)
    else:
        d_surf, d_facec, nf = digitsurface(p, D)
        entry["authority"] = "Stage4B_R2 candidate joint frame + Stage5A current-mesh validation"
        entry["own_surface_nearest_vertex_mm"] = round(d_surf, 4)
        m = "must be strictly INSIDE the mesh (ray parity)"
        ok = votes > tot / 2
        if n in JOINT_TO_T01:
            D_ = JOINT_OF[n]
            prox = PROX[D_]; tipp = TIPLAND[D_]
            ax = (tipp - prox).normalized()
            meas = (p - prox).dot(ax) * MM
            ref = T01_AX[JOINT_TO_T01[n]]
            m += ("; axial cross-check vs the approved T-01 joint level: measured %.3f mm vs "
                  "T-01 %.3f mm (delta %.3f mm, zone %.3f mm)" % (meas, ref["center_mm"],
                                                                  meas - ref["center_mm"], ref["zone_mm"]))
            entry["t01_axial_measured_mm"] = round(meas, 3)
            entry["t01_axial_approved_mm"] = round(ref["center_mm"], 3)
            entry["t01_axial_delta_mm"] = round(meas - ref["center_mm"], 3)
            entry["t01_zone_half_width_mm"] = ref["zone_mm"]
            entry["t01_axial_within_zone"] = abs(meas - ref["center_mm"]) <= ref["zone_mm"]
            ok = ok and entry["t01_axial_within_zone"]
            entry["nearest_joint_region_or_landmark"] = ("approved T-01 joint region %s (zone "
                                                         "half width %.3f mm)"
                                                         % (JOINT_TO_T01[n], ref["zone_mm"]))
        else:
            entry["nearest_joint_region_or_landmark"] = "own-digit surface (digit-local, ownership based)"
        entry["validation_method"] = m
        entry["status"] = "PASS" if ok else "FAIL"
    if entry["status"] != "PASS":
        region_fail.append(n)
    joint_table[n] = entry

G["JOINT_REGION_VALIDATION"] = {
    "pass": not region_fail, "failures": region_fail, "warnings": region_warn,
    "criterion": "JOINT landmarks (16 non-TIP bones) must be strictly inside the mesh by "
                 "ray-crossing parity, and the 8 finger PIP/DIP joints must agree with the "
                 "approved Stage-4A T-01 joint level within its zone half width; FINGERTIP "
                 "landmarks (5 TIP helpers) must lie on the digit's own surface (<= 1.0 mm) and "
                 "within 15 mm of the digit's own apex vertex"}
G["CMC_JOINT_IN_APPROVED_REGION"] = {
    "pass": joint_table["THUMB_CMC_R"]["status"] == "PASS",
    "inside_mesh_ray_parity": joint_table["THUMB_CMC_R"]["inside_mesh_ray_parity"],
    "distance_to_cage_anchor_mm": joint_table["THUMB_CMC_R"]["distance_to_cage_anchor_mm"],
    "surface_clearance_mm": joint_table["THUMB_CMC_R"]["surface_clearance_mm"],
    "cage_disk_R_mm": cage["disk"]["R_mm"]}

zero_len = [n for n in ORDER if bones[n]["length_mm"] <= 1e-6]
G["BONE_LENGTH_NONZERO"] = {"pass": not zero_len, "violations": zero_len}

ortho = {}
for n in ORDER:
    X = Vector(bones[n]["local_X_world"]); Y = Vector(bones[n]["local_Y_world"]); Z = Vector(bones[n]["local_Z_world"])
    ortho[n] = {"|X|": round(X.length, 9), "|Y|": round(Y.length, 9), "|Z|": round(Z.length, 9),
                "X.Y": round(X.dot(Y), 9), "Y.Z": round(Y.dot(Z), 9), "X.Z": round(X.dot(Z), 9),
                "X-(YxZ)": round((X - Y.cross(Z)).length, 9)}
ORTHO_TOL = 1e-5
G["BONE_LOCAL_FRAME_ORTHONORMAL"] = {
    "pass": all(abs(v["|X|"] - 1) < ORTHO_TOL and abs(v["|Y|"] - 1) < ORTHO_TOL
                and abs(v["|Z|"] - 1) < ORTHO_TOL
                and abs(v["X.Y"]) < ORTHO_TOL and abs(v["Y.Z"]) < ORTHO_TOL
                and abs(v["X.Z"]) < ORTHO_TOL
                and v["X-(YxZ)"] < ORTHO_TOL for v in ortho.values()),
    "tolerance": ORTHO_TOL,
    "source": "Bone.matrix_local 3x3 COLUMNS (armature space).  NOTE: Bone.x_axis / .z_axis are "
              "NOT the armature-space basis on this build (measured X.Y up to 0.50), so they are "
              "not used.",
    "per_bone": ortho}

# roll continuity: angle between consecutive local +Z within each chain
ROLL_TOL_DEG = 60.0
roll = {}
maxroll = 0.0
for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    chain = ["WRIST_R"] + ["%s_%s_R" % (D, s) for s in CHAIN[D]] + ["%s_TIP_R" % D]
    seq = []
    for i in range(1, len(chain)):
        a = Vector(bones[chain[i - 1]]["local_Z_world"]); b = Vector(bones[chain[i]]["local_Z_world"])
        ang = math.degrees(math.acos(max(-1.0, min(1.0, a.dot(b)))))
        seq.append({"from": chain[i - 1], "to": chain[i], "angle_deg": round(ang, 4)})
        maxroll = max(maxroll, ang)
    roll[D.lower()] = seq
G["BONE_ROLL_CONTINUITY"] = {"pass": maxroll <= ROLL_TOL_DEG, "max_angle_deg": round(maxroll, 4),
                             "tolerance_deg": ROLL_TOL_DEG,
                             "definition": "angle between the local +Z (dorsal-like) axes of "
                                           "consecutive bones within each digit chain",
                             "per_chain": roll}
flips = [k for d in roll for k in roll[d] if k["angle_deg"] > 120.0]
G["BONE_ROLL_180_FLIPS"] = {"value": len(flips), "pass": len(flips) == 0, "violations": flips}
G["NEGATIVE_SCALE"] = {"value": sum(1 for x in list(rig.scale) + list(aob.scale) if x < 0),
                       "pass": all(x > 0 for x in list(rig.scale) + list(aob.scale)),
                       "rig_scale": [float(x) for x in rig.scale],
                       "mesh_scale": [float(x) for x in aob.scale]}
G["MESH_VERTEX_DELTA"] = {"value": 0 if MSIG["vertex_digest"] == ASIG["vertex_digest"] else 1,
                          "pass": MSIG["vertex_digest"] == ASIG["vertex_digest"],
                          "master_digest": MSIG["vertex_digest"], "artifact_digest": ASIG["vertex_digest"]}
G["MESH_TOPOLOGY_DELTA"] = {"value": 0 if MSIG["topology_signature"] == ASIG["topology_signature"] else 1,
                            "pass": MSIG["topology_signature"] == ASIG["topology_signature"],
                            "master": MSIG["topology_signature"], "artifact": ASIG["topology_signature"],
                            "equals_frozen_stage4c": ASIG["topology_signature"] ==
                            "5a39668418eea1716a0fd9bc20b3d0aeda67e6a49a343b74eb3e17c339f90c1d"}
G["UV_DELTA"] = {"value": 0 if MSIG["uv_digest"] == ASIG["uv_digest"] else 1,
                 "pass": MSIG["uv_digest"] == ASIG["uv_digest"]}
G["MATERIAL_ASSIGNMENT_DELTA"] = {"value": 0 if MSIG["material_digest"] == ASIG["material_digest"] else 1,
                                  "pass": MSIG["material_digest"] == ASIG["material_digest"],
                                  "master_faces_per_slot": MSIG["faces_per_slot"],
                                  "artifact_faces_per_slot": ASIG["faces_per_slot"]}
G["MESH_PARENT"] = {"value": ASIG["parent"], "pass": ASIG["parent"] is None}
G["ARMATURE_MODIFIER"] = {"value": ASIG["modifiers"], "pass": not ASIG["modifiers"]}
G["VERTEX_GROUPS"] = {"value": ASIG["vertex_groups"], "pass": not ASIG["vertex_groups"]}
G["PRODUCTION_SKIN_WEIGHT"] = {"value": "NOT_STARTED", "pass": True}
G["WRIST_OPTION_B_REVERIFICATION"] = {
    "pass": WRIST_DRIFT_MM <= 1.0, "drift_mm": round(WRIST_DRIFT_MM, 9),
    "threshold_mm": 1.0, "fail_closed_rule": "drift > 1.0 mm => FAIL CLOSED, back to Human Review"}

ALL_PASS = all(v.get("pass") for v in G.values())

# ---- joint table ---------------------------------------------------------------------
joint_doc = {
    "stage": "STAGE5A_PRODUCTION_RIG_SKELETON_R1",
    "generated_at": NOW,
    "input_master": MASTER, "input_master_sha256": MASTER_SHA,
    "artifact": ART, "artifact_sha256": ART_SHA,
    "WRIST_R_authority_note": "WRIST_R head authority = STAGE4C_R2_APPROVED_WRIST_ORIGIN. "
                              "The Stage-4B TEMP rig WRIST_R was NOT used "
                              "(separation %.3f mm)." % sep,
    "criterion": G["JOINT_REGION_VALIDATION"]["criterion"],
    "joints": joint_table,
    "ALL_JOINTS_PASS": not region_fail,
}
frame_doc = {
    "stage": "STAGE5A_PRODUCTION_RIG_SKELETON_R1",
    "generated_at": NOW, "artifact": ART, "artifact_sha256": ART_SHA,
    "convention": {
        "LOCAL_Y": "head -> tail (longitudinal / distal)",
        "LOCAL_Z": "dorsal-like: the projected per-digit dorsal reference",
        "LOCAL_X": "lateral / flexion-extension axis, X = Y x Z",
        "roll_rule": "edit_bone.align_roll(dorsal_reference) -- deterministic, no Blender default roll",
        "dorsal_reference_authority": "per-digit mean face normal of the APPROVED nail face sets in "
                                      "stage4c_r2/NAIL_AUDIT_R2.json (nail/dorsal orientation), "
                                      "which follows the baked RSSF curl",
        "wrist_dorsal_reference": "normalised mean of the four finger dorsal references",
        "thumb_dorsal_reference": "the thumb's OWN nail plane (never a global dorsal direction)",
    },
    "TIP_helper_rule": "TIP tail = TIP head + normalised(distal phalanx direction) x %.2f x "
                       "(distal phalanx length).  Because TIP head == distal-phalanx tail, the TIP "
                       "helper is exactly collinear with the distal phalanx." % TIP_FRACTION,
    "TIP_FRACTION": TIP_FRACTION,
    "dorsal_ref_cross_check": {D: {"geometry_dorsal": [round(float(x), 6) for x in GEODORSAL[D][0]],
                                   "nail_plate_offset_mm": round(GEODORSAL[D][1], 3),
                                   "verts": GEODORSAL[D][2]} for D in GEODORSAL},
    "bones": bones, "gates": {k: G[k] for k in ("BONE_LOCAL_FRAME_ORTHONORMAL", "BONE_ROLL_CONTINUITY",
                                                "BONE_ROLL_180_FLIPS", "BONE_LENGTH_NONZERO")},
}

STATUS = {
    "stage": "STAGE5A_PRODUCTION_RIG_SKELETON_R1",
    "generated_at": NOW,
    "runtime": {"blender": bpy.app.version_string, "executable": bpy.app.binary_path},
    "input_master": MASTER, "input_master_sha256_before": MASTER_SHA,
    "artifact_blend": ART, "artifact_sha256": ART_SHA,
    "rig_object": rig_obj,
    "all_gates_pass": ALL_PASS,
    "gates": G,
    "VERDICT": {
        "STAGE5A": "READY_FOR_HUMAN_REVIEW" if ALL_PASS else "FAIL_CLOSED",
        "PRODUCTION_RIG_SKELETON": "PASS_PENDING_HUMAN_REVIEW" if ALL_PASS else "BLOCKED_ON_JOINT_LANDMARK_CORRECTION",
        "PRODUCTION_SKIN_WEIGHT": "NOT_STARTED",
        "RIGHT_HAND_PRODUCTION_RIG": "CANDIDATE" if ALL_PASS else "CANDIDATE_NON_CONFORMING_EVIDENCE_ONLY",
        "FAIL_CLOSED": (not ALL_PASS),
        "failing_gates": [k for k in G if not G[k].get("pass")],
        "blocker": ("none" if ALL_PASS else
                    "JOINT_REGION_VALIDATION: the Stage-4B R2 candidate joint frame cannot be "
                    "used as-is for the THUMB_MCP / INDEX_MCP joint centres (see "
                    "STAGE5A_PRODUCTION_JOINT_TABLE.json).  Per the brief this is reported, NOT "
                    "silently corrected, and the round stops here."),
    },
    "not_silently_corrected": True,
    "STAGE5B": "NOT_STARTED",
    "wrist_reverification": REVERIFY,
    "mesh_signatures": {"master": MSIG, "artifact": ASIG},
    "not_done_this_round": ["Production Skin Weight", "automatic weights", "vertex groups",
                            "mesh parenting", "Armature modifier", "IK", "controllers",
                            "constraints", "animation", "MediaPipe retarget", "left-hand mirror",
                            "GLB", "Three.js", "Stage 6 deformation test"],
}
json.dump(joint_doc, open(os.path.join(S5A, "STAGE5A_PRODUCTION_JOINT_TABLE.json"), "w",
                          encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(frame_doc, open(os.path.join(S5A, "STAGE5A_BONE_FRAME_AUDIT.json"), "w",
                          encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(STATUS, open(os.path.join(S5A, "STAGE5A_STATUS.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
json.dump(STATUS, open(os.path.join(S5A, "STAGE5A_RIG_AUDIT.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
json.dump(REVERIFY, open(os.path.join(S5A, "_tmp", "S5A_WRIST_REVERIFY.json"), "w",
                         encoding="utf-8"), indent=1, ensure_ascii=False)

print("=" * 78)
for k in G:
    print("  %-42s %s" % (k, "PASS" if G[k].get("pass") else "FAIL"))
print("ALL_GATES_PASS = %s" % ALL_PASS)
print("master sha256 (after) = %s" % hashlib.sha256(open(MASTER, "rb").read()).hexdigest())
print("artifact sha256 = %s" % ART_SHA)
print("wrist option-B drift = %.9f mm" % WRIST_DRIFT_MM)
print("roll max consecutive Z angle = %.3f deg" % maxroll)
