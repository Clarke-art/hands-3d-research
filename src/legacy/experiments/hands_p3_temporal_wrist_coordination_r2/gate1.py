from support import *
sys.path.insert(0,str(OLD/'_deps'))
import numpy as np, scipy, inspect, traceback
from scipy.optimize import least_squares
from persistence import atomic_record,atomic_json,load_record,save_last
R1=ROOT/'experiments/hands_p3_whole_hand_layout_feasibility_r1'
source=(R1/'solve.py').read_text(encoding='utf8');tree=ast.parse(source)
calls=[n.lineno for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='surface_metrics']
definitions=[n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
assert calls==[106] and 'surface_metrics' not in definitions
previous=(PREV/'evaluate.py').read_text(encoding='utf8')
assert previous.index('def surface_metrics')>previous.index('ref_t=REF')
# Historical executed slice ended at ref_t=REF, excluding that later definition.
functions_from(PREV/'evaluate.py',['rot','surface_metrics'],globals())
assert callable(surface_metrics)
key=dict(press_pivot=[0,0,0],press_axis=[1,0,0],key_top_playable_surface=[dict(xmin=0,xmax=1,ymin=0,ymax=1,z=0)])
_,h,g,_=surface_metrics(np.array([[.5,.5,.001]]),key,0.)
assert h[0]==0 and abs(g[0]-.001)<1e-12
vectors=dict(x=np.array([0.,1.,-2.,3.25]),fun=np.array([.25,-.75,0.]),grad=np.array([1.,2.,3.,4.]),active_mask=np.array([0,1,-1,0],dtype=np.int8),times=np.array([1.,1.125,1.25]),states=np.arange(78,dtype=float).reshape(3,26)/100,source_states=np.arange(78,dtype=float).reshape(3,26)/100,contact_xy=np.arange(16,dtype=float).reshape(8,2),jac_data=np.array([1.,2.]),jac_indices=np.array([0,3],dtype=np.int32),jac_indptr=np.array([0,1,1,2],dtype=np.int32))
meta=dict(record_type='FINAL_OPTIMIZER_RESULT',success=True,status=2,message='deterministic serialization test, NO OPTIMIZER RUN',nfev=7,njev=6,cost=.3125,optimality=4.,elapsed_seconds=.125,residual_calls=13,jac_shape=[3,4],schema_version=1)
finalhash=atomic_record('GATE1_KNOWN_FINAL.npz',vectors,meta)
a,m=load_record('GATE1_KNOWN_FINAL.npz');assert m==meta
assert all(np.array_equal(a[k],v) for k,v in vectors.items())
rejections=[]
try:atomic_record('GATE1_KNOWN_FINAL.npz',dict(x=np.array([99.])),meta)
except FileExistsError:rejections.append('existing_final_overwrite_rejected')
assert sha(O/'GATE1_KNOWN_FINAL.npz')==finalhash
save_last('GATE1_LAST_FINITE.npz',vectors['x'],vectors['fun'],dict(residual_calls=13,elapsed_seconds=.125))
oldhash=sha(O/'GATE1_LAST_FINITE.npz')
try:atomic_record('GATE1_LAST_FINITE.npz',dict(x=np.array([9.]),fun=np.array([8.])),dict(record_type='INTERMEDIATE_RESIDUAL_EVALUATION'),replace=True,fail_before_commit=True)
except RuntimeError:rejections.append('failed_checkpoint_export_preserved_existing_checkpoint')
assert sha(O/'GATE1_LAST_FINITE.npz')==oldhash
try:atomic_json('GATE1_FAILED_DIAGNOSTIC.json',dict(status='injected failure'),fail_before_commit=True)
except RuntimeError:rejections.append('failed_secondary_diagnostic_preserved_final_result')
assert sha(O/'GATE1_KNOWN_FINAL.npz')==finalhash
try:raise ValueError('deterministic solver-exception simulation; no optimizer invoked')
except Exception:
 atomic_record('GATE1_EXCEPTION_STATE.npz',dict(x=vectors['x'],fun=vectors['fun']),dict(record_type='EXCEPTION_LAST_FINITE_STATE',not_final_optimizer_result=True,traceback=traceback.format_exc()))
assert len(rejections)==3
callback='callback' in inspect.signature(least_squares).parameters
atomic_json('RESULT_PERSISTENCE_GATE.json',dict(RESULT_PERSISTENCE_GATE='PASS',scipy_version=scipy.__version__,least_squares_signature=str(inspect.signature(least_squares)),callback_supported=callback,checkpoint_choice='Compatible residual-call finite-state checkpoint every >=5s, separate from immutable final record; no callback required',historical_missing_symbol_call_line=106,historical_import_slice_excluded_function=True,surface_metrics_import_and_known_contact_test_pass=True,known_vector_roundtrip_all_fields=True,complete_metadata_roundtrip=True,atomic_pending_readback=True,failed_export_protection_checks=rejections,simulated_exception_last_finite_saved=True,optimizer_calls_in_gate1=0,R1_terminal_result_restored=False,known_final_sha256=finalhash))
protect();print('RESULT_PERSISTENCE_GATE = PASS; scipy',scipy.__version__,'callback',callback,'NO_OPTIMIZER_CALLS')
