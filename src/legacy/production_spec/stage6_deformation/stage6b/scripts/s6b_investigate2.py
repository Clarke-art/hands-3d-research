# =====================================================================================
# STAGE6B -- read-only characterisation of the thumb/index ownership-boundary edges
# =====================================================================================
import bpy
import sys
import os
import json
import math
import collections
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import s6b_common as B                                          # noqa: E402

OUTDIR = sys.argv[sys.argv.index("--") + 1:][0]
ctx = B.build_context()
V0 = ctx["V0"]
NV = ctx["NV"]
POLY = ctx["poly"]
EDGES = ctx["edges"]
own = ctx["own_r1a"]
FO = ctx["FO"]
WEB = set(ctx["first_web"])
NAIL = set(ctx["nail_thumb"])
CAP = set(ctx["distal_cap"])
EDGE_LEN0 = [(V0[a] - V0[b]).length * 1000.0 for a, b in EDGES]

pairs = collections.Counter()
short = []
for k, (a, b) in enumerate(EDGES):
    if own[a] == own[b]:
        continue
    key = tuple(sorted((own[a], own[b])))
    pairs[key] += 1
    if EDGE_LEN0[k] < 3.0:
        short.append((EDGE_LEN0[k], k, a, b, own[a], own[b],
                      a in WEB, b in WEB, a in NAIL, b in NAIL, a in CAP, b in CAP))

print("=== edges crossing a digit-ownership boundary (count by digit pair) ===")
for k, v in sorted(pairs.items(), key=lambda kv: -kv[1]):
    print("   %-16s %d" % ("|".join(k), v))
print("total crossing edges = %d of %d" % (sum(pairs.values()), len(EDGES)))

print()
print("=== crossing edges shorter than 3.0 mm at bind (the fusion candidates) ===")
short.sort()
for r in short[:40]:
    l, k, a, b, oa, ob_, aw, bw, an, bn, ac, bc = r
    print("   %.4f mm  e%-5d v%-5d(%s%s%s%s)-v%-5d(%s%s%s%s)  in_web=%s in_nail=%s in_cap=%s"
          % (l, k, a, oa, " W" if aw else "", " N" if an else "", " C" if ac else "",
             b, ob_, " W" if bw else "", " N" if bn else "", " C" if bc else "",
             aw or bw, an or bn, ac or bc))
print("count < 3.0 mm = %d ; < 2.0 mm = %d ; < 1.5 mm = %d"
      % (len(short), sum(1 for r in short if r[0] < 2.0),
         sum(1 for r in short if r[0] < 1.5)))

print()
print("=== THUMB|INDEX crossing edges only ===")
ti = [r for r in short if set((r[4], r[5])) == {"THUMB", "INDEX"}]
print("count = %d ; min length %.4f mm ; median %.4f mm"
      % (len(ti), ti[0][0] if ti else -1,
         sorted(r[0] for r in ti)[len(ti) // 2] if ti else -1))
print("  how many involve a NAIL vertex: %d ; a CAP vertex: %d ; a WEB vertex: %d"
      % (sum(1 for r in ti if r[8] or r[9]), sum(1 for r in ti if r[10] or r[11]),
         sum(1 for r in ti if r[6] or r[7])))

print()
print("=== all THUMB|INDEX crossing edges (length, endpoints) ===")
for r in sorted(ti)[:30]:
    l, k, a, b, oa, ob_, aw, bw, an, bn, ac, bc = r
    print("   %.4f mm  e%-5d v%-5d(%s)%s%s - v%-5d(%s)%s%s"
          % (l, k, a, oa, " N" if an else "", " W" if aw else "",
             b, ob_, " N" if bn else "", " W" if bw else ""))
print("INVESTIGATE2_DONE")
