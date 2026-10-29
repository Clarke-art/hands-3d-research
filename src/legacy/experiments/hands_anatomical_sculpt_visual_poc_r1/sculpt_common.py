import sys,os,json,hashlib,ast,math,types,time
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[1]; PARENT=ROOT/'experiments/hands_local_skin_asset_repair_poc_r1'
PREV=ROOT/'experiments/hands_index_root_webspace_anatomy_repair_r1'
POSE=ROOT/'experiments/hands_anatomical_whole_hand_pose_repair_r1'
C1=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance'
OLD=ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'
os.environ.update(TEMP=str(OUT),TMP=str(OUT),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
READS={};HASHING=False
def safe(p):
 p=Path(p).absolute()
 assert p.is_relative_to(ROOT),'OUTSIDE_HANDS'
 assert not any(a.is_symlink() or a.is_junction() for a in [p,*p.parents] if a.is_relative_to(ROOT)),'REPARSE_FORBIDDEN'
 assert p.resolve().is_relative_to(ROOT),'PATH_ESCAPE'
 return p
def sha(p):
 global HASHING
 old=HASHING;HASHING=True
 try:
  h=hashlib.sha256()
  with safe(p).open('rb') as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  return h.hexdigest()
 finally:HASHING=old
def guard(event,args):
 if event not in ['open','os.listdir','os.scandir','os.mkdir','os.remove','os.rename'] or not args or not isinstance(args[0],(str,bytes,os.PathLike)):return
 raw=Path(os.fsdecode(args[0])).absolute()
 assert '/3d interactive components/piano' not in raw.as_posix().lower(),'PIANO_FORBIDDEN'
 if str(raw).upper()=='NUL':return
 p=safe(raw) if raw.is_relative_to(ROOT) else raw.resolve()
 writing=event in ['os.mkdir','os.remove','os.rename']
 if event=='open':
  mode,flags=args[1:3];writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
 if writing:assert p.is_relative_to(OUT),'WRITE_OUTSIDE_TRIAL'
 if event=='open' and not writing and not HASHING and p.is_relative_to(ROOT) and not p.is_relative_to(OUT) and p.is_file() and str(p) not in READS:READS[str(p)]=sha(p)
sys.addaudithook(guard)
def read(p):return json.loads(safe(p).read_text(encoding='utf-8-sig'))
def encode(x):return x.tolist() if hasattr(x,'tolist') else x.item() if hasattr(x,'item') else str(x)
def save(n,x):
 with (OUT/n).open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2,default=encode,allow_nan=False)
def extract(p,names,ns):
 tr=ast.parse(safe(p).read_text(encoding='utf8'));nodes=[n for n in tr.body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(nodes)==len(names)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns)
def protection(n):
 rows=[{'path':p,'before':h,'after':sha(p),'unchanged':sha(p)==h} for p,h in READS.items()];assert all(x['unchanged'] for x in rows);save(n,{'all_unchanged':True,'piano_access':False,'files':rows})
MAN=read(C1/'SCENE_MANIFEST.json');SOURCE=safe(MAN['path']);FIXED=POSE/'ROUND_2_STATIC_NOT_APPROVED.blend'
assert sha(SOURCE)==MAN['sha256']=='d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7'
PROPOSAL=read(PARENT/'CONFIRMED_ROI_PROPOSAL.json')
for r in read(OUT/'PROTECTED_BEFORE.json'):
 assert sha(r['path'])==r['sha256'];READS[r['path']]=r['sha256']
READS[str(SOURCE)]=sha(SOURCE);READS[str(FIXED)]=sha(FIXED)
NOTES=read(C1/'PERFORMANCE_TIMELINE.json')['notes']
import numpy as np,bpy
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
c=types.ModuleType('readonly_helpers');hp=ROOT/'experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/blender_helpers.py';exec(compile(safe(hp).read_text(encoding='utf8'),str(hp),'exec'),c.__dict__)
c.DIGITS=['THUMB','INDEX','MIDDLE','RING','LITTLE'];c.RIG=read(OLD/'RIG_CANONICAL_PROBE_R1.json');c.MARKERS={s:read(OLD/'FINGERTIP_CONTACT_MARKERS_R1.json')['markers'][s] for s in ['R','L']};c.SETUPS={(s,d):c.digit_setup(s,d) for s in ['R','L'] for d in c.DIGITS}
KEYS=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys']
TOPO=read(PREV/'NATIVE_TOPOLOGY.json');F=np.array(TOPO['faces'],int);E=np.array(TOPO['edges'],int)
SCOPE=read(OUT/'SCULPT_SCOPE_ACTIVE_BEFORE_EDIT.json')
A=np.array(SCOPE['patches']['A']['all_editable_vertex_ids']);B=np.array(SCOPE['patches']['B']['all_editable_vertex_ids']);S=np.array(SCOPE['S_core_vertex_ids'])
assert not (set(A)&set(S) or set(B)&set(S))
T=np.r_[F[:,[0,1,2]],F[:,[0,2,3]]]
def open_scene(p):
 bpy.ops.wm.open_mainfile(filepath=str(safe(p)),load_ui=False,use_scripts=False)
 assert not bpy.data.libraries,'EXTERNAL_LIBRARY_FORBIDDEN'
 sc=bpy.data.scenes[MAN['scene']];bpy.context.window.scene=sc
 for seq in [bpy.data.images,bpy.data.sounds,bpy.data.fonts]:
  for ob in seq:
   if getattr(ob,'filepath','') and not getattr(ob,'packed_file',None) and ob.filepath not in ['<builtin>','Bfont']:
    pp=safe(bpy.path.abspath(ob.filepath))
    if pp.is_file():READS[str(pp)]=sha(pp)
 mesh=bpy.data.objects[MAN['mapping']['R']['mesh']];rig=bpy.data.objects[MAN['mapping']['R']['rig']];left=bpy.data.objects[MAN['mapping']['L']['mesh']]
 return sc,mesh,rig,left
def coords(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 try:
  me.calc_loop_triangles()
  return np.array([list(<REDACTED_EMAIL>) for v in me.vertices]),np.array([list(t.vertices) for t in me.loop_triangles]),np.array([list(f.vertices) for f in me.polygons])
 finally:ev.to_mesh_clear()
def weights(mesh):
 names=[g.name for g in mesh.vertex_groups];w=np.zeros((len(mesh.data.vertices),len(names)))
 for v in mesh.data.vertices:
  for g in v.groups:w[v.index,g.group]=g.weight
 return names,w
def normals(v):
 p=v[F];n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0])+np.cross(p[:,2]-p[:,0],p[:,3]-p[:,0]);vn=np.zeros_like(v)
 for j in range(4):np.add.at(vn,F[:,j],n)
 return vn/np.maximum(np.linalg.norm(vn,axis=1)[:,None],1e-20)
def jacobians(mesh,rig):
 names,w=weights(mesh);out=np.zeros((len(w),3,3))
 for j,name in enumerate(names):
  if name not in rig.pose.bones:continue
  mat=<REDACTED_EMAIL>[name]<REDACTED_EMAIL>[name].matrix_local.inverted()@rig.matrix_world.inverted()@mesh.matrix_world
  out+=w[:,j,None,None]*np.array(mat)[:3,:3]
 return out
def payload(action):
 curves=[f for l in action.layers for s in l.strips for bag in s.channelbags for f in bag.fcurves]
 return [dict(path=f.data_path,index=f.array_index,extrapolation=f.extrapolation,keys=[dict(co=list(k.co),interpolation=k.interpolation,left=list(k.handle_left),right=list(k.handle_right),lt=k.handle_left_type,rt=k.handle_right_type) for k in f.keyframe_points]) for f in curves]
def signature(mesh,rig,left):
 uv={l.name:[list(d.uv) for d in l.data] for l in mesh.data.uv_layers}
 return {'actions':{a.name:c.digest(payload(a)) for a in bpy.data.actions},'bones':c.digest(c.native(mesh,rig)['bones']),'uv':c.digest(uv),'left':c.digest(c.native(left,bpy.data.objects[MAN['mapping']['L']['rig']])),'face':c.digest([list(f.vertices) for f in mesh.data.polygons]),'smooth':[f.use_smooth for f in mesh.data.polygons],'drivers':c.digest(c.native(mesh,rig)['corrective_drivers']),'modifiers':[(m.name,m.type,getattr(m,'use_deform_preserve_volume',None)) for m in mesh.modifiers]}
