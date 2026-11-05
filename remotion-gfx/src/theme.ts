import {staticFile} from 'remotion';
// "Blueprint Notes" look: navy glass, hairline rules, survey-yellow accent.
export const C = {
  glass: 'rgba(12,20,38,0.80)',
  line: 'rgba(255,255,255,0.28)',
  ink: '#F7F4EC',
  dim: 'rgba(247,244,236,0.62)',
  accent: '#FFC83D',
};
export const fontCss = `
@font-face{font-family:'Outfit';src:url('${staticFile('fonts/outfit-var.woff2')}') format('woff2');font-weight:100 900;}
@font-face{font-family:'Space Mono';src:url('${staticFile('fonts/spacemono-400.woff2')}') format('woff2');font-weight:400;}
@font-face{font-family:'Space Mono';src:url('${staticFile('fonts/spacemono-700.woff2')}') format('woff2');font-weight:700;}
`;
