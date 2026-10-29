import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import numpy as np
from depth_math import selftest,planes_from_mesh

def run():
    read(ROOT/'AGENTS.md') if False else path(ROOT/'AGENTS.md').read_text(encoding='utf-8-sig')
    path(R2/'FINAL_VERIFICATION_REPORT.md').read_text(encoding='utf8')
    I=read(SRC/'INPUT_BINDINGS.json');man=I['scene'];path(man['path'])
    state=read(R2/'BLENDER_STATE_RECONSTRUCTION.json');assert state['pass_'] and state['native_sha256']==I['native_sha256']
    S,sm=archive(SRC/'SOURCE_LOCAL_STATES.npz');C,cm=archive(R2/'ACTUAL_BLENDER_STATIC_SKIN.npz')
    assert np.array_equal(C['times'],TIMES) and np.array_equal(S['times'],TIMES)
    assert C['baseline_vertices'].shape==C['corrected_vertices'].shape==(3,3300,3)
    off=C['face_offsets'];flat=C['face_vertices'];assert off[0]==0 and off[-1]==len(flat) and np.all(np.diff(off)>=3) and np.all((flat>=0)&(flat<3300)) and len(off)==3299
    F=[flat[off[i]:off[i+1]].tolist() for i in range(len(off)-1)]
    M=read(MODEL/'SOURCE_MODEL_MANIFEST.json');assert F==M['faces'] and M['source_sha256']==man['sha256'] and cm['source_sha256']==man['sha256']
    expected,em=archive(R2/'EXPECTED_RECONSTRUCTION.npz');errors=[]
    for ix,t in enumerate(TIMES):
        R,meta=archive(SRC/('SOURCE_LOCAL_RESULT_'+str(ix)+'.npz'))
        assert meta['time']==t and R['q'].shape==(5,4) and R['world'].shape==(4,4) and R['key_angles'].shape==(88,) and R['x'].shape==(6,)
        assert np.array_equal(R['x'][:4],R['q'][4])
        assert all(np.array_equal(R[k],S[k][ix]) for k in ['q','world','key_angles'])
        err=float(np.linalg.norm(C['corrected_vertices'][ix]-expected['vertices'][ix],axis=1).max()*1000);assert err<.01;errors.append(err)
        assert state['rows'][ix]['other_bone_basis_error']==0 and state['rows'][ix]['world_matrix_error_mm']==0 and state['rows'][ix]['key_angles_exact']
    K=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys'];W=read(R2/'GEOMETRY_WITNESS_0.json');read(R2/'GEOMETRY_POSE_0.json');read(R2/'E5_SURFACE_INTERIOR_WITNESS.json')
    angle=S['key_angles'][0,55];pv=np.array(K[55]['press_pivot']);axis=np.array(K[55]['press_axis']);axis/=np.linalg.norm(axis);x,y,z=axis;cross=np.array([[0,-z,y],[z,0,-x],[-y,x,0]]);rot=np.eye(3)+np.sin(angle)*cross+(1-np.cos(angle))*cross@cross
    parity=[]
    for g in W['E5_actual_geometry']:
        actual=np.array(g['world_vertices_m']);registered=next(c for c in K[55]['geometry'] if c['name']==g['component'])
        compare=(np.array(registered['vertices'])-pv)@rot.T+pv;err=float(abs(actual-compare).max()*1000);assert err<.001;parity.append(err)
        T=[(f[0],f[j],f[j+1]) for f in g['faces'] for j in range(1,len(f)-1)];planes_from_mesh(actual,T)
    tests=selftest()
    # Validate all script syntax before Blender, without importing bpy into offline Python.
    for p in O.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    prior=read(R2/'FINAL_PROTECTION_READBACK.json')['input_sha256_after']
    assert all(sha(p)==prior[str(p)] for p in [Path(man['path']),SRC/'SOURCE_LOCAL_RESULT_0.npz',SRC/'SOURCE_LOCAL_RESULT_1.npz',SRC/'SOURCE_LOCAL_RESULT_2.npz'])
    read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/DIGIT_SKIN_ROI.json');archive(MODEL/'SOURCE_MODEL.npz');read(SRC/'POLICY.json');read(OLD/'FINGERTIP_CONTACT_MARKERS_R1.json')
    snapshot('INPUT_SHA_BEFORE.json')
    dump('TOOLCHAIN_PREFLIGHT.json',dict(pass_=True,numpy=np.__version__,modules=['common','depth_math','numpy','stdlib'],imports_absolute_script_directory=True,times=TIMES,
        cache_skin_errors_mm=errors,vertex_count=3300,face_count=len(F),units='world meters; output mm',cached_E5_registered_geometry_errors_mm=parity,known_geometry_tests=tests,
        missing_cache_data=['Actual evaluated all-88-key geometry for all three Action times','Actual Blender tessellation of cached baseline/corrected polygons','BVH sets for final two times and left-hand geometry'],
        permitted_blender_supplement='Read original scene/key Action only; tessellate cached skin coordinates in temporary in-memory mesh; never apply saved correction or save scene',optimizer_calls=0))
    print('PREFLIGHT_PASS',errors,flush=True)

if __name__=='__main__':
    try:run()
    except BaseException:
        import traceback
        dump('PREFLIGHT_FAILURE.json',dict(error=traceback.format_exc()))
        raise
