import json,math
from pathlib import Path
O=Path(__file__).resolve().parent

def boundary_contact_sets(sequence,t,hand):
 def active(at):
  return [e for e in sequence if e['hand']==hand and e['required_contact'] and e['display_interval'][0]<=at<e['display_interval'][1]]
 left=active(math.nextafter(t,-math.inf));right=active(t);union={}
 for role,items in [('left',left),('right',right)]:
  for e in items:
   identity=(e['hand'],e['finger'],e['midi']);r=union.setdefault(identity,dict(hand=e['hand'],finger=e['finger'],midi=e['midi'],note_ids=[],sides=[]));r['note_ids'].append(e['note_id']);r['sides'].append(role)
 return dict(time=t,hand=hand,left_notes=[e['note_id'] for e in left],right_notes=[e['note_id'] for e in right],geometric_contacts=list(union.values()),force_constraints='NOT_INFERRED',same_finger_same_key_deduplicated=True,geometric_joint_feasibility='UNTESTED',velocity_compatibility='UNTESTED')
if __name__=='__main__':
 s=json.loads((O/'CONTACT_STATE_SEQUENCE.json').read_text())['all_source_sequence'];I=json.loads((O/'EXPERIMENT_INPUT.json').read_text());tests=[]
 for label,time,hand,count in [('main_event',I['junction_time'],'R',2),('same_finger_repeated_note',2.492855,'R',1),('same_hand_chord_onset',.35,'L',3),('chord_hold_interior',.7,'L',3)]:
  r=boundary_contact_sets(s,time,hand);assert len(r['geometric_contacts'])==count;r['case']=label;r['rule_test_pass']=True;tests.append(r)
 (O/'BOUNDARY_REUSE_TESTS.json').write_text(json.dumps(dict(status='RULE_REUSE_PASS',tests=tests,source='previous verified contact state sequence, unchanged',not_other_motion_verification=True),indent=2));print('BOUNDARY_RULE_REGRESSION',[(r['case'],r['left_notes'],r['right_notes']) for r in tests])
