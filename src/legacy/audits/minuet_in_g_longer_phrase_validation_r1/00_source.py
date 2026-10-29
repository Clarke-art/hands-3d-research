from pathlib import Path
import urllib.request,json,hashlib
from datetime import datetime,timezone,timedelta
P=Path(__file__).resolve().parent;ROOT=P.parents[1];BASE='https://www.mutopiaproject.org/ftp/BachJS/BWVAnh114/anna-magdalena-04/'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
manifest={}
for name,url in [('piece-info-id75.html','https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=75'),('anna-magdalena-04.mid',BASE+'anna-magdalena-04.mid'),('anna-magdalena-04.ly',BASE+'anna-magdalena-04.ly')]:
 req=urllib.request.Request(url,headers={'User-Agent':'3D-Hands-Piano-Source-Validation/1.0'})
 with urllib.request.urlopen(req,timeout=30) as res:data=res.read();info={'url':url,'response_url':res.url,'content_type':res.headers.get('Content-Type'),'bytes':len(data)}
 if name.endswith('.mid'):assert data[:4]==b'MThd'
 (P/'source'/name).write_bytes(data);manifest[name]={**info,'sha256':sha(P/'source'/name)}
(P/'SOURCE_PROVENANCE.json').write_text(json.dumps({'work':'Menuet in G, BWV Anh.114','edition':'Mutopia-2017/01/19-75','instrument':'Harpsichord, Piano, Clavichord','source':'Bach-Gesellschaft as credited by edition','maintainer':'Allen Garvin','license':'Public Domain as labelled by Mutopia','selected_version':'Original keyboard version; NOT guitar/trumpet arrangement','local_prior_target_MIDI_found':False,'input_authority':'Direct Human reply: adopt original version from same Mutopia upstream','retrieved_client_time':datetime.now(timezone(timedelta(hours=8))).isoformat(),'files':manifest,'download_only':'No MIDI events rewritten, no score simplification, no new motion or candidate'},ensure_ascii=False,indent=2),encoding='utf8')
(P/'USER_AUTHORITY_BIND.json').write_text(json.dumps({'authority':'Current direct Human task MINUET_IN_G_LONGER_PHRASE_VALIDATION_R1','Musette_short_phrase_Human_visible_acceptance':'ACCEPTABLE_IN_PRODUCT_VIEW','engineering_limitations_retained':True,'historical_engineering_results_not_overwritten':True,'cross_song_generalization':'NOT_YET_ESTABLISHED','source_choice':'Same Mutopia upstream original keyboard version, explicitly selected by Human','scope':'Opening16 notated bars, no automatic repeat expansion or score changes','candidate_limit':1,'fail_closed_before_generation_if_core_structure_unsupported':True},ensure_ascii=False,indent=2),encoding='utf8')
print('CANONICAL_KEYBOARD_SOURCE_SAVED_UNCHANGED',json.dumps(manifest,ensure_ascii=False),flush=True)
