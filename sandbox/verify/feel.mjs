// Stage-5 feel probe — MEASURED, not asserted. Two checks the gate doesn't cover:
// 1. NPC soft body: sprinting through the constable's beat may never overlap him.
// 2. Sprint FOV kick: fov widens ~76 under sprint, returns ~70 at rest.
// Usage: node verify/feel.mjs   (server on 8123)
import { chromium } from 'playwright';

const sleep = ms => new Promise(r => setTimeout(r, ms));
const browser = await chromium.launch({ headless: false,
  args: ['--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding'] });
const page = await (await browser.newContext({ viewport: { width: 1280, height: 720 } })).newPage();
await page.goto('http://localhost:8123/');
const kb = page.keyboard;
for (let i = 0; i < 80; i++) { if (await page.evaluate(() => __game.world)) break; await sleep(500); }
await sleep(2000);

let pass = true;
const check = (name, ok, detail) => { pass &&= ok; console.log(`${ok ? 'PASS' : 'FAIL'}  ${name} — ${detail}`); };

// -- helpers reused from the gate’s steering loop --
const g = () => page.evaluate(() => ({ x: __game.x, z: __game.z, yaw: __game.yaw,
  npcs: __game.npcs, fov: __game.fov }));
async function driveTo(tx, tz, tol, timeoutMs) {
  const t0 = Date.now(); let held = { L: false, R: false };
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
    await sleep(100);
  }
  for (const k of ['KeyW', 'ShiftLeft', 'ArrowLeft', 'ArrowRight']) await kb.up(k);
}

// 1. FOV kick, measured at rest -> sprint -> rest
const fRest0 = (await g()).fov;
await kb.down('ShiftLeft'); await kb.down('KeyW'); await sleep(1200);
const fSprint = (await g()).fov;
await kb.up('KeyW'); await kb.up('ShiftLeft'); await sleep(1200);
const fRest1 = (await g()).fov;
check('sprint FOV kick', fSprint > 74 && fRest0 < 71 && fRest1 < 71,
  `rest ${fRest0.toFixed(1)} -> sprint ${fSprint.toFixed(1)} -> rest ${fRest1.toFixed(1)}`);

// 2. NPC soft body: intercept the constable on his beat and sprint through him for 6 s
{
  // reach the constable's beat (x~57-65) via the viaduct street, then CHASE the
  // moving target for up to 90 s, re-steering at his live position every tick
  for (const [wx, wz] of [[240, 21], [170, 21], [100, 21], [62, 30]]) await driveTo(wx, wz, 5, 60_000);
  let minD = 1e9, contactMs = 0;
  const t0 = Date.now();
  await kb.down('KeyW'); await kb.down('ShiftLeft');
  let held = { L: false, R: false };
  while (Date.now() - t0 < 90_000) {
    const s = await g();
    const n = s.npcs.find(q => q.x < 100) ?? s.npcs[0];   // constable beat x~57-65; array order is load order
    const d = Math.hypot(n.x - s.x, n.z - s.z);
    if (d < 5) { minD = Math.min(minD, d); }
    if (d < 1.2) { contactMs += 100; if (contactMs > 4000) break; }   // 4 s pressed against him
    let err = Math.atan2(-(n.x - s.x), -(n.z - s.z)) - s.yaw;
    while (err > Math.PI) err -= 2 * Math.PI;
    while (err < -Math.PI) err += 2 * Math.PI;
    const wL = err > 0.08, wR = err < -0.08;
    if (wL !== held.L) { await (wL ? kb.down('ArrowLeft') : kb.up('ArrowLeft')); held.L = wL; }
    if (wR !== held.R) { await (wR ? kb.down('ArrowRight') : kb.up('ArrowRight')); held.R = wR; }
    if (Math.abs(err) > 0.9) await kb.up('KeyW'); else await kb.down('KeyW');
    await sleep(100);
  }
  for (const k of ['KeyW', 'ShiftLeft', 'ArrowLeft', 'ArrowRight']) await kb.up(k);
  check('npc soft body blocks pass-through', contactMs > 1000 && minD > 0.45,
    `min distance ${minD.toFixed(2)} m with ${contactMs} ms of pressing into him (never overlapped)`);
}

await browser.close();
console.log(pass ? 'FEEL PROBE PASS' : 'FEEL PROBE FAIL');
process.exit(pass ? 0 : 1);
