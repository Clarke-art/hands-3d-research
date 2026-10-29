import sys,ast
sys.dont_write_bytecode=True
from common import *
import numpy as np,math
G=read(OUT/'REVIEW_GEOMETRY.json');P=read(OUT/'TEMP_DONOR_TRANSFER_DESIGN_ONLY.json');R=read(OLD/'DORSAL_MCP_DENT_ROI_R1.json');C=read(OUT/'DONOR_TO_CURRENT_TOPOLOGY_CORRESPONDENCE_R1.json');T=read(OUT/'HISTORICAL_OPERATION_RAM_REPLAY.json');S=read(OUT/'RAW_SOURCE_GEOMETRY.json')['stages']
origin=np.array(G['frame']['origin_world_mm']);x=np.array(G['frame']['x']);y=np.array(G['frame']['y']);n=np.array(G['frame']['outward'])
tree=ast.parse((OUT/'analyze.py').read_text());nodes=[z for z in tree.body if isinstance(z,ast.FunctionDef) and z.name=='sections'];exec(compile(ast.Module(body=nodes,type_ignores=[]),'sections','exec'))
current=G['stages']['STAGE4C_R2'];v=np.array(P['world_mm']);fs=R['faces'];F=P['faces']
G['stages']['TRANSFER_PROBE']={**current,'world_mm':v.tolist(),'sections':sections(v,F,fs)}
rot=np.array(C['rigid_display_registration']['rotation_row']);trans=np.array(C['rigid_display_registration']['translation_mm']);loc=np.array(S['OFFICIAL_BASE']['matrix_world'])[:3,3]
for i,snap in enumerate(T['snapshots'][:2]):
 w=(np.array(snap['local_m'])+loc)*1000@rot+trans
 mapped={int(k) for i in R['vertices'] for k in T['final_ancestry'][i]};rid=[i for i,a in enumerate(snap['ancestry']) if set(map(int,a))&mapped];ff=[fi for fi,p in enumerate(snap['faces']) if set(p)&set(rid)]
 G['stages']['TRACE_'+str(i)]={'world_mm':w.tolist(),'faces':snap['faces'],'smooth':[False]*len(snap['faces']),'roi_vertices':rid,'roi_faces':ff,'sections':sections(w,snap['faces'],ff),'operation':snap['name']}
dump('REVIEW_GEOMETRY.json',G)
def normal(v,p):
 q=v[p];a=sum((np.cross(q[k]-q[0],q[(k+1)%len(q)]-q[0]) for k in range(len(q))),np.zeros(3));return a/max(np.linalg.norm(a),1e-15)
edgefaces={}
for fi,p in enumerate(F):
 for a,b in zip(p,p[1:]+p[:1]):edgefaces.setdefault(tuple(sorted([a,b])),[]).append(fi)
base=np.array(current['world_mm']);moved=set(P['moved_vertex_ids']);rows=[]
for e,ff in edgefaces.items():
 if len(ff)!=2 or not any(moved&set(F[fi]) for fi in ff):continue
 def angle(w):return float(np.degrees(np.arccos(np.clip(normal(w,F[ff[0]])@normal(w,F[ff[1]]),-1,1))))
 aa=angle(base);bb=angle(v);rows.append({'edge_vertices':list(e),'faces':ff,'before_deg':aa,'probe_deg':bb,'boundary':bool(set(e)-moved)})
dump('PROBE_VISUAL_GEOMETRY_DIAGNOSTICS.json',{'all_changed_patch_edge_progression':rows,'mapped_ROI_max_dihedral_before_deg':max(r['before_deg'] for r in rows if set(r['faces'])&set(fs)),'mapped_ROI_max_dihedral_probe_deg':max(r['probe_deg'] for r in rows if set(r['faces'])&set(fs)),'new_obtuse_boundary_edges':[r for r in rows if r['boundary'] and r['before_deg']<90<=r['probe_deg']],'all_unmoved_coordinates_exact':all(np.array_equal(base[i],v[i]) for i in range(len(v)) if i not in moved),'max_displacement_mm':float(np.max(np.linalg.norm(v-base,axis=1))),'sections':sections(v,F,fs),'Human_approval':'PENDING','anatomy_threshold':None})
