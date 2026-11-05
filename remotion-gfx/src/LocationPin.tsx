import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {C, fontCss} from './theme';
import {Corners} from './Corners';
export const LocationPin: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const card = spring({frame: f, fps, config: {damping: 16, mass: 0.6}});
  const drop = spring({frame: f - 3, fps, config: {damping: 9, mass: 0.7, stiffness: 140}});
  const ripple = (d: number) => interpolate(f, [12 + d, 42 + d], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const word = 'CHANGLUN';
  const sub = 'KUBANG PASU · KEDAH';
  const typed = Math.floor(interpolate(f, [16, 40], [0, sub.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  return (
    <AbsoluteFill style={{fontFamily: 'Outfit'}}>
      <style>{fontCss}</style>
      <div style={{position: 'absolute', inset: 0, opacity: card, transform: `translateY(${(1 - card) * 16}px)`}}>
        <div style={{position: 'absolute', inset: 0, background: C.glass, borderRadius: 24, border: `1.5px solid ${C.line}`}} />
        <Corners />
        {/* pin + ripples */}
        <div style={{position: 'absolute', left: 34, top: 30, width: 130, height: 140}}>
          {[0, 9].map((d) => (
            <div key={d} style={{position: 'absolute', left: 65 - 44, top: 112 - 14, width: 88, height: 28, borderRadius: '50%',
              border: `2px solid ${C.accent}`, opacity: (1 - ripple(d)) * (ripple(d) > 0 ? 0.9 : 0), transform: `scale(${0.3 + ripple(d) * 1.1})`}} />
          ))}
          <svg width={70} height={92} viewBox="0 0 70 92" style={{position: 'absolute', left: 30, top: 22, transform: `translateY(${(1 - drop) * -70}px)`, opacity: Math.min(1, drop * 3)}}>
            <path d="M35 90 C35 90 4 54 4 34 A31 31 0 0 1 66 34 C66 54 35 90 35 90Z" fill={C.accent} />
            <circle cx={35} cy={34} r={12} fill="#0C1426" />
          </svg>
        </div>
        <div style={{position: 'absolute', left: 168, top: 40, fontFamily: 'Space Mono', fontSize: 19, letterSpacing: 3, color: C.dim}}>03 · LOKASI</div>
        <div style={{position: 'absolute', left: 166, top: 62, fontSize: 70, fontWeight: 800, color: C.ink, letterSpacing: 2, display: 'flex'}}>
          {word.split('').map((ch, i) => {
            const s = spring({frame: f - 6 - i * 1.5, fps, config: {damping: 14, mass: 0.5}});
            return <span key={i} style={{display: 'inline-block', opacity: s, transform: `translateY(${(1 - s) * 22}px)`}}>{ch}</span>;
          })}
        </div>
        <div style={{position: 'absolute', left: 168, top: 146, fontFamily: 'Space Mono', fontSize: 19, letterSpacing: 1.5, color: C.accent}}>
          {sub.slice(0, typed)}<span style={{opacity: f % 16 < 8 && typed < sub.length ? 1 : 0}}>▍</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
