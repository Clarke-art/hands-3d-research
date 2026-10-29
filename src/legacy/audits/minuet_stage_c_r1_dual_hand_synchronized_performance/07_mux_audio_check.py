from common import *
sys.path.insert(0,str(OLD/'_deps'))
import numpy as np
import subprocess,wave
from scipy.signal import correlate,correlation_lags
ff='D:/ffmpeg/bin/ffmpeg.exe'
with wave.open(str(P/'piano_performance.wav'),'rb') as w:
    assert w.getframerate()==48000 and w.getnchannels()==2
    ref=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(float)/32768
out={};hashes=[]
for file in read(P/'VIDEO_VERIFICATION.json'):
    raw=subprocess.check_output([ff,'-v','error','-i',str(P/file),'-map','0:a:0','-f','f32le','-ac','2','-ar','48000','-'])
    hashes.append(hashlib.sha256(raw).hexdigest());decoded=np.frombuffer(raw,dtype='<f4').reshape(-1,2)[:len(ref)].astype(float)
    assert len(decoded)==len(ref)
    a=decoded.mean(axis=1);b=ref.mean(axis=1);corr=correlate(a,b,method='fft');lags=correlation_lags(len(a),len(b));keep=abs(lags)<=480
    bestlag=int(lags[keep][np.argmax(corr[keep])]);rho=float(np.corrcoef(a,b)[0,1])
    assert bestlag==0 and rho>.98,('AUDIO_MUX_CLOCK_OR_CONTENT_MISMATCH',file,bestlag,rho)
    out[file]=dict(decoded_audio_sha256=hashes[-1],best_lag_samples_48k=bestlag,lag_search_window_ms=10,reference_waveform_correlation=rho,decoded_codec_padding_samples=len(raw)//8-len(ref))
assert len(set(hashes))==1
dump('MUX_AUDIO_CLOCK_VERIFICATION.json',dict(pass_=True,three_views_decoded_audio_identical=True,reference_WAV_sha256=sha(P/'piano_performance.wav'),best_lag_samples=0,per_video=out,limitation='Waveform identity/clock check after lossy AAC encoding; not a perceptual realtime listening claim. NOTE_ON/OFF/pitch/velocity23-voice scheduling is verified separately.'))
print('ALL_THREE_AUDIO_TRACKS_IDENTICAL_ZERO_LAG_WAV_CORRELATION_PASS',flush=True)
