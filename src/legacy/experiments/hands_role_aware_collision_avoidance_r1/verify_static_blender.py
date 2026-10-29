"""Independent non-candidate static replay; never bake/create an Action."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
prefix=Path(__file__).with_name('baseline_blender.py').read_text(encoding='utf8').split('uniform=')[0]
exec(compile(prefix,str(Path(__file__).with_name('baseline_blender.py')),'exec'))
from mathutils import Matrix
result=read(OUT/'STATIC_PREFLIGHT_VERIFIED_RESULT.json')
data=dict(np.load(OUT/'STATIC_PREFLIGHT_VERIFIED.npz'))
model_manifest=read(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOURCE_MODEL_MANIFEST.json')
all_rois=model_manifest['rois'];rows=[];states=[]
def contact_of(V,n):
    key=c.KEYS[n['key_index']];ang=bpy.data.objects[MAN['key_pivots'][str(n['key_index'])]].rotation_euler.x
    pv=np.array(key['press_pivot']);pt=V[c.MARKERS['R'][n['finger']-1]['mesh_vertex']]
    p=c.axisrot(-ang,[1,0,0])@(pt-pv)+pv
    surfaces=key['key_top_playable_surface'];s=min(surfaces,key=lambda s:np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
    gap=(p[2]-s['z'])*1000;miss=np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']]))*1000
    return dict(gap_mm=float(gap),horizontal_mm=float(miss),pass_original_contact=abs(gap)<=3 and miss<.03)
def key_hits(V):
    hits={};witness={}
    for key in c.KEYS:
        ang=bpy.data.objects[MAN['key_pivots'][str(key['key_index'])]].rotation_euler.x if str(key['key_index']) in MAN['key_pivots'] else 0
        pv=np.array(key['press_pivot']);local=(V-pv)@c.axisrot(ang,[1,0,0])+pv
        for g in key['geometry']:
            gv=np.array(g['vertices']);center=gv.mean(0);planes=[]
            for tri in np.asarray(g['triangles']).reshape(-1,3):
                a,b,c0=gv[tri];normal=np.cross(b-a,c0-a);l=np.linalg.norm(normal)
                if l<1e-12:continue
                normal/=l
                if normal@(center-a)>0:normal=-normal
                planes.append(np.r_[normal,normal@a])
            planes=np.unique(np.round(planes,10),axis=0)
            depth=-np.max(local@planes[:,:3].T-planes[:,3],axis=1)*1000
            for digit,roi in all_rois.items():
                ids=np.array(roi['vertices']);i=ids[int(np.argmax(depth[ids]))];d=max(0,float(depth[i]))
                label=digit+':'+str(key['midi_note'])+':'+g['name']
                hits[label]=d
                if d>.5:witness[label]=dict(digit=digit,midi=key['midi_note'],component=g['name'],depth_mm=d,
                    vertex=int(i),world_point_m=V[i].tolist(),key_local_point_m=local[i].tolist())
    return hits,witness

for k,t in enumerate(data['times']):
    settime(float(t));sourceV,F=vertices();sourceBasis={b.name:np.array(b.matrix_basis) for b in rig.pose.bones};root=np.array(rig.matrix_world)
    source_pairs=pair(sourceV);olddepth,oldwitness=key_hits(sourceV)
    for j in [SCOPE['new']['finger']-1,SCOPE['old']['finger']-1]:
        d=c.DIGITS[j]
        for name,rot in zip(c.SETUPS['R',d][0],c.joint_mats('R',d,np.radians(data['qdeg'][k,j]))):
            rig.pose.bones[name].rotation_quaternion=Matrix(rot.tolist()).to_quaternion()
    bpy.context.view_layer.update();newV,_=vertices();newpairs=pair(newV);newdepth,newwitness=key_hits(newV)
    modified={n for j in [SCOPE['new']['finger']-1,SCOPE['old']['finger']-1] for n in c.SETUPS['R',c.DIGITS[j]][0]}
    untouched=max(float(np.max(abs(np.array(b.matrix_basis)-sourceBasis[b.name]))) for b in rig.pose.bones if b.name not in modified)
    regressions=[dict(**newwitness[label],source_depth_mm=olddepth[label],increase_mm=depth-olddepth[label])
        for label,depth in newdepth.items() if depth>.5 and depth-olddepth[label]>.02]
    active=[n for n in NOTES if n['hand']=='R' and n['note_on']<=t<n['note_off']]
    if abs(t-SCOPE['old']['note_off'])<1e-9:active.append(SCOPE['old'])
    contacts=[dict(event=n['note_id'],source=contact_of(sourceV,n),new=contact_of(newV,n)) for n in active]
    qactual=np.array([degrees(d) for d in c.DIGITS]);delta=qactual-data['source_qdeg'][k]
    row=dict(t=float(t),source_middle_ring=source_pairs,new_middle_ring=newpairs,contacts=contacts,
        key_regressions=regressions,inherited_source_key_witnesses=list(oldwitness.values()),
        unmodified_bone_basis_max_error=untouched,root_matrix_max_error=float(np.max(abs(np.array(rig.matrix_world)-root))),
        numeric_angle_vs_actual_max_error_deg=float(np.max(abs(qactual-data['qdeg'][k]))),
        max_abs_correction_deg=float(np.max(abs(delta))),max_spread_correction_deg=float(np.max(abs(delta[:,3]))),
        pass_=newpairs['triangle_pairs']==0 and not regressions and all(r['new']['pass_original_contact'] for r in contacts) and untouched<1e-7)
    rows.append(row);states.append((sourceV,newV))
np.savez_compressed(OUT/'STATIC_ACTUAL_SKIN.npz',times=data['times'],source=np.array([r[0] for r in states]),new=np.array([r[1] for r in states]))
save('STATIC_ACTUAL_VALIDATION.json',dict(rows=rows,pass_=all(r['pass_'] for r in rows),
    original_contact_gate=dict(vertical_abs_mm=3,horizontal_mm=.03,source='C2 06_apply_validate.py line94'),
    distinction='Planner 2.05mm is a stricter feasibility target; original contact is independently evaluated at 3mm, no retuning performed',
    spatial_scope='Actual same C3 distal skin BVHs; full-hand digit ROI vertices against all 88 registered convex key components at 3 static anchors',
    limitations='No animated trajectory, no continuous collision proof; vertex-body tests cannot exclude all triangle-only crossings',
    new_actions=0,saved_blends=0,new_dynamic_candidates=0,source_sha256=sha(SOURCE)))
save('STOP_GATE.json',dict(status='FAIL',reason='Single valid finite role/corridor feasibility batch failed actual skin/contact/key non-regression; no dynamic candidate authorized by gate',
    dynamic_candidate_count=0,valid_static_optimizer_calls=1,invalid_development_optimizer_calls=1,
    no_second_dynamic_candidate=True,root_expansion=False,R3_started=False))
print('ACTUAL_STATIC_STOP',[(r['t'],r['new_middle_ring']['triangle_pairs'],len(r['key_regressions'])) for r in rows],flush=True)
