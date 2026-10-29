# =====================================================================================
# STAGE6B_R1C -- PENETRATION VISUAL ADJUDICATION : shared evidence + software rasteriser
# =====================================================================================
# EVIDENCE-ONLY ROUND.  Nothing is written to any .blend, no geometry / topology /
# weight / bone / joint / ownership change, no pose solve, no collision correction.
#
# Renderer: a real triangle rasteriser (z-buffer + flat/Gouraud shading) over the ACTUAL
# posed mesh triangles, so the Human Review images show a SOLID mesh surface, not a point
# cloud.  The cross-section is a REAL geometric mesh/plane intersection (segment clipping),
# never a screen-space overlay.
# =====================================================================================
import os
import sys
import json
import math

import bpy
import numpy as np
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S6D = os.path.join(PROD, "stage6_deformation")
S6B_R1B = os.path.join(S6D, "stage6b_r1b")
S6B_R1C = os.path.join(S6D, "stage6b_r1c")
for _p in (os.path.join(S6D, "stage6b", "scripts"),
           os.path.join(S6D, "stage6b_r1b", "scripts")):
    if _p not in sys.path:
        sys.path.append(_p)

import s6b_common as B                                              # noqa: E402
import s6br1b_common as K                                          # noqa: E402

MM = 1000.0
MESH_OBJ = "Hand  - Realistic"
RIG_OBJ = "RIGHT_HAND_PRODUCTION_RIG"


# =====================================================================================
# exact triangle / triangle geometry
# =====================================================================================
def tri_plane_sign(p, a, b, c):
    """signed distance of p from the plane of triangle (a,b,c), oriented by its normal"""
    n = (b - a).cross(c - a)
    if n.length < 1e-18:
        return None, None
    n = n.normalized()
    return (p - a).dot(n), n


def ray_triangle(o, d, a, b, c):
    """Moller-Trumbore.  returns t or None (t in units of |d|)"""
    e1 = b - a
    e2 = c - a
    h = d.cross(e2)
    det = e1.dot(h)
    if abs(det) < 1e-18:
        return None
    inv = 1.0 / det
    s = o - a
    u = s.dot(h) * inv
    if u < -1e-12 or u > 1 + 1e-12:
        return None
    q = s.cross(e1)
    v = d.dot(q) * inv
    if v < -1e-12 or u + v > 1 + 1e-12:
        return None
    t = e2.dot(q) * inv
    return t


def tri_tri_intersection(A, Btri):
    """exact-ish tri/tri: collect the intersection segment endpoints by clipping each
    edge of A against B and each edge of B against A.  Returns (points, ok)."""
    pts = []
    for tri, other in ((A, Btri), (Btri, A)):
        a, b, c = tri
        for (p, q) in ((a, b), (b, c), (c, a)):
            d = q - p
            if d.length < 1e-15:
                continue
            t = ray_triangle(p, d, other[0], other[1], other[2])
            if t is not None and -1e-9 <= t <= 1 + 1e-9:
                pts.append(p + d * t)
    if len(pts) < 2:
        return pts, False
    return pts, True


def seg_len(pts):
    m = 0.0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            m = max(m, (pts[i] - pts[j]).length)
    return m


def vertex_penetration(A, Btri):
    """how far the vertices of A have gone 'inside' B (positive = interpenetration)"""
    n = (Btri[1] - Btri[0]).cross(Btri[2] - Btri[0])
    if n.length < 1e-18:
        return 0.0
    n = n.normalized()
    worst = max((Btri[0] - v).dot(n) for v in A)      # positive when v is behind B's plane
    return max(0.0, worst)


# =====================================================================================
# software rasteriser (solid mesh surface)
# =====================================================================================
def ortho_basis(d, up_hint):
    """returns (right, up) such that (right, up, d) is right-handed and `up` points up
    on screen."""
    d = Vector(d).normalized()
    up = Vector(up_hint)
    u = up - up.dot(d) * d
    if u.length < 1e-9:
        alt = Vector((0.0, 1.0, 0.0))
        u = alt - alt.dot(d) * d
    u = u.normalized()
    r = u.cross(d).normalized()
    return r, u


def bary_inside(p, a, b, c, tol=1e-9):
    v0 = b - a
    v1 = c - a
    v2 = p - a
    d00 = v0.dot(v0)
    d01 = v0.dot(v1)
    d11 = v1.dot(v1)
    d20 = v2.dot(v0)
    d21 = v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-18:
        return False
    v = (d11 * d20 - d01 * d21) / den
    w = (d00 * d21 - d01 * d20) / den
    u = 1.0 - v - w
    return (u >= -tol) and (v >= -tol) and (w >= -tol)


def poke_depth(A, Btri):
    """how far surface A pokes THROUGH triangle B.

    Only vertices of A whose perpendicular foot really lands INSIDE B are counted, and
    the inside test is done by an explicit clamped closest-point distance (NOT by a
    barycentric sign test, which is numerically unstable on sliver triangles and can
    fabricate tens of millimetres out of a degenerate face)."""
    e = max(((A[0] - A[1]).length, (A[1] - A[2]).length, (A[2] - A[0]).length,
             (Btri[0] - Btri[1]).length, (Btri[1] - Btri[2]).length, (Btri[2] - Btri[0]).length))
    if e <= 1e-9:
        return 0.0
    n = (Btri[1] - Btri[0]).cross(Btri[2] - Btri[0])
    if n.length < 1e-18:
        return 0.0
    n = n.normalized()
    limit = 2.0 * e                      # a poke cannot exceed twice the local facet size
    best = 0.0
    for v in A:
        d = (v - Btri[0]).dot(n)
        ad = abs(d)
        if ad <= 1e-12 or ad > limit:
            continue
        proj = v - d * n
        cp = closest_point_on_triangle(proj, Btri[0], Btri[1], Btri[2])
        if (proj - cp).length <= 1e-6:   # 0.001 mm
            best = max(best, ad)
    return best


def face_normal_of(V, p):
    n = Vector((0.0, 0.0, 0.0))
    for i in range(len(p)):
        a = V[p[i]]
        b = V[p[(i + 1) % len(p)]]
        n = n + a.cross(b)
    return n.normalized() if n.length > 1e-18 else Vector((0, 0, 1))


def stage6b_proxy(V, POLY, fa, fb):
    """EXACTLY the Stage6B frozen penetration-proxy predicate:
       min(|(centroid_b - centroid_a) . n_a|, |(centroid_a - centroid_b) . n_b|)"""
    ca = sum((V[v] for v in POLY[fa]), Vector()) / len(POLY[fa])
    cb = sum((V[v] for v in POLY[fb]), Vector()) / len(POLY[fb])
    na = face_normal_of(V, POLY[fa])
    nb = face_normal_of(V, POLY[fb])
    return min(abs((cb - ca).dot(na)), abs((ca - cb).dot(nb))) * MM


def closest_point_on_triangle(p, a, b, c):
    """closest point of triangle (a,b,c) to p (clamped)."""
    ab = b - a
    ac = c - a
    ap = p - a
    d1 = ab.dot(ap)
    d2 = ac.dot(ap)
    if d1 <= 0.0 and d2 <= 0.0:
        return a
    bp = p - b
    d3 = ab.dot(bp)
    d4 = ac.dot(bp)
    if d3 >= 0.0 and d4 <= d3:
        return b
    vc = d1 * d4 - d3 * d2
    if vc <= 0.0 and d1 >= 0.0 and d3 <= 0.0:
        v = d1 / (d1 - d3)
        return a + ab * v
    cp = p - c
    d5 = ab.dot(cp)
    d6 = ac.dot(cp)
    if d6 >= 0.0 and d5 <= d6:
        return c
    vb = d5 * d2 - d1 * d6
    if vb <= 0.0 and d2 >= 0.0 and d6 <= 0.0:
        w = d2 / (d2 - d6)
        return a + ac * w
    va = d3 * d6 - d5 * d4
    if va <= 0.0 and (d4 - d3) >= 0.0 and (d5 - d6) >= 0.0:
        w = (d4 - d3) / ((d4 - d3) + (d5 - d6))
        return b + (c - b) * w
    den = 1.0 / (va + vb + vc)
    v = vb * den
    w = vc * den
    return a + ab * v + ac * w


class View(object):
    """orthographic view"""

    def __init__(self, centre, direction, up_hint, half_width_mm, Wp, Hp):
        self.c = Vector(centre)
        self.d = Vector(direction).normalized()
        self.r, self.u = ortho_basis(self.d, Vector(up_hint))
        self.hw = float(half_width_mm) / MM
        self.W, self.H = Wp, Hp
        self.s = (Wp * 0.5 - 8.0) / self.hw             # px per metre

    def proj(self, p):
        q = p - self.c
        return (q.dot(self.r) * self.s + self.W * 0.5,
                q.dot(self.u) * self.s + self.H * 0.5,
                q.dot(self.d))


def tris_of(POLY, V):
    out = []
    for fi, p in enumerate(POLY):
        if len(p) == 3:
            out.append((fi, (p[0], p[1], p[2])))
        else:
            out.append((fi, (p[0], p[1], p[2])))
            out.append((fi, (p[0], p[2], p[3])))
    return out


def face_normals(V, POLY):
    out = []
    for p in POLY:
        n = Vector((0.0, 0.0, 0.0))
        for i in range(len(p)):
            a = V[p[i]]
            b = V[p[(i + 1) % len(p)]]
            n = n + a.cross(b)
        out.append(n.normalized() if n.length > 1e-18 else Vector((0, 0, 1)))
    return out


def vertex_normals(V, POLY):
    fn = face_normals(V, POLY)
    acc = [Vector((0.0, 0.0, 0.0)) for _ in V]
    for fi, p in enumerate(POLY):
        for v in p:
            acc[v] = acc[v] + fn[fi]
    for i in range(len(V)):
        if acc[i].length > 1e-18:
            acc[i] = acc[i].normalized()
        else:
            acc[i] = Vector((0, 0, 1))
    return acc


class Canvas(object):
    def __init__(self, Wp, Hp, bg=(0.055, 0.06, 0.07)):
        self.W, self.H = Wp, Hp
        self.rgb = np.zeros((Hp, Wp, 3), dtype=np.float32)
        self.rgb[:, :, 0] = bg[0]
        self.rgb[:, :, 1] = bg[1]
        self.rgb[:, :, 2] = bg[2]
        self.z = np.full((Hp, Wp), 1e30, dtype=np.float64)

    def px(self, x, y, c, r=0, alpha=1.0, z=None, write_z=True):
        xi, yi = int(round(x)), int(round(y))
        if r <= 0:
            if 0 <= xi < self.W and 0 <= yi < self.H:
                if z is None or z < self.z[yi, xi]:
                    self.rgb[yi, xi] = self.rgb[yi, xi] * (1 - alpha) + np.array(c, np.float32) * alpha
                    if write_z and z is not None:
                        self.z[yi, xi] = z
            return
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy > r * r + 1:
                    continue
                X, Y = xi + dx, yi + dy
                if 0 <= X < self.W and 0 <= Y < self.H:
                    if z is None or z < self.z[Y, X]:
                        self.rgb[Y, X] = self.rgb[Y, X] * (1 - alpha) + np.array(c, np.float32) * alpha
                        if write_z and z is not None:
                            self.z[Y, X] = z

    def line(self, p, q, c, r=1, alpha=1.0, z=None):
        n = max(2, int(max(abs(q[0] - p[0]), abs(q[1] - p[1])) * 1.6) + 1)
        for i in range(n + 1):
            t = i / n
            self.px(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, c, r, alpha, z)

    def tri(self, p0, p1, p2, shade, base, alpha=1.0, blend=False):
        xs = [p0[0], p1[0], p2[0]]
        ys = [p0[1], p1[1], p2[1]]
        x0 = max(0, int(math.floor(min(xs))))
        x1 = min(self.W - 1, int(math.ceil(max(xs))))
        y0 = max(0, int(math.floor(min(ys))))
        y1 = min(self.H - 1, int(math.ceil(max(ys))))
        if x1 < x0 or y1 < y0:
            return
        xsar = np.arange(x0, x1 + 1, dtype=np.float64) + 0.5
        ysar = np.arange(y0, y1 + 1, dtype=np.float64) + 0.5
        X, Y = np.meshgrid(xsar, ysar)
        e0x, e0y = p1[0] - p0[0], p1[1] - p0[1]
        e1x, e1y = p2[0] - p0[0], p2[1] - p0[1]
        den = e0x * e1y - e0y * e1x
        if abs(den) < 1e-12:
            return
        bx = X - p0[0]
        by = Y - p0[1]
        l1 = (bx * e1y - by * e1x) / den
        l2 = (e0x * by - e0y * bx) / den
        m = (l1 >= 0.0) & (l2 >= 0.0) & (l1 + l2 <= 1.0)
        if not m.any():
            return
        Z = p0[2] + l1 * (p1[2] - p0[2]) + l2 * (p2[2] - p0[2])
        Zm = np.where(m, Z, 1e30)
        if not blend:
            upd = Zm < self.z[y0:y1 + 1, x0:x1 + 1]
            if not upd.any():
                return
            sh = np.array(shade, dtype=np.float32).reshape(1, 1, 1)
            col = np.zeros((y1 - y0 + 1, x1 - x0 + 1, 3), dtype=np.float32)
            col[:] = np.array(base, dtype=np.float32) * sh
            tgt = self.rgb[y0:y1 + 1, x0:x1 + 1]
            m2 = upd[:, :, None]
            tgt[:] = np.where(m2, tgt * (1 - alpha) + col * alpha, tgt)
            self.z[y0:y1 + 1, x0:x1 + 1] = np.where(upd, Zm, self.z[y0:y1 + 1, x0:x1 + 1])
        else:
            sh = np.array(shade, dtype=np.float32).reshape(1, 1, 1)
            col = np.zeros((y1 - y0 + 1, x1 - x0 + 1, 3), dtype=np.float32)
            col[:] = np.array(base, dtype=np.float32) * sh
            tgt = self.rgb[y0:y1 + 1, x0:x1 + 1]
            m2 = m[:, :, None]
            tgt[:] = np.where(m2, tgt * (1 - alpha) + col * alpha, tgt)


FONT = {
 "A":["01110","10001","10001","11111","10001","10001","10001"],"B":["11110","10001","11110","10001","10001","10001","11110"],
 "C":["01110","10001","10000","10000","10000","10001","01110"],"D":["11110","10001","10001","10001","10001","10001","11110"],
 "E":["11111","10000","11110","10000","10000","10000","11111"],"F":["11111","10000","11110","10000","10000","10000","10000"],
 "G":["01110","10001","10000","10111","10001","10001","01111"],"H":["10001","10001","11111","10001","10001","10001","10001"],
 "I":["11111","00100","00100","00100","00100","00100","11111"],"J":["00111","00010","00010","00010","00010","10010","01100"],
 "K":["10001","10010","11100","10100","10010","10010","10001"],"L":["10000","10000","10000","10000","10000","10000","11111"],
 "M":["10001","11011","10101","10101","10001","10001","10001"],"N":["10001","11001","10101","10011","10001","10001","10001"],
 "O":["01110","10001","10001","10001","10001","10001","01110"],"P":["11110","10001","10001","11110","10000","10000","10000"],
 "Q":["01110","10001","10001","10001","10101","10010","01101"],"R":["11110","10001","10001","11110","10100","10010","10001"],
 "S":["01111","10000","10000","01110","00001","00001","11110"],"T":["11111","00100","00100","00100","00100","00100","00100"],
 "U":["10001","10001","10001","10001","10001","10001","01110"],"V":["10001","10001","10001","10001","10001","01010","00100"],
 "W":["10001","10001","10001","10101","10101","11011","10001"],"X":["10001","10001","01010","00100","01010","10001","10001"],
 "Y":["10001","10001","01010","00100","00100","00100","00100"],"Z":["11111","00001","00010","00100","01000","10000","11111"],
 "0":["01110","10001","10011","10101","11001","10001","01110"],"1":["00100","01100","00100","00100","00100","00100","01110"],
 "2":["01110","10001","00001","00110","01000","10000","11111"],"3":["11111","00010","00100","00010","00001","10001","01110"],
 "4":["00010","00110","01010","10010","11111","00010","00010"],"5":["11111","10000","11110","00001","00001","10001","01110"],
 "6":["00110","01000","10000","11110","10001","10001","01110"],"7":["11111","00001","00010","00100","01000","01000","01000"],
 "8":["01110","10001","10001","01110","10001","10001","01110"],"9":["01110","10001","10001","01111","00001","00010","01100"],
 " ":["00000"]*7,"-":["00000","00000","00000","11111","00000","00000","00000"],"_":["00000"]*6+["11111"],
 ":":["00000","00100","00100","00000","00100","00100","00000"],".":["00000","00000","00000","00000","00000","01100","01100"],
 "/":["00001","00010","00010","00100","01000","01000","10000"],"+":["00000","00100","00100","11111","00100","00100","00000"],
 "=":["00000","00000","11111","00000","11111","00000","00000"],"(":["00010","00100","01000","01000","01000","00100","00010"],
 ")":["01000","00100","00010","00010","00010","00100","01000"],"%":["11001","11010","00010","00100","01000","01011","10011"],
 "?":["01110","10001","00001","00110","00100","00000","00100"],",":["00000","00000","00000","00000","01100","00100","01000"],
 "*":["00000","10101","01110","11111","01110","10101","00000"],"<":["00001","00010","00100","01000","00100","00010","00001"],
 ">":["10000","01000","00100","00010","00100","01000","10000"],"#":["01010","11111","01010","01010","11111","01010","00000"],
}


def text(cv, x, y, s, size=2, c=(0.95, 0.95, 0.95), alpha=1.0):
    for ch in str(s).upper():
        g = FONT.get(ch, FONT["?"])
        for gy in range(len(g)):
            for gx in range(len(g[0])):
                if g[gy][gx] == "1":
                    for dy in range(size):
                        for dx in range(size):
                            cv.px(x + gx * size + dx, y + gy * size + dy, c, 0, alpha)
        x += 6 * size
    return x


def save(cv, name, subdir=None):
    d = subdir or os.path.join(S6B_R1C, "renders")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    img = bpy.data.images.new(name, width=cv.W, height=cv.H, alpha=False)
    pix = np.zeros((cv.H, cv.W, 4), dtype=np.float32)
    pix[:, :, :3] = cv.rgb
    pix[:, :, 3] = 1.0
    img.pixels.foreach_set(np.ascontiguousarray(pix[::-1]).reshape(-1).tolist())
    img.filepath_raw = p
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)
    return p
