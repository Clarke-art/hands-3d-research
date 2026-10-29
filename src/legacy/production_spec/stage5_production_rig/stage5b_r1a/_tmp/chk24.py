import bpy, sys, os, json
sys.path.append(r"<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1a/scripts")
import r1a_common as C
TOP = r"<HANDS_ROOT>/production_spec/stage5_production_rig"
R1A = os.path.join(TOP,"stage5b_r1a","RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend")
bA = C.load_weights(R1A); WA=bA["W"]; NV=bA["NV"]
ref = C.load_reference(TOP); V0=ref["V0"]
TF=C.thumb_frame(ref); TAU=ref["med_edge"]; RG=C.build_regions(ref,TF,TAU,*C.thumb_radii(ref,TF))
META=RG["THUMB_FIRST_METACARPAL"]; THENAR=RG["THENAR_BASE"]
DIST=RG["THUMB_DISTAL"]; PROX=RG["THUMB_PROXIMAL"]; FOLD=RG["THUMB_BASE_FOLD"]; WEB=RG["FIRST_WEB"]; PALM=RG["CENTRAL_PALM"]
union=META|THENAR
outside=[i for i in range(NV) if WA[i].get("THUMB_CMC_R",0.0)>0 and i not in union]
none=[i for i in outside if i not in (DIST|PROX|FOLD|WEB|PALM)]
print("outside total:",len(outside)," not in any R1A region:",len(none))
from collections import Counter
print("own breakdown of the 24:", Counter(ref["OWN_V"][i] for i in none))
print("their THUMB_CMC weights:", sorted(round(WA[i]["THUMB_CMC_R"],9) for i in none)[-8:])
print("max:", max(WA[i]["THUMB_CMC_R"] for i in none) if none else 0)
print("sample verts:", [(i, ref["OWN_V"][i], round(WA[i]["THUMB_CMC_R"],9)) for i in sorted(none)[:8]])
# region breakdown of the 'outside' CMC mass, verified
for name,reg in (("THUMB_DISTAL",DIST),("THUMB_PROXIMAL",PROX),("THUMB_BASE_FOLD",FOLD),("FIRST_WEB",WEB),("CENTRAL_PALM",PALM)):
    ids=[i for i in outside if i in reg]
    print("%-22s n=%-4d sum=%.6f"%(name,len(ids),sum(WA[i]["THUMB_CMC_R"] for i in ids)))
print()
for v in (777,):
    print("v%d own=%s arc=%.4f dThumb=%.4f W=%s"%(v,ref["OWN_V"][v],TF["arc_thumb_mm"][v],ref["dchain"][v]["THUMB"],{k:round(x,6) for k,x in sorted(WA[v].items(),key=lambda kv:-kv[1])}))
    print("   in PROXIMAL:",v in PROX," in META:",v in META," in THENAR:",v in THENAR," R_TUBE=%.4f"%(RG["r_tube"]))
top=sorted(outside,key=lambda i:-WA[i]["THUMB_CMC_R"])[:8]
for v in top:
    print("  top v%-5d own=%-7s CMC=%.6f region=%s"%(v,ref["OWN_V"][v],WA[v]["THUMB_CMC_R"],
      "PROX" if v in PROX else "PALM" if v in PALM else "META" if v in META else "THENAR" if v in THENAR else "-"))
