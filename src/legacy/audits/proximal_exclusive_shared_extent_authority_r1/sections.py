"""Plane/mesh intersection and superlevel topology sweeps, no distance fields."""
import sys,math
sys.dont_write_bytecode=True
from common import *

def contour(coords,axis,origin,height,heights,comp):
    crossing=[ei for ei,(a,b) in enumerate(E) if (heights[a]>height)!=(heights[b]>height) and (a if heights[a]>height else b) in comp]
    xset=set(crossing);points={};cadj={e:set() for e in crossing};badfaces=[];ff=set()
    for ei in crossing:
        a,b=E[ei];t=(height-heights[a])/(heights[b]-heights[a]);points[ei]=coords[a]+t*(coords[b]-coords[a])
        ff.update(E_F[ei])
    for fi in sorted(ff):
        vs=F[fi];es=[EF[tuple(sorted((a,b)))] for a,b in zip(vs,vs[1:]+vs[:1])];xs=[e for e in es if e in xset]
        if len(xs)==2:cadj[xs[0]].add(xs[1]);cadj[xs[1]].add(xs[0])
        elif xs:badfaces.append({'face_id':fi,'crossing_edges':xs})
    cc=components(cadj,cadj) if cadj else []
    ref=np.eye(3)[int(np.argmin(np.abs(axis)))];uu=unit(np.cross(axis,ref));vv=np.cross(axis,uu)
    loops=[]
    for c in cc:
        closed=all(len(cadj[e])==2 for e in c);order=[];winding=None
        if closed:
            now=min(c);prev=None
            for _ in range(len(c)):
                order.append(now);nxt=sorted(cadj[now]-({prev} if prev is not None else set()))[0];prev,now=now,nxt
            xy=np.array([[np.dot(points[e]-origin,uu),np.dot(points[e]-origin,vv)] for e in order]);ang=np.arctan2(xy[:,1],xy[:,0]);delta=(np.roll(ang,-1)-ang+np.pi)%(2*np.pi)-np.pi;winding=float(np.sum(delta)/(2*np.pi))
        radial=[float(np.linalg.norm(p-(origin+height/1000*axis))*1000) for e,p in points.items() if e in c]
        loops.append({'crossed_edge_ids':sorted(c),'ordered_crossed_edge_ids':order,'closed_degree2':closed,'axis_winding':winding,'min_radius_mm':min(radial) if radial else None,'max_radius_mm':max(radial) if radial else None})
    return {'crossed_edge_ids':crossing,'ring_vertex_ids':sorted({v for e in crossing for v in E[e]}),'crossed_face_ids':sorted(ff),'loop_count':len(cc),'loops':loops,'ambiguous_or_open_faces':badfaces,'circumferential_complete':len(loops)==1 and loops[0]['closed_degree2'] and abs(abs(loops[0]['axis_winding'])-1)<1e-8 and not badfaces,'intersection_world_m':{str(e):p.tolist() for e,p in points.items()}}

def sweep(digit,variant,coords,axis,origin):
    heights=(coords-origin)@axis*1000;seed=TIPS[digit]
    required=(CAP|NAILS['thumb']|{seed}) if digit=='thumb' else (INDEX_SOURCES|{seed})
    other={v for d,s in NAILS.items() if d!=digit for v in s}|{v for d,v in TIPS.items() if d!=digit}
    if digit=='index':other|=CAP
    forbidden=WEB|other
    levels=sorted(set(float(x) for x in heights if x<heights[seed]),reverse=True)
    current=float(heights[seed]);records=[];last_ok=None;first_bad=None;first_collision=None
    for j,z in enumerate(levels):
        h=(current+z)/2;current=z
        comp=component(seed,{i for i in range(NV) if heights[i]>h})
        if not comp:continue
        ct=contour(coords,axis,origin,h,heights,comp)
        marks=comp&forbidden;webhit=comp&WEB
        r={'sequence':j,'axial_station_mm':h,'vertex_event_interval_mm':[z,2*h-z],'distal_component':packed(comp),'fully_distal_face_ids':[fi for fi,vs in enumerate(F) if set(vs)<=comp],'required_anchor_missing_ids':sorted(required-comp),'web_in_component':sorted(webhit),'other_anchor_conflicts':sorted(comp&other),'ring':ct,'eligible_geometric_ring':ct['circumferential_complete'] and not marks,'anatomical_exclusivity_certified':False}
        records.append(r)
        if ct['circumferential_complete'] and not marks and required<=comp:last_ok=r
        if required<=comp and not r['eligible_geometric_ring'] and first_bad is None:first_bad=r
        if marks:
            first_collision=r
            break
    # A clean ring is necessary evidence only. One side may be shared before frozen markers.
    return {'digit':digit,'variant':variant,'coordinate_state':'NATIVE' if coords is N else 'RSSF','axis_world':axis.tolist(),'origin_world_m':origin.tolist(),'station_unit':'mm along axis from origin','required_anchor_ids':sorted(required),'forbidden_anchor_ids':sorted(forbidden),'station_selection':'Midpoints of every successive distinct vertex projection level, from independent digit tip toward proximal; no selected ring depth/metric step','ring_method':'Original polygon intersections; crossed mesh edge IDs as nodes, each intersected face connects its two crossed edges. Degree2 single loop with axis winding ±1 is circumferentially complete. Four-crossing polygons flagged, not silently triangulated.','last_clean_complete_anchor_enclosing_ring':last_ok['sequence'] if last_ok else None,'first_incomplete_or_conflicting_anchor_enclosing_ring':first_bad['sequence'] if first_bad else None,'first_forbidden_marker_merge':first_collision['sequence'] if first_collision else None,'ring_sequence':records,'canonical_extent_selected':False,'caveat':'Topology isolates a distal branch but cannot infer shared skin starts exactly at first frozen web marker. Plane orientation and continuous within-edge boundary remain design choices. Native axis uses engineering landmark evidence, not native winner labels.'}

if __name__=='__main__':
    all_results={};brief={}
    for digit in ['thumb','index']:
        geo=ANCHORS[digit]['native_direction_support'];origin=np.array(geo['axis_anchor_world_m']);axis=unit(np.array(geo['axis']))
        mcp=np.array(geo['joint_world_m']['MCP']);axis2=unit(N[TIPS[digit]]-mcp)
        variants={'NATIVE_ENGINEERING_AXIS':(N,axis,origin),'NATIVE_MCP_TIP_AXIS':(N,axis2,mcp)}
        if digit=='thumb':p=CHAINS[digit][1];q=CHAINS[digit][-1]
        else:p=CHAINS[digit][0];q=CHAINS[digit][-1]
        variants['RSSF_LIVE_MCP_TIP_AXIS']=(V,unit(q-p),p)
        all_results[digit]={}
        for variant,(coords,ax,ori) in variants.items():
            result=sweep(digit,variant,coords,ax,ori);all_results[digit][variant]=result
            lc=result['last_clean_complete_anchor_enclosing_ring'];fm=result['first_forbidden_marker_merge'];rs=result['ring_sequence']
            def short(k):
                if k is None:return None
                r=next(x for x in rs if x['sequence']==k)
                return {'sequence':k,'station_mm':r['axial_station_mm'],'distal_count':r['distal_component']['count'],'ring_vertices':len(r['ring']['ring_vertex_ids']),'complete':r['ring']['circumferential_complete'],'web_hit':r['web_in_component'],'other_anchor_conflicts':r['other_anchor_conflicts'],'required_missing':r['required_anchor_missing_ids']}
            brief[digit+'_'+variant]={'slices':len(rs),'last_clean':short(lc),'first_marker_merge':short(fm)}
        dump(digit.upper()+'_BRANCH_CONTINUITY_AUDIT.json',{'status':'ANALYZED_AUTHORITY_UNRESOLVED','variants':all_results[digit],'native_partition_labels_used_for_selection':False,'historical_R2_R3_labels_loaded':False})
    dump('PROXIMAL_CROSS_SECTION_TRANSITION_AUDIT.json',{'status':'ANALYZED_AUTHORITY_UNRESOLVED','summary':brief,'details':['THUMB_BRANCH_CONTINUITY_AUDIT.json','INDEX_BRANCH_CONTINUITY_AUDIT.json'],'cross_sections_executed':True,'full_geodesic_fields_computed':False,'surface_topology_only':True})
    print(json.dumps(brief,indent=2))
