# Final master: render's music+SFX stem + cleanly processed voice, no clipping.
import numpy as np, subprocess, json, sys, soundfile as sf
S='/tmp/claude-0/-home-user-Video-Prop/b344c461-90fd-5890-89a8-7efa79372a5a/scratchpad/'
GAP=float(sys.argv[1]) if len(sys.argv)>1 else 20.0
def dec(f,ch=2):
    raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-vn','-ac',str(ch),'-ar','48000','-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,dtype=np.float32).reshape(-1,ch).copy()
sr=48000
stem=dec(S+(sys.argv[2] if len(sys.argv)>2 else 'stem2.mp4')); v=dec(S+'voice_proc.wav',1)[:,0]
n=min(len(stem),len(v)); stem=stem[:n]; v=v[:n]
rms=lambda x:20*np.log10(np.sqrt((x**2).mean())+1e-12)
tl=json.load(open(S+'timeline.json'))
speech=np.zeros(n,bool)
for x in tl: speech[int(x['start']*sr):int((x['start']+x['dur'])*sr)]=True
# bed level measured where the voice plays, voice level measured on its active frames
vl=rms(v[speech]); bl=rms(stem[speech].mean(1))
g=10**((bl+GAP-vl)/20)
mix=stem+(v*g)[:,None]
print(f'voice {vl:.1f} dB, bed {bl:.1f} dB, voice gain {20*np.log10(g):+.1f} dB -> gap {GAP} dB')
# gain-only master to -14 LUFS, then keep true peak under -1.5 dBTP with a 4x-oversampled soft limiter (only acts on rare peaks)
sf.write(S+'mix_pre.wav',mix,sr,subtype='FLOAT')
m=subprocess.run(['ffmpeg','-v','info','-i',S+'mix_pre.wav','-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
I=float([l for l in m.splitlines() if l.strip().startswith('I:')][-1].split()[1])
mix*=10**((-14.0-I)/20)
from scipy.signal import resample_poly
up=resample_poly(mix,4,1,axis=0); lim=10**(-1.5/20)
env=np.abs(up).max(1)
gr=np.minimum(1,lim/np.maximum(env,1e-9))
# smooth gain: instant attack (look-ahead 1 ms), 60 ms release
k=int(0.001*sr*4); from scipy.ndimage import minimum_filter1d
gr=minimum_filter1d(gr,size=2*k+1)
rel=np.exp(-1/(0.06*sr*4)); out=np.empty_like(gr); c=1.0
for i in range(len(gr)):
    c=gr[i] if gr[i]<c else min(gr[i],c+(1-c)*(1-rel))
    out[i]=c
up*=out[:,None]
final=resample_poly(up,1,4,axis=0).astype(np.float32)
print('limiter max reduction %.2f dB, frames limited %.3f%%'%(-20*np.log10(out.min()),100*(out<0.999).mean()))
sf.write(S+'master.wav',final,sr,subtype='FLOAT')
