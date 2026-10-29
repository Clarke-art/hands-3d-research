"""Event-derived overlapping task envelopes. No pose or pitch-specific rules."""
from dataclasses import dataclass
from copy import deepcopy

def smooth(u):
 u=max(0.,min(1.,u));return u*u*u*(10+u*(-15+6*u))

@dataclass(frozen=True)
class PhasePolicy:
 prepare_sec:float=.18
 release_contact_sec:float=.04
 exit_sec:float=.12
 mechanical_rebound_context_sec:float=.07

class EventPhasePlan:
 def __init__(self,notes,policy=PhasePolicy()):
  self.notes=sorted(deepcopy(notes),key=lambda n:(n['note_on'],n['finger']))
  self.policy=policy
  for n in self.notes:
   if n['hand']!='R' or not 1<=n['finger']<=5 or n['note_off']<=n['note_on']:raise ValueError('Invalid right-hand event')
  for j in range(1,6):
   ns=[n for n in self.notes if n['finger']==j]
   if any(a['note_off']>b['note_on']+1e-9 for a,b in zip(ns,ns[1:])):raise ValueError('Same finger has overlapping active notes')
 def intervals(self):
  p=self.policy;out=[]
  for n in self.notes:
   for role,a,b in [('PREPARING',n['note_on']-p.prepare_sec,n['note_on']),('ACTIVE_CONTACT',n['note_on'],n['note_off']),('RELEASING',n['note_off'],n['note_off']+p.release_contact_sec),('EXITING',n['note_off'],n['note_off']+p.exit_sec)]:
    out.append(dict(finger=n['finger'],note_id=n['note_id'],midi=n['midi_note'],role=role,start=a,end=b))
  return out
 def at(self,t):
  p=self.policy;fingers={j:[] for j in range(1,6)};mechanical=[]
  for n in self.notes:
   on,off=n['note_on'],n['note_off'];base=dict(note_id=n['note_id'],midi=n['midi_note'],key_index=n['key_index'],note=n['note_name'])
   def add(role,w,hard=False,permission=False,meaning=''):
    fingers[n['finger']].append(dict(base,role=role,envelope=w,hard_contact=hard,contact_permission=permission,meaning=meaning))
   # Independent envelopes: no mutually exclusive elif role arbitration.
   if on-p.prepare_sec<=t<on:add('PREPARING',smooth((t-on+p.prepare_sec)/p.prepare_sec),meaning='Approach corridor preference; no hold/contact exemption')
   if on<=t<off:add('ACTIVE_CONTACT',1.,True,True,'Original moving key surface; permit only validated pad region')
   if off<=t<off+p.release_contact_sec:add('RELEASING',1-smooth((t-off)/p.release_contact_sec),meaning='Fading unload preference, never compulsory old-key hold')
   if off<=t<off+p.exit_sec:
    u=(t-off)/p.exit_sec;add('EXITING',16*u*u*(1-u)*(1-u),meaning='One-sided departure/safety relation, not old-key equality or floor over entire finger')
   if off<=t<off+p.mechanical_rebound_context_sec:
    mechanical.append(dict(base,kind='MECHANICAL_REBOUND_CONTEXT',actual_angle_authority='unchanged source key Action',requires_finger_hold=False))
  output=[]
  for j,tasks in fingers.items():
   engagement=max([task['envelope'] for task in tasks]+[0.])
   tasks.append(dict(role='IDLE',envelope=1-engagement,hard_contact=False,contact_permission=False,meaning='Source-style preference conditioned by shared hand context; never fixed neutral target'))
   output.append(dict(finger=j,tasks=tasks,active_keys=[q['midi'] for q in tasks if q['role']=='ACTIVE_CONTACT']))
  edges=[dict(fingers=[j,j+1],constraint='shared surface clearance and passage coordination',task_note_ids=sorted({q['note_id'] for f in output[j-1:j+1] for q in f['tasks'] if 'note_id' in q})) for j in range(1,5)]
  return dict(video_sec=t,music_sec=t-.35,fingers=output,shared_neighbor_tasks=edges,mechanical_context=mechanical)
 def permit(self,t,finger,midi,vertex,pad_vertices):
  # Caller must supply a geometrically verified pad-only region. Empty = deny.
  return vertex in pad_vertices and any(n['finger']==finger and n['midi_note']==midi and n['note_on']<=t<n['note_off'] for n in self.notes)
