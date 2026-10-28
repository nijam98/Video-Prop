// Render an overlay scene to a transparent PNG sequence.
// usage: node render.js <outDir> <durationSec> <fps> "<query string>" [t1,t2,... for stills only]
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const [outDir, dur, fps, query, stills] = process.argv.slice(2);
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => { console.error('PAGE ERROR', e); process.exit(1); });
  const url = 'file://' + path.join(__dirname, 'overlay.html') + '?' + query;
  await page.goto(url);
  await page.evaluate(() => window.ready);
  const times = stills
    ? stills.split(',').map(Number)
    : Array.from({ length: Math.round(+dur * +fps) }, (_, i) => i / +fps);
  for (let i = 0; i < times.length; i++) {
    await page.evaluate(t => window.renderAt(t), times[i]);
    const name = stills ? `still_${times[i].toFixed(2)}.png` : `f_${String(i).padStart(4, '0')}.png`;
    await page.screenshot({ path: path.join(outDir, name), omitBackground: true });
  }
  await browser.close();
  console.log(`rendered ${times.length} frames -> ${outDir}`);
})();
