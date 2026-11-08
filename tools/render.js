// Render frames with headless Chromium and encode with ffmpeg.
//   node tools/render.js stills 0.5,12,27      -> build/stills/t_XX.png
//   node tools/render.js video [workers]        -> build/video.mp4 (no audio)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..');
const BUILD = path.join(ROOT, 'build');
const URL = 'file://' + path.join(ROOT, 'src', 'index.html');
fs.mkdirSync(BUILD, { recursive: true });

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });
  await page.goto(URL);
  await page.evaluate(() => window.ready);
  return page;
}
async function grab(page, f) {
  const data = await page.evaluate(f => { renderFrame(f); return document.getElementById('c').toDataURL('image/png'); }, f);
  return Buffer.from(data.split(',')[1], 'base64');
}

async function stills(times) {
  const browser = await chromium.launch();
  const page = await openPage(browser);
  const dir = path.join(BUILD, 'stills'); fs.mkdirSync(dir, { recursive: true });
  for (const t of times) {
    const f = Math.round(t * 30);
    fs.writeFileSync(path.join(dir, `t_${String(t).replace('.', '_')}.png`), await grab(page, f));
  }
  await browser.close();
}

async function segment(browser, k, f0, f1) {
  const page = await openPage(browser);
  const file = path.join(BUILD, `seg_${k}.mp4`);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
    '-x264-params', 'keyint=60', '-r', '30', file], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = f0; f < f1; f++) {
    const png = await grab(page, f);
    if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - f0) % 150 === 0) console.log(`seg ${k}: ${f - f0}/${f1 - f0} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close', c => c ? rej(new Error('ffmpeg ' + c)) : res()));
  await page.close();
  return file;
}

async function video(workers) {
  const browser = await chromium.launch();
  const total = 60 * 30, per = Math.ceil(total / workers);
  const jobs = [];
  for (let k = 0; k < workers; k++) jobs.push(segment(browser, k, k * per, Math.min(total, (k + 1) * per)));
  const files = await Promise.all(jobs);
  await browser.close();
  fs.writeFileSync(path.join(BUILD, 'list.txt'), files.map(f => `file '${f}'`).join('\n'));
  await new Promise((res, rej) => spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', path.join(BUILD, 'list.txt'), '-c', 'copy', path.join(BUILD, 'video.mp4')], { stdio: 'inherit' })
    .on('close', c => c ? rej(new Error('concat ' + c)) : res()));
  console.log('video ok');
}

const [mode, arg] = process.argv.slice(2);
if (mode === 'stills') stills(arg.split(',').map(Number)).catch(e => { console.error(e); process.exit(1); });
else video(Number(arg) || 4).catch(e => { console.error(e); process.exit(1); });
