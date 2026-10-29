import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import support as s
from support import *
prior=read(ROOT/'audits/hands_fingertip_key_alignment_diagnostic_r1/FINAL_INPUT_SHA_RECEIPT.json')
protected=[r['path'] for r in prior['files']]
for side in ['R','L']:protected.append(str(ROOT/c.RIG[side]['baseline']))
for p in protected:READS[str(safe(p))]=sha(p)
save('PROTECTED_BEFORE.json',dict(files=[dict(path=p,sha256=h) for p,h in READS.items()],piano_access=False))
sc,rig,mesh,left,lrig=s.open_scene(SOURCE)
sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']]
bounds=read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg']
rs=[]
for t in [0.,.17,.35,26/60,.6,.8,.812856,.992856,1.1,1.207142,1.247142,2.45,2.6,2.9,3.15]:
 c.settime(sc,t);V,T,F=s.coords_tri(mesh)
 rs.append(dict(time=t,qdeg=s.degrees('INDEX'),palm_world=np.array(rig.matrix_world),wrist=np.array(rig.pose.bones['WRIST_R'].matrix),index_pad=V[1750],active=[dict(hand=n['hand'],finger=n['finger'],key=n['note_name']) for n in NOTES if n['note_on']<=t<n['note_off']]))
save('MINIMAL_FACTS.json',dict(joint_names=c.SETUPS['R','INDEX'][0],axes=c.SETUPS['R','INDEX'][2],spread=c.SETUPS['R','INDEX'][3],bounds_deg=bounds,index_bones=[dict(name=b.name,mode=b.rotation_mode,constraints=[dict(name=x.name,type=x.type) for x in b.constraints]) for b in rig.pose.bones if b.name.startswith('INDEX_')],notes=[n for n in NOTES if n['hand']=='R' and n['finger']==2],samples=rs,camera=dict(name=sc.camera.name,type=sc.camera.data.type,matrix=np.array(sc.camera.matrix_world),scale=sc.camera.data.ortho_scale),external_libraries=len(bpy.data.libraries),sounds=[dict(path=a.filepath,packed=bool(a.packed_file)) for a in bpy.data.sounds],modifiers=[dict(name=m.name,type=m.type) for m in mesh.modifiers]))
save('BASELINE_PROTECTED_MEMORY.json',dict(actions=s.protected_state(),native={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}))
protection('FACTS_INPUT_RECEIPT.json')
print('FACTS',json.dumps(dict(bounds=bounds,index_samples=[dict(time=r['time'],q=r['qdeg'].tolist(),pad=r['index_pad'].tolist()) for r in rs]),ensure_ascii=False),flush=True)
