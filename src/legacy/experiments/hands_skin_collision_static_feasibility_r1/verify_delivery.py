import json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent
read=lambda n:json.loads((O/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=read('PROTECTED_INPUTS_BEFORE.json');after={p:sha(Path(p)) for p in before};assert before==after
(O/'PROTECTED_INPUTS_AFTER.json').write_text(json.dumps(after,indent=2)+'\n',encoding='utf8')
F=read('STATIC_POSE_FEASIBILITY.json');POL=read('POLICY_LOCK.json');M=read('COLLISION_METHOD_TESTS.json');required=['COLLISION_METHOD_VALIDATION.md','INITIAL_POSE_COLLISION_DIAGNOSIS.md','STATIC_POSE_FEASIBILITY.json','HUMAN_VISUAL_REVIEW.md','FINAL_RECOMMENDATION.md']
assert F['status']=='STATIC_FEASIBILITY_PARTIAL' and F['passed_tests']==['S2','S3','S4'];assert F['total_numerical_wall_seconds']<600
assert M['status']=='VALIDATED_FOR_STATIC_SCREEN' and M['triangle_without_inside_vertices_test']['pass_'] and M['contact_tangent_vs_hover_validation']
for t in F['tests']:
 assert len(t['attempts'])<=2
 for a in t['attempts']:
  assert a['frozen_hand_identity_unchanged']
  assert a['controls']['root_z_fixed_per_initialization']
 if t['test'] in F['passed_tests']:
  selected=next(a for a in t['attempts'] if a['scene']==t['selected_scene']);g=selected['actual_geometry'];assert g['contact']['top_surface_crossing_triangles']>0 and g['contact']['true_pulp_surface_contact_distance_mm']==0 and not g['nonadjacent_self_triangle_pairs'] and g['target_key_max_depth_mm']<=.25 and g['wrong_key_or_nonpulp_max_depth_mm']<=.25
for n in required:assert (O/n).stat().st_size>0 and '\ufffd' not in (O/n).read_text(encoding='utf8')
assert len(list((O/'stills').glob('*.png')))==8 and len(read('STILL_MANIFEST.json'))==8
assert not list(O.glob('*.mp4')) and not (O/'_frames').exists();assert len(list(O.glob('*.blend')))==1
files=[p for p in O.rglob('*') if p.is_file() and p.name!='DELIVERY_MANIFEST.json'];total=sum(p.stat().st_size for p in files)
manifest=dict(task=POL['task'],status=F['status'],authority='DESIGN_PROVISIONAL',protected_files=len(before),all_protected_files_unchanged=True,numerical_wall_seconds=F['total_numerical_wall_seconds'],passes=F['passed_tests'],stills=8,videos=0,new_animation_keyframes=0,diagnostic_blends=1,total_bytes=total,required_files=[dict(file=n,sha256=sha(O/n),bytes=(O/n).stat().st_size) for n in required],files=[dict(file=p.relative_to(O).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(files)])
(O/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('DELIVERY_VERIFIED',len(before),'protected files unchanged; numerical wall',F['total_numerical_wall_seconds'],'s; 3 formal static passes; 8 stills; 1 static Blend; 0 new keyframes; MB',round(total/1024/1024,2))
