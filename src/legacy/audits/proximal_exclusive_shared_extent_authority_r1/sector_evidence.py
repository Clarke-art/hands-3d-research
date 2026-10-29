import sys
sys.dont_write_bytecode=True
from common import *
br=read(OUT/'THUMB_BRANCH_CONTINUITY_AUDIT.json');ring=br['true_topological_rings']['rings'][0];rv=ring['vertex_ids'];shared=sorted(set(rv)&WEB)
normals={}
for state,coords in [('NATIVE',N),('RSSF',V)]:
    fn=[]
    for vs in F:
        pp=coords[vs];normal=np.sum(np.cross(pp,np.roll(pp,-1,axis=0)),axis=0);fn.append(unit(normal) if np.linalg.norm(normal)>1e-15 else normal)
    fn=np.array(fn);center=coords[rv].mean(0)
    axis=unit(np.array(ANCHORS['thumb']['native_direction_support']['axis'])) if state=='NATIVE' else unit(CHAINS['thumb'][2]-CHAINS['thumb'][1])
    nailfaces=src('nail_authority')['per_digit_faces']['thumb'];cue=unit(fn[nailfaces].sum(0));u=unit(cue-axis*(cue@axis));w=np.cross(axis,u)
    rows=[]
    for v in rv:
        off=coords[v]-center;normal=unit(fn[V_F[v]].sum(0));theta=float(np.degrees(np.arctan2(off@w,off@u))%360)
        rows.append({'vertex_id':v,'known_shared':v in WEB,'polar_angle_deg':theta,'radius_from_ring_center_mm':float(np.linalg.norm(off-axis*(off@axis))*1000),'local_normal_world':normal.tolist(),'normal_axis_dot':float(normal@axis),'valence':len(ADJ[v]),'incident_face_ids':V_F[v]})
    aa=sorted(r['polar_angle_deg'] for r in rows if r['known_shared']);gaps=np.diff(aa+[aa[0]+360]);span=float(360-max(gaps))
    normals[state]={'center_world_m':center.tolist(),'axis':axis.tolist(),'dorsal_nail_cue_projected':u.tolist(),'ring_rows':rows,'known_shared_minimum_circular_span_deg':span,'angles_are_descriptive_not_sector_boundary':True}
dump('THUMB_LOCAL_SHARED_SECTOR_EVIDENCE.json',{'status':'LOCAL_ANATOMICAL_FRONTIER_UNRESOLVED','ring_edge_ids':ring['edge_ids'],'ring_vertices':rv,'known_shared_ring_vertices':shared,'ring_vertex_count':len(rv),'closed_regular_valence4':all(len(ADJ[v])==4 for v in rv),'states':normals,'finding':'Frozen shared occupies three vertices of the first complete16-vertex circumferential ring; local normals and polar coordinates describe a partial sector, not a tube merge. No normal-angle cutoff is promoted into authority.','required_future_review_granularity':'One thumb MCP/IP shared-sector boundary, preserving all known memberships; not 900 vertex decisions.'})
print({state:r['known_shared_minimum_circular_span_deg'] for state,r in normals.items()})
