from stage_common import *
assert not (P/'CANDIDATE_ATTEMPT.json').exists()
text=(A2/'coordinated_motion.py').read_text(encoding='utf8')
text=text.replace('from scipy.optimize import least_squares\nfrom scipy.interpolate import PchipInterpolator\nfrom scipy.sparse import lil_matrix',"if 'bpy' not in sys.modules:\n    from scipy.optimize import least_squares\n    from scipy.interpolate import PchipInterpolator\n    from scipy.sparse import lil_matrix")
text=text.replace("NEUTRAL=np.degrees(o.qanchor('R1'));BASE,RBASE=o.root('R')", "HAND='L'\nNEUTRAL=np.degrees((o.qanchor('L1')+o.qanchor('L2'))/2);BASE,RBASE=o.root(HAND)\nNEUTRAL_PADS=np.array([c.fk(HAND,d,np.radians(NEUTRAL[j]))[0]@RBASE.T+BASE for j,d in enumerate(c.DIGITS)])")
text=text.replace("c.SETUPS['R',d]","c.SETUPS[HAND,d]")
text=text.replace("o.ANCHORS['R1']['pad_prediction_xyz_m'][n['finger']-1][1]","NEUTRAL_PADS[n['finger']-1,1]")
text=text.replace("o.ANCHORS['R1']['pad_prediction_xyz_m'][n['finger']-1][0]","NEUTRAL_PADS[n['finger']-1,0]")
text=text.replace("o.ANCHORS['R1']['pad_prediction_xyz_m'][j][0]","NEUTRAL_PADS[j,0]")
needle="self.keys={k['midi_note']:k for k in c.KEYS};self.repeats={}"
extra="""self.keys={k['midi_note']:k for k in c.KEYS};self.repeats={}
        if not self.events:raise ValueError('empty chord/event set')
        for n in self.events:
            if n['hand']!=HAND or not 1<=n['finger']<=5 or n['midi_note'] not in self.keys or n['note_off']<=n['note_on']:
                raise ValueError('invalid left-hand target, finger, or event')
        for i,a in enumerate(self.events):
            for b in self.events[i+1:]:
                if a['finger']==b['finger'] and max(a['note_on'],b['note_on'])<min(a['note_off'],b['note_off']):
                    raise ValueError('overlapping targets assigned to the same finger')
        self.onset_groups={t:[n['note_id'] for n in self.events if n['note_on']==t] for t in sorted(set(n['note_on'] for n in self.events))}
        self.bounds=B.copy()
        used={n['finger'] for n in self.events}
        for finger,label in [(2,'LEFT_IDLE_INDEX'),(4,'LEFT_IDLE_RING')]:
            if finger not in used:self.bounds[finger-1]=np.array(o.SP['joint_increment_bounds_deg'][label])"""
assert needle in text;text=text.replace(needle,extra)
old="""self.state_low=np.r_[[min(offsets)*1000-45,-30,-16],[-8,-8,-12],B[:,0].ravel()]
        self.state_high=np.r_[[max(offsets)*1000+45,35,12],[8,8,12],B[:,1].ravel()]
        self.nominal=np.r_[[np.median(offsets)*1000,0,-6],[0,0,0],NEUTRAL.ravel()]"""
new="""yoffsets=[self.xy_seed[i,1]/1000-NEUTRAL_PADS[n['finger']-1,1] for i,n in enumerate(self.events)]
        self.state_low=np.r_[[min(offsets)*1000-45,min(yoffsets)*1000-25,-16],[-8,-8,-12],self.bounds[:,0].ravel()]
        self.state_high=np.r_[[max(offsets)*1000+45,max(yoffsets)*1000+25,12],[8,8,12],self.bounds[:,1].ravel()]
        self.nominal=np.r_[[np.median(offsets)*1000,np.mean(yoffsets)*1000,-6],[0,0,0],NEUTRAL.ravel()]"""
assert old in text;text=text.replace(old,new)
old="""lo=self.boxlo;hi=self.boxhi;d=np.abs(pads[j]-(lo+hi)/2)-(hi-lo)/2
            sdf=np.linalg.norm(np.maximum(d,0),axis=1)+np.minimum(np.max(d,axis=1),0)
            margin=np.array([-.004 if k in activekeys else .003 for k in self.boxkeys])"""
new="""lo=self.boxlo;hi=self.boxhi;angles=self.key_angles(t);vv=[]
            for midi in self.boxkeys:
                pivot=np.array(self.keys[midi]['press_pivot']);inv=c.axisrot(-angles[midi-21],[1,0,0]);vv.append(inv@(pads[j]-pivot)+pivot)
            vv=np.array(vv);d=np.abs(vv-(lo+hi)/2)-(hi-lo)/2
            sdf=np.linalg.norm(np.maximum(d,0),axis=1)+np.minimum(np.max(d,axis=1),0)
            margin=np.array([0 if k in activekeys else .003 for k in self.boxkeys])"""
assert old in text;text=text.replace(old,new)
needle="""elif future:
                i,n=future[0]"""
replacement="""elif any(n['note_off']+self.policy['finger_release_follow_sec']<=t<n['note_off']+self.policy['recovery_sec'] for i,n in ns):
                i,n=next((i,n) for i,n in reversed(ns) if n['note_off']+self.policy['finger_release_follow_sec']<=t<n['note_off']+self.policy['recovery_sec'])
                u=float(c.smooth((t-n['note_off']-self.policy['finger_release_follow_sec'])/(self.policy['recovery_sec']-self.policy['finger_release_follow_sec'])))
                tasks.append((j,i,.002+.008*u,2*(1-u)))
            elif future:
                i,n=future[0]"""
assert needle in text;text=text.replace(needle,replacement)
# Unlike the R2 adjacent-pair initializer, this static solve includes ALL active
# chord fingers and real key-local XY unknowns in one common-root problem.
text=text.replace("fit=least_squares(lambda x:self.pose_residual(x,self.xy_seed,t,tasks),np.clip(seed,self.state_low+1e-7,self.state_high-1e-7),\n            bounds=(self.state_low,self.state_high),max_nfev=80,ftol=1e-6,xtol=1e-6,gtol=1e-6)",
    "N=len(self.events);initial=np.r_[seed,self.xy_seed.ravel()];lower=np.r_[self.state_low,self.xy_low.ravel()];upper=np.r_[self.state_high,self.xy_high.ravel()]\n        def res(x):return np.r_[self.pose_residual(x[:26],x[26:].reshape(N,2),t,tasks),(x[26:]-self.xy_seed.ravel())*.12]\n        fit=least_squares(res,np.clip(initial,lower+1e-7,upper-1e-7),bounds=(lower,upper),max_nfev=100,ftol=1e-6,xtol=1e-6,gtol=1e-6)")
text=text.replace('finger_release_follow_sec=.04','finger_release_follow_sec=.07,recovery_sec=.32')
text=text.replace("motion_method='Banded joint wrist/digit/contact solve over adjacent event windows, then C1 shape-preserving bake'", "motion_method='Stage A R2 banded wrist/digit/contact framework adapted to actual left FK and concurrent chord tasks; common C1 bake'")
text=text.replace("no_per_pitch_special_rules=True)","no_per_pitch_special_rules=True,chord_events_same_finger_conflicts_rejected=True,endpoint_prepared_return_weight=.20)")
(P/'left_chord_motion.py').write_text(text,encoding='utf8')
dump('STAGE_A_CODE_REUSE_BIND.json',dict(source_module=str(A2/'coordinated_motion.py'),source_sha256=sha(A2/'coordinated_motion.py'),
    adapted_module_sha256=sha(P/'left_chord_motion.py'),source_unmodified=True,
    reused=['vector FK composition','shared wrist+all digit state','moving key target','time phases','joint least squares','temporal framework'],
    adaptations=['actual L rest matrices/axes/markers/root','natural L1/L2 joint reference','joint multi-contact static solve','same-finger conflict validation','idle left index/ring domain','release recovery window'],
    right_trajectory_mirrored=False,chord_specific_pitch_conditions=False))
print('LEFT_CHORD_KERNEL_PREPARED_FROM_UNMODIFIED_A2')
