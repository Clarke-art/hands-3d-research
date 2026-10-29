import sys,ast
sys.dont_write_bytecode=True
from common import *
SOURCE=ROOT/'production_spec/stage4_blender/scripts/stage4a_t01_edgeloop.py'
tree=ast.parse(SOURCE.read_text(encoding='utf8'))
functions=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ['vcycle','opposite_at','walk']]
incident={v:[] for v in range(NV)};link={}
for ei,(a,b) in enumerate(E):incident[a].append(ei);incident[b].append(ei)
for vs in F:
    for j,v in enumerate(vs):
        ep=EF[tuple(sorted((vs[j-1],v)))];en=EF[tuple(sorted((v,vs[(j+1)%len(vs)])))]
        link.setdefault((v,ep),set()).add(en);link.setdefault((v,en),set()).add(ep)
env={'incident':incident,'edge_v':dict(enumerate(map(tuple,E))),'link':link,'VCYC':{}}
exec(compile(ast.Module(body=functions,type_ignores=[]),str(SOURCE),'exec'),env)
loops=[];seen=set()
for ei,(a,b) in enumerate(E):
    ff,sf,vf,kf=env['walk'](ei,a);bb,sb,vb,kb=env['walk'](ei,b);es=tuple(sorted(set(ff+bb)))
    if es in seen:continue
    seen.add(es)
    if sf!= 'closed' or sb!='closed':continue
    vs={v for e in es for v in E[e]}
    if len(vs)!=len(es):continue
    loops.append({'edge_ids':list(es),'vertex_ids':sorted(vs)})
results={};summary={}
for digit in ['thumb','index']:
    seed=TIPS[digit];required=CAP|NAILS['thumb']|{seed} if digit=='thumb' else INDEX_SOURCES|{seed}
    other={v for d,s in NAILS.items() if d!=digit for v in s}|{v for d,v in TIPS.items() if d!=digit}
    if digit=='index':other|=CAP
    rows=[]
    for lp in loops:
        rv=set(lp['vertex_ids'])
        if seed in rv:continue
        dc=component(seed,set(range(NV))-rv)
        # Must separate independently identified digit tip from every other digit tip / wrist.
        if dc&{v for d,v in TIPS.items() if d!=digit}:continue
        core=dc|rv
        if not NAILS[digit]<=core:continue
        geo=ANCHORS[digit]['native_direction_support'];axis=np.array(geo['axis']);origin=np.array(geo['axis_anchor_world_m'])
        ax=(N[sorted(rv)]-origin)@axis*1000;s,_,_,knots=PROJ[digit]
        row={**lp,'distal_interior':packed(dc),'core_including_ring':packed(core),'frozen_web_in_core':sorted(core&WEB),'other_anchor_conflicts':sorted(core&other),'missing_required_sources':sorted(required-core),'native_axial_min_max_mm':[float(ax.min()),float(ax.max())],'native_axial_mean_mm':float(ax.mean()),'corrected_chain_arc_min_max_mm':[float(s[sorted(rv)].min()),float(s[sorted(rv)].max())],'incident_face_ids':sorted({fi for v in rv for fi in V_F[v]}),'circumferential_completeness':'CLOSED_ORIGINAL_EDGE_LOOP_SEPARATES_DIGIT_TIP_FROM_OTHER_TIPS','surface_audit':surface_audit(core)}
        row['eligible_structural_core']=not(core&WEB or core&other or required-core) and row['surface_audit']['surface_supported']
        rows.append(row)
    rows.sort(key=lambda r:(r['core_including_ring']['count'],r['edge_ids']))
    eligible=[r for r in rows if r['eligible_structural_core']]
    maxima=[r for r in eligible if not any(set(r['core_including_ring']['vertex_ids'])<set(q['core_including_ring']['vertex_ids']) for q in eligible)]
    result={'status':'STRUCTURAL_EVIDENCE_NOT_ANATOMICAL_AUTHORITY','method_source':{'path':str(SOURCE.relative_to(ROOT)),'sha256':sha(SOURCE),'executed_definitions_only':['vcycle','opposite_at','walk'],'module_body_executed':False},'selection':'All pure topological opposite-edge closed loops; remove ring vertices and follow tip-connected component. Require nails and established source ingredients, exclude all other digit/wrist terminal/nail anchors and frozen web; require full face support. No nearest partition or skin weights.','rings':rows,'eligible_ring_count':len(eligible),'maximal_eligible_ring_count':len(maxima),'maximal_eligible_rings':[r['edge_ids'] for r in maxima],'unique_maximal_core':maxima[0] if len(maxima)==1 else None,'why_not_final_authority':'Last topological loop free of known web can conservatively bound distal core but does not establish the full shared interface outside it. First web may occupy a partial circumference before any topology failure.'}
    results[digit]=result
    summary[digit]={'rings':len(rows),'eligible':len(eligible),'maximal':len(maxima),'unique_core_count':maxima[0]['core_including_ring']['count'] if len(maxima)==1 else None,'unique_ring_ids':maxima[0]['vertex_ids'] if len(maxima)==1 else None,'arc_mm':maxima[0]['corrected_chain_arc_min_max_mm'] if len(maxima)==1 else None}
    # Augment existing branch evidence without rerunning sweeps.
    old=read(OUT/(digit.upper()+'_BRANCH_CONTINUITY_AUDIT.json'));old['true_topological_rings']=result
    for variant in old['variants'].values():
        clean=[]
        for r in variant['ring_sequence']:
            hits=set(r['ring']['ring_vertex_ids'])&set(variant['forbidden_anchor_ids'])
            r['ring']['known_shared_or_other_anchor_endpoint_ids']=sorted(hits)
            r['ring']['vertex_supported_exclusive_candidate']=r['eligible_geometric_ring'] and not hits and not r['required_anchor_missing_ids']
            if r['ring']['vertex_supported_exclusive_candidate']:clean.append(r['sequence'])
        variant['last_vertex_supported_marker_free_ring']=clean[-1] if clean else None
        variant['last_clean_complete_anchor_enclosing_ring_caveat']='Previous field concerns plane-intersection contour and distal component only; crossed mesh edge endpoints may include known shared. For mesh-vertex eligibility use last_vertex_supported_marker_free_ring.'
    dump(digit.upper()+'_BRANCH_CONTINUITY_AUDIT.json',old)
dump('TOPOLOGICAL_RING_SUMMARY.json',summary)
print(json.dumps(summary,indent=2))
