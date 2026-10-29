import os, sys, json
import bpy
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
sys.path.append(os.path.join(HERE,"..","..","..","stage6_deformation","stage6b_r1b","scripts"))
import s6br1b_common as K
ctx=K.B.build_context(); ref=ctx["ref"]; NV=ref["NV"]; EDGES=ref["EDGES"]
probe=K.load_probe_sets(); PART=K.r2_partition(ctx,ref)
CORR=K.build_corrected_ownership(ctx,ref,PART["partition"],probe)["corrected"]
CAND=os.path.join(HERE,"..","RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1D.blend")
def flips(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob=bpy.data.objects[K.MESH_OBJ]
    W=K.read_weights(ob,NV)
    out=[]
    for a,b in EDGES:
        wa,wb=W[a],W[b]
        hi_a=set(g for g,v in wa.items() if v>=0.95)
        lo_b=set(g for g in wa if wb.get(g,0.0)<=0.05)
        hi_b=set(g for g,v in wb.items() if v>=0.95)
        lo_a=set(g for g in wb if wa.get(g,0.0)<=0.05)
        L=hi_a&lo_b; R=hi_b&lo_a
        if L and R and L!=R:
            out.append((a,b,sorted(L),sorted(R)))
    return out,W
f1,W1=flips(K.R1B_MASTER)
f2,W2=flips(CAND)
s1=set((a,b) for a,b,_,_ in f1); s2=set((a,b) for a,b,_,_ in f2)
print("R1B flips = %d ; R1D flips = %d"%(len(f1),len(f2)))
print("R1B edges:",sorted(s1))
print("R1D edges:",sorted(s2))
print("FIXED (in R1B not in R1D):",sorted(s1-s2))
print("NEW  (in R1D not in R1B):",sorted(s2-s1))
for a,b,L,R in f2:
    print("  R1D flip %d-%d L=%s R=%s | Wa=%s Wb=%s"%(
        a,b,L,R,{g:round(v,3) for g,v in sorted(W2[a].items())},{g:round(v,3) for g,v in sorted(W2[b].items())}))
