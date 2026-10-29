import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import s6br1b_common as K
ctx = K.B.build_context(); ref = ctx["ref"]; EDGES = ref["EDGES"]; V0 = ref["V0"]
own = ctx["own_r1a"]
probe = K.load_probe_sets()
tau = ref["med_edge"]
print("median edge mm = %.4f" % tau)
req84 = sorted(set([a for _k,a,b in probe["CLASS_B"]] + [b for _k,a,b in probe["CLASS_B"]] +
                   [a for _k,a,b in probe["CLASS_A"]] + [b for _k,a,b in probe["CLASS_A"]]))
bndset = set()
for thr in (0.0, tau, 1.5*tau, 2*tau, 3*tau, 4*tau, 5*tau):
    P = K.r2_partition(ctx, ref, margin_threshold_mm=thr if thr>0 else 1e-9)
    part = P["partition"]
    C = K.build_corrected_ownership(ctx, ref, part, probe)
    corr = C["corrected"]
    mixedB = sum(1 for _k,a,b in probe["CLASS_B"] if corr[a]!=corr[b])
    bnd = [k for k,(a,b) in enumerate(EDGES) if corr[a]!=corr[b] and {corr[a],corr[b]}=={"THUMB","INDEX"}]
    bndset.add(len(bnd))
    m84 = min(P["margin_mm"][v] for v in req84)
    nf = sum(1 for i in range(ref["NV"]) if own[i]!=corr[i])
    print("thr=%7.3f  ambig=%5d  changed=%4d  mixed_classB=%d  R2boundary_edges=%3d  min_margin_of_84=%.2f  changed84=%d"
          % (thr, P["ambiguous_margin_vertices"], nf, mixedB, len(bnd), m84,
             sum(1 for v in req84 if own[v]!=corr[v])))
