import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {C, fontCss} from './theme';
import {Corners} from './Corners';
// Visible from frame 0 (it is the thumbnail). The fill from 90% to 100% starts at FILL.
const FILL = 66;
export const LoanMeter: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = interpolate(f, [FILL, FILL + 16], [90, 100], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.22, 1, 0.36, 1)});
  const done = spring({frame: f - FILL - 12, fps, config: {damping: 14, mass: 0.6}});
  const breathe = 0.5 + 0.5 * Math.sin(f / 9);
  const W = 520;
  return (
    <AbsoluteFill style={{fontFamily: 'Outfit'}}>
      <style>{fontCss}</style>
      <div style={{position: 'absolute', inset: 0, background: C.glass, borderRadius: 22, border: `1.5px solid ${C.line}`}} />
      <Corners />
      <div style={{position: 'absolute', left: 40, top: 30, fontFamily: 'Space Mono', fontSize: 20, letterSpacing: 3, color: C.dim}}>
        01 · MARGIN PEMBIAYAAN
      </div>
      <div style={{position: 'absolute', right: 40, top: 18, fontSize: 56, fontWeight: 800, color: p >= 99.5 ? C.accent : C.ink, fontVariantNumeric: 'tabular-nums'}}>
        {Math.round(p)}%
      </div>
      {/* track */}
      <div style={{position: 'absolute', left: 40, top: 104, width: W, height: 14, borderRadius: 7, background: 'rgba(255,255,255,0.14)'}} />
      <div style={{position: 'absolute', left: 40, top: 104, width: (W * p) / 100, height: 14, borderRadius: 7, background: `linear-gradient(90deg, #F7F4EC, ${C.accent})`}} />
      {/* 90% tick */}
      <div style={{position: 'absolute', left: 40 + W * 0.9 - 1, top: 96, width: 2, height: 30, background: C.ink, opacity: 0.55 + 0.3 * breathe * (p < 91 ? 1 : 0)}} />
      <div style={{position: 'absolute', left: 40, top: 134, fontFamily: 'Space Mono', fontSize: 19, color: C.dim}}>
        loan biasa <span style={{color: C.ink}}>90%</span>
      </div>
      <div style={{position: 'absolute', right: 40, top: 128, fontSize: 28, fontWeight: 800, letterSpacing: 1, color: C.accent,
        opacity: done, transform: `translateY(${(1 - done) * 10}px) scale(${0.9 + 0.1 * done})`, transformOrigin: 'right center'}}>
        FULL LOAN ✓
      </div>
    </AbsoluteFill>
  );
};
