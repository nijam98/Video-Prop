import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {C, fontCss} from './theme';
export const RebateRing: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = spring({frame: f, fps, config: {damping: 13, mass: 0.7}});
  const sweep = interpolate(f, [4, 30], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.33, 1, 0.68, 1)});
  const n = Math.round(sweep * 10);
  const R = 118, CIRC = 2 * Math.PI * R;
  const glint = interpolate(f, [30, 44], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{fontFamily: 'Outfit', alignItems: 'center'}}>
      <style>{fontCss}</style>
      <div style={{position: 'absolute', left: 15, top: 0, width: 270, height: 270, transform: `scale(${0.6 + 0.4 * pop})`, opacity: Math.min(1, pop * 1.4)}}>
        <svg width={270} height={270} viewBox="-135 -135 270 270" style={{position: 'absolute', inset: 0}}>
          <circle r={130} fill={C.glass} stroke={C.line} strokeWidth={1.5} />
          <circle r={R} fill="none" stroke="rgba(255,255,255,0.13)" strokeWidth={9} />
          <circle r={R} fill="none" stroke={C.accent} strokeWidth={9} strokeLinecap="round"
            strokeDasharray={CIRC} strokeDashoffset={CIRC * (1 - sweep)} transform="rotate(-90)" />
          {Array.from({length: 40}).map((_, i) => (
            <line key={i} x1={0} y1={-100} x2={0} y2={i % 10 === 0 ? -92 : -96} stroke="rgba(255,255,255,0.35)" strokeWidth={1.5} transform={`rotate(${i * 9})`} />
          ))}
        </svg>
        <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
          <div style={{fontFamily: 'Space Mono', fontSize: 19, letterSpacing: 4, color: C.dim, marginBottom: -4}}>REBATE</div>
          <div style={{fontSize: 92, fontWeight: 800, color: C.ink, lineHeight: 1, fontVariantNumeric: 'tabular-nums',
            textShadow: `0 0 ${18 * glint * (1 - glint) * 4}px rgba(255,200,61,0.8)`}}>
            {n}<span style={{fontSize: 48, color: C.accent}}>%</span>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
