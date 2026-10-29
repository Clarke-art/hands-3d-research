import sys
sys.dont_write_bytecode=True
from negative_controls import run as original_controls
from semantic_audit import *
from certified_path import strict,area_coeff
from fractions import Fraction as Fr

def run():
 original_controls();data=read(OUT/'GEOMETRIC_GATE_NEGATIVE_CONTROLS_R1.json');pts={i:fq(P[i]) for i in [79,955,3025,3340]};e=sub(pts[955],pts[79]);u=sub(pts[3025],pts[79])
 for name,sign,illegal in [('ACTUAL2182_3330_SAME_SIDE_COPLANAR_LIMIT',1,True),('ACTUAL2182_3330_OPPOSITE_SIDE_LEGAL_FLAT_UNFOLD',-1,False)]:
  cache=dict(pts);cache[3340]=add(pts[79],add(mul(e,Fr(1,3)),mul(u,Fr(sign,3))));rr=intersection(P,[3025,955,79],[79,955,3340],[79,955],[[79,955]],cache);data['controls'].append({'name':name,'expected':'HARD_FAIL' if illegal else 'LEGAL','actual':rr,'passed':rr['illegal']==illegal,'same_actual_native_feature_control_as_reconciliation_R1':True})
 old=read(ROOT/'audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/GEOMETRIC_GATE_NEGATIVE_CONTROLS_R1.json');assert {z['name'] for z in old['controls']}=={z['name'] for z in data['controls']};assert len(data['controls'])==16 and all(z['passed'] for z in data['controls'])
 v0=np.array([[0.,0,0],[1,0,0],[0,1,0],[2,0,0],[3,0,0],[2,1,0]]);v1=v0.copy();v1[3:,0]-=4;pp={i:fq(v0[i]) for i in range(6)};dd={i:sub(fq(v1[i]),pp[i]) for i in range(6)};signs=[strict(area_coeff(pp,dd,z,2)) for z in __import__('itertools').combinations(range(6),3)];assert any(z is None for z in signs)
 data.update({'phase':PHASE,'status':'PASS','NEGATIVE_CONTROLS_PASS':16,'NEGATIVE_CONTROL_TOTAL':16,'source_suite':ref(ROOT/'audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/GEOMETRIC_GATE_NEGATIVE_CONTROLS_R1.json'),'new_continuous_rank3_certificate_rejects_persistent_tunnel':True,'new_certifier_checks_use_exact_predicates_not_samples':True,'gate_reconciliation_historical_validator_modified':False});dump('R4_NEGATIVE_CONTROL_REGRESSION.json',data);print('R4 NEGATIVE CONTROL REGRESSION 16/16 PASS',flush=True)
if __name__=='__main__':run()
