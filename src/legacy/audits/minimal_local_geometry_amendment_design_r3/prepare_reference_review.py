import sys
sys.dont_write_bytecode=True
from geometry import *
R2=ROOT/'audits/minimal_local_geometry_amendment_design_r2'
prior=np.array(read(R1/'GEOMETRY_AMENDMENT_CANDIDATES_R1.json')['candidates']['C']['world_mm'])
failed=np.array(read(R2/'REVIEW_COORDINATES_R2.json')['states']['FAILED_SOLVE_S5']['RSSF_RAW'])
refs=read(OUT/'HEALTHY_DORSAL_MCP_REFERENCE_PATCH_AUDIT_R3.json')['reference_candidates']
states={'CURRENT':{'RSSF_RAW':V.tolist()},'R1C_FAILED_REFERENCE':{'RSSF_RAW':prior.tolist()},'R2S5_FAILED_REFERENCE':{'RSSF_RAW':failed.tolist()}}
metadata={}
label_edges={}
for j,z in enumerate(refs):
 label='REFERENCE_'+str(j+1);c=np.array(z['center_world_mm']);bb=np.array(z['surface_frame']);scale=z['alignment_to_dent']['uniform_scale_reference_to_target'];vv=origin+((V-c)@bb)*scale@B.T
 states[label]={'RSSF_RAW':vv.tolist()};metadata[label]={'reference_name':z['name'],'source_center':c.tolist(),'rigid_frame_reference_to_target':bb@B.T,'similarity_scale':scale}
 label_edges[label]=sorted({ei for fi in z['face_ids'] for ei in FE[fi]})
metadata={k:{kk:(vv.tolist() if isinstance(vv,np.ndarray) else vv) for kk,vv in v.items()} for k,v in metadata.items()}
dump('REVIEW_COORDINATES_R3.json',{'states':states,'comparison_edge_ids':R['edges'],'label_edge_ids':label_edges,'failure_edge_id':6675,'references_are_only_similarity_aligned':True,'reference_alignment':metadata,'render_only_labels':['REFERENCE_1','REFERENCE_2']})
