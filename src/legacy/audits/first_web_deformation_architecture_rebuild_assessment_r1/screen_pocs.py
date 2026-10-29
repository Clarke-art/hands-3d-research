import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
def checks(o,V,V0):
    F=[list(p.vertices) for p in o.data.polygons];E=np.array([list(e.vertices) for e in o.data.edges])
    tri=np.array([[f[0],f[j],f[j+1]] for f in F for j in range(1,len(f)-1)]);own=np.array([i for i,f in enumerate(F) for j in range(1,len(f)-1)])
    def areas(v):return np.bincount(own,weights=np.linalg.norm(np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]]),axis=1)*.5,minlength=len(F))
    A,A0=areas(V),areas(V0)
    return {'NaN_Inf':int((~np.isfinite(V)).sum()),'collapsed_faces':int(((A<=1e-12)|(A/A0<=1e-6)).sum()),'degenerate_edges':int((np.linalg.norm(V[E[:,0]]-V[E[:,1]],axis=1)<=1e-12).sum())}
assets={'BASELINE':BASE,'A':OUT/'ROUTE_A_LOCAL_RETOPOLOGY_POC_R1.blend','B':OUT/'ROUTE_B_HELPER_BONE_POC_R1.blend','C':OUT/'ROUTE_C_LOCAL_CAGE_POC_R1.blend'}
cam=cameras();regcam=m.cameras();zero_cams={k:regcam[k] for k in ['PALMAR_FULL','THENAR_CLOSE','DORSAL_FULL']};zero_cams['FIRST_WEB_CLOSE']=copy.deepcopy(zero_cams['THENAR_CLOSE']);zero_cams['FIRST_WEB_CLOSE']['ortho_scale_m']=.07
dump('SCREEN_MATCHED_CAMERAS_R1.json',{'ZERO':zero_cams,'motion':{str(f):cam[str(f)] for f in FRAMES},'same_all_routes':True})
source_pose={};rows={};zero_base=None
for label,path in assets.items():
    ob,rig=fresh() if label=='BASELINE' else load(path)
    neutral(rig);V0=coords(ob);shape=core.shape_payload(ob);actionhash=digest(action_payload(bpy.data.actions[ACTION]));assert actionhash==read(ROOT/'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['actions_before'][ACTION]
    if label=='BASELINE':zero_base=V0
    rows[label]=[]
    for case in ['ZERO']+FRAMES:
        if case=='ZERO':neutral(rig);cams=zero_cams;name='ZERO'
        else:motion(rig,case);cams=cam[str(case)];name=f'F{case:03}'
        pose={n:np.array(rig.pose.bones[n].matrix).tolist() for n in read(OUT/'TOPOLOGY_INPUT_R1.json')['native']['rest']}
        if label=='BASELINE':source_pose[str(case)]=pose
        else:assert pose==source_pose[str(case)],(label,case,'ORIGINAL_JOINT_POSE_CHANGED')
        V,faces=m.evaluate(ob,ob.matrix_world);VA=np.array([list(v) for v in V]);check=checks(ob,VA,V0)
        rr=m.Renderer(cams,label.lower()+'_selected');rr.sc.display.shading.shadow_intensity=0
        rr.draw(label,name,V,faces,list(cams));rr.dispose()
        rec={'case':case,'source_frame':690+2*(case-1) if isinstance(case,int) else None,'minimum':check,'approved_corrective_natural_values':values(ob),'renders':rr.records,'original_21_joint_pose_exact':True}
        neutral(rig);restore=float(np.linalg.norm(coords(ob)-V0,axis=1).max()*1000);rec['ZERO_restore_max_mm']=restore;rec['ZERO_restore']='PASS' if restore<.001 else 'FAIL';assert restore<.001
        rows[label].append(rec)
    if label!='BASELINE':
        rows[label][0]['ZERO_existing_vertices_vs_baseline_max_mm']=float(np.linalg.norm(V0[:len(zero_base)]-zero_base,axis=1).max()*1000)
    assert core.shape_payload(ob)==shape and digest(action_payload(bpy.data.actions[ACTION]))==actionhash
    print('POC_KEY_SCREEN_READY',label,flush=True)
dump('KEY_SCREEN_MACHINE_R1.json',{'inputs_unchanged':inputs(),'conditions':rows,'full_motion_ran':False,'next_gate':'Ordinary visible keyframe decision before any full motion/regression','forbidden_forensics_ran':False})
