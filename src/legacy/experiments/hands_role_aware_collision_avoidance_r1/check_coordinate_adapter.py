from role_planner import *
p=Planner(read(OUT/'EVENT_SCOPE.json'));rows=[]
for k,t in enumerate(p.times):
    for j in p.changed:
        vid=c.MARKERS['R'][j]['mesh_vertex'];actual=p.actual['vertices'][k,vid]
        point=p.marker(k,j,p.source[k,j]);segs=p.skeleton(k,j,p.source[k,j])
        rows.append(dict(t=float(t),digit=c.DIGITS[j],pad_vs_actual_mm=float(np.linalg.norm(point-actual)*1000),
            native_fk_segments_m=[[[*a],[*b]] for a,b in segs],segment_lengths_mm=[float(np.linalg.norm(a-b)*1000) for a,b in segs]))
assert max(r['pad_vs_actual_mm'] for r in rows)<.03
assert all(2<l<70 for r in rows for l in r['segment_lengths_mm'])
save('COORDINATE_ADAPTER_CHECK.json',dict(pass_=True,rows=rows,
    reason='Use existing frozen native REST/REL and actual skin pad, keep all parameter bounds/portal policy unchanged',
    invalid_prior_static_optimizer_calls=1,invalid_prior_result='STATIC_PREFLIGHT_RESULT.json',new_dynamic_candidates=0))
print('NATIVE_FK_ADAPTER_VERIFIED',max(r['pad_vs_actual_mm'] for r in rows),p.radii,flush=True)
