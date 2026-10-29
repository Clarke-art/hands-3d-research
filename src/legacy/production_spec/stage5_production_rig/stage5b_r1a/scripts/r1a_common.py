# =====================================================================================
# STAGE5B_R1A -- shared helpers (READ-ONLY reference geometry / weights / regions)
# =====================================================================================
# This module never writes.  It opens blends, extracts reference geometry and weights,
# and builds the R1A semantic regions deterministically.
# =====================================================================================
import os
import json
import math
import heapq
import bpy
from mathutils import Vector

MM = 1000.0

CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"],
         "LITTLE": ["MCP", "PIP", "DIP"]}
DD = {"THUMB": "thumb", "INDEX": "index", "MIDDLE": "middle", "RING": "ring",
      "LITTLE": "little"}
DIGITS = ["THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"]

DEFORM = ["WRIST_R"] + ["%s_%s_R" % (d, s) for d in DIGITS for s in CHAIN[d]]
assert len(DEFORM) == 16, len(DEFORM)

# groups R1A is allowed to touch (only inside the authorised thumb region)
FREE_GROUPS = ["WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R", "INDEX_MCP_R"]
# four-finger (already approved) groups: MUST NOT change anywhere
FROZEN_GROUPS = [g for g in DEFORM if g not in FREE_GROUPS]
assert len(FROZEN_GROUPS) == 11, len(FROZEN_GROUPS)

DIGIT_OF_BONE = {"WRIST_R": "wrist"}
for _d in DIGITS:
    for _s in CHAIN[_d]:
        DIGIT_OF_BONE["%s_%s_R" % (_d, _s)] = _d

WEB_OK = {"WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "INDEX_MCP_R"}
WEB_FORBIDDEN = {"THUMB_IP_R", "INDEX_PIP_R", "INDEX_DIP_R",
                 "MIDDLE_MCP_R", "MIDDLE_PIP_R", "MIDDLE_DIP_R",
                 "RING_MCP_R", "RING_PIP_R", "RING_DIP_R",
                 "LITTLE_MCP_R", "LITTLE_PIP_R", "LITTLE_DIP_R"}


# ------------------------------------------------------------------ small geometry
def S(z):
    """smoothstep, clamped"""
    z = max(0.0, min(1.0, z))
    return z * z * (3.0 - 2.0 * z)


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
    return (p - (a + ab * t)).length


def d_poly(p, poly):
    b = 1e9
    for i in range(len(poly) - 1):
        b = min(b, seg_dist(p, poly[i], poly[i + 1]))
    return b


def arc_of(pts, v):
    """(arclength_mm, perpendicular_distance) of v projected on the polyline pts"""
    best = (1e9, 0.0)
    acc = 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (v - a).dot(ab) / max(ab.length_squared, 1e-18)))
        d = (v - (a + ab * t)).length
        if d < best[0]:
            best = (d, (acc + t * ab.length) * MM)
        acc += ab.length
    return best[1], best[0]


def chp(jf, D):
    p = [Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])]
    for s in CHAIN[D]:
        p.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
    return p


def chain_arc_table(jf, D):
    pts = chp(jf, D)
    acc = 0.0
    a = [0.0]
    for k in range(len(pts) - 1):
        acc += (pts[k + 1] - pts[k]).length
        a.append(acc * MM)
    return a


def build_geo(mesh_verts, edges):
    """Dijkstra single-source adjacency over mesh edges (weights = edge length, in metres)"""
    eadj = {}
    for a, b in edges:
        w = (mesh_verts[a] - mesh_verts[b]).length
        eadj.setdefault(a, []).append((b, w))
        eadj.setdefault(b, []).append((a, w))

    def dij(src):
        d = {src: 0.0}
        pq = [(0.0, src)]
        while pq:
            du, u = heapq.heappop(pq)
            if du > d.get(u, 1e18) + 1e-15:
                continue
            for v, w in eadj.get(u, ()):
                if du + w < d.get(v, 1e18) - 1e-16:
                    d[v] = du + w
                    heapq.heappush(pq, (du + w, v))
        return d

    return eadj, dij


def rings(eadj, seed, n):
    """BFS n rings from a seed set (returns set of vertices)"""
    seen = set(seed)
    front = set(seed)
    for _ in range(n):
        nxt = set()
        for u in front:
            for v, _w in eadj.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    nxt.add(v)
        front = nxt
    return seen - set(seed)


# ------------------------------------------------------------------ reference load
def load_reference(top):
    """Open the frozen Stage5A R2A master and extract the R1A reference geometry."""
    s4 = os.path.join(os.path.dirname(top), "stage4_blender")
    jf = json.load(open(os.path.join(s4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"),
                        encoding="utf-8"))["bones"]
    oa = json.load(open(os.path.join(s4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"),
                        encoding="utf-8"))
    t01 = json.load(open(os.path.join(s4, "stage4a_t01", "T01_FINAL_AUDIT.json"),
                         encoding="utf-8"))
    r2a = os.path.join(top, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
    cap = json.load(open(os.path.join(top, "stage5a_r2a", "THUMB_DISTAL_CAP_AUDIT.json"),
                         encoding="utf-8"))

    bpy.ops.wm.open_mainfile(filepath=r2a)
    ob = bpy.data.objects["Hand  - Realistic"]
    rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
    me = ob.data
    MW = ob.matrix_world.copy()
    NV = len(me.vertices)
    V0 = [(MW @ v.co).copy() for v in me.vertices]
    L0 = [v.co.copy() for v in me.vertices]
    TOPO0 = [tuple(p.vertices) for p in me.polygons]
    MAT0 = [p.material_index for p in me.polygons]
    UV0 = ([tuple(round(u, 9) for u in d.uv) for d in me.uv_layers.active.data]
           if me.uv_layers.active else [])
    EDGES = [(e.vertices[0], e.vertices[1]) for e in me.edges]
    FC = [sum((V0[v] for v in p.vertices), Vector()) / len(p.vertices)
          for p in me.polygons]
    ntri = sum(len(p.vertices) - 2 for p in me.polygons)
    elen = sorted((V0[a] - V0[b]).length * MM for a, b in EDGES)
    med_edge = elen[len(elen) // 2]

    AC = {D: chp(jf, D) for D in DIGITS}
    AO = Vector(oa["WRIST_ORIGIN"])
    AC["wrist"] = [AO, Vector(jf["WRIST_R"]["tail"])]

    OWN_V = [min(AC, key=lambda D: d_poly(V0[i], AC[D])) for i in range(NV)]
    FO = {p.index: min(AC, key=lambda D: d_poly(FC[p.index], AC[D]))
          for p in me.polygons}

    # lateral distance to each chain + 2nd nearest chain
    dchain = [dict((D, d_poly(V0[i], AC[D]) * MM) for D in list(AC)) for i in range(NV)]
    order2 = [sorted(dchain[i].items(), key=lambda kv: kv[1])[:2] for i in range(NV)]

    # nail faces / vertices
    NAIL_FACES = sorted(p.index for p in me.polygons if p.material_index == 1)
    NAIL_BY_DIGIT = {}
    for p in me.polygons:
        if p.material_index == 1 and FO[p.index] in DIGITS:
            NAIL_BY_DIGIT.setdefault(FO[p.index], set()).update(p.vertices)
    NAIL_V = set(v for p in me.polygons if p.material_index == 1 for v in p.vertices)

    # bone frames (world)
    BH = {b.name: rig.matrix_world @ b.head_local for b in rig.data.bones}
    BT = {b.name: rig.matrix_world @ b.tail_local for b in rig.data.bones}
    BONES = [b.name for b in rig.data.bones]

    eadj, dij = build_geo(V0, EDGES)
    NW0 = MW.copy()
    TOPSIG = (NV, len(me.edges), len(me.polygons), ntri)

    return {"blend": r2a, "jf": jf, "oa": oa, "t01": t01, "cap": cap,
            "NV": NV, "V0": V0, "L0": L0, "MW0": NW0, "TOPO0": TOPO0, "MAT0": MAT0,
            "UV0": UV0, "EDGES": EDGES, "FC": FC, "AC": AC, "AO": AO,
            "OWN_V": OWN_V, "FO": FO, "dchain": dchain, "order2": order2,
            "NAIL_FACES": NAIL_FACES, "NAIL_BY_DIGIT": NAIL_BY_DIGIT,
            "NAIL_V": NAIL_V, "BH": BH, "BT": BT, "BONES": BONES,
            "eadj": eadj, "dij": dij, "med_edge": med_edge, "TOPSIG": TOPSIG,
            "ntri": ntri}


def load_weights(blend):
    """Open a bound blend and read the 16 deform vertex groups + mesh state."""
    bpy.ops.wm.open_mainfile(filepath=blend)
    ob = bpy.data.objects["Hand  - Realistic"]
    rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
    me = ob.data
    MW = ob.matrix_world.copy()
    NV = len(me.vertices)
    V = [(MW @ v.co).copy() for v in me.vertices]
    groups = sorted(g.name for g in ob.vertex_groups)
    W = [dict() for _ in range(NV)]
    for g in ob.vertex_groups:
        for i in range(NV):
            try:
                w = g.weight(i)
            except RuntimeError:
                continue
            if w > 0.0:
                W[i][g.name] = w
    TOPO = [tuple(p.vertices) for p in me.polygons]
    MAT = [p.material_index for p in me.polygons]
    UV = ([tuple(round(u, 9) for u in d.uv) for d in me.uv_layers.active.data]
          if me.uv_layers.active else [])
    ntri = sum(len(p.vertices) - 2 for p in me.polygons)
    parent = ob.parent.name if ob.parent else None
    mods = [(m.name, m.type, (m.object.name if getattr(m, "object", None) else None))
            for m in ob.modifiers]
    return {"blend": blend, "ob": ob, "rig": rig, "me": me, "MW": MW, "NV": NV, "V": V,
            "groups": groups, "W": W, "TOPO": TOPO, "MAT": MAT, "UV": UV,
            "ntri": ntri, "parent": parent, "mods": mods,
            "topsisig": (NV, len(me.edges), len(me.polygons), ntri)}


def zero_pose_delta(ob, MW, V0):
    """evaluated (rest-pose) mesh vs frozen geometry"""
    dg = bpy.context.evaluated_depsgraph_get()
    obe = ob.evaluated_get(dg)
    VE = [(MW @ v.co).copy() for v in obe.data.vertices]
    dz = [(VE[i] - V0[i]).length * MM for i in range(len(V0))]
    return dz, VE


# ------------------------------------------------------------------ thumb local frame
def thumb_frame(ref):
    """Thumb LOCAL FRAME for R1A.

    longitudinal coordinate = ARC LENGTH along the approved thumb joint polyline
      (CMC head -> CMC/MCP joint -> MCP/IP joint -> TIP), i.e. the projection of the
      real mesh surface onto the approved KINEMATIC axis of the digit.  s grows from
      the CMC head (0) towards the tip.

    A geodesic-from-distal-most-vertex coordinate is ALSO measured, purely as a
    diagnostic: on this mesh it is NOT usable as a digit coordinate because the
    thumb nail plate / dorsal sheet is topologically far (150-180 mm) from the
    distal-most vertex although it is only 8-30 mm away in space (surface crease).
    """
    jf = ref["jf"]
    NV = ref["NV"]
    V0 = ref["V0"]
    dstar = int(ref["cap"]["thumb"]["distal_most_vertex"])
    GEO = ref["dij"](dstar)
    pts = chp(jf, "THUMB")
    XIJ = chain_arc_table(jf, "THUMB")
    ARC = [arc_of(pts, V0[i])[0] for i in range(NV)]        # mm
    sg = {i: GEO[i] * MM for i in range(NV)}                # mm (diagnostic only)

    def nearest_vert(P):
        return min(range(NV), key=lambda i: (V0[i] - P).length)

    geo_levels = {}
    for name, key in (("IP", "THUMB_IP_R"), ("MCP", "THUMB_MCP_R"),
                      ("CMC", "THUMB_CMC_R"), ("WRIST", "WRIST_R"),
                      ("TIP", "THUMB_TIP_R")):
        geo_levels[name] = sg[nearest_vert(Vector(jf[key]["head"]))]

    return {"dstar": dstar, "arc_thumb_mm": ARC, "XIJ_thumb_arc_mm": XIJ,
            "s_MCP_joint_mm": XIJ[1], "s_IP_joint_mm": XIJ[2], "s_TIP_mm": XIJ[3],
            "geodesic_from_tip_mm": sg,
            "geodesic_joint_levels_mm": geo_levels,
            "geodesic_joint_levels_note": ("diagnostic only; NOT monotone along the digit on "
                                          "this mesh - see R1A root-cause audit")}


def thumb_masks(ref, tf, tau, r_tt, r_max):
    """R1A semantic region masks (thumb chain family).  Deterministic, evidence based."""
    NV = ref["NV"]
    s = tf["arc_thumb_mm"]
    s_mcp, s_ip = tf["s_MCP_joint_mm"], tf["s_IP_joint_mm"]
    d = [ref["dchain"][i]["THUMB"] for i in range(NV)]
    own = ref["OWN_V"]
    FO = ref["FO"]
    MAT = ref["MAT0"]
    TOPO = ref["TOPO0"]

    # vertices incident to a face that carries NAIL_BED material and is thumb owned
    nail_thumb_v = set()
    for fi, vs in enumerate(TOPO):
        if MAT[fi] == 1 and FO[fi] == "THUMB":
            nail_thumb_v.update(vs)
    cap_v = set(ref["cap"]["thumb_cap_vertex_ids"])

    def f_tube(dd):
        if r_max <= r_tt + 1e-9:
            return 1.0
        return 1.0 - S((dd - r_tt) / (r_max - r_tt))

    distal, proximal, metacarpal, thenar_base = set(), set(), set(), set()
    for i in range(NV):
        o = own[i]
        si = s[i]
        di = d[i]
        if o == "THUMB" or i in nail_thumb_v or i in cap_v:
            if i in nail_thumb_v or i in cap_v or si >= s_ip - tau:
                distal.add(i)
            if s_mcp - tau <= si <= s_ip + tau:
                proximal.add(i)
            if si <= s_mcp + tau:
                metacarpal.add(i)
        # thenar base: base zone of the thumb whose lateral radius is beyond the tube
        if o in ("THUMB", "wrist") and si <= s_mcp + tau and di > r_tt:
            thenar_base.add(i)
    return {"nail_thumb_vertices": nail_thumb_v, "cap_vertices": cap_v,
            "THUMB_DISTAL": distal, "THUMB_PROXIMAL": proximal,
            "THUMB_FIRST_METACARPAL": metacarpal, "THENAR_BASE": thenar_base,
            "f_tube": f_tube}


def first_web_mask(ref, tf, tau, r_tt):
    """Pose-aware first-web commissure band.

    A vertex is FIRST WEB when
      (a) its two nearest chains are exactly {THUMB, INDEX}          -> it lies on the
          ownership boundary between the thumb and the index,
      (b) the thumb-chain arc of its projection is at or proximal of the thumb IP joint
          (minus one transition band) -> EXCLUDES the thumb distal phalanx / nail,
      (c) the index-chain arc of its projection is at or proximal of the index PIP joint
          (plus one transition band) -> EXCLUDES the index distal chain,
      (d) it is not part of the thumb nail patch and not in the thumb distal cap.
    """
    NV = ref["NV"]
    V0 = ref["V0"]
    jf = ref["jf"]
    s = tf["arc_thumb_mm"]
    s_ip = tf["s_IP_joint_mm"]
    tau = tau
    pts_i = chp(jf, "INDEX")
    XIJ_I = chain_arc_table(jf, "INDEX")
    s_pip_i = XIJ_I[1]                       # index PIP joint arc (INDEX_MCP tail)
    FO = ref["FO"]
    MAT = ref["MAT0"]
    TOPO = ref["TOPO0"]
    nailT = set()
    for fi, vs in enumerate(TOPO):
        if MAT[fi] == 1 and FO[fi] == "THUMB":
            nailT.update(vs)
    cap_v = set(ref["cap"]["thumb_cap_vertex_ids"])
    web = set()
    for i in range(NV):
        if {ref["order2"][i][0][0], ref["order2"][i][1][0]} != {"THUMB", "INDEX"}:
            continue
        if i in nailT or i in cap_v:
            continue
        if s[i] > s_ip - tau:
            continue
        si, _ = arc_of(pts_i, V0[i])
        if si > s_pip_i + tau:
            continue
        web.add(i)
    return web



def thumb_radius(ref):
    """characteristic thumb surface radius = median lateral distance to the thumb chain
    over thumb-owned vertices (data-derived)."""
    ds = sorted(ref["dchain"][i]["THUMB"] for i in range(ref["NV"])
                if ref["OWN_V"][i] == "THUMB")
    return ds[len(ds) // 2] if ds else 0.0


def thumb_radii(ref, tf):
    """data-derived radial scales for the thumb base split.

    R_TT  = median lateral distance to the thumb chain over the thumb-owned vertices of the
            PROXIMAL PHALANX band (a clean tube region: no thenar, no web) -> tube radius
    R_MAX = p95 lateral distance over the thumb-owned vertices of the metacarpal/base band
            (metacarpal + thenar + web corner) -> outer radius of the thumb base
    """
    s = tf["arc_thumb_mm"]
    s_mcp, s_ip = tf["s_MCP_joint_mm"], tf["s_IP_joint_mm"]
    d = lambda i: ref["dchain"][i]["THUMB"]
    tube = sorted(d(i) for i in range(ref["NV"])
                  if ref["OWN_V"][i] == "THUMB" and s_mcp <= s[i] <= s_ip)
    base = sorted(d(i) for i in range(ref["NV"])
                  if ref["OWN_V"][i] == "THUMB" and s[i] <= s_mcp)
    r_tt = tube[len(tube) // 2] if tube else 8.0
    r_max = base[int(0.95 * (len(base) - 1))] if base else 2.0 * r_tt
    return r_tt, max(r_max, r_tt * 1.25)


def nail_thumb_vertices(ref):
    """vertices of a polygon that carries NAIL_BED material and whose FACE centroid is
    thumb owned (the R1 / NAIL_WEIGHT_AUDIT definition, kept identical)."""
    out = set()
    for fi, vs in enumerate(ref["TOPO0"]):
        if ref["MAT0"][fi] == 1 and ref["FO"][fi] == "THUMB":
            out.update(vs)
    return out


def ownership_r1a(ref):
    """R1A semantic ownership authority.

    R1 used the 2-D nearest chain polyline distance as the VERTEX ownership authority.  That
    heuristic mis-assigns the thumb nail-border vertices (1383, 2740) and two of the approved
    thumb distal-cap vertices (1061, 2189) to INDEX, because in this pose the thumb's distal
    phalanx abuts the index MCP region.  R1A promotes the evidence based authority:
    a vertex incident to a THUMB-owned NAIL_BED face, or inside the R2A-approved thumb
    distal-cap patch, is THUMB owned.
    """
    nail = nail_thumb_vertices(ref)
    cap = set(ref["cap"]["thumb_cap_vertex_ids"])
    return [("THUMB" if (ref["OWN_V"][i] == "THUMB" or i in nail or i in cap)
             else ref["OWN_V"][i]) for i in range(ref["NV"])], nail, cap


def build_regions(ref, tf, tau, r_tt, r_max):
    """R1A semantic regions (thumb chain family).  Deterministic + evidence based."""
    NV = ref["NV"]
    s = tf["arc_thumb_mm"]
    s_mcp, s_ip = tf["s_MCP_joint_mm"], tf["s_IP_joint_mm"]
    d = [ref["dchain"][i]["THUMB"] for i in range(NV)]
    own_r1a, nail, cap = ownership_r1a(ref)
    own = ref["OWN_V"]
    r_tube = r_tt + tau

    distal = set(i for i in range(NV) if own_r1a[i] == "THUMB" and s[i] >= s_ip - tau)
    proximal = set(i for i in range(NV) if own_r1a[i] == "THUMB"
                   and s_mcp - tau <= s[i] < s_ip - tau and d[i] <= r_tube)
    metacarpal = set(i for i in range(NV) if own_r1a[i] == "THUMB"
                     and s[i] < s_mcp - tau and d[i] <= r_tube)
    base_fold = set(i for i in range(NV) if own_r1a[i] == "THUMB"
                    and d[i] > r_tube and s_mcp + tau < s[i] < s_ip - tau)
    thenar_thumb = set(i for i in range(NV) if own_r1a[i] == "THUMB"
                       and s[i] <= s_mcp + tau and d[i] > r_tt)
    thumb_own_set = set(i for i in range(NV) if own_r1a[i] == "THUMB")
    thenar_wrist = set(j for j in rings(ref["eadj"], thumb_own_set, 2)
                       if own[j] == "wrist" and s[j] <= s_mcp)
    thenar = thenar_thumb | thenar_wrist

    # THUMB|INDEX topological ownership boundary -> first web band on the thumb side
    bnd = set()
    for a, b in ref["EDGES"]:
        if (own_r1a[a] == "THUMB" and own_r1a[b] == "INDEX") or \
           (own_r1a[a] == "INDEX" and own_r1a[b] == "THUMB"):
            bnd.add(a)
            bnd.add(b)
    band = rings(ref["eadj"], bnd, 2)
    s_pip_i = chain_arc_table(ref["jf"], "INDEX")[1]
    pts_i = chp(ref["jf"], "INDEX")
    web = set()
    for i in band:
        if own_r1a[i] != "THUMB" or i in nail or i in cap:
            continue
        if s[i] > s_ip - tau:
            continue
        if arc_of(pts_i, ref["V0"][i])[0] > s_pip_i + tau:
            continue
        web.add(i)
    web_index_side = set(i for i in band if own_r1a[i] == "INDEX")

    central_palm = set(i for i in range(NV) if own[i] == "wrist") - thenar
    auth = thumb_own_set | thenar | web

    covered = distal | proximal | metacarpal | base_fold | thenar | web
    uncovered = sorted(thumb_own_set - covered)
    return {"own_r1a": own_r1a, "nail_thumb_vertices": nail, "cap_vertices": cap,
            "r_tube": r_tube, "web_band_ring_vs": sorted(bnd),
            "THUMB_DISTAL": distal, "THUMB_PROXIMAL": proximal,
            "THUMB_FIRST_METACARPAL": metacarpal, "THUMB_BASE_FOLD": base_fold,
            "THENAR_BASE": thenar, "FIRST_WEB": web, "WEB_INDEX_SIDE": web_index_side,
            "CENTRAL_PALM": central_palm, "AUTH": auth, "uncovered_thumb_owned": uncovered,
            "f_tube": lambda dd: (1.0 - S((dd - r_tt) / (r_max - r_tt))
                                  if r_max > r_tt + 1e-9 else 1.0)}

