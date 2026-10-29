from pathlib import Path
P=Path(__file__).resolve().parent;OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1'
code=(OLD/'04_scene.py').read_text()
code=code.replace('MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1','MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1').replace('MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_CANDIDATE_R1.blend','HAND_POSTURE_CONTACT_REFINED_DESIGN_ONLY_R1.blend')
old="root=bpy.data.objects.new('PROCEDURAL_PALM_ROOT_'+s,None);sc.collection.objects.link(root);C=Matrix(c['native_to_canonical']);R=Matrix(rz(float(A[s+'_yaw']))).to_4x4();T=Matrix.Translation(Vector(A[s+'_root']));root.matrix_world=T@R@C;rig.parent=root;rig.matrix_parent_inverse=Matrix.Identity(4)"
new="root=bpy.data.objects.new('COORDINATED_PALM_ROOT_'+s,None);sc.collection.objects.link(root);C=Matrix(c['native_to_canonical']);root.rotation_mode='QUATERNION';rig.parent=root;rig.matrix_parent_inverse=Matrix.Identity(4)"
assert old in code;code=code.replace(old,new)
code=code.replace('  frame=1+t*FPS\n','  frame=1+t*FPS\n  last=root.rotation_quaternion.copy();root.matrix_world=Matrix.Translation(Vector(A[s+\'_root\'][i]))@Matrix(A[s+\'_rotation\'][i]).to_4x4()@C\n  if i and root.rotation_quaternion.dot(last)<0:root.rotation_quaternion.negate()\n  root.keyframe_insert(data_path=\'location\',frame=frame);root.keyframe_insert(data_path=\'rotation_quaternion\',frame=frame)\n')
code=code.replace(" rig.animation_data.action.name='NEW_MIDI_PROCEDURAL_'+s+'_R1';linear(rig)"," rig.animation_data.action.name='NEW_MIDI_PROCEDURAL_REFINED_'+s+'_R1';linear(rig)\n root.animation_data.action.name='NEW_MIDI_PROCEDURAL_PALM_'+s+'_R1';linear(root)")
(P/'03_scene.py').write_text(code,encoding='utf-8')
render=(OLD/'06_render.py').read_text().replace('MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_CANDIDATE_R1.blend','HAND_POSTURE_CONTACT_REFINED_DESIGN_ONLY_R1.blend')
render=render.replace("prefs.compute_device_type='CUDA'","prefs.compute_device_type='OPTIX'")
start=render.index("if '--preview' in sys.argv:");end=render.index('\nelse:',start)
render=render[:start]+'''if '--preview' in sys.argv:
 sc.camera=bpy.data.objects['SKIN_REVIEW'];sc.frame_set(52);sc.render.filepath=str(P/'_preview_pose.png');bpy.ops.render.render(write_still=True)
 sc.camera=bpy.data.objects['CONTACT_SIDE'];sc.frame_set(70);sc.render.filepath=str(P/'_preview_side.png');bpy.ops.render.render(write_still=True)
'''.rstrip()+render[end:]
render=render.replace(' for j in range(sc.frame_end):'," start=int(sys.argv[sys.argv.index('--start')+1]) if '--start' in sys.argv else 0\n end=int(sys.argv[sys.argv.index('--end')+1]) if '--end' in sys.argv else sc.frame_end\n priority=[j for j in [51,69,111,150] if start<=j<end]\n for j in priority+[j for j in range(start,end) if j not in priority]:")
(P/'05_render.py').write_text(render,encoding='utf-8')
print('Scene and render scripts: inherited assets, materials, lights, camera; new root and joint animation only')
