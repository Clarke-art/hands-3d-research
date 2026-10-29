"""Offline interface smoke test using unchanged upstream PianoPlayer core."""
import pathlib,sys,json,argparse
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'third_party/pianoplayer_core'))
from pianoplayer.hand import Hand
from pianoplayer.models import INote,keypos
def run(path):
    data=json.loads(pathlib.Path(path).read_text('utf-8'));notes=[]
    for i,n in enumerate(data['notes']):
        a=INote(name=n['name'],pitch=n['midi'],octave=n['octave'],time=n['time'],duration=n['duration'],noteID=i,measure=1,isBlack=False,isChord=False,NinChord=1,fingering=0)
        a.x=keypos(a);notes.append(a)
    original=[(n.pitch,n.time,n.duration) for n in notes]
    hand=Hand(notes,side='right',size='M');hand.verbose=False;hand.generate(start_measure=1,nmeasures=1)
    assert original==[(n.pitch,n.time,n.duration) for n in notes]
    assert all(type(n.fingering)==int and 1<=n.fingering<=5 for n in notes)
    return dict(status='INTERFACE_SMOKE_ONLY_NOT_TEACHER_VALIDATED',fingerings=[n.fingering for n in notes],preserved_notes=len(notes))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('input',type=pathlib.Path);args=a.parse_args();print(json.dumps(run(args.input)))
