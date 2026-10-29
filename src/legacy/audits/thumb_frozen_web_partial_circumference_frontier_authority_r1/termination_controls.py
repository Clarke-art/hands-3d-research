import sys,itertools
sys.dont_write_bytecode=True
from local_data import *
S=read(OUT/'THUMB_PROXIMAL_RING_STACK_R1.json');fs=S['face_ids'];sets={fi:set(F[fi]) for fi in fs};minimal=[]
for n in [1,2]:
    for choice in itertools.combinations(fs,n):
        ids=set().union(*(sets[fi] for fi in choice))
        if SEEDS<=ids and (n==1 or choice[1] in FADJ[choice[0]]):minimal.append(list(choice))
    if minimal:break
assert minimal==[[1178,1179]]
stack=set(S['vertex_set']['vertex_ids']);otherrows=[]
for v in sorted(WEB-SEEDS):
    otherrows.append({'vertex_id':v,'shares_face_with_stack_vertices':sorted({w for fi in VF[v] for w in F[fi]}&stack),'one_ring_stack_contacts':sorted(grow({v},1)&stack),'two_ring_stack_contacts':sorted(grow({v},2)&stack),'role_inference':'No graph path or angular nearest projection manufactured; no auto shared extension.'})
base=read(OUT/'LOCAL_DIAGNOSTIC_STRIP_SETS.json')['F3'];baseids=set(base['shared_vertex_ids']);end=read(OUT/'DISTAL_PROXIMAL_TERMINATION_AUDIT.json');alternatives=[]
choices=[('CROP_AT_R00_R08',[]),('DISTAL_ONE_NON_NAIL_FACE',[1176]),('DISTAL_TWO_NON_NAIL_FACES',[1176,1213]),('PROXIMAL_ONE_FACE_ROW',end['PROXIMAL']['two_face_row_continuation_probe'][0]['face_ids']),('PROXIMAL_TWO_FACE_ROWS',list({fi for h in end['PROXIMAL']['two_face_row_continuation_probe'] for fi in h['face_ids']}))]
whole=max((set(r['core_including_ring']['vertex_ids']) for r in RAW),key=len)
for name,added in choices:
    ids=baseids|{v for fi in added for v in F[fi]};rest=whole-ids;cs=components(rest);tipcomp=next(c for c in cs if 284 in c)
    alternatives.append({'name':name,'added_face_ids':added,'added_vertex_ids':sorted(ids-baseids),'diagnostic_shared_vertex_count':len(ids),'surface_audit':surface(ids),'cap_overlap':sorted(ids&CAP),'nail_overlap':sorted(ids&NAILS['thumb']),'cap_nail_continuity':CAP|NAILS['thumb']<=tipcomp,'same_frozen_web_membership':True,'is_authority_candidate':False})
dump('LOCAL_TERMINATION_NONUNIQUENESS_CONTROLS.json',{'status':'MULTIPLE_STRUCTURALLY_VALID_STOP_CHOICES','F1_minimum_face_connector':{'minimum_face_count':n,'all_minimizers':minimal,'conclusion':'Unique seed connector, but minimum seed cover is not a supported anatomical stop rule.'},'other17_web_local_projection':otherrows,'termination_alternatives':alternatives,'distal_asymmetry':'Face1177 contains fixed thumb nail v304 and cannot become default shared support; neighboring face1176 does not. One-row/two-row tapered alternatives on this side preserve fixed anchors. Nail exclusion constrains extension but does not uniquely mandate a flat termination at R00.','proximal':'Real face-strip continuation exists for both boundary columns for two rows past R08; no local topology stop or source collision identifies R08 as anatomical termination.','no_candidate_or_membership_applied':True,'single_remaining_local_blocker':'THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY'})
print('Unique F1 seed connector:',minimal,'; termination alternatives:',[(r['name'],r['surface_audit']['surface_supported'],r['nail_overlap']) for r in alternatives])
