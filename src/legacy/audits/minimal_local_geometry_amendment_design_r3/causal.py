import sys
sys.dont_write_bytecode=True
from contact_geometry import *
R2=ROOT/'audits/minimal_local_geometry_amendment_design_r2'
failed=read(R2/'R2_FAILED_SOLVE_WRITE_SET_EVIDENCE.json')['support_depth_witnesses']
trace=read(R2/'CORE_HINGE_CONSTRAINT_TRACE_R2.json')
target=np.array(trace[failed['5']['attempt']['attempt_id']]['world_mm']);delta=target-V
pairvertices=sorted(set(F[204])|set(F[207]));base=face_pair_metrics(V)
grid=[]
for t in np.linspace(0,1,101):
 m=face_pair_metrics(V+t*delta);grid.append({'fraction':float(t),'minimum_separation_mm':m['minimum_separation_mm'],'exact_contact':m['exact_contact'],'crossing':m['crossing'],'segment_mm':m['max_crossing_segment_mm']})
def onset(predicate):
 k=next((i for i,z in enumerate(grid) if predicate(z)),None)
 if k is None:return None
 lo=grid[max(0,k-1)]['fraction'];hi=grid[k]['fraction']
 for _ in range(40):
  mid=(lo+hi)/2;m=face_pair_metrics(V+mid*delta);s={'minimum_separation_mm':m['minimum_separation_mm'],'exact_contact':m['exact_contact'],'crossing':m['crossing']}
  if predicate(s):hi=mid
  else:lo=mid
 return {'fraction_bracket':[lo,hi],'fraction':hi,'metrics_at_upper':face_pair_metrics(V+hi*delta)}
near=onset(lambda z:z['minimum_separation_mm']<=1e-3)
exact=onset(lambda z:z['minimum_separation_mm']<=1e-8)
cross=onset(lambda z:z['crossing'])
ablations={}
for name,ids in [('FACE204_ONLY',F[204]),('FACE207_ONLY',F[207]),('BOTH_FACES',pairvertices)]:
 v=V.copy();v[ids]=target[ids];ablations[name]=face_pair_metrics(v)
for component,axis in [('TANGENT_X',x),('TANGENT_Y',y),('NORMAL',n)]:
 v=V.copy();v[pairvertices]+=np.outer(delta[pairvertices]@axis,axis);ablations[component+'_ONLY']=face_pair_metrics(v)
restore={};single={}
for i in pairvertices:
 v=target.copy();v[i]=V[i];restore[str(i)]=face_pair_metrics(v)
 v=V.copy();v[i]=target[i];single[str(i)]=face_pair_metrics(v)
neighborhoods={}
for fi in [204,207]:
 s0=set(F[fi]);s1=s0|{j for i in s0 for j in adj[i]};s2=s1|{j for i in s1 for j in adj[i]}
 neighborhoods[str(fi)]={'native_cycle':F[fi],'native_edge_ids':FE[fi],'incident_face_ids':sorted(face_domain(s0)),'one_ring_vertices':sorted(s1-s0),'two_ring_vertices':sorted(s2-s1),'one_ring_incident_faces':sorted(face_domain(s1)),'two_ring_incident_faces':sorted(face_domain(s2))}
stages={}
for dep in ['3','4','5']:
 a=failed[dep]['attempt'];v=np.array(trace[a['attempt_id']]['world_mm']);stages[dep]={'attempt_id':a['attempt_id'],'metrics':face_pair_metrics(v),'vertices':{str(i):{'baseline_world_mm':V[i].tolist(),'failed_world_mm':v[i].tolist(),'delta_world_mm':(v[i]-V[i]).tolist(),'delta_in_dent_frame_mm':((v[i]-V[i])@B).tolist()} for i in pairvertices}}
cause={'motion_ablation_crossing':{k:z['crossing'] for k,z in ablations.items()},'restoring_single_vertex_removes_crossing':[int(i) for i,z in restore.items() if not z['crossing']],'single_vertex_motion_is_sufficient':[int(i) for i,z in single.items() if z['crossing']],'mechanism':'Native fan-triangle vertex/edge ordering and signed separation are lost under the R2 field; endpoint positions, motion-component and face-motion counterfactuals below identify the responsible motions. Final intersection alone is not used as a causal explanation.','normal_rotation_deg':{'face204':math.degrees(math.acos(float(np.clip(normal(V,F[204])@normal(target,F[204]),-1,1)))),'face207':math.degrees(math.acos(float(np.clip(normal(V,F[207])@normal(target,F[207]),-1,1))))}}
dump('FACE204_207_CONTACT_CAUSAL_AUDIT_R3.json',{'DESIGN_ANALYSIS_ONLY':True,'shared_vertex_ids':sorted(set(F[204])&set(F[207])),'shared_edge_ids':sorted(set(FE[204])&set(FE[207])),'baseline':base,'native_neighborhoods':neighborhoods,'R2_S3_S4_S5':stages,'interpolation_onset_sweep':grid,'first_near_contact':near,'first_exact_contact':exact,'first_crossing':cross,'near_contact_tolerance_mm':1e-3,'exact_distance_tolerance_mm':1e-8,'crossing_segment_tolerance_mm':1e-7,'tolerance_class':'COMPUTATIONAL_GEOMETRY_TOLERANCE_NOT_ANATOMY_CLEARANCE','face_and_component_motion_counterfactuals':ablations,'restore_one_vertex_counterfactuals':restore,'single_vertex_motion_counterfactuals':single,'onset_cause':cause,'source_refs':[ref(R2/'R2_FAILED_SOLVE_WRITE_SET_EVIDENCE.json'),ref(R2/'CORE_HINGE_CONSTRAINT_TRACE_R2.json')],'candidate_generation_count':0})
print('BASELINE',base['minimum_separation_mm'],base['closest_features'],flush=True)
print('ONSETS',{'near':near['fraction'] if near else None,'exact':exact['fraction'] if exact else None,'cross':cross['fraction'] if cross else None},flush=True)
print('CAUSE',cause,flush=True)
