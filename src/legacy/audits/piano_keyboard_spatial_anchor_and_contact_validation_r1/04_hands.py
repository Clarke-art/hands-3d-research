import bpy,sys,json,hashlib,ast,importlib.util
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sp=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
tree=ast.parse((ROOT/'audits/pianovam_first_web_corrective_ab_isolation_r1/isolate.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='action_payload'],type_ignores=[]),'action_identity','exec'))
tree=ast.parse((ROOT/'audits/dual_hand_synchronized_real_motion_validation_r1/01_build_verify.py').read_text())
cfg=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='cfg' for t in n.targets))) if False else {}
# Extract the static cfg assignment (dict() calls contain only literal named fields).
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='cfg' for t in n.targets)],type_ignores=[]),'approved_sources','exec'))
digits=['THUMB','INDEX','MIDDLE','RING','LITTLE'];expected={'R':'b03d02e4f9f4f624c6c3faf1c1c1d53d717eac4770a216d3b1f54af89672cdb0','L':'d3061e8effcb6f7ad0a7759ae0f9aa75a196d295a072e83c617a2c8ce4c29ac8'}
markers={};frames={};arrays={};static={};identities={};faces={};smooth={};body_regions={}
def intrinsic(ob,rig):
 x=h.core(ob,rig)
 for k in ['mesh_object','armature_object']:x[k].pop('collections')
 x['armature_object'].pop('animation');x.pop('pose_state')
 for m in x['modifiers']:m['settings'].pop('is_override_data',None)
 # Corrective runtime values can change; geometry and drivers remain protected.
 for b in x['corrective_geometry_and_driver']['blocks']:b['settings'].pop('value',None)
 return x
for side,c in cfg.items():
 assert sha(ROOT/c['baseline'])==c['sha'] and sha(ROOT/c['source'])==c['source_sha']
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/c['baseline']),load_ui=False,use_scripts=False)
 ob=bpy.data.objects[c['mesh']];rig=bpy.data.objects[c['rig']];h.neutral(rig)
 assert np.allclose(np.array(rig.matrix_world),np.eye(4))
 static[side]=intrinsic(ob,rig);V,F=h.coords(ob);faces[side]=F;smooth[side]=[f.use_smooth for f in ob.data.polygons]
 wrist=rig.data.bones['WRIST_'+side];w=np.array(wrist.head_local);Q=np.array(wrist.matrix_local.to_3x3()).T
 # The approved wrist frame's Z is dorsal; -Z is palmar. X is ulnar for R.
 assert np.linalg.det(Q)>.999
 frames[side]={'rotation':Q.tolist(),'native_wrist':w.tolist(),'static_scale':1,'definition':'wrist rest X -> keyboard low-high; Y longitudinal -> rear; Z dorsal -> up. Mirrored hand preserves wrist frame and reverses radial anatomy. No pose-dependent rotation.'}
 local=(V-w)@Q.T;body_regions[side]={'wrist_vertices':np.flatnonzero(local[:,1]<.045).tolist(),'palm_vertices':np.flatnonzero((local[:,1]>=.045)&(local[:,1]<.105)).tolist()}
 rows=[]
 for finger,digit in enumerate(digits,1):
  tip=rig.data.bones[digit+'_TIP_'+side];distal=tip.parent;tipco=np.array(tip.head_local);D=np.array(distal.matrix_local.to_3x3());axis=D[:,1];palmar=-Q[2];palmar=palmar-axis*np.dot(palmar,axis);palmar/=np.linalg.norm(palmar)
  target=tipco-axis*.003+palmar*.004
  candidates=np.flatnonzero((np.linalg.norm(V-tipco,axis=1)<.017)&((V-tipco)@palmar>.0005))
  assert len(candidates)>0
  vid=int(candidates[np.argmin(np.linalg.norm(V[candidates]-target,axis=1))]);point=Vector(V[vid]);pad=distal.matrix_local.inverted()@point
  rows.append({'finger':finger,'digit':digit,'semantic_tip':tip.name,'distal_frame':distal.name,'mesh_vertex':vid,'canonical_mesh_world_point':V[vid].tolist(),'local_pad_point':list(pad),'distance_to_tip_mm':float(np.linalg.norm(V[vid]-tipco)*1000),'palmar_projection_mm':float(np.dot(V[vid]-tipco,palmar)*1000),'selection':'Closest canonical surface vertex to TIP-3mm distal +4mm palmar, constrained to distal17mm palmar hemisphere; fixed once before action evaluation. No bone-head proxy.','AUDIT_ONLY':True})
 markers[side]=rows
 with bpy.data.libraries.load(str(ROOT/c['source']),link=False) as (a,b):b.actions=[c['action']]
 action=bpy.data.actions[c['action']];assert digest(action_payload(action))==expected[side]
 rig.animation_data_create();rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0]
 verts=[];pads=[];drifts=[]
 for i in range(421):
  bpy.context.scene.frame_set(1+i//2,subframe=(i%2)*.5);v,_=h.coords(ob);verts.append((v-w)@Q.T);pp=[]
  for r in rows:
   native=<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point']);pp.append((np.array(native)-w)@Q.T);drifts.append(float(np.linalg.norm(np.array(native)-v[r['mesh_vertex']])*1000))
  pads.append(pp)
 arrays[side+'_verts']=np.array(verts);arrays[side+'_pads']=np.array(pads)
 identities[side]={'action':action.name,'payload_sha256':digest(action_payload(action)),'expected':expected[side],'identity':'MATCH','source_file':c['source'],'source_sha256':sha(ROOT/c['source']),'pad_vs_corresponding_evaluated_vertex_max_mm':max(drifts)}
 rig.animation_data.action=None;h.neutral(rig);assert intrinsic(ob,rig)==static[side]
 print('EXTRACTED',side,'pad skin drift mm',max(drifts),flush=True)
dump('FINGERTIP_CONTACT_MARKERS_R1.json',{'type':'VIRTUAL_FINGERTIP_PAD_CONTACT_MARKER','AUDIT_ONLY':True,'new_bones':0,'hand_mesh_or_rig_mutation':False,'markers':markers,'limitation':'Rigid distal-frame point derived from actual palmar pad surface. Marker follows the distal frame; skin drift quantified separately. Not calibrated pressure center.'})
dump('HAND_EXTRACTION_R1.json',{'frames':frames,'faces':faces,'smooth':smooth,'body_regions':body_regions,'cfg':cfg,'identities':identities,'action_hashes':expected})
np.savez_compressed(P/'hand_motion_canonical.npz',**arrays)
dump('STATIC_COMPONENT_DIGESTS_R1.json',{s:digest(x) for s,x in static.items()})
dump('ACTION_IDENTITY_R1.json',{'hands':identities,'internal_action_operations':0,'phase':'EXTRACTED; save/reopen verification pending'})
