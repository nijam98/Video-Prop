# Final audio master (clear voice, no distortion)

The browser compressor in the HyperFrames voice chain squashed the voice too hard
(crest factor 8.9 dB -> 6.2 dB), and the bass "impact" on the location pin
(99% of its energy under 80 Hz) made phone speakers buzz. The delivery file is
therefore mastered outside the render:

1. Render the composition with the voice clips hidden (`data-hidden="true"` on every
   `vo-*` audio) -> music + SFX stem.
2. Rebuild the edited voice from `assets/voice.wav` and the cut list, then process it
   gently with ffmpeg:
   `highpass=f=100:poles=2, equalizer=f=250:t=q:w=1:g=-3, equalizer=f=3500:t=q:w=0.9:g=3,
    highshelf=f=9000:g=1.5, deesser=i=0.35:m=0.5:f=0.5,
    acompressor=threshold=-24dB:ratio=2.5:attack=8:release=160:knee=6:makeup=1`
3. `master.py`: voice set 20 dB above the bed, gain-only to -14 LUFS, then a 4x
   oversampled peak limiter at -1.5 dBTP that only touches rare peaks.
4. Mux with the HD video (CRF 15, ~23 Mbit/s, AAC 320k).
