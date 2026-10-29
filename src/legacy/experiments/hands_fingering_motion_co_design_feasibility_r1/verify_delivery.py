"""Final local delivery checks. Never follow historical manifest paths."""
import sys,json,hashlib,re
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;ROOT=O.parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
p=read(O/'SOURCE_SHA_CHECK.json')
after={}
for name in p['before']:
 path=Path(name).resolve();assert path.is_relative_to(ROOT)
 after[name]=sha(path)
assert p['before']==after
p['after']=after;p['final_delivery_checked']=True;dump('SOURCE_SHA_CHECK.json',p)
policy=sha(O/'EVALUATION_POLICY.json')
assert policy==read(O/'POLICY_LOCK_RECEIPT.json')['policy_sha256']
assert policy==read(O/'CANDIDATE_COMPARISON.json')['ranking_policy_sha256']
c=read(O/'CANDIDATES.json');r=read(O/'PIANOPLAYER_RUNS.json');g=read(O/'STATIC_RIG_PROBES.json')
assert len(c['candidates'])==4 and len(r['runs'])==3 and len(g['rows'])==240
assert len({tuple(x['fingers']) for x in c['candidates']})==4
s=read(O/'CANDIDATE_COMPARISON.json')['summaries']
assert all(not x['occupancy_conflicts'] for x in s)
assert s[-1]['fingers'][:9]==s[0]['fingers'][:9]
assert len(c['left_notes'])==7 and all(x['left_unchanged'] for x in s)
links=[]
for name in ['FINGERING_CANDIDATES.md','HAND_MOTION_FEASIBILITY.md','FINAL_RECOMMENDATION.md']:
 for target in re.findall(r'\]\(<([^>]+)>\)',(O/name).read_text(encoding='utf8')):
  path=Path(target).resolve();assert path.is_relative_to(ROOT) and path.is_file(),target
  links.append(target)
for path in O.iterdir():assert path.suffix.lower() not in ['.blend','.mp4','.mov','.avi','.npz','.mid','.wav']
cost=read(O/'COMPUTE_LOG.json');details=read(O/'CORRECTION_LOG.json')
cost['details_cumulative_seconds']=details['cumulative_details_seconds']
cost['main_plus_details_recorded_seconds']=cost['total_seconds']+details['cumulative_details_seconds']
cost['source_sha_files']=len(after);dump('COMPUTE_LOG.json',cost)
dump('FINAL_STATUS.json',dict(task='HANDS_FINGERING_MOTION_CO_DESIGN_FEASIBILITY_R1',status='INCONCLUSIVE',
 stop='STOP — HUMAN REVIEW',distinct_alternatives=3,original_official_fingering_unchanged=True,
 left_unchanged=True,new_trajectories=0,new_actions=0,new_blends=0,new_videos=0,blender_calls=0,
 immediate_motion_generation_recommended=False,provisional_smaller_change_option='P3, pending additional joint-layout evidence',
 historical_protection_FAIL_preserved=True,source_sha_files=len(after),source_sha_unchanged=True,
 independent_piano_accessed=False,next_experiment_started=False))
dump('DELIVERY_CHECK.json',dict(pass_=True,report_count=3,report_local_links=len(links),source_sha_unchanged=True,
 locked_policy_unchanged=True,candidate_limit_pass=True,exact_event_validation_pass=True,
 no_forbidden_media_or_trajectory_files=True,scope='Current experiment delivery and referenced source files only; not historical global protection certification'))
manifest={path.name:sha(path) for path in O.iterdir() if path.is_file() and path.name not in ['OUTPUT_MANIFEST.json','delivery_check.log']}
dump('OUTPUT_MANIFEST.json',manifest)
print(json.dumps(dict(pass_=True,status='INCONCLUSIVE',reports=3,links=len(links),source_sha_files=len(after),core_plus_details_seconds=cost['main_plus_details_recorded_seconds'])))
