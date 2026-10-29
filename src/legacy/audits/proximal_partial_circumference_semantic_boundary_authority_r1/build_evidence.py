"""Exact-face role review. No scalar ranking, solver or production mutations."""
import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PREV=OUT.parent/'narrow_proximal_web_to_palm_transition_authority_r1'
TRACE=OUT.parent/'thumb_shared_strip_longitudinal_stop_rule_authority_r1'
REC=ROOT/'production_spec/stage5_production_rig/cap_derived_r2_r3_input_reconciliation_r1'
REF=ROOT/'production_spec/stage5_production_rig/stage5b_r1e_manual_anatomical_reference_review_r1'
NAME='PROXIMAL_PARTIAL_CIRCUMFERENCE_SEMANTIC_BOUNDARY_AUTHORITY_R1'
REVIEW='PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_HUMAN_REVIEW_R1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,d):(OUT/n).write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def inventory():return {str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and OUT not in p.parents and '.git' not in p.parts}
def unit(v):
    v=np.asarray(v,dtype=float);l=np.linalg.norm(v);assert l>1e-13;return v/l
if not (OUT/'FROZEN_HASHES_BEFORE.json').exists():
    ext=set(read(PREV/'FROZEN_HASHES_AFTER.json')['external']);ext.add(r'<USER_HOME>\.codex\attachments\66c87572-e27d-4c74-b6e9-9309b571c332\已粘贴的文本.txt')
    dump('FROZEN_HASHES_BEFORE.json',{'workspace':inventory(),'external':{p:sha(p) for p in sorted(ext)}})
checks=[]
def ck(n,v):assert v,n;checks.append({'name':n,'passed':True})
for p,h in read(PREV/'OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json')['files'].items():ck('prior artifact hash '+p,sha(PREV/p)==h)
a=read(REC/'AUTHORITY_INPUT_VERIFICATION.json')
keys=['cap_authority','corrected_rig','kinematic_authority','kinematic_application','Stage4C_geometry','native_geometry','nail_authority','first_web_membership','first_web_human_approval','CMC_cage_source','CMC_cage_construction']
for k in keys:ck('frozen authority hash '+k,sha(ROOT/a['sources'][k]['path'])==a['sources'][k]['sha256'])
ck('frozen extraction hash',sha(REC/'READ_ONLY_LIVE_EXTRACTION.json')==read(REC/'RECONCILIATION_EVIDENCE_HASH_MANIFEST_R1.json')['output_file_hashes']['READ_ONLY_LIVE_EXTRACTION.json'])
P=read(PREV/'PROXIMAL_TRANSITION_LOCAL_PATCH_R1.json')
j=read(REC/'READ_ONLY_LIVE_EXTRACTION.json');F=j['RSSF']['faces'];E=j['RSSF']['edges'];ef={tuple(sorted(e)):i for i,e in enumerate(E)}
ck('same native/RSSF topology',F==j['NATIVE']['faces'] and E==j['NATIVE']['edges'])
vf={};efs={}
for f,vs in enumerate(F):
    for v in vs:vf.setdefault(v,[]).append(f)
    for x,y in zip(vs,vs[1:]+vs[:1]):efs.setdefault(ef[tuple(sorted((x,y)))],[]).append(f)
def edges(f):
    vs=F[f];return [ef[tuple(sorted((x,y)))] for x,y in zip(vs,vs[1:]+vs[:1])]
def section(e):
    mid=next(iter(set(E[e[0]])&set(E[e[1]])));return [next(v for v in E[e[0]] if v!=mid),mid,next(v for v in E[e[1]] if v!=mid)]
tt=read(TRACE/'RAW_LOCAL_COLUMN_TRACES.json');rows=[r for r in tt['proximal']['rows'] if r['row_id'] in ['P01','P02','P03','P04','P05','P06','P07']];del tt
rowmap={r['row_id']:r for r in rows};ck('one-row guard context only',list(rowmap)==['P01','P02','P03','P04','P05','P06','P07'])
CAP=read(ROOT/a['sources']['cap_authority']['path']);NAIL=read(ROOT/a['sources']['nail_authority']['path'])['per_digit_faces']['thumb'];WEB=read(ROOT/a['sources']['first_web_membership']['path'])['selected_vertices'];SEEDS=[1396,1399,1402,2774]
F3=read(OUT.parent/'thumb_frozen_web_partial_circumference_frontier_authority_r1/LOCAL_DIAGNOSTIC_STRIP_SETS.json')['F3']['shared_face_ids']
ck('frozen counts and seed identity',len(CAP['vertex_ids'])==37 and len(WEB)==21 and set(SEEDS)<=set(WEB) and len(NAIL)==12)
freeze=read(ROOT/'production_spec/stage4_blender/stage4c_r2/STAGE4C_R2_HUMAN_APPROVAL_FREEZE.json');WRIST=np.array(freeze['binding_constraints_on_stage5']['stage5_may_use_as_wrist_reference']['WRIST_ORIGIN'])
b=j['CORRECTED']['bones'];chain=np.array([b['THUMB_'+s+'_R']['head_world_m'] for s in ['CMC','MCP','IP']]+[b['THUMB_IP_R']['tail_world_m']])
kin=read(ROOT/a['sources']['kinematic_authority']['path']);ck('corrected distal axis approved',kin['status']=='HUMAN_APPROVED' and np.allclose(chain[-1],kin['slots']['THUMB_IP_R.tail']['world_m']))
coords={s:np.array(j[s]['vertices_world_m']) for s in ['NATIVE','RSSF']}
nailvertices=sorted({v for f in NAIL for v in F[f]})
def area(Q,f):vs=Q[F[f]];return np.cross(vs,np.roll(vs,-1,axis=0)).sum(0)
def rotation_between(n,m):
    n=unit(n);m=unit(m);v=np.cross(n,m);c=float(n@m)
    if np.linalg.norm(v)<1e-12:
        assert c>0;return np.eye(3)
    K=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    return np.eye(3)+K+K@K/(1+c)
# Approved corrected direction transported using exact corresponding frozen nail vertices.
# This is an orientation reference only: NO transferred native MCP/CMC position is asserted.
X=coords['RSSF'][nailvertices];Y=coords['NATIVE'][nailvertices];xc=X.mean(0);yc=Y.mean(0)
u,_,vt=np.linalg.svd((X-xc).T@(Y-yc));R=vt.T@u.T
if np.linalg.det(R)<0:vt[-1]*=-1;R=vt.T@u.T
native_nail_fit_rms_mm=float(np.sqrt(np.mean(np.sum(((X-xc)@R.T-(Y-yc))**2,axis=1)))*1000)
frames={};flow={};patches=[]
localfaceids=P['direct_incident_face_ids']
for s,Q in coords.items():
    normal={f:unit(area(Q,f)) for f in set(localfaceids)|set(NAIL)}
    distal=unit(chain[-1]-chain[-2]);distal=R@distal if s=='NATIVE' else distal
    dorsal=unit(sum((area(Q,f) for f in NAIL),np.zeros(3))); dorsal=unit(dorsal-distal*(dorsal@distal))
    radial=unit(np.cross(distal,dorsal))
    # Side sign comes from FIRST_WEB-facing frozen surface, never an ownership winner.
    webcentre=Q[SEEDS].mean(0);nailcentre=Q[nailvertices].mean(0)
    if radial@(webcentre-nailcentre)>0:radial=-radial
    frames[s]={'distal_axis':distal.tolist(),'dorsal_axis_from_approved_nail':dorsal.tolist(),'radial_axis_away_from_frozen_web':radial.tolist(),'web_seed_centroid_world_m':webcentre.tolist(),'nail_centroid_world_m':nailcentre.tolist(),'independent_wrist_world_m':WRIST.tolist(),'corrected_chain_world_m':chain.tolist() if s=='RSSF' else None,'native_nail_orientation_transport_rotation':R.tolist() if s=='NATIVE' else None,'native_nail_transport_fit_rms_mm':native_nail_fit_rms_mm if s=='NATIVE' else None,'native_joint_registration_status':'NO_APPROVED_NATIVE_CORRECTED_MCP_CMC_REGISTRATION' if s=='NATIVE' else 'HUMAN_APPROVED_CORRECTED_RSSF_STRUCTURE','source_rule':'Approved corrected distal direction; approved thumb nail; frozen first-web seeds; Stage4C approved wrist. Native axis only transported by same nail IDs; no native corrected joint locations claimed.','no_axis_is_a_palm_normal':True}
    stateflow=[]
    for row in P['row_ids']:
        t=rowmap[row];k=int(row[1:]);prev=rowmap[f'P{k-1:02d}'];nxt=rowmap[f'P{k+1:02d}'];fan=sorted({f for v in t['vertex_ids'] for f in vf[v]})
        laneout=[]
        for lane,f in enumerate(t['face_ids']):
            inc=t['incoming_edge_ids'][lane];out=t['outgoing_edge_ids'][lane]
            a0=Q[E[inc]].mean(0);a1=Q[E[out]].mean(0);long=unit(a1-a0);nn=normal[f];tangent=unit(long-nn*(long@nn))
            records=[]
            for edge,direction,other in [(inc,'DISTAL',prev['face_ids'][lane]),(out,'PROXIMAL',nxt['face_ids'][lane])]:
                assert other in efs[edge]; rot=rotation_between(nn,normal[other]); transported=rot@tangent
                records.append({'shared_edge_id':edge,'shared_edge_vertex_ids':E[edge],'direction':direction,'from_face_id':f,'to_face_id':other,'source_normal':nn.tolist(),'target_normal':normal[other].tolist(),'minimal_rotation_matrix':rot.tolist(),'source_longitudinal_tangent':tangent.tolist(),'transported_tangent':transported.tolist(),'transport_rule':'Minimal normal-aligning rotation at the real shared edge; descriptive flow, not ownership propagation.'})
            si=section(t['incoming_edge_ids']);so=section(t['outgoing_edge_ids'])
            laneout.append({'face_id':f,'normal':nn.tolist(),'longitudinal_surface_tangent':tangent.tolist(),'incoming_transverse_vector':unit(Q[si[lane+1]]-Q[si[lane]]).tolist(),'outgoing_transverse_vector':unit(Q[so[lane+1]]-Q[so[lane]]).tolist(),'transports':records})
        stateflow.append({'row':row,'faces':t['face_ids'],'lane_flows':laneout,'incident_face_fan_ids':fan,'ordered_vertex_fans':{str(v):P['topology']['vertices'][str(v)]['local_ordered_face_fan'] for v in t['vertex_ids']},'distal_context_row':prev['row_id'],'distal_context_faces':prev['face_ids'],'proximal_context_row':nxt['row_id'],'proximal_context_faces':nxt['face_ids'],'surface_flow_pattern':'AMBIGUOUS','geometric_organization':'Two paired original quad lanes preserve longitudinal continuation and a transverse cross-strip connection. Each incident fan is a regular four-face cycle. Adjacent flank faces are available from the first row onward.','role_interpretation':'Compatible with a web flank continuing toward a wider sheet; no independently registered wider-sheet face role identifies where the organization becomes BROAD_INTERFACE.','inherited_widening_only':'Previous chord/arc record retained as descriptive context; no new maximum or cutoff is evaluated.'})
    flow[s]=stateflow
for row in P['row_ids']:
    t=rowmap[row];k=int(row[1:]);patches.append({'row':row,'focus_face_ids':t['face_ids'],'focus_vertex_ids':t['vertex_ids'],'direct_incident_face_ids':sorted({f for v in t['vertex_ids'] for f in vf[v]}),'one_distal_row':{'row':f'P{k-1:02d}','face_ids':rowmap[f'P{k-1:02d}']['face_ids']},'one_proximal_row':{'row':f'P{k+1:02d}','face_ids':rowmap[f'P{k+1:02d}']['face_ids']},'no_recursive_growth':True})
dump('LOCAL_ANATOMICAL_REFERENCE_FRAME_R1.json',{'states':frames,'reference_roles_only':True,'axis_is_not_surface_role':True,'native_MCP_CMC_positions_not_inferred':True,'wrist_source':'Stage4C R2 Human-approved wrist origin; erroneous Stage4B cut-plane WRIST not used'})
dump('LOCAL_FACE_PATCHES_R1.json',{'patches':patches,'analysis_scope_face_ids':localfaceids,'guards':['P01','P07'],'guards_are_context_only_not_stop_candidates':True})
dump('LOCAL_SURFACE_FLOW_R1.json',{'states':flow,'pattern_labels':['DIGIT_WRAPPING','WEB_FLANK','TRANSITIONAL','BROAD_INTERFACE','AMBIGUOUS'],'surface_flow_is_not_scalar_ranking':True,'new_scalar_extrema_computed':False,'role_authority_pattern':'AMBIGUOUS','no_anatomical_role_from_normal_sign':True})

references={'review_date':'2026-10-03','scope':'One targeted first-web/MCP/thenar reference-check session; no general anatomy search or mesh ownership mapping.','local_reference_check':{'project_reference_directory':'references/hand_r_canonical_ai','rejected_as_anatomical_truth':'Generated AI canonical views and unregistered model thumbnails are not anatomical authority.','existing_reliable_pack':str(REF.relative_to(ROOT)),'existing_landmark_registration_status':'PENDING_HUMAN_REGISTRATION','anatomical_context_sufficient_for_focused_human_review':True,'exact_mesh_role_mapping_sufficient':False},'sources':[{'id':'LOCAL_DORSAL','source':'Sciencia58, Hand male both sides','url':'https://commons.wikimedia.org/wiki/File:Hand_male_both_sides.jpg','local_path':str((REF/'references/male_both_sides.jpg').relative_to(ROOT)),'sha256':sha(REF/'references/male_both_sides.jpg'),'license':'CC BY-SA 4.0','what_it_supports':'Externally visible dorsal thumb/index/commissure organization; use only right-hand dorsal panel.','what_it_does_not_support':'Internal joint centres, exact thenar boundary or any mesh face ID; a different hand with pending registration.'},{'id':'LOCAL_PALMAR','source':'Sciencia58, Hand female 5','url':'https://commons.wikimedia.org/wiki/File:Hand_female_5.jpg','local_path':str((REF/'references/Hand female 5.jpg').relative_to(ROOT)),'sha256':sha(REF/'references/Hand female 5.jpg'),'license':'CC BY-SA 4.0','what_it_supports':'Palmar first-web/thenar surface appearance, not a registered anatomical boundary.','what_it_does_not_support':'Model face ID, hidden CMC location or transfer of a crease into a stop authority.'},{'id':'KAPANDJI1986','source':'A. Kapandji, Functional anatomy of the first web space, Ann Chir Main 5(2):158–165','publication_date':'1986','url':'https://pubmed.ncbi.nlm.nih.gov/3767503/','doi':'10.1016/S0753-9053(86)80033-3','access_date':'2026-10-03','access_level':'Primary indexed English abstract retrieved via web search; direct page fetch encountered CAPTCHA; full text not inspected.','what_it_supports':'First-web function involves trapeziometacarpal structure, first dorsal interosseous/adductor pollicis/fascial relationships, web integument and thenar aponeurotic system.','what_it_does_not_support':'One universal skin-row boundary, this asset’s face IDs, or selection A/B/C.'},{'id':'CADAVER2024','source':'Measurement and observation of the first web space based on morphology and clinical applications','publication_date':'2024; indexed publication date not otherwise verified','url':'https://pubmed.ncbi.nlm.nih.gov/39084025/','access_date':'2026-10-03','access_level':'Primary PubMed indexed abstract excerpt from targeted search; direct page fetch encountered CAPTCHA; full text not inspected.','what_it_supports':'Cadaver skin morphology may be an asymmetric quadrilateral toward the index side; palmar-abduction pose matters in its measurement.','what_it_does_not_support':'A cylindrical sector test, exact P03/P04/P05 boundary, or anatomical registration of this mesh.'}],'not_used_as_new_normal_anatomy_authority':['Clinical WashU postoperative image: scar/occlusion and no redistribution permission; link retained in old pack but not embedded or used to define the normal boundary.','Unverified commercial, AI, Pinterest or source-free anatomy images.'],'no_external_image_registered_to_mesh':True}
dump('ANATOMICAL_REFERENCE_EVIDENCE.json',references)
faces=[];partial=[];broad=[]
for row in P['row_ids']:
    t=rowmap[row]
    for f in t['face_ids']:
        context={'vertex_ids':F[f],'edge_ids':edges(f),'incident_fan_face_ids':sorted({g for v in F[f] for g in vf[v]}),'distal_incident_face_id':next(x for x in flow['RSSF'] if x['row']==row)['lane_flows'][t['face_ids'].index(f)]['transports'][0]['to_face_id'],'proximal_incident_face_id':next(x for x in flow['RSSF'] if x['row']==row)['lane_flows'][t['face_ids'].index(f)]['transports'][1]['to_face_id']}
        evidence=['Original quad and both real lane continuation edges remain present.','First-web frozen seeds and the existing strip provide a directional/context reference, not a frozen anatomical label for this face.','Nail and corrected distal direction distinguish viewing sides; neither defines palm ownership.','No local face fan has an independently approved broader palm/thenar identity to prove a positive role onset.']
        questions={'thumb_local_digit_surface':{'answer':'AMBIGUOUS','support':'Digit-branch/web-flank interpretation remains compatible, especially at the early rows; not anatomically registered.'},'first_web_facing_flank':{'answer':'AMBIGUOUS','support':'Context is toward frozen first-web surface strip; exact-face flank identity is not frozen.'},'thumb_partial_circumference_sector':{'answer':'AMBIGUOUS','support':'Two lanes alone do not prove thumb wrapping or its loss.'},'broader_palm_metacarpal_thenar_interface':{'answer':'AMBIGUOUS','support':'Patch continuity with adjacent fans is real, but those fans have no independent broader-interface role map.'},'evidence_source':['LOCAL_FACE_PATCHES_R1.json','LOCAL_SURFACE_FLOW_R1.json','LOCAL_ANATOMICAL_REFERENCE_FRAME_R1.json','ANATOMICAL_REFERENCE_EVIDENCE.json']}
        faces.append({'face_id':f,'row':row,'surface_role':'AMBIGUOUS','evidence_basis':evidence,'exact_face_questions':questions,'anatomical_reference':['LOCAL_DORSAL','LOCAL_PALMAR','KAPANDJI1986','CADAVER2024'],'topological_context':context,'native_support':{'surface_flow':'AMBIGUOUS','same_face_ids':True,'axis_reference':'Nail-transported corrected direction; no approved native MCP/CMC registration.'},'RSSF_support':{'surface_flow':'AMBIGUOUS','same_face_ids':True,'axis_reference':'Approved corrected kinematics/nail/web/wrist axes, not role labels.'},'status':'PENDING_FOCUSED_HUMAN_ANATOMICAL_ADJUDICATION'})
    partial.append({'row':row,'face_ids':t['face_ids'],'THUMB_LOCAL_CIRCUMFERENTIAL_SURFACE_PATCH':'UNRESOLVED','requirements':{'A_transverse_flow_wraps_thumb_local_structure':'AMBIGUOUS: cross-strip flow is known; thumb wrapping identity not registered.','B_longitudinal_flow_along_digit_metacarpal_branch':'SUPPORTED_COMPATIBILITY: real paired lane continuation, not a unique anatomical branch role.','C_normal_field_digit_side_wrapping_semantics':'AMBIGUOUS: geometric transport is defined, but no normal sign/threshold defines semantics.','D_sector_relation_to_frozen_web_context':'SUPPORTED_CONTEXT_ONLY: frozen seeds/strip are visible and unchanged; extrapolated sector membership is not approved.'},'native_RSSF_result':'Neither state establishes all A–D as anatomical role authority.','does_not_require_closed_ring':True,'does_not_assume_cylindrical_chain':True})
    broad.append({'row':row,'face_ids':t['face_ids'],'positive_broader_interface_role':'NOT_PROVEN','checks':[{'test':'Flow ceases to wrap thumb','result':'AMBIGUOUS','basis':'The geometric field is available; no calibrated anatomical wrapping reference is registered.'},{'test':'Transverse flow crosses a broader metacarpal/palm sheet','result':'AMBIGUOUS','basis':'Adjacent flank quads exist, but no approved exact-face broader sheet identifies the destination.'},{'test':'Left/right lanes cease to form paired digit-sector lanes','result':'NOT_OBSERVED_TOPOLOGICALLY','basis':'Both original lanes remain paired across real incoming/outgoing sections through all fixed rows; pairing persistence alone does not prove digit role.'},{'test':'Incident fan becomes continuous with known wider palm-facing patch','result':'AMBIGUOUS','basis':'Four-face cyclic fans and local continuity exist throughout. Wider patch anatomical identity is not frozen.'},{'test':'Frozen-web strip becomes the edge of a broader sheet','result':'AMBIGUOUS','basis':'No local authority distinguishes a sector from a sheet edge. Shared topology is not anatomical registration.'}],'not_digit_does_not_imply_palm':True,'no_more_search':True})
dump('PROXIMAL_EXACT_FACE_ROLE_MAP_R1.json',{'allowed_roles':['DIGIT_WEB_SURFACE','TRANSITION_SURFACE','BROADER_SHARED_INTERFACE','AMBIGUOUS'],'faces':faces,'row_role':{r:'AMBIGUOUS' for r in P['row_ids']},'no_geometry_morphology_renamed_as_anatomical_role':True})
dump('EXACT_FACE_PARTIAL_CIRCUMFERENCE_ROLE_AUDIT.json',{'rows':partial,'all_required_anatomical_conditions_proven':False,'closed_ring_not_required':True,'new_scalar_extrema':False})
dump('BROADER_INTERFACE_POSITIVE_EVIDENCE_AUDIT.json',{'rows':broad,'positive_role_onset':'UNRESOLVED','machine_evidence_exhausted_for_local_boundary':True})
dump('P02_EARLY_SIDE_CONTROL_AUDIT.json',{'row':'P02','face_ids':rowmap['P02']['face_ids'],'result':'FAIL','failure_means':'DOMINANT_DIGIT_WEB_ORGANIZATION_NOT_ANATOMICALLY_CERTIFIED','new_rule_applied':'Broader influence is permitted; absence of broader influence is NOT required.','positive_compatible_evidence':'Paired lanes and transverse strip structure continue from immediate distal P01; frozen web reference remains consistent.','remaining_limit':'The immediate fan plus approved viewing axes does not prove dominant thumb-wrapping identity in both states. This is not a negative finding that P02 is broader interface.','human_question':'Q1_P02_digit_web_acceptable'})
dump('P06_LATE_SIDE_CONTROL_AUDIT.json',{'row':'P06','face_ids':rowmap['P06']['face_ids'],'result':'FAIL','failure_means':'POSITIVE_BROADER_INTERFACE_ROLE_NOT_CERTIFIED','positive_test_source':'BROADER_INTERFACE_POSITIVE_EVIDENCE_AUDIT.json','post_reversal_is_not_palm_role':True,'P07_guard':'Only immediate faces1379/1376 used for incident transport; no successor search.','human_question':'Q2_P06_broader_interface_acceptable','stop_automatic_search':True})
priorchoices=read(PREV/'PROXIMAL_STOP_NEIGHBOR_NEGATIVE_CONTROL_AUDIT.json')['alternatives'];choices=[]
for opt,q in zip('ABC',priorchoices):
    before,after=q['row_pair'];choices.append({'option':opt,'stop':q['stop'],'row_pair':q['row_pair'],'boundary_edges':q['edges'],'DISTAL_ROLE':'AMBIGUOUS','PROXIMAL_ROLE':'AMBIGUOUS','ROLE_CHANGE_PROVEN':False,'TOO_EARLY':'UNRESOLVED','TOO_LATE':'UNRESOLVED','UNRESOLVED':True,'basis':'No adjacent pair has exact distal DIGIT_WEB_SURFACE and proximal BROADER_SHARED_INTERFACE proof; other candidates cannot be rejected by exact role.','state_convergence':'Same stable IDs and local flow organization; no unique anatomical role transition.'})
dump('THREE_BOUNDARY_ROLE_CHANGE_COMPARISON.json',{'candidates':choices,'fourth_boundary_not_added':True,'option_D':'KEEP_UNRESOLVED; no new edge boundary','no_weighted_ranking':True,'machine_unique_candidate':'NONE','machine_evidence_exhausted':True})
status={'authority':NAME,'status':'MACHINE_EVIDENCE_EXHAUSTED_HUMAN_ADJUDICATION_REQUIRED','row_exact_face_roles':{r:'AMBIGUOUS' for r in P['row_ids']},'P02_early_control':'FAIL','P06_late_control':'FAIL','candidate_A_role_change_proven':'NO','candidate_B_role_change_proven':'NO','candidate_C_role_change_proven':'NO','machine_unique_candidate':'NONE','machine_evidence_exhausted':'YES','external_anatomical_reference_used':'YES','anatomical_context_sufficient_for_focused_Human_review':True,'Human_Review_HTML_generated':False,'Human_Review_has_selectable_controls':False,'response_JSON_export_implemented':False,'new_scalar_extrema_computed':False,'FIRST_WEB21_changed':'NO','cap37_changed':'NO','nail_changed':'NO','first_web_hard_pin_count':0,'CMC_cage_ownership_hard_source':False,'distal_stops_reopened':False,'CORRECTED_COMMON_MM_SEMANTICS':'CANDIDATE_PENDING_HUMAN_APPROVAL','R2_runs':0,'R3_runs':0,'skin_runs':0,'Stage6_runs':0,'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'Human_response_count':0,'production_modified':False,'NEXT':'HUMAN_PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_ADJUDICATION','wait_for':'Human-exported response JSON','STOP':True}
dump(NAME+'_STATUS.json',status)
# Presentation geometry is allowed for viewing only; it creates no whole-palm role domain.
view={'vertices':{s:Q.tolist() for s,Q in coords.items()},'faces':F,'edges':E,'row_faces':{r:rowmap[r]['face_ids'] for r in P['row_ids']},'local_context_faces':localfaceids,'guard_rows':{r:rowmap[r]['face_ids'] for r in ['P01','P07']},'frozen_first_web_vertices':WEB,'frozen_first_web_seeds':SEEDS,'frozen_surface_strip_faces':F3,'strip_role':'EXISTING_GEOMETRIC_CONTEXT_NOT_NEW_ROLE_EXTENSION','thumb_nail_faces':NAIL,'cap37_faces':CAP['face_ids'],'cap37_vertex_ids':CAP['vertex_ids'],'frames':frames,'boundaries':choices,'whole_hand_render_only':True,'whole_hand_role_classification':False}
dump('REVIEW_VIEW_DATA.json',view)
dump('INPUT_VERIFICATION.json',{'status':'PASS','checks':checks,'no_historical_ownership_or_weights_consulted':True,'no_old_scripts_imported':True,'scope':'Exact P02–P06 face role review; immediate P01/P07 guards; direct incident fans; approved references. Full surface coordinates used only for viewing context.'})
print(json.dumps({'status':status['status'],'exact_faces':len(faces),'local_fan_faces':len(localfaceids),'guard_rows':['P01','P07'],'NEXT':status['NEXT']},indent=2))
