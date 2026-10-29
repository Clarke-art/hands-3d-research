import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import numpy as np,shutil
G=read(OUT/'STATIC_BIND_AND_REBASE_R1.json')
assert sha(CANDIDATE)==G['candidate']['sha256']
backup=OUT/'RIGHT_HAND_OFFICIAL_L1_INITIAL_TRANSFER_R1.blend';assert not backup.exists()
shutil.copy2(CANDIDATE,backup)
for f in ['REPRESENTATIVE_MOTION_EVIDENCE_R1.json','MOTION_RENDER_MANIFEST_R1.json','POSED_DISPLAY_COORDINATES_R1.json']:
    shutil.copy2(OUT/f,OUT/('INITIAL_TRANSFER_'+f))
ob,rig=open_candidate();before=product_payload(ob,rig)
groups=[g.name for g in ob.vertex_groups];active=[groups.index(n) for n in ['WRIST_R','THUMB_CMC_R','THUMB_MCP_R','THUMB_IP_R']]
weights=np.zeros((len(ob.data.vertices),len(groups)))
for v in ob.data.vertices:
    for g in v.groups:weights[v.index,g.group]=g.weight
original=weights.copy()
adj=[set() for _ in ob.data.vertices]
for e in ob.data.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
raw=read(LINEAGE/'RAW_SOURCE_GEOMETRY.json')['stages']
ancestor=read(LINEAGE/'HISTORICAL_OPERATION_RAM_REPLAY.json')['final_ancestry']
lookup={tuple(v):i for i,v in enumerate(raw['STAGE4A_R2_BASE']['local_m'])}
known={i:lookup[tuple(v)] for i,v in enumerate(raw['STAGE4A_R2']['local_m']) if tuple(v) in lookup}
regions=read(ROOT/'production_spec/stage5_production_rig/stage5b_r1b/_tmp/R1B_REGIONS.json')['regions']
seeds=set()
for i in regions['FIRST_WEB']+regions['THUMB_BASE_FOLD']:
    if i in known:seeds|={int(k) for k,w in ancestor[known[i]].items() if w>.015}
distance={i:0 for i in seeds};front=set(seeds)
for step in [1,2]:
    front={j for i in front for j in adj[i] if j not in distance}
    distance.update({j:step for j in front})
region=sorted(distance)
assert len(region)<=260
V=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices])
total=original[:,active].sum(1)
field=original[:,active].copy()
for sweep in range(5):
    temp=field.copy()
    for i in region:
        if total[i]<1e-7:continue
        neighbors=np.array(sorted(adj[i]));d=np.linalg.norm(V[neighbors]-V[i],axis=1)
        spatial=np.exp(-d*d/(2*.008*.008))
        average=spatial@field[neighbors]/spatial.sum()
        if average.sum()>1e-10:average*=total[i]/average.sum()
        temp[i]=field[i]*.4+average*.6
    field=temp
for i in region:
    strength={0:.95,1:.7,2:.3}[distance[i]]
    weights[i,active]=original[i,active]*(1-strength)+field[i]*strength
changed=[]
for i in region:
    if np.max(np.abs(weights[i]-original[i]))<1e-7:continue
    for j in active:
        if weights[i,j]>0:ob.vertex_groups[j].add([i],float(weights[i,j]),'REPLACE')
        else:ob.vertex_groups[j].remove([i])
    changed.append(i)
after=product_payload(ob,rig)
for k in before:
    if k!='weights':assert before[k]==after[k],k
assert state_zero(rig)
assert all(before['weights'][i]==after['weights'][i] for i in set(range(len(weights)))-set(changed))
for i in changed:
    def other(row):return {j:w for j,w in row if j not in active}
    assert other(before['weights'][i])==other(after['weights'][i])
bpy.context.scene['LOCAL_WEIGHT_TUNING_REGION']='FIRST_WEB_AND_THUMB_BASE_TRANSITION_ONLY'
bpy.context.scene['LOCAL_WEIGHT_TUNING_VERTEX_COUNT']=len(changed)
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE),copy=True,compress=False)
ob,rig=open_candidate();assert product_payload(ob,rig)==after
dump('LOCAL_VISIBLE_WEIGHT_TUNING_R1.json',{'status':'SAVED_ONCE_REOPEN_PASS','initial_candidate':ref(backup),
 'candidate':ref(CANDIDATE),'actual_changed_vertex_ids':changed,'local_weight_tuning_vertex_count':len(changed),
 'active_group_names':[groups[j] for j in active],'other_influence_columns_unchanged':True,
 'native_source_positions_topology_UV_materials_rig_unchanged':True,'method':'One bounded first-web/thumb-base local five-sweep neighbor smoothing with compact 0/1/2-ring brush; preserve original four-group total',
 'rig_fit_changes_during_tuning':0,'source_geometry_writes':0,'shape_keys_correctives_added':0,'tuning_attempt_count':1})
G['initial_candidate']=ref(backup);G['candidate']=ref(CANDIDATE);G['candidate_save_calls']=2
G['local_weight_tuning_vertex_count']=len(changed);G['final_candidate_native_payload_hash']=digest(after)
dump('STATIC_BIND_AND_REBASE_R1.json',G)
# Final static images share no cast shadows with final motion comparison.
VZ,F=evaluate(ob,ob.matrix_world);renderer=Renderer(G['cameras'],'final_renders');renderer.sc.display.shading.shadow_intensity=0.
views=['PALMAR_FULL','DORSAL_FULL','RADIAL_SIDE','ULNAR_SIDE','THUMB_WEB_OBLIQUE','THENAR_CLOSE']
renderer.draw('OFFICIAL_L1','REST',[Vector(v) for v in G['source_world_m']],[tuple(f) for f in G['faces']],views)
renderer.draw('REBASED','ZERO',VZ,F,views);renderer.dispose()
dump('FINAL_STATIC_MATCHED_RENDER_MANIFEST_R1.json',{'renders':renderer.records,'cameras':G['cameras'],'source_geometry_unchanged':True,'cast_shadow_intensity':0.,'same_source_candidate_display':True})
print('LOCAL_WEIGHT_TUNING_COMPLETE',len(changed),sha(CANDIDATE),flush=True)
