import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from sculpt_common import *
receipts=[]
for kind in ['A','B']:
 sc,mesh,rig,left=open_scene(OUT/(kind+'_SCULPT_NOT_APPROVED.blend'));c.settime(sc,2.6);v,tt,ff=coords(mesh);expected=np.load(OUT/(kind+'_ROUND_2_SCULPT.npz'));assert np.array_equal(v,expected['V'])
 native=c.native(mesh,rig);sig=signature(mesh,rig,left);basis=np.array([list(x.co) for x in mesh.data.shape_keys.key_blocks['Basis'].data]);_,w=weights(mesh)
 sc0,m0,r0,l0=open_scene(SOURCE);c.settime(sc0,2.6);base_native=c.native(m0,r0);base_sig=signature(m0,r0,l0)
 assert sig==base_sig and np.array_equal(basis,np.array([list(x.co) for x in m0.data.shape_keys.key_blocks['Basis'].data])) and np.array_equal(w,weights(m0)[1])
 for name,co in base_native['shapes'].items():assert native['shapes'][name]==co
 receipts.append({'region':kind,'final_file':str(OUT/(kind+'_SCULPT_NOT_APPROVED.blend')),'sha256':sha(OUT/(kind+'_SCULPT_NOT_APPROVED.blend')),'reopened_evaluated_error_mm':0.,'Basis_and_original_shape_coords_exact':True,'original_weights_exact':True,'UV_topology_actions_rest_driver_signatures_exact':True,'vertex_count':3300,'native_face_count':3298,'linked_external_libraries':False})
save('FINAL_CANDIDATE_REOPEN_RECEIPT.json',receipts);protection('REOPEN_INPUT_RECEIPT.json')

