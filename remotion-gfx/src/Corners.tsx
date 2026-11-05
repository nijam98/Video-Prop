import React from 'react';
import {C} from './theme';
// Blueprint corner ticks around a card.
export const Corners: React.FC<{inset?: number; size?: number; color?: string}> = ({inset = 8, size = 14, color = C.accent}) => {
  const s: React.CSSProperties = {position: 'absolute', width: size, height: size, borderColor: color, borderStyle: 'solid', borderWidth: 0};
  return (
    <>
      <div style={{...s, left: inset, top: inset, borderLeftWidth: 2, borderTopWidth: 2}} />
      <div style={{...s, right: inset, top: inset, borderRightWidth: 2, borderTopWidth: 2}} />
      <div style={{...s, left: inset, bottom: inset, borderLeftWidth: 2, borderBottomWidth: 2}} />
      <div style={{...s, right: inset, bottom: inset, borderRightWidth: 2, borderBottomWidth: 2}} />
    </>
  );
};
