import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
from skin_proxy import *
from scipy.spatial.transform import Rotation
from triangle_distance import distances
def read(name):return json.loads((O/name).read_text(encoding='utf-8-sig'))
def dump(name,x):(O/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=read('ANATOMY_CONSTRAINT_PROPOSAL.json');orig=json.loads(json.dumps(p))
for k in ['B2_reason','B2_seed','B2_non_target_constraint','B2_constraint_confidence']:orig['experiment'].pop(k,None)
oldbytes=(json.dumps(orig,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode()
assert hashlib.sha256(oldbytes).hexdigest()==read('B_SOLVE_1.json')['proposal_sha256']
(O/'ANATOMY_CONSTRAINT_PROPOSAL_B1_LOCK.json').write_bytes(oldbytes)
data=read('ACTUAL_RIG_ANATOMY.json');canon_error=0.;summary=[]
reference=next(r for r in data['rows'] if r['label']=='FROZEN_R2_REST')['digits'][2]['joints'][0]
H=np.array(reference['rest_local_matrix'])@np.linalg.inv(np.array(c.RIG['R']['bones'][reference['bone']]['matrix']))
for row in data['rows']+[read('B_ACTUAL_1.json')['actual_anatomy'],read('B_ACTUAL_2.json')['actual_anatomy']]:
 for digit in row['digits']:
  for j in digit['joints']:
   quat=Rotation.from_matrix(np.array(j['basis_rotation'])).as_quat()
   j['twist_about_rest_longitudinal_Y_deg']=float(np.degrees(2*np.arctan2(quat[1],quat[3])))
   if row['hand']=='R':canon_error=max(canon_error,float(np.max(abs(np.array(j['rest_local_matrix'])<REDACTED_EMAIL>(c.RIG['R']['bones'][j['bone']]['matrix'])))))
 middle=next(d for d in row['digits'] if d['digit']=='MIDDLE')
 summary.append(dict(label=row['label'],middle_MCP_spread_deg=middle['controls_recovered_deg'][3],middle_MCP_heading_deg=middle['joints'][0]['palm_heading_deg'],middle_MCP_longitudinal_twist_component_deg=middle['joints'][0]['twist_about_rest_longitudinal_Y_deg'],PIP_off_axis_increment_rotation_error=middle['joints'][1]['off_model_rotation_matrix_error'],DIP_off_axis_increment_rotation_error=middle['joints'][2]['off_model_rotation_matrix_error']))
assert canon_error<1e-6
data['canonical_rest_matrix_max_error']=canon_error
dump('ACTUAL_RIG_ANATOMY.json',data)
# Supplement is an angle convention refinement on recorded rotations, no new optimization.
out=dict(canonical_rest_matrix_error=canon_error,canonical_to_actual_armature_rest_frame=H.tolist(),frame_alignment_note='Canonical probe is in a different global coordinate frame. One common near-rigid transform aligns every right-hand rest bone; local axis controls are unchanged.',angle_summary=summary,MCP_spread_axis_longitudinal_component=float(c.SETUPS['R','MIDDLE'][3][1]),meaning='Quaternion swing-twist component about rest bone longitudinal Y; not a clinical axial rotation angle. Spread about canonical Z is oblique to the curved rest bone.',no_new_solve=True)
for ai in [1,2]:
 r=read(f'B_SOLVE_{ai}.json');a=read(f'B_ACTUAL_{ai}.json');snap=np.load(O/f'B_ACTUAL_SKIN_{ai}.npz')
 a['proxy_actual_max_vertex_error_mm']=float(np.linalg.norm(snap['vertices']-skin(np.array(r['state'])),axis=1).max()*1000)
 a['actual_anatomy']=next(x for x in [read('B_ACTUAL_1.json')['actual_anatomy'],read('B_ACTUAL_2.json')['actual_anatomy']] if x['label']==f'B_{ai}')
 # Add swing-twist metrics to independent actual anatomy.
 for d in a['actual_anatomy']['digits']:
  for j in d['joints']:
   quat=Rotation.from_matrix(np.array(j['basis_rotation'])).as_quat();j['twist_about_rest_longitudinal_Y_deg']=float(np.degrees(2*np.arctan2(quat[1],quat[3])))
 a['zero_non_target_intrusion']=a['actual_geometry']['wrong_key_or_nonpulp_max_depth_mm']==0.
 dump(f'B_ACTUAL_{ai}.json',a)
dump('ANGLE_AND_PARITY_SUPPLEMENT.json',out)
print('CANONICAL_REST_MATCH',canon_error,'spread axis longitudinal',out['MCP_spread_axis_longitudinal_component'])
for row in summary:print(row['label'],row['middle_MCP_spread_deg'],row['middle_MCP_heading_deg'],row['middle_MCP_longitudinal_twist_component_deg'])


