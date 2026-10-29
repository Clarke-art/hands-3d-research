import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from geometry_detector import *
planes=np.array([[1,0,0,.005],[-1,0,0,.005],[0,1,0,.005],[0,-1,0,.005],[0,0,1,.005],[0,0,-1,.005]])
T=np.array([[-.012,-.012,0],[.012,-.012,0],[0,.016,0]])
vertex_depth=np.maximum(-np.max(T@planes[:,:3].T-planes[:,3],axis=1),0).max()*1000;depth,pt=triangle_inside_depth(T,planes);safe,_=triangle_inside_depth(T+[0,0,.02],planes);tangent,_=triangle_inside_depth(T+[0,0,.005],planes)
assert vertex_depth==0 and abs(depth-5)<1e-6 and safe==0 and tangent<1e-6
M=json.loads((O/'COLLISION_METHOD_TESTS.json').read_text());M['triangle_without_inside_vertices_test']=dict(vertex_only_depth_mm=float(vertex_depth),true_triangle_inside_depth_mm=depth,witness_point=pt.tolist(),safe_depth_mm=safe,tangent_depth_mm=tangent,pass_=True);M['key_depth_method']='Vertex depths plus exact maximum depth on intersecting skin triangles through a small linear-polytope enumeration';(O/'COLLISION_METHOD_TESTS.json').write_text(json.dumps(M,indent=2)+'\n',encoding='utf8');print('TRIANGLE_ONLY_PENETRATION_TEST_PASS',vertex_depth,depth)
