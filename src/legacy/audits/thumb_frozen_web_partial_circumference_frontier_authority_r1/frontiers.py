import sys,math
sys.dont_write_bytecode=True
from local_data import *
STACK=read(OUT/'THUMB_PROXIMAL_RING_STACK_R1.json');RINGS=STACK['rings'];SEQ=[r['vertex_sequence'] for r in RINGS];CORR=read(OUT/'THUMB_RING_TO_RING_CORRESPONDENCE.json')['pairs'];ALLS=set(STACK['vertex_set']['vertex_ids']);STRIP=set(STACK['face_ids'])
def edge(a,b):return EF[tuple(sorted((a,b)))]
def cyclic_arcs(indices,n=16):
    # Every minimum-cardinality cyclic arc containing seeds; no angular threshold.
    if not indices:return []
    arcs=[]
    for start in range(n):
        for length in range(1,n+1):
            seq=[(start+k)%n for k in range(length)]
            if set(indices)<=set(seq):arcs.append(seq);break
    m=min(map(len,arcs));return [x for x in arcs if len(x)==m]
seedi=sorted({i for r in RINGS for i in r['known_shared_indices']});arcs=cyclic_arcs(seedi);assert len(arcs)==1;cols=arcs[0];assert cols==[4,5,6]
def band_faces(j,columns):
    rows=[]
    for c,d in zip(columns,columns[1:]):
        target={SEQ[j][c],SEQ[j][d],SEQ[j+1][c],SEQ[j+1][d]};f=[fi for fi in CORR[j]['face_ids'] if set(F[fi])==target];assert len(f)==1;rows+=f
    return rows
def candidate(name,js,columns):
    ids={SEQ[j][c] for j in js for c in columns};faces=sorted({fi for j,k in zip(js,js[1:]) if k==j+1 for fi in band_faces(j,columns)})
    left=[edge(SEQ[j][columns[0]],SEQ[k][columns[0]]) for j,k in zip(js,js[1:])];right=[edge(SEQ[j][columns[-1]],SEQ[k][columns[-1]]) for j,k in zip(js,js[1:])]
    # Removal from thumb distal tube is tested only as a compatibility gate, never selector.
    whole=max((set(r['core_including_ring']['vertex_ids']) for r in RAW),key=len)
    rest=whole-ids;cs=components(rest);anchorcomp=next((c for c in cs if 284 in c),set());complement=ALLS-ids
    return {'name':name,'status':'DIAGNOSTIC_NOT_AUTHORITY','ring_indices':js,'circumferential_columns':columns,'shared_vertex_ids':sorted(ids),'shared_face_ids':faces,'role_extension_ids':sorted(ids-WEB),'role_extension_vertex_count':len(ids-WEB),'role_support_face_count':len(faces),'left_frontier_edge_ids':left,'right_frontier_edge_ids':right,'distal_cut_edge_ids':[edge(SEQ[js[0]][a],SEQ[js[0]][b]) for a,b in zip(columns,columns[1:])],'proximal_cut_edge_ids':[edge(SEQ[js[-1]][a],SEQ[js[-1]][b]) for a,b in zip(columns,columns[1:])],'distal_termination':'UNRESOLVED_ANALYSIS_CROP_NOT_ANATOMICAL_STOP','proximal_termination':'UNRESOLVED_ANALYSIS_CROP_NOT_ANATOMICAL_STOP','surface_audit':surface(ids),'contains_all_four_seeds':SEEDS<=ids,'whole_ring_shared':any(set(SEQ[j])<=ids for j in js),'seed_only_complement_promoted_exclusive':False,'cap_conflict_ids':sorted(ids&CAP),'nail_conflict_ids':sorted(ids&NAILS['thumb']),'thumb_exclusive_complement_role_ids':None,'remaining_stack_vertex_ids':sorted(complement),'remaining_stack_count':len(complement),'complement_cap_nail_continuity':{'all_fixed_thumb_anchors_in_tip_component':CAP|NAILS['thumb']<=(anchorcomp),'all_remaining_stack_vertices_in_tip_component':complement<=anchorcomp,'remaining_component_sizes':[len(c) for c in cs],'test_does_not_grant_exclusivity':True}}
f1=candidate('F1_MINIMUM_SEED_CONNECTED_FACE_PATCH',[0,1],cols)
f3=candidate('F3_TOPOLOGICAL_COLUMN_STRIP_THROUGH_LOCAL_STACK',list(range(9)),cols)
# Width sensitivity: neighboring real face columns, never silently accepted as support.
wideL=candidate('DIAGNOSTIC_ONE_FACE_COLUMN_WIDER_LEFT',list(range(9)),[3,4,5,6]);wideR=candidate('DIAGNOSTIC_ONE_FACE_COLUMN_WIDER_RIGHT',list(range(9)),[4,5,6,7])
dump('LOCAL_DIAGNOSTIC_STRIP_SETS.json',{'F1':f1,'F3':f3,'wider_left':wideL,'wider_right':wideR})

def face_normals(coords):
    out=[]
    for vs in F:
        pp=coords[vs];n=np.sum(np.cross(pp,np.roll(pp,-1,axis=0)),axis=0);out.append(unit(n) if np.linalg.norm(n)>1e-15 else n)
    return np.array(out)
def delta_angle(a,b):return float((b-a+180)%360-180)
normal_evidence={};longitudinal={}
for state,P in [('NATIVE',N),('RSSF',V)]:
    FN=face_normals(P);centers=np.array([P[seq].mean(0) for seq in SEQ]);nailcue=unit(FN[NAILF['thumb']].sum(0))
    if state=='RSSF':indexroot=INDEX_CHAIN[0]
    else:
        idx=read(ROOT/'production_spec/stage5_production_rig/stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1/NATIVE_INDEX_ANCHOR_SET.json');indexroot=np.array(idx['native_direction_support']['joint_world_m']['MCP'])
    webcontext=P[sorted(WEB-SEEDS)].mean(0);rs=[]
    for j,seq in enumerate(SEQ):
        axis=unit(centers[max(j-1,0)]-centers[min(j+1,8)])
        dorsal=unit(nailcue-axis*(nailcue@axis));side=np.cross(axis,dorsal)
        towardI=indexroot-centers[j];towardI=unit(towardI-axis*(towardI@axis))
        towardW=webcontext-centers[j];towardW=unit(towardW-axis*(towardW@axis))
        vn=np.array([unit(FN[VF[v]].sum(0)) for v in seq]);off=P[seq]-centers[j];angles=np.degrees(np.arctan2(off@side,off@dorsal))%360
        dotsI=vn@towardI;dotsW=vn@towardW
        turning=[float(np.degrees(np.arccos(np.clip(vn[c]@vn[(c+1)%16],-1,1)))) for c in range(16)]
        crossingsI=[c for c in range(16) if dotsI[c]*dotsI[(c+1)%16]<0];crossingsW=[c for c in range(16) if dotsW[c]*dotsW[(c+1)%16]<0]
        ang=angles[cols];gaps=np.diff(sorted(ang.tolist())+[min(ang)+360]);width=float(360-max(gaps));centroid=float(np.degrees(np.arctan2(np.sin(np.radians(ang)).mean(),np.cos(np.radians(ang)).mean()))%360)
        rs.append({'ring_id':RINGS[j]['ring_id'],'center_world_m':centers[j].tolist(),'longitudinal_axis':axis.tolist(),'nail_dorsal_projected_cue':dorsal.tolist(),'index_root_facing_projected_direction':towardI.tolist(),'other17_web_centroid_facing_projected_direction':towardW.tolist(),'vertices':[{'vertex_id':v,'column':c,'normal_world':vn[c].tolist(),'angle_deg':float(angles[c]),'normal_dot_index_facing':float(dotsI[c]),'normal_dot_web_facing':float(dotsW[c]),'normal_turn_to_next_vertex_deg':turning[c],'known_shared':v in WEB} for c,v in enumerate(seq)],'F2_auxiliary_sign_crossing_edges':{'index_facing':[edge(seq[c],seq[(c+1)%16]) for c in crossingsI],'web_facing':[edge(seq[c],seq[(c+1)%16]) for c in crossingsW]},'F2_largest_neighbor_normal_turn_edges':[edge(seq[c],seq[(c+1)%16]) for c in np.argsort(turning)[-2:][::-1]],'topology_strip_descriptor':{'columns':cols,'centroid_angle_deg':centroid,'angular_width_deg':width,'left_angle_deg':float(angles[cols[0]]),'right_angle_deg':float(angles[cols[-1]]),'known_seeds_index_dot_values':[float(dotsI[c]) for c,v in enumerate(seq) if v in SEEDS],'known_seeds_web_dot_values':[float(dotsW[c]) for c,v in enumerate(seq) if v in SEEDS]}})
    deltas=[]
    for a,b in zip(rs,rs[1:]):
        x=a['topology_strip_descriptor'];y=b['topology_strip_descriptor'];deltas.append({'rings':[a['ring_id'],b['ring_id']],'centroid_angle_delta_deg':delta_angle(x['centroid_angle_deg'],y['centroid_angle_deg']),'width_delta_deg':y['angular_width_deg']-x['angular_width_deg'],'left_angle_delta_deg':delta_angle(x['left_angle_deg'],y['left_angle_deg']),'right_angle_delta_deg':delta_angle(x['right_angle_deg'],y['right_angle_deg'])})
    normal_evidence[state]=rs;longitudinal[state]={'rings':[{k:r[k] for k in ['ring_id','topology_strip_descriptor']} for r in rs],'consecutive_deltas':deltas,'max_abs_centroid_jump_deg':max(abs(x['centroid_angle_delta_deg']) for x in deltas),'constant_topological_columns':True,'exact_180_flip_detected':any(abs(x['centroid_angle_delta_deg'])>179.999 for x in deltas),'threshold_grants_authority':False}
dump('THUMB_LOCAL_SHARED_SECTOR_EVIDENCE_R2.json',{'status':'AUXILIARY_GEOMETRIC_EVIDENCE_ONLY','states':normal_evidence,'F2_rule':'Describe normal dot products toward independent INDEX root and other17 frozen web centroid, sign crossings and actual neighboring-normal turning extrema. No score threshold decides ownership.','angular_threshold_used_for_membership':False,'native_or_RSSF_proximity_winner_used':False,'limitation':'Web-facing and index-facing cues are not equivalent; normal transition is auxiliary and may not locate an anatomical sector frontier.'})

# Walk exactly two face rows beyond each crop endpoint, using opposite edges in actual quads.
# This tests termination rather than extending anatomy or exploring the palm.
ends={}
for name,j,inside_j in [('DISTAL',0,0),('PROXIMAL',8,7)]:
    sideedges=[edge(SEQ[j][a],SEQ[j][b]) for a,b in zip(cols,cols[1:])];inside=set(CORR[inside_j]['face_ids']);current=sideedges;lastfaces=inside;hops=[]
    for hop in [1,2]:
        nextedges=[];faces=[];records=[]
        for e in current:
            ff=sorted(set(EFS[e])-lastfaces)
            rec={'incoming_edge':e,'outward_face_ids':ff,'unique_quad_continuation':False}
            if len(ff)==1 and len(F[ff[0]])==4:
                fi=ff[0];vs=F[fi];opp=[edge(a,b) for a,b in zip(vs,vs[1:]+vs[:1]) if not set((a,b))&set(E[e])];assert len(opp)==1
                rec.update({'unique_quad_continuation':True,'opposite_outward_edge':opp[0],'face_vertex_ids':vs});nextedges+=opp;faces.append(fi)
            records.append(rec)
        ids={v for fi in faces for v in F[fi]};newvs={v for e in nextedges for v in E[e]}
        hops.append({'hop':hop,'records':records,'face_ids':sorted(set(faces)),'outward_vertex_ids':sorted(newvs),'cap_overlap':sorted(ids&CAP),'nail_overlap':sorted(ids&NAILS['thumb']),'frozen_web_overlap':sorted(ids&WEB),'outward_edge_support_continues':len(nextedges)==len(current),'outward_vertex_valences':{str(v):len(ADJ[v]) for v in newvs}})
        lastfaces=set(faces);current=nextedges
        if not nextedges:break
    ends[name]={'endpoint_ring':RINGS[j]['ring_id'],'termination_authority':'UNRESOLVED','two_face_row_continuation_probe':hops,'scope_limited_to_two_face_rows':True,'warning':'A topology stop/pole, if present, is not by itself a biological shared-role stop; no graph extension applied.'}
dump('DISTAL_PROXIMAL_TERMINATION_AUDIT.json',ends)

comparison=[]
for j,(a,b) in enumerate(zip(normal_evidence['NATIVE'],normal_evidence['RSSF'])):
    comparison.append({'ring_id':a['ring_id'],'same_sector_vertex_ids':True,'same_left_right_edge_correspondence':True,'width_native_deg':a['topology_strip_descriptor']['angular_width_deg'],'width_RSSF_deg':b['topology_strip_descriptor']['angular_width_deg'],'F2_index_sign_edges_native':a['F2_auxiliary_sign_crossing_edges']['index_facing'],'F2_index_sign_edges_RSSF':b['F2_auxiliary_sign_crossing_edges']['index_facing'],'F2_web_sign_edges_native':a['F2_auxiliary_sign_crossing_edges']['web_facing'],'F2_web_sign_edges_RSSF':b['F2_auxiliary_sign_crossing_edges']['web_facing']})
dump('THUMB_SHARED_SECTOR_LONGITUDINAL_CONTINUITY_AUDIT.json',{'status':'DIAGNOSTIC_TOPOLOGY_CONTINUOUS_ENDPOINT_AUTHORITY_UNRESOLVED','F3_single_arc_per_ring':True,'F3_frontier_correspondence_continuous':True,'F3_native_RSSF_membership_identical':True,'states':longitudinal,'native_RSSF_comparison':comparison,'F1_vs_F3':{'common_rings':[0,1],'same_frontier_columns_there':True,'different_longitudinal_domains':True,'F1_not_evidence_for_disappearance_on_R02':True},'final_longitudinal_frontier_defined':False,'arbitrary_normal_or_angle_threshold':False})
dump('THUMB_SHARED_SECTOR_FRONTIER_CANDIDATE_AUDIT.json',{'status':'FAIL_CLOSED','F1':{**f1,'generator':'Minimum contiguous circumferential columns covering frozen shared seeds; minimal face-connected quad patch across only seed-bearing rings. Unique2-face seed connector; NOT anatomical termination.','stop_condition_clear_exclusive_region':'NOT_ESTABLISHED; seed hull boundary is insufficient','required_extension_foundation':'Seeds constrain inclusion, not where shared influence ends.'},'F2':{'status':'AUXILIARY_ONLY_NO_UNIQUE_FRONTIER','evidence':'THUMB_LOCAL_SHARED_SECTOR_EVIDENCE_R2.json','rejects_standalone_normal_ownership':True,'hard_conflict_policy':'No hard rejection based on normal direction alone; cue disagreement and repose changes documented; cannot assert that absence of a veto certifies F4.'},'F3':{**f3,'generator':'Parallel transport columns4..6 through exact face strips. Mapping itself is unique; applying shared role for all9rings is a hypothesis, not implied by absence/presence of seeds.','first_web_other17_projection':'Only exact face incidence is considered, not nearest-angle/nearest-chain projection. No independent boundary from outside seeds is inferred.'},'F4':{'status':'NOT_FORMED','why':'F1 and F3 agree on transverse columns on R00/R01 but do not supply the same longitudinal extent. Neither defines a justified distal/proximal stop. F2 is auxiliary and cannot manufacture stop authority.','candidate_vertex_ids':None},'width_sensitivity':{'one_face_column_wider_left':wideL,'one_face_column_wider_right':wideR,'purpose':'Both wider alternatives use full faces and continuous topology. Check whether geometric evidence uniquely supports choosing narrower width; do not promote a widest/connected option.'},'final_frontier':{'left_edge_ids':None,'right_edge_ids':None,'distal_termination':None,'proximal_termination':None,'shared_face_strip_ids':None,'thumb_exclusive_complement_ids':None},'single_remaining_local_blocker':'THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY','no_role_extension_emitted':True})
role_rows=[]
for j,seq in enumerate(SEQ):
    for c,v in enumerate(seq):
        role_rows.append({'vertex_id':v,'ring_id':RINGS[j]['ring_id'],'circumferential_index':c,'role':'SHARED_NEUTRAL' if v in WEB else 'UNRESOLVED','evidence_basis':'Frozen FIRST_WEB_21 known membership' if v in WEB else 'No final frontier or exclusive stop authority; not classified by complement alone','F1_diagnostic_membership':v in f1['shared_vertex_ids'],'F3_diagnostic_membership':v in f3['shared_vertex_ids'],'hard_source':False if v in WEB else None})
dump('THUMB_PARTIAL_CIRCUMFERENCE_ROLE_MAP_R1.json',{'status':'UNRESOLVED','scope':'Exactly9 existing thumb MCP/IP closed rings,144vertices','role_enum':['THUMB_EXCLUSIVE','SHARED_NEUTRAL','UNRESOLVED'],'vertices':role_rows,'counts':dict(Counter(r['role'] for r in role_rows)),'per_ring_state':{r['ring_id']:{'required_A_B_C_state':None,'state_status':'UNRESOLVED','known_shared_seed_count':len(r['known_shared_vertices']),'F3_diagnostic_state':'PARTIAL_SHARED_SECTOR','F3_state_is_final_authority':False} for r in RINGS},'why_no_A_B_C_final_assignment':'Neither no seed nor a valid connected strip proves exclusive/shared termination. No whole-ring shared and no seed-only complementary exclusive assignment.','FIRST_WEB_membership_changed':False,'role_extension_created':False})
summary={'ring_count':9,'ring_stack_vertices':144,'ring_stack_faces':128,'F1_shared_vertices':len(f1['shared_vertex_ids']),'F1_extension_vertices':f1['role_extension_vertex_count'],'F1_faces':len(f1['shared_face_ids']),'F3_shared_vertices':len(f3['shared_vertex_ids']),'F3_extension_vertices':f3['role_extension_vertex_count'],'F3_faces':len(f3['shared_face_ids']),'F3_left_edges':len(f3['left_frontier_edge_ids']),'F3_right_edges':len(f3['right_frontier_edge_ids']),'F3_complement_count':f3['remaining_stack_count'],'F3_surface_supported':f3['surface_audit']['surface_supported'],'F3_wire_edges':len(f3['surface_audit']['wire_only_edge_ids']),'cap_nail_continuity':f3['complement_cap_nail_continuity'],'F2_seed_cue_values':{state:[{'ring':r['ring_id'],'webdot':r['topology_strip_descriptor']['known_seeds_web_dot_values'],'indexdot':r['topology_strip_descriptor']['known_seeds_index_dot_values']} for r in rs[:2]] for state,rs in normal_evidence.items()},'max_centroid_jumps':{k:v['max_abs_centroid_jump_deg'] for k,v in longitudinal.items()},'endpoint_continuation':{k:[{'hop':h['hop'],'continues':h['outward_edge_support_continues'],'cap':h['cap_overlap'],'nail':h['nail_overlap']} for h in v['two_face_row_continuation_probe']] for k,v in ends.items()},'remaining_blocker':'THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY'}
dump('LOCAL_STATIC_SUMMARY.json',summary);print(json.dumps(summary,indent=2))
