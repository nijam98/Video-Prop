import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {C, fontCss} from './theme';
import {Corners} from './Corners';
// Full loan meter: fills 0 -> 100% right at the start ("Full loan"),
// then the detail line lands on "harga jualan".
const FILL_START = 1;
const FILL_END = 20;
const DETAIL = 25;
export const LoanMeter: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = interpolate(f, [FILL_START, FILL_END], [0, 100], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.22, 1, 0.36, 1)});
  const done = spring({frame: f - FILL_END + 2, fps, config: {damping: 14, mass: 0.6}});
  const detail = spring({frame: f - DETAIL, fps, config: {damping: 16, mass: 0.6}});
  const glow = interpolate(f, [FILL_END - 2, FILL_END + 6, FILL_END + 20], [0, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const W = 520;
  return (
    <AbsoluteFill style={{fontFamily: 'Outfit'}}>
      <style>{fontCss}</style>
      <div style={{position: 'absolute', inset: 0, background: C.glass, borderRadius: 22, border: `1.5px solid ${C.line}`}} />
      <Corners />
      <div style={{position: 'absolute', left: 40, top: 30, fontFamily: 'Space Mono', fontSize: 20, letterSpacing: 3, color: C.dim}}>
        01 · PEMBIAYAAN PENUH
      </div>
      <div style={{position: 'absolute', right: 40, top: 18, fontSize: 56, fontWeight: 800, color: p >= 99.5 ? C.accent : C.ink, fontVariantNumeric: 'tabular-nums'}}>
        {Math.round(p)}%
      </div>
      <div style={{position: 'absolute', left: 40, top: 104, width: W, height: 14, borderRadius: 7, background: 'rgba(255,255,255,0.14)'}} />
      <div style={{position: 'absolute', left: 40, top: 104, width: (W * p) / 100, height: 14, borderRadius: 7, background: `linear-gradient(90deg, #F7F4EC, ${C.accent})`,
        boxShadow: `0 0 ${22 * glow}px rgba(255,200,61,${0.9 * glow})`}} />
      <div style={{position: 'absolute', left: 40, top: 132, fontSize: 26, fontWeight: 700, color: C.ink, display: 'flex', alignItems: 'center', gap: 10,
        opacity: detail, transform: `translateX(${(1 - detail) * -14}px)`}}>
        <span style={{width: 26, height: 26, borderRadius: 7, background: C.accent, display: 'inline-flex', alignItems: 'center', justifyContent: 'center'}}>
          <svg width={16} height={16} viewBox="0 0 22 22"><path d="M4 11.5l4.5 4.5L18 6.5" fill="none" stroke="#0C1426" strokeWidth={3.6} strokeLinecap="round" strokeLinejoin="round" /></svg>
        </span>
        Harga jualan
      </div>
      <div style={{position: 'absolute', right: 40, top: 128, fontSize: 28, fontWeight: 800, letterSpacing: 1, color: C.accent,
        opacity: done, transform: `translateY(${(1 - done) * 10}px) scale(${0.9 + 0.1 * done})`, transformOrigin: 'right center'}}>
        FULL LOAN ✓
      </div>
    </AbsoluteFill>
  );
};
