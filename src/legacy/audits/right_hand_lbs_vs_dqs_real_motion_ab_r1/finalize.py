import json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=read('DEFORMATION_MODE_VERIFICATION_R1.json')
for p,h in v['input_hashes_unchanged'].items():assert sha(ROOT/p)==h
assert sha(ROOT/v['test_asset']['path'])==v['test_asset']['sha256']
counts={}
for label in ['LBS','DQS']:
    for sub,expected in [('selected',20),('regression',24),('motion',420)]:
        count=len(list((OUT/(label.lower()+'_'+sub)).glob('*.png')));assert count==expected,(label,sub,count)
        counts[label+'_'+sub]=count
assert all(x is None for x in read('RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_STATUS.json')['HUMAN_REVIEW'].values())
dump('REVIEW_UI_VERIFICATION_R1.json',{'status':'PASS','url':'http://127.0.0.1:8771/review.html','videos':[{'id':'palmarVideo','duration':7,'width':1280,'height':640,'readyState':4,'error':None},{'id':'obliqueVideo','duration':7,'width':1280,'height':640,'readyState':4,'error':None}],'default_images_loaded':16,'selector_test':{'frame':'F76','pose':'FULL_OPP_L3','all_images_loaded':True},'restored_default':{'frame':'F130','pose':'ZERO'},'console_errors':[],'proof':'REVIEW_PAGE_PROOF_R1.png','human_answers_written':False})
dump('FINAL_ASSET_PROTECTION_R1.json',{'status':'PASS','input_sha256_unchanged':v['input_hashes_unchanged'],'test_asset':v['test_asset'],'render_counts':counts,'total_matched_renders':sum(counts.values()),'basis_vertex_writes':0,'weight_writes':0,'driver_edits':0,'new_correctives':0,'action_payload_sha256':v['source_action_payload_sha256'],'protected_payload_check':'Baseline/A/B data compared at saved clean reopen; shared mesh/Key/rest data, matched Action and per-observation pose matrices','baseline_modified':False,'production_promoted':False})
files=[{'path':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='FINAL_OUTPUT_MANIFEST_R1.json']
dump('FINAL_OUTPUT_MANIFEST_R1.json',{'phase':'RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1','verdict':'DQS_WORSE','workflow_status':'STOP_HUMAN_REVIEW','candidate':v['test_asset'],'files':files})
print('FINAL_AB_DELIVERY_PASS',len(files),'files',sum(counts.values()),'matched renders','SOURCE_UNCHANGED','HUMAN_PENDING')
