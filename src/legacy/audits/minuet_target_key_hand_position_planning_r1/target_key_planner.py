"""Pitch-independent Stage A adapter over frozen FK; no repertoire pose table.

Given explicit fingering, produce key-local contacts and continuous common root.
The reach interval is a conservative planning heuristic, not a feasibility proof.
Bounded FK adaptation and evaluated/visible checks must qualify the result.
"""
from stage_common import *

class TargetKeyPlanner:
    def __init__(self, keys, anchors, hand='R', reach_mm=18):
        if hand not in ('R','L'): raise ValueError('hand must be R or L')
        self.keys={k['midi_note']:k for k in keys};self.hand=hand
        a=anchors['R1' if hand=='R' else 'L1']
        self.neutral=np.array(a['pad_prediction_xyz_m'])
        self.root=np.array(a['root_xyz_m']);self.reach=reach_mm/1000

    def locate(self, midi, finger, root_delta=None):
        if midi not in self.keys or not 1<=finger<=5: raise ValueError('invalid target/finger')
        k=self.keys[midi];delta=np.zeros(3) if root_delta is None else np.array(root_delta)
        ref=self.neutral[finger-1]+delta
        candidates=[]
        for i,s in enumerate(k['key_top_playable_surface']):
            # White front preferred; actual black surface retained at its raised z.
            inset=np.array([.003,.007]) if k['color']=='WHITE' else np.array([.002,.002])
            low=np.array([s['xmin'],s['ymin']])+inset
            high=np.array([s['xmax'],s['ymax']])-inset
            if np.any(high<=low): continue
            xy=np.clip([k['key_center'][0],ref[1]],low,high)
            point=np.r_[xy,s['z']+.0005]
            front_bias=0 if k['color']=='BLACK' or i==0 else .03
            candidates.append((abs(point[1]-ref[1])+front_bias,point,i,low,high))
        if not candidates: raise ValueError('no inset playable region')
        _,point,i,low,high=min(candidates,key=lambda x:x[0])
        return dict(midi_note=midi,key_index=k['key_index'],color=k['color'],
            surface_index=i,unpressed_pad_xyz=point,playable_xy_min=low,
            playable_xy_max=high,press_pivot=k['press_pivot'],
            press_axis=k['press_axis'],press_angle_rad=k['press_angle_rad'])

    def plan(self, events):
        ns=sorted(events,key=lambda n:n['note_on'])
        if not ns: raise ValueError('empty event stream')
        for i,n in enumerate(ns):
            if n['hand']!=self.hand or n['note_off']<=n['note_on']: raise ValueError('invalid hand/time')
            self.locate(n['midi_note'],n['finger'])
            if i and ns[i-1]['note_off']>n['note_on']+1e-9:
                raise ValueError('Stage A is monophonic; chords/held overlaps unsupported')
        # Common lateral stance from intersection of digit-relative reach intervals.
        segments=[];current=[];low=-float('inf');high=float('inf')
        def commit():
            offsets=[self.keys[n['midi_note']]['key_center'][0]-self.neutral[n['finger']-1,0] for n in current]
            delta=np.array([np.clip(np.mean(offsets),low,high),-.005,-.002])
            if any(self.keys[n['midi_note']]['color']=='BLACK' for n in current): delta[1]=.006
            segments.append(dict(first_id=current[0]['note_id'],last_id=current[-1]['note_id'],
                onset=current[0]['note_on'],end=current[-1]['note_off'],
                note_ids=[n['note_id'] for n in current],delta=delta,
                lateral_interval=[low,high]))
        for n in ns:
            offset=self.keys[n['midi_note']]['key_center'][0]-self.neutral[n['finger']-1,0]
            lo,hi=offset-self.reach,offset+self.reach
            if current and max(low,lo)>min(high,hi):
                commit();current=[];low=-float('inf');high=float('inf')
            current.append(n);low=max(low,lo);high=min(high,hi)
        commit()
        transitions=[]
        for a,b in zip(segments,segments[1:]):
            boundary=b['onset'];start=max(a['onset'],boundary-.20);end=boundary+.08
            transitions.append(dict(start=start,end=end,from_delta=a['delta'],to_delta=b['delta'],
                boundary_note=b['first_id'],distance_mm=float(np.linalg.norm(b['delta']-a['delta'])*1000)))
        return dict(hand=self.hand,segments=segments,transitions=transitions,
            reach_interval_mm=self.reach*1000,feasibility='HEURISTIC_REQUIRES_FK_AND_VISIBLE_VALIDATION',
            key_targets={n['note_id']:self.locate(n['midi_note'],n['finger'],
                next(s['delta'] for s in segments if n['note_id'] in s['note_ids'])) for n in ns})

    @staticmethod
    def root_at(plan,t):
        root=np.array(plan['segments'][0]['delta']).copy()
        for tr in plan['transitions']:
            if t<tr['start']: break
            root=np.array(tr['from_delta'])+(np.array(tr['to_delta'])-tr['from_delta'])*c.smooth((t-tr['start'])/(tr['end']-tr['start']))
        return root

    def moving_target(self,target,pressure):
        k=self.keys[target['midi_note']];pivot=np.array(target['press_pivot'])
        R=c.axisrot(pressure*k['press_angle_rad'],k['press_axis'])
        return R@(np.array(target['unpressed_pad_xyz'])-pivot)+pivot
