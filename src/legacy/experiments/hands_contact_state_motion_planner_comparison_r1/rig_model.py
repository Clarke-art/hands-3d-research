import sys,json,ast
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
from skin_proxy import *
from scipy.interpolate import PchipInterpolator,CubicHermiteSpline
from itertools import combinations
PRE=O.parent/'hands_c01_anatomy_preparation_audit_r1'
B=json.loads((PRE/'B_SOLVE_2.json').read_text());E=json.loads((O/'ENDPOINT_SOLVE_2.json').read_text());Q0=np.array(E['reference_q_R1']);Q1=np.array(E['reference_q_R2']);ACTIVE=np.array(E['active_flex_anchor'])
TR=RAW['triangles'];LABEL=np.array(META['triangle_labels']);D=RAW;rot=c.axisrot
src=(O/'geometry_detector.py').read_text(encoding='utf-8-sig');tree=ast.parse(src)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['clip','area','keylocal','keyworld','contact_metric','triangle_inside_depth']],type_ignores=[]),'geometry','exec'))
tree=ast.parse((O.parent/'hands_skin_collision_static_feasibility_r1/solve_static_skin.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='prepkey'],type_ignores=[]),'key_planes','exec'))
DATA=np.load(O/'MOTION_COLLOCATION_KEYS.npz');K=DATA['knots'];TC=DATA['times'];KA=DATA['key_angles'];START=K[0];EXCHANGE=2.921426;FULL=2.956426;END=K[-1]
ZS=np.r_[B['state'][:10],B['lambda_reference'],0.];ZE=np.r_[E['state'][:10],E['lambda_reference'],E['active_flex_alpha']]
LOW=np.r_[[-150,-30,-12.217247311392744],[-8,-8,-12],[0,0,0,-35],0,0];HIGH=np.r_[[60,35,12],[8,8,12],[25,25,18,35],1,1]
def state(z):
 st=np.zeros(26);st[:10]=z[:10];st[10:]=((1-z[10])*Q0[1:]+z[10]*Q1[1:]).ravel();st[14:17]=(1-z[11])*st[14:17]+z[11]*ACTIVE
 return st
def curve(Y):
 p=PchipInterpolator(K,Y,axis=0);der=p.derivative()(K);der[0]=0;der[-1]=0
 return CubicHermiteSpline(K,Y,der,axis=0)
def unroot(V,st):return (V-BASE-np.array(st[:3])/1000)@rr(st[3:6])+BASE
