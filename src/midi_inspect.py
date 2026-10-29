"""Strict, offline SMF reader for restoration checks; no playback or inference."""
import pathlib,struct,json,sys
def inspect(path):
    b=pathlib.Path(path).read_bytes()
    if b[:4]!=b'MThd':raise ValueError('Missing SMF header')
    length=struct.unpack('>I',b[4:8])[0]
    if length!=6:raise ValueError('Unsupported header')
    fmt,count,division=struct.unpack('>HHH',b[8:14]); pos=14;notes=0;events=0;tracks=[]
    def vlq(buf,i):
        v=0
        for _ in range(4):
            c=buf[i];i+=1;v=(v<<7)|(c&127)
            if not c&128:return v,i
        raise ValueError('Overlong VLQ')
    for _ in range(count):
        if b[pos:pos+4]!=b'MTrk':raise ValueError('Missing track')
        n=int.from_bytes(b[pos+4:pos+8],'big');t=b[pos+8:pos+8+n];pos+=8+n
        if len(t)!=n:raise ValueError('Truncated track')
        i=0;running=None;tick=0;end=False
        while i<len(t):
            dt,i=vlq(t,i);tick+=dt;status=t[i]
            if status&128:i+=1
            elif running is not None:status=running
            else:raise ValueError('Invalid running status')
            if status==255:
                kind=t[i];i+=1;size,i=vlq(t,i);i+=size
                if kind==47:end=True
                running=None
            elif status in (240,247):size,i=vlq(t,i);i+=size;running=None
            elif 128<=status<240:
                running=status;size=1 if status>>4 in (12,13) else 2
                data=t[i:i+size]
                if len(data)!=size or any(x&128 for x in data):raise ValueError('Invalid channel data')
                if status>>4==9 and data[1]>0:notes+=1
                i+=size
            else:raise ValueError('Invalid SMF status')
            if i>len(t):raise ValueError('Event exceeds track')
            events+=1
        if not end:raise ValueError('Missing end of track')
        tracks.append(tick)
    if pos!=len(b):raise ValueError('Trailing chunks')
    return dict(format=fmt,tracks=count,division=division,note_on=notes,events=events,track_end_ticks=tracks)
if __name__=='__main__':print(json.dumps(inspect(sys.argv[1]),indent=2))
