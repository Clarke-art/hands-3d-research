import sys,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
spec=importlib.util.spec_from_file_location('audit_common',OUT/'common.py');ac=importlib.util.module_from_spec(spec);spec.loader.exec_module(ac)
sys.path.insert(0,str(ROOT/'audits/minimal_local_geometry_amendment_design_r4'));sys.modules.pop('common',None)
import contact_components as cc,robust_geometry as rg,collision_engine as ce,contact_geometry as cg,geometry as ge,semantic_audit as sa
import numpy as np
G=ac.read(OUT/'REVIEW_GEOMETRY.json');D=ac.read(OUT/'DENT_SOURCE_LINEAGE_METRICS_R1.json');results={}
for label in ['OFFICIAL_BASE','OFFICIAL_L1','STAGE2_L1','STAGE4A_R2_BASE','STAGE4A_R2','STAGE4B_RSSF','STAGE4C_R2','R2_PRODUCTION']:
 s=G['stages'][label];v=np.array(s['world_mm']);F=s['faces'];E=sorted({tuple(sorted((a,b))) for p in F for a,b in zip(p,p[1:]+p[:1])});emap={e:i for i,e in enumerate(E)};FE=[[emap[tuple(sorted((a,b)))] for a,b in zip(p,p[1:]+p[:1])] for p in F];tri=[];owners=[]
 for fi,p in enumerate(F):
  for k in range(1,len(p)-1):tri.append([p[0],p[k],p[k+1]]);owners.append(fi)
 tri=np.array(tri);owners=np.array(owners)
 # Exact predicates use unregistered stage-native coordinates to avoid display-rounding contacts.
 raw=ac.read(OUT/'RAW_SOURCE_GEOMETRY.json')['stages'][label];v=np.array(raw['canonical_world_m'])*1000
 for mod in [cc,rg,ce,cg,ge,sa]:
  for name,val in [('F',F),('E',E),('FE',FE),('tri',tri),('owners',owners),('V',v),('origin',np.zeros(3))]:setattr(mod,name,val)
 ce.COMMON.clear()
 found,_,counts=cc.registry(v,s['roi_vertices']);band=4. if label=='OFFICIAL_BASE' else 2. if label in ['OFFICIAL_L1','STAGE2_L1'] else .5;pairs=ce.broad(v,s['roi_vertices'],band=band);minimum=None;closest=None
 for a,b in pairs:
  if set(F[int(owners[a])])&set(F[int(owners[b])]):continue
  m=cg.tri_pair_metrics(v,tri[a],tri[b]);dist=m['distance_mm']
  if minimum is None or dist<minimum:minimum=dist;closest={'native_face_ids':[int(owners[a]),int(owners[b])],'triangle_indices':[int(a),int(b)],'metrics':m}
 certified=minimum is not None and minimum<=band
 assert certified,('Expand distance search to certify closest',label,minimum,band)
 result={'counts':counts,'exact_local_contact_components':{str(k):z for k,z in found.items()},'closest_nonadjacent_native_face_distance_mm':minimum,'closest_nonadjacent_relation':closest,'nearest_distance_certified_by_AABB_exclusion':certified,'AABB_band_mm':band,'scope':'Mapped native ROI incident triangles against entire stage mesh. Native coordinate binary64 exact contacts; same finite-feature semantics as transfer gate. Natural crease versus introduced fold remains visual comparison, not an anatomy threshold.'}
 results[label]=result;D['stages'][label]['closest_local_self_contact_fold_relation']=result
 print('NATIVE CONTACT',label,counts,'closest',minimum,flush=True)
ac.dump('NATIVE_STAGE_CONTACT_DIAGNOSTICS.json',results);ac.dump('DENT_SOURCE_LINEAGE_METRICS_R1.json',D)
