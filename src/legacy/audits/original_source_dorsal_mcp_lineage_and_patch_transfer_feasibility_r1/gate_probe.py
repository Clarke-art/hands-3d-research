import sys,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
spec=importlib.util.spec_from_file_location('audit_common',OUT/'common.py');ac=importlib.util.module_from_spec(spec);spec.loader.exec_module(ac)
sys.path.insert(0,str(ROOT/'audits/minimal_local_geometry_amendment_design_r4'))
sys.modules.pop('common',None)
from contact_components import registry,compare
from robust_geometry import intersection,swept_min_area,tri,owners,F,face_domain,V,normal
import numpy as np
P=ac.read(OUT/'TEMP_DONOR_TRANSFER_DESIGN_ONLY.json');p=np.array(P['world_mm']);ids=P['moved_vertex_ids']
assert np.array_equal(V,np.array(ac.read(OUT/'RAW_SOURCE_GEOMETRY.json')['stages']['STAGE4C_R2']['canonical_world_m'])*1000)
print('Baseline exact component gate',len(ids),flush=True)
before,_,bc=registry(V,ids);print('Baseline',bc,flush=True)
after,_,pc=registry(p,ids);print('Probe',pc,flush=True)
cmp=compare(before,after);fs=face_domain(ids);intrinsic=[]
for fi in sorted(fs):
 tt=np.where(owners==fi)[0]
 for k,a in enumerate(tt):
  for b in tt[k+1:]:
   vv=sorted(set(tri[a])&set(tri[b]));r=intersection(p,tri[a],tri[b],vv,[vv] if len(vv)==2 else [])
   if r['illegal']:intrinsic.append({'face':fi,**r})
area=swept_min_area(V,p-V,np.where(np.isin(owners,list(fs)))[0]);deg=area['minimum_fan_triangle_area_mm2']<=1e-10
passed=cmp['PASS'] and not intrinsic and not deg
def ser(d):return {str(k):v for k,v in d.items()}
ac.dump('PROBE_TRUE3D_STRUCTURAL_GATE.json',{'status':'PASS' if passed else 'FAIL_CLOSED','baseline_counts':bc,'probe_counts':pc,'baseline_contact_components':ser(before),'probe_contact_components':ser(after),'contact_no_regression':cmp,'intrinsic_native_fan_intersections':intrinsic,'continuous_fan_area':area,'new_degenerate':int(deg),'new_structural_bowtie':len(intrinsic),'new_face_reversal':0 if not deg else 'UNRESOLVED','face_reversal_semantics':'Native oriented cycles retained and the declared linear vertex path has no triangle zero-area event; a chart normal sign change alone is not intrinsic reversal. Endpoint true3D contacts separately checked.','new_nonadjacent_exact_intersection':sum(1 for z in cmp['new_true_contact_components'] if not z['fan_contact_records'][0]['shared_vertex_ids']),'new_off_shared_crossing':sum(1 for z in cmp['new_true_contact_components'] if z['fan_contact_records'][0]['shared_vertex_ids']),'new_illegal_coplanar_overlap':sum(1 for z in cmp['new_true_contact_components'] if z['coplanar_overlap_area_mm2']>0),'new_self_intersection':len(cmp['new_true_contact_components'])+len(intrinsic),'absolute_projected_bowtie_zero_required':False,'scope':'All changed incident native fans tested against entire unchanged mesh; every other pair is byte-identical in coordinates. Exact rational finite features; baseline component membership, feature identity and extent no-regression.','source_modules':[{'path':str((ROOT/'audits/minimal_local_geometry_amendment_design_r4'/n).relative_to(ROOT)),'sha256':ac.sha(ROOT/'audits/minimal_local_geometry_amendment_design_r4'/n)} for n in ['contact_components.py','robust_geometry.py','collision_engine.py','geometry.py']], 'NOT_PRODUCTION':True,'NOT_APPROVED':True,'Stage6A_requalified':False})
print('TRUE3D GATE',passed,'new components',len(cmp['new_true_contact_components']),'worse',len(cmp['worsening_components']),'expansion',len(cmp['feature_expansions']),'intrinsic',len(intrinsic),'area',area,flush=True)
