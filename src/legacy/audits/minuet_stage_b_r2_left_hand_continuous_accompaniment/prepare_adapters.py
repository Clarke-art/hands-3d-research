from stage_common import *
assert not (P/'CANDIDATE_ATTEMPT.json').exists()
text=(B1/'03_generate.py').read_text(encoding='utf8').replace('from left_chord_motion import *','from left_continuous_motion import *')
start=text.index('taskidx=np.zeros(');stop=text.index('angles=np.array(',start)
replacement="""taskidx=np.zeros((K,5,2),int);taskweights=np.zeros((K,5));lifts=np.zeros((K,5,2));factors=np.zeros((K,5,2));taskrows=[]
for k,t in enumerate(knots):
    rows=co.task_components(float(t));taskrows.append(rows)
    for r in rows:
        j=r['finger'];taskweights[k,j]=r['weight']
        for z,(i,lift,factor) in enumerate(r['components']):taskidx[k,j,z]=i;lifts[k,j,z]=lift;factors[k,j,z]=factor
"""
text=text[:start]+replacement+text[stop:]
text=text.replace('angles[np.arange(K)[:,None],tkey[taskidx]]','angles[np.arange(K)[:,None,None],tkey[taskidx]]')
start=text.index('for k,tasks in enumerate(taskrows):');stop=text.index('lo,hi=co.boxlo,co.boxhi',start)
text=text[:start]+"""for k,rows in enumerate(taskrows):
    for r in rows:
        for i,lift,factor in r['components']:
            if r['weight']>1 and factor>.1:margin[k,r['finger'],np.array(co.boxkeys)==events[i]['midi_note']]=0
"""+text[stop:]
text=text.replace('pernode=15+5*len(co.boxkeys)+10+20+3+3+5','pernode=15+5*len(co.boxkeys)+10+20+3+3+5+8')
text=text.replace("targets=np.einsum('kdij,kdj->kdi',taskrot,point-taskpivot)+taskpivot;targets[:,:,2]+=lifts",
    "component_points=np.einsum('kdcij,kdcj->kdci',taskrot,point-taskpivot)+taskpivot;component_points[:,:,:,2]+=lifts\n    targets=np.sum(component_points*factors[:,:,:,None],axis=2)")
old='pose=np.c_[contact,collision,jointclear,prior,states[:,3:6]*.20,rootprior,passive]'
new="""idle_rows=[];q=states[:,6:].reshape(K,5,4)
    for j,label in [(1,'LEFT_IDLE_INDEX'),(3,'LEFT_IDLE_RING')]:
        lim=np.array(o.SP['joint_increment_bounds_deg'][label]);idle=1-np.clip(taskweights[:,j]/pol['prepare_weight'],0,1)
        idle_rows.append((np.maximum(lim[0]-q[:,j],0)+np.maximum(q[:,j]-lim[1],0))*idle[:,None]*pol['idle_domain_weight'])
    pose=np.c_[contact,collision,jointclear,prior,states[:,3:6]*.20,rootprior,passive,*idle_rows]"""
assert old in text;text=text.replace(old,new)
text=text.replace("for j,i,lift,w in taskrows[k]:cols.extend([K*26+2*i,K*26+2*i+1])",
    "for r in taskrows[k]:\n        for i,lift,factor in r['components']:cols.extend([K*26+2*i,K*26+2*i+1])")
text=text.replace("sha(P/'left_chord_motion.py')","sha(P/'left_continuous_motion.py')")
(P/'03_generate.py').write_text(text,encoding='utf8')
text=(B1/'04_scene.py').read_text(encoding='utf8')
text=text.replace('STAGE_B_LEFT_TRIAD_DESIGN_ONLY_R1.blend','STAGE_B_R2_LEFT_CONTINUOUS_DESIGN_ONLY.blend').replace('STAGE_B_LEFT_TRIAD_ONLY_R1','STAGE_B_R2_LEFT_CONTINUOUS_ONLY')
text=text.replace('DESIGN_ONLY_STAGE_B_LEFT_TRIAD_JOINTS','DESIGN_ONLY_STAGE_B_R2_LEFT_CONTINUOUS_JOINTS').replace('DESIGN_ONLY_STAGE_B_LEFT_TRIAD_ROOT','DESIGN_ONLY_STAGE_B_R2_LEFT_CONTINUOUS_ROOT')
text=text.replace("for n in tl['notes']:\n    data=bpy.data.curves.new", "for midi in sorted(set(n['midi_note'] for n in tl['notes'])):\n    n=next(n for n in tl['notes'] if n['midi_note']==midi)\n    data=bpy.data.curves.new")
text=text.replace('LEFT_TRIAD_NOTE_','LEFT_ACCOMP_NOTE_')
(P/'04_scene.py').write_text(text,encoding='utf8')
(P/'06_render.py').write_text((B1/'06_render.py').read_text(encoding='utf8').replace('left_triad_only=True','left_four_bar_only=True'),encoding='utf8')
text=(B1/'07_audio.py').read_text(encoding='utf8').replace('voices=3','voices=len(TL[\'notes\'])').replace("source_chord_duration_sec=","source_music_duration_sec=")
(P/'07_audio.py').write_text(text,encoding='utf8')
(P/'09_framing_verify.py').write_text((B1/'09_framing_verify.py').read_text(encoding='utf8'),encoding='utf8')
# Finite pre-generation actual skin readback, not a dynamic candidate.
text=(B1/'02_static_readback.py').read_text(encoding='utf8').replace('from left_chord_motion import *','from left_continuous_motion import *')
text=text.replace("for n in tl['notes']:\n    k=c.KEYS[n['key_index']]", "for midi in sorted(set(n['midi_note'] for n in tl['notes'])):\n    n=next(n for n in tl['notes'] if n['midi_note']==midi)\n    k=c.KEYS[n['key_index']]")
text=text.replace("read(P/'STATIC_FEASIBILITY.json')['static_tests']","read(P/'CONTINUOUS_PREFLIGHT.json')['tests']")
text=text.replace("for n in tl['notes']:\n        j=n['finger']-1;sp=V[c.MARKERS['L'][j]['mesh_vertex']]", "for task in co.task_components(row['time']):\n        i,lift,factor=max(task['components'],key=lambda x:x[2]);n=tl['notes'][i]\n        j=n['finger']-1;sp=V[c.MARKERS['L'][j]['mesh_vertex']]")
text=text.replace("dict(note=n['note_name'],finger=n['finger'],bone_pad=", "dict(note=n['note_name'],finger=n['finger'],phase=task['phase'],bone_pad=")
text=text.replace("if row['test']=='all_three_fully_down':", "if row['test'] in ['chord_to_single_boundary','index_single_down']:")
text=text.replace("f'preflight_static_down_{view.lower()}.png'", "f'preflight_{row[\"test\"]}_{view.lower()}.png'")
(P/'02_static_readback.py').write_text(text,encoding='utf8')
dump('CONTINUOUS_CODE_REUSE_BIND.json',dict(B1_generator_sha256=sha(B1/'03_generate.py'),B1_scene_sha256=sha(B1/'04_scene.py'),
    generator_sha256=sha(P/'03_generate.py'),source_baselines_unmodified=True,
    changes=['affine released/preparing target components','continuous time-local idle policy','complete input stream in one solve'],
    no_separate_note_animations=True,no_fixed_root_curve=True,no_pitch_special_pose=True))
print('CONTINUOUS_ADAPTERS_READY')
