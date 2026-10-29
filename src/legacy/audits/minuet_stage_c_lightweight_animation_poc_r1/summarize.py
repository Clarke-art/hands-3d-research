from pathlib import Path
import json
P=Path(__file__).resolve().parent
r=json.loads((P/'ACTUAL_VALIDATION.json').read_text());rows=r['rows'];out={}
for label,a,b in [('early',.95,1.65),('late',3.70,3.9),('whole',0,6)]:
 rr=[v for v in rows if a<=v['time']<=b]
 out[label]={s:dict(middle_ring_pair_sum=sum(x[s]['pair_intersections']['MIDDLE_RING'] for x in rr),middle_ring_peak=max(x[s]['pair_intersections']['MIDDLE_RING'] for x in rr),middle_ring_hit_samples=sum(x[s]['pair_intersections']['MIDDLE_RING']>0 for x in rr),black_peak_mm=max([h['depth_mm'] for x in rr for h in x[s]['black_hits']]+[0]),black_depth_sum_mm=sum(h['depth_mm'] for x in rr for h in x[s]['black_hits']),black_hit_rows=sum(len(x[s]['black_hits']) for x in rr)) for s in ['source','new']}
out['exact_probes']=[x for x in rows if abs(x['time']-1.133333333)<1e-7 or abs(x['time']-3.825)<1e-7]
out['adjacent_pairs']={k:{s:dict(peak=max(x[s]['pair_intersections'][k] for x in rows),sum=sum(x[s]['pair_intersections'][k] for x in rows),hit_samples=sum(x[s]['pair_intersections'][k]>0 for x in rows)) for s in ['source','new']} for k in ['INDEX_MIDDLE','MIDDLE_RING','RING_LITTLE']}
out['black_keys']={str(m):{s:dict(peak_mm=max([h['depth_mm'] for x in rows for h in x[s]['black_hits'] if h['midi']==m]+[0]),hit_samples=sum(any(h['midi']==m for h in x[s]['black_hits']) for x in rows)) for s in ['source','new']} for m in [66,68,70,73,75,78,80,82]}
(P/'SPATIAL_SUMMARY.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
