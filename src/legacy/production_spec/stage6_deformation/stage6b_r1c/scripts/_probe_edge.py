import os, sys, json
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import r1c_pen_common as R
ctx=R.B.build_context(); ref=ctx["ref"]; POLY=ctx["poly"]; V0=ref["V0"]; NV=ref["NV"]
print("NV",NV,"faces",len(POLY),"verts per face set",sorted(set(len(p) for p in POLY)))
TRIS=R.tris_of(POLY,V0)
print("tris",len(TRIS))
me=[]
for fi,t in TRIS:
    a,b,c=V0[t[0]],V0[t[1]],V0[t[2]]
    me.append(((a-b).length+(b-c).length+(c-a).length)/3.0*1000.0)
me=np.array(me)
print("tri mean edge mm: min %.4f p50 %.4f p90 %.4f p99 %.4f max %.4f"%(me.min(),np.percentile(me,50),np.percentile(me,90),np.percentile(me,99),me.max()))
print("frac > 10mm:",float((me>10).mean())," frac >20mm:",float((me>20).mean()))
big=[(i,TRIS[i][0],round(me[i],3)) for i in np.argsort(-me)[:10]]
print("largest tris:",big)
print("face ids of largest:",[TRIS[i][0] for i in np.argsort(-me)[:10]])
# contact faces from the adjudication
d=json.load(open("../STAGE6B_R1C_PENETRATION_ADJUDICATION.json",encoding="utf-8"))
for cid,r in d["cases"].items():
    f=r["adjudication_focus"]; m=r["max_pair"]
    for lbl,ff in (("focus",(f["face_a"],f["face_b"])),("max",(m["face_a"],m["face_b"]))):
        for x in ff:
            p=POLY[x]; vs=[V0[v] for v in p]
            es=[ (vs[i]-vs[(i+1)%len(p)]).length*1000 for i in range(len(p)) ]
            ar=R.face_area(V0,p)*1e6
            print("%-12s %-5s face %-5d nverts=%d edges=%s area=%.2f mm2"%(cid,lbl,x,len(p),[round(e,3) for e in es],ar))
