// Stage 2c perf datum — greybox frame floor. Run on a QUIET machine (no Blender, no renders).
// Reports median/p95 frame rate idle and during sprint traversal, plus the real GL backend
// and rendered resolution. No video recording (it contends the measurement).
import { chromium } from 'playwright';

const sleep = ms => new Promise(r => setTimeout(r, ms));
const browser = await chromium.launch({ headless: false,
  args: ['--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding'] });
const page = await (await browser.newContext({ viewport: { width: 1280, height: 720 } })).newPage();
await page.goto('http://localhost:8123/');
await sleep(1500);

const env = await page.evaluate(() => {
  const c = document.querySelector('canvas');
  const gl = c.getContext('webgl2') || c.getContext('webgl');
  const dbg = gl.getExtension('WEBGL_debug_renderer_info');
  return {
    glRenderer: dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : 'masked',
    canvasPx: [c.width, c.height], cssPx: [c.clientWidth, c.clientHeight],
    dpr: devicePixelRatio, ua: navigator.userAgent.match(/Chrome\/[\d.]+/)?.[0],
  };
});
console.log('backend:', JSON.stringify(env, null, 1));

const stats = () => page.evaluate(() => {
  const f = __game.fps; return f ? { median: f.median, p95low: f.p95low, frames: f.frames } : null;
});
const reset = () => page.evaluate(() => { /* fps window is rolling 600 frames; just wait it out */ });

// idle datum: 25 s standing at spawn (rolling window fills with idle frames)
await sleep(25_000);
console.log('idle:', JSON.stringify(await stats()));

// play datum: sprint + steer along the route for 60 s (rolling window = pure play frames)
const kb = page.keyboard;
await kb.down('KeyW'); await kb.down('ShiftLeft');
const t0 = Date.now();
let held = { L: false, R: false };
while (Date.now() - t0 < 60_000) {
  const s = await page.evaluate(() => ({ x: __game.x, z: __game.z, yaw: __game.yaw, cp: __game.cp, done: __game.routeDone, route: __game.route }));
  if (s.done) break;
  const [cx, cz] = s.route[Math.min(s.cp, s.route.length - 1)];
  let err = Math.atan2(-(cx - s.x), -(cz - s.z)) - s.yaw;
  while (err > Math.PI) err -= 2 * Math.PI; while (err < -Math.PI) err += 2 * Math.PI;
  const wantL = err > 0.08, wantR = err < -0.08;
  if (wantL !== held.L) { await (wantL ? kb.down('ArrowLeft') : kb.up('ArrowLeft')); held.L = wantL; }
  if (wantR !== held.R) { await (wantR ? kb.down('ArrowRight') : kb.up('ArrowRight')); held.R = wantR; }
  await sleep(150);
}
console.log('play:', JSON.stringify(await stats()));
for (const k of ['KeyW', 'ShiftLeft', 'ArrowLeft', 'ArrowRight']) await kb.up(k);
await browser.close();
