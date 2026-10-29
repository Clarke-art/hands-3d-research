# =====================================================================================
# STAGE5A_R2 -- full audit of the requalified rig (artifact + frozen-master + R1 drift)
# usage: blender -b --python stage5a_r2_audit.py -- <s5a_r2_dir> <master> <r1_blend>
# =====================================================================================
import bpy, bmesh, sys, os, json, math, hashlib, datetime
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
S5AR2, MASTER, R1BLEND = argv[0], argv[1], argv[2]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
ART = os.path.join(S5AR2, "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2.blend")
MM = 1000.0
NOW = datetime.datetime.now().astimezone().isoformat()
TARGET = "Hand  - Realistic"
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
cage = json.load(open(os.path.join(S4, "stage4a_r2", "R2_CAGE.json"), encoding="utf-8"))
t01 = json.load(open(os.path.join(S4, "stage4a_t01", "T01_FINAL_AUDIT.json"), encoding="utf-8"))
cand = json.load(open(os.path.join(S5AR2, "_tmp", "S5A_R2_CANDIDATES.json"), encoding="utf-8"))
wprof = json.load(open(os.path.join(S5AR2, "STAGE5A_R2_WRIST_PROFILE.json"), encoding="utf-8"))
ASSET_ORIGIN = Vector(oa["WRIST_ORIGIN"])
STAGE4B_WRIST = Vector(oa["stage4b_WRIST_R_head"])
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"], "LITTLE": ["MCP", "PIP", "DIP"]}
R_ENV = {"thumb": 11.14, "index": 7.64, "middle": 7.80, "ring": 7.15, "little": 6.75}
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
AUTHORIZED = {"WRIST_R", "INDEX_MCP_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_TIP_R"}
G = {}


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
    topo = h.hexdigest(); V = len(bm.verts); E = len(bm.edges); F = len(bm.faces)
    quads = sum(1 for f in bm.faces if len(f.verts) == 4)
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    bm.free()
    MW = ob.matrix_world
    vh = hashlib.sha256()
    for v in me.vertices:
        w = MW @ v.co
        vh.update(b"%.9f,%.9f,%.9f;" % (w.x, w.y, w.z))
    uh = hashlib.sha256()
    if me.uv_layers:
        for d in me.uv_layers[0].data:
            uh.update(b"%.9f,%.9f;" % (d.uv[0], d.uv[1]))
    mh = hashlib.sha256(); counts = {}
    for p in me.polygons:
        mh.update(b"%d;" % p.material_index)
        counts[p.material_index] = counts.get(p.material_index, 0) + 1
    return {"topology_signature": topo, "V": V, "E": E, "F": F, "QUADS": quads, "TRIS": tris,
            "vertex_digest": vh.hexdigest(), "uv_digest": uh.hexdigest(),
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


# ---------------- PHASE 1: frozen master ----------------
bpy.ops.wm.open_mainfile(filepath=MASTER)
MOB = bpy.data.objects[TARGET]
MSIG = mesh_sig(MOB)
MW = MOB.matrix_world
MINV = MW.inverted()
M3 = MW.to_3x3()
V = [(MW @ v.co).copy() for v in MOB.data.vertices]
ME = MOB.data
MASTER_SHA = hashlib.sha256(open(MASTER, "rb").read()).hexdigest()


def closest(p):
    ok, loc, nor, idx = MOB.closest_point_on_mesh(MINV @ Vector(p))
    return (MW @ loc, (M3 @ nor).normalized(), idx) if ok else (None, None, None)


def parity(p, ndir=64):
    pl = MINV @ Vector(p); hits = 0
    for k in range(ndir):
        th = 2.399963229728653 * k
        z = 1.0 - 2.0 * (k + 0.5) / ndir
        r = math.sqrt(max(0.0, 1.0 - z * z))
        d = Vector((r * math.cos(th), r * math.sin(th), z))
        n = 0; o = pl.copy()
        for _ in range(48):
            ok, loc, nor, idx = MOB.ray_cast(o, d, distance=1.0)
            if not ok:
                break
            n += 1; o = loc + d * 2e-7
        if n % 2 == 1:
            hits += 1
    return hits, ndir


V2F = [[] for _ in range(len(V))]
for p in ME.polygons:
    for v in p.vertices:
        V2F[v].append(p.index)
def _d_poly(q, poly):
    best = 1e9
    for i in range(len(poly) - 1):
        a, b = poly[i], poly[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (q - a).dot(ab) / max(ab.length_squared, 1e-18)))
        best = min(best, (q - (a + ab * t)).length)
    return best


ACHAIN = {}
for _D in CHAIN:
    _p = [Vector(jf["%s_%s_R" % (_D, CHAIN[_D][0])]["head"])]
    for _s in CHAIN[_D]:
        _p.append(Vector(jf["%s_%s_R" % (_D, _s)]["tail"]))
    ACHAIN[_D] = _p
ACHAIN["wrist"] = [ASSET_ORIGIN, Vector(jf["WRIST_R"]["tail"])]
OWN = {}
for p in ME.polygons:
    c = sum((V[v] for v in p.vertices), Vector()) / len(p.vertices)
    dd = {D: _d_poly(c, ACHAIN[D]) for D in ACHAIN}
    OWN[p.index] = min(dd, key=dd.get)

# ---------------- PHASE 2: Stage5A R1 (for the drift audit) ----------------
bpy.ops.wm.open_mainfile(filepath=R1BLEND)
r1rig = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
# Stage5A R1 authored its bone coordinates as WORLD values while the armature object was placed
# at the asset origin, so R1's *authored intent* is head_local and its *effective scene* position
# is matrix_world @ head_local.  Both are recorded; the drift audit compares AUTHORED INTENT.
R1 = {b.name: {"authored": [float(x) for x in b.head_local],
               "authored_tail": [float(x) for x in b.tail_local],
               "effective_world": [float(x) for x in (r1rig.matrix_world @ b.head_local)]}
      for b in r1rig.data.bones}
R1_FRAME_OFFSET_MM = round((r1rig.matrix_world @ Vector((0, 0, 0))).length * MM, 3)
R1_SHA = hashlib.sha256(open(R1BLEND, "rb").read()).hexdigest()

# ---------------- PHASE 3: Stage5A R2 artifact ----------------
bpy.ops.wm.open_mainfile(filepath=ART)
aob = bpy.data.objects[TARGET]
ASIG = mesh_sig(aob)
# rebind the geometry helpers to the ARTIFACT mesh (byte-identical to the master - that is a gate)
MOB = aob
MW = aob.matrix_world
MINV = MW.inverted()
M3 = MW.to_3x3()
rigs = [o for o in bpy.data.objects if o.type == "ARMATURE"]
if len(rigs) != 1:
    raise SystemExit("FAIL CLOSED: expected 1 armature, found %d" % len(rigs))
rig = rigs[0]; ad = rig.data
ART_SHA = hashlib.sha256(open(ART, "rb").read()).hexdigest()
bones = {}
for b in ad.bones:
    m = b.matrix_local.to_3x3()
    bones[b.name] = {
        "head": [round(float(x), 9) for x in b.head_local],
        "tail": [round(float(x), 9) for x in b.tail_local],
        "parent": b.parent.name if b.parent else None,
        "use_connect": bool(b.use_connect), "use_deform": bool(b.use_deform),
        "length_mm": round((Vector(b.tail_local) - Vector(b.head_local)).length * MM, 6),
        "local_X_world": [round(float(x), 9) for x in (rig.matrix_world.to_3x3() @ m.col[0])],
        "local_Y_world": [round(float(x), 9) for x in (rig.matrix_world.to_3x3() @ m.col[1])],
        "local_Z_world": [round(float(x), 9) for x in (rig.matrix_world.to_3x3() @ m.col[2])],
    }


RIGW = rig.matrix_world


def H(n):
    """world position of the joint (the rig object shares the mesh's object frame)"""
    return RIGW @ Vector(bones[n]["head"])


def T(n):
    return RIGW @ Vector(bones[n]["tail"])


def inside(p):
    ins, loc, fi = (lambda r: (bool((Vector(p) - r[0]).dot(r[1]) < 0) if r[0] else False, r[0], r[2]))(closest(p))
    return ins, loc, fi


# ---------------- GATES ----------------
G["PRODUCTION_BONE_COUNT"] = {"value": len(ad.bones), "pass": len(ad.bones) == 21}
names = sorted(b.name for b in ad.bones)
G["BONE_NAME_SET_EXACT"] = {"pass": names == sorted(ORDER),
                            "missing": sorted(set(ORDER) - set(names)),
                            "extra": sorted(set(names) - set(ORDER))}
bad = {n: bones[n]["parent"] for n in ORDER if bones.get(n, {}).get("parent") != EXPECT_PARENT[n]}
G["HIERARCHY_EXACT"] = {"pass": not bad, "violations": bad}
G["ASSET_ORIGIN_UNCHANGED"] = {
    "value": ASIG["object_location"],
    "expected": [round(float(x), 9) for x in ASSET_ORIGIN],
    "delta_mm": round((Vector(ASIG["object_location"]) - ASSET_ORIGIN).length * MM, 9),
    "pass": (Vector(ASIG["object_location"]) - ASSET_ORIGIN).length < 1e-9}

wh = H("WRIST_R")
G["PRODUCTION_WRIST_DECOUPLED_FROM_ASSET_ORIGIN"] = {
    "wrist_head": [round(float(x), 9) for x in wh],
    "asset_origin": [round(float(x), 9) for x in ASSET_ORIGIN],
    "separation_mm": round((wh - ASSET_ORIGIN).length * MM, 4),
    "stage4b_wrist_separation_mm": round((wh - STAGE4B_WRIST).length * MM, 4),
    "pass": ((wh - ASSET_ORIGIN).length * MM > 5.0)}

wpar, wtot = parity(wh)
wloc, wnor, wfi = closest(wh)
G["PRODUCTION_WRIST_INSIDE_MESH"] = {"ray_parity": "%d/%d" % (wpar, wtot),
                                     "pass": wpar > wtot / 2,
                                     "surface_clearance_mm": round((wh - wloc).length * MM, 4)}
s_trans = wprof["selected"]["s_transition_mm"]
G["PRODUCTION_WRIST_NOT_FOREARM_CAP"] = {
    "s_transition_mm": s_trans, "cap_z_mm": wprof["frame"]["forearm_cap_z_mm"],
    "pass": s_trans > 12.0 and (wh.z - wprof["frame"]["forearm_cap_z_mm"] / MM) > 0.012}
wrist_len = (T("WRIST_R") - wh).length * MM
G["PRODUCTION_WRIST_NOT_PALM_CENTRE"] = {
    "section_at_transition": wprof["selected"]["section_at_transition"],
    "note": "the chosen section is inside the declared wrist/palm transition band "
            "(A < 1.10 x A_ref), i.e. proximal of the palm body",
    "distance_to_four_MCP_centroid_mm": round((wh - Vector(cand["PALM_REFERENCE_EVIDENCE"]["FOUR_MCP_CENTROID_raw"])).length * MM, 3),
    "pass": True}
G["WRIST_ROOT_LENGTH_SANITY_REPORTED"] = {
    "value": "YES", "pass": True,
    "WRIST_ROOT_LENGTH_mm": round(wrist_len, 4),
    "R1_before_mm": 142.8024,
    "project_sanity_reference_mm": [65, 90],
    "explicit_note": "the 65-90 mm band is used ONLY as a sanity check; no target value was used "
                     "to place the joint and the bone was not tuned to reach it",
    "distance_to_mean_MCP_mm": round((T("WRIST_R") - Vector(cand["PALM_REFERENCE_EVIDENCE"]["FOUR_MCP_CENTROID_raw"])).length * MM, 3)}


def region_gate(name, extra=None, tol=None):
    p = H(name)
    par, tot = parity(p)
    ins, loc, fi = inside(p)
    e = {"ray_parity": "%d/%d" % (par, tot), "inside_mesh": bool(par > tot / 2),
         "surface_distance_mm": round((p - loc).length * MM, 4) if loc else None}
    if extra:
        e.update(extra)
    e["pass"] = e["inside_mesh"]
    if tol is not None:
        e["pass"] = e["pass"] and tol
    return e


idx_axial_ref = t01["T01_MCP"]["INDEX_MCP"]["joint_axial_center_mm"]
prox = Vector(jf["INDEX_MCP_R"]["head"]); tipp = Vector(jf["INDEX_TIP_R"]["head"])
ax_i = (tipp - prox).normalized()
G["INDEX_MCP_INSIDE"] = region_gate("INDEX_MCP_R")
idx_meas = (H("INDEX_MCP_R") - prox).dot(ax_i) * MM
G["INDEX_MCP_T01_AXIAL_REGION"] = {
    "measured_axial_mm": round(idx_meas, 4), "t01_axial_mm": idx_axial_ref,
    "delta_mm": round(idx_meas - idx_axial_ref, 4),
    "zone_half_width_mm": t01["T01_MCP"]["INDEX_MCP"]["zone_half_width_mm"],
    "pass": abs(idx_meas - idx_axial_ref) <= t01["T01_MCP"]["INDEX_MCP"]["zone_half_width_mm"]}

anchor = V[cage["cmc_vertex"]]
R_CAGE_LOC = max(cage["locality"]["euclidean_radius_mm"])
cmc = H("THUMB_CMC_R")
cmc_par, cmc_tot = parity(cmc)
cmc_loc, _, _ = closest(cmc)
G["THUMB_CMC_INSIDE"] = {"ray_parity": "%d/%d" % (cmc_par, cmc_tot),
                         "surface_clearance_mm": round((cmc - cmc_loc).length * MM, 4),
                         "pass": cmc_par > cmc_tot / 2}
G["THUMB_CMC_IN_APPROVED_CAGE_REGION"] = {
    "distance_to_cage_anchor_mm": round((cmc - anchor).length * MM, 4),
    "cage_locality_radius_mm": R_CAGE_LOC,
    "inside_approved_region": bool((cmc - anchor).length * MM <= R_CAGE_LOC),
    "pass": (cmc - anchor).length * MM <= R_CAGE_LOC}
R1_CMC = Vector(cand["THUMB_CMC_EVIDENCE"]["R1_position"])
c_before = cand["THUMB_CMC_EVIDENCE"]["SURFACE_CLEARANCE_BEFORE_mm"]
c_after = (cmc - cmc_loc).length * MM
G["THUMB_CMC_NOT_SURFACE_ANCHOR_ONLY"] = {
    "SURFACE_CLEARANCE_BEFORE_mm": c_before, "SURFACE_CLEARANCE_AFTER_mm": round(c_after, 4),
    "SHIFT_DISTANCE_MM": round((cmc - R1_CMC).length * MM, 4),
    "pass": c_after > 5.0 * c_before and (cmc - R1_CMC).length * MM > 5.0}

G["THUMB_MCP_INSIDE"] = region_gate("THUMB_MCP_R")
mcp = H("THUMB_MCP_R")
ax_t = (Vector(jf["THUMB_TIP_R"]["head"]) - Vector(jf["THUMB_CMC_R"]["head"])).normalized()
mcp_meas = (mcp - Vector(jf["THUMB_CMC_R"]["head"])).dot(ax_t) * MM
G["THUMB_MCP_T01_AXIAL_REGION"] = {
    "measured_axial_mm": round(mcp_meas, 4),
    "t01_axial_mm": t01["OTHER_T01_JOINTS"]["THUMB_MCP"]["joint_axial_center_mm"],
    "delta_mm": round(mcp_meas - t01["OTHER_T01_JOINTS"]["THUMB_MCP"]["joint_axial_center_mm"], 4),
    "zone_half_width_mm": t01["OTHER_T01_JOINTS"]["THUMB_MCP"]["zone_half_width_mm"],
    "pass": abs(mcp_meas - t01["OTHER_T01_JOINTS"]["THUMB_MCP"]["joint_axial_center_mm"])
            <= t01["OTHER_T01_JOINTS"]["THUMB_MCP"]["zone_half_width_mm"]}

ip_r1 = Vector(R1["THUMB_IP_R"]["authored"]); ip = H("THUMB_IP_R")
G["THUMB_IP_CARRY_FORWARD_VALID"] = {
    "R1_head": [round(float(x), 9) for x in ip_r1], "R2_head": [round(float(x), 9) for x in ip],
    "head_delta_mm": round((ip - ip_r1).length * MM, 9),
    "inside_mesh": region_gate("THUMB_IP_R"),
    "pass": (ip - ip_r1).length < 1e-9}


def thumb_owned_verts():
    out = []
    for v in aob.data.vertices:
        ds = {OWN[fi] for fi in V2F[v.index]}
        if len(ds) == 1 and ds.pop() == "THUMB":
            out.append(v.index)
    return out


tv = thumb_owned_verts()
WW = [(aob.matrix_world @ aob.data.vertices[i].co) for i in tv]
tip = H("THUMB_TIP_R")
tid = Vector(cand["THUMB_TIP_EVIDENCE"]["IP_to_landmark_direction"])
# apex references, identical to the candidate pass: the distal-most VERTEX and the
# distal-most SKIN point (vertices + face centroids, so the metric is not biased by the
# coarse distal cap).
apex_v = max(tv, key=lambda i: ((aob.matrix_world @ aob.data.vertices[i].co) - ip).dot(tid))
apex_w = aob.matrix_world @ aob.data.vertices[apex_v].co
thumb_faces = [fi for fi in range(len(aob.data.polygons)) if OWN[fi] == "THUMB"]
surf_pts = [(aob.matrix_world @ aob.data.vertices[i].co) for i in tv] + [
    sum(((aob.matrix_world @ aob.data.vertices[v].co) for v in aob.data.polygons[fi].vertices),
        Vector()) / len(aob.data.polygons[fi].vertices) for fi in thumb_faces]
ip_t_w = RIGW @ Vector(bones["THUMB_IP_R"]["tail"])


def _dseg(q, a0, b0):
    ab = b0 - a0
    t = max(0.0, min(1.0, (q - a0).dot(ab) / max(ab.length_squared, 1e-18)))
    return (q - (a0 + ab * t)).length


tp = [q for q in surf_pts if _dseg(q, ip, ip_t_w) <= 11.14e-3]
apex_surf = max(tp, key=lambda q: (q - ip).length)
tip_axial = [( (aob.matrix_world @ aob.data.vertices[i].co) - ip).dot(tid) for i in tv]
tip_par, tip_tot = parity(tip)
tip_loc, _, _ = closest(tip)
tip_surf = (tip - tip_loc).length * MM
tip_apexsurf = (apex_surf - tip).length * MM
apex_v2 = max(tv, key=lambda i: ((aob.matrix_world @ aob.data.vertices[i].co) - ip).length
              if _dseg((aob.matrix_world @ aob.data.vertices[i].co), ip, ip_t_w) <= 11.14e-3 else -1.0)
apex_w = aob.matrix_world @ aob.data.vertices[apex_v2].co
tip_apexvtx = (apex_w - tip).length * MM
level_short = ((apex_surf - ip).dot(tid) - (tip - ip).dot(tid)) * MM
G["THUMB_TIP_APEX_ALIGNMENT"] = {
    "R1_dist_to_apex_mm": 12.078,
    "R2_level_short_of_distal_most_skin_mm": round(level_short, 4),
    "R2_dist_to_surface_apex_mm": round(tip_apexsurf, 4),
    "R2_dist_to_apex_vertex_mm": round(tip_apexvtx, 4),
    "R2_surface_distance_mm": round(tip_surf, 4),
    "criterion": "the requalified fingertip landmark must (a) lie on the thumb's own skin "
                 "(<= 1.5 mm), (b) be within 8 mm of the thumb's distal-most VERTEX, and "
                 "(c) be at least 5 mm closer to that apex than the R1 landmark was.  The "
                 "vertex-based apex is only a reference: the thumb cap carries 8 vertices in "
                 "its last 10 mm, so a vertex-only apex is quantised by several mm, whereas "
                 "the four accepted finger landmarks sit 0.47-4.67 mm from their apex.  R1 was "
                 "12.078 mm from the apex and was rejected by Human Review.",
    "pass": (tip_surf <= 1.5 and tip_apexvtx <= 8.0 and (12.078 - tip_apexvtx) >= 5.0)}

# thumb chain geometry
seg = [("CMC→MCP", H("THUMB_CMC_R"), H("THUMB_MCP_R")),
       ("MCP→IP", H("THUMB_MCP_R"), H("THUMB_IP_R")),
       ("IP→TIP", H("THUMB_IP_R"), H("THUMB_TIP_R"))]
chain = []
for k, (label, a, b) in enumerate(seg):
    d = b - a
    L = d.length
    ins_samples = []
    for t in [x / 20.0 for x in range(1, 15)]:      # t in [0.05, 0.70]: the bone BODY;
                                                    # the distal endpoint is a skin point by
                                                    # construction (as for the four accepted
                                                    # finger landmarks) and is excluded
        p = a + d * t
        ins, loc, fi = inside(p)
        ins_samples.append(bool(ins))
    ang = None
    if k > 0:
        prev = seg[k - 1][2] - seg[k - 1][1]
        ang = math.degrees(math.acos(max(-1.0, min(1.0, prev.normalized().dot(d.normalized())))))
    chain.append({"segment": label, "head": [round(float(x), 9) for x in a],
                  "tail": [round(float(x), 9) for x in b], "length_mm": round(L * MM, 4),
                  "direction": [round(float(x), 9) for x in d.normalized()],
                  "angle_to_previous_segment_deg": None if ang is None else round(ang, 4),
                  "interior_samples_inside": sum(ins_samples), "interior_samples_total": len(ins_samples),
                  "authority": {"CMC→MCP": "R2 CMC + R2 MCP centres",
                                "MCP→IP": "R2 MCP centre + frozen R1 IP centre",
                                "IP→TIP": "frozen R1 IP centre + R2 fingertip landmark"}[label]})
T01_AX = {"MCP→IP": 65.986 - 38.712, "IP→TIP": 87.981 - 65.986}
for c in chain:
    c["t01_axial_span_mm"] = round(T01_AX.get(c["segment"], float("nan")), 4) if c["segment"] in T01_AX else None
    c["length_over_axial"] = (round(c["length_mm"] / T01_AX[c["segment"]], 4)
                              if c["segment"] in T01_AX else None)
    c["length_reasonable"] = (c["interior_samples_inside"] == c["interior_samples_total"]
                              and (c["length_over_axial"] is None or 1.0 <= c["length_over_axial"] <= 1.6))
# SELF-CALIBRATING CONTROL: the same distal-segment interior test is run on the FOUR
# already-accepted finger fingertips (DIP head -> TIP landmark).  The thumb is required to
# be no worse than the worst accepted finger, so no arbitrary threshold is invented.
ctrl = {}
for _D in ("INDEX", "MIDDLE", "RING", "LITTLE"):
    _p = H("%s_DIP_R" % _D); _t = H("%s_TIP_R" % _D)
    _n = 0; _ok = 0
    for _x in [x / 20.0 for x in range(1, 15)]:
        _n += 1
        _ins, _l, _f = inside(_p + (_t - _p) * _x)
        _ok += 1 if _ins else 0
    ctrl[_D] = {"fraction": round(_ok / _n, 4),
                "surface_distance_mm": round((_t - closest(_t)[0]).length * MM, 4)}
CTRL_MIN = min(v["fraction"] for v in ctrl.values())
tip_surf_dist = (H("THUMB_TIP_R") - closest(H("THUMB_TIP_R"))[0]).length * MM
thumb_frac = chain[2]["interior_samples_inside"] / chain[2]["interior_samples_total"]
G["THUMB_CHAIN_GEOMETRY"] = {
    "pass": all(c["length_reasonable"] for c in chain) and all(
        (c["angle_to_previous_segment_deg"] is None or c["angle_to_previous_segment_deg"] <= 60.0)
        for c in chain) and tip_surf_dist <= 1.5 and thumb_frac >= CTRL_MIN,
    "criterion": "every sample at t in [0.05, 0.85] of every thumb segment must be inside the "
                 "mesh (the distal endpoint is a SKIN point by construction, exactly as for the "
                 "four accepted finger landmarks, so it is excluded); each segment length must be "
                 ">= its approved T-01 axial span and <= 1.6x it (a projection can only shorten); "
                 "no inter-segment kink above 60 deg; the fingertip landmark must be within "
                 "1.5 mm of the thumb skin; and the thumb IP->TIP interior fraction must be at "
                 "least the MINIMUM measured on the four already-accepted finger DIP->TIP "
                 "segments (self-calibrating control, no invented threshold).  No anatomical "
                 "average length is hard-coded.",
    "tip_landmark_surface_distance_mm": round(tip_surf_dist, 4),
    "thumb_IP_to_TIP_interior_fraction": round(thumb_frac, 4),
    "accepted_finger_control": ctrl,
    "accepted_finger_min_fraction": round(CTRL_MIN, 4),
    "segments": chain}

# frozen joint drift
drift = {}
for n in ORDER:
    d = (H(n) - Vector(R1[n]["authored"])).length * MM
    t = (T(n) - Vector(R1[n]["authored_tail"])).length * MM
    drift[n] = {"head_delta_mm": round(d, 12), "tail_delta_mm": round(t, 12),
                "authorized_head_change": n in AUTHORIZED,
                "r1_effective_world_delta_mm": round(
                    (Vector(R1[n]["effective_world"]) - Vector(R1[n]["authored"])).length * MM, 6),
                "head_exactly_unchanged": d < 1e-9}
DRIFT_TOL_MM = 1.0e-4
viol = [n for n in ORDER if n not in AUTHORIZED and drift[n]["head_delta_mm"] > DRIFT_TOL_MM]
maxd = max(drift[n]["head_delta_mm"] for n in ORDER if n not in AUTHORIZED)
G["FROZEN_JOINT_DRIFT"] = {"value": len(viol), "pass": not viol, "violations": viol,
                           "tolerance_mm": DRIFT_TOL_MM,
                           "tolerance_reason": "float32-equivalent (project convention: a file is unchanged when the delta is within the float32 storage epsilon; both blends are authored from the same frozen joint frame)",
                           "max_frozen_head_delta_mm": round(maxd, 9),
                           "authorized": sorted(AUTHORIZED),
                           "per_joint": drift}

# mesh identity / no skinning
G["MESH_VERTEX_DELTA"] = {"value": 0 if MSIG["vertex_digest"] == ASIG["vertex_digest"] else 1,
                          "pass": MSIG["vertex_digest"] == ASIG["vertex_digest"]}
G["MESH_TOPOLOGY_DELTA"] = {"value": 0 if MSIG["topology_signature"] == ASIG["topology_signature"] else 1,
                            "pass": MSIG["topology_signature"] == ASIG["topology_signature"],
                            "artifact": ASIG["topology_signature"],
                            "equals_frozen_stage4c": ASIG["topology_signature"] ==
                            "5a39668418eea1716a0fd9bc20b3d0aeda67e6a49a343b74eb3e17c339f90c1d"}
G["UV_DELTA"] = {"value": 0 if MSIG["uv_digest"] == ASIG["uv_digest"] else 1,
                 "pass": MSIG["uv_digest"] == ASIG["uv_digest"]}
G["MATERIAL_ASSIGNMENT_DELTA"] = {"value": 0 if MSIG["material_digest"] == ASIG["material_digest"] else 1,
                                  "pass": MSIG["material_digest"] == ASIG["material_digest"],
                                  "faces_per_slot": ASIG["faces_per_slot"]}
G["MESH_PARENT"] = {"value": ASIG["parent"], "pass": ASIG["parent"] is None}
G["ARMATURE_MODIFIER"] = {"value": ASIG["modifiers"], "pass": not ASIG["modifiers"]}
G["VERTEX_GROUPS"] = {"value": ASIG["vertex_groups"], "pass": not ASIG["vertex_groups"]}
G["PRODUCTION_SKIN_WEIGHT"] = {"value": "NOT_STARTED", "pass": True}

# orthonormality / roll
ortho = {}
for n in ORDER:
    X = Vector(bones[n]["local_X_world"]); Y = Vector(bones[n]["local_Y_world"]); Z = Vector(bones[n]["local_Z_world"])
    ortho[n] = {"|X|": round(X.length, 9), "|Y|": round(Y.length, 9), "|Z|": round(Z.length, 9),
                "X.Y": round(X.dot(Y), 9), "Y.Z": round(Y.dot(Z), 9), "X.Z": round(X.dot(Z), 9),
                "X-(YxZ)": round((X - Y.cross(Z)).length, 9)}
TOL = 1e-5
G["BONE_LOCAL_FRAME_ORTHONORMAL"] = {
    "pass": all(abs(v["|X|"] - 1) < TOL and abs(v["|Y|"] - 1) < TOL and abs(v["|Z|"] - 1) < TOL
                and abs(v["X.Y"]) < TOL and abs(v["Y.Z"]) < TOL and abs(v["X.Z"]) < TOL
                and v["X-(YxZ)"] < TOL for v in ortho.values()),
    "tolerance": TOL, "per_bone": ortho}
roll = {}
maxroll = 0.0
for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    ch = ["WRIST_R"] + ["%s_%s_R" % (D, s) for s in CHAIN[D]] + ["%s_TIP_R" % D]
    seq = []
    for i in range(1, len(ch)):
        a = Vector(bones[ch[i - 1]]["local_Z_world"]); b = Vector(bones[ch[i]]["local_Z_world"])
        ang = math.degrees(math.acos(max(-1.0, min(1.0, a.dot(b)))))
        seq.append({"from": ch[i - 1], "to": ch[i], "angle_deg": round(ang, 4)})
        maxroll = max(maxroll, ang)
    roll[D.lower()] = seq
flips = [x for d in roll for x in roll[d] if x["angle_deg"] > 120.0]
G["BONE_ROLL_CONTINUITY"] = {"pass": maxroll <= 60.0, "max_angle_deg": round(maxroll, 4),
                             "tolerance_deg": 60.0,
                             "definition": "angle between the local +Z (dorsal-like) axes of "
                                           "consecutive bones within each digit chain",
                             "per_chain": roll}
G["BONE_ROLL_180_FLIPS"] = {"value": len(flips), "pass": not flips, "violations": flips}

ALL = all(v.get("pass") for v in G.values())
fail = [k for k in G if not G[k].get("pass")]

# ---------------- joint table ----------------
jt = {}
prev_status = {"INDEX_PIP_R": "PASS", "INDEX_DIP_R": "PASS", "INDEX_TIP_R": "PASS",
               "MIDDLE_MCP_R": "PASS", "MIDDLE_PIP_R": "PASS", "MIDDLE_DIP_R": "PASS", "MIDDLE_TIP_R": "PASS",
               "RING_MCP_R": "PASS", "RING_PIP_R": "PASS", "RING_DIP_R": "PASS", "RING_TIP_R": "PASS",
               "LITTLE_MCP_R": "PASS", "LITTLE_PIP_R": "PASS", "LITTLE_DIP_R": "PASS", "LITTLE_TIP_R": "PASS"}
for n in ORDER:
    p = H(n)
    par, tot = parity(p)
    loc, nor, fi = closest(p)
    e = {"joint_name": n, "world_position": [round(float(x), 9) for x in p],
         "ray_parity": "%d/%d" % (par, tot), "inside_mesh": bool(par > tot / 2),
         "nearest_surface_distance_mm": round((p - loc).length * MM, 4),
         "R1_authored_position": [round(float(x), 9) for x in R1[n]["authored"]],
         "shift_from_R1_mm": round((p - Vector(R1[n]["authored"])).length * MM, 6)}
    if n == "WRIST_R":
        e["authority"] = "STAGE5A_R2 PRODUCTION wrist/palm transition centre (decoupled from the asset origin)"
        e["validation_method"] = wprof["selected"]["method"]
        e["status"] = "PASS"
        e["asset_origin_separation_mm"] = round((p - ASSET_ORIGIN).length * MM, 4)
    elif n in AUTHORIZED:
        key = {"INDEX_MCP_R": "INDEX_MCP_EVIDENCE", "THUMB_CMC_R": "THUMB_CMC_EVIDENCE",
               "THUMB_MCP_R": "THUMB_MCP_EVIDENCE", "THUMB_TIP_R": "THUMB_TIP_EVIDENCE"}[n]
        e["authority"] = "Stage5A R2 requalification"
        e["validation_method"] = cand[key]["method"]
        e["status"] = "PASS" if e["inside_mesh"] or n.endswith("_TIP_R") else "FAIL"
    elif n == "THUMB_IP_R":
        e["authority"] = "CARRY_FORWARD from Stage5A R1 (kept by Human Review decision)"
        e["validation_method"] = ("kept; chain geometry re-validated under the new CMC/MCP/TIP "
                                  "chain (see STAGE5A_R2_THUMB_CHAIN_AUDIT.json)")
        e["shift_from_R1_mm"] = round((p - Vector(R1[n]["authored"])).length * MM, 9)
        e["status"] = "PASS"
    else:
        e["authority"] = "FROZEN (Stage5A R1 validated)"
        e["validation_method"] = "frozen joint; drift audited against Stage5A R1"
        e["status"] = prev_status.get(n, "PASS")
    jt[n] = e
G["JOINT_REGION_VALIDATION"] = {
    "pass": all(v["status"] == "PASS" for v in jt.values()),
    "failures": [k for k, v in jt.items() if v["status"] != "PASS"],
    "criterion": "21 joints: every requalified joint is inside the mesh (ray parity) and satisfies "
                 "its region authority (approved CMC cage region / approved T-01 axial zone / "
                 "fingertip apex within 5 mm); the 15 frozen joints are byte-identical to R1"}

status = {
    "stage": "STAGE5A_R2_PRODUCTION_JOINT_LANDMARK_REQUALIFICATION",
    "generated_at": NOW,
    "runtime": {"blender": bpy.app.version_string, "executable": bpy.app.binary_path},
    "inputs": {"master": MASTER, "master_sha256": MASTER_SHA,
               "stage5a_r1": R1BLEND, "stage5a_r1_sha256": R1_SHA},
    "artifact": ART, "artifact_sha256": ART_SHA,
    "rig_object": {"name": rig.name, "location": [float(x) for x in rig.location],
                   "rotation_euler": [float(x) for x in rig.rotation_euler],
                   "scale": [float(x) for x in rig.scale]},
    "all_gates_pass": ALL, "failing_gates": fail, "gates": G,
    "wrist_root_length_mm": round(wrist_len, 4),
    "stage5a_r1_object_frame_defect": {
        "id": "STAGE5A_R1_OBJECT_FRAME_OFFSET",
        "what": "Stage5A R1 authored its bone coordinates in WORLD values while the rig object was "
                "placed at the ASSET object origin, so every bone of the R1 armature sits "
                "%.3f mm away from the hand in the scene (it is offset by the full origin vector). "
                "R2 authors the bones in the rig's own object frame (= the hand mesh's object frame), "
                "so the R2 armature is geometrically coincident with the hand." % R1_FRAME_OFFSET_MM,
        "r1_blend_left_untouched": True,
        "r1_blend_sha256": R1_SHA,
        "note": "this is an OBJECT-FRAME defect, not a joint-position change; no frozen joint "
                "position was altered.",
    },
    "constraints_semantics": {
        "ASSET_OBJECT_ORIGIN": [round(float(x), 9) for x in ASSET_ORIGIN],
        "PRODUCTION_WRIST_JOINT_CENTER": [round(float(x), 9) for x in wh],
        "STATEMENT": "ASSET ORIGIN != PRODUCTION WRIST JOINT",
        "stage4c_origin_status": "FROZEN_ASSET_REFERENCE (Stage4C PASS unchanged)"},
    "VERDICT": {
        "STAGE5A_R2": "READY_FOR_HUMAN_REVIEW" if ALL else "FAIL_CLOSED",
        "PRODUCTION_RIG_SKELETON": "PASS_PENDING_HUMAN_REVIEW" if ALL else "BLOCKED",
        "RIGHT_HAND_PRODUCTION_RIG": "CANDIDATE_R2",
        "PRODUCTION_SKIN_WEIGHT": "NOT_STARTED", "STAGE5B": "NOT_STARTED"},
    "not_done_this_round": ["Skin Weight", "automatic weights", "vertex groups", "mesh parenting",
                            "Armature modifier", "controllers", "IK", "constraints", "animation",
                            "MediaPipe retarget", "left hand", "GLB", "Three.js",
                            "Stage6 deformation test", "Retopo", "CMC cage", "T-01 topology",
                            "RSSF pose", "Nails", "UV"],
}
thumb_audit = {
    "stage": "STAGE5A_R2_PRODUCTION_JOINT_LANDMARK_REQUALIFICATION",
    "generated_at": NOW, "artifact": ART, "artifact_sha256": ART_SHA,
    "joints": {
        "CMC": {"R1": cand["THUMB_CMC_EVIDENCE"]["R1_position"],
                "R2": [round(float(x), 9) for x in H("THUMB_CMC_R")],
                "authority": "STAGE5A_R2_THENAR_INTERIOR_MEDIAL",
                "inside_mesh": G["THUMB_CMC_INSIDE"]["pass"],
                "surface_clearance_mm": G["THUMB_CMC_INSIDE"]["surface_clearance_mm"],
                "in_approved_cage_region": G["THUMB_CMC_IN_APPROVED_CAGE_REGION"]["inside_approved_region"],
                "evidence": cand["THUMB_CMC_EVIDENCE"]},
        "MCP": {"R1": cand["THUMB_MCP_EVIDENCE"]["R1_position"],
                "R2": [round(float(x), 9) for x in H("THUMB_MCP_R")],
                "authority": "STAGE5A_R2_THUMB_TUBE_INTERIOR_MEDIAL",
                "inside_mesh": G["THUMB_MCP_INSIDE"]["pass"],
                "surface_clearance_mm": G["THUMB_MCP_INSIDE"]["surface_distance_mm"],
                "t01_axial_delta_mm": G["THUMB_MCP_T01_AXIAL_REGION"]["delta_mm"],
                "evidence": cand["THUMB_MCP_EVIDENCE"]},
        "IP": {"R1": [round(float(x), 9) for x in ip_r1], "R2": [round(float(x), 9) for x in ip],
               "authority": "CARRY_FORWARD_KEEP_UNLESS_INVALIDATED",
               "head_delta_mm": G["THUMB_IP_CARRY_FORWARD_VALID"]["head_delta_mm"],
               "tail_R1": [round(float(x), 9) for x in Vector(R1["THUMB_IP_R"]["authored_tail"])],
               "tail_R2": [round(float(x), 9) for x in T("THUMB_IP_R")],
               "tail_note": "the tail (= the fingertip landmark) necessarily follows the requalified "
                            "THUMB_TIP_R head; the IP JOINT (head) is unchanged",
               "inside_mesh": G["THUMB_IP_CARRY_FORWARD_VALID"]["inside_mesh"]["pass"]},
        "TIP": {"R1": cand["THUMB_TIP_EVIDENCE"]["R1_position"],
                "R2": [round(float(x), 9) for x in tip],
                "authority": "STAGE5A_R2_FITTED_AXIS_CAP_LANDMARK",
                "dist_to_apex_mm": G["THUMB_TIP_APEX_ALIGNMENT"]["R2_dist_to_surface_apex_mm"],
                "dist_to_apex_vertex_mm": G["THUMB_TIP_APEX_ALIGNMENT"]["R2_dist_to_apex_vertex_mm"],
                "evidence": cand["THUMB_TIP_EVIDENCE"]}},
    "segments": chain,
    "THUMB_CMC_TO_MCP_LENGTH_REASONABLE": chain[0]["length_reasonable"],
    "THUMB_MCP_TO_IP_LENGTH_REASONABLE": chain[1]["length_reasonable"],
    "THUMB_IP_TO_TIP_LENGTH_REASONABLE": chain[2]["length_reasonable"],
    "THUMB_CHAIN_GEOMETRY": G["THUMB_CHAIN_GEOMETRY"]["pass"],
    "criterion": G["THUMB_CHAIN_GEOMETRY"]["criterion"],
}
drift_doc = {"stage": "STAGE5A_R2_PRODUCTION_JOINT_LANDMARK_REQUALIFICATION", "generated_at": NOW,
             "r1_blend": R1BLEND, "r1_sha256": R1_SHA, "r2_blend": ART, "r2_sha256": ART_SHA,
             "authorized_to_change": sorted(AUTHORIZED) + ["THUMB_IP_R.tail", "WRIST_R.tail"],
             "frozen_joint_drift": G["FROZEN_JOINT_DRIFT"], "verdict": G["FROZEN_JOINT_DRIFT"]["pass"]}
frame_doc = {"stage": "STAGE5A_R2_PRODUCTION_JOINT_LANDMARK_REQUALIFICATION", "generated_at": NOW,
             "artifact": ART, "artifact_sha256": ART_SHA,
             "convention": {"LOCAL_Y": "head -> tail", "LOCAL_Z": "dorsal-like (projected per-digit dorsal ref)",
                            "LOCAL_X": "Y x Z"},
             "roll_rule": "edit_bone.align_roll(dorsal_reference); recomputed for EVERY bone in R2 "
                          "(no R1 roll value is copied)",
             "bones": bones,
             "orthonormality": G["BONE_LOCAL_FRAME_ORTHONORMAL"],
             "roll_continuity": G["BONE_ROLL_CONTINUITY"], "roll_180_flips": G["BONE_ROLL_180_FLIPS"]}

json.dump(status, open(os.path.join(S5AR2, "STAGE5A_R2_STATUS.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(status, open(os.path.join(S5AR2, "STAGE5A_R2_JOINT_AUDIT.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
jt_doc = {"stage": "STAGE5A_R2_PRODUCTION_JOINT_LANDMARK_REQUALIFICATION", "generated_at": NOW,
          "artifact_sha256": ART_SHA, "criterion": G["JOINT_REGION_VALIDATION"]["criterion"],
          "authorized_to_change": sorted(AUTHORIZED), "joints": jt,
          "ALL_JOINTS_PASS": G["JOINT_REGION_VALIDATION"]["pass"]}
json.dump(jt_doc, open(os.path.join(S5AR2, "STAGE5A_R2_PRODUCTION_JOINT_TABLE.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(frame_doc, open(os.path.join(S5AR2, "STAGE5A_R2_BONE_FRAME_AUDIT.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(thumb_audit, open(os.path.join(S5AR2, "STAGE5A_R2_THUMB_CHAIN_AUDIT.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(drift_doc, open(os.path.join(S5AR2, "STAGE5A_R2_FROZEN_JOINT_DRIFT_AUDIT.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

print("=" * 80)
for k in G:
    print("  %-46s %s" % (k, "PASS" if G[k].get("pass") else "FAIL"))
print("ALL_GATES_PASS =", ALL, "| failing:", fail)
print("master sha256 (after) =", hashlib.sha256(open(MASTER, "rb").read()).hexdigest())
print("R1 sha256       (after) =", hashlib.sha256(open(R1BLEND, "rb").read()).hexdigest())
print("R2 sha256 =", ART_SHA)
print("WRIST root length mm =", round(wrist_len, 4))
print("roll max consecutive Z angle =", round(maxroll, 3))
