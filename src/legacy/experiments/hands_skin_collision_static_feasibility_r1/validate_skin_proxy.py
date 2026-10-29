from skin_proxy import *
A=np.load(O/'ACTUAL_SOURCE_SNAPSHOTS.npz');rows=json.loads((O/'SOURCE_POSES.json').read_text());errors=[]
for row in rows:
 S.base=Rotation.from_quat(np.array(row['pose_quats'])[:,[1,2,3,0]]).as_matrix()[None];S.world=np.array(row['rig_world'])[None];pred=S(original=True)[0];error=np.linalg.norm(pred-A[row['label']],axis=1)*1000;errors.append(dict(label=row['label'],maximum_vertex_error_mm=float(error.max()),rms_vertex_error_mm=float(np.sqrt(np.mean(error**2)))))
 print('SKIN_MODEL_PARITY',row['label'],round(error.max(),6),flush=True)
S.base=np.tile(np.eye(3),(1,len(REST),1,1));S.world=RAW['base_rig_world'][None]
(O/'SKIN_PROXY_PARITY.json').write_text(json.dumps(dict(parity_tests=errors,pass_=max(x['maximum_vertex_error_mm'] for x in errors)<.05,scope='Original frozen Skin implementation, same actual weights, native meshes, corrective driver; final acceptance always Blender evaluation'),indent=2)+'\n',encoding='utf8');assert max(x['maximum_vertex_error_mm'] for x in errors)<.05
