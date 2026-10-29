import json,hashlib,requests
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
SRC=ROOT/'references/piano_motion/pianovam_sample_r1'
BASE='https://huggingface.co/datasets/PianoVAM/PianoVAM_v1/resolve/main/'
recording='2024-03-04_03-46-36'
metadata=json.loads((SRC/'metadata.json').read_text())
entry=next(e for e in metadata.values() if e['record_time']==recording)
assert entry['performance_method']=='Solo' and entry['split']!='special(4hands)'
(SRC/'selected_metadata_entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[]
for directory,ext in [('Handskeleton','json'),('MIDI','mid'),('Fingering','tsv'),('Video','mp4')]:
    relative=f'{directory}/{recording}.{ext}';url=BASE+relative
    h=requests.head(url,allow_redirects=True,timeout=90);h.raise_for_status()
    size=int(h.headers.get('content-length') or h.headers.get('x-linked-size') or 0)
    if directory=='Video' and (not size or size>30000000):
        files.append({'remote_path':relative,'downloaded':False,'size':size,'reason':'Video cap 30 MB'});continue
    target=SRC/relative;target.parent.mkdir(exist_ok=True)
    if not target.exists():
        r=requests.get(url,timeout=120);r.raise_for_status();target.write_bytes(r.content)
    data=target.read_bytes();assert not size or len(data)==size
    files.append({'remote_path':relative,'url':url,'downloaded':True,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'head_size':size})
    print(directory,len(data),flush=True)
data={'DATASET':'PianoVAM_v1','DATASET_VERSION':'v1.2','LICENSE':'CC BY-NC-SA 4.0','USAGE_SCOPE':'INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY','DO_NOT_PROMOTE_DATASET_MOTION_TO_COMMERCIAL_PRODUCT':True,'SOURCE_RECORDING_ID':recording,'SOURCE_PIECE':entry['piece'],'SOURCE_PERFORMER':entry['P1_name'],'recording_attempts':1,'selection':'Shortest two solo entries compared by duration and HEAD size; Mozart 22.805 s has smaller video and richer Fingering than Ravel 22.400 s. Four-hands excluded.','head_comparison':[{'recording':'2024-02-17_21-37-57','duration_sec':22.4,'skeleton_bytes':3578138,'midi_bytes':676,'fingering_bytes':1736,'video_bytes':9052490},{'recording':recording,'duration_sec':22.805,'skeleton_bytes':3259497,'midi_bytes':1263,'fingering_bytes':7706,'video_bytes':7343859}],'files':files,'metadata_bytes':(SRC/'metadata.json').stat().st_size,'DOWNLOADED_FILE_COUNT':1+sum(f['downloaded'] for f in files),'DOWNLOADED_BYTES':(SRC/'metadata.json').stat().st_size+sum(f.get('bytes',0) for f in files),'generated_metadata_entry_not_downloaded':True,'attribution':{'dataset':'PianoVAM / PianoVAM authors, Hugging Face PianoVAM/PianoVAM_v1','dataset_url':'https://huggingface.co/datasets/PianoVAM/PianoVAM_v1','reference_code':'https://github.com/yonghyunk1m/PianoVAM-Code','license_url':'https://creativecommons.org/licenses/by-nc-sa/4.0/','changes':'Single-window hand-local skeletal retarget to an independent test Action.','commercial_use':False}}
(OUT/'PIANOVAM_SINGLE_SAMPLE_ACQUISITION_R1_STATUS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
