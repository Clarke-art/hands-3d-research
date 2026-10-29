from geometry import *
import geometry as g
R1=ROOT/'experiments/hands_c1_dynamic_artist_correction_poc_r1';R2=ROOT/'experiments/hands_c1_exit_handoff_correction_r2'
STARTCOPY=OUT/'R2_START_ISOLATED_NOT_APPROVED.blend'
assert sha(STARTCOPY)==sha(R2/'EXIT_CORRECTED_NOT_APPROVED.blend')
READS[str(R2/'EXIT_CORRECTED_NOT_APPROVED.blend')]=sha(STARTCOPY)
for p in [ROOT/'AGENTS.md',R2/'TECHNICAL_REPORT.md',R2/'CANDIDATE_2_VALIDATION.json',R2/'R2_REGRESSION_DETAILS.json',R2/'CANDIDATE_2_EDIT_LEDGER.json',ROOT/'experiments/hands_b01_visual_animation_refinement_r1/FINAL_B01_VISUAL_REVIEW.md',ROOT/'experiments/hands_b01_visual_animation_refinement_r1/B01_MACHINE_VALIDATION.json']:
 READS[str(p)]=sha(p)
extract(R1/'validate_full.py',['collision','selfpairs'],globals())
survey=[]
for tag,path in [('C1',SOURCE),('R2',STARTCOPY)]:
 sc,rig,mesh,left,lrig=s.open_scene(path);g.init()
 for t in [2.921426,3.,3.058333333333333,3.12,3.2,3.3,3.349997,3.4,3.5,3.5642825,3.6,3.7,3.778568,3.8]:
  c.settime(sc,t);V,T,F=s.coords_tri(mesh);keys=collision(V)
  active=[n for n in NOTES if n['hand']=='R' and n['note_on']<=t<n['note_off']]
  illegal={k:v for k,v in keys.items() if k not in [n['note_name'] for n in active] and (v['depth_mm']>1e-6 or v['pairs'])}
  for r in illegal.values():
   if r['witness']:
    r['dominant_bones']=[max([(mesh.vertex_groups[a.group].name,a.weight) for a in mesh.data.vertices[int(i)].groups],key=lambda a:a[1])[0] for i in r['witness']['vertices']]
  survey.append(dict(version=tag,time=t,illegal=illegal,active=[dict(id=n['note_id'],key=n['note_name'],finger=n['finger'],contact=s.contact(V,KEYS[n['key_index']],'R',n['finger']),pad_neutral=s.key_local(V[[c.MARKERS['R'][n['finger']-1]['mesh_vertex']]],KEYS[n['key_index']])[0]) for n in active],q={d:s.degrees(d) for d in DIGITS},self_count=len(selfpairs(V))))
save('BOUNDARY_AND_FINGER_SURVEY.json',dict(rows=survey,events=[n for n in NOTES if 1.9<n['note_on']<=3.8 or 2.1<n['note_off']<=3.8],B01=dict(core=[1.1,1.4214275],edit=[.9,1.705713],review=[.9,1.75],overlaps=False,status='FAIL retained; no candidate loaded')))
sc,rig,mesh,left,lrig=s.open_scene(STARTCOPY);g.init()
BASE_ACTION=rig.animation_data.action
NATIVE={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]};OTHER=s.protected_state(True)
save('PROTECTED_BEFORE.json',dict(files=[dict(path=p,sha256=h) for p,h in READS.items()]))
protection('SURVEY_INPUT_RECEIPT.json')
print('BOUNDARY_SURVEY',json.dumps([dict(version=r['version'],t=r['time'],keys=[(k,round(v['depth_mm'],4),v.get('dominant_bones')) for k,v in r['illegal'].items()],active=[(n['id'],n['pad_neutral'].tolist()) for n in r['active']],self=r['self_count']) for r in survey],ensure_ascii=False),flush=True)
