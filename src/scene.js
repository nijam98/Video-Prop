/* Naz Property – "Formula Gaji x 12 x 10" (1080x1920, 30fps, 64s)
 * Style: hand-drawn characters (rough.js, "boiling" lines) + hologram UI (glow, scanlines, flicker).
 * Every frame is a pure function of time, so frames can be rendered in any order. */

const W = 1080, H = 1920, FPS = 30, DUR = 64;
const out = document.getElementById('c');
const octx = out.getContext('2d');
const buf = document.createElement('canvas'); buf.width = W; buf.height = H;
const ctx = buf.getContext('2d');
const rc = rough.canvas(buf);
let g = ctx;          // current drawing context for helpers
let T = 0, FRAME = 0, BOIL = 0;

// ---------------------------------------------------------------- palette
const INK = '#141428', CYAN = '#3ff3ff', CYAN2 = '#7af9ff', YEL = '#ffd23f', RED = '#ff3b4e',
  GREEN = '#3ef0a0', SKIN = '#c98a5c', SKIN_D = '#a86c43', PAPER = '#fffdf3', GOLD = '#ffc94a';
const F_BOLD = '"Baloo 2"', F_HOLO = 'Orbitron', F_HAND = '"Patrick Hand"';

// ---------------------------------------------------------------- math
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const inv = (a, b, x) => clamp((x - a) / (b - a));
const E = {
  out: t => 1 - Math.pow(1 - t, 3),
  in: t => t * t * t,
  io: t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  back: t => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  el: t => t <= 0 ? 0 : t >= 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - .75) * 2.0944) + 1,
};
function rnd(i) {
  let t = (Math.imul(i | 0, 2654435761) + 0x6D2B79F5) >>> 0;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}
function rgba(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${n >> 16 & 255},${n >> 8 & 255},${n & 255},${a})`;
}
const pop = (t0, x = T, d = .35) => E.back(inv(t0, t0 + d, x));
const fadeIn = (t0, d = .25) => inv(t0, t0 + d, T);
const vis = (a, b, fi = .2, fo = .2) => Math.min(inv(a, a + fi, T), 1 - inv(b - fo, b, T));
const talk = () => (window.ENV ? ENV[Math.min(ENV.length - 1, FRAME)] : 0) || 0;

// rough.js options with "boiling" seed (lines re-sketch 8x per second)
function R(seed, o = {}) {
  return Object.assign({
    seed: 1 + ((seed * 131 + BOIL * 977) % 99991), roughness: 1.15, bowing: 1.1,
    stroke: INK, strokeWidth: 3.2, fillWeight: 2.2, hachureGap: 9,
  }, o);
}
const S = (seed, fill, o = {}) => R(seed, Object.assign({ fill, fillStyle: 'solid' }, o));

// ---------------------------------------------------------------- text
function text(str, x, y, o = {}) {
  const { font = F_BOLD, size = 60, weight = 800, color = '#fff', align = 'center', base = 'middle',
    stroke = null, sw = 8, glow = null, blur = 20, alpha = 1, rot = 0, scale = 1, spacing = 0 } = o;
  if (alpha <= 0 || scale <= 0) return;
  g.save(); g.globalAlpha *= alpha; g.translate(x, y); g.rotate(rot); g.scale(scale, scale);
  g.font = `${weight} ${size}px ${font}`; g.textAlign = align; g.textBaseline = base;
  if (spacing) g.letterSpacing = spacing + 'px';
  if (stroke) { g.lineJoin = 'round'; g.lineWidth = sw; g.strokeStyle = stroke; g.strokeText(str, 0, 0); }
  if (glow) { g.shadowColor = glow; g.shadowBlur = blur; g.fillStyle = color; g.fillText(str, 0, 0); }
  g.fillStyle = color; g.fillText(str, 0, 0);
  g.restore();
}
function measure(str, size, font = F_BOLD, weight = 800) {
  g.save(); g.font = `${weight} ${size}px ${font}`; const w = g.measureText(str).width; g.restore(); return w;
}
function flicker(k = 0) {
  const r = rnd(FRAME * 7 + k * 131);
  return r < 0.04 ? 0.55 : 0.9 + 0.1 * rnd(FRAME * 3 + k);
}
function holoText(str, x, y, size, o = {}) {
  const { color = CYAN, alpha = 1, font = F_HOLO, weight = 900, align = 'center', scale = 1, k = 0, spacing = 0, rot = 0 } = o;
  const a = alpha * flicker(k);
  if (a <= 0) return;
  const base = { font, size, weight, align, scale, spacing, rot };
  const off = Math.max(1.5, size * .025);
  text(str, x - off, y, Object.assign({}, base, { color: 'rgba(255,60,140,.5)', alpha: a * .45 }));
  text(str, x + off, y, Object.assign({}, base, { color: 'rgba(60,140,255,.5)', alpha: a * .45 }));
  text(str, x, y, Object.assign({}, base, { color, glow: color, blur: 26, alpha: a * .85 }));
  text(str, x, y, Object.assign({}, base, { color, alpha: a }));
  text(str, x, y, Object.assign({}, base, { color: '#ffffff', alpha: a * .22 }));
}

// ---------------------------------------------------------------- shapes
function rrect(x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
function holoPanel(x, y, w, h, o = {}) {
  const { alpha = 1, color = CYAN, r = 26, k = 0, fill = .10 } = o;
  if (alpha <= 0) return;
  const a = alpha * flicker(k + 50);
  g.save(); g.globalAlpha *= a;
  const gr = g.createLinearGradient(0, y, 0, y + h);
  gr.addColorStop(0, rgba(color, fill * 1.5)); gr.addColorStop(1, rgba(color, fill * .4));
  rrect(x, y, w, h, r); g.fillStyle = gr; g.fill();
  // moving scan band
  g.save(); rrect(x, y, w, h, r); g.clip();
  const sy = y + ((T * 260 + k * 97) % (h + 200)) - 100;
  const sg = g.createLinearGradient(0, sy - 60, 0, sy + 60);
  sg.addColorStop(0, rgba(color, 0)); sg.addColorStop(.5, rgba(color, .16)); sg.addColorStop(1, rgba(color, 0));
  g.fillStyle = sg; g.fillRect(x, sy - 60, w, 120);
  for (let yy = y; yy < y + h; yy += 6) { g.fillStyle = rgba(color, .05); g.fillRect(x, yy, w, 2); }
  g.restore();
  g.shadowColor = color; g.shadowBlur = 24; g.strokeStyle = rgba(color, .9); g.lineWidth = 3;
  rrect(x, y, w, h, r); g.stroke();
  // corner brackets
  g.lineWidth = 7; g.lineCap = 'round'; const c = 38;
  [[x, y, 1, 1], [x + w, y, -1, 1], [x, y + h, 1, -1], [x + w, y + h, -1, -1]].forEach(([cx, cy, sx, sy2]) => {
    g.beginPath(); g.moveTo(cx + sx * 6, cy + sy2 * (c + 6)); g.lineTo(cx + sx * 6, cy + sy2 * 6); g.lineTo(cx + sx * (c + 6), cy + sy2 * 6); g.stroke();
  });
  g.restore();
}
function glowLine(pts, color, width = 3, blur = 18, alpha = 1) {
  g.save(); g.globalAlpha *= alpha; g.strokeStyle = color; g.lineWidth = width; g.shadowColor = color; g.shadowBlur = blur;
  g.lineJoin = 'round'; g.lineCap = 'round'; g.beginPath();
  pts.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.stroke(); g.restore();
}
function burst(x, y, r1, r2, n, color, rot = 0, seed = 1) {
  const pts = [];
  for (let i = 0; i < n * 2; i++) {
    const a = rot + i / (n * 2) * Math.PI * 2, r = i % 2 ? r1 : r2 * (0.85 + .3 * rnd(seed * 31 + i));
    pts.push([x + Math.cos(a) * r, y + Math.sin(a) * r]);
  }
  rc.polygon(pts, S(seed, color, { strokeWidth: 4 }));
}
function checkMark(x, y, s, color = GREEN, alpha = 1) {
  glowLine([[x - s * .5, y], [x - s * .12, y + s * .38], [x + s * .55, y - s * .42]], color, s * .16, 20, alpha);
}
function notEqual(x, y, s, color, alpha = 1, glow = true) {
  g.save(); g.globalAlpha *= alpha; g.strokeStyle = color; g.lineWidth = s * .13; g.lineCap = 'round';
  if (glow) { g.shadowColor = color; g.shadowBlur = 18; }
  g.beginPath(); g.moveTo(x - s * .4, y - s * .16); g.lineTo(x + s * .4, y - s * .16);
  g.moveTo(x - s * .4, y + s * .16); g.lineTo(x + s * .4, y + s * .16);
  g.moveTo(x + s * .22, y - s * .45); g.lineTo(x - s * .22, y + s * .45); g.stroke(); g.restore();
}
function warnTriangle(x, y, s, seed = 5) {
  rc.polygon([[x, y - s * .55], [x + s * .6, y + s * .45], [x - s * .6, y + s * .45]], S(seed, YEL, { strokeWidth: 4 }));
  text('!', x, y + s * .1, { size: s * .7, color: INK, weight: 800 });
}
function handArrow(x1, y1, x2, y2, prog = 1, color = '#fff', seed = 3, w = 5) {
  if (prog <= 0) return;
  const xe = lerp(x1, x2, prog), ye = lerp(y1, y2, prog);
  const mx = (x1 + xe) / 2 + (ye - y1) * .18, my = (y1 + ye) / 2 - (xe - x1) * .18;
  rc.path(`M ${x1} ${y1} Q ${mx} ${my} ${xe} ${ye}`, R(seed, { stroke: color, strokeWidth: w }));
  if (prog > .85) {
    const a = Math.atan2(ye - my, xe - mx), L = 34;
    rc.linearPath([[xe + Math.cos(a + 2.6) * L, ye + Math.sin(a + 2.6) * L], [xe, ye], [xe + Math.cos(a - 2.6) * L, ye + Math.sin(a - 2.6) * L]],
      R(seed + 1, { stroke: color, strokeWidth: w }));
  }
}
function scribbleCircle(cx, cy, rx, ry, prog, color = RED, seed = 9, w = 6) {
  if (prog <= 0) return;
  const pts = [], n = 60, turns = 1.15 * prog;
  for (let i = 0; i <= n; i++) {
    const a = -1.9 + i / n * turns * Math.PI * 2, j = 1 + .05 * Math.sin(i * .7 + seed);
    pts.push([cx + Math.cos(a) * rx * j, cy + Math.sin(a) * ry * j]);
  }
  g.save(); g.shadowColor = color; g.shadowBlur = 10;
  rc.curve(pts, R(seed, { stroke: color, strokeWidth: w, roughness: .8 }));
  g.restore();
}
function sparkle(x, y, s, a = 1, color = '#fff') {
  if (a <= 0) return;
  g.save(); g.globalAlpha *= a; g.fillStyle = color; g.shadowColor = color; g.shadowBlur = 16;
  g.beginPath(); g.moveTo(x, y - s); g.quadraticCurveTo(x, y, x + s, y); g.quadraticCurveTo(x, y, x, y + s);
  g.quadraticCurveTo(x, y, x - s, y); g.quadraticCurveTo(x, y, x, y - s); g.fill(); g.restore();
}
function sparkles(cx, cy, rx, ry, n, seed, a = 1) {
  for (let i = 0; i < n; i++) {
    const ph = (T * (0.6 + rnd(seed + i) * .8) + rnd(seed * 7 + i)) % 1;
    const s = 10 + 18 * rnd(seed * 3 + i);
    sparkle(cx + (rnd(seed * 5 + i) - .5) * 2 * rx, cy + (rnd(seed * 11 + i) - .5) * 2 * ry, s * Math.sin(ph * Math.PI), a, i % 3 ? '#fff' : YEL);
  }
}

// ---------------------------------------------------------------- background
const SKY = Array.from({ length: 22 }, (_, i) => ({ x: i * 54 - 40 + rnd(i) * 20, w: 40 + rnd(i + 50) * 60, h: 90 + rnd(i + 90) * 260 }));
function background(tint = 0) {
  const gr = g.createRadialGradient(540, 760, 80, 540, 900, 1250);
  gr.addColorStop(0, '#22348a'); gr.addColorStop(.45, '#121a52'); gr.addColorStop(1, '#060820');
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
  if (tint > 0) { g.fillStyle = `rgba(150,0,20,${.38 * tint})`; g.fillRect(0, 0, W, H); }
  // skyline (hand drawn, faint)
  const hz = 1180;
  g.save(); g.globalAlpha = .55;
  SKY.forEach((b, i) => {
    rc.rectangle(b.x, hz - b.h, b.w, b.h, R(400 + i, { stroke: rgba(CYAN, .35), strokeWidth: 2, fill: tint > .3 ? '#2a0c22' : '#0e1745', fillStyle: 'solid', roughness: 1.4 }));
    for (let wy = hz - b.h + 18; wy < hz - 20; wy += 34) for (let wx = b.x + 10; wx < b.x + b.w - 14; wx += 22)
      if (rnd(i * 977 + wy * 3 + wx) > .55) { g.fillStyle = rgba(YEL, .35); g.fillRect(wx, wy, 8, 12); }
  });
  g.restore();
  // perspective floor grid
  g.save();
  const fg = g.createLinearGradient(0, hz, 0, H); fg.addColorStop(0, '#0a1440'); fg.addColorStop(1, '#03051a');
  g.fillStyle = fg; g.fillRect(0, hz, W, H - hz);
  g.strokeStyle = rgba(tint > .3 ? '#ff4060' : CYAN, .22); g.lineWidth = 2;
  for (let i = -12; i <= 12; i++) { g.beginPath(); g.moveTo(540 + i * 40, hz); g.lineTo(540 + i * 260, H); g.stroke(); }
  for (let k = 0; k < 14; k++) {
    const f = ((k + (T * .8) % 1) / 14), y = hz + (H - hz) * f * f;
    g.globalAlpha = .4 + .6 * f; g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke();
  }
  g.restore();
  // horizon glow
  const hg = g.createLinearGradient(0, hz - 60, 0, hz + 40);
  hg.addColorStop(0, rgba(CYAN, 0)); hg.addColorStop(.6, rgba(tint > .3 ? '#ff3050' : CYAN, .25)); hg.addColorStop(1, rgba(CYAN, 0));
  g.fillStyle = hg; g.fillRect(0, hz - 60, W, 100);
  // floating dust
  for (let i = 0; i < 46; i++) {
    const x = (rnd(i) * W + T * 18 * (rnd(i + 9) - .5) * 4 + W) % W;
    const y = ((rnd(i + 3) * H - T * (14 + 30 * rnd(i + 5))) % H + H) % H;
    const a = .25 + .35 * Math.sin(T * 2 + i);
    g.fillStyle = rgba(CYAN2, Math.max(0, a)); g.beginPath(); g.arc(x, y, 1.5 + 2.5 * rnd(i + 7), 0, 7); g.fill();
  }
}

// ---------------------------------------------------------------- characters
function ik(sx, sy, hx, hy, l1, l2, bend) {
  const dx = hx - sx, dy = hy - sy, d = Math.min(Math.hypot(dx, dy), l1 + l2 - 1), a = Math.atan2(dy, dx);
  const b = Math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1));
  const ex = sx + Math.cos(a + bend * b) * l1, ey = sy + Math.sin(a + bend * b) * l1;
  return { ex, ey, hx: sx + Math.cos(a) * d, hy: sy + Math.sin(a) * d };
}
function limb(pts, color, w = 40) {
  const j = (i) => (rnd(BOIL * 13 + i) - .5) * 2.4;
  g.save(); g.lineCap = 'round'; g.lineJoin = 'round';
  g.beginPath(); pts.forEach((p, i) => i ? g.lineTo(p[0] + j(i), p[1] + j(i + 5)) : g.moveTo(p[0], p[1]));
  g.strokeStyle = INK; g.lineWidth = w + 7; g.stroke(); g.strokeStyle = color; g.lineWidth = w; g.stroke();
  g.restore();
}
function hand(x, y, type, ang = 0, seed = 1) {
  g.save(); g.translate(x, y); g.rotate(ang);
  const fing = (x1, y1, x2, y2) => { limb([[x1, y1], [x2, y2]], SKIN, 12); };
  if (type === 'point') fing(10, 0, 62, 0);
  if (type === 'thumb') fing(0, -6, 0, -50);
  if (type === 'open' || type === 'wave') {
    [-.75, -.25, .25, .7].forEach((a, i) => fing(Math.cos(a) * 14, Math.sin(a) * 14, Math.cos(a) * 46, Math.sin(a) * 46));
    fing(-4, 10, -24, 36);
  }
  rc.circle(0, 0, 54, S(seed, SKIN, { strokeWidth: 3.5 }));
  g.restore();
}
function arm(sh, tgt, bend, color, type, seed, l1 = 150, l2 = 145) {
  const k = ik(sh[0], sh[1], tgt[0], tgt[1], l1, l2, bend);
  limb([sh, [k.ex, k.ey], [k.hx, k.hy]], color, 40);
  return { x: k.hx, y: k.hy, ang: Math.atan2(k.hy - k.ey, k.hx - k.ex), type, seed };
}
function face(hy, P, seed) {
  const lx = P.lookX * 7, ly = P.lookY * 5;
  const ex = P.expr;
  // eyes
  if (ex === 'happy') {
    [-33, 33].forEach((x, i) => rc.arc(x, hy - 6, 34, 26, Math.PI, Math.PI * 2, false, R(seed + i, { strokeWidth: 5 })));
  } else {
    const big = ex === 'shock';
    [-33, 33].forEach((x, i) => {
      rc.ellipse(x, hy - 8, big ? 46 : 32, big ? 50 : 34, S(seed + i, '#fff', { strokeWidth: 3 }));
      g.fillStyle = INK; g.beginPath(); g.arc(x + lx, hy - 8 + ly, big ? 6 : 8.5, 0, 7); g.fill();
      g.fillStyle = '#fff'; g.beginPath(); g.arc(x + lx + 2.5, hy - 11 + ly, 2.5, 0, 7); g.fill();
    });
  }
  // brows
  const by = ex === 'shock' ? hy - 66 : ex === 'worried' ? hy - 48 : ex === 'stern' ? hy - 40 : hy - 46;
  const tilt = ex === 'worried' ? 10 : ex === 'stern' ? -12 : 0;
  rc.line(-52, by + tilt, -16, by - tilt * .4, R(seed + 3, { strokeWidth: 7, stroke: P.brow || '#111' }));
  rc.line(16, by - tilt * .4, 52, by + tilt, R(seed + 4, { strokeWidth: 7, stroke: P.brow || '#111' }));
  // nose
  rc.path(`M -2 ${hy + 4} Q -14 ${hy + 28} 6 ${hy + 30}`, R(seed + 5, { stroke: SKIN_D, strokeWidth: 4 }));
  if (P.mustache) rc.path(`M -32 ${hy + 46} Q 0 ${hy + 32} 32 ${hy + 46} Q 0 ${hy + 40} -32 ${hy + 46} Z`, S(seed + 6, '#1b1b1b', { strokeWidth: 2 }));
  // mouth
  const my = hy + 64;
  if (P.blush) { g.fillStyle = 'rgba(255,110,120,.35)'; [-50, 50].forEach(x => { g.beginPath(); g.ellipse(x, hy + 30, 16, 9, 0, 0, 7); g.fill(); }); }
  if (ex === 'shock') {
    rc.ellipse(0, my + 4, 38, 50, S(seed + 7, '#5b1620', { strokeWidth: 3 }));
    g.fillStyle = '#e8616e'; g.beginPath(); g.ellipse(0, my + 18, 12, 8, 0, 0, 7); g.fill();
  } else if (P.talk > .08) {
    const o = P.talk;
    rc.ellipse(0, my, 46 + 6 * o, 8 + 34 * o, S(seed + 8, '#5b1620', { strokeWidth: 3 }));
    if (o > .35) { g.fillStyle = '#fff'; g.fillRect(-14, my - (4 + 17 * o) + 3, 28, 6); }
  } else if (ex === 'happy' || ex === 'smile') {
    rc.path(`M -28 ${my - 8} Q 0 ${my + 26} 28 ${my - 8} Z`, S(seed + 9, '#5b1620', { strokeWidth: 3 }));
    g.fillStyle = '#fff'; g.fillRect(-20, my - 7, 40, 6);
  } else if (ex === 'worried') {
    rc.path(`M -22 ${my + 6} Q 0 ${my - 10} 22 ${my + 6}`, R(seed + 9, { strokeWidth: 5 }));
  } else if (ex === 'stern') {
    rc.line(-22, my, 22, my - 2, R(seed + 9, { strokeWidth: 5, stroke: '#7a2836' }));
  } else {
    rc.path(`M -24 ${my - 4} Q 0 ${my + 14} 24 ${my - 4}`, R(seed + 9, { strokeWidth: 5 }));
  }
}

/* Malaysian man. (x,y) = feet, s = scale (height ~ 790*s px).
 * arms: {l:[x,y], r:[x,y]} hand targets in local coords; hands: {l:type, r:type} */
function drawMan(x, y, s, p = {}) {
  const P = Object.assign({ expr: 'neutral', talk: 0, shirt: '#2f80ed', lookX: 0, lookY: 0, mustache: true, blush: false,
    l: [-150, -380], r: [150, -380], hl: 'fist', hr: 'fist', bl: 1, br: -1, hold: null, alpha: 1 }, p);
  g.save(); g.globalAlpha *= P.alpha; g.translate(x, y); g.scale(s, s);
  const ub = Math.sin(T * 2.6) * 4;
  g.fillStyle = 'rgba(0,0,0,.4)'; g.beginPath(); g.ellipse(0, 0, 170, 30, 0, 0, 7); g.fill();
  rc.polygon([[-64, -335], [-4, -335], [-12, -26], [-58, -26]], S(11, '#2b2d42'));
  rc.polygon([[4, -335], [64, -335], [58, -26], [12, -26]], S(12, '#2b2d42'));
  rc.ellipse(-44, -16, 84, 34, S(13, '#151515')); rc.ellipse(44, -16, 84, 34, S(14, '#151515'));
  g.translate(0, ub);
  rc.polygon([[-114, -585], [114, -585], [94, -320], [-94, -320]], S(15, P.shirt));
  // shirt pattern (hand drawn batik-ish dots)
  for (let i = 0; i < 7; i++) rc.circle(-70 + (i % 4) * 46 + (i > 3 ? 23 : 0), -520 + Math.floor(i / 4) * 90, 16, R(30 + i, { stroke: 'rgba(255,255,255,.45)', strokeWidth: 2 }));
  rc.rectangle(-96, -340, 192, 22, S(16, '#3d2b1f'));
  rc.line(0, -560, 0, -342, R(17, { strokeWidth: 2.5 }));
  rc.polygon([[-42, -590], [0, -548], [-20, -522], [-60, -572]], S(18, '#fff'));
  rc.polygon([[42, -590], [0, -548], [20, -522], [60, -572]], S(19, '#fff'));
  rc.rectangle(-24, -620, 48, 40, S(20, SKIN));
  const hy = -692;
  rc.ellipse(-78, hy + 4, 30, 46, S(21, SKIN)); rc.ellipse(78, hy + 4, 30, 46, S(22, SKIN));
  rc.ellipse(0, hy, 158, 184, S(23, SKIN));
  rc.path(`M -82 ${hy - 6} C -96 ${hy - 96} -30 ${hy - 126} 12 ${hy - 116} C 64 ${hy - 112} 98 ${hy - 70} 82 ${hy - 8} C 74 ${hy - 52} 46 ${hy - 72} 6 ${hy - 70} C -34 ${hy - 70} -64 ${hy - 50} -82 ${hy - 6} Z`, S(24, '#161616'));
  face(hy, P, 40);
  const L = arm([-100, -560], P.l, P.bl, P.shirt, P.hl, 60);
  const Rr = arm([100, -560], P.r, P.br, P.shirt, P.hr, 61);
  if (P.hold) P.hold(L, Rr);
  [L, Rr].forEach(h => hand(h.x, h.y, h.type, h.type === 'thumb' ? 0 : h.ang, h.seed));
  g.restore();
}

/* Bank officer in tudung + blazer. */
function drawOfficer(x, y, s, p = {}) {
  const P = Object.assign({ expr: 'stern', talk: 0, lookX: 0, lookY: 0, l: [-150, -380], r: [150, -380], hl: 'fist', hr: 'fist',
    bl: 1, br: -1, hold: null, alpha: 1, brow: '#2b1a12' }, p);
  const BL = '#1d3a6e', HIJ = '#8a3ab9';
  g.save(); g.globalAlpha *= P.alpha; g.translate(x, y); g.scale(s, s);
  const ub = Math.sin(T * 2.3 + 1) * 3;
  g.fillStyle = 'rgba(0,0,0,.4)'; g.beginPath(); g.ellipse(0, 0, 160, 28, 0, 0, 7); g.fill();
  rc.polygon([[-80, -340], [80, -340], [104, -30], [-104, -30]], S(70, '#22223a'));
  rc.ellipse(-40, -16, 70, 28, S(71, '#151515')); rc.ellipse(40, -16, 70, 28, S(72, '#151515'));
  g.translate(0, ub);
  rc.polygon([[-110, -585], [110, -585], [92, -330], [-92, -330]], S(73, BL));
  rc.polygon([[-30, -585], [30, -585], [0, -470]], S(74, '#fff'));
  rc.rectangle(40, -500, 60, 34, S(75, '#fff', { strokeWidth: 2 }));
  text('BANK', 70, -483, { size: 18, color: '#1d3a6e', font: F_HOLO, weight: 900 });
  const hy = -690;
  rc.path(`M -120 -560 C -130 ${hy - 40} -90 ${hy - 120} 0 ${hy - 124} C 90 ${hy - 120} 130 ${hy - 40} 120 -560 C 80 -520 -80 -520 -120 -560 Z`, S(76, HIJ));
  rc.ellipse(0, hy + 6, 136, 166, S(77, SKIN));
  rc.path(`M -70 ${hy - 40} C -50 ${hy - 86} 50 ${hy - 86} 70 ${hy - 40}`, R(78, { stroke: '#5e1f86', strokeWidth: 10 }));
  rc.path(`M -60 ${hy + 60} C -40 ${hy + 110} 40 ${hy + 110} 60 ${hy + 60} C 80 ${hy + 110} 70 -600 0 -585 C -70 -600 -80 ${hy + 110} -60 ${hy + 60} Z`, S(79, HIJ));
  face(hy + 6, Object.assign({}, P, { mustache: false }), 90);
  [-1, 1].forEach(sg => rc.line(sg * 42, hy - 30, sg * 50, hy - 36, R(98 + sg, { strokeWidth: 3 })));
  const L = arm([-98, -560], P.l, P.bl, BL, P.hl, 100);
  const Rr = arm([98, -560], P.r, P.br, BL, P.hr, 101);
  if (P.hold) P.hold(L, Rr);
  [L, Rr].forEach(h => hand(h.x, h.y, h.type, h.type === 'thumb' ? 0 : h.ang, h.seed));
  g.restore();
}

// ---------------------------------------------------------------- props
function payslip(cx, cy, w, h, rot = 0, o = {}) {
  g.save(); g.translate(cx, cy); g.rotate(rot);
  rc.rectangle(-w / 2, -h / 2, w, h, S(200, PAPER, { strokeWidth: 3.5 }));
  text('SLIP GAJI', 0, -h / 2 + 30, { font: F_HAND, size: 34, weight: 400, color: INK });
  rc.line(-w / 2 + 20, -h / 2 + 54, w / 2 - 20, -h / 2 + 54, R(201, { strokeWidth: 2 }));
  text('Gaji Kasar:', 0, -h / 2 + 80, { font: F_HAND, size: 28, weight: 400, color: '#555' });
  text('RM2,500', 0, h / 2 - 50, { size: 62, color: '#d62839', weight: 800 });
  rc.line(-w / 2 + 30, h / 2 - 18, w / 2 - 30, h / 2 - 18, R(202, { stroke: '#d62839', strokeWidth: 3 }));
  if (o.stamp > 0) {
    const s = 1 + 1.5 * (1 - E.out(o.stamp));
    g.save(); g.globalAlpha *= clamp(o.stamp * 2); g.rotate(-.22); g.scale(s, s);
    rc.rectangle(-115, -32, 230, 64, R(203, { stroke: '#e0102a', strokeWidth: 5 }));
    text('TAK CUKUP?', 0, 2, { size: 40, color: '#e0102a' });
    g.restore();
  }
  g.restore();
}
function house2D(x, y, s, a = 1) {
  g.save(); g.globalAlpha *= a; g.translate(x, y); g.scale(s, s);
  rc.ellipse(0, 10, 560, 60, S(300, '#1f7a5a', { strokeWidth: 2.5 }));
  rc.rectangle(-170, -230, 340, 230, R(301, { fill: '#f6d365', fillStyle: 'solid' }));
  rc.rectangle(-170, -230, 340, 230, R(302, { fill: '#e2b23f', fillStyle: 'hachure', stroke: 'none', hachureGap: 14 }));
  rc.rectangle(110, -360, 40, 90, S(303, '#a23b3b'));
  rc.polygon([[-205, -220], [0, -390], [205, -220]], R(304, { fill: '#e63946', fillStyle: 'solid' }));
  rc.polygon([[-205, -220], [0, -390], [205, -220]], R(305, { fill: '#b8202c', fillStyle: 'hachure', stroke: 'none', hachureAngle: 60 }));
  rc.rectangle(-36, -130, 72, 130, S(306, '#8d5524'));
  g.fillStyle = YEL; g.beginPath(); g.arc(22, -64, 5, 0, 7); g.fill();
  [[-140, -180], [62, -180]].forEach(([wx, wy], i) => {
    rc.rectangle(wx, wy, 78, 70, S(307 + i, '#9be7ff'));
    rc.line(wx + 39, wy, wx + 39, wy + 70, R(309 + i)); rc.line(wx, wy + 35, wx + 78, wy + 35, R(311 + i));
  });
  rc.circle(0, -290, 46, S(313, '#9be7ff'));
  rc.rectangle(222, -150, 22, 150, S(314, '#7a4a25'));
  rc.circle(233, -190, 130, R(315, { fill: '#2a9d8f', fillStyle: 'solid' }));
  rc.circle(233, -190, 130, R(316, { fill: '#1e7a6e', fillStyle: 'hachure', stroke: 'none' }));
  for (let i = 0; i < 3; i++) {
    const ph = (T * .5 + i / 3) % 1;
    g.fillStyle = `rgba(230,240,255,${.5 * (1 - ph)})`; g.beginPath(); g.arc(130 + Math.sin(ph * 6) * 10, -380 - ph * 120, 14 + ph * 22, 0, 7); g.fill();
  }
  g.restore();
}

// --- 3D house (wireframe hologram that materialises into a hand-drawn model)
const HOUSE = (() => {
  const w = 1, d = .8, h = 1.1, rh = 1.95, ov = .14;
  const F = (pts, color, hatch, kids = []) => ({ pts, color, hatch, kids });
  const faces = [
    F([[-w, 0, d], [w, 0, d], [w, h, d], [-w, h, d]], '#f6d365', '#d9a933', [
      F([[-.22, 0, d], [.22, 0, d], [.22, .66, d], [-.22, .66, d]], '#8d5524', null),
      F([[-.84, .42, d], [-.42, .42, d], [-.42, .82, d], [-.84, .82, d]], '#9be7ff', null),
      F([[.42, .42, d], [.84, .42, d], [.84, .82, d], [.42, .82, d]], '#9be7ff', null)]),
    F([[w, 0, -d], [-w, 0, -d], [-w, h, -d], [w, h, -d]], '#f6d365', '#d9a933'),
    F([[-w, 0, -d], [-w, 0, d], [-w, h, d], [-w, rh, 0], [-w, h, -d]], '#eec25a', '#c99a2e', [
      F([[-w, .45, -.3], [-w, .45, .3], [-w, .85, .3], [-w, .85, -.3]], '#9be7ff', null)]),
    F([[w, 0, d], [w, 0, -d], [w, h, -d], [w, rh, 0], [w, h, d]], '#eec25a', '#c99a2e', [
      F([[w, .45, .3], [w, .45, -.3], [w, .85, -.3], [w, .85, .3]], '#9be7ff', null)]),
    F([[-w - ov, h - .06, d + ov], [w + ov, h - .06, d + ov], [w + ov, rh, 0], [-w - ov, rh, 0]], '#e63946', '#a51d29'),
    F([[w + ov, h - .06, -d - ov], [-w - ov, h - .06, -d - ov], [-w - ov, rh, 0], [w + ov, rh, 0]], '#e63946', '#a51d29'),
    F([[.45, 1.5, -.2], [.75, 1.5, -.2], [.75, 2.25, -.2], [.45, 2.25, -.2]], '#a23b3b', null),
    F([[.75, 1.5, -.5], [.45, 1.5, -.5], [.45, 2.25, -.5], [.75, 2.25, -.5]], '#a23b3b', null),
    F([[.45, 1.5, -.5], [.45, 1.5, -.2], [.45, 2.25, -.2], [.45, 2.25, -.5]], '#8e2f2f', null),
    F([[.75, 1.5, -.2], [.75, 1.5, -.5], [.75, 2.25, -.5], [.75, 2.25, -.2]], '#8e2f2f', null),
    F([[.45, 2.25, -.2], [.75, 2.25, -.2], [.75, 2.25, -.5], [.45, 2.25, -.5]], '#6e2424', null),
  ];
  const center = [0, .7, 0];
  const orient = (f, c) => {
    const [a, b, cc] = f.pts, u = b.map((v, i) => v - a[i]), v = cc.map((v2, i) => v2 - a[i]);
    const n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
    const m = f.pts.reduce((s, p) => s.map((q, i) => q + p[i] / f.pts.length), [0, 0, 0]);
    if (n[0] * (m[0] - c[0]) + n[1] * (m[1] - c[1]) + n[2] * (m[2] - c[2]) < 0) f.pts.reverse();
  };
  const chim = new Set(['#a23b3b', '#8e2f2f', '#6e2424']);
  faces.forEach(f => orient(f, chim.has(f.color) ? [.6, 1.875, -.35] : center));
  return faces;
})();
function house3D(cx, cy, scale, rotY, o = {}) {
  const { mat = 1, holo = 0, pitch = .32, alpha = 1, gray = 0, holoColor = CYAN, seed = 500 } = o;
  if (alpha <= 0) return;
  const D = 6, f = scale;
  const cp = Math.cos(pitch), sp = Math.sin(pitch), cr = Math.cos(rotY), sr = Math.sin(rotY);
  const tr = p => {
    let x = p[0] * cr + p[2] * sr, z = -p[0] * sr + p[2] * cr, y = p[1] - .8;
    const y2 = y * cp - z * sp, z2 = y * sp + z * cp;
    return [x, y2, z2];
  };
  const proj = q => [cx + q[0] * f / (D - q[2]) * D, cy - q[1] * f / (D - q[2]) * D];
  const camVis = (pts3) => {
    const P = pts3.map(proj);
    let a = 0; for (let i = 0; i < P.length; i++) { const p = P[i], q = P[(i + 1) % P.length]; a += p[0] * q[1] - q[0] * p[1]; }
    return a < 0;
  };
  g.save(); g.globalAlpha *= alpha;
  // pedestal rings
  const base = proj(tr([0, -.02, 0]));
  for (let i = 0; i < 3; i++) {
    g.save(); g.strokeStyle = rgba(holoColor, .55 - i * .15); g.lineWidth = 4 - i; g.shadowColor = holoColor; g.shadowBlur = 20;
    g.setLineDash([30 + i * 10, 18]); g.lineDashOffset = -T * 80 * (i % 2 ? -1 : 1);
    g.beginPath(); g.ellipse(base[0], base[1] + 10, f * (1.45 + i * .22), f * (.42 + i * .07), 0, 0, 7); g.stroke(); g.restore();
  }
  const list = HOUSE.map((fc, i) => {
    const q = fc.pts.map(tr);
    const z = q.reduce((s, p) => s + p[2], 0) / q.length;
    return { fc, q, z, i };
  }).filter(o2 => camVis(o2.q)).sort((a, b) => a.z - b.z);
  const drawFace = (fc, q, sd) => {
    const P = q.map(proj);
    if (mat > 0) {
      g.save(); g.globalAlpha *= mat;
      let col = fc.color;
      if (gray > 0) col = mixGray(col, gray);
      rc.polygon(P, R(sd, { fill: col, fillStyle: 'solid', strokeWidth: 3 }));
      if (fc.hatch) rc.polygon(P, R(sd + 1, { fill: gray > 0 ? mixGray(fc.hatch, gray) : fc.hatch, fillStyle: 'hachure', stroke: 'none', hachureGap: 12, hachureAngle: 40 + sd % 50 }));
      g.restore();
    }
    if (holo > 0) {
      g.save(); g.globalAlpha *= holo * flicker(sd);
      g.fillStyle = rgba(holoColor, .12 * (1 - mat)); g.beginPath(); P.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.closePath(); g.fill();
      glowLine([...P, P[0]], holoColor, 3, 22);
      g.restore();
    }
  };
  list.forEach(({ fc, q, i }) => {
    drawFace(fc, q, seed + i * 7);
    fc.kids.forEach((k, j) => drawFace(k, k.pts.map(tr), seed + i * 7 + 100 + j * 3));
  });
  g.restore();
}
function mixGray(hex, a) {
  const n = parseInt(hex.slice(1), 16), r = n >> 16 & 255, gg = n >> 8 & 255, b = n & 255, l = (r * .3 + gg * .59 + b * .11);
  return `rgb(${lerp(r, l * .8 + 40, a) | 0},${lerp(gg, l * .7 + 10, a) | 0},${lerp(b, l * .7 + 20, a) | 0})`;
}

// --- particles
function confetti(t0, n, cx, cy, spread = 2.4, seed = 1) {
  const a = T - t0; if (a < 0 || a > 4) return;
  const cols = [YEL, RED, CYAN, GREEN, '#ff7ad9', '#fff', GOLD];
  for (let i = 0; i < n; i++) {
    const ang = -Math.PI / 2 + (rnd(seed + i) - .5) * spread, sp = 1100 + 1300 * rnd(seed + i + 77), k = 2.2;
    const x = cx + Math.cos(ang) * sp * (1 - Math.exp(-k * a)) / k + Math.sin(a * 3 + i) * 30 * a;
    const y = cy + Math.sin(ang) * sp * (1 - Math.exp(-k * a)) / k + 260 * a * a;
    const rot = a * (4 + 8 * rnd(seed + i + 9)) + i, s = 12 + 16 * rnd(seed + i + 3);
    g.save(); g.globalAlpha = clamp(4 - a); g.translate(x, y); g.rotate(rot); g.scale(1, Math.abs(Math.cos(a * 6 + i)));
    g.fillStyle = cols[i % cols.length]; g.fillRect(-s / 2, -s / 4, s, s / 2); g.restore();
  }
}
function coins(t0, n, cx, cy, seed = 3) {
  const a = T - t0; if (a < 0 || a > 2.2) return;
  for (let i = 0; i < n; i++) {
    const ang = -Math.PI / 2 + (rnd(seed + i) - .5) * 2.6, sp = 700 + 700 * rnd(seed + i + 5);
    const x = cx + Math.cos(ang) * sp * a, y = cy + Math.sin(ang) * sp * a + 900 * a * a;
    g.save(); g.globalAlpha = clamp(2.2 - a); g.translate(x, y); g.scale(Math.cos(a * 9 + i), 1);
    g.fillStyle = GOLD; g.strokeStyle = '#a0701a'; g.lineWidth = 4; g.beginPath(); g.arc(0, 0, 24, 0, 7); g.fill(); g.stroke();
    g.fillStyle = '#a0701a'; g.font = `800 20px ${F_BOLD}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('RM', 0, 1);
    g.restore();
  }
}
function flyingDigits(t0, t1, cx, cy, seed = 1) {
  const chars = ['0', '1', '2', '5', '×', '12', '10', 'RM', '%', '+', '=', '3', '0', '7'];
  for (let i = 0; i < 110; i++) {
    const tb = t0 + i * (t1 - t0) / 110, a = T - tb, life = 1.5;
    if (a < 0 || a > life) continue;
    const ang = rnd(seed + i) * Math.PI * 2, sp = 300 + 500 * rnd(seed + i + 3), p = a / life;
    const x = cx + Math.cos(ang) * sp * a * (1 + p), y = cy + Math.sin(ang) * sp * a * .8 * (1 + p);
    const size = 24 + 70 * p * p * (0.5 + rnd(seed + i + 5));
    const col = i % 4 === 0 ? YEL : CYAN;
    text(chars[i % chars.length], x, y, { font: F_HOLO, size, weight: 900, color: col, glow: col, blur: 18, alpha: Math.sin(p * Math.PI) * .9 });
  }
}
function holoTimer(x, y, r, val, prog, a = 1) {
  if (a <= 0) return;
  g.save(); g.globalAlpha *= a * flicker(77);
  g.strokeStyle = rgba(CYAN, .25); g.lineWidth = r * .14; g.beginPath(); g.arc(x, y, r, 0, 7); g.stroke();
  g.strokeStyle = CYAN; g.shadowColor = CYAN; g.shadowBlur = 26; g.lineCap = 'round';
  g.beginPath(); g.arc(x, y, r, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * prog); g.stroke();
  for (let i = 0; i < 12; i++) {
    const an = i / 12 * Math.PI * 2; g.lineWidth = 3;
    g.beginPath(); g.moveTo(x + Math.cos(an) * r * 1.18, y + Math.sin(an) * r * 1.18); g.lineTo(x + Math.cos(an) * r * 1.28, y + Math.sin(an) * r * 1.28); g.stroke();
  }
  g.restore();
  holoText(String(val), x, y - r * .08, r * .82, { k: 78, alpha: a });
  holoText('SAAT', x, y + r * .5, r * .22, { k: 79, alpha: a, weight: 700 });
}
function redLights(I) {
  if (I <= 0) return;
  g.save(); g.globalCompositeOperation = 'lighter';
  [[0, 0, 0], [W, 0, Math.PI]].forEach(([x, y, ph]) => {
    const p = .5 + .5 * Math.sin(T * 9 + ph);
    const gr = g.createRadialGradient(x, y, 20, x, y, 1100);
    gr.addColorStop(0, `rgba(255,30,50,${.55 * I * p})`); gr.addColorStop(1, 'rgba(255,0,30,0)');
    g.fillStyle = gr; g.fillRect(0, 0, W, H);
  });
  g.restore();
  const v = g.createRadialGradient(540, 960, 500, 540, 960, 1200);
  v.addColorStop(0, 'rgba(255,0,30,0)'); v.addColorStop(1, `rgba(255,0,30,${.45 * I * (.6 + .4 * Math.sin(T * 9))})`);
  g.fillStyle = v; g.fillRect(0, 0, W, H);
}
function siren(x, y, s, I) {
  if (I <= 0) return;
  g.save(); g.globalAlpha *= clamp(I * 2);
  const a = T * 7;
  g.save(); g.globalCompositeOperation = 'lighter';
  [a, a + Math.PI].forEach(an => {
    const gr = g.createRadialGradient(x, y, 10, x, y, 520);
    gr.addColorStop(0, 'rgba(255,40,60,.55)'); gr.addColorStop(1, 'rgba(255,40,60,0)');
    g.fillStyle = gr; g.beginPath(); g.moveTo(x, y); g.arc(x, y, 520, an - .28, an + .28); g.closePath(); g.fill();
  });
  g.restore();
  rc.rectangle(x - 60 * s, y + 30 * s, 120 * s, 28 * s, S(800, '#444'));
  rc.path(`M ${x - 46 * s} ${y + 32 * s} Q ${x - 46 * s} ${y - 54 * s} ${x} ${y - 56 * s} Q ${x + 46 * s} ${y - 54 * s} ${x + 46 * s} ${y + 32 * s} Z`, S(801, '#ff2a40'));
  g.fillStyle = 'rgba(255,255,255,.7)'; g.beginPath(); g.ellipse(x - 18 * s, y - 18 * s, 8 * s, 18 * s, .3, 0, 7); g.fill();
  g.restore();
}

// ---------------------------------------------------------------- camera / fx
const SHAKES = [[0.36, 34, .7], [26.42, 30, .8], [35.12, 18, .4], [38.86, 10, .3]];
const FLASHES = [[0.36, .35, '#fff'], [10.6, .25, CYAN], [16.74, .2, '#fff'], [20.1, .2, CYAN], [26.42, .35, '#fff'], [35.4, .3, '#ff2040'], [51.3, .25, '#fff']];
const GLITCHES = [1.45, 10.6, 20.1, 51.3];
function shake() {
  let x = 0, y = 0;
  SHAKES.forEach(([t0, amp, d]) => {
    const a = T - t0; if (a < 0 || a > d) return;
    const k = amp * Math.pow(1 - a / d, 2);
    x += k * Math.sin(a * 83); y += k * Math.cos(a * 71);
  });
  return [x, y];
}
function setCam(z, cx, cy) {
  const [sx, sy] = shake();
  g.setTransform(z, 0, 0, z, W / 2 - cx * z + sx, H / 2 - cy * z + sy);
}

// ---------------------------------------------------------------- scenes
function scene1() {
  // 0 – 10.6  Hook: payslip, dream house, shocked face
  background(0);
  const zIn = E.io(inv(0, .38, T));
  const z = lerp(2.5, 1, zIn) * (1 + .05 * inv(.4, 10.6, T)) * (1 + .06 * E.out(inv(3.1, 3.4, T)) * (1 - inv(3.4, 7, T)));
  const fx = 330, fy = 1330, s = .86;
  const slipX = fx, slipY = fy - s * 470;
  setCam(z, lerp(slipX, 540, zIn), lerp(slipY, 960, zIn));
  // house + glow
  const hg = g.createRadialGradient(720, 520, 40, 720, 520, 420);
  hg.addColorStop(0, 'rgba(255,220,120,.35)'); hg.addColorStop(1, 'rgba(255,220,120,0)');
  g.fillStyle = hg; g.fillRect(250, 100, 940, 900);
  house2D(720, 760, .95);
  text('Rumah Idaman', 720, 830, { font: F_HAND, size: 52, weight: 400, color: '#fff', stroke: INK, sw: 8 });
  sparkles(720, 560, 300, 220, 10, 11);
  // hologram price tag above house
  const pa = vis(1.4, 7.4);
  if (pa > 0) {
    holoPanel(560, 220, 320, 120, { alpha: pa, k: 3 });
    const q = Math.floor(T * 12) % 2 ? 'RM ???' : 'RM ? ? ?';
    holoText(T > 2.2 ? q : 'HARGA', 720, 282, 52, { alpha: pa, k: 4 });
  }
  // shock wave at BOOM
  const sw = inv(.36, 1.1, T);
  if (sw > 0 && sw < 1) {
    g.save(); g.strokeStyle = rgba('#ffffff', 1 - sw); g.lineWidth = 18 * (1 - sw);
    g.beginPath(); g.arc(slipX, slipY, 80 + 900 * E.out(sw), 0, 7); g.stroke(); g.restore();
  }
  if (T > .36 && T < 1.4) burst(slipX, slipY, 170, 260, 14, YEL, T * .5, 3);
  const shocked = T < 7.3;
  drawMan(fx, fy, s, {
    expr: shocked ? 'shock' : 'smile', talk: shocked ? 0 : talk(), lookX: shocked ? .9 : .4, lookY: shocked ? -.6 : 0,
    l: [-140, -470], r: [140, -470], bl: -1, br: 1, hl: 'fist', hr: 'fist',
    hold: () => payslip(0, -470 + Math.sin(T * 14) * (shocked ? 3 : 0), 300, 210, -.04, { stamp: inv(5.1, 5.35, T) * (1 - inv(7.2, 7.5, T)) }),
  });
  // comic "!" and question marks
  const ex = vis(.4, 2.8, .1, .2);
  if (ex > 0) text('!', fx + 120, fy - s * 900, { size: 150, color: YEL, stroke: INK, sw: 12, scale: pop(.4), alpha: ex, rot: .15 });
  [[3.15, -150, -880, -.3], [3.5, 150, -930, .25], [3.85, -30, -990, 0]].forEach(([t0, dx, dy, r], i) => {
    const a = vis(t0, 7.3, .1, .3);
    if (a > 0) text('?', fx + dx * s, fy + dy * s + Math.sin(T * 4 + i) * 8, { size: 110, color: i === 1 ? CYAN : '#fff', stroke: INK, sw: 10, scale: pop(t0), alpha: a, rot: r });
  });
  // 10 saat timer pops in
  const ta = vis(7.76, 10.7, .1, .05);
  if (ta > 0) holoTimer(lerp(250, 930, E.io(inv(10.2, 10.6, T))), lerp(360, 170, E.io(inv(10.2, 10.6, T))), lerp(130, 80, E.io(inv(10.2, 10.6, T))) * pop(7.76), 10, 1, ta);
  // speed lines during the zoom
  if (T < .45) {
    g.setTransform(1, 0, 0, 1, 0, 0);
    for (let i = 0; i < 40; i++) {
      const an = rnd(i) * Math.PI * 2, r0 = 200 + 300 * rnd(i + 4);
      g.strokeStyle = `rgba(255,255,255,${.5 * (1 - T / .45)})`; g.lineWidth = 3 + 4 * rnd(i + 9);
      g.beginPath(); g.moveTo(540 + Math.cos(an) * r0, 960 + Math.sin(an) * r0); g.lineTo(540 + Math.cos(an) * 1400, 960 + Math.sin(an) * 1400); g.stroke();
    }
  }
}

function calcKey(x, y, w, h, label, pressT, k) {
  const pr = pressT.reduce((m, t0) => Math.max(m, 1 - inv(t0, t0 + .22, T) - (T < t0 ? 1 : 0)), 0);
  const s = 1 - .08 * pr;
  g.save(); g.translate(x + w / 2, y + h / 2); g.scale(s, s);
  g.fillStyle = rgba(pr > 0 ? YEL : CYAN, .08 + .4 * pr); rrect(-w / 2, -h / 2, w, h, 16); g.fill();
  g.shadowColor = pr > 0 ? YEL : CYAN; g.shadowBlur = 12 + 24 * pr;
  rc.rectangle(-w / 2, -h / 2, w, h, R(600 + k, { stroke: pr > 0 ? YEL : rgba(CYAN, .85), strokeWidth: 2.5, roughness: .9 }));
  g.restore();
  holoText(label, x + w / 2, y + h / 2 + 2, 44, { color: pr > 0 ? YEL : CYAN, k: 600 + k, scale: s });
}
function scene2() {
  // 10.6 – 20.1  Hologram calculator: GAJI x 12 x 10
  background(0);
  setCam(1 + .03 * inv(10.6, 20.1, T), 540, 960);
  const px = 70, py = 210, pw = 620, ph = 900;
  const m = E.out(inv(10.6, 11.15, T));
  g.save(); g.translate(px + pw / 2, py + ph / 2); g.scale(1, Math.max(.02, m)); g.translate(-px - pw / 2, -py - ph / 2);
  holoPanel(px, py, pw, ph, { k: 1 });
  holoText('HOLO-KALKULATOR', px + pw / 2, py + 42, 26, { weight: 700, k: 2, spacing: 4 });
  const dx = px + 30, dy = py + 75, dw = pw - 60, dh = 330;
  g.fillStyle = 'rgba(0,20,40,.55)'; rrect(dx, dy, dw, dh, 18); g.fill();
  glowLine([[dx, dy + dh], [dx + dw, dy + dh]], CYAN, 2, 12, .6);
  // formula rows
  const rows = [
    [12.96, 'GAJI KASAR', CYAN, 'type'],
    [14.62, '× 12', CYAN, 'pop'],
    [15.82, '× 10', CYAN, 'pop'],
    [16.74, '= HARGA RUMAH', YEL, 'pop'],
  ];
  rows.forEach(([t0, str, col, mode], i) => {
    if (T < t0) return;
    let s2 = str;
    if (mode === 'type') s2 = str.slice(0, Math.ceil(clamp((T - t0) / .4) * str.length));
    const y = dy + 52 + i * 76, sc = mode === 'pop' ? pop(t0, T, .3) : 1;
    holoText(s2, dx + dw - 24, y, i === 3 ? 46 : 60, { color: col, align: 'right', k: 10 + i, scale: sc });
  });
  if (T > 16.74) checkMark(dx + 46, dy + 52 + 3 * 76, 46, GREEN, fadeIn(16.9));
  // keypad
  const keys = [['7', '8', '9', '÷'], ['4', '5', '6', '×'], ['1', '2', '3', '-'], ['C', '0', '=', '+']];
  const press = { '×': [14.28, 15.54], '1': [14.62, 15.85], '2': [14.76], '0': [16.0], '=': [16.74], 'C': [12.7] };
  const kx = px + 34, ky = py + 440, kw = (pw - 68 - 3 * 18) / 4, kh = 86;
  keys.forEach((row, r) => row.forEach((lab, c) => calcKey(kx + c * (kw + 18), ky + r * (kh + 18), kw, kh, lab, press[lab] || [], r * 4 + c)));
  g.restore();
  if (m < 1) glowLine([[px - 20, py + ph / 2], [px + pw + 20, py + ph / 2]], '#fff', 6, 30, 1 - m);
  // success flash on display
  const sf = vis(16.74, 18.2, .05, .6);
  if (sf > 0) { g.save(); g.globalAlpha = sf * .25; g.fillStyle = YEL; rrect(dx, dy, dw, dh, 18); g.fill(); g.restore(); }
  if (T > 17.3) scribbleCircle(dx + dw / 2, dy + 52 + 3 * 76, dw / 2 + 10, 50, E.out(inv(17.3, 17.8, T)), YEL, 21, 5);
  flyingDigits(12.7, 19.6, px + pw / 2, dy + dh / 2, 5);
  // presenter
  drawMan(880, 1330, .62, {
    expr: T > 16.74 ? 'happy' : 'smile', talk: talk(), lookX: -1, lookY: -.4, blush: T > 16.74,
    l: [-300, -720 + Math.sin(T * 3) * 10], bl: 1, hl: 'point', r: [120, -360], hr: 'fist',
  });
  holoText('FORMULA 10 SAAT', 70, 120, 44, { align: 'left', k: 9, color: YEL, alpha: fadeIn(10.7) });
  // countdown timer
  const left = Math.max(0, Math.ceil(10 - (T - 10.6) / .95));
  holoTimer(930, 170, 80, left, 1 - clamp((T - 10.6) / 9.5), 1 - inv(19.9, 20.1, T));
}

function scene3(tt = T) {
  // 20.1 – 35.1  RM2,500 -> RM30,000 -> RM300,000, 3D house rises
  const Tsave = T; T = tt;
  background(0);
  setCam(1 + .04 * E.out(inv(26.42, 27, T)) - .04 * inv(27, 35, T) * 0, 540, 960);
  // number panel
  const pa = E.out(inv(20.1, 20.5, T));
  const PY = 200;
  holoPanel(90, PY, 900, 340, { alpha: pa, k: 31 });
  const label = T < 23.9 ? 'GAJI KASAR SEBULAN' : T < 26.42 ? 'SETAHUN (× 12)' : 'ANGGARAN HARGA RUMAH';
  holoText(label, 540, PY + 55, 32, { weight: 700, k: 32, alpha: pa, spacing: 3, color: T >= 26.42 ? YEL : CYAN });
  let val = 0;
  if (T >= 20.8) val = 2500 * E.out(inv(20.8, 21.4, T));
  if (T >= 23.96) val = lerp(2500, 30000, E.out(inv(23.96, 24.4, T)));
  if (T >= 26.42) val = lerp(30000, 300000, E.out(inv(26.42, 26.75, T)));
  const step = T > 26.42 ? 1000 : T > 23.96 ? 100 : 10;
  const vs = 'RM' + (Math.round(val / step) * step).toLocaleString('en-US');
  const punch = 1 + .15 * (1 - inv(23.96, 24.3, T)) * (T > 23.96 ? 1 : 0) + .12 * (1 - inv(26.42, 26.9, T)) * (T > 26.42 ? 1 : 0);
  if (T >= 20.8) holoText(vs, 540, PY + 190, 120, { color: T >= 26.42 ? YEL : '#fff', k: 33, scale: punch * pop(20.8) });
  // hand-drawn formula strip (sticky notes) under the panel
  const fa = fadeIn(20.5, .3) * (1 - inv(26.5, 26.8, T));
  if (fa > 0) {
    const toks = [['RM2,500', 21.38, 250], ['× 12', 23.32, 175], ['× 10', 25.5, 175], ['=', 26.42, 70], [T >= 26.42 ? 'RM300K' : '?', 26.42, 220]];
    const gap = 18, tw = toks.reduce((m, t2) => m + t2[2], 0) + gap * (toks.length - 1);
    let x = 540 - tw / 2;
    g.save(); g.globalAlpha *= fa;
    toks.forEach(([str, t0, w], i) => {
      const on = T >= t0, cx = x + w / 2, cy = 690 + Math.sin(T * 3 + i) * 5;
      const sc = on ? 1 + .15 * (1 - inv(t0, t0 + .3, T)) : 1;
      g.save(); g.translate(cx, cy); g.rotate((i % 2 ? .04 : -.04)); g.scale(sc, sc);
      if (str !== '=') rc.rectangle(-w / 2, -50, w, 100, S(1500 + i, on ? (i === 4 ? YEL : PAPER) : '#9aa3c7', { strokeWidth: 3.5 }));
      text(str, 0, 4, { font: F_HAND, size: 62, weight: 400, color: str === '=' ? '#fff' : INK });
      g.restore();
      x += w + gap;
    });
    g.restore();
  }
  // multiplier chips
  [[23.2, 23.96, '× 12'], [25.3, 26.42, '× 10']].forEach(([t0, t1, s], i) => {
    if (T < t0 || T > t1 + .3) return;
    const fly = E.out(inv(t0, t0 + .35, T)), merge = E.in(inv(t1 - .1, t1 + .2, T));
    const x = lerp(1250, 540, fly), y = lerp(620, 380, merge);
    g.save(); g.globalAlpha = 1 - merge;
    holoPanel(x - 130, y - 62, 260, 124, { color: YEL, k: 40 + i, r: 60 });
    holoText(s, x, y + 4, 76, { color: YEL, k: 42 + i });
    g.restore();
  });
  coins(23.98, 16, 540, 380, 7);
  // house rises
  const rise = E.out(inv(26.6, 28.3, T)), mat = E.io(inv(27.6, 28.8, T));
  if (T > 26.5) {
    const y = lerp(1900, 1030, rise);
    house3D(620, y, 210, -.6 + Math.sin(T * .45) * .5 + (T - 26.5) * .25, { mat, holo: 1 - mat * .75, alpha: 1 });
    // scan beam while materialising
    if (mat > 0 && mat < 1) glowLine([[300, lerp(1100, 560, mat)], [940, lerp(1100, 560, mat)]], CYAN, 6, 30, 1 - Math.abs(mat - .5) * 1.6);
    sparkles(620, 820, 330, 260, 12, 17, mat);
  }
  confetti(26.42, 140, 540, 420, 2.8, 11);
  // annotations
  if (T > 31.68) scribbleCircle(540, PY + 190, 430, 100, E.out(inv(31.68, 32.2, T)), RED, 33, 7);
  if (T > 32.9) {
    handArrow(250, 560, 360, 760, E.out(inv(32.9, 33.3, T)), '#fff', 44, 6);
    text('Angka permulaan!', 330, 600, { font: F_HAND, size: 50, weight: 400, color: YEL, stroke: INK, sw: 8, rot: -.08, scale: pop(33.2), align: 'center' });
  }
  // the man
  const cele = T > 26.42 && T < 28.8;
  const up = Math.sin(T * 10) * 18;
  drawMan(220, 1330, .58, {
    expr: T < 26.42 ? 'smile' : cele ? 'shock' : 'happy', talk: cele ? 0 : talk(), lookX: .6, lookY: -.5, blush: T > 26.42,
    l: cele ? [-200, -800 + up] : [-140, -380], r: cele ? [200, -800 - up] : (T > 28.8 ? [210, -560] : [140, -380]),
    bl: cele ? -1 : 1, br: cele ? 1 : -1, hl: cele ? 'open' : 'fist', hr: cele ? 'open' : (T > 28.8 ? 'thumb' : 'fist'),
  });
  T = Tsave;
}

function iconCard(i, x, y, w, h, t0, title, drawIcon) {
  const s = E.back(inv(t0, t0 + .4, T)) * (1 - E.in(inv(45.95, 46.35, T)));
  if (s <= 0.001) return;
  g.save(); g.translate(x + w / 2, y + h / 2); g.scale(s, s); g.rotate((1 - s) * .4 + (i % 2 ? .02 : -.02)); g.translate(-x - w / 2, -y - h / 2);
  holoPanel(x, y, w, h, { color: '#ff4a5e', k: 90 + i, fill: .14 });
  drawIcon(x + w / 2, y + h * .43);
  text(title, x + w / 2, y + h - 46, { size: 40, color: '#fff', stroke: INK, sw: 8 });
  rc.circle(x + w - 26, y + 26, 54, S(900 + i, RED, { strokeWidth: 3 }));
  text('!', x + w - 26, y + 30, { size: 42, color: '#fff' });
  g.restore();
}
function scene4() {
  // 35.1 – 51.3  Bank officer warning, commitments, then reassurance
  const red = Math.min(1, inv(35.1, 35.4, T)) * (1 - inv(45.9, 46.5, T));
  background(red);
  setCam(1, 540, 960);
  const I = (T < 37 ? 1 : .5) * red;
  siren(540, 120, 1, red);
  // frozen, grey house with the number
  const ha = vis(35.1, 40.2, .1, .4);
  if (ha > 0) {
    house3D(300, 820, 120, .35, { mat: 1, holo: .4, gray: .75, holoColor: '#ff4a5e', alpha: ha });
    holoText('RM300,000', 300, 470, 64, { color: '#ffb3bb', alpha: ha, k: 51 });
    if (T > 38.86) {
      const st = inv(38.86, 39.05, T), sc = 1 + 1.4 * (1 - E.out(st));
      g.save(); g.globalAlpha = ha * clamp(st * 2); g.translate(300, 560); g.rotate(-.18); g.scale(sc, sc);
      rc.rectangle(-200, -45, 400, 90, R(951, { stroke: '#ff2a40', strokeWidth: 7 }));
      text('BELUM TENTU LULUS', 0, 3, { size: 42, color: '#ff2a40' });
      g.restore();
    }
  }
  // officer: enters, raises card, then moves to centre and points at the icons
  const enter = E.out(inv(35.5, 36.2, T)), mv = E.io(inv(39.9, 40.5, T)), mv2 = E.io(inv(45.95, 46.6, T));
  let ox = lerp(1350, 720, enter), os = .82;
  ox = lerp(ox, 540, mv); os = lerp(os, .6, mv);
  ox = lerp(ox, 800, mv2); os = lerp(os, .7, mv2);
  const card = E.back(inv(36.4, 36.8, T)) * (1 - inv(39.9, 40.2, T));
  const wag = Math.sin(T * 12) * 40;
  const happy = T > 45.95;
  drawOfficer(ox, 1330, os, {
    expr: happy ? 'happy' : 'stern', lookX: happy ? -.6 : -.8, blush: happy,
    r: card > 0 ? [lerp(150, 170, card), lerp(-380, -800, card)] : (happy ? [240, -560] : [150, -380]), br: card > 0 || happy ? 1 : -1, hr: happy ? 'thumb' : 'fist',
    l: happy ? [-150, -380] : T > 40.2 ? [-250, -860] : [-260, -620 + wag], bl: happy ? 1 : -1, hl: happy ? 'fist' : 'point',
    hold: (L, Rr) => {
      if (card <= 0) return;
      g.save(); g.translate(Rr.x, Rr.y - 150); g.rotate(.08 + Math.sin(T * 5) * .03); g.scale(card, card);
      rc.rectangle(-190, -150, 380, 280, S(960, '#e8283c', { strokeWidth: 5 }));
      rc.rectangle(-172, -132, 344, 244, R(961, { stroke: '#fff', strokeWidth: 4 }));
      warnTriangle(-110, -50, 110, 962);
      text('AMARAN', 60, -60, { size: 52, color: '#fff' });
      text('RM300K', 0, 30, { size: 66, color: YEL });
      notEqual(-110, 92, 58, '#fff', 1, false);
      text('LULUS', 40, 96, { size: 56, color: '#fff' });
      g.restore();
    },
  });
  // commitment icons
  const cw = 420, chh = 330, x1 = 90, x2 = 570, y1 = 190, y2 = 545;
  iconCard(0, x1, y1, cw, chh, 41.86, 'Hutang Kereta', (cx, cy) => {
    rc.path(`M ${cx - 150} ${cy + 30} L ${cx - 140} ${cy - 10} L ${cx - 80} ${cy - 20} L ${cx - 40} ${cy - 70} L ${cx + 60} ${cy - 70} L ${cx + 110} ${cy - 20} L ${cx + 150} ${cy - 10} L ${cx + 155} ${cy + 30} Z`, S(970, '#4cc9f0', { strokeWidth: 4 }));
    rc.polygon([[cx - 30, cy - 58], [cx + 55, cy - 58], [cx + 90, cy - 22], [cx - 60, cy - 22]], S(971, '#cdf3ff', { strokeWidth: 3 }));
    [cx - 85, cx + 90].forEach((wx, k) => { rc.circle(wx, cy + 32, 66, S(972 + k, '#222', { strokeWidth: 4 })); rc.circle(wx, cy + 32, 26, S(974 + k, '#bbb')); });
  });
  iconCard(1, x2, y1, cw, chh, 42.34, 'Hutang / Kad Kredit', (cx, cy) => {
    g.save(); g.translate(cx, cy); g.rotate(-.12);
    rc.rectangle(-140, -85, 280, 175, S(980, '#7b61ff', { strokeWidth: 4 }));
    rc.rectangle(-140, -50, 280, 34, S(981, '#222', { strokeWidth: 2 }));
    rc.rectangle(-110, 4, 54, 40, S(982, GOLD, { strokeWidth: 3 }));
    text('**** 2500', 40, 60, { font: F_HOLO, size: 24, weight: 700, color: '#fff' });
    g.restore();
  });
  iconCard(2, x1, y2, cw, chh, 42.92, 'DSR (Nisbah Hutang)', (cx, cy) => {
    const r = 120, yy = cy + 50;
    [[GREEN, Math.PI, Math.PI * 1.4], [YEL, Math.PI * 1.4, Math.PI * 1.7], [RED, Math.PI * 1.7, Math.PI * 2]].forEach(([c, a0, a1]) => {
      g.save(); g.strokeStyle = c; g.lineWidth = 30; g.shadowColor = c; g.shadowBlur = 12;
      g.beginPath(); g.arc(cx, yy, r, a0, a1); g.stroke(); g.restore();
    });
    const nv = clamp((T - 42.92) / .9), na = Math.PI * (1.05 + .85 * E.el(nv)) + Math.sin(T * 18) * .02;
    rc.line(cx, yy, cx + Math.cos(na) * (r - 20), yy + Math.sin(na) * (r - 20), R(990, { strokeWidth: 8, stroke: '#fff' }));
    rc.circle(cx, yy, 30, S(991, '#fff'));
  });
  iconCard(3, x2, y2, cw, chh, 43.7, 'Bayaran Bulanan', (cx, cy) => {
    rc.rectangle(cx - 120, cy - 90, 240, 190, S(995, '#fff', { strokeWidth: 4 }));
    rc.rectangle(cx - 120, cy - 90, 240, 46, S(996, RED, { strokeWidth: 4 }));
    for (let r = 0; r < 3; r++) for (let c = 0; c < 5; c++) { g.fillStyle = '#c7cbe0'; g.fillRect(cx - 100 + c * 42, cy - 28 + r * 38, 26, 24); }
    rc.circle(cx + 110, cy + 80, 90, S(997, GOLD, { strokeWidth: 4 }));
    text('RM', cx + 110, cy + 83, { size: 36, color: '#7a5210' });
  });
  // reassurance: GAJI KECIL ≠ TAK MAMPU
  if (T > 45.95) {
    const a = fadeIn(46.0, .3);
    house3D(540, 420, 90, T * .8, { mat: 1, holo: .35, alpha: a * (1 - inv(48.4, 48.7, T)) });
    if (T > 48.6) holoText('GAJI KECIL', 540, 300, 96, { color: '#fff', k: 61, scale: pop(48.6) });
    if (T > 49.4) {
      text('TAK MAMPU?', 540, 440, { size: 100, color: '#ff5a6a', stroke: INK, sw: 12, scale: pop(49.4), rot: -.03 });
      const sp = E.out(inv(50.0, 50.3, T));
      if (sp > 0) {
        g.save(); g.shadowColor = RED; g.shadowBlur = 12;
        rc.line(270, 470, lerp(270, 820, sp), lerp(470, 400, sp), R(1001, { stroke: '#ff1f3a', strokeWidth: 14 }));
        rc.line(280, 420, lerp(280, 810, sp), lerp(420, 470, sp), R(1002, { stroke: '#ff1f3a', strokeWidth: 10 }));
        g.restore();
      }
    }
    if (T > 50.5) {
      holoText('BOLEH BELI RUMAH!', 540, 590, 66, { color: GREEN, k: 62, scale: pop(50.5) });
      sparkles(540, 590, 420, 80, 10, 63);
    }
    // man comes back, confident
    const me = E.out(inv(46.0, 46.6, T));
    drawMan(lerp(-300, 300, me), 1330, .7, {
      expr: 'happy', talk: talk(), lookX: .5, blush: true,
      l: [-150, -380], r: [240, -560 + Math.sin(T * 6) * 10], br: 1, hr: 'thumb',
    });
  }
  redLights(I);
}

function cta(x, y, w, h, a) {
  if (a <= 0) return;
  const beat = (T - 54.6) / .9, ph = beat - Math.floor(beat);
  const s = pop(54.5, T, .45) * (1 + .06 * Math.pow(Math.max(0, Math.cos(ph * Math.PI * 2)), 4));
  // expanding ring
  g.save(); g.globalAlpha = a * (1 - ph) * .8; g.strokeStyle = YEL; g.lineWidth = 6; g.shadowColor = YEL; g.shadowBlur = 20;
  rrect(x - w / 2 - ph * 40, y - h / 2 - ph * 40, w + ph * 80, h + ph * 80, 60); g.stroke(); g.restore();
  g.save(); g.globalAlpha *= a; g.translate(x, y); g.scale(s, s);
  g.shadowColor = 'rgba(255,170,30,.8)'; g.shadowBlur = 40;
  const gr = g.createLinearGradient(0, -h / 2, 0, h / 2); gr.addColorStop(0, '#ffcf3f'); gr.addColorStop(1, '#ff8a00');
  rrect(-w / 2, -h / 2, w, h, 56); g.fillStyle = gr; g.fill(); g.shadowBlur = 0;
  rc.rectangle(-w / 2 + 4, -h / 2 + 4, w - 8, h - 8, R(1100, { strokeWidth: 5 }));
  text('SEMAK KELAYAKAN', 0, -26, { size: 58, color: '#fff', stroke: INK, sw: 10 });
  text('PERCUMA!', 0, 42, { size: 70, color: '#fff', stroke: INK, sw: 10 });
  g.restore();
}
function logo(x, y, s, a) {
  if (a <= 0) return;
  g.save(); g.globalAlpha *= a; g.translate(x, y); g.scale(s, s);
  g.save(); g.shadowColor = GOLD; g.shadowBlur = 30;
  rc.linearPath([[-250, 0], [-190, -62], [-130, 0]], R(1200, { stroke: GOLD, strokeWidth: 12 }));
  rc.rectangle(-232, -10, 84, 58, R(1201, { stroke: GOLD, strokeWidth: 9 }));
  rc.rectangle(-162, -66, 16, 34, R(1202, { stroke: GOLD, strokeWidth: 6 }));
  g.restore();
  text('NAZ', -100, -4, { size: 112, color: GOLD, align: 'left', glow: GOLD, blur: 20, stroke: INK, sw: 10 });
  holoText('PROPERTY', 50, 66, 40, { align: 'center', k: 120, spacing: 12, color: '#fff' });
  g.restore();
}
function scene5() {
  // 51.3 – 64  CTA: point to comments/form, rotating house, logo
  background(0);
  setCam(1, 540, 960);
  const la = E.back(inv(51.65, 52.2, T));
  logo(560, 220, la * 1.12, clamp(la * 1.5));
  if (T > 51.65) sparkles(560, 230, 300, 70, 6, 71, 1);
  const ha = E.out(inv(51.4, 52.0, T));
  house3D(560, 615, 140, T * .8, { mat: 1, holo: .4, alpha: ha, pitch: .3 });
  // badges
  [[60.98, 'LPPSA', 380], [61.94, 'BANK', 620], [62.72, 'PENIAGA', 860]].forEach(([t0, s, x], i) => {
    if (T < t0) return;
    const sc = pop(t0);
    holoPanel(x - 110, 862, 220, 76, { k: 130 + i, r: 38, alpha: 1 });
    holoText(s, x, 900, 40, { k: 133 + i, scale: sc, color: i === 0 ? YEL : CYAN });
  });
  cta(620, 1070, 680, 190, fadeIn(54.5, .15));
  // sub pills
  [[55.3, 'Isi borang di bawah', 430], [57.9, 'atau klik link di bio', 800]].forEach(([t0, s, x], i) => {
    if (T < t0) return;
    const sc = pop(t0);
    g.save(); g.translate(x, 1222); g.scale(sc, sc);
    rc.rectangle(-178, -36, 356, 72, S(1300 + i, i ? '#ffffff' : YEL, { strokeWidth: 3 }));
    text(s, 0, 3, { size: 40, color: INK, weight: 800 });
    g.restore();
  });
  // bouncing hand-drawn arrows down (toward the comments / form)
  if (T > 55.3) for (let i = 0; i < 3; i++) {
    const b = Math.abs(Math.sin(T * 5 + i)) * 22, x = 430 + i * 170;
    handArrow(x, 1270 + b, x, 1345 + b, 1, i === 1 ? YEL : '#fff', 1400 + i * 2, 7);
  }
  // presenter pointing down
  const me = E.out(inv(51.3, 51.9, T)), wave = T > 63.3;
  drawMan(lerp(-200, 165, me), 1330, .6, {
    expr: wave ? 'happy' : 'smile', talk: talk(), lookX: .4, lookY: wave ? 0 : .5, blush: true,
    r: wave ? [170, -860 + Math.sin(T * 14) * 30] : [250, -330 + Math.sin(T * 5) * 18], br: wave ? 1 : -1, hr: wave ? 'wave' : 'point',
    l: [-140, -380], hl: 'fist',
  });
}

// ---------------------------------------------------------------- captions
const CAPS = [
  [0.00, 1.40, 'Gaji *RM2,500*'],
  [1.40, 3.00, 'tapi tak tahu hampa nak beli rumah harga berapa?'],
  [3.10, 5.10, 'Jangan-jangan selama ni hampa ingat gaji tak cukup,'],
  [5.10, 7.25, 'padahal tak pernah pun cuba.'],
  [7.35, 9.20, 'Saya bagi *10 saat*'],
  [9.20, 10.65, 'untuk tunjuk formula paling mudah.'],
  [10.80, 12.60, 'Hampa nak tahu caranya?'],
  [12.70, 14.22, 'Ambil *gaji kasar* setiap bulan,'],
  [14.22, 15.25, 'darab dengan *12*,'],
  [15.25, 16.65, 'kemudian darab dengan *10*.'],
  [16.70, 17.30, '*Siap!*'],
  [17.30, 20.05, 'Itulah anggaran kasar untuk hampa beli rumah.'],
  [20.20, 22.70, 'Contohnya, gaji kasar *RM2,500*.'],
  [22.80, 24.70, 'Darab dengan 12, dapat *RM30,000*.'],
  [24.70, 26.35, 'Darab lagi dengan *10*...'],
  [26.38, 27.30, '*BOOM!*'],
  [27.30, 28.76, 'Hampa dapat *RM300,000*. Nampak tak?'],
  [28.78, 31.60, 'Dengan formula mudah ni, hampa dah dapat'],
  [31.60, 35.05, 'satu angka permulaan untuk rancang beli rumah.'],
  [35.25, 37.00, 'Tapi, jangan salah faham.'],
  [37.00, 40.05, '*RM300 ribu* itu bukan bermaksud bank confirm lulus.'],
  [40.10, 42.30, 'Bank tetap tengok *komitmen kereta*,'],
  [42.30, 43.62, '*hutang*, *DSR*'],
  [43.62, 45.85, 'dan kemampuan *bayaran bulanan* hampa.'],
  [45.95, 48.55, 'Jadi, jangan terus anggap'],
  [48.55, 51.30, '*gaji kecil* tak mampu beli rumah.'],
  [51.38, 54.45, 'Nak tahu detail lanjut & semak kelayakan'],
  [54.45, 55.30, 'secara *PERCUMA*?'],
  [55.30, 57.35, 'Isi sahaja borang dekat bawah'],
  [57.35, 59.85, 'atau klik *link di bio*.'],
  [59.90, 61.90, 'Saya boleh buat semakan *LPPSA*,'],
  [61.90, 63.35, '*bank* atau yang *berniaga*.'],
  [63.40, 64.10, 'Bye bye!'],
];
function captions() {
  const c = CAPS.find(([a, b]) => T >= a && T < b);
  if (!c) return;
  const [a, , str] = c;
  const size = 66, maxW = 900, lh = 80;
  const words = []; let hl = false;
  str.split(/(\*)/).forEach(part => { if (part === '*') { hl = !hl; return; } part.split(' ').filter(Boolean).forEach(w => words.push([w, hl])); });
  const lines = [[]]; let lw = 0;
  const sp = measure(' ', size);
  words.forEach(wd => {
    const w = measure(wd[0], size);
    if (lw + w > maxW && lines[lines.length - 1].length) { lines.push([]); lw = 0; }
    lines[lines.length - 1].push([wd[0], wd[1], w]); lw += w + sp;
  });
  const s = E.back(inv(a, a + .16, T));
  const y0 = 1475 - (lines.length - 1) * lh / 2;
  g.save(); g.translate(540, y0); g.scale(s, s); g.translate(-540, -y0);
  lines.forEach((ln, li) => {
    const tw = ln.reduce((m, w) => m + w[2], 0) + sp * (ln.length - 1);
    let x = 540 - tw / 2;
    ln.forEach(([w, h, ww]) => {
      text(w, x, y0 + li * lh, { size, align: 'left', color: h ? YEL : '#fff', stroke: '#0a0a18', sw: 14 });
      x += ww + sp;
    });
  });
  g.restore();
}

// ---------------------------------------------------------------- post + frame
const scan = (() => {
  const c = document.createElement('canvas'); c.width = W; c.height = H; const x = c.getContext('2d');
  for (let y = 0; y < H; y += 4) { x.fillStyle = 'rgba(0,0,0,.06)'; x.fillRect(0, y, W, 1.5); }
  const v = x.createRadialGradient(540, 900, 520, 540, 960, 1250);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.55)');
  x.fillStyle = v; x.fillRect(0, 0, W, H);
  return c;
})();

function renderFrame(f) {
  FRAME = f; T = f / FPS; BOIL = Math.floor(T * 8);
  g = ctx;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.clearRect(0, 0, W, H);
  if (T < 10.6) scene1();
  else if (T < 20.1) scene2();
  else if (T < 35.1) scene3();
  else if (T < 35.42) {
    // record-scratch rewind of scene 3, then cut to the warning
    scene3(35.1 - (T - 35.1) * 3.2);
  }
  else if (T < 51.3) scene4();
  else scene5();
  ctx.setTransform(1, 0, 0, 1, 0, 0);

  g = octx;
  octx.setTransform(1, 0, 0, 1, 0, 0); octx.globalAlpha = 1; octx.globalCompositeOperation = 'source-over';
  // record-scratch wobble
  if (T >= 35.1 && T < 35.42) {
    const a = T - 35.1;
    octx.drawImage(buf, 0, 0);
    for (let i = 0; i < 24; i++) {
      const y = i * 80, dx = Math.sin(a * 60 + i * .7) * 40;
      octx.drawImage(buf, 0, y, W, 80, dx, y, W, 80);
    }
    octx.fillStyle = 'rgba(255,0,40,.18)'; octx.fillRect(0, 0, W, H);
  } else octx.drawImage(buf, 0, 0);
  // transition glitch
  GLITCHES.forEach(t0 => {
    const d = Math.abs(T - t0); if (d > .14) return;
    const k = 1 - d / .14;
    for (let i = 0; i < 14; i++) {
      const y = rnd(FRAME * 31 + i) * H, h = 20 + rnd(FRAME * 17 + i) * 140, dx = (rnd(FRAME * 7 + i) - .5) * 160 * k;
      octx.drawImage(buf, 0, y, W, h, dx, y, W, h);
    }
    octx.fillStyle = rgba(CYAN, .18 * k); octx.fillRect(0, 0, W, H);
  });
  // flashes
  FLASHES.forEach(([t0, d, col]) => {
    const a = T - t0; if (a < 0 || a > d) return;
    octx.fillStyle = rgba(col, .85 * Math.pow(1 - a / d, 2)); octx.fillRect(0, 0, W, H);
  });
  octx.drawImage(scan, 0, 0);
  // moving bright scan band (hologram screen feel)
  const by = (T * 420) % (H + 400) - 200;
  const bg = octx.createLinearGradient(0, by - 90, 0, by + 90);
  bg.addColorStop(0, 'rgba(120,240,255,0)'); bg.addColorStop(.5, 'rgba(120,240,255,.05)'); bg.addColorStop(1, 'rgba(120,240,255,0)');
  octx.fillStyle = bg; octx.fillRect(0, by - 90, W, 180);
  captions();
}

window.renderFrame = renderFrame;
window.FRAMES = DUR * FPS;
window.ready = (async () => {
  await Promise.all([
    document.fonts.load(`800 60px ${F_BOLD}`), document.fonts.load(`600 60px ${F_BOLD}`),
    document.fonts.load(`900 60px ${F_HOLO}`), document.fonts.load(`700 60px ${F_HOLO}`),
    document.fonts.load(`400 60px ${F_HAND}`),
  ]);
  await document.fonts.ready;
  return true;
})();
