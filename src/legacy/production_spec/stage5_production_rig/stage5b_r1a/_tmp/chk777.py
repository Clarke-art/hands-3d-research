import bpy, sys, os, json
sys.path.append(r"<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1a/scripts")
import r1a_common as C
from mathutils import Vector
TOP = r"<HANDS_ROOT>/production_spec/stage5_production_rig"
R1A = os.path.join(TOP,"stage5b_r1a","RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend")
R1  = os.path.join(TOP,"stage5b_r1","RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend")
bA = C.load_weights(R1A); WA=bA["W"]; NV=bA["NV"]
b1 = C.load_weights(R1);  W1=b1["W"]
ref = C.load_reference(TOP); V0=ref["V0"]
for v in (777,776,778,292,1459):
    print("v%-5d own=%-7s world=%s"%(v, ref["OWN_V"][v], [round(x*1000,2) for x in V0[v]]))
    print("      R1 :", {k:round(x,6) for k,x in sorted(W1[v].items(),key=lambda kv:-kv[1])})
    print("      R1A:", {k:round(x,6) for k,x in sorted(WA[v].items(),key=lambda kv:-kv[1])})
# how many CENTRAL_PALM vertices carry THUMB_CMC and their distribution
TF=C.thumb_frame(ref); TAU=ref["med_edge"]; RG=C.build_regions(ref,TF,TAU,*C.thumb_radii(ref,TF))
CP=RG["CENTRAL_PALM"]
cmc=[(i,WA[i].get("THUMB_CMC_R",0.0)) for i in sorted(CP) if WA[i].get("THUMB_CMC_R",0.0)>0]
cmc.sort(key=lambda t:-t[1])
print("\nCENTRAL_PALM verts with THUMB_CMC>0 :", len(cmc), " sum=", round(sum(w for _,w in cmc),6))
print("top10:", [(i,round(w,6)) for i,w in cmc[:10]])
print("count>0.5:", sum(1 for _,w in cmc if w>0.5), " count==1.0:", sum(1 for _,w in cmc if w>=0.999999))
