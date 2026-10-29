import sys
sys.dont_write_bytecode=True
from solve import *
dep=5;ids=sorted(sets[dep]);ix,lap,full,H,W,lc,fc=operators(ids);bc,_=exact(V,ids);records=[]
# Mechanical motion-path hypotheses, not new shape targets or clearances.
# The contact active set on2182/3330 suggests separating the two branches
# in the dorsal-normal direction before tangent continuation.
for name,anchors in [('ROOT_EDGE_OUTWARD',{79:.15,955:.15}),('ROOT_EDGE_INWARD',{79:-.15,955:-.15}),('CREASE_APEX_OUTWARD',{3332:.15,3340:.15}),('CREASE_APEX_INWARD',{3332:-.15,3340:-.15})]:
 diag=np.zeros(len(ids));rhs=np.zeros(len(ids))
 for i,h in anchors.items():diag[ix[i]]=20;rhs[ix[i]]=20*h
 dd=np.linalg.solve(H+np.diag(diag),rhs);v=V.copy();v[ids]+=dd[:,None]*n;st=orientation(v,ids);cc,num=exact(v,ids);new=sorted(set(cc)-set(bc));continuous,ct=ccd(V,v,ids,set(bc));good=not new and continuous and not any(st[k] for k in ['new_reversed_faces','new_degenerate_faces','new_bowtie_faces'])
 records.append({'name':name,'native_anchor_vertex_offsets_in_dorsal_normal_mm':anchors,'support_depth':dep,'seed_is_target_or_clearance':False,'max_displacement_mm':float(np.linalg.norm(v-V,axis=1).max()),'orientation':st,'new_pair_ids':[list(k) for k in new],'continuous_motion':ct,'mechanically_feasible_motion_seed':good,'world_mm':v.tolist() if good else None,'coordinate_design_not_Human_candidate':True})
 print(name,good,'newpairs',new,'ccd',continuous,flush=True)
dump('NORMAL_FIRST_CONTINUATION_MECHANICAL_PROBE_R3.json',{'scope':'Four directional path hypotheses based on the new2182/3330 active contact, not a support expansion or another target family. None is a selectable geometry candidate.','motion_amplitude_is_anatomy_clearance':False,'probes':records})
