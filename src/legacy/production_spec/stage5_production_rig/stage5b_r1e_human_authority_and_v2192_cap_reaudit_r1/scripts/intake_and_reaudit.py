import sys
sys.dont_write_bytecode = True
import json, hashlib, datetime, shutil, heapq
from pathlib import Path
import numpy as np

out = Path(__file__).resolve().parents[1]
root = out.parents[2]
s5 = out.parent
source = Path('<USER_HOME>/Downloads/HUMAN_MANUAL_REGISTRATION_RESPONSES_R1.json')
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    return json.loads(p.read_text(encoding='utf-8'))
def inventory():
    return {str(p.relative_to(root)).replace('\\','/'):sha(p)
            for name in ['production_spec','docs'] for p in (root/name).rglob('*')
            if p.is_file() and out not in p.parents}
def dump(name, data):
    (out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

before = inventory()
human = load(source)
assert human['questions'] == {'Q1':'YES','Q2':'UNRESOLVED','Q3':'UNDECIDED','Q4':'NO','Q5':'LIMITED'}
assert 'v2192 的 distal-cap membership 需单独重新审计' in human['notes']
shutil.copyfile(source, out/source.name)
assert sha(source) == sha(out/source.name)
intake = {
    'record_type':'HUMAN_AUTHORITY_INPUT_ACCEPTED_VERBATIM',
    'accepted_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'source_path':str(source), 'source_sha256':sha(source),
    'authorization':'Current user explicitly instructed Q1-Q5 and notes to be Human authority input',
    'questions':human['questions'], 'notes':human['notes'], 'clusters':human['clusters'],
    'original_response':human,
    'human_review_completed':True,
    'AI_reinterpreted_or_overrode_response':False,
    'prior_review_snapshot_modified':False,
    'export_field_authority_automatically_applied':human['authority_automatically_applied'],
    'export_field_explanation':'Original page export flag is preserved; current explicit user instruction accepts this as Human input. No production authority is automatically edited.',
    'required_separate_audit':'V2192_DISTAL_CAP_MEMBERSHIP_REAUDIT_R1',
    'constraints':['Q4 remains NO','Q5 remains LIMITED','Q2 remains UNRESOLVED','Q3 and all cluster decisions remain UNDECIDED','Do not treat mesh path continuity as anatomical cap-to-index proof','Do not use R3 THUMB membership as anatomical proof','Do not derive weights or change production membership']
}
dump('HUMAN_AUTHORITY_INPUT_R1.json',intake)

cap_path=s5/'stage5a_r2a/THUMB_DISTAL_CAP_AUDIT.json'
errata=s5/'stage5a_r2b/STAGE5A_R2A_DISTAL_CAP_METHOD_ERRATA.md'
r3_script=root/'production_spec/stage6_deformation/stage6b_r3_thumb_tip_ownership_boundary/scripts/r3_ownership.py'
cap=load(cap_path)
prior_dir=s5/'stage5b_r1e_manual_anatomical_reference_review_r1'
prior=load(prior_dir/'CAP_TO_COLLAR_3_EDGE_ANATOMICAL_SANITY_AUDIT.json')
raw_path=s5/'stage5b_r1e_endpoint_authority_review/_tmp/review_raw.json'
static_path=s5/'stage5b_r1e_narrow_anatomical_review/_tmp/anatomy_static_extract.json'
raw=load(raw_path); static=load(static_path)
current=np.array(raw['R1B']['v']); native=np.array(static['historical']['STAGE4A_R2_PRE_RSSF']['vertices_world_m'])
faces=raw['R1B']['faces']; edges=raw['R1B']['edges']
cap_ids=cap['thumb_cap_vertex_ids']; cap_faces=cap['thumb_cap_face_ids']
assert set(cap_ids)==set(raw['R3']['CAP'])
assert set(cap_ids)=={v for f in cap_faces for v in faces[f]}
assert sha(s5/'stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend')==static['historical']['STAGE5B_R1B']['sha256']
adj=[[] for _ in current]
for a,b in edges:
    adj[a].append(b); adj[b].append(a)
def distance_path(start,targets,vertices):
    dist={start:0.}; parent={}; queue=[(0.,start)]
    while queue:
        cost,a=heapq.heappop(queue)
        if cost!=dist[a]:continue
        if a in targets:
            path=[a]
            while path[-1] in parent:path.append(parent[path[-1]])
            return {'path':path[::-1],'distance_mm':cost}
        for b in sorted(adj[a]):
            nc=cost+float(np.linalg.norm(vertices[a]-vertices[b])*1000)
            if nc<dist.get(b,float('inf')):
                dist[b]=nc;parent[b]=a;heapq.heappush(queue,(nc,b))
body=set(load(prior_dir/'BODY_SIDE_16_MANUAL_REGISTRATION_CANDIDATES.json')['body_ids'])
audit={
    'audit_id':'V2192_DISTAL_CAP_MEMBERSHIP_REAUDIT_R1',
    'scope':'Separate read-only membership provenance and static mesh audit requested by Human notes; not a new Human registration',
    'human_authority_source_sha256':sha(source),
    'human_questions_verbatim':human['questions'],'human_notes_verbatim':human['notes'],
    'vertex_id':2192,
    'historical_list_membership':{'R2A_approved_cap_list_contains_v2192':2192 in cap_ids,'approved_cap_vertex_ids':cap_ids,'approved_cap_face_ids':cap_faces,'cap_faces_incident_to_v2192':[f for f in cap_faces if 2192 in faces[f]],'R3_cap_set_identical_to_R2A':True},
    'provenance_chain':[
        {'source':str(cap_path.relative_to(root)),'finding':'R2A records v2192 among the 9 cap vertices'},
        {'source':str(errata.relative_to(root)),'finding':'Canonical method is geodesic connected cap from a distal-most surface seed selected within digit-owned faces; older slab-method prose is superseded'},
        {'source':'production_spec/stage5_production_rig/stage5a_r2a/scripts/s5a_r2a_audit.py','finding':'digit_cap selects seed from DIG_VERTS[D] using approved distal joint and tip direction, then restricts patch faces to OWN_FACES[D]. Correct input digit identity is a prerequisite.'},
        {'source':str(r3_script.relative_to(root)),'finding':'CAP imports R2A cap IDs, and THUMB_STRONG explicitly unions CAP. R3 label inheritance is not independent validation of anatomical cap identity.'}
    ],
    'static_mesh_evidence':{
        'v2192_current_world_mm':(current[2192]*1000).tolist(),
        'v2192_native_pre_RSSF_world_mm':(native[2192]*1000).tolist(),
        'incident_faces':[i for i,f in enumerate(faces) if 2192 in f],
        'one_ring':sorted(adj[2192]),
        'nearest_Human_Q1_body16_along_edges_current':distance_path(2192,body,current),
        'nearest_Human_Q1_body16_along_edges_native':distance_path(2192,body,native),
        'three_edge_path':[2192,703,2169,704],
        'current_three_edge_length_mm':sum(float(np.linalg.norm(current[a]-current[b])*1000) for a,b in zip([2192,703,2169],[703,2169,704])),
        'path_first_web_intersection':prior['first_web_intersection'],
        'topological_continuity':'Existing continuous mesh path; Human Q5 remains LIMITED for anatomical interpretation',
        'existing_visual_evidence':'../stage5b_r1e_manual_anatomical_reference_review_r1/renders/CAP_TO_COLLAR_3_EDGE_ANATOMICAL_SANITY_CHECK.png',
        'previous_static_visual_observation':prior['visual_observation'],
        'visual_observation_role':'Supporting model evidence only; does not override Human review or assign new anatomical membership'
    },
    'result':{
        'historical_administrative_membership':'CONFIRMED_IN_FROZEN_APPROVED_LIST',
        'anatomical_thumb_distal_cap_membership':'NOT_ESTABLISHED_BY_INDEPENDENT_CORRESPONDENCE',
        'issue':'Frozen cap identity needs independent resolution; geodesic continuity and inherited THUMB labels do not resolve the region conflict.',
        'membership_removed':False,'replacement_cap_proposed':False,
        'required_resolution':'Independent native thumb terminal-region identification and original digit-owned seed/face provenance validation, before any proposed production membership revision',
        'Human_Q4':'NO','Human_Q5':'LIMITED'
    },
    'source_hashes':{str(p.relative_to(root)):sha(p) for p in [cap_path,errata,r3_script,raw_path,static_path]},
    'production_membership_or_authority_changed':False,
    'BLEND_FILES_WRITTEN':0,'R1F_CREATED':False,'deformation_runs':0
}
dump('V2192_DISTAL_CAP_MEMBERSHIP_REAUDIT_R1.json',audit)
status={'HumanReview':'COMPLETED_INPUT_ACCEPTED','questions':human['questions'],'notes':human['notes'],
        'v2192_separate_reaudit':'READ_ONLY_PROVENANCE_AND_MESH_AUDIT_COMPLETED; ANATOMICAL_MEMBERSHIP_UNRESOLVED',
        'prior_Human_review_reopened':False,'production_authorities_changed':False,
        'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,
        'BLEND_FILES_WRITTEN':0,'R1F_CREATED':False,'STOP':'NO_AUTOMATIC_MEMBERSHIP_OR_WEIGHT_CHANGE'}
dump('HUMAN_AUTHORITY_AND_CAP_REAUDIT_STATUS.json',status)
report=f'''# Human authority input 与 v2192 独立审计

已读取 `{source}`，原文件逐字节保存，SHA-256：`{sha(source)}`。

本轮 Human authority：Q1=YES；Q2=UNRESOLVED；Q3=UNDECIDED；Q4=NO；Q5=LIMITED。四簇候选均保持 UNDECIDED。不以 AI 观察替换这些答复，也不把上一轮 Human Review 重新标为待完成。

Human notes 原文：

> {human['notes']}

## v2192 的单独 membership 审计

v2192 确实列在冻结 R2A distal-cap 的九个顶点中，并作为 cap face 356 的顶点进入清单。R3 直接继承该 cap 清单，又将其并入 THUMB_STRONG。因此继承后的 R3 THUMB 标签不能作为独立解剖验证。

canonical geodesic cap 方法先依赖 digit-owned 顶点/面片识别远端 seed，再沿表面生成 cap。测地法的连通性不能独立验证输入 digit identity。历史 JSON 的 slab-method 文本已由 R2B errata 声明废止，本轮没有据该旧叙述重算 cap。

本轮独立重算 v2192 至 body16 的最近 edge path，并记录原生及当前静态坐标、one-ring、incident faces；详见单独 JSON。此前原生模型的区域冲突图保留作证据。Human 对 Q5 的 LIMITED 和 notes 对路径解释的限制原样有效，不升级为已批准的真实 thumb-cap→index-collar 解剖路径。Q4 保持 NO。

结论：**历史清单 membership 存在；真实 thumb distal-cap 对应未得到独立确认。** 两者分别记录。没有删除 v2192、重建 cap 或改变已冻结 authority。后续针对原生拇指末端区域及原始 seed/owned-face 的验证属于独立 cap 议题，不重开已完成的 Q1–Q5 Human 判断。

全部生产文件与上一轮审阅包保持原样；DELTA=0，BLEND writes=0，R1F=false。STOP，未推导权重。
'''
(out/'HUMAN_AUTHORITY_AND_V2192_CAP_REAUDIT_REPORT.md').write_text(report,encoding='utf-8')
after=inventory();assert before==after
dump('FROZEN_HASH_VERIFICATION.json',{'before':before,'after':after,'protected_file_count':len(before),'all_before_equals_after':True,'changed_files':[],'original_Human_response_sha256':sha(source),'original_Human_response_copy_exact':True})
print('Human input accepted verbatim:',human['questions'])
print('Read-only v2192 provenance/static mesh audit saved; frozen files unchanged:',len(before))
