import torch, torchaudio, numpy as np, wave, json, sys
W=[("Okay","okei"),("yang","yang"),("special","spesyel"),("untuk","untuk"),("rumah","rumah"),("ni,","ni"),("CCC","si si si"),("dah","dah"),("dapat","dapat"),("dah.","dah"),
("Jadi","jadi"),("senang","senang"),("kata","kata"),("boleh","boleh"),("terus","terus"),("masuk,","masuk"),("move","muv"),("in.","in"),
("Semua","semua"),("dah","dah"),("boleh","boleh"),("masuk","masuk"),("dah.","dah"),
("Yang","yang"),("paling","paling"),("penting,","penting"),("Rizab","rizab"),("Melayu","melayu"),("ada","ada"),("rebate","ribet"),("15%.","lima belas peratus"),
("Untuk","untuk"),("non-Bumi","non bumi"),("lot,","lot"),("ada","ada"),("rebate","ribet"),("RM30,000.","tiga puluh ribu"),
("Jangan","jangan"),("lepaskan","lepaskan"),("peluang","peluang"),("apa,","apa"),("nak","nak"),("dapat","dapat"),("rumah","rumah"),("di","di"),("kawasan","kawasan"),("yang","yang"),("sangat","sangat"),("premium","premium"),("kat","kat"),("Lusnak","lusnak"),("ni.","ni"),
("Stay","stei"),("tune.","tiun"),("Next","nekst"),("video.","video")]
b=torchaudio.pipelines.MMS_FA
model=b.get_model(); tok=b.get_tokenizer(); al=b.get_aligner()
wf=wave.open(sys.argv[1]); a=np.frombuffer(wf.readframes(wf.getnframes()),dtype=np.int16).astype(np.float32)/32768
wav=torch.tensor(a)[None]
words=[]; idx=[]
for i,(d,s) in enumerate(W):
    for p in s.split(): words.append(p); idx.append(i)
with torch.inference_mode():
    em,_=model(wav)
    spans=al(em[0], tok(words))
ratio=wav.shape[1]/em.shape[1]/16000
out=[]
for i,(d,s) in enumerate(W):
    ss=[sp for k,sp in enumerate(spans) if idx[k]==i]
    st=ss[0][0].start*ratio; en=ss[-1][-1].end*ratio
    sc=np.mean([t.score for sp in ss for t in sp])
    out.append({"w":d,"s":round(st,2),"e":round(en,2),"score":round(float(sc),2)})
    print(f"{st:6.2f}-{en:6.2f} {sc:.2f} {d}")
json.dump(out,open(sys.argv[2],"w"),indent=0)
