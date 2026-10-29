from pathlib import Path
import json,hashlib,re
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
read=lambda n:json.loads((P/n).read_text(encoding='utf-8-sig'))
proof=read('KEYBOARD_INDEPENDENT_VERIFICATION_R1.json');im=Image.open(P/'KEY_MAPPING_PROOF_BASE.png').convert('RGB');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',23)
for row in proof['actual_camera_projected_sample_labels']:
 x,y=row['pixel'];text=row['label'];box=d.textbbox((0,0),text,font=font);w=box[2];x=max(8,min(1592-w,x-w/2));d.text((x,y),text,font=font,fill='#ffe6b1')
d.text((25,20),'APPROVED 88-KEY GEOMETRY | MIDI 21=A0 ... 108=C8 | LOW -> HIGH',font=font,fill='#f3f6f9');im.save(P/'KEY_MAPPING_PROOF_R1.png')
required=['KEYBOARD_AUTHORITY_R1.json','KEYBOARD_COORDINATE_FRAME_R1.json','KEYBOARD_88_KEY_TABLE_R1.json','PERFORMANCE_TIMELINE_R1.json','FINGERING_AUTHORITY_R1.json','FINGERTIP_CONTACT_MARKERS_R1.json','ROOT_ANCHOR_MODEL_R1.json','CONTACT_TOLERANCE_POLICY_R1.json','CONTACT_MEASUREMENTS_R1.json','ACTION_IDENTITY_R1.json','MINIMUM_SAFETY_R1.json','FINAL_ASSET_PROTECTION_R1.json','KEY_EVENT_ANIMATION_R1.json','review.html','PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1_REPORT.md','PIANO_KEYBOARD_SPATIAL_ANCHOR_VALIDATION_CANDIDATE_R1.blend','product_7s_dual_on_88keys.mp4','product_7s_teaching_keyboard_view.mp4','product_7s_contact_close.mp4']
assert all((P/n).is_file() and (P/n).stat().st_size>0 for n in required)
html=(P/'review.html').read_text(encoding='utf-8');links=re.findall(r'(?:src|href)="([^"]+)"',html);assert all((P/f).exists() for f in links if not f.startswith('https://'))
for p in P.glob('*.json'):json.loads(p.read_text(encoding='utf-8-sig'))
I=read('ACTION_IDENTITY_R1.json');assert I['candidate_sha256']==hashlib.sha256((P/required[15]).read_bytes()).hexdigest()
T=read('PERFORMANCE_TIMELINE_R1.json');assert all(0<=e['time_sec']<7 for e in T['events']);assert all(e['key_index']==e['midi_note']-21 for e in T['events'] if e['event_type']!='PEDAL');assert all(e['finger_confidence'] is None for e in T['events'])
assert hashlib.sha256((P/'CONTACT_TOLERANCE_POLICY_R1.json').read_bytes()).hexdigest()==read('PRE_RESULT_POLICY_LOCK_R1.json')['sha256']
notes=T['notes'];short=read('KEY_EVENT_ANIMATION_R1.json')['sub_60Hz_note_visibility_audit']['unsampled_note_ids'];short_info=[{'note_id':n['note_id'],'duration_ms':(n['source_off_sec']-n['source_on_sec'])*1000,'hand':n['hand'],'note':n['note_name']} for n in notes if n['note_id'] in short]
result={'status':'PASS','required_deliverables':len(required),'local_review_links_valid':True,'candidate_hash_current':True,'all_JSON_parse':True,'timeline_key_mapping_all_events':True,'policy_hash_unchanged':True,'short_note_preview_limit':short_info,'visual_inspection':'210/210 teaching output frames via seven consecutive sheets plus ordinary close views and time strip; Human review pending','naturalness':'FAIL_CANDIDATE','findings':['Repeated target-note/pad separation and fingertip occlusion in key volumes','Large unchanged wrist-orientation variation especially right','Piecewise smooth root; no >10mm/60Hz teleport flag','No exact fingering or independent metric contact claim']}
(P/'DELIVERY_VERIFICATION_R1.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
manifest={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in P.iterdir() if p.is_file() and p.name!='FINAL_OUTPUT_MANIFEST_R1.json'}
(P/'FINAL_OUTPUT_MANIFEST_R1.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
