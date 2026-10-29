import sys
sys.dont_write_bytecode=True
from common import *
C=read(OUT/'APPLICATION_NATIVE_GEOMETRY_R1.json');F=C['faces'];E=C['edges'];write=set(IDS);prior=read(DESIGN/'FORMAL_DONOR_TRANSFER_DOWNSTREAM_PLAN_R1.json');expected=prior['geometry_footprint']
for r in prior['frozen_authorities']:assert sha(ROOT/r['path'])==r['sha256']
cap_path=ROOT/'production_spec/stage5_production_rig/stage5b_r1e_human_cap_authority_freeze_r1/THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json';r3_path=ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json';w_path=R2.parent/'AUTHORIZED_WEIGHT_WRITE_SET_R2.json';nail_path=SOURCE.parent/'NAIL_AUDIT_R2.json';cmc_path=ROOT/'production_spec/stage4_blender/stage4a_r2/R2_CAGE.json'
cap=read(cap_path);r3=read(r3_path);weights=read(w_path);nail=read(nail_path);cmc=read(cmc_path)
native_faces=[i for i,p in enumerate(F) if write.intersection(p)];native_edges=[i for i,e in enumerate(E) if write.intersection(e)]
sets={'cap37':(cap['vertex_ids'],cap_path),'FIRST_WEB21':(r3['FIRST_WEB21']['membership_vertex_ids'],r3_path),'fresh_R3_protected_domain':(r3['graph']['vertex_ids'],r3_path),'historical317_weight_universe':(weights['approved_write_universe_317'],w_path),'old_cap9':(r3['old_cap9']['vertex_ids'],r3_path),'thumb_nail':(sorted({i for fi in nail['per_digit_faces']['thumb'] for i in F[fi]}),nail_path)}
# Explicit frozen historical cage points -> frozen Stage4A native IDs only.
# No current spatial selection, new anatomy authority, geodesic solve or target solve.
raw_path=ROOT/'audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/RAW_SOURCE_GEOMETRY.json';rest=read(raw_path)['stages']['STAGE4A_R2'];assert sha(ROOT/rest['input']['path'])==rest['input']['sha256']
lookup={}
for i,p in enumerate(rest['canonical_world_m']):lookup.setdefault(tuple(round(z,6) for z in p),[]).append(i)
point_matches=[]
for p in cmc['new_vertex_world']:
 hits=lookup.get(tuple(p),[]);assert len(hits)==1,('Frozen explicit CMC new-cage point does not uniquely resolve native Stage4A ID',p,hits)
 point_matches.append({'kind':'frozen_new_cage','frozen_world_m_rounded_6':p,'native_vertex_id':hits[0]})
new_cage={r['native_vertex_id'] for r in point_matches};assert len(new_cage)==57
# boundary_loop_world uses historical CO before pole treatment (some boundary
# vertices subsequently moved). Resolve the final16 boundary through actual frozen
# native cage incidence, rather than falsely requiring those pre-pole coordinates.
rest_edges=rest['edges'];boundary_ids={v for a,b in rest_edges if a in new_cage or b in new_cage for v in [a,b]}-new_cage
assert len(boundary_ids)==16
cage_faces=[i for i,p in enumerate(rest['faces']) if new_cage.intersection(p)]
assert len(cage_faces)==64 and set(F[i][j] for i in cage_faces for j in range(len(F[i])))==new_cage|boundary_ids
assert rest['faces']==F and rest['edges']==E
cmcids=sorted(new_cage|boundary_ids);assert len(cmcids)==73
sets['CMC_frozen_cage_context']=(cmcids,cmc_path)
rows={k:{'membership_count':len(set(ids)),'frozen_vertex_ids':sorted(set(ids)),'membership_sha256':digest(sorted(set(ids))),'write_intersection_ids':sorted(write.intersection(ids)),'source':ref(path),'anatomy_authority_recomputed':False} for k,(ids,path) in sets.items()}
mapping={'cap37':'cap37_write_overlap','FIRST_WEB21':'FIRST_WEB21_write_overlap','fresh_R3_protected_domain':'fresh_R3_frozen_domain_write_overlap','historical317_weight_universe':'approved_317_weight_universe_write_overlap'}
for k,e in mapping.items():assert rows[k]['write_intersection_ids']==expected[e]
assert native_faces==expected['incident_native_face_ids'] and native_edges==expected['incident_edge_ids']
assert all(not r['write_intersection_ids'] for r in rows.values())
assert not set(native_faces).intersection(nail['per_digit_faces']['thumb'])
dump('APPLICATION_AUTHORITY_INTERSECTION_AUDIT_R1.json',{'status':'PASS','design_report_intersections_consistent':True,'actual54_write_set_exact':True,'sets':rows,'CMC_context_semantics':'57 explicitly frozen final new-cage points resolve by exact six-decimal historical serialization to native Stage4A IDs;16 final boundary vertices resolve by actual frozen native edge/face incidence (64 cage quads). Historical boundary_loop_world is pre-pole-treatment CO, not final boundary position authority. No new radius/nearest-surface selection or modeling execution; source/application/candidate native topology identical.','CMC_explicit_frozen_point_native_ID_correspondence':point_matches,'CMC_frozen_final_boundary_native_IDs':sorted(boundary_ids),'CMC_frozen_cage_face_IDs':cage_faces,'CMC_rest_geometry_reference':ref(raw_path),'thumb_nail_face_ids_unchanged':nail['per_digit_faces']['thumb'],'thumb_nail_incident_face_overlap':[],'cap37_incident_face_overlap':sorted(set(native_faces).intersection(cap['face_ids'])),'fresh_R3_exact_boundary_incident_edge_overlap':sorted(set(native_edges).intersection(r3['boundary']['edge_ids'])),'incident_native_face_ids':native_faces,'incident_edge_ids':native_edges,'membership_authority_files_unchanged':True,'NO_RESEARCH_REOPEN':True,'no_paths_bounds_ownership_skin_recomputation':True})
print('Frozen cap37/FIRST_WEB21/freshR3/317/thumb nail/oldcap9/CMC context membership consistency PASS; all write intersections empty')
