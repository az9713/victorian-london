// Lookdev sampler — walks to named spots and shoots them. Stage 3/4 iteration tool.
// The gate is the acceptance test; this is the fast loop between gate runs.
// Usage: node verify/look.mjs [spot ...]   (no args = all)   -> verify/look/*.png
// No teleport exists by design, so every spot is reached by holding real keys.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(here, 'look');
fs.mkdirSync(OUT, { recursive: true });
const BASE = 'http://localhost:8123/';
const sleep = ms => new Promise(r => setTimeout(r, ms));

// A TOUR in walk order from spawn (290,20). via = street waypoints (beelines wedge
// into building pockets); stand/look chosen so each frame answers its `why`.
const TOUR = [
  // viaduct: stand in the x140-160 terrace-row gap so the camera has clear air behind
  ['viaduct',       { via: [[240, 21], [175, 21], [150, 30]],  x: 150, z: 42,  yaw: 0,           pitch: 0.15, why: 'viaduct arches closing the north edge' }],
  ['brick-lane',    { via: [[240, 21], [288, 30]],             x: 286, z: 120, yaw: Math.PI,     pitch: 0.15, why: 'roofline clutter down Brick Lane' }],
  ['market-pier',   { via: [[288, 150], [260, 150]],           x: 232, z: 150, yaw: Math.PI,     pitch: 0.05, why: 'brick texel size on the market piers' }],
  ['rookery',       { via: [[200, 150], [180, 150]],           x: 171, z: 152, yaw: Math.PI,     pitch: 0.20, why: 'rookery north front from Dorset St' }],
  ['terrace-brick', { via: [[160, 150]],                       x: 150, z: 156, yaw: Math.PI,     pitch: 0.10, why: 'the pocket south of George Yard mouth' }],
  ['gy-flank',      { via: [[150, 150], [150, 120]],           x: 150, z: 92,  yaw: 0,           pitch: 0.05, why: 'graveyard flank walls at walking distance' }],
  ['ginpalace',     { via: [[150, 150], [100, 150], [65, 150], [65, 185]], x: 70, z: 196, yaw: 0, pitch: 0.10, why: 'gin palace frontage' }],
  // church: open street at x55-65, pitch high enough that the +50 m spire enters frame;
  // standing further east puts the camera inside buildings or the character
  ['church',        { via: [[65, 185], [60, 200]],             x: 55,  z: 207, yaw: Math.PI / 2, pitch: 1.0,  why: 'church + spire from Commercial St' }],
];

const want = process.argv.slice(2).filter(a => !a.startsWith('-'));
const spots = TOUR.filter(([k]) => !want.length || want.includes(k));

const browser = await chromium.launch({ headless: false,
  args: ['--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding'] });
const page = await (await browser.newContext({ viewport: { width: 1280, height: 720 } })).newPage();
await page.goto(BASE);
const kb = page.keyboard;

for (let i = 0; i < 80; i++) {                 // wait for GLBs + textures
  if (await page.evaluate(() => __game.world)) break;
  await sleep(500);
}
await sleep(2500);

const g = () => page.evaluate(() => ({ x: __game.x, z: __game.z, yaw: __game.yaw, pitch: __game.pitch }));

async function faceYaw(target) {
  for (let i = 0; i < 90; i++) {
    const s = await g();
    let err = target - s.yaw;
    while (err > Math.PI) err -= 2 * Math.PI;
    while (err < -Math.PI) err += 2 * Math.PI;
    if (Math.abs(err) < 0.06) return;
    const k = err > 0 ? 'ArrowLeft' : 'ArrowRight';
    await kb.down(k); await sleep(Math.abs(err) > 0.5 ? 120 : 45); await kb.up(k);
  }
}
async function tiltTo(target) {
  for (let i = 0; i < 60; i++) {
    const p = (await g()).pitch;
    if (Math.abs(p - target) < 0.06) return;
    const k = target > p ? 'ArrowUp' : 'ArrowDown';
    await kb.down(k); await sleep(45); await kb.up(k);
  }
}
// walk to (tx,tz) with the same steering loop the gate uses
async function walkTo(tx, tz, tol = 2.5, timeoutMs = 90_000) {
  const t0 = Date.now();
  let held = { L: false, R: false }, lastP = null, lastProg = Date.now(), wig = 0;
  await kb.down('KeyW'); await kb.down('ShiftLeft');
  while (Date.now() - t0 < timeoutMs) {
    const s = await g();
    if (Math.hypot(s.x - tx, s.z - tz) < tol) break;
    let err = Math.atan2(-(tx - s.x), -(tz - s.z)) - s.yaw;
    while (err > Math.PI) err -= 2 * Math.PI;
    while (err < -Math.PI) err += 2 * Math.PI;
    const wL = err > 0.08, wR = err < -0.08;
    if (wL !== held.L) { await (wL ? kb.down('ArrowLeft') : kb.up('ArrowLeft')); held.L = wL; }
    if (wR !== held.R) { await (wR ? kb.down('ArrowRight') : kb.up('ArrowRight')); held.R = wR; }
    if (Math.abs(err) > 0.9) await kb.up('KeyW'); else await kb.down('KeyW');
    if (lastP && Math.hypot(s.x - lastP.x, s.z - lastP.z) > 0.8) lastProg = Date.now();
    if (Date.now() - lastProg > 3500) {
      const side = ++wig % 2 ? 'KeyA' : 'KeyD';
      await kb.down(side); await sleep(700); await kb.up(side);
      lastProg = Date.now();
    }
    lastP = s;
    await sleep(110);
  }
  for (const k of ['KeyW', 'ShiftLeft', 'ArrowLeft', 'ArrowRight']) await kb.up(k);
}

for (const [name, s] of spots) {
  for (const [wx, wz] of s.via ?? []) await walkTo(wx, wz, 5, 60_000);
  await walkTo(s.x, s.z);
  await faceYaw(s.yaw);
  await tiltTo(s.pitch);
  await sleep(500);
  const at = await g();
  await page.screenshot({ path: path.join(OUT, `${name}.png`) });
  console.log(`${name}: stood ${at.x.toFixed(0)},${at.z.toFixed(0)} (wanted ${s.x},${s.z}) — ${s.why}`);
}

const fps = await page.evaluate(() => __game.fps);
console.log(`fps median ${fps?.median.toFixed(0)} over ${fps?.frames} frames`);
await browser.close();
