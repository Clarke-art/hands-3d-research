import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from trial_geometry import *
def install_fixed_asset(kind,mesh):
 if kind=='BASE':return
 edit=np.load(OUT/(kind+'_EDIT.npz'));mesh.data=mesh.data.copy()
 if kind.startswith('A'):
  delta=edit['basis_delta'];base=mesh.data.shape_keys.key_blocks[0]
  for i in A:base.data[int(i)].co+=Vector(delta[i]);mesh.data.vertices[int(i)].co=base.data[int(i)].co
 elif kind=='B1':
  names,w=weights(mesh);target=edit['weights_after']
  for i in B:
   for j,n in enumerate(names):
    if abs(target[i,j]-w[i,j])>1e-10:mesh.vertex_groups[n].add([int(i)],float(target[i,j]),'REPLACE')
 else:
  base=mesh.data.shape_keys.key_blocks[0];k=mesh.shape_key_add(name='EXPERIMENT_ROI_B_RELIEF_R1_NOT_APPROVED',from_mix=False)
  for i in B:k.data[int(i)].co=base.data[int(i)].co+Vector(edit['corrective_delta'][i])
  k.value=1.
 mesh.data.update();bpy.context.view_layer.update()

results={};baselines={};comps_cache={}
for label,t in POSES:
 for kind in ['BASE','A1','A2','B1','B2']:
  path=FIXED if label=='FIXED_GEOMETRY_PASS' else SOURCE if kind=='BASE' else OUT/FILES[kind]
  sc,mesh,rig,left=open_scene(path)
  if label=='FIXED_GEOMETRY_PASS':install_fixed_asset(kind,mesh)
  setpose(sc,rig,label,t);v,tt,ff=coords(mesh);l,lt,lf=coords(left);assert np.array_equal(ff,F)
  if kind=='BASE':comps_cache[label]=components(sc)
  cp=comps_cache[label];st=collisions(v,tt);cross=set(map(tuple,tree(v,tt).overlap(tree(l,lt))))
  start=time.perf_counter();kr=keyrows(v,tt,cp,{'A#4','A4','C#5'} if label=='FIXED_GEOMETRY_PASS' else set())
  contacts=active_contacts(v,l,2.6 if t is None else t) if label!='NEUTRAL_REST' else []
  shapes={k.name:k.value for k in mesh.data.shape_keys.key_blocks}
  rec={'pose':label,'candidate':kind,'time_sec':t,'neutral_definition':'Original rig armature pose_position REST at unchanged C1 2.6s object/root transform; shape keys retained' if t is None else None,'shape_values':shapes,'keys':kr,'self_pairs':sorted(st),'cross_hand_pairs':sorted(cross),'active_contacts':contacts,'keycheck_seconds':time.perf_counter()-start,'signature':signature(mesh,rig,left)}
  if kind=='BASE':baselines[label]={'v':v,'t':tt,'l':l,'self':st,'cross':cross,'keys':kr,'sig':rec['signature'],'contacts':contacts};rec['comparison']='BASELINE_INHERITED_DEFECTS_NOT_REPAIRED'
  else:
   base=baselines[label];allowed=A if kind.startswith('A') else B;outside=np.setdiff1d(np.arange(3300),allowed)
   assert np.max(abs(v[outside]-base['v'][outside]))==0,'DEFORMATION_OUTSIDE_ALLOWED'
   assert np.max(abs(l-base['l']))==0,'LEFT_CHANGED'
   assert rec['signature']==base['sig'],'FROZEN_ATTR_CHANGED'
   assert np.max(abs(v[S]-base['v'][S]))==0,'S_CHANGED'
   br={(r['key_index'],r['component']):r for r in base['keys']};regress=[]
   for r in kr:
    b=br[(r['key_index'],r['component'])]
    if r['depth_mm']>b['depth_mm']+1e-5 or r['bvh_pairs']>b['bvh_pairs']:regress.append({'key':r['key'],'component':r['component'],'baseline_depth_mm':b['depth_mm'],'candidate_depth_mm':r['depth_mm'],'baseline_pairs':b['bvh_pairs'],'candidate_pairs':r['bvh_pairs']})
   newself=sorted(st-base['self']);newcross=sorted(cross-base['cross']);shift=np.linalg.norm(v-base['v'],axis=1)*1000
   rec.update({'max_skin_shift_mm':float(shift.max()),'actual_changed_vertex_ids':np.flatnonzero(shift>1e-7),'outside_allowed_error_mm':0.,'S_skin_error_mm':0.,'left_skin_error_mm':0.,'new_self_pairs':newself,'new_cross_hand_pairs':newcross,'key_regressions':regress,'deformation':deform_metrics(v,base['v'],allowed,tt,base['t']),'inherited_collisions_present':any(r['depth_mm']>1e-6 or r['bvh_pairs'] for r in base['keys'])})
   rec['geometry_regression']=bool(newself or newcross or regress or len(rec['deformation']['flipped_face_ids']))
   rec['contact_position_max_delta_mm']=max([float(np.linalg.norm(np.array(a['contact']['skin_world'])-np.array(b['contact']['skin_world']))*1000) for a,b in zip(contacts,base['contacts'])]+[0.])
  joints={n:dict(head_world=list(<REDACTED_EMAIL>[n].head),tail_world=list(<REDACTED_EMAIL>[n].tail)) for n in ['INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R','THUMB_CMC_R','THUMB_MCP_R']}
  save(kind+'__'+label+'.json',rec);np.savez_compressed(OUT/(kind+'__'+label+'.npz'),V=v,T=tt,L=l,LT=lt)
  if kind=='BASE':save('BASE__'+label+'__CAMERA_CONTEXT.json',{'joints':joints,'key_components':[dict(key=co[0]['note_name'],name=co[2],V=co[3],T=co[4]) for co in cp]})
  results[kind+'__'+label]={k:rec[k] for k in rec if k not in ['signature','self_pairs','cross_hand_pairs','keys']}
  print('VALIDATED',kind,label,'regression',rec.get('geometry_regression'),'newself',len(rec.get('new_self_pairs',[])),'keyseconds',round(rec['keycheck_seconds'],2),flush=True)
save('MULTIPOSE_GEOMETRY_SUMMARY.json',results)

# 16 right-hand notes × three active samples, original C1 clock and untouched key Actions.
sample_results={}
for kind in ['BASE','A1','A2','B1','B2']:
 sc,mesh,rig,left=open_scene(SOURCE if kind=='BASE' else OUT/FILES[kind]);rows=[]
 for n in [n for n in NOTES if n['hand']=='R']:
  for tag,t in [('ON_PLUS_35MS',n['note_on']+.035),('MID_ACTIVE',(n['note_on']+n['note_off'])/2),('PRE_OFF',n['note_off']-.00001)]:
   assert n['note_on']<=t<n['note_off'];c.settime(sc,t);v,_,_=coords(mesh)
   r={'note_id':n['note_id'],'key':n['note_name'],'finger':n['finger'],'sample':tag,'time_sec':t,'contact':contact(v,KEYS[n['key_index']],'R',n['finger']),'frozen_corrective_value':mesh.data.shape_keys.key_blocks['FIRST_WEB_OPPOSITION_CREASE_R1'].value,'experimental_corrective_value':mesh.data.shape_keys.key_blocks['EXPERIMENT_ROI_B_RELIEF_R1_NOT_APPROVED'].value if kind=='B2' else None}
   if kind!='BASE':
    b=sample_results['BASE'][len(rows)];r['skin_contact_delta_mm']=float(np.linalg.norm(v[r['contact']['vertex']]-np.array(b['contact']['skin_world']))*1000);assert r['skin_contact_delta_mm']==0
   rows.append(r)
 assert len(rows)==48;sample_results[kind]=rows
 print('CONTACT48',kind,'strict_pass',sum(r['contact']['pass_prior_static_strict'] for r in rows),'samples',len(rows),flush=True)
save('RIGHT16_ACTIVE48_SKIN_CONTACTS.json',sample_results);protection('VALIDATION_INPUT_RECEIPT.json')
