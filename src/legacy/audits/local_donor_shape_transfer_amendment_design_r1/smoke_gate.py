import sys
sys.dont_write_bytecode=True
from geometric_gate import *
D=read(OUT/'TEMP_BIND_SMOKE_COORDINATES_R1.json')['states'];result={}
for cid in ['BIND','IDX_MCP_15','IDX_MCP_30','IDX_MCP_45']:
 current=np.array(D['CURRENT'][cid]);candidate=np.array(D['FORMAL_CANDIDATE'][cid]);z=assess(candidate,current,IDS)
 sourceangles=angles(current);candidateangles=angles(candidate);roi_edges=[ei for ei,ff in enumerate(EF) if set(ff)&set(R['faces'])]
 z.update({'case':cid,'local_ROI_max_dihedral_deg':float(max(candidateangles[roi_edges])),'current_ROI_max_dihedral_deg':float(max(sourceangles[roi_edges])),'ROI_max_displacement_vs_candidate_BIND_mm':float(np.max(np.linalg.norm(candidate[R['vertices']]-np.array(D['FORMAL_CANDIDATE']['BIND'])[R['vertices']],axis=1))),'limited_local_shape_gate_only':True,'not_Full42':True,'not_Stage6A_qualification':True,'frozen9_crossings_not_classified':True,'render_review':'PENDING'})
 result[cid]=z;print('LIMITED LOCAL SMOKE',cid,z['status'],'newcontact',len(z['contact_no_regression']['new_true_contact_components']),'new boundary',len(z['boundary']['new_boundary_sharp_folds']),flush=True)
dump('FORMAL_DONOR_TRANSFER_LIMITED_IDX_SMOKE_R1.json',{'status':'PASS' if all(z['status']=='PASS' for z in result.values()) else 'FAIL_CLOSED_DONOR_TRANSFER_CONTOUR_GATE','states':result,'scope':'BIND and3 isolated index MCP temporary smoke; no Full42 requalification, no cap/ownership/weight authority recompute.'})
