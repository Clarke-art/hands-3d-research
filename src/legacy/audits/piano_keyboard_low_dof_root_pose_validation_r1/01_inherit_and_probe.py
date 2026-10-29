import bpy,sys,json,hashlib,shutil
import numpy as np
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];PRE=ROOT/'audits/piano_keyboard_spatial_anchor_and_contact_validation_r1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
names=['KEYBOARD_AUTHORITY_R1.json','KEYBOARD_COORDINATE_FRAME_R1.json','KEYBOARD_88_KEY_TABLE_R1.json','CONTACT_TOLERANCE_POLICY_R1.json','PERFORMANCE_TIMELINE_R1.json','FINGERTIP_CONTACT_MARKERS_R1.json','KEY_EVENT_ANIMATION_R1.json','FINGERING_AUTHORITY_R1.json']
identity={}
for n in names:
 shutil.copyfile(PRE/n,P/n);identity[n]={'source':str(PRE/n),'source_sha256':sha(PRE/n),'local_sha256':sha(P/n),'identity':'MATCHED'}
protected={}
for f,v in read(PRE/'PROTECTED_INPUTS_BEFORE_R1.json').items():
 if f.endswith('CANONICAL_UPRIGHT_ACTION_LATEST_STAGE.json'):continue
 assert sha(f)==v,('FROZEN_DRIFT',f);protected[f]=v
for f in PRE.iterdir():
 if f.is_file():protected[str(f)]=sha(f)
ex=read(PRE/'HAND_EXTRACTION_R1.json')
for c in ex['cfg'].values():assert sha(ROOT/c['source'])==c['source_sha'];protected[str(ROOT/c['source'])]=sha(ROOT/c['source'])
dump('PROTECTED_INPUTS_BEFORE_R1.json',protected);dump('INHERITED_IDENTITIES_R1.json',identity)
for n,file in [('PERFORMANCE_TIMELINE_IDENTITY_R1.json','PERFORMANCE_TIMELINE_R1.json'),('FINGERTIP_MARKER_IDENTITY_R1.json','FINGERTIP_CONTACT_MARKERS_R1.json')]:dump(n,identity[file])
bpy.ops.wm.open_mainfile(filepath=str(PRE/'PIANO_KEYBOARD_SPATIAL_ANCHOR_VALIDATION_CANDIDATE_R1.blend'),load_ui=False,use_scripts=False)
out={}
for s,c in ex['cfg'].items():
 rig=bpy.data.objects[c['rig']];Q=np.array(ex['frames'][s]['rotation']);w=np.array(ex['frames'][s]['native_wrist']);rows=[]
 for i in range(421):
  bpy.context.scene.frame_set(1+i//2,subframe=(i%2)*.5);b=rig.pose.bones['WRIST_'+s];R=<REDACTED_EMAIL>(b.matrix.to_3x3());long=R[:,1];up=R[:,2]
  rows.append({'heading_deg':float(np.degrees(np.arctan2(-long[0],long[1]))),'longitudinal_elevation_deg':float(np.degrees(np.arctan2(long[2],np.linalg.norm(long[:2])))),'dorsal_tilt_deg':float(np.degrees(np.arccos(np.clip(up[2]/np.linalg.norm(up),-1,1)))),'wrist_rotation_canonical':R.tolist()})
 rest=rig.data.bones;coords={n:(np.array(b.head_local)-w)@Q.T for n,b in rest.items()};width=float(np.linalg.norm(coords['INDEX_MCP_'+s]-coords['LITTLE_MCP_'+s]));length=float(np.linalg.norm(coords['MIDDLE_MCP_'+s]-coords['WRIST_'+s]));out[s]={'source_wrist_observations':rows,'canonical_palm_width_m':width,'canonical_wrist_to_middle_mcp_m':length,'wrist_head_canonical':coords['WRIST_'+s].tolist(),'middle_mcp_canonical':coords['MIDDLE_MCP_'+s].tolist(),'index_mcp_canonical':coords['INDEX_MCP_'+s].tolist(),'little_mcp_canonical':coords['LITTLE_MCP_'+s].tolist()}
dump('PRE_SOLVE_ORIENTATION_EVIDENCE_R1.json',out)
print(json.dumps({s:{'heading_range':list(np.min([[r['heading_deg'],r['longitudinal_elevation_deg'],r['dorsal_tilt_deg']] for r in v['source_wrist_observations']],axis=0))+list(np.max([[r['heading_deg'],r['longitudinal_elevation_deg'],r['dorsal_tilt_deg']] for r in v['source_wrist_observations']],axis=0)),'palm_width':v['canonical_palm_width_m'],'palm_length':v['canonical_wrist_to_middle_mcp_m']} for s,v in out.items()},indent=2))
