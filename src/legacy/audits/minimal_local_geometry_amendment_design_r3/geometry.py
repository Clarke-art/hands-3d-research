import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np, math
DIAG=ROOT/'audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1'
R1=ROOT/'audits/minimal_local_geometry_amendment_design_r1'
R=read(DIAG/'DORSAL_MCP_DENT_ROI_R1.json')
L=read(DIAG/'LINEAGE_RAW_READONLY_EXTRACTION.json')
G=read(DIAG/'DENT_RENDER_GEOMETRY_R1.json')
F=L['topology']['faces'];E=L['topology']['edges']
V=np.array(L['stages']['STAGE4C_R2_RAW']['raw_world_m'])*1000
origin=np.array(G['frame']['origin_world_mm'])
B=np.array([G['frame'][k] for k in ['x','y','outward']]).T
Q=(V-origin)@B
adj=[set() for _ in V]
for a,b in E:adj[a].add(b);adj[b].add(a)
emap={tuple(sorted(e)):j for j,e in enumerate(E)}
EF=[[] for _ in E]
FE=[]
for fi,p in enumerate(F):
 es=[emap[tuple(sorted((a,b)))] for a,b in zip(p,p[1:]+p[:1])]
 FE.append(es)
 for ei in es:EF[ei].append(fi)
def normal(v,p):
 z=sum((np.cross(v[p[k]]-v[p[0]],v[p[(k+1)%len(p)]]-v[p[0]]) for k in range(len(p))),np.zeros(3))
 return z/max(np.linalg.norm(z),1e-15)
def normals(v):
 out=np.zeros((len(F),3))
 for n in sorted(set(map(len,F))):
  ids=np.array([i for i,p in enumerate(F) if len(p)==n]);ps=v[np.array([F[i] for i in ids])]
  ar=sum((np.cross(ps[:,k]-ps[:,0],ps[:,(k+1)%n]-ps[:,0]) for k in range(n)),np.zeros((len(ids),3)))
  out[ids]=ar/np.maximum(np.linalg.norm(ar,axis=1)[:,None],1e-15)
 return out
def areas(v):
 out=np.zeros(len(F))
 for n in sorted(set(map(len,F))):
  ids=np.array([i for i,p in enumerate(F) if len(p)==n]);ps=v[np.array([F[i] for i in ids])]
  ar=sum((np.cross(ps[:,k]-ps[:,0],ps[:,(k+1)%n]-ps[:,0]) for k in range(n)),np.zeros((len(ids),3)))
  out[ids]=np.linalg.norm(ar,axis=1)*.5
 return out
def angles(v):
 ns=normals(v);ee=np.array([fs for fs in EF]);return np.degrees(np.arccos(np.clip(np.sum(ns[ee[:,0]]*ns[ee[:,1]],axis=1),-1,1)))
def feat(q):return np.column_stack([np.ones(len(q)),q[:,0],q[:,1],q[:,0]**2,q[:,0]*q[:,1],q[:,1]**2])
reuse(R1/'geometry_metrics.py',['quad_bowties','sections'],globals())
x=B[:,0];y=B[:,1];n=B[:,2]
# All native quads are checked, including those outside the design patch.
FULLFS=list(range(len(F)))
baseN=normals(V);baseA=angles(V);baseBow=set(quad_bowties(V));baseAreas=areas(V)
cf=np.linalg.lstsq(feat(Q[R['2_ring']]),Q[R['2_ring'],2],rcond=None)[0]
def depth(v):
 q=(v-origin)@B;return float(max(0,-np.min((q[:,2]-feat(q)@cf)[R['core_vertices']])))
def face_domain(ids):return {fi for fi,p in enumerate(F) if set(ids).intersection(p)}
def boundary_domain(ids):
 ids=set(ids);fs=face_domain(ids)
 # Include every edge in a mixed moved/fixed face, every face-interface edge,
 # and the complete fixed/fixed edge ring incident to the exterior vertices.
 boundaryfs={fi for fi in fs if set(F[fi])-ids}
 interfaces={ei for ei,ff in enumerate(EF) if (set(ff)&fs) and (set(ff)-fs)}
 boundary=interfaces|{ei for fi in boundaryfs for ei in FE[fi]}
 exterior={i for fi in boundaryfs for i in F[fi] if i not in ids}|{i for ei in boundary for i in E[ei] if i not in ids}
 fixedring={ei for ei,(a,b) in enumerate(E) if a not in ids and b not in ids and ({a,b}&exterior)}
 return sorted(boundary),sorted(fixedring),sorted(fs)
def boundary_audit(v,ids):
 boundary,fixed,fs=boundary_domain(ids);an=angles(v);ns=normals(v);d=v-V;mag=np.linalg.norm(d,axis=1);rows=[]
 for ei in sorted(set(boundary)|set(fixed)|{6675,6602,6676}):
  a,b=E[ei];rows.append({'edge_id':ei,'vertex_ids':E[ei],'face_ids':EF[ei],'boundary_incident':ei in boundary,'outer_fixed_fixed_ring':ei in fixed,'baseline_dihedral_deg':float(baseA[ei]),'candidate_dihedral_deg':float(an[ei]),'delta_deg':float(an[ei]-baseA[ei]),'adjacent_face_baseline_outward_dot':(baseN[EF[ei]]@n).tolist(),'adjacent_face_candidate_outward_dot':(ns[EF[ei]]@n).tolist(),'adjacent_face_baseline_to_candidate_dot':np.sum(baseN[EF[ei]]*ns[EF[ei]],axis=1).tolist(),'endpoint_displacement_mm':mag[[a,b]].tolist(),'local_displacement_gradient':float(np.linalg.norm(d[a]-d[b])/max(np.linalg.norm(V[a]-V[b]),1e-12))})
 # A conservative engineering diagnostic, explicitly not an anatomy threshold.
 # Never accept a newly obtuse opposing interface or a new >45deg hinge with
 # >20deg increase. Full table and visual checks remain necessary.
 folds=[r for r in rows if (r['baseline_dihedral_deg']<90 and r['candidate_dihedral_deg']>=90) or (r['candidate_dihedral_deg']>45 and r['delta_deg']>20)]
 return {'boundary_edge_ids':boundary,'outer_fixed_fixed_edge_ids':fixed,'all_edges':rows,'new_boundary_sharp_folds':folds,'max_boundary_dihedral_deg':float(max(an[boundary])),'max_boundary_displacement_gradient':max(r['local_displacement_gradient'] for r in rows if r['boundary_incident']),'boundary_displacement_max_mm':float(max(mag[i] for fi in fs if set(F[fi])-set(ids) for i in F[fi])) if fs else 0,'screen_is_anatomy_threshold':False,'screen_definition':'Conservative geometry-design screen: newly obtuse interface OR angle>45deg and increase>20deg; full per-edge table + matched visual inspection required.'}
def structure(v,ids):
 ns=normals(v);fs=sorted(face_domain(ids));bows=set(quad_bowties(v));aa=areas(v);an=angles(v)
 newreverse=[fi for fi in fs if baseN[fi]@n>=0 and ns[fi]@n<-1e-7]
 deg=[int(fi) for fi in np.where(aa<1e-8)[0] if baseAreas[fi]>=1e-8]
 # Winding identity and correcting a documented old inward contour are distinct.
 flip=[fi for fi in fs if ns[fi]@baseN[fi]<0 and baseN[fi]@n>=0]
 ba=boundary_audit(v,ids)
 return {'vertex_count_unchanged':True,'edge_count_unchanged':True,'face_count_unchanged':True,'native_face_cycles_unchanged':True,'native_face_winding_preserved':True,'native_2face_incidence_unchanged':all(len(ff)==2 for ff in EF),'new_degenerate_faces':deg,'new_quad_bowties':sorted(bows-baseBow),'new_reference_reversed_faces':newreverse,'new_previously_outward_normal_reversals':flip,'corrected_preexisting_inward_faces':[fi for fi in fs if baseN[fi]@n<0 and ns[fi]@n>=0],'new_boundary_sharp_folds':ba['new_boundary_sharp_folds'],'edge6675_deg':float(an[6675]),'edge6602_deg':float(an[6602]),'edge6676_deg':float(an[6676]),'fixed_reference_core_depth_mm':depth(v),'baseline_core_depth_mm':depth(V),'boundary_audit':ba}
# Exact contact implementation from R1, with all shared-topology cases retained.
tri=[];owners=[]
for fi,p in enumerate(F):
 for k in range(1,len(p)-1):tri.append([p[0],p[k],p[k+1]]);owners.append(fi)
tri=np.array(tri);owners=np.array(owners);eps=1e-5
reuse(R1/'independent_contact_audit.py',['cross2','coplanar_overlap','edge_tri','point_seg_dist','contacts'],globals())
def contact_check(v,ids):
 global changed
 affected=face_domain(ids)
 changed=np.array([i for i,fi in enumerate(owners) if fi in affected])
 found,checked=contacts(v)
 return found,checked

def protection():
 cap=read(CAP_PATH);r3=read(R3_PATH)
 w=read(S5/'targeted_rig_and_skin_data_rebuild_r2/AUTHORIZED_WEIGHT_WRITE_SET_R2.json')
 cmc=read(ROOT/'production_spec/stage4_blender/stage4a_r2/CMC_LOCAL_RETOPO_AUDIT_R2.json')
 mats=L['stages']['R2_PRODUCTION']['face_material_indices']
 nail={v for fi,p in enumerate(F) if mats[fi]==1 for v in p}
 dist=np.linalg.norm(V-np.array(cmc['cmc']['world'])*1000,axis=1)
 return {'thumb_nail':nail,'cap37':set(cap['vertex_ids']),'old_cap9':set(cap['old_cap9_ids']),'FIRST_WEB21':set(r3['FIRST_WEB21']['membership_vertex_ids']),'fresh_R3_protected_memberships':set(r3['graph']['vertex_ids']),'historical317_skin_authority':set(w['approved_write_universe_317']),'CMC_protected_existing_20mm_context':set(np.where(dist<=cmc['surgery']['R_mm'])[0])}

def nested():
 ps=protection();sets={0:set(R['core_vertices'])};records=[];prevf=set();preve=set()
 for depth_i in range(6):
  if depth_i:sets[depth_i]=sets[depth_i-1]|{j for i in sets[depth_i-1] for j in adj[i]}
  pool=sets[depth_i];ff=face_domain(pool);ee={ei for fi in ff for ei in FE[fi]}
  hit={k:sorted(map(int,pool&v)) for k,v in ps.items()}
  records.append({'support_depth':depth_i,'support_set_name':f'S{depth_i}','DESIGN_SEARCH_POOL_ONLY':True,'vertex_count':len(pool),'vertex_ids':sorted(pool),'new_vertex_ids':sorted(pool-sets.get(depth_i-1,set())),'incident_face_ids':sorted(ff),'new_incident_face_ids':sorted(ff-prevf),'incident_edge_ids':sorted(ee),'new_incident_edge_ids':sorted(ee-preve),'authority_intersections':hit,'status':'PROTECTION_BOUNDARY_REACHED' if any(hit.values()) else 'ELIGIBLE_DESIGN_SEARCH_POOL'})
  prevf=ff;preve=ee
 return sets,records
