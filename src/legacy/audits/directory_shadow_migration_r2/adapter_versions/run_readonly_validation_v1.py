import sys
sys.dont_write_bytecode=True
import os,json,hashlib,ast,zipfile,io,struct,re,math,time,encodings.cp437
from pathlib import Path
from readonly_path_adapter import PathAdapter
O=Path(__file__).parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
run=sys.argv[1];assert re.fullmatch(r'readonly_[0-9]{2}',run),run
dest=O/'runs'/run;dest.mkdir(parents=True,exist_ok=False)
registry=rd(O/'PATH_ADAPTER_REGISTRY_V2.json');expressions=rd(O/'LEGACY_PATH_EXPRESSIONS.json');adapter=PathAdapter(registry);adapter.pin()
allowed_reads={adapter.key(x['resolved_path']) for x in registry['inputs']};allowed_writes={adapter.key(dest/'RESULTS.json'),adapter.key(dest/'OPERATIONS.json')};denials=[]
def audit(event,args):
 if event=='open':
  path,mode,flags=args
  if isinstance(path,int):return
  key=adapter.key(path);writing=(isinstance(mode,str) and any(t in mode for t in 'wax+')) or (isinstance(flags,int) and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
  if writing and key not in allowed_writes:
   denials.append({'event':event,'path':str(path),'reason':'write outside two own result files'});raise PermissionError('Write denied')
  if not writing and key not in allowed_reads:
   denials.append({'event':event,'path':str(path),'reason':'read outside explicit registry'});raise PermissionError('Read denied')
 elif event in {'os.remove','os.rename','os.rmdir','os.mkdir','shutil.copyfile','subprocess.Popen','os.system','os.symlink','os.link'}:
  denials.append({'event':event,'reason':'mutation/process creation denied'});raise PermissionError(event+' denied')
 elif event=='exec':
  filename=args[0].co_filename
  if any(str(p).lower() in filename.lower() for p in [adapter.source,adapter.shadow,adapter.formal]):raise PermissionError('Historical program execution denied')
 elif event=='import':raise PermissionError('New imports denied after whitelist setup')
sys.addaudithook(audit)
started=time.monotonic();checks=[]
def check(name,value,scope='READ_ONLY_EXECUTED',details=None):
 checks.append({'name':name,'pass':bool(value),'scope':scope,'details':details})
 if not value:raise AssertionError(name)
def pilot(name):return adapter.json(adapter.pilot(name))
def midi_parse(b):
 assert b[:4]==b'MThd';hlen=struct.unpack('>I',b[4:8])[0];fmt,tracks,ppq=struct.unpack('>HHH',b[8:14]);assert not ppq&0x8000;pos=8+hlen;notes={};tempos=[];events=[]
 def vlq(data,i):
  value=0
  for _ in range(4):
   c=data[i];i+=1;value=(value<<7)|(c&127)
   if not c&128:return value,i
  raise ValueError('Invalid VLQ')
 for ti in range(tracks):
  assert b[pos:pos+4]==b'MTrk';length=struct.unpack('>I',b[pos+4:pos+8])[0];data=b[pos+8:pos+8+length];pos+=8+length;i=0;tick=0;running=None;seq=0
  while i<len(data):
   delta,i=vlq(data,i);tick+=delta;status=data[i]
   if status&128:i+=1
   else:
    assert running is not None;status=running
   if status==255:
    subtype=data[i];i+=1;n,i=vlq(data,i);payload=data[i:i+n];i+=n
    if subtype==81:tempos.append([tick,int.from_bytes(payload,'big')])
   elif status in [240,247]:n,i=vlq(data,i);i+=n;running=None
   else:
    assert 128<=status<=239;running=status;kind=status>>4;channel=status&15;n=1 if kind in [12,13] else 2;payload=data[i:i+n];assert len(payload)==n;i+=n
    if kind in [8,9]:
     e={'track':ti,'sequence':seq,'tick':tick,'type':'note_on' if kind==9 else 'note_off','time':delta,'note':payload[0],'velocity':payload[1],'channel':channel};notes[ti,seq]=e;events.append(e)
   seq+=1
 assert pos==len(b);return {'format':fmt,'tracks':tracks,'ppq':ppq,'tempos':tempos,'notes':notes,'events':events}
def npz_read(b):
 z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip() is None;arrays={}
 for n in z.namelist():
  assert n.endswith('.npy');data=z.read(n);assert data[:6]==b'\x93NUMPY';major=data[6];start=10 if major==1 else 12;length=struct.unpack('<H' if major==1 else '<I',data[8:start])[0];header=ast.literal_eval(data[start:start+length].decode('latin1' if major<3 else 'utf8'));descr=header['descr'];assert isinstance(descr,str) and 'O' not in descr;item=int(re.search(r'(\d+)$',descr).group(1));count=math.prod(header['shape']);assert len(data)-start-length==item*count
  arrays[n[:-4]]={'shape':list(header['shape']),'dtype':descr,'fortran_order':header['fortran_order'],'payload_bytes':item*count,'array_sha256':hashlib.sha256(data).hexdigest()}
 return arrays
try:
 # Actual byte reads for the entire immutable shadow and the exact external input whitelist.
 for row in registry['inputs']:adapter.bytes(row['logical_legacy_path'])
 check('registry_all_actual_reads_SHA_match',len(adapter.reads)==len(registry['inputs']),details={'files':len(registry['inputs'])})
 check('formal_hands_root_resolves',adapter.hands.name=='hands' and adapter.hands==Path(registry['project_root'])/'hands')
 wrong_hands=adapter.formal.parent/'hands';check('uncorrected_formal_parent_would_be_wrong',wrong_hands!=adapter.hands,details={'old':str(adapter.source.parent/'hands'),'naive_formal':str(wrong_hands),'naive_deep_shadow':str(adapter.shadow.parent/'hands'),'adapter':str(adapter.hands),'unmodified_legacy_script_works':False})
 path_tests=[]
 for e in expressions:
  before=Path(e['old_resolved'])
  if adapter.key(before) in adapter.rows:
   actual=adapter.legacy_parent_file(e['suffix']);adapter.bytes(actual);path_tests.append({'source':e['relative_source'],'line':e['line'],'old':e['old_resolved'],'naive_formal':e['naive_formal_resolved'],'adapted':str(actual),'classification':'VIA_PATH_ADAPTER','executed_read':True})
  else:path_tests.append({'source':e['relative_source'],'line':e['line'],'old':e['old_resolved'],'naive_formal':e['naive_formal_resolved'],'classification':'STATIC_ONLY_DIRECTORY_OR_NOT_REGISTERED','executed_read':False})
 check('pilot_formal_alias_maps_to_immutable_shadow',adapter.resolve(adapter.pilot('verify_midi.py'))==adapter.shadow/'verify_midi.py')
 B=adapter.json(adapter.source.parent/'hands_sequence_fingering_planning_r1/SOURCE_EVENT_BINDINGS.json');m=midi_parse(adapter.bytes(B['source_midi']));check('raw_MIDI_PPQ_tempo',m['ppq']==B['ppq'] and m['tempos']==B['tempo_events'])
 match=[]
 for bind in B['bindings']:
  for f in ['midi_note_on','midi_note_off']:
   e=bind[f];match.append(m['notes'].get((e['track'],e['sequence']))==e)
 check('23_notes_46_original_MIDI_bindings',len(B['bindings'])==23 and len(match)==46 and all(match),details={'bindings':len(B['bindings']),'events':len(match)})
 T=adapter.json(B['source_timeline']);byid={n['note_id']:n for n in T['notes']};check('source_timeline_original_bindings',all(byid[b['note_id']]==b['source_timeline_note'] for b in B['bindings']))
 P=pilot('POLICY_LOCK.json');C=adapter.json(P['source_input']['candidate_source']);cand=next(c for c in C['candidates'] if c['candidate_id']==P['source_input']['candidate_id']);fingers={n['note_id']:n['finger'] for n in cand['notes']};check('locked_C01_fingers_unchanged',len(fingers)==23 and all(fingers[n['note_id']]==n['finger'] for n in P['source_input']['notes']))
 R=pilot('SOURCE_MIDI_REVALIDATION.json');check('historic_MIDI_revalidation_consistent',R['midi_sha256']==B['source_midi_sha256'] and R['timeline_sha256']==B['source_timeline_sha256'] and R['candidate_sha256']==P['source_input']['candidate_sha256'] and len(R['notes'])==23)
 containers=[]
 for row in registry['inputs']:
  path=Path(row['logical_legacy_path'])
  if path.suffix=='.blend':
   header=adapter.bytes(path)[:12];containers.append({'legacy':str(path),'header_hex':header.hex(),'storage_prefix':'BLENDER' if header.startswith(b'BLENDER') else 'ZSTANDARD_FRAME' if header.startswith(bytes.fromhex('28b52ffd')) else 'UNKNOWN','sha256':row['expected_sha256'],'native_scene_loaded':False,'compressed_native_header_decoded':False})
 check('frozen_blend_containers_actual_byte_SHA_access',len(containers)>=4 and all(x['storage_prefix']!='UNKNOWN' for x in containers),scope='BYTE_CONTAINER_ONLY_NOT_BLENDER_REEXECUTION_OR_COMPRESSED_NATIVE_PARSE')
 meta=pilot('SKIN_MODEL_META.json');skin=npz_read(adapter.bytes(adapter.pilot('SKIN_MODEL.npz')));check('skin_NPZ_CRC_and_header_structure',skin['triangles']['shape'][0]==len(meta['triangle_labels']) and skin['weights']['shape'][0]==skin['rest_vertices']['shape'][0] and skin['weights']['shape'][1]==len(meta['names']) and len(meta['key_table'])==88)
 core_dir=adapter.hands/'audits/midi_driven_dual_hand_piano_performance_poc_r1';keys=adapter.json(core_dir/'KEYBOARD_88_KEY_TABLE_R1.json')['keys'];check('actual_88_key_geometry_source_matches_skin_metadata',keys==meta['key_table'])
 original=adapter.json(adapter.source.parent/'hands_contact_state_motion_planner_comparison_r1/ORIGINAL_ACTION_INSPECTION.json');ctx=pilot('R2_CONTEXT_RAW.json');check('13_existing_key_Action_digest_records_match',original['action_payloads']==ctx['action_payloads'] and len(original['action_payloads'])==13,scope='EXISTING_NATIVE_AUDIT_RECORDS_READ_ONLY_NOT_FRESH_ACTION_EXTRACTION')
 curve_checks=[]
 for key,curves in original['fcurves'].items():
  cc=ctx['curves'][key];assert len(cc)==len(curves)
  for a,b in zip(curves,cc):curve_checks.append(a['path']==b['path'] and a['index']==b['index'] and len(a['points'])==len(b['points']) and all(x['display_time']==y['time'] and x['angle']==y['value'] and x['interpolation']==y['interpolation'] for x,y in zip(a['points'],b['points'])))
 check('serialized_original_Action_FCurves_equal',all(curve_checks),scope='RECORD_CONSISTENCY_ONLY',details={'curve_records':len(curve_checks),'animated_keys':13,'88_geometry_keys':88})
 actual=pilot('R2_BASE_ACTUAL.json')+pilot('R2_ADAPTIVE_ACTUAL.json');summary=pilot('R2_FINAL_FACTS.json');delivery=pilot('R2_DELIVERY_CHECK.json');status=pilot('R2_FINAL_STATUS.json');ids=[x['id'] for x in actual];fail=sum(not x['all_gates'] for x in actual)
 check('historical_103_actual_records_and_86_failures_preserved',len(set(ids))==len(actual)==103 and fail==86 and delivery['unique_actual_samples']==103 and delivery['failed_actual_samples']==86,scope='HISTORICAL_RECORD_RECHECK_NOT_GEOMETRY_RECOMPUTE')
 check('historical_native_Action_source_not_saved_flags',all(x['native_identity'] and x['original_key_actions_match'] and not x['source_saved'] for x in actual),scope='HISTORICAL_RECORD_RECHECK')
 npz_checks=[]
 for x in actual:
  arrays=npz_read(adapter.bytes(adapter.pilot('AUDIT_'+x['id']+'_ACTUAL_SKIN.npz')));npz_checks.append({'id':x['id'],'shape':arrays['vertices']['shape'],'passed':arrays['vertices']['shape']==skin['rest_vertices']['shape']})
 check('103_actual_skin_evidence_archives_accessible_CRC',all(x['passed'] for x in npz_checks))
 code=pilot('R2_CODE_AND_CALL_AUDIT.json');check('historic_code_SHA_bindings',all(hashlib.sha256(adapter.bytes(adapter.pilot(n))).hexdigest()==h for n,h in code['script_sha256'].items()))
 before=pilot('PROTECTED_FILES_BEFORE.json');after=pilot('PROTECTED_FILES_AFTER.json');scope=pilot('R2_PROTECTION_SCOPE_AUDIT.json');check('historic_86259_protection_semantics_unchanged',len(before)==len(after)==86259 and before==after and scope['observed_new_path_count']==618 and scope['status']=='GLOBAL_FAIL_CONCURRENT_ADDITIONS; EXISTING_PROTECTED_FILES_PASS',scope='HISTORICAL_MANIFEST_CONTENT_NOT_CURRENT_GLOBAL_REHASH')
 report_refs=[]
 reports=delivery['required_deliverables']
 check('seven_original_report_delivery_SHA_bindings',isinstance(reports,dict) and len(reports)==7 and all(hashlib.sha256(adapter.bytes(adapter.pilot(n))).hexdigest()==h for n,h in reports.items()))
 if isinstance(reports,dict):reports=list(reports)
 else:reports=[x if isinstance(x,str) else x.get('file',x.get('name',x.get('path'))) for x in reports]
 for name in reports:
  # Actual report existence is established by immutable registry; parse only explicit concrete filenames.
  name=Path(name).name;text=adapter.bytes(adapter.pilot(name)).decode('utf-8-sig')
  refs=sorted(set(re.findall(r'(?<![A-Za-z0-9_])[A-Za-z][A-Za-z0-9_.-]*\.(?:json|py|npz|md|log|blend|casadi)\b',text)))
  for ref in refs:
   target=adapter.pilot(ref)
   try:physical=adapter.resolve(target);adapter.bytes(target);report_refs.append({'report':name,'reference':ref,'resolved':str(physical),'classification':'VIA_PATH_ADAPTER','read_verified':True})
   except PermissionError:report_refs.append({'report':name,'reference':ref,'classification':'UNVERIFIED_TEXT_MENTION_OR_DYNAMIC_REFERENCE','read_verified':False})
 tests=[]
 for label,operation in [('unregistered_read',lambda:adapter.bytes(adapter.hands/'unregistered_read_probe.json')),('formal_target_write',lambda:(adapter.formal/'forbidden.json').write_bytes(b'')),('source_R2_write',lambda:(adapter.source/'POLICY_LOCK.json').open('wb')),('shadow_write',lambda:(adapter.shadow/'POLICY_LOCK.json').open('wb')),('source_program_exec',lambda:exec(compile('pass',str(adapter.shadow/'verify_midi.py'),'exec'))),('root_link_creation',lambda:os.symlink(str(adapter.shadow),str(adapter.hands.parent/'forbidden_shadow_link')))]:
  try:operation();tests.append({'name':label,'blocked':False})
  except PermissionError:tests.append({'name':label,'blocked':True})
 check('six_side_effect_or_unlisted_access_denial_probes',all(x['blocked'] for x in tests),details=tests)
 check('original_R2_not_read_by_adapter',not any(Path(x['resolved']).is_relative_to(adapter.source) for x in adapter.reads))
 semantic={'checks':checks,'path_expression_tests':path_tests,'MIDI_binding_count':23,'MIDI_event_count':46,'containers':containers,'skin_container_structure':skin,'native_software_import_or_solver_calls':0,'Action_record_count':13,'actual_skin_archive_count':len(npz_checks),'historical_failures':fail,'historic_R2_status':status['status'],'historic_R2_scoped_PASS':status['C01_G4_E5_SCOPED_CONTINUOUS_BRIDGE_PASS'],'report_reference_checks':report_refs,'safety_probes':tests,'read_resources':sorted((x['resolved'],x['sha256']) for x in adapter.reads)}
 fingerprint=hashlib.sha256(json.dumps(semantic,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
 result={'task':'PIANO_HANDS_DIRECTORY_SHADOW_MIGRATION_R2','run':run,'status':'PASS_READ_ONLY_SCOPED_TESTS','checks':checks,'semantic_fingerprint':fingerprint,'semantic':semantic,'seconds':time.monotonic()-started,'source_scripts_executed':[],'protected_original_files_mutated':[],'immutable_shadow_files_mutated':[],'formal_target_created':False,'complete_Blender_solver_reproduction_PASS':False,'unknowns':['Fresh native Blend loading/linked resources/drivers/handlers not executed','CasADi/NumPy/SciPy binary loading and ABI not exercised','Historical __file__/CWD/dynamic exec/CLI imports not transparently patched or run','Report text mentions not in immutable whitelist remain unverified','All-17 relocation/source callers/cleanup ledger entry not tested by this one-directory pilot']}
 with (dest/'RESULTS.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
 with (dest/'OPERATIONS.json').open('x',encoding='utf8') as f:json.dump({'reads':adapter.reads,'audit_denials':denials,'input_handles_pinned':len(registry['inputs']),'policy':'Exact resource whitelist; no native or historical program execution; two own result files only'},f,ensure_ascii=False,indent=2)
 print('READ_ONLY_PASS',run,len(checks),'checks',len(adapter.reads),'immutable reads',fingerprint,flush=True)
finally:adapter.unpin()
