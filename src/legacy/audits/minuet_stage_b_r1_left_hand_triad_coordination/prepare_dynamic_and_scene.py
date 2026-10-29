from stage_common import *
assert not (P/'CANDIDATE_ATTEMPT.json').exists()
text=(A2/'02_generate.py').read_text(encoding='utf8').replace('from coordinated_motion import *','from left_chord_motion import *')
start=text.index('# Event-level adjacent-pair initial poses')
stop=text.index('lower=np.r_[',start)
replacement="""# Generic phase-level initialization: every active/prepare/release finger at
# a support time enters ONE shared-root pose problem, never per-finger animation.
seedtimes=sorted(set([0.,float(end)]+[n['note_on']+d for n in events for d in [-.075,0,.035]]+[n['note_off']+d for n in events for d in [0,.07,.32]]))
seedtimes=[t for t in seedtimes if 0<=t<=end];seedstates=[];seedxy=[]
for t in seedtimes:
    fit=co.static_solve(t)
    seedstates.append(fit.x[:26]);seedxy.append(fit.x[26:].reshape(N,2))
seedstates=np.array(seedstates);seed=np.column_stack([np.interp(knots,seedtimes,seedstates[:,d]) for d in range(26)])
initialxy=np.mean(seedxy,axis=0)
X0=np.r_[seed.ravel(),initialxy.ravel()]
"""
text=text[:start]+replacement+text[stop:]
text=text.replace("['right-hand']","['left-hand']")
needle="for i,n in enumerate(events[:-1]):\n        if n['note_id'] in co.repeats:out.append((xy[i+1]-xy[i])*3)"
assert needle in text
text=text.replace(needle,needle+"\n    out.append((states[-1]-states[0])*pol['endpoint_prepared_return_weight'])")
needle="assert row==len(sample)"
text=text.replace(needle,"J[row:row+26,:26]=1;J[row:row+26,(K-1)*26:K*26]=1;row+=26\n"+needle)
text=text.replace('R_q=Q,R_delta=traj[:,:3]/1000,R_extra_rot_deg=traj[:,3:6],R_extra_rotation=RR','L_q=Q,L_delta=traj[:,:3]/1000,L_extra_rot_deg=traj[:,3:6],L_extra_rotation=RR')
text=text.replace("sha(P/'coordinated_motion.py')","sha(P/'left_chord_motion.py')")
text=text.replace('source_event_count=16','source_event_count=len(events),concurrent_peak_fingers=max(len(co.tasks(t)) for t in knots),phase_initialization_solves=len(seedtimes)')
text=text.replace('source_notes=16','source_notes=len(events)')
text=text.replace('left_generated=False','left_generated=True,right_generated=False')
(P/'03_generate.py').write_text(text,encoding='utf8')
# Reuse approved Action bake/save-reopen/identity and actual key readback.
text=(A2/'03_scene.py').read_text(encoding='utf8')
text=text.replace('STAGE_A_R2_COORDINATED_RIGHT_DESIGN_ONLY.blend','STAGE_B_LEFT_TRIAD_DESIGN_ONLY_R1.blend')
text=text.replace('STAGE_A_R2_COORDINATED_RIGHT_ONLY','STAGE_B_LEFT_TRIAD_ONLY_R1')
text=text.replace("info=sm['mapping']['R1']","info=sm['mapping']['L1']")
text=text.replace("o.ANCHORS['R1']['root_xyz_m']","o.ANCHORS['L1']['root_xyz_m']")
text=text.replace("c.SETUPS['R',d]","c.SETUPS['L',d]").replace("c.joint_mats('R',d,","c.joint_mats('L',d,")
text=text.replace("c.MARKERS['R']","c.MARKERS['L']").replace("o.worldpads('R',","o.worldpads('L',")
for a,b in [('R_q','L_q'),('R_delta','L_delta'),('R_extra_rotation','L_extra_rotation'),('R_extra_rot_deg','L_extra_rot_deg'),('R_verts','L_verts'),('R_pads','L_pads'),('R_skin_pads','L_skin_pads')]:text=text.replace(a,b)
text=text.replace('DESIGN_ONLY_STAGE_A_R2_COORDINATED_JOINTS','DESIGN_ONLY_STAGE_B_LEFT_TRIAD_JOINTS').replace('DESIGN_ONLY_STAGE_A_R2_COORDINATED_ROOT','DESIGN_ONLY_STAGE_B_LEFT_TRIAD_ROOT')
text=text.replace("(x,-.53,.58),(x,.014,.014),.47","(x,-.60,.62),(x,-.04,.015),.56")
text=text.replace("(x+.07,-.53,.24),(x,.025,.004),.47","(x+.07,-.60,.27),(x,-.025,.004),.56")
text=text.replace("(x,.008,.82),(x,.008,0),.47","(x,-.06,.82),(x,-.06,0),.56")
start=text.index("camera_bind=read(P/'R1_REVIEW_CAMERA_BIND.json')")
stop=text.index("sc['DESIGN_ONLY']=True;",start)
text=text[:start]+text[stop:]
text=text.replace("sc['RIGHT_ONLY_TECHNICAL_VALIDATION']=True","sc['LEFT_ONLY_TECHNICAL_VALIDATION']=True")
text=text.replace("left_in_performance_scene=False","right_in_performance_scene=False,left_only=True")
text=text.replace("all_R1_review_cameras_exact_matched=True,R1_camera_bind_sha256=sha(P/'R1_REVIEW_CAMERA_BIND.json'),",'')
# Audit display labels are separate FONT objects; copied frozen keys unchanged.
needle="x=float(np.mean([c.KEYS[n['key_index']]['key_center'][0] for n in tl['notes']]))"
labels="""for oldlabel in [v for v in sc.objects if v.type=='FONT']:oldlabel.hide_render=True
for n in tl['notes']:
    data=bpy.data.curves.new('LEFT_TRIAD_NOTE_'+n['note_name'],type='FONT');data.body=n['note_name'];data.align_x='CENTER';data.size=.009
    label=bpy.data.objects.new(data.name,data);sc.collection.objects.link(label);label.location=(c.KEYS[n['key_index']]['key_center'][0],-.018,.0005);label.color=(.12,.24,.18,1)
"""
assert needle in text;text=text.replace(needle,labels+needle)
text=text.replace("print('ONE_RIGHT_ONLY_SCENE_READBACK'","print('ONE_LEFT_TRIAD_SCENE_READBACK'")
(P/'04_scene.py').write_text(text,encoding='utf8')
(P/'06_render.py').write_text((A2/'05_render.py').read_text(encoding='utf8').replace('right_only=True','left_triad_only=True'),encoding='utf8')
dump('STAGE_A_DYNAMIC_REUSE_BIND.json',dict(source_generator_sha256=sha(A2/'02_generate.py'),source_scene_sha256=sha(A2/'03_scene.py'),
    generator_sha256=sha(P/'03_generate.py'),scene_adapter_sha256=sha(P/'04_scene.py'),
    unchanged_source=True,all_chord_fingers_share_one_trajectory_solve=True,
    changes=['multi-finger phase-level joint initialization','actual L FK/root/joints','full-release recovery','paired relaxed endpoints','left-only scene/cameras/labels'],
    no_right_motion_mirrored=True))
print('LEFT_JOINT_DYNAMIC_AND_BAKE_ADAPTERS_READY')
