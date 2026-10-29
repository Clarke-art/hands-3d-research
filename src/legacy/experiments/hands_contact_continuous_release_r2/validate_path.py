"""Independent full-window actual-skin preflight, without an animation asset."""
import bpy,sys,ast,math
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from runtime import *
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
helper=R1/'baseline_blender.py'
save('ADDITIONAL_PROTECTED_BEFORE.json',{str(helper):sha(helper)})
tree=ast.parse(helper.read_text(encoding='utf8'))
defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['settime','vertices','degrees','pair']]
exec(compile(ast.Module(body=defs,type_ignores=[]),str(helper),'exec'))
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
sc=bpy.data.scenes[MAN['scene']];bpy.context.window.scene=sc;assert not bpy.data.libraries
rig=bpy.data.objects[MAN['mapping']['R']['rig']];mesh=bpy.data.objects[MAN['mapping']['R']['mesh']]
left=bpy.data.objects[MAN['mapping']['L']['rig']]
request=dict(np.load(OUT/'VALIDATION_REQUEST.npz'));rows=[];contacts=[];witness=[];source_qs=[];new_qs=[];root_error=0.;other_basis_error=0.;left_error=0.;bodychecks=0
M=read(R6/'SOURCE_MODEL_MANIFEST.json');all_rois=M['rois']
components=[]
for key in c.KEYS:
    for body in key['geometry']:
        verts=np.array(body['vertices']);center=verts.mean(0);planes=[]
        tris=np.asarray(body['triangles']).reshape(-1,3)
        for tri in tris:
            a,b,c0=verts[tri];normal=np.cross(b-a,c0-a);l=np.linalg.norm(normal)
            if l<1e-12:continue
            normal/=l
            if normal@(center-a)>0:normal=-normal
            planes.append(np.r_[normal,normal@a])
        planes=np.unique(np.round(planes,10),axis=0)
        components.append((key,body,verts,tris,planes))
def contacts_at(V,t):
    ns=[n for n in NOTES if n['hand']=='R' and n['note_on']<=t<n['note_off']]
    ns += [n for n in NOTES if n['hand']=='R' and n['finger']-1 in CHANGED and abs(t-n['note_off'])<1e-9]
    answer=[]
    for n in ns:
        key=c.KEYS[n['key_index']];ang=bpy.data.objects[MAN['key_pivots'][str(n['key_index'])]].rotation_euler.x;pv=np.array(key['press_pivot'])
        p=c.axisrot(-ang,[1,0,0])@(V[c.MARKERS['R'][n['finger']-1]['mesh_vertex']]-pv)+pv
        s=min(key['key_top_playable_surface'],key=lambda s:np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
        gap=float((p[2]-s['z'])*1000);miss=float(np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']]))*1000)
        answer.append(dict(t=float(t),event=n['note_id'],gap_mm=gap,horizontal_mm=miss,pass_=abs(gap)<=3 and miss<.03))
    return answer
def spatial(V0,V1,t,trees0,trees1):
    global bodychecks
    errors=[];surface_errors=[];lo=np.minimum(V0.min(0),V1.min(0));hi=np.maximum(V0.max(0),V1.max(0))
    for key,body,kv,tris,pl in components:
        ang=bpy.data.objects[MAN['key_pivots'][str(key['key_index'])]].rotation_euler.x if str(key['key_index']) in MAN['key_pivots'] else 0
        R=c.axisrot(ang,[1,0,0]);pv=np.array(key['press_pivot']);world=(kv-pv)@R.T+pv
        if np.any(world.max(0)<lo) or np.any(world.min(0)>hi):continue
        bodychecks+=1;local0=(V0-pv)@R+pv;local1=(V1-pv)@R+pv
        dep0=-np.max(local0@pl[:,:3].T-pl[:,3],1)*1000;dep1=-np.max(local1@pl[:,:3].T-pl[:,3],1)*1000
        for d,roi in all_rois.items():
            ids=np.array(roi['vertices']);excess=dep1[ids]-np.maximum(.5,dep0[ids]);bad=np.flatnonzero((dep1[ids]>.5)&(excess>.02))
            if len(bad):
                vid=int(ids[bad[np.argmax(excess[bad])]])
                errors.append(dict(t=float(t),digit=d,key=key['midi_note'],component=body['name'],vertex=vid,
                    depth_mm=float(dep1[vid]),source_depth_mm=float(dep0[vid]),increase_mm=float(dep1[vid]-dep0[vid]),world_m=V1[vid].tolist()))
        keytree=BVHTree.FromPolygons([Vector(v) for v in world],tris.tolist(),all_triangles=True,epsilon=0)
        for d in ['MIDDLE','RING']:
            oldpairs=trees0[d].overlap(keytree);newpairs=trees1[d].overlap(keytree)
            owned=any(n['hand']=='R' and c.DIGITS[n['finger']-1]==d and n['midi_note']==key['midi_note'] and n['note_on']<=t<=n['note_off'] for n in NOTES)
            if not oldpairs and newpairs and not owned:
                surface_errors.append(dict(t=float(t),digit=d,key=key['midi_note'],component=body['name'],new_triangle_pairs=len(newpairs),source_triangle_pairs=0))
    return errors,surface_errors
modified={name for j in CHANGED for name in c.SETUPS['R',c.DIGITS[j]][0]}
for k,t in enumerate(request['times']):
    settime(float(t));V0,F=vertices();sourceq=np.array([degrees(d) for d in c.DIGITS]);source_qs.append(sourceq)
    basis0={b.name:np.array(b.matrix_basis) for b in rig.pose.bones};root0=np.array(rig.matrix_world);left0=np.array([np.array(b.matrix_basis) for b in left.pose.bones])
    for jj,j in enumerate(CHANGED):
        d=c.DIGITS[j];qtarget=sourceq[j]+request['delta_deg'][k,jj]
        before=c.joint_mats('R',d,np.radians(sourceq[j]));after=c.joint_mats('R',d,np.radians(qtarget))
        for name,a,b in zip(c.SETUPS['R',d][0],before,after):
            old=np.array(rig.pose.bones[name].rotation_quaternion.to_matrix());rig.pose.bones[name].rotation_quaternion=Matrix((b@a.T@old).tolist()).to_quaternion()
    bpy.context.view_layer.update();V1,_=vertices();q1=np.array([degrees(d) for d in c.DIGITS]);new_qs.append(q1)
    allverts0=[Vector(v) for v in V0];allverts1=[Vector(v) for v in V1]
    trees0={d:BVHTree.FromPolygons(allverts0,ROIS[d]['faces'],epsilon=0) for d in ROIS}
    trees1={d:BVHTree.FromPolygons(allverts1,ROIS[d]['faces'],epsilon=0) for d in ROIS}
    pairs0=len(trees0['MIDDLE'].overlap(trees0['RING']));pairs1=len(trees1['MIDDLE'].overlap(trees1['RING']))
    neighbor=[]
    for a,b in [('INDEX','MIDDLE'),('RING','LITTLE'),('INDEX','RING'),('MIDDLE','LITTLE')]:
        ca=len(trees0[a].overlap(trees0[b]));cb=len(trees1[a].overlap(trees1[b]))
        if cb>ca:neighbor.append(dict(pair=a+'_'+b,source_pairs=ca,new_pairs=cb))
    keyrows,surfaces=spatial(V0,V1,float(t),trees0,trees1)
    active=contacts_at(V1,float(t));contacts.extend(active)
    root_error=max(root_error,float(abs(np.array(rig.matrix_world)-root0).max()))
    other_basis_error=max(other_basis_error,max(float(abs(np.array(b.matrix_basis)-basis0[b.name]).max()) for b in rig.pose.bones if b.name not in modified))
    left_error=max(left_error,float(abs(np.array([np.array(b.matrix_basis) for b in left.pose.bones])-left0).max()))
    row=dict(t=float(t),source_pairs=pairs0,new_pairs=pairs1,contact_failures=sum(not r['pass_'] for r in active),key_regression_count=len(keyrows),new_key_surface_crossings=len(surfaces),neighbor_regressions=neighbor)
    rows.append(row)
    if keyrows or surfaces or pairs1 or neighbor:
        witness.append(dict(**row,key_witnesses=keyrows[:4],surface_witnesses=surfaces[:4],pair_faces=[[ROIS['MIDDLE']['faces'][a],ROIS['RING']['faces'][b]] for a,b in trees1['MIDDLE'].overlap(trees1['RING'])[:2]]))
    if k%60==0:print('FULL_WINDOW_ACTUAL_PREFLIGHT',k,len(request['times']),flush=True)
qnew=np.array(new_qs);qold=np.array(source_qs);delta=qnew[:,CHANGED]-qold[:,CHANGED]
lo=np.array([0,0,0,-28]);hi=np.array([75,95,65,28]);domain=max(float((lo-qnew[:,CHANGED]).max()),float((qnew[:,CHANGED]-hi).max()),0)
speed=np.diff(delta,axis=0)/np.diff(request['times'])[:,None,None]
first=next((r['t'] for r in rows if r['new_pairs'] or r['contact_failures'] or r['key_regression_count'] or r['new_key_surface_crossings'] or r['neighbor_regressions']),None)
passed=first is None and domain<=.002 and abs(speed).max()<=180 and root_error<1e-7 and other_basis_error<1e-7 and left_error<1e-7
save('ACTUAL_PATH_VALIDATION.json',dict(pass_=bool(passed),rows=rows,contacts=contacts,witnesses=witness,
    samples=len(rows),first_failure_observed=first,max_skin_pairs=max(r['new_pairs'] for r in rows),
    skin_collision_samples=sum(r['new_pairs']>0 for r in rows),contact_failure_records=sum(not r['pass_'] for r in contacts),
    key_regression_samples=sum(r['key_regression_count']>0 for r in rows),surface_regression_samples=sum(r['new_key_surface_crossings']>0 for r in rows),
    domain_violation_deg=domain,added_velocity_sample_max_deg_sec=float(abs(speed).max()),root_matrix_error=root_error,other_basis_error=other_basis_error,left_basis_error=left_error,
    window_boundary_delta_deg=delta[[0,-1]],key_body_checks=bodychecks,
    scope='Full 0.788571s numeric preflight path replay; 240Hz + exact events + one deterministic close-interval midpoint pass. All 88 registered key components broad-phase tested; actual distal skin/key BVHs and pointwise body depths.',
    limitations='No continuous geometric proof; finite samples and localized distal ROI may miss smaller/other-region events. No Action or Blend exists.',
    candidate_count=0,saved_blends=0,new_actions=0,source_sha256=sha(SOURCE)))
np.savez_compressed(OUT/'ACTUAL_PATH_ANGLES.npz',times=request['times'],source_qdeg=qold,new_qdeg=qnew)
assert sha(helper)==read(OUT/'ADDITIONAL_PROTECTED_BEFORE.json')[str(helper)]
print('ACTUAL_CONTINUOUS_PREFLIGHT_RESULT',passed,'first',first,'peak_pair',max(r['new_pairs'] for r in rows),flush=True)
