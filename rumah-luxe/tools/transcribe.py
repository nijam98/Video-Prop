import sys, json, wave, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)
w_=wave.open(sys.argv[1]); a=np.frombuffer(w_.readframes(w_.getnframes()),dtype=np.int16).astype(np.float32)/32768
segs, info = m.transcribe(a, language="ms", word_timestamps=True, vad_filter=False, beam_size=5, condition_on_previous_text=False,
    initial_prompt="Rumah teres dua tingkat, harga, lokasi, bilik tidur, bilik air, dapur, ruang tamu, tanah.")
out=[]
for s in segs:
    out.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"w":w.word,"s":w.start,"e":w.end,"p":w.probability} for w in s.words]})
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}", flush=True)
json.dump(out, open(sys.argv[2],"w"), ensure_ascii=False, indent=1)
