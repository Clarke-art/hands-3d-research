from stage_common import *
E=np.load(P/'evaluated.npz');A=np.load(P/'motion.npz');notes=read(P/'PERFORMANCE_TIMELINE.json')['notes'];rows=[]
for label,n in [('first_chord',notes[0]),('A3_single',notes[3]),('B3_long',notes[4]),('C4_long',notes[5]),('B3_return',notes[6])]:
    t=(n['note_on']+n['note_off'])/2;i=int(np.argmin(abs(E['times']-t)));pads=E['L_pads'][i]
    rows.append(dict(label=label,time=float(E['times'][i]),thumb_xyz_m=pads[0],little_xyz_m=pads[4],
        thumb_little_lateral_span_mm=float(abs(pads[0,0]-pads[4,0])*1000),
        thumb_q_deg=np.degrees(A['L_q'][i,0]),little_q_deg=np.degrees(A['L_q'][i,4])))
dump('VISIBLE_POSTURE_EVIDENCE.json',dict(rows=rows,
    provisional_G3_D4_key_center_span_mm=(c.KEYS[62-21]['key_center'][0]-c.KEYS[55-21]['key_center'][0])*1000,
    mode='READ_ONLY_POST_GENERATION_NO_REPAIR',
    observation='Normal teaching/side frames show appreciable idle thumb/little extension during index single-note holding; requires product-quality judgment, not a millimeter contact patch.',
    supported_cause='No event-relative home/layout target for inactive thumb/little; static L1/L2 joint prior and clearance alone can return to a wide open posture.',
    rig_modification_required_claimed=False,second_solve_performed=False))
print('POSTURE_SPANS',[(r['label'],round(r['thumb_little_lateral_span_mm'],1)) for r in rows],flush=True)
