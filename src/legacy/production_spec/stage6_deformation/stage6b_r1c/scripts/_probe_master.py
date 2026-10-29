import os, sys, json
import bpy
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import r1c_pen_common as R
MESH="Hand  - Realistic"
IDS=[693,2156,2172,3201,689,2160,697,2162,2191,2584,2176,704,2190,1062,2578,2071,651,154,1066,1067,2580,2058,2583,2066,649]
FILES=[("Stage5B R1B (frozen master)", os.path.join(R.PROD,"stage5_production_rig","stage5b_r1b","RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend")),
       ("Stage5B R1C (candidate)",    R.K.R1C_MASTER)]
def dom(W):
    return max(W.items(), key=lambda kv: kv[1])[0] if W else None
for lbl,p in FILES:
    bpy.ops.wm.open_mainfile(filepath=p)
    ob=bpy.data.objects[MESH]; G=[g.name for g in ob.vertex_groups]
    def W(i): return dict((G[g.group],round(g.weight,3)) for g in ob.data.vertices[i].groups if g.weight>1e-3)
    n_wrist=0; n_ip=0
    for i in IDS:
        d=dom(W(i))
        if d=="WRIST_R": n_wrist+=1
        if d=="THUMB_IP_R": n_ip+=1
    print("=== %s ==="%lbl)
    print("   WRIST_R-dominant %d / THUMB_IP_R-dominant %d of %d"%(n_wrist,n_ip,len(IDS)))
    for i in (2156,693,2191,2584):
        print("   v%-5d %s"%(i,W(i)))
    # global census of hard 0/1 flips
    POLY=[tuple(p.vertices) for p in ob.data.polygons]
    flip=0
    for p in POLY:
        n=len(p)
        for k in range(n):
            a,b=p[k],p[(k+1)%n]
            wa,wb=W(a),W(b)
            if len(wa)==1 and len(wb)==1 and list(wa)[0]!=list(wb)[0]:
                if list(wa.values())[0]>0.95 and list(wb.values())[0]>0.95: flip+=1
    print("   hard 0/1 flip edges in the WHOLE mesh: %d"%flip)
