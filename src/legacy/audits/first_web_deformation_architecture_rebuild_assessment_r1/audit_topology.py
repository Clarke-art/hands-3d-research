import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
request=Path('<USER_HOME>/.codex/attachments/a7bcef96-4373-42ff-8d2f-05f722487f5b/已粘贴的文本.txt')
dump('PRIOR_HUMAN_DECISION_BIND_R1.json',{'phase':'RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1','Q1':'NO','Q2':'NO','Q3':'YES','Q4':'NO','DQS_ROUTE':'REJECTED','authority':'Direct user request attachment','request_path':str(request),'request_sha256':sha(request),'failed_patch_candidate_not_input':True})
ob,rig=fresh();V0=coords(ob);W=weights(ob);faces=[list(p.vertices) for p in ob.data.polygons];edges=[list(e.vertices) for e in ob.data.edges];ids=set(PATCH_IDS)
adj={i:[] for i in range(len(V0))}
for a,b in edges:adj[a].append(b);adj[b].append(a)
selected=[(i,f) for i,f in enumerate(faces) if all(v in ids for v in f)]
motion(rig,130);V=coords(ob)
# A plain wire overlay is for identifying visible fold lines; no strain score or hidden crossing analysis.
row={'source_baseline_sha256':sha(BASE),'vertex_count':len(V0),'bone_count':len(rig.data.bones),'patch_ids':PATCH_IDS,'patch_vertex_count':len(ids),'patch_face_count':len(selected),'patch_polygon_sides':{str(n):sum(len(f)==n for _,f in selected) for n in set(len(f) for _,f in selected)},'whole_mesh_polygon_sides':{str(n):sum(len(f)==n for f in faces) for n in set(map(len,faces))},'local_valence':{str(i):len(adj[i]) for i in PATCH_IDS},'local_edges':[{'vertices':[a,b],'zero_vector':(V0[b]-V0[a]).tolist(),'F130_vector':(V[b]-V[a]).tolist()} for a,b in edges if a in ids and b in ids],'local_faces':[{'face_id':i,'vertices':f} for i,f in selected],'ZERO_world':V0.tolist(),'F130_world':V.tolist(),'weights':W.tolist(),'group_names':[g.name for g in ob.vertex_groups],'shape':core.shape_payload(ob),'native':m.product_payload(ob,rig),'scope':'Read-only selected first-web connectivity and ordinary visible fold lines. No whole-hand retopo or complex strain/crossing census.'}
dump('TOPOLOGY_INPUT_R1.json',row)
print('LOCAL_TOPOLOGY',row['patch_face_count'],row['patch_polygon_sides'],'VALENCES',sorted(set(row['local_valence'].values())),flush=True)
rr=m.Renderer(cameras()['130'],'baseline_selected');rr.sc.display.shading.shadow_intensity=0;vv,ff=m.evaluate(ob,ob.matrix_world);rr.draw('BASELINE','F130',vv,ff,list(cameras()['130']));rr.dispose()
