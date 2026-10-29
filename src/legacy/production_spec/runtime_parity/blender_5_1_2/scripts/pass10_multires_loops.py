# STAGE1C - Pass 10: same edge-loop census on the multires level-1 evaluated mesh (does +1 subdiv fix T-01?)
import bpy, bmesh, json
from mathutils import Vector
TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
mr = next((m for m in ob.modifiers if m.type == "MULTIRES"), None)
mr.levels = 1
mr.render_levels = 1
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
ob_eval = ob.evaluated_get(dg)
me = ob_eval.to_mesh()
bm = bmesh.new(); bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
# world transform
mw = ob.matrix_world
W = [(mw @ v.co).copy() for v in bm.verts]
E = [(e.verts[0].index, e.verts[1].index) for e in bm.edges]
print("L1 verts", len(W), "edges", len(E))

incident = {}
for i,(a,b) in enumerate(E):
    incident.setdefault(a, []).append(i)
    incident.setdefault(b, []).append(i)

def walk(se, sv):
    loop=[se]; ce=se; cv=sv
    while True:
        a,b = E[ce]
        nv = b if cv==a else a
        d = W[nv]-W[cv]
        if d.length < 1e-9: break
        d = d.normalized()
        if len(incident.get(nv, [])) != 4: break
        best, bs = None, -2
        for ei in incident[nv]:
            if ei == ce: continue
            x,y = E[ei]
            o = y if x==nv else x
            dd = W[o]-W[nv]
            if dd.length < 1e-9: continue
            s = dd.normalized().dot(d)
            if s > bs: bs, best = s, ei
        if best is None or bs < 0.2 or best == se or best in loop: break
        loop.append(best); cv, ce = nv, best
        if len(loop) > 800: break
    return loop

covered=set(); loops=[]
for i in range(len(E)):
    if i in covered: continue
    a,b = E[i]
    l1 = walk(i,a); l2 = walk(i,b)
    full = list(reversed(l2[1:])) + l1
    if len(full) < 3: continue
    for ei in full: covered.add(ei)
    loops.append(full)

SEG = {
    "THUMB":  ((1.492, 0.036, 0.243), (1.443, 0.012, 0.298), 0.014),
    "INDEX":  ((1.458, 0.023, 0.163), (1.446, 0.011, 0.245), 0.0115),
    "MIDDLE": ((1.422, 0.023, 0.149), (1.424, 0.010, 0.235), 0.0115),
    "RING":   ((1.3925, 0.029, 0.160), (1.399, 0.014, 0.235), 0.0115),
    "LITTLE": ((1.3545, 0.031, 0.187), (1.372, 0.019, 0.262), 0.0110),
}
def sg(p0s,p1s):
    p0,p1 = Vector(p0s), Vector(p1s); ax = p1-p0; L=ax.length
    return p0, ax/L, L
out={}
for name,(p0s,p1s,rad) in SEG.items():
    p0, ax, L = sg(p0s,p1s)
    rings=[]
    for lg in loops:
        ts=[]; aligns=[]
        for ei in lg:
            i0,i1 = E[ei]
            mid=(W[i0]+W[i1])*0.5
            d=mid-p0; t=d.dot(ax)
            if -0.006 <= t <= L+0.006 and (d-ax*t).length <= rad+0.006:
                ts.append(t)
                dd=W[i1]-W[i0]
                if dd.length>1e-9: aligns.append(abs(dd.normalized().dot(ax)))
        if len(ts)<4 or len(ts) < 0.55*len(lg): continue
        a=sum(aligns)/len(aligns)
        if a < 0.45:
            rings.append(round(sum(ts)/len(ts),5))
    rings.sort()
    gaps=[round(rings[i+1]-rings[i],5) for i in range(len(rings)-1)]
    if name=="THUMB":
        joints={"IP":0.42*L,"MCP_T":0.72*L,"CMC":L-0.10*L}
    else:
        joints={"DIP":0.26*L,"PIP":0.58*L,"MCP":L-0.06*L}
    jr={}
    for jn,jt in joints.items():
        w=min(0.011,0.12*L)
        jr[jn]={"loops_in_window": sum(1 for r in rings if abs(r-jt)<=w), "window_m": round(w,4),
                "loop_t":[r for r in rings if abs(r-jt)<=w]}
    out[name]={"circ_loops_total":len(rings),"median_gap_m": round(sorted(gaps)[len(gaps)//2],5) if gaps else None,
               "positions_m":rings,"joints":jr}
    print(f"{name}: loops={len(rings)} medgap={out[name]['median_gap_m']} joints={ {k:v['loops_in_window'] for k,v in jr.items()} }")
    print("   pos:", rings)
with open(r"<HANDS_ROOT>/production_spec/runtime_parity/blender_5_1_2/evidence\topology_rings_multires_l1_5_1_2.json", "w") as f:
    json.dump(out,f,indent=1)
ob_eval.to_mesh_clear()
print("PASS10_DONE")
