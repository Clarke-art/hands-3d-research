import sys
sys.dont_write_bytecode=True
from data import *

def trace(name,incoming,last):
    rows=[];seen=set(last);event=None
    # Finite mesh/repetition guards bound traversal; no row count is an authority.
    while True:
        records=row_step(incoming,last)
        if not all(r['unique_quad'] for r in records):
            event={'type':'NON_UNIQUE_OR_NON_QUAD_CONTINUATION','row':len(rows)+1,'records':records};break
        fs=[r['face_id'] for r in records];out=[r['outgoing_edge'] for r in records];ids={v for fi in fs for v in F[fi]};tip={v for ei in out for v in E[ei]}
        if seen&set(fs):event={'type':'REVISITED_FACE','row':len(rows)+1,'face_ids':fs};break
        events=[]
        if ids&NAILS['thumb']:events.append('FROZEN_NAIL_CONFLICT')
        if ids&CAP:events.append('FROZEN_CAP_CONFLICT')
        if any(len(ADJ[v])!=4 for v in tip):events.append('OUTGOING_ROW_NONREGULAR_VALENCE')
        if len(out)==2 and len(set(E[out[0]])&set(E[out[1]]))!=1:events.append('SECTOR_CHAIN_CORRESPONDENCE_LOST')
        row={'row_id':name+f'{len(rows)+1:02d}','face_ids':fs,'vertex_ids':sorted(ids),'incoming_edge_ids':incoming,'outgoing_edge_ids':out,'outgoing_vertex_ids':sorted(tip),'records':records,'valences':{str(v):len(ADJ[v]) for v in sorted(tip)},'nail_overlap':sorted(ids&NAILS['thumb']),'cap_overlap':sorted(ids&CAP),'event_types':events}
        rows.append(row);seen.update(fs)
        if events:
            event={'type':events,'row':len(rows),'face_ids':fs,'row_id':row['row_id'],'following_row_negative_control':row_step(out,fs)};break
        incoming=out;last=fs
    return {'rows':rows,'first_structural_or_authority_event':event,'event_is_automatically_shared_role_stop':False,'trace_rule':'Unique outward incident quad; continue through its opposite edge; stop audit traversal at first fixed-anchor conflict/nonregular valence/lost correspondence/revisit. No angular or distance threshold.'}
distal=trace('D',[edge(2774,1396)],STACK['rings'][0]['proximal_face_strip'])
prox=trace('P',[edge(2360,3238),edge(3238,1422)],STACK['rings'][-1]['distal_face_strip'])
dump('RAW_LOCAL_COLUMN_TRACES.json',{'distal_non_nail':distal,'proximal':prox})
print(json.dumps({k:{'rows':[(r['row_id'],r['face_ids'],r['event_types']) for r in t['rows']],'event':t['first_structural_or_authority_event']} for k,t in [('distal',distal),('proximal',prox)]},indent=2))
