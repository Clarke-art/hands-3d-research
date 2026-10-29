import sys
sys.dont_write_bytecode=True
import os,json,hashlib,subprocess,time,collections
from pathlib import Path
ROOT=Path(r'D:\codex one\3D interactive components')
H=ROOT/'hands'; O=Path(__file__).parent
def save(n,d):
    (O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        while b:=f.read(4*1024*1024): h.update(b)
    return h.hexdigest()
def walk(r):
    stack=[r];files=[];dirs=[];issues=[]
    while stack:
        d=stack.pop(); st=d.stat(follow_symlinks=False)
        if st.st_file_attributes&0x400:
            issues.append({'path':str(d),'type':'reparse'});continue
        dirs.append(str(d))
        with os.scandir(d) as entries:
            for e in entries:
                p=Path(e.path)
                if p==O:continue
                s=e.stat(follow_symlinks=False)
                if s.st_file_attributes&0x400:
                    issues.append({'path':str(p),'type':'reparse'});continue
                if s.st_file_attributes&0x10:stack.append(p)
                else:files.append((p,s))
    return files,dirs,issues
def owner(p):return Path(p).relative_to(ROOT).parts[0]
names=sorted(x.name for x in ROOT.iterdir() if x.is_dir() and x.name.startswith('hands_'))
assert len(names)==17,names
resume='--references-only' in sys.argv
if not resume:save('ROOT_BEFORE.json',{'time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'entries':[str(p) for p in ROOT.iterdir()],'directories':names})
inventory=json.loads((O/'DIRECTORY_INVENTORY.json').read_text()) if resume else []
baseline=json.loads((O/'FILES_BEFORE.json').read_text()) if resume else {}
for name in ([] if resume else names+['hands']):
    r=ROOT/name;files,dirs,issues=walk(r);rows=[]
    for p,s in sorted(files,key=lambda x:str(x[0])):
        if p==H/'AGENTS.md':continue
        s0=p.stat(); digest=sha(p);s1=p.stat()
        assert (s0.st_size,s0.st_mtime_ns,s0.st_ino)==(s1.st_size,s1.st_mtime_ns,s1.st_ino),f'Changed while hashing: {p}'
        rows.append({'path':str(p),'relative':str(p.relative_to(r)),'bytes':s0.st_size,'sha256':digest,'mtime_ns':s0.st_mtime_ns,'file_id':s0.st_ino,'device':s0.st_dev,'nlink':s0.st_nlink})
    baseline[name]=rows
    total=sum(x['bytes'] for x in rows)
    print('HASHED',name,len(rows),total,flush=True)
    if name!='hands':
        inventory.append({'name':name,'source':str(r),'proposed_destination':str(H/name),'destination_conflict':(H/name).exists(),'file_count':len(rows),'directory_count_including_root':len(dirs),'logical_bytes':total,'GiB':total/(1024**3),'reparse_or_scan_issues':issues,'hardlinked_files':sum(x['nlink']>1 for x in rows),'last_write_ns':max((x['mtime_ns'] for x in rows),default=0)})
if not resume:save('FILES_BEFORE.json',baseline);save('DIRECTORY_INVENTORY.json',inventory)
# rg locates references without executing historical scripts. --no-follow is the default.
args=['rg','-l','-F','--hidden','--no-ignore','-g','!*.blend','-g','!*.blend1','-g','!*.mp4','-g','!*.png','-g','!*.jpg','-g','!*.npz','-g','!*.dll','-g','!*.pyd','-g','!*.onnx','-g','!*.wav','-g','!*.pyc','-g','!*.gif','-g','!*.glb','-g','!*.zip','-g','!*.gz','-g','!*.tar','-g','!*.7z','-g','!*.pdf','-g','!**/directory_structure_correction_r1/**']
for n in names:args+=['-e',n]
args+=['-e','PIANO_CONTACT_EXECUTION_FOUNDATION_R3','-e','hands_contact_execution_foundation_r3',str(ROOT)]
p=subprocess.run(args,capture_output=True,text=True,encoding='utf8');assert p.returncode in (0,1),(p.returncode,p.stderr)
save('REFERENCE_SCAN_COMMAND.json',{'args':args,'stderr':p.stderr,'returncode':p.returncode,'scope':'All root trees, hidden and ignored text included; binary content excluded by rg and explicit globs; no symlink traversal.'})
hits=[]
for f in p.stdout.splitlines():
    fp=Path(f)
    try:t=fp.read_text(encoding='utf-8-sig')
    except UnicodeError:
        hits.append({'file':f,'owner':owner(f),'scan_error':'non-UTF8 matched text; unresolved'});continue
    lower=t.lower();refs=[n for n in names if n.lower() in lower]
    lines=t.splitlines();examples=[]
    for i,line in enumerate(lines,1):
        matched=[n for n in refs if n.lower() in line.lower()]
        if matched or 'piano_contact_execution_foundation_r3' in line.lower() or 'hands_contact_execution_foundation_r3' in line.lower():
            for n in matched or ['R3']:
                pos=line.lower().find(n.lower())
                examples.append({'target':n,'line':i,'text':line[max(0,pos-150):pos+len(n)+250]})
    executable=fp.suffix.lower() in {'.py','.ps1','.js','.mjs','.ts','.bat','.cmd','.html','.sh','.toml','.ini','.cfg','.yaml','.yml'}
    frozen=any(w in fp.name.upper() for w in ['PROTECT','FROZEN','POLICY_LOCK','HASHES','MANIFEST'])
    hits.append({'file':f,'owner':owner(f),'sha256':sha(fp),'bytes':fp.stat().st_size,'targets':refs,'potential_runtime_source':executable,'protection_record':frozen,'examples':examples})
save('REFERENCE_INDEX.json',hits)
latest=ROOT/'hands_long_context_corridor_ik_bridge_r2'/'PROTECTED_FILES_BEFORE.json'
old=json.loads(latest.read_text(encoding='utf8'))
relations=[]
for x in inventory:
    prefix=x['source']+'\\'; entries={p:h for p,h in old.items() if p.startswith(prefix)}
    current={r['path']:r['sha256'] for r in baseline[x['name']]}
    relations.append({'name':x['name'],'latest_R2_manifest':str(latest),'entries':len(entries),'same_hash':sum(current.get(p)==h for p,h in entries.items()),'missing':[p for p in entries if p not in current],'different':[p for p,h in entries.items() if p in current and current[p]!=h],'current_additional_files':len(current.keys()-entries.keys()),'protection_reference_records':[a['file'] for a in hits if a.get('protection_record') and x['name'] in a.get('targets',[])]})
save('PROTECTION_RELATIONSHIPS.json',relations)
summary=[]
for x in inventory:
    n=x['name'];out=[a for a in hits if a['owner']==n and a.get('potential_runtime_source')];inc=[a for a in hits if a['owner']!=n and n in a.get('targets',[])];live=[a for a in inc if a.get('potential_runtime_source')]
    summary.append({'name':n,'outgoing_potential_runtime_sources':len(out),'incoming_reference_files':len(inc),'incoming_potential_runtime_sources':len(live),'incoming_runtime_sources':[a['file'] for a in live],'outgoing_runtime_sources':[a['file'] for a in out],'protection_entries':next(a['entries'] for a in relations if a['name']==n)})
save('DEPENDENCY_SUMMARY.json',summary)
save('R3_PATH_PRECHECK.json',{'required_output':str(H/'hands_contact_execution_foundation_r3'),'wrong_root_exists':(ROOT/'hands_contact_execution_foundation_r3').exists(),'correct_output_exists':(H/'hands_contact_execution_foundation_r3').exists(),'matched_source_files':[a['file'] for a in hits if any(e['target']=='R3' for e in a.get('examples',[]))],'research_started_by_this_task':False})
print(json.dumps(summary,ensure_ascii=False),flush=True)
