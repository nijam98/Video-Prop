// Animated overlays for the 3-part house tour.
// Every scene is a pure function of time: window.renderAt(t) draws the frame at t seconds,
// so the renderer can step through frames deterministically.
//
// URL params: part=1|2|3, scene=intro|cta, title, sub, cta, ctatop, preview=1

const W = 1080, H = 1920;
const Q = new URLSearchParams(location.search);
const PART = +(Q.get('part') || 1);
const SCENE = Q.get('scene') || 'intro';
const TITLE = Q.get('title') || 'HOUSE TOUR';
const SUB = Q.get('sub') || '';
const SUB2 = Q.get('sub2') || '';
// raw time: continuous motion (wobble, shimmer, spin) keeps running while the intro holds
let RT = 0;
const KICK = Q.get('kick') || ('PART 0' + PART);
const BADGE = Q.get('badge') || `PART ${PART}/3`;
const CTA = Q.get('cta') || 'TEKAN LINK DI BIO';
const CTA_TOP = Q.get('ctatop') || 'Berminat?';
if (Q.get('preview')) document.body.classList.add('preview');

const stage = document.getElementById('stage');
const SVGNS = 'http://www.w3.org/2000/svg';

// Badge (top-left) shared by all parts; the intro ends by morphing into it.
const BCX = 195, BCY = 235, BW = 270, BH = 78;

// ---------- helpers ----------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, x) => a + (b - a) * x;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const eOutCubic = x => 1 - Math.pow(1 - x, 3);
const eInCubic = x => x * x * x;
const eInOut = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const eOutBack = (x, s = 1.7) => x <= 0 ? 0 : x >= 1 ? 1 : 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2);
const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };

function el(tag, css, parent, html) {
  const e = document.createElement(tag);
  if (css) e.style.cssText = css;
  if (html != null) e.innerHTML = html;
  (parent || stage).appendChild(e);
  return e;
}
function sv(tag, attrs, parent) {
  const e = document.createElementNS(SVGNS, tag);
  for (const k in attrs || {}) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}
function set(e, attrs) { for (const k in attrs) e.setAttribute(k, attrs[k]); }
function fullSvg(parent) {
  const s = sv('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, parent || stage);
  s.style.cssText = 'position:absolute;left:0;top:0;overflow:visible';
  return s;
}
// Shrink font until the element is no wider than maxW.
function fitWidth(e, maxW, start) {
  let s = start;
  e.style.fontSize = s + 'px';
  while (e.getBoundingClientRect().width > maxW && s > 12) { s -= 2; e.style.fontSize = s + 'px'; }
  return s;
}
function fitSvgText(e, maxW, start) {
  let s = start;
  e.setAttribute('font-size', s);
  while (e.getComputedTextLength() > maxW && s > 12) { s -= 2; e.setAttribute('font-size', s); }
  return s;
}
function rrPath(cx, cy, w, h, r) {
  const x = cx - w / 2, y = cy - h / 2;
  return `M${cx},${y} H${x + w - r} A${r},${r} 0 0 1 ${x + w},${y + r} V${y + h - r} A${r},${r} 0 0 1 ${x + w - r},${y + h} ` +
    `H${x + r} A${r},${r} 0 0 1 ${x},${y + h - r} V${y + r} A${r},${r} 0 0 1 ${x + r},${y} Z`;
}

// =====================================================================
// PART 1 — LIQUID MORPH (pearl iridescent goo)
// =====================================================================
function buildLiquid(scene) {
  const intro = scene === 'intro';
  const PCX = 540, PCY = intro ? 820 : 1250, PW = intro ? 800 : 860, PH = intro ? 200 : 210;
  const svg = fullSvg();
  const defs = sv('defs', {}, svg);
  defs.innerHTML = `
    <radialGradient id="scrim" cx="540" cy="${PCY}" r="${intro ? 820 : 900}" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#160a26" stop-opacity=".78"/>
      <stop offset=".55" stop-color="#160a26" stop-opacity=".5"/>
      <stop offset="1" stop-color="#160a26" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="pearl" gradientUnits="userSpaceOnUse" x1="120" y1="0" x2="960" y2="0">
      <stop offset="0" stop-color="#ffaedd"/><stop offset=".26" stop-color="#d2b8ff"/>
      <stop offset=".5" stop-color="#9fd4ff"/><stop offset=".74" stop-color="#ffe2b8"/>
      <stop offset="1" stop-color="#ffaedd"/>
    </linearGradient>
    <linearGradient id="ink" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#3a1460"/><stop offset=".5" stop-color="#1d1340"/><stop offset="1" stop-color="#4a1550"/>
    </linearGradient>
    <filter id="goo" filterUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}" color-interpolation-filters="sRGB">
      <feGaussianBlur id="gooBlur" in="SourceGraphic" stdDeviation="16" result="b"/>
      <feColorMatrix in="b" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 40 -18" result="g"/>
      <feGaussianBlur id="bumpBlur" in="g" stdDeviation="8" result="gb"/>
      <feSpecularLighting in="gb" surfaceScale="7" specularConstant="1.1" specularExponent="24" lighting-color="#ffffff" result="spec">
        <fePointLight id="light" x="380" y="500" z="380"/>
      </feSpecularLighting>
      <feComposite in="spec" in2="g" operator="in" result="specIn"/>
      <feComposite in="g" in2="specIn" operator="arithmetic" k1="0" k2="1" k3="0.7" k4="0" result="lit"/>
      <feDropShadow id="gooShadow" in="lit" dx="0" dy="14" stdDeviation="16" flood-color="#2a0f45" flood-opacity=".5"/>
    </filter>`;
  function dispFilter(id, seed, shadow) {
    const f = sv('filter', { id, filterUnits: 'userSpaceOnUse', x: 0, y: 0, width: W, height: H }, defs);
    sv('feTurbulence', { type: 'fractalNoise', baseFrequency: '0.010 0.026', numOctaves: 2, seed, result: 'n' }, f);
    const d = sv('feDisplacementMap', { in: 'SourceGraphic', in2: 'n', scale: 0, xChannelSelector: 'R', yChannelSelector: 'G', result: 'd' }, f);
    if (shadow) sv('feDropShadow', { in: 'd', dx: 0, dy: 3, stdDeviation: 7, 'flood-color': '#12061f', 'flood-opacity': .7 }, f);
    return d;
  }
  const scrim = sv('rect', { x: 0, y: 0, width: W, height: H, fill: 'url(#scrim)' }, svg);

  // ripples (CTA) live under the goo
  const ripples = [0, 1].map(() => sv('rect', { fill: 'none', stroke: '#fff', 'stroke-width': 4 }, svg));

  const goo = sv('g', { filter: 'url(#goo)', fill: 'url(#pearl)' }, svg);
  const pill = sv('rect', {}, goo);
  const N = 9;
  const blobs = [];
  for (let i = 0; i < N; i++) {
    blobs.push({
      el: sv('circle', {}, goo), r: lerp(78, 100, hash(i + 1)), ang: hash(i + 11) * Math.PI * 2,
      dist: lerp(650, 950, hash(i + 21)), d: i * 0.05 + hash(i + 31) * 0.14, ph: hash(i + 41) * 6.28,
      fx: (hash(i + 51) - .5) * 520, fy: -180 - hash(i + 61) * 520, curve: (hash(i + 71) - .5) * 260,
    });
  }
  const sats = [26, 20, 32].map((r, i) => ({ el: sv('circle', {}, goo), r, off: i * 2.1, dir: i % 2 ? -1 : 1 }));

  const pearl = defs.querySelector('#pearl');
  const gooBlur = defs.querySelector('#gooBlur');
  const bumpBlur = defs.querySelector('#bumpBlur');
  const light = defs.querySelector('#light');
  const gooShadow = defs.querySelector('#gooShadow');

  // texts
  const kickD = dispFilter('dk', 4, true), titleD = dispFilter('dt', 7, false), subD = dispFilter('ds', 9, true), sub2D = dispFilter('ds2', 11, true), badgeD = dispFilter('db', 2, false);
  const kick = sv('text', { x: 540, 'text-anchor': 'middle', 'font-family': 'Syne', 'font-weight': 700, 'font-size': 44, fill: '#fff', filter: 'url(#dk)' }, svg);
  const title = sv('text', { x: 540, 'text-anchor': 'middle', 'font-family': 'Syne', 'font-weight': 800, fill: 'url(#ink)', filter: 'url(#dt)' }, svg);
  const sub = sv('text', { x: 540, 'text-anchor': 'middle', 'font-family': 'Cormorant Garamond', 'font-style': 'italic', 'font-weight': 600, fill: '#fff', filter: 'url(#ds)' }, svg);
  const sub2 = sv('text', { x: 540, 'text-anchor': 'middle', 'font-family': 'Syne', 'font-weight': 700, 'font-size': 32, 'letter-spacing': 3, fill: '#fff', filter: 'url(#ds2)' }, svg);
  sub2.textContent = intro ? SUB2 : '';
  fitSvgText(sub2, 960, 32);
  const badge = sv('text', { x: BCX, y: BCY + 10, 'text-anchor': 'middle', 'font-family': 'Syne', 'font-weight': 700, 'font-size': 28, 'letter-spacing': 3, fill: '#2a1544', filter: 'url(#db)' }, svg);
  kick.textContent = intro ? KICK : '';
  title.textContent = intro ? TITLE : CTA;
  sub.textContent = intro ? SUB : CTA_TOP;
  badge.textContent = intro ? BADGE : '';
  const titleSize = fitSvgText(title, PW - 120, intro ? 92 : 64);
  set(title, { 'letter-spacing': 0 });
  const subSize = fitSvgText(sub, 940, intro ? 76 : 88);
  // tap dot (CTA)
  const tap = sv('g', {}, svg);
  sv('circle', { r: 30, fill: 'rgba(255,255,255,.92)' }, tap);
  sv('circle', { r: 44, fill: 'none', stroke: 'rgba(255,255,255,.75)', 'stroke-width': 4 }, tap);

  function textIn(node, d, t, a, b, out0, out1, ls0, ls1) {
    const pin = eOutCubic(prog(t, a, b));
    const pout = out0 != null ? eInCubic(prog(t, out0, out1)) : 0;
    node.setAttribute('opacity', pin * (1 - pout));
    d.setAttribute('scale', lerp(110, 0, pin) + 110 * pout);
    if (ls0 != null) node.setAttribute('letter-spacing', lerp(ls0, ls1, pin) + 20 * pout);
  }

  return function render(t) {
    // morph progress into the badge (intro only)
    const m = intro ? eInOut(prog(t, 3.35, 4.05)) : 0;
    let cx = lerp(PCX, BCX, m), cy = lerp(PCY, BCY, m);
    let w, h;
    const grow = intro ? prog(t, 0.75, 1.55) : prog(t, 0.6, 1.35);
    w = lerp(PW * eOutBack(grow, 1.2), BW, m);
    h = lerp(PH * eOutCubic(clamp(grow * 1.4)), BH, m);
    // CTA: gentle breathing + press bumps
    let press = 0;
    if (!intro) {
      for (let k = 0; k < 4; k++) {
        const ph = t - 1.8 - k * 1.3;
        if (ph >= 0 && ph < 0.28) press = Math.max(press, Math.sin(ph / 0.28 * Math.PI));
      }
      const br = 1 + 0.012 * Math.sin(t * 3) * prog(t, 1.4, 1.8) - 0.05 * press;
      w *= br; h *= br;
    }
    set(pill, { x: cx - w / 2, y: cy - h / 2, width: Math.max(w, 0), height: Math.max(h, 0), rx: h / 2 });
    const sc = lerp(1, BH / PH, m);
    const wob = prog(t, 1.0, 1.7) * (1 - m);
    blobs.forEach((b, i) => {
      const tx = cx + (i - (N - 1) / 2) / ((N - 1) / 2) * Math.max(0, w / 2 - h / 2) * 0.92;
      const ty = cy;
      const a = 0.04 + b.d, p = intro ? eOutCubic(prog(t, a, a + 1.15)) : prog(t, a, a + 0.95);
      let x, y;
      if (intro) {
        const sx = tx + Math.cos(b.ang) * b.dist, sy = ty + Math.sin(b.ang) * b.dist;
        const nx = -Math.sin(b.ang), ny = Math.cos(b.ang);
        x = lerp(sx, tx, p) + nx * b.curve * Math.sin(p * Math.PI);
        y = lerp(sy, ty, p) + ny * b.curve * Math.sin(p * Math.PI);
      } else {
        x = lerp(tx + b.fx, tx, eOutCubic(p));
        y = lerp(ty + b.fy - 500, ty, eOutBack(p, 1.6));
      }
      x += wob * 16 * Math.sin(RT * 2.1 + b.ph);
      y += wob * 13 * Math.cos(RT * 1.7 + b.ph * 1.3);
      const r = b.r * lerp(0.5, 1, p) * sc * (intro ? 1 : 1 - 0.05 * press) * Math.min(1, h / PH * 1.15 + 0.35);
      set(b.el, { cx: x, cy: y, r: p > 0 ? r : 0 });
    });
    const satIn = eOutBack(prog(t, 1.45, 2.05), 2) * (1 - m);
    sats.forEach((s, i) => {
      const a = RT * 0.85 * s.dir + s.off;
      const rx = w / 2 + 60 + 28 * Math.sin(RT * 1.3 + i * 2), ry = h / 2 + 64 + 26 * Math.cos(RT * 1.1 + i);
      set(s.el, { cx: cx + Math.cos(a) * rx, cy: cy + Math.sin(a) * ry, r: s.r * satIn });
    });
    set(pearl, { gradientTransform: `rotate(${18 + RT * 24} 540 ${cy})` });
    set(gooBlur, { stdDeviation: lerp(16, 7, m) });
    set(bumpBlur, { stdDeviation: lerp(8, 3.5, m) });
    set(light, { x: cx - lerp(180, 60, m) + 70 * Math.sin(RT * 0.8), y: cy - lerp(320, 120, m), z: lerp(380, 150, m) });
    set(gooShadow, { dy: lerp(14, 6, m), stdDeviation: lerp(16, 8, m) });

    if (intro) {
      scrim.setAttribute('opacity', eOutCubic(prog(t, 0, 0.6)) * (1 - prog(t, 3.3, 4.0)));
      set(kick, { y: PCY - PH / 2 - 60 });
      textIn(kick, kickD, t, 0.95, 1.6, 3.0, 3.35, 40, 16);
      set(title, { y: PCY + titleSize * 0.34 });
      textIn(title, titleD, t, 1.2, 1.95, 3.05, 3.4, 30, 2);
      set(sub, { y: PCY + PH / 2 + subSize + 30 });
      textIn(sub, subD, t, 1.5, 2.25, 3.1, 3.45);
      set(sub2, { y: PCY + PH / 2 + subSize + 100 });
      textIn(sub2, sub2D, t, 1.75, 2.4, 3.12, 3.45, 12, 3);
      badge.setAttribute('opacity', eOutCubic(prog(t, 3.85, 4.15)));
      badgeD.setAttribute('scale', lerp(40, 0, eOutCubic(prog(t, 3.85, 4.15))));
      tap.setAttribute('opacity', 0);
      ripples.forEach(r => r.setAttribute('opacity', 0));
    } else {
      scrim.setAttribute('opacity', eOutCubic(prog(t, 0, 0.5)));
      set(title, { y: PCY + titleSize * 0.35 });
      textIn(title, titleD, t, 0.95, 1.6, null, null, 24, 1);
      set(sub, { y: PCY - PH / 2 - 64 });
      textIn(sub, subD, t, 1.15, 1.8);
      sub2.setAttribute('opacity', 0);
      kick.setAttribute('opacity', 0); badge.setAttribute('opacity', 0);
      // ripples + tap
      ripples.forEach((r, k) => {
        let best = -1;
        for (let j = 0; j < 4; j++) { const ph = t - 1.8 - j * 1.3; if (ph >= 0 && ph < 1.2 && j % 2 === k) best = ph; }
        if (best < 0) { r.setAttribute('opacity', 0); return; }
        const rp = best / 1.2, s = 1 + 0.22 * eOutCubic(rp);
        const rw = PW * s, rh = PH * (1 + 0.6 * eOutCubic(rp));
        set(r, { x: PCX - rw / 2, y: PCY - rh / 2, width: rw, height: rh, rx: rh / 2, opacity: 0.8 * (1 - rp), 'stroke-width': lerp(6, 1, rp) });
      });
      const tapIn = eOutBack(prog(t, 1.45, 1.8), 2);
      set(tap, { opacity: tapIn, transform: `translate(${PCX + PW / 2 - 70},${PCY + PH / 2 - 6}) scale(${tapIn * (1 - 0.22 * press)})` });
    }
  };
}

// =====================================================================
// PART 2 — NEON GLOW
// =====================================================================
function buildNeon(scene) {
  const intro = scene === 'intro';
  const PINK = '#ff3dd6', CYAN = '#3df2ff', GOLD = '#ffd84d';
  const glow = (c, k = 1) => `0 0 ${3 * k}px #fff, 0 0 ${9 * k}px ${c}, 0 0 ${20 * k}px ${c}, 0 0 ${42 * k}px ${c}, 0 0 ${80 * k}px ${c}`;
  const tubeFilter = (c, k = 1) => `drop-shadow(0 0 ${3 * k}px ${c}) drop-shadow(0 0 ${12 * k}px ${c}) drop-shadow(0 0 ${30 * k}px ${c})`;

  const scrim = el('div', 'position:absolute;inset:0;');
  scrim.style.background = intro
    ? 'radial-gradient(ellipse 980px 900px at 540px 840px, rgba(9,2,26,.84), rgba(9,2,26,.6) 55%, rgba(9,2,26,.25) 100%)'
    : 'linear-gradient(to top, rgba(9,2,26,.92) 0%, rgba(9,2,26,.8) 32%, rgba(9,2,26,.4) 56%, rgba(9,2,26,0) 74%)';

  function tube(d, color, parent, fill) {
    const bg = fill ? sv('path', { d, fill, stroke: 'none' }, parent) : null;
    const g = sv('g', {}, parent);
    g.style.filter = tubeFilter(color);
    const outer = sv('path', { d, fill: 'none', stroke: color, 'stroke-width': 13, 'stroke-linecap': 'round', opacity: .6 }, g);
    const core = sv('path', { d, fill: 'none', stroke: '#fff4fd', 'stroke-width': 4.5, 'stroke-linecap': 'round' }, g);
    const L = core.getTotalLength();
    [outer, core].forEach(p => set(p, { 'stroke-dasharray': L + ' ' + L }));
    return {
      g, bg, core, L,
      draw(p) { [outer, core].forEach(q => q.setAttribute('stroke-dashoffset', L * (1 - p))); },
      point(p) { return core.getPointAtLength(L * p); },
    };
  }
  function neonText(str, css, color) {
    const wrap = el('div', 'position:absolute;left:0;width:1080px;text-align:center;white-space:nowrap;line-height:1;transform:translateY(-50%);' + css);
    const inner = el('span', 'display:inline-block', wrap);
    const spans = [...str].map(ch => { const s = el('span', '', inner); s.textContent = ch === ' ' ? '\u00a0' : ch; return s; });
    return { wrap, inner, spans, color };
  }
  function lit(span, on, color, k) {
    if (on) { span.style.color = '#fff3fc'; span.style.textShadow = glow(color, k); }
    else { span.style.color = color + '30'; span.style.textShadow = 'none'; }
  }
  // flicker on at t0, flicker off at t1
  function flick(t, t0, seed, t1) {
    if (t < t0) return 0;
    let on = 1;
    const dt = t - t0;
    if (dt < 0.34) { const f = Math.floor(dt * 30); on = hash(seed * 7.31 + f) < 0.2 + 0.8 * dt / 0.34 ? 1 : 0; }
    if (t1 != null && t >= t1) { const d2 = t - t1; if (d2 > 0.24) return 0; const f = Math.floor(d2 * 30); on = on && hash(seed * 3.7 + f + 99) > d2 / 0.24 ? 1 : 0; }
    return on;
  }

  const svg = fullSvg();
  const spark = sv('circle', { r: 9, fill: '#fff' }, svg);
  spark.style.filter = tubeFilter('#fff', 1.2);

  if (intro) {
    const FCY = 840;
    const frame = tube(rrPath(540, FCY, 880, 600, 60), PINK, svg);
    const kick = neonText(KICK, `top:${FCY - 220}px;font-family:'Tilt Neon';font-size:46px;letter-spacing:16px;padding-left:16px;`, CYAN);
    const title = neonText(TITLE, `top:${FCY - 40}px;font-family:Monoton;`, PINK);
    fitWidth(title.inner, 790, 118);
    const sub = neonText(SUB, `top:${FCY + 130}px;font-family:'Tilt Neon';`, CYAN);
    fitWidth(sub.inner, 780, 54);
    const sub2 = neonText(SUB2, `top:${FCY + 210}px;font-family:'Tilt Neon';`, PINK);
    fitWidth(sub2.inner, 760, 38);
    // badge
    const badgeSvg = fullSvg();
    const bt = tube(rrPath(BCX, BCY, BW, BH, BH / 2), CYAN, badgeSvg, 'rgba(12,2,30,.62)');
    const badge = neonText(BADGE, `top:${BCY}px;left:${BCX - 540}px;font-family:'Tilt Neon';font-size:32px;letter-spacing:4px;`, PINK);

    return function render(t) {
      scrim.style.opacity = eOutCubic(prog(t, 0, 0.4)) * (1 - prog(t, 3.55, 4.15));
      const k = 1 + 0.07 * Math.sin(RT * 11) + 0.05 * Math.sin(RT * 23);
      const dp = eInOut(prog(t, 0.1, 1.1));
      frame.draw(dp);
      frame.g.style.opacity = t < 3.35 ? 1 : flick(t, 0, 1, 3.35);
      frame.g.style.filter = tubeFilter(PINK, k);
      if (dp > 0 && dp < 1) { const p = frame.point(dp); set(spark, { cx: p.x, cy: p.y, opacity: 1 }); }
      else spark.setAttribute('opacity', 0);
      kick.spans.forEach((s, i) => lit(s, flick(t, 0.85 + hash(i) * 0.35, i + 3, 3.25 + hash(i + 5) * 0.15), CYAN, k));
      title.spans.forEach((s, i) => {
        let on = flick(t, 1.05 + hash(i + 50) * 0.55, i + 50, 3.2 + hash(i + 9) * 0.2);
        if (i === 2 && t > 2.4 && t < 2.62) on = hash(Math.floor(t * 30) + 7) > 0.5 ? 1 : 0; // a buzzing letter
        lit(s, on, PINK, k);
      });
      sub.spans.forEach((s, i) => lit(s, flick(t, 1.6 + hash(i + 80) * 0.3, i + 80, 3.3 + hash(i + 3) * 0.12), CYAN, k));
      sub2.spans.forEach((s, i) => lit(s, flick(t, 1.9 + hash(i + 120) * 0.3, i + 120, 3.3 + hash(i + 7) * 0.12), PINK, k * 0.8));
      // unlit tubes fade away once the intro is done
      const ghost = 1 - prog(t, 3.45, 3.7);
      [kick, title, sub, sub2].forEach(x => { x.wrap.style.opacity = ghost; });
      badge.wrap.style.opacity = t < 3.6 ? 0 : 1;
      // badge
      const bp = eInOut(prog(t, 3.6, 3.95));
      bt.draw(bp);
      bt.bg.setAttribute('opacity', bp);
      bt.g.style.opacity = t < 3.6 ? 0 : 1;
      badge.spans.forEach((s, i) => lit(s, flick(t, 3.8 + hash(i + 20) * 0.1, i + 20), PINK, 0.8));
    };
  } else {
    const CY = 1250;
    const tw = 880, th = 220;
    const t1 = tube(rrPath(540, CY, tw, th, th / 2), CYAN, svg, 'rgba(12,2,30,.55)');
    // marquee bulbs around the sign
    const ring = sv('path', { d: rrPath(540, CY, tw + 70, th + 70, (th + 70) / 2), fill: 'none' }, svg);
    const RL = ring.getTotalLength();
    const NB = 46;
    const bulbs = [];
    for (let i = 0; i < NB; i++) {
      const p = ring.getPointAtLength(RL * i / NB);
      bulbs.push(sv('circle', { cx: p.x, cy: p.y, r: 6 }, svg));
    }
    const txt = neonText(CTA, `top:${CY}px;font-family:'Tilt Neon';`, PINK);
    fitWidth(txt.inner, 760, 84);
    const top = neonText(CTA_TOP.toUpperCase(), `top:${CY - 245}px;font-family:Monoton;`, CYAN);
    fitWidth(top.inner, 820, 76);

    return function render(t) {
      scrim.style.opacity = eOutCubic(prog(t, 0, 0.5));
      const k = 1 + 0.16 * Math.sin((t - 1.6) * 5) * prog(t, 1.5, 1.9) + 0.05 * Math.sin(t * 23);
      const dp = eInOut(prog(t, 0.1, 0.9));
      t1.draw(dp);
      t1.bg.setAttribute('opacity', dp);
      t1.g.style.filter = tubeFilter(CYAN, k);
      if (dp > 0 && dp < 1) { const p = t1.point(dp); set(spark, { cx: p.x, cy: p.y, opacity: 1 }); }
      else spark.setAttribute('opacity', 0);
      txt.spans.forEach((s, i) => lit(s, flick(t, 0.7 + hash(i + 30) * 0.5, i + 30), PINK, k));
      top.spans.forEach((s, i) => lit(s, flick(t, 1.2 + hash(i + 60) * 0.35, i + 60), CYAN, k));
      const on = flick(t, 1.3, 77);
      const chase = Math.floor(t * 10);
      bulbs.forEach((b, i) => {
        const hot = on && (i + chase) % 3 === 0;
        set(b, { fill: hot ? '#fff6c8' : (on ? GOLD + '55' : GOLD + '22'), opacity: on || t > 1.3 ? 1 : 0.4 });
        b.style.filter = hot ? `drop-shadow(0 0 4px ${GOLD}) drop-shadow(0 0 12px ${GOLD})` : 'none';
      });
    };
  }
}

// =====================================================================
// PART 3 — Y2K CHROME
// =====================================================================
function buildY2K(scene) {
  const intro = scene === 'intro';
  const INK = '#151826', VIOLET = '#7a5cff';
  const CHROME = 'linear-gradient(180deg,#ffffff 0%,#e8edf5 16%,#a5afbd 36%,#f5f8fc 48%,#2d3442 52%,#5a6373 63%,#bcc5d1 82%,#ffffff 100%)';
  const HOLO = 'linear-gradient(90deg,#ff9be0,#c3a6ff,#89e8ff,#b8ffcf,#fff09a,#ff9be0)';
  const LIGHT_CHROME = 'linear-gradient(180deg,#ffffff 0%,#eef2f7 38%,#c6cfdb 56%,#e9eef4 78%,#ffffff 100%)';

  const scrim = el('div', 'position:absolute;inset:0;');
  scrim.style.background = intro
    ? 'radial-gradient(ellipse 900px 820px at 540px 830px, rgba(14,12,34,.8), rgba(14,12,34,.55) 55%, rgba(14,12,34,0) 100%)'
    : 'linear-gradient(to top, rgba(14,12,34,.85) 0%, rgba(14,12,34,.65) 30%, rgba(14,12,34,.3) 55%, rgba(14,12,34,0) 72%)';

  const svg = fullSvg();
  const defs = sv('defs', {}, svg);
  defs.innerHTML = `
    <linearGradient id="chromeG" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff"/><stop offset=".35" stop-color="#b9c3cf"/><stop offset=".5" stop-color="#f4f7fb"/>
      <stop offset=".52" stop-color="#3a4252"/><stop offset=".75" stop-color="#9aa5b4"/><stop offset="1" stop-color="#fff"/>
    </linearGradient>
    <linearGradient id="holoG" gradientUnits="userSpaceOnUse" x1="120" y1="0" x2="960" y2="0">
      <stop offset="0" stop-color="#ff9be0"/><stop offset=".25" stop-color="#c3a6ff"/><stop offset=".5" stop-color="#89e8ff"/>
      <stop offset=".75" stop-color="#b8ffcf"/><stop offset="1" stop-color="#fff09a"/>
    </linearGradient>`;
  const STAR = 'M0,-1 C0.1,-0.1 0.1,-0.1 1,0 C0.1,0.1 0.1,0.1 0,1 C-0.1,0.1 -0.1,0.1 -1,0 C-0.1,-0.1 -0.1,-0.1 0,-1Z';
  function star(x, y, s) {
    const g = sv('g', {}, svg);
    sv('path', { d: STAR, fill: 'url(#chromeG)', stroke: INK, 'stroke-width': 2.2, 'vector-effect': 'non-scaling-stroke' }, g);
    g.style.filter = 'drop-shadow(0 0 10px rgba(255,255,255,.85))';
    return { g, x, y, s };
  }
  function chromeText(str, font, size, cy, maxW) {
    const box = el('div', `position:absolute;left:540px;top:${cy}px;font-family:${font};line-height:1.08;white-space:nowrap;`);
    const back = el('div', `color:${INK};`, box); back.textContent = str;
    const front = el('div', `position:absolute;inset:0;background:${CHROME};-webkit-background-clip:text;background-clip:text;color:transparent;`, box); front.textContent = str;
    const shine = el('div', `position:absolute;inset:0;background:linear-gradient(100deg,transparent 42%,rgba(255,255,255,.95) 50%,transparent 58%);background-size:300% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;`, box); shine.textContent = str;
    const fs = fitWidth(box, maxW, size);
    back.style.webkitTextStroke = `${Math.round(fs * 0.13)}px ${INK}`;
    back.style.filter = `drop-shadow(0 ${Math.round(fs * 0.07)}px 0 ${VIOLET}) drop-shadow(0 ${Math.round(fs * 0.12)}px ${Math.round(fs * 0.14)}px rgba(0,0,0,.5))`;
    return {
      box, fs,
      setShine(p) { shine.style.backgroundPosition = `${lerp(100, 0, p)}% 0`; shine.style.opacity = p > 0 && p < 1 ? 1 : 0; },
      tf(s, rot, extra = '') { box.style.transform = `translate(-50%,-50%) ${extra} rotate(${rot}deg) scale(${s})`; },
    };
  }
  function badgeEl() {
    const b = el('div', `position:absolute;left:${BCX - BW / 2}px;top:${BCY - BH / 2}px;width:${BW}px;height:${BH}px;border-radius:${BH / 2}px;
      background:${LIGHT_CHROME};border:3px solid ${INK};box-shadow:0 6px 0 ${VIOLET},0 10px 20px rgba(0,0,0,.35),inset 0 3px 4px rgba(255,255,255,.9);
      display:flex;align-items:center;justify-content:center;font-family:Unbounded;font-weight:700;font-size:26px;letter-spacing:2px;color:${INK};
      text-shadow:0 1px 0 rgba(255,255,255,.8);`);
    b.textContent = BADGE;
    return b;
  }

  if (intro) {
    const CY = 830;
    const swoosh = sv('path', { d: `M150,${CY + 105} C380,${CY + 40} 700,${CY + 170} 930,${CY + 90}`, fill: 'none', stroke: 'url(#holoG)', 'stroke-width': 12, 'stroke-linecap': 'round' }, svg);
    swoosh.style.filter = 'drop-shadow(0 0 8px rgba(255,255,255,.7))';
    const SL = swoosh.getTotalLength(); set(swoosh, { 'stroke-dasharray': SL + ' ' + SL });
    const stars = [[150, 620, 58], [935, 680, 44], [895, 1010, 66], [175, 1030, 38], [560, 560, 30], [1000, 880, 26]].map(a => star(...a));
    const title = chromeText(TITLE, "Unbounded;font-weight:900", 132, CY - 20, 930);
    const kick = el('div', `position:absolute;left:540px;top:${CY - 175}px;padding:14px 30px;border-radius:40px;background:${HOLO};background-size:200% 100%;
      border:3px solid ${INK};font-family:Unbounded;font-weight:700;font-size:30px;letter-spacing:6px;color:${INK};box-shadow:0 5px 0 ${INK};white-space:nowrap;`);
    kick.textContent = KICK;
    const sub = el('div', `position:absolute;left:540px;top:${CY + 175}px;font-family:Unbounded;font-weight:700;color:#fff;white-space:nowrap;
      text-shadow:0 3px 0 ${INK},0 -2px 0 ${INK},2px 0 0 ${INK},-2px 0 0 ${INK},0 6px 16px rgba(0,0,0,.6);`);
    sub.textContent = SUB;
    fitWidth(sub, 900, 44);
    const sub2 = el('div', `position:absolute;left:540px;top:${CY + 238}px;font-family:Unbounded;font-weight:400;color:#fff;white-space:nowrap;letter-spacing:2px;
      text-shadow:0 2px 0 ${INK},0 -2px 0 ${INK},2px 0 0 ${INK},-2px 0 0 ${INK},0 6px 16px rgba(0,0,0,.6);`);
    sub2.textContent = SUB2;
    fitWidth(sub2, 900, 28);
    const badge = badgeEl();
    const bstar = star(BCX + BW / 2 - 6, BCY - BH / 2 + 2, 22);
    stars.push(bstar);

    return function render(t) {
      scrim.style.opacity = eOutCubic(prog(t, 0, 0.4)) * (1 - prog(t, 3.5, 4.1));
      const out = eInCubic(prog(t, 3.2, 3.55));
      const ti = eOutBack(prog(t, 0.2, 0.95), 1.9);
      title.tf(lerp(0.15, 1, ti) * (1 - out), lerp(-14, 0, ti) + 25 * out, `perspective(800px) rotateX(${lerp(70, 0, eOutCubic(prog(t, 0.2, 0.8)))}deg)`);
      title.box.style.opacity = prog(t, 0.2, 0.35);
      title.setShine(t < 1.8 ? prog(t, 1.1, 1.8) : t < 2.5 ? 0 : prog(t, 2.5, 3.2));
      const ki = eOutBack(prog(t, 0.55, 0.95), 2.4) * (1 - eInCubic(prog(t, 3.15, 3.45)));
      kick.style.transform = `translate(-50%,-50%) scale(${ki}) rotate(${lerp(-10, -3, ki)}deg)`;
      kick.style.backgroundPosition = `${(RT * 40) % 200}% 0`;
      const si = eOutCubic(prog(t, 1.2, 1.7));
      sub.style.transform = `translate(-50%,-50%) translateY(${lerp(40, 0, si)}px)`;
      sub.style.opacity = si * (1 - prog(t, 3.2, 3.45));
      const s2 = eOutCubic(prog(t, 1.45, 1.95));
      sub2.style.transform = `translate(-50%,-50%) translateY(${lerp(30, 0, s2)}px)`;
      sub2.style.opacity = s2 * (1 - prog(t, 3.2, 3.45));
      swoosh.setAttribute('stroke-dashoffset', SL * (1 - eInOut(prog(t, 0.9, 1.5))) - SL * eInCubic(prog(t, 3.15, 3.5)));
      stars.forEach((s, i) => {
        const isBadge = s === bstar;
        const a = isBadge ? 3.85 : 0.6 + i * 0.12;
        let sc = eOutBack(prog(t, a, a + 0.4), 2.6);
        if (!isBadge) sc *= (0.85 + 0.15 * Math.sin(RT * 5 + i * 1.7)) * (1 - eInCubic(prog(t, 3.15 + i * 0.03, 3.45 + i * 0.03)));
        const rot = isBadge ? 0 : RT * 50 * (i % 2 ? -1 : 1) + i * 20;
        set(s.g, { transform: `translate(${s.x},${s.y}) rotate(${rot}) scale(${s.s * sc})` });
      });
      const bi = eOutBack(prog(t, 3.7, 4.1), 2);
      badge.style.transform = `scale(${bi})`;
      badge.style.opacity = prog(t, 3.7, 3.8);
    };
  } else {
    const CY = 1250, BWd = 880, BHd = 200;
    const ripple = sv('rect', { fill: 'none', stroke: 'url(#holoG)', 'stroke-width': 8 }, svg);
    ripple.style.filter = 'drop-shadow(0 0 8px rgba(255,255,255,.8))';
    const btn = el('div', `position:absolute;left:${540 - BWd / 2}px;top:${CY - BHd / 2}px;width:${BWd}px;height:${BHd}px;border-radius:${BHd / 2}px;
      background:${LIGHT_CHROME};border:5px solid ${INK};overflow:hidden;display:flex;align-items:center;justify-content:center;`);
    const label = el('div', `font-family:Unbounded;font-weight:900;color:${INK};white-space:nowrap;text-shadow:0 2px 0 rgba(255,255,255,.85);position:relative;z-index:2;`, btn);
    label.textContent = CTA;
    fitWidth(label, BWd - 130, 62);
    const band = el('div', `position:absolute;top:-20px;bottom:-20px;width:150px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.95),transparent);transform:skewX(-22deg);z-index:1;`, btn);
    const top = chromeText(CTA_TOP.toUpperCase(), "Unbounded;font-weight:900", 96, CY - 225, 860);
    // svg stars on top layer
    const svg2 = fullSvg();
    const stars = [[120, 1110, 46], [965, 1120, 36], [990, 1385, 54], [95, 1395, 34]].map(a => { const s = star(...a); svg2.appendChild(s.g); return s; });
    // classic Y2K arrow cursor
    const cur = sv('g', {}, svg2);
    sv('path', { d: 'M0,0 L0,72 L17,56 L29,84 L41,79 L29,52 L52,52 Z', fill: '#fff', stroke: INK, 'stroke-width': 4.5, 'stroke-linejoin': 'round' }, cur);
    cur.style.filter = 'drop-shadow(0 6px 6px rgba(0,0,0,.45))';
    const clicks = [2.0, 3.4];

    return function render(t) {
      scrim.style.opacity = eOutCubic(prog(t, 0, 0.5));
      let press = 0;
      clicks.forEach(c => { const ph = t - c; if (ph >= 0 && ph < 0.3) press = Math.max(press, Math.sin(ph / 0.3 * Math.PI)); });
      const bi = eOutBack(prog(t, 0.15, 0.8), 2.0);
      btn.style.transform = `translateY(${press * 8}px) rotate(${lerp(-8, 0, bi)}deg) scale(${lerp(0.2, 1, bi) * (1 + 0.01 * Math.sin(t * 3))})`;
      btn.style.opacity = prog(t, 0.15, 0.3);
      btn.style.boxShadow = `0 ${12 - press * 8}px 0 ${VIOLET},0 ${26 - press * 10}px 40px rgba(0,0,0,.45),inset 0 6px 8px rgba(255,255,255,.9),inset 0 -10px 18px rgba(0,0,0,.25)`;
      const sweep = ((t - 0.9) % 1.8) / 1.8;
      band.style.left = (t < 0.9 ? -300 : lerp(-300, BWd + 150, eInOut(clamp(sweep / 0.6)))) + 'px';
      const ti = eOutBack(prog(t, 0.55, 1.1), 2.2);
      top.tf(lerp(0.2, 1, ti), lerp(10, 0, ti));
      top.box.style.opacity = prog(t, 0.55, 0.7);
      top.setShine(t < 2.1 ? prog(t, 1.4, 2.1) : t < 3.0 ? 0 : prog(t, 3.0, 3.7));
      // ripple on click
      let rp = -1; clicks.forEach(c => { const ph = t - c; if (ph >= 0 && ph < 1) rp = ph; });
      if (rp >= 0) {
        const s = 1 + 0.25 * eOutCubic(rp), rw = BWd * s, rh = BHd * (1 + 0.7 * eOutCubic(rp));
        set(ripple, { x: 540 - rw / 2, y: CY - rh / 2, width: rw, height: rh, rx: rh / 2, opacity: 1 - rp, 'stroke-width': lerp(10, 2, rp) });
      } else ripple.setAttribute('opacity', 0);
      // cursor path
      const ci = eOutCubic(prog(t, 1.0, 1.6));
      const cx = lerp(1050, 790, ci) + 6 * Math.sin(t * 2), cy = lerp(1700, 1312, ci) + 5 * Math.cos(t * 2.3);
      set(cur, { transform: `translate(${cx},${cy}) scale(${1.25 * (1 - 0.15 * press)})`, opacity: prog(t, 1.0, 1.15) });
      stars.forEach((s, i) => {
        const a = 0.7 + i * 0.15;
        const sc = eOutBack(prog(t, a, a + 0.4), 2.6) * (0.8 + 0.2 * Math.sin(t * 4.5 + i * 2));
        set(s.g, { transform: `translate(${s.x},${s.y}) rotate(${t * 45 * (i % 2 ? -1 : 1)}) scale(${s.s * sc})` });
      });
    };
  }
}

// =====================================================================
// TRACK LAYER — karaoke subtitles + selling-point callouts above the presenter's head
// window.TRACK = { captions:[{s,e,words:[{w,s,e}]}], callouts:[{s,e,text}], head:{dt, x:[], y:[]} }
// (all times relative to the start of the part)
// =====================================================================
function buildTrack() {
  const T = window.TRACK || { captions: [], callouts: [], head: null };
  const PINK = '#ff3dd6', CYAN = '#3df2ff', INK = '#151826', VIOLET = '#7a5cff';
  const CHROME = 'linear-gradient(180deg,#ffffff 0%,#e8edf5 16%,#a5afbd 36%,#f5f8fc 48%,#2d3442 52%,#5a6373 63%,#bcc5d1 82%,#ffffff 100%)';
  const CAP_Y = 1470;
  const LIGHT_CHROME = 'linear-gradient(180deg,#ffffff 0%,#eef2f7 38%,#c6cfdb 56%,#e9eef4 78%,#ffffff 100%)';
  const outline = (c, r) => [[r, 0], [-r, 0], [0, r], [0, -r], [r, r], [-r, r], [r, -r], [-r, -r]].map(([x, y]) => `${x}px ${y}px 0 ${c}`).join(',');

  // ---------- captions ----------
  const capLayer = el('div', `position:absolute;left:50px;width:980px;top:${CAP_Y}px;height:0;`);
  const capStyle = {
    1: { box: "font-family:Syne;font-weight:800;font-size:60px;color:#fff;", word: 'padding:0 12px;border-radius:18px;',
      off: s => { s.style.background = 'none'; s.style.color = '#fff'; s.style.textShadow = '0 3px 14px rgba(15,5,30,.9),0 0 3px rgba(0,0,0,.7)'; s.style.boxShadow = 'none'; },
      on: s => { s.style.background = 'linear-gradient(100deg,#ffaedd,#d2b8ff 45%,#9fd4ff)'; s.style.color = '#22113a'; s.style.textShadow = 'none'; s.style.boxShadow = '0 6px 18px rgba(30,10,60,.5), inset 0 2px 4px rgba(255,255,255,.8)'; } },
    2: { box: "font-family:'Tilt Neon';font-size:62px;color:#fff;", word: 'padding:0 6px;',
      off: s => { s.style.color = '#f4fdff'; s.style.textShadow = `0 0 3px #fff,0 0 10px ${CYAN},0 0 22px ${CYAN}`; },
      on: s => { s.style.color = '#fff3fc'; s.style.textShadow = `0 0 3px #fff,0 0 9px ${PINK},0 0 20px ${PINK},0 0 40px ${PINK},0 0 70px ${PINK}`; } },
    3: { box: `font-family:Unbounded;font-weight:900;font-size:50px;color:#fff;text-transform:uppercase;`, word: 'padding:0 8px;',
      off: s => { s.style.color = '#fff'; s.style.textShadow = outline(INK, 3) + `,0 7px 0 ${VIOLET}`; },
      on: s => { s.style.color = '#ff9be0'; s.style.textShadow = outline(INK, 3) + `,0 7px 0 ${VIOLET}`; } },
  }[PART];
  const caps = T.captions.map((c, k) => {
    const nxt = T.captions[k + 1];
    const end = nxt ? Math.min(nxt.s, c.e + 0.6) : c.e + 0.6;
    const wrap = el('div', `position:absolute;left:0;width:980px;top:0;text-align:center;line-height:1.3;display:none;`, capLayer);
    const box = el('div', `display:inline-block;white-space:nowrap;${capStyle.box}`, wrap);
    if (PART === 2) box.style.cssText += `background:rgba(9,2,26,.62);border:2px solid ${CYAN}88;border-radius:30px;padding:10px 26px;box-shadow:0 0 18px ${CYAN}55, inset 0 0 14px ${CYAN}33;`;
    const words = c.words.map((w, i) => { if (i) box.appendChild(document.createTextNode(' ')); const s = el('span', `display:inline-block;${capStyle.word}`, box); s.textContent = w.w; return { s, t: w.s, e: w.e }; });
    wrap.style.display = 'block';
    let fs = parseFloat(getComputedStyle(box).fontSize);
    while (box.getBoundingClientRect().width > 960 && fs > 30) { fs -= 2; box.style.fontSize = fs + 'px'; }
    wrap.style.display = 'none';
    return { wrap, box, words, s: c.s, end };
  });

  // ---------- head track ----------
  function headAt(t) {
    const h = T.head;
    if (!h || !h.x.length) return { x: 540, y: 560 };
    const f = clamp(t / h.dt, 0, h.x.length - 1), i = Math.floor(f), u = f - i, j = Math.min(i + 1, h.x.length - 1);
    return { x: lerp(h.x[i], h.x[j], u), y: lerp(h.y[i], h.y[j], u) };
  }

  // ---------- callouts ----------
  let drawCallout, measureW;
  if (PART === 1) {
    const svg = fullSvg();
    const defs = sv('defs', {}, svg);
    defs.innerHTML = `
      <linearGradient id="cpearl" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="400" y2="0">
        <stop offset="0" stop-color="#ffaedd"/><stop offset=".35" stop-color="#d2b8ff"/><stop offset=".7" stop-color="#9fd4ff"/><stop offset="1" stop-color="#ffe2b8"/>
      </linearGradient>
      <filter id="cgoo" filterUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}" color-interpolation-filters="sRGB">
        <feGaussianBlur in="SourceGraphic" stdDeviation="9" result="b"/>
        <feColorMatrix in="b" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 36 -16" result="g"/>
        <feGaussianBlur in="g" stdDeviation="4" result="gb"/>
        <feSpecularLighting in="gb" surfaceScale="5" specularConstant="1" specularExponent="24" lighting-color="#fff" result="spec">
          <fePointLight id="clight" x="300" y="300" z="220"/></feSpecularLighting>
        <feComposite in="spec" in2="g" operator="in" result="si"/>
        <feComposite in="g" in2="si" operator="arithmetic" k1="0" k2="1" k3="0.7" k4="0" result="lit"/>
        <feDropShadow in="lit" dx="0" dy="8" stdDeviation="10" flood-color="#2a0f45" flood-opacity=".5"/>
      </filter>
      <filter id="cdisp" filterUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}">
        <feTurbulence type="fractalNoise" baseFrequency="0.012 0.03" numOctaves="2" seed="5" result="n"/>
        <feDisplacementMap id="cdm" in="SourceGraphic" in2="n" scale="0" xChannelSelector="R" yChannelSelector="G"/>
      </filter>`;
    const g = sv('g', { filter: 'url(#cgoo)', fill: 'url(#cpearl)' }, svg);
    const pill = sv('rect', {}, g), tail = sv('circle', {}, g), drip = sv('circle', {}, g);
    const txt = sv('text', { 'text-anchor': 'middle', 'font-family': 'Syne', 'font-weight': 800, 'font-size': 40, fill: '#22113a', filter: 'url(#cdisp)' }, svg);
    const grad = defs.querySelector('#cpearl'), light = defs.querySelector('#clight'), dm = defs.querySelector('#cdm');
    let lastText = null, tw = 0;
    measureW = text => { txt.textContent = text; const w = txt.getComputedTextLength() + 84; lastText = null; return w; };
    drawCallout = (c, t, ax, ay) => {
      if (!c) { [pill, tail, drip].forEach(e => e.setAttribute('opacity', 0)); txt.setAttribute('opacity', 0); return; }
      [pill, tail, drip].forEach(e => e.setAttribute('opacity', 1));
      if (c.text !== lastText) { txt.textContent = c.text; tw = txt.getComputedTextLength(); lastText = c.text; }
      const lt = t - c.s, rem = c.e - t;
      const grow = eOutBack(prog(lt, 0.1, 0.55), 1.3) * (1 - eInCubic(prog(rem, 0.35, 0) ));
      const pw = tw + 84, ph = 86;
      const cy = ay - 34 - ph / 2;
      const w = Math.max(0, lerp(ph * 0.4, pw, grow)), h = ph * clamp(eOutCubic(prog(lt, 0, 0.3)) * (rem < 0.35 ? rem / 0.35 : 1));
      set(pill, { x: ax - w / 2, y: cy - h / 2, width: w, height: h, rx: h / 2 });
      const tr = 17 * eOutBack(prog(lt, 0, 0.3), 2) * clamp(rem / 0.3);
      set(tail, { cx: ax, cy: ay - 26, r: tr });
      set(drip, { cx: ax, cy: ay - 4 + 5 * Math.sin(t * 4), r: 9 * eOutBack(prog(lt, 0.25, 0.5), 2) * clamp(rem / 0.3) });
      set(grad, { x1: ax - pw / 2, x2: ax + pw / 2, gradientTransform: `rotate(${t * 30} ${ax} ${cy})` });
      set(light, { x: ax - pw * 0.25, y: cy - 140, z: 220 });
      const ti = eOutCubic(prog(lt, 0.3, 0.65)) * (1 - prog(rem, 0.3, 0.1));
      set(txt, { x: ax, y: cy + 14, opacity: ti });
      dm.setAttribute('scale', lerp(70, 0, ti));
    };
  } else if (PART === 2) {
    const svg = fullSvg();
    const fillP = sv('path', { fill: 'rgba(9,2,26,.7)' }, svg);
    const g = sv('g', {}, svg);
    g.style.filter = `drop-shadow(0 0 3px ${CYAN}) drop-shadow(0 0 12px ${CYAN}) drop-shadow(0 0 26px ${CYAN})`;
    const outer = sv('path', { fill: 'none', stroke: CYAN, 'stroke-width': 11, opacity: .6, 'stroke-linejoin': 'round' }, g);
    const core = sv('path', { fill: 'none', stroke: '#f0feff', 'stroke-width': 4, 'stroke-linejoin': 'round' }, g);
    const txt = el('div', `position:absolute;width:max-content;white-space:nowrap;font-family:'Tilt Neon';font-size:44px;line-height:1;transform:translate(-50%,-50%);`);
    const meas = el('span', `position:absolute;visibility:hidden;white-space:nowrap;font-family:'Tilt Neon';font-size:44px;`);
    let lastText = null, tw = 0, spans = [];
    measureW = text => { meas.textContent = text; return meas.getBoundingClientRect().width + 70; };
    function bubble(cx, cy, w, h, r, ax, ay) {
      const x = cx - w / 2, y = cy - h / 2, b = y + h;
      return `M${cx},${y} H${x + w - r} A${r},${r} 0 0 1 ${x + w},${y + r} V${b - r} A${r},${r} 0 0 1 ${x + w - r},${b} ` +
        `H${ax + 20} L${ax},${ay} L${ax - 20},${b} H${x + r} A${r},${r} 0 0 1 ${x},${b - r} V${y + r} A${r},${r} 0 0 1 ${x + r},${y} Z`;
    }
    function flick(t, t0, seed) {
      if (t < t0) return 0; const dt = t - t0; if (dt > 0.3) return 1;
      return hash(seed * 7.31 + Math.floor(dt * 30)) < 0.25 + 0.75 * dt / 0.3 ? 1 : 0;
    }
    drawCallout = (c, t, ax, ay) => {
      if (!c) { [fillP, g].forEach(e => e.style.opacity = 0); txt.style.opacity = 0; return; }
      if (c.text !== lastText) {
        meas.textContent = c.text; tw = meas.getBoundingClientRect().width; lastText = c.text;
        txt.innerHTML = ''; spans = [...c.text].map(ch => { const s = el('span', '', txt); s.textContent = ch === ' ' ? ' ' : ch; return s; });
      }
      const lt = t - c.s, rem = c.e - t;
      const w = tw + 70, h = 80, cy = ay - 24 - h / 2;
      const d = bubble(ax, cy, w, h, 26, ax, ay);
      [fillP, outer, core].forEach(p => p.setAttribute('d', d));
      const L = core.getTotalLength(), dp = eInOut(prog(lt, 0, 0.4));
      [outer, core].forEach(p => set(p, { 'stroke-dasharray': `${L} ${L}`, 'stroke-dashoffset': L * (1 - dp) }));
      const off = rem < 0.3 ? (hash(Math.floor(rem * 30) + 3) < rem / 0.3 ? 1 : 0) : 1;
      g.style.opacity = off; fillP.style.opacity = dp * (rem < 0.3 ? rem / 0.3 : 1);
      txt.style.left = ax + 'px'; txt.style.top = cy + 'px'; txt.style.opacity = 1;
      spans.forEach((s, i) => {
        const on = flick(lt, 0.25 + hash(i + 11) * 0.25, i + 11) && off;
        s.style.color = on ? '#fff3fc' : PINK + '22';
        s.style.textShadow = on ? `0 0 3px #fff,0 0 9px ${PINK},0 0 20px ${PINK},0 0 40px ${PINK}` : 'none';
      });
    };
  } else {
    const box = el('div', `position:absolute;width:max-content;transform-origin:50% 100%;`);
    const pillEl = el('div', `position:relative;padding:18px 34px 18px 30px;border-radius:44px;background:${LIGHT_CHROME};border:3px solid ${INK};
      box-shadow:0 7px 0 ${VIOLET},0 14px 24px rgba(0,0,0,.4),inset 0 3px 4px rgba(255,255,255,.9);white-space:nowrap;
      font-family:Unbounded;font-weight:700;font-size:34px;color:${INK};text-shadow:0 1px 0 rgba(255,255,255,.85);`, box);
    const pointer = el('div', `position:absolute;left:50%;bottom:-17px;width:30px;height:30px;margin-left:-15px;transform:rotate(45deg);
      background:linear-gradient(135deg,#f5f8fc,#9aa5b4);border-right:3px solid ${INK};border-bottom:3px solid ${INK};box-shadow:6px 6px 0 ${VIOLET};z-index:-1;`, box);
    const label = el('span', '', pillEl);
    const starSvg = sv('svg', { width: 54, height: 54, viewBox: '-1.2 -1.2 2.4 2.4' }, box);
    starSvg.style.cssText = 'position:absolute;right:-22px;top:-26px;overflow:visible';
    starSvg.innerHTML = `<defs><linearGradient id="csg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset=".5" stop-color="#9aa5b4"/><stop offset=".52" stop-color="#3a4252"/><stop offset="1" stop-color="#fff"/></linearGradient></defs>
      <path d="M0,-1 C0.1,-0.1 0.1,-0.1 1,0 C0.1,0.1 0.1,0.1 0,1 C-0.1,0.1 -0.1,0.1 -1,0 C-0.1,-0.1 -0.1,-0.1 0,-1Z" fill="url(#csg)" stroke="${INK}" stroke-width="2.2" vector-effect="non-scaling-stroke"/>`;
    const star = starSvg.querySelector('path');
    let lastText = null, bw = 0, bh = 0;
    measureW = text => { label.textContent = text; lastText = null; return pillEl.getBoundingClientRect().width + 30; };
    drawCallout = (c, t, ax, ay) => {
      if (!c) { box.style.opacity = 0; return; }
      if (c.text !== lastText) { label.textContent = c.text; lastText = c.text; const r = pillEl.getBoundingClientRect(); bw = r.width; bh = r.height; }
      const lt = t - c.s, rem = c.e - t;
      const sc = eOutBack(prog(lt, 0, 0.45), 2.2) * (1 - eInCubic(prog(rem, 0.3, 0)));
      box.style.opacity = 1;
      box.style.left = (ax - bw / 2) + 'px';
      box.style.top = (ay - 20 - bh) + 'px';
      box.style.transform = `scale(${sc}) rotate(${lerp(-12, 0, clamp(lt / 0.45)) + 1.5 * Math.sin(t * 2.2)}deg)`;
      star.setAttribute('transform', `rotate(${t * 60}) scale(${0.85 + 0.15 * Math.sin(t * 5)})`);
    };
  }
  // real callout widths, so the bubble never leaves the screen
  T.callouts.forEach(c => { c.hw = measureW(c.text) / 2; });
  const halfW = c => c.hw;

  return function render(t) {
    // captions
    caps.forEach(c => {
      const vis = t >= c.s && t < c.end;
      c.wrap.style.display = vis ? 'block' : 'none';
      if (!vis) return;
      const lt = t - c.s;
      const a = eOutCubic(prog(lt, 0, 0.18));
      if (PART === 1) c.wrap.style.transform = `translateY(calc(-50% + ${lerp(16, 0, a)}px))`, c.wrap.style.opacity = a;
      else if (PART === 2) c.wrap.style.transform = 'translateY(-50%)', c.wrap.style.opacity = lt < 0.12 ? (hash(Math.floor(lt * 30) + c.s) > 0.4 ? 1 : 0.3) : 1;
      else c.wrap.style.transform = `translateY(-50%) scale(${lerp(0.7, 1, eOutBack(prog(lt, 0, 0.2), 2.5))})`, c.wrap.style.opacity = prog(lt, 0, 0.06);
      // active word = last word whose start has passed
      let act = -1; c.words.forEach((w, i) => { if (t >= w.t - 0.03) act = i; });
      c.words.forEach((w, i) => {
        (i === act ? capStyle.on : capStyle.off)(w.s);
        w.s.style.transform = i === act ? 'scale(1.06)' : 'none';
      });
    });
    // callout
    const c = T.callouts.find(c => t >= c.s && t < c.e);
    if (c) {
      const hp = headAt(t);
      const hw = halfW(c);
      const ax = clamp(hp.x, hw + 30, W - hw - 30);
      const ay = clamp(hp.y - 30, 440, 1150);
      drawCallout(c, t, ax, ay);
    } else drawCallout(null, t);
  };
}

// ---------- boot ----------
let render = () => {};
const HOLD = +(Q.get('hold') || 0), HOLD_AT = 2.4;
window.renderAt = t => { RT = t; render(SCENE === 'intro' && t > HOLD_AT ? Math.max(HOLD_AT, t - HOLD) : t); };
const FONTS = ['700 40px Syne', '800 40px Syne', 'italic 600 40px "Cormorant Garamond"', '40px "Tilt Neon"', '40px Monoton',
  '400 40px Unbounded', '700 40px Unbounded', '900 40px Unbounded'];
window.ready = Promise.all(FONTS.map(f => document.fonts.load(f))).then(() => {
  render = SCENE === 'track' ? buildTrack() : [buildLiquid, buildNeon, buildY2K][PART - 1](SCENE);
  render(+(Q.get('t') || 0));
  return true;
});
