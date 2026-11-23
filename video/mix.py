# Mixes voiceover + music bed (ducked) + SFX from sfx.json onto silent.mp4
import json,subprocess
A='../audio/'; S=A+'sfx/'
sfx=json.load(open('sfx.json')); VO=0.4; DUR=22
names=sorted({e['name'] for e in sfx})
inputs=['-i','silent.mp4','-i',A+'chris_v4.mp3','-i',S+'music.mp3']+sum([['-i',S+n+'.mp3'] for n in names],[])
idx={n:3+i for i,n in enumerate(names)}
gain={'pop':6,'click':1,'whoosh':-4,'riser':-7,'ding':4,'notif':-1,'type':-3}
f=[]
f.append(f"[1:a]aresample=44100,highpass=f=70,equalizer=f=3500:t=q:w=1.2:g=1.5,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,adelay={int(VO*1000)}|{int(VO*1000)},apad=whole_dur={DUR}[vo]")
f.append("[vo]asplit=2[vo1][vosc]")
f.append(f"[2:a]aresample=44100,volume=-17dB,afade=t=in:d=0.6,afade=t=out:st={DUR-1.6}:d=1.6,apad=whole_dur={DUR}[mus]")
f.append("[mus][vosc]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=300[musd]")
counts={}
labels=[]
for n,e in enumerate(sfx):
    i=idx[e['name']]; counts[i]=counts.get(i,0)+1
for i,c in counts.items(): f.append(f"[{i}:a]aresample=44100,asplit={c}"+''.join(f"[s{i}_{k}]" for k in range(c)))
used={}
for n,e in enumerate(sfx):
    i=idx[e['name']]; k=used.get(i,0); used[i]=k+1
    db=gain.get(e['name'],0)+20*__import__('math').log10(max(e['vol'],.01))-6
    d=int(e['t']*1000)
    f.append(f"[s{i}_{k}]volume={db:.1f}dB,adelay={d}|{d}[e{n}]"); labels.append(f"[e{n}]")
f.append("[vo1][musd]"+''.join(labels)+f"amix=inputs={2+len(labels)}:normalize=0:duration=longest,atrim=0:{DUR},loudnorm=I=-14:TP=-1.5:LRA=9[aout]")
cmd=['ffmpeg','-y','-loglevel','error']+inputs+['-filter_complex',';'.join(f),'-map','0:v','-map','[aout]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','44100','-movflags','+faststart','-shortest','Rule200_Bulanan_Qhomes.mp4']
subprocess.run(cmd,check=True); print('ok')
