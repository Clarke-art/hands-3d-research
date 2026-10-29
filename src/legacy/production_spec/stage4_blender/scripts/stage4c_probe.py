# STAGE4C_RSSF_ASSET_FINALIZATION_R1 -- READ-ONLY probe.
#
# Dumps everything the finalisation decisions depend on, and writes nothing to the blend:
#   * scene inventory (objects / parents / modifiers / constraints / animation data / vgroups)
#   * the Stage-4B TEMP armature (custom properties + every bone head/tail in world space)
#   * mesh statistics, material slots, UV layers
#   * a full UV audit: layer count, degenerate/missing faces, winding consistency (flipped),
#     stretch (UV area share vs 3D area share), island count, overlap rasterisation,
#     texel density spread
#   * nail-candidate faces per digit (dorsal outer shell of the distal phalanx)
#
# usage: blender -b <R2.blend> --python stage4c_probe.py -- <out.json>
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector

OUT = sys.argv[sys.argv.index("--") + 1]
TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
me = ob.data
MW = ob.matrix_world

# ---------------------------------------------------------------- 1. scene inventory
inv = {"objects": [], "mesh_object": TARGET}
for o in bpy.data.objects:
    inv["objects"].append({
        "name": o.name, "type": o.type,
        "parent": o.parent.name if o.parent else None,
        "parent_type": o.parent_type,
        "modifiers": [{"name": m.name, "type": m.type,
                       "object": getattr(m, "object", None).name if getattr(m, "object", None) else None}
                      for m in o.modifiers],
        "constraints": [{"name": c.name, "type": c.type} for c in o.constraints],
        "has_animation_data": o.animation_data is not None,
        "animation_data_actions": ([a.name for a in [o.animation_data.action] if a]
                                   if o.animation_data else []),
        "vertex_groups": [g.name for g in o.vertex_groups],
        "shape_keys": bool(o.data.shape_keys) if o.type == "MESH" else None,
        "custom_props": {k: str(o[k]) for k in o.keys() if k != "_RNA_UI"},
    })

# ---------------------------------------------------------------- 2. armature
arms = {}
for o in bpy.data.objects:
    if o.type != "ARMATURE":
        continue
    aw = o.matrix_world
    arms[o.name] = {
        "custom_props": {k: str(o[k]) for k in o.keys() if k != "_RNA_UI"},
        "bones": {b.name: {"head": [round(float(x), 6) for x in (aw @ b.head_local)],
                           "tail": [round(float(x), 6) for x in (aw @ b.tail_local)],
                           "length_mm": round((aw @ b.tail_local - aw @ b.head_local).length * 1000, 3),
                           "parent": b.parent.name if b.parent else None}
                  for b in o.data.bones},
        "pose_bones_with_nonidentity_transform": [
            b.name for b in o.pose.bones
            if (b.matrix_basis - b.matrix_basis.Identity(4)).median_scale > 1e-9
            or any(abs(v) > 1e-9 for v in b.location)
            or any(abs(v) > 1e-9 for v in b.rotation_euler)],
    }
inv["armatures"] = arms

# ---------------------------------------------------------------- 3. mesh + materials
bm = bmesh.new(); bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
NV, NE, NF = len(bm.verts), len(bm.edges), len(bm.faces)
tri_count = sum(len(f.verts) - 2 for f in bm.faces)
faces = [[v.index for v in f.verts] for f in bm.faces]
W = [(MW @ v.co).copy() for v in bm.verts]
face_mat = [f.material_index for f in bm.faces]
face_norm = [(MW.to_3x3() @ f.normal).normalized() for f in bm.faces]

mesh = {
    "verts": NV, "edges": NE, "faces": NF, "tris_if_triangulated": tri_count,
    "quad_faces": sum(1 for f in bm.faces if len(f.verts) == 4),
    "tri_faces": sum(1 for f in bm.faces if len(f.verts) == 3),
    "ngon_faces": sum(1 for f in bm.faces if len(f.verts) > 4),
    "materials": [{"index": i, "name": (m.name if m else None),
                   "faces_assigned": sum(1 for x in face_mat if x == i),
                   "diffuse_color": ([round(float(c), 4) for c in m.diffuse_color] if m else None),
                   "use_nodes": (bool(m.use_nodes) if m else None)}
                  for i, m in enumerate(list(me.materials) + [None] * 0)],
    "material_slots": len(me.materials),
    "uv_layers": [uv.name for uv in me.uv_layers],
    "active_uv": me.uv_layers.active.name if me.uv_layers.active else None,
    "object_origin_world": [round(float(x), 6) for x in MW.translation],
    "bbox_world_min": [round(min(p[i] for p in W), 6) for i in range(3)],
    "bbox_world_max": [round(max(p[i] for p in W), 6) for i in range(3)],
}
# material face counts (me.materials covers slots)
mesh["material_slots_detail"] = [
    {"index": i, "name": m.name if m else None,
     "faces_assigned": sum(1 for x in face_mat if x == i)}
    for i, m in enumerate(me.materials)]
inv["mesh"] = mesh

# ---------------------------------------------------------------- 4. UV audit
def tri_area3d(f):
    a = W[f[0]]
    tot = 0.0
    for k in range(1, len(f) - 1):
        tot += (W[f[k]] - a).cross(W[f[k + 1]] - a).length * 0.5
    return tot


EDGE_FACES = {}
for fi, f in enumerate(faces):
    for i in range(len(f)):
        k = (f[i], f[(i + 1) % len(f)])
        EDGE_FACES.setdefault(k if k[0] < k[1] else (k[1], k[0]), []).append(fi)


def uv_audit(layer, res=4096):
    U = [Vector(l.uv) for l in layer.data]           # index by loop index
    fdata = []
    for fi, f in enumerate(faces):
        li = [bm.faces[fi].loops[i].index for i in range(len(f))]
        uv = [U[i] for i in li]
        # signed UV area (shoelace over the polygon loops, in loop order)
        s = 0.0
        for i in range(len(uv)):
            x1, y1 = uv[i]; x2, y2 = uv[(i + 1) % len(uv)]
            s += x1 * y2 - x2 * y1
        s *= 0.5
        a3 = tri_area3d(f)
        fdata.append({"fi": fi, "uv": uv, "loops": li, "signed": s, "abs_uv": abs(s),
                      "a3": a3, "verts": f})
    nz = [d for d in fdata if d["abs_uv"] < 1e-10]
    neg = [d for d in fdata if d["signed"] < -1e-12]
    pos = [d for d in fdata if d["signed"] > 1e-12]
    tot_uv = sum(d["abs_uv"] for d in fdata)
    tot_3d = sum(d["a3"] for d in fdata)
    # stretch: share of UV area / share of 3D area
    stretch = []
    for d in fdata:
        if d["a3"] <= 0 or tot_uv <= 0:
            continue
        stretch.append((d["abs_uv"] / tot_uv) / (d["a3"] / tot_3d))
    stretch.sort()
    # texel density (texels per cm) for the given resolution
    td = sorted([math.sqrt(d["abs_uv"] * res * res) / math.sqrt(d["a3"] * 1e4)
                 for d in fdata if d["a3"] > 0 and d["abs_uv"] > 0])
    # islands: union-find on faces sharing an edge with matching UVs at both ends
    par = list(range(len(fdata)))
    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    def uni(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            par[ra] = rb
    lp_uv = {}
    for d in fdata:
        for i, li in enumerate(d["loops"]):
            lp_uv[li] = d["uv"][i]
    for (a, b), fs in EDGE_FACES.items():
        if len(fs) != 2:
            continue
        f1, f2 = fs
        d1, d2 = fdata[f1], fdata[f2]
        ok = True
        for v in (a, b):
            u1 = None; u2 = None
            for i, vi in enumerate(d1["verts"]):
                if vi == v:
                    u1 = d1["uv"][i]
            for i, vi in enumerate(d2["verts"]):
                if vi == v:
                    u2 = d2["uv"][i]
            if u1 is None or u2 is None or (u1 - u2).length > 1e-6:
                ok = False; break
        if ok:
            uni(f1, f2)
    islands = len({find(i) for i in range(len(fdata))})
    # overlap: rasterise UV triangles, count cells covered by faces from different islands
    G = 512
    cover = np.zeros((G, G), dtype=np.int32)
    owner = np.full((G, G), -1, dtype=np.int32)
    multi = 0
    for d in fdata:
        uv = d["uv"]
        if d["abs_uv"] < 1e-12:
            continue
        # rasterise the polygon fan by barycentric inside-tests on cell centres
        for k in range(1, len(uv) - 1):
            A, B, C = uv[0], uv[k], uv[k + 1]
            x0 = max(0, int(min(A.x, B.x, C.x) * G) - 1)
            x1 = min(G - 1, int(max(A.x, B.x, C.x) * G) + 1)
            y0 = max(0, int(min(A.y, B.y, C.y) * G) - 1)
            y1 = min(G - 1, int(max(A.y, B.y, C.y) * G) + 1)
            if x1 < x0 or y1 < y0:
                continue
            for yy in range(y0, y1 + 1):
                py = (yy + 0.5) / G
                for xx in range(x0, x1 + 1):
                    px_ = (xx + 0.5) / G
                    P = Vector((px_, py))
                    d1 = (B.x - A.x) * (P.y - A.y) - (B.y - A.y) * (P.x - A.x)
                    d2 = (C.x - B.x) * (P.y - B.y) - (C.y - B.y) * (P.x - B.x)
                    d3 = (A.x - C.x) * (P.y - C.y) - (A.y - C.y) * (P.x - C.x)
                    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
                    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
                    if has_neg and has_pos:
                        continue
                    if cover[yy, xx] == 0:
                        owner[yy, xx] = find(d["fi"])
                    elif owner[yy, xx] != find(d["fi"]):
                        multi += 1
                    cover[yy, xx] += 1
    covered = int((cover > 0).sum())
    return {
        "layer": layer.name,
        "faces": len(fdata),
        "missing_uv_faces": len([d for d in fdata if all(u.length < 1e-12 for u in d["uv"])]),
        "zero_area_uv_faces": len(nz),
        "negative_signed_uv_faces": len(neg),
        "positive_signed_uv_faces": len(pos),
        "uv_winding_consistent": (len(neg) == 0 or len(pos) == 0),
        "uv_flipped_faces": min(len(neg), len(pos)),
        "uv_area_total": round(tot_uv, 6),
        "area3d_total": round(tot_3d, 8),
        "stretch_rel_share": {"min": round(stretch[0], 4), "p05": round(stretch[int(0.05 * (len(stretch) - 1))], 4),
                              "median": round(stretch[len(stretch) // 2], 4),
                              "p95": round(stretch[int(0.95 * (len(stretch) - 1))], 4),
                              "max": round(stretch[-1], 4)},
        "texel_density_px_per_cm_at_%d" % res: {
            "min": round(td[0], 1), "p05": round(td[int(0.05 * (len(td) - 1))], 1),
            "median": round(td[len(td) // 2], 1),
            "p95": round(td[int(0.95 * (len(td) - 1))], 1), "max": round(td[-1], 1),
            "max_over_min": round(td[-1] / td[0], 2) if td[0] > 0 else None},
        "island_count": islands,
        "overlap_grid": G,
        "overlap_uv_area_fraction": round(multi / covered, 5) if covered else None,
        "uv_coverage_fraction_of_unit_square": round(covered / (G * G), 5),
    }


inv["uv_audit"] = [uv_audit(uv) for uv in me.uv_layers] if me.uv_layers else []

# ---------------------------------------------------------------- 5. nail candidates
FN = ["thumb", "index", "middle", "ring", "little"]
DORSAL = None
arm = None
for o in bpy.data.objects:
    if o.type == "ARMATURE":
        arm = o
if arm is not None:
    aw = arm.matrix_world
    B = {b.name: ((aw @ b.head_local).copy(), (aw @ b.tail_local).copy()) for b in arm.data.bones}
    # global dorsal from the palm frame
    mcp = sum((B["%s_MCP_R" % n.upper()][0] for n in ("index", "middle", "ring", "little")), Vector()) / 4
    wrist = B["WRIST_R"][0]
    tips = {n: B["%s_TIP_R" % n.upper()][0] for n in ("index", "middle", "ring", "little")}
    fw = (sum(tips.values(), Vector()) / 4 - wrist).normalized()
    radial = (tips["index"] - tips["little"]).normalized()
    radial = (radial - fw * radial.dot(fw)).normalized()
    DORSAL = fw.cross(radial).normalized()
    nail = {}
    for n in FN:
        U = n.upper()
        db = "THUMB_IP_R" if n == "thumb" else "%s_DIP_R" % U
        mb = "THUMB_CMC_R" if n == "thumb" else "%s_MCP_R" % U
        h, t = B[db]
        dirv = (t - h).normalized(); L = (t - h).length
        mu = (B[mb][1] - B[mb][0]).normalized()
        lat = DORSAL.cross(mu)
        lat = lat.normalized() if lat.length > 1e-9 else radial
        nn = lat.cross(dirv)
        nn = nn.normalized() if nn.length > 1e-9 else DORSAL.copy()
        if nn.dot(DORSAL) < 0:
            nn = -nn
        ax_lo, ax_hi = 0.12 * L, 0.88 * L
        sel = []
        for fi, f in enumerate(faces):
            c = sum((W[v] for v in f), Vector()) / len(f)
            a = (c - h).dot(dirv)
            if a < ax_lo or a > ax_hi:
                continue
            perp = (c - (h + dirv * a)).dot(nn)
            if perp <= 0:
                continue
            if face_norm[fi].dot(nn) < 0.30:
                continue
            sel.append((fi, round(a / L, 3), round(perp * 1000, 2)))
        nail[n] = {
            "distal_bone": db, "bone_len_mm": round(L * 1000, 2),
            "nail_normal": [round(float(x), 4) for x in nn],
            "nail_normal_dot_global_dorsal": round(float(nn.dot(DORSAL)), 4),
            "candidate_faces": len(sel),
            "candidate_axial_span": [min((s[1] for s in sel), default=None),
                                     max((s[1] for s in sel), default=None)],
            "candidate_max_perp_mm": max((s[2] for s in sel), default=None),
            "faces": [s[0] for s in sel],
        }
    inv["nail_candidates"] = nail
    inv["global_dorsal"] = [round(float(x), 4) for x in DORSAL]
    # thumb nail plane vs the four fingers
    ang = {}
    for a in ("index", "middle", "ring", "little"):
        na = Vector(nail["thumb"]["nail_normal"]); nb = Vector(nail[a]["nail_normal"])
        ang["thumb_vs_%s" % a] = round(math.degrees(math.acos(max(-1, min(1, na.dot(nb))))), 2)
    inv["nail_plane_angles_deg"] = ang

bm.free()
json.dump(inv, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", OUT)
print("objects:", [(o["name"], o["type"]) for o in inv["objects"]])
print("mesh:", mesh["verts"], mesh["edges"], mesh["faces"], "tris", mesh["tris_if_triangulated"],
      "| materials", mesh["material_slots"], "| uv", mesh["uv_layers"])
print("origin:", mesh["object_origin_world"])
for u in inv["uv_audit"]:
    print("UV:", json.dumps(u, ensure_ascii=False)[:600])
if "nail_candidates" in inv:
    for k, v in inv["nail_candidates"].items():
        print("nail %-7s bone=%-12s faces=%3d span=%s ndotD=%.3f"
              % (k, v["distal_bone"], v["candidate_faces"], v["candidate_axial_span"],
                 v["nail_normal_dot_global_dorsal"]))
    print("nail plane angles:", inv["nail_plane_angles_deg"])
