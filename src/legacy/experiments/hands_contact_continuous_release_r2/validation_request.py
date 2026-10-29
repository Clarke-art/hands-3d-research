from path_model import *
path=dict(np.load(OUT/'PATH_PREFLIGHT.npz'));curve=Curve();coeff=path['coefficients']
extra=read(OUT/'ADAPTIVE_PROBES.json')['times'];times=np.unique(np.r_[BASE['times'],extra])
np.savez_compressed(OUT/'VALIDATION_REQUEST.npz',times=times,delta_deg=curve.delta(coeff,times),ideal_qdeg=curve.state(coeff,times))
save('VALIDATION_REQUEST.json',dict(samples=len(times),base_samples=len(BASE['times']),extra_midpoint_samples=len(times)-len(BASE['times']),
    candidate_count=0,kind='Whole-window numeric-path preflight replay; no Action/Blend/video',
    exact_curve_coefficients_sha256=sha(OUT/'PATH_PREFLIGHT.npz'),source_sampling='240Hz + events; one midpoint pass in close/colliding proxy intervals'))
print('WHOLE_WINDOW_PREFLIGHT_REPLAY_REQUEST',len(times),flush=True)
