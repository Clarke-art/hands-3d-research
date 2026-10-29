import sys
sys.dont_write_bytecode=True
from common import *
data={k:read(OUT/(k+'_REOPENED_NATIVE_PAYLOAD_R1.json')) for k in ASSETS}
receipt=ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1/APPLICATION_AUTHORITY_INTERSECTION_AUDIT_R1.json';authority=read(receipt);sets={}
for name,n in {'cap37':37,'old_cap9':9,'FIRST_WEB21':21,'fresh_R3_protected_domain':962,'historical317_weight_universe':317,'thumb_nail':22,'CMC_frozen_cage_context':73}.items():
 a=authority['sets'][name];ids=a['frozen_vertex_ids'];p=ROOT/a['source']['path'];assert sha(p)==a['source']['sha256'] and len(ids)==len(set(ids))==n and digest(ids)==a['membership_sha256']
 assert all(all(s['protected']['mesh']['vertex_ids'][i]==i for i in ids) for s in data.values())
 sets[name]={'membership_count':n,'frozen_native_vertex_ids':ids,'membership_sha256':digest(ids),'authority':ref(p),'membership_drift':0,'each_derived_mapping_count':{k:n for k in ASSETS},'ID_consistency_only':True}
for name,path,field,count in [('dorsal54',ROOT/'audits/local_donor_shape_transfer_amendment_design_r1/FORMAL_DONOR_TRANSFER_WRITE_SET_R1.json','vertex_ids',54),('palmar16',DESIGN/'PALMAR_ROOT_FORMAL_WRITE_SET_R1.json','vertex_ids',16)]:
 a=read(path);ids=a[field];assert len(ids)==len(set(ids))==count
 assert all(all(s['protected']['mesh']['vertex_ids'][i]==i for i in ids) for s in data.values())
 sets[name]={'membership_count':count,'frozen_native_vertex_ids':ids,'membership_sha256':digest(ids),'authority':ref(path),'membership_drift':0,'each_derived_mapping_count':{k:count for k in ASSETS},'ID_consistency_only':True}
assert sets['palmar16']['frozen_native_vertex_ids']==IDS
for s in data.values():
 k=next(k for k,v in data.items() if v is s);source=read(OUT/'FROZEN_INPUT_NATIVE_PAYLOADS_R1.json')[k];assert all(s['coordinates_local_m'][i]==source['coordinates_local_m'][i] for i in sets['dorsal54']['frozen_native_vertex_ids'])
dump('PALMAR_STAGE5_AUTHORITY_MEMBERSHIP_R1.json',{'status':'PASS','sets':sets,'frozen_authority_receipt':ref(receipt),'membership_recomputed_or_reclassified':False,'solver_R3_ownership_anatomy_research_runs':0,'nail_payload_semantics_inherited_exact':True})
s=data['R2'];E=[e[1] for e in s['protected']['mesh']['edges']];F=[f[1] for f in s['protected']['mesh']['faces']];adj=[set() for _ in s['coordinates_local_m']]
for a,b in E:adj[a].add(b);adj[b].add(a)
w=set(IDS);one=w|{j for i in w for j in adj[i]};two=one|{j for i in one for j in adj[i]};wf={fi for fi,p in enumerate(F) if set(p)&w};rows=[]
for p in read(ROOT/'production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/LOCKED_CURRENT9_ROWS_R1.json')['rows']:
 pv=set(p['vertex_ids']);pf=set(p['face_ids']);rows.append({'pair_id':p['pair_id'],'case_id':p['case_id'],'direct_vertex_overlap':sorted(w&pv),'changed_face_overlap':sorted(wf&pf),'1ring_overlap':sorted(one&pv),'2ring_overlap':sorted(two&pv)})
d=sum(bool(r['direct_vertex_overlap'] or r['changed_face_overlap']) for r in rows);a=sum(bool(r['1ring_overlap']) for r in rows);b=sum(bool(r['2ring_overlap']) for r in rows);assert d==a==b==0
assert data['CORRECTED']['protected']['mesh']['vertex_ids']==data['R2']['protected']['mesh']['vertex_ids'] and data['CORRECTED']['protected']['mesh']['edges']==data['R2']['protected']['mesh']['edges']
dump('PALMAR_STAGE5_CURRENT9_INDEPENDENCE_R1.json',{'status':'PASS','CURRENT9_DIRECT_OVERLAP':d,'CURRENT9_1RING_OVERLAP':a,'CURRENT9_2RING_OVERLAP':b,'rows':rows,'both_new_Stage5_native_topologies_exact_same':True,'scope':'ID / native topology consistency only; not fresh crossing/deformation qualification','CURRENT9_HUMAN_RESPONSE':'HOLD_NOT_CLOSED','answer_writes':0,'closure_created':False,'acceptance_expanded':False})
print('Membership IDs/counts unchanged; dorsal54 delta0; current9 overlap0/0/0',flush=True)
