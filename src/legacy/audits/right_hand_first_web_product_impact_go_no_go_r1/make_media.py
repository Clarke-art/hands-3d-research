"""Assemble 7-second product observation videos and a small, purposeful evidence set.

No new detection heuristic and no severity census: the point is Human-visible
observation of continuous motion, not a millisecond-accurate defect locator.
"""
import json, subprocess
from pathlib import Path


OUT = Path(__file__).resolve().parent
VIEWS = ['DEFAULT_TEACHING_VIEW', 'NORMAL_ORBIT_VIEW', 'REASONABLE_CLOSE_VIEW']
FF = 'D:/ffmpeg/bin/ffmpeg.exe'
FP = 'D:/ffmpeg/bin/ffprobe.exe'
DATA = json.loads((OUT / 'PRODUCT_VIEW_OBSERVATION_R1.json').read_text(encoding='utf-8-sig'))
FRAMES = {r['frame']: r for r in DATA['frames'] if 'observation' not in r}
assert len(FRAMES) == 210

def frame_path(v, f):
    return OUT / 'product_views' / f'BASELINE_FROZEN__F{f:03d}__{v}.png'


missing = [str(frame_path(v, f)) for v in VIEWS for f in range(1, 211) if not frame_path(v, f).exists()]
assert not missing, missing[:5]

records = []
for v in VIEWS:
    dst = OUT / f'product_7s_{v.lower()}.mp4'
    subprocess.run([FF, '-y', '-loglevel', 'error', '-framerate', '30', '-start_number', '1',
                    '-i', str(OUT / 'product_views' / f'BASELINE_FROZEN__F%03d__{v}.png'),
                    '-frames:v', '210', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', str(dst)], check=True)
    meta = json.loads(subprocess.check_output(
        [FP, '-v', 'error', '-show_entries', 'stream=width,height,nb_frames,r_frame_rate:format=duration',
         '-of', 'json', str(dst)]))
    assert abs(float(meta['format']['duration']) - 7.0) < 0.05, meta
    assert meta['streams'][0]['nb_frames'] == '210', meta
    records.append({'view': v, 'file': dst.name, 'metadata': meta})

# Side-by-side teaching + orbit + close, single 7s file for review convenience.
filt = ("[0:v][1:v][2:v]hstack=inputs=3,"
        "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='DEFAULT TEACHING':x=12:y=12:fontcolor=white:fontsize=20:box=1:boxcolor=black@0.55,"
        "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='NORMAL ORBIT':x=972:y=12:fontcolor=white:fontsize=20:box=1:boxcolor=black@0.55,"
        "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='REASONABLE CLOSE':x=1932:y=12:fontcolor=white:fontsize=20:box=1:boxcolor=black@0.55[v]")
subprocess.run([FF, '-y', '-loglevel', 'error',
                '-i', str(OUT / 'product_7s_default_teaching_view.mp4'),
                '-i', str(OUT / 'product_7s_normal_orbit_view.mp4'),
                '-i', str(OUT / 'product_7s_reasonable_close_view.mp4'),
                '-filter_complex', filt, '-map', '[v]', '-frames:v', '210',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                str(OUT / 'product_7s_three_views.mp4')], check=True)
meta = json.loads(subprocess.check_output(
    [FP, '-v', 'error', '-show_entries', 'stream=width,height,nb_frames:format=duration', '-of', 'json',
     str(OUT / 'product_7s_three_views.mp4')]))
assert meta['streams'][0]['nb_frames'] == '210', meta
records.append({'view': 'THREE_VIEW_STACK', 'file': 'product_7s_three_views.mp4', 'metadata': meta})

(OUT / 'VIDEO_VERIFICATION_R1.json').write_text(json.dumps(
    {'status': 'PASS', 'duration_seconds': 7, 'fps': 30, 'frames': 210,
     'videos': records}, ensure_ascii=False, indent=2), encoding='utf-8')
print('PRODUCT_MEDIA_READY')