from pathlib import Path
import json
p=Path(__file__).resolve().parent/'01_coordinate.py'
env={'__file__':str(p),'__name__':'__main__'}
exec(compile(p.read_text(encoding='utf8').split('calls=0;start=')[0],str(p),'exec'),env,env)
np=env['np'];x=np.array(env['pol']['solver']['seed']);motion=env['motion'];apply=env['apply'];V0,p0=apply(*[motion(.8,x)[k] for k in [0,2]])
rows=[]
for j in [0,4,8,20,23,26]:
 h=.003*x[j] if x[j] else np.sqrt(np.finfo(float).eps);tiny=x.copy();tiny[j]+=h;V1,p1=apply(*[motion(.8,tiny)[k] for k in [0,2]]);wide=x.copy();wide[j]+=.02 if j==0 else .03;V2,p2=apply(*[motion(.8,wide)[k] for k in [0,2]])
 rows.append({'parameter':j,'relative_step':h,'relative_max_vertex_displacement_mm':float(np.max(abs(V1-V0))*1000),'absolute_step':float(wide[j]-x[j]),'absolute_max_vertex_displacement_mm':float(np.max(abs(V2-V0))*1000)})
env['dump']('DERIVATIVE_PRECISION_CHECK_R1.json',{'rows':rows,'unsaved_diagnostic_only':True,'candidate_generated':False})
print(json.dumps(rows),flush=True)
