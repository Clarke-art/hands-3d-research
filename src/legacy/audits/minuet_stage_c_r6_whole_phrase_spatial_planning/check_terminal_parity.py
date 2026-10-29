from whole_phrase_model import *
actual=dict(np.load(P/'ACTUAL_TERMINAL_SKIN.npz'))
trajectory=dict(np.load(P/'TERMINAL_TRAJECTORY_EVIDENCE.npz'))
ix=actual['indices'];times=actual['times']
max_terminal=0.;max_source=0.;witness=None
for begin in range(0,len(times),25):
    sl=slice(begin,begin+25);model=Skin(times[sl]);predicted=model(trajectory['qdeg'][ix[sl]])
    errors=np.linalg.norm(predicted-actual['terminal'][sl],axis=-1)*1000
    se=np.linalg.norm(model(original=True)-actual['source'][sl],axis=-1)*1000
    max_source=max(max_source,float(se.max()))
    if errors.max()>max_terminal:
        ti,vi=np.unravel_index(errors.argmax(),errors.shape);max_terminal=float(errors[ti,vi])
        witness=dict(video_sec=float(times[begin+ti]),vertex=int(vi),error_mm=max_terminal)
dump('TERMINAL_SKIN_PARITY.json',dict(terminal_max_mm=max_terminal,source_max_mm=max_source,
    witness=witness,samples=len(times),pass_=bool(max_terminal<.03 and max_source<.03),
    includes_frozen_corrective_driver=True,actual_blender_pose_checks=True,
    save_reopen='NOT_RUN_NO_VALID_CANDIDATE'))
print('TERMINAL_BLENDER_PARITY',max_terminal,max_source,flush=True)
