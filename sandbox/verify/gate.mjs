// verify-by-playing gate driver — stage 1 sandbox.
// Real CDP input via Playwright (keyboard.down/up = held keys), telemetry is READ-ONLY.
// Usage: node gate.mjs [--fault=deadkeys|seal|cam]  (fault runs must FAIL — red-test)
// Headed browser: the sim runs on rAF and requires a visible pane (documented in index.html).
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(here, 'out');
fs.mkdirSync(OUT, { recursive: true });
const FAULT = (process.argv.find(a => a.startsWith('--fault=')) || '').split('=')[1] || null;
const BASE = 'http://localhost:8123/';
const ROUTE_TIMEOUT_MS = FAULT ? 25_000 : 300_000;

const checks = [];
function check(name, ok, detail) { checks.push({ name, ok, detail }); console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? ' — ' + detail : ''}`); }
const sleep = ms => new Promise(r => setTimeout(r, ms));

// ---- provenance: the server must be serving the current bytes on disk ----
const disk = fs.readFileSync(path.join(here, '..', 'index.html'), 'utf8');
const served = await (await fetch(BASE + 'index.html')).text();
check('provenance: served bytes == disk bytes', served === disk);

const browser = await chromium.launch({ headless: false,
  args: ['--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding'] });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, recordVideo: FAULT ? undefined : { dir: OUT, size: { width: 1280, height: 720 } } });
const page = await context.newPage();
await page.goto(BASE + (FAULT ? `?fault=${FAULT}` : ''));
await sleep(1200);
const kb = page.keyboard;

const g = () => page.evaluate(() => ({
  x: __game.x, z: __game.z, yaw: __game.yaw, cp: __game.cp, cam: __game.activeCamera,
  done: __game.routeDone, secs: __game.routeSeconds, frames: __game.fps ? __game.fps.frames : 0,
  fpsMed: __game.fps ? __game.fps.median : null, downs: __probe.downs, ups: __probe.ups,
  route: __game.route,
}));

// ---- proof 1: input-liveness (unbound key, press+release seen by the app) ----
for (let i = 0; i < 60; i++) {            // wait for the asset upgrade to finish loading
  const w = await page.evaluate(() => __game.world);
  if (w) break; await sleep(500);
}
await sleep(2500);                        // let texture upload / first-frame jank settle
let s0 = await g();
await kb.down('KeyX'); await sleep(80); await kb.up('KeyX'); await sleep(80);
let s1 = await g();
check('liveness: app saw unbound-key press+release', s1.downs === s0.downs + 1 && s1.ups === s0.ups + 1,
  `downs ${s0.downs}->${s1.downs} ups ${s0.ups}->${s1.ups}`);

// ---- proof 4a: verbs measured — walk speed, then sprint ~2x ----
await kb.down('KeyW'); await sleep(1500); await kb.up('KeyW'); await sleep(120);
let s2 = await g();
const walkDist = Math.hypot(s2.x - s1.x, s2.z - s1.z);
check('verb: W walk moved the player', walkDist > 3, `${walkDist.toFixed(1)} m in 1.5 s`);
await kb.down('ShiftLeft'); await kb.down('KeyW'); await sleep(1500); await kb.up('KeyW'); await kb.up('ShiftLeft'); await sleep(120);
let s3 = await g();
const sprintDist = Math.hypot(s3.x - s2.x, s3.z - s2.z);
check('verb: sprint ≈ 2x walk (measured)', sprintDist / Math.max(walkDist, 0.01) > 1.5 && sprintDist / Math.max(walkDist, 0.01) < 2.6,
  `walk ${walkDist.toFixed(1)} m vs sprint ${sprintDist.toFixed(1)} m`);

// ---- proof 4b: arrow-key camera changes yaw ----
await kb.down('ArrowLeft'); await sleep(400); await kb.up('ArrowLeft'); await sleep(80);
let s4 = await g();
check('verb: arrow key turns the camera', Math.abs(s4.yaw - s3.yaw) > 0.3, `yaw ${s3.yaw.toFixed(2)} -> ${s4.yaw.toFixed(2)}`);

// ---- verb: footsteps fire while moving (counter measured; audio is procedural) ----
{
  const s = await page.evaluate(() => __game.steps);
  await kb.down('KeyW'); await sleep(1300); await kb.up('KeyW'); await sleep(100);
  const e = await page.evaluate(() => __game.steps);
  check('verb: footsteps fire while walking', e - s >= 2, `${e - s} steps in 1.3 s`);
}

// ---- ambient NPCs: present and actually moving (measured) ----
{
  let a = await page.evaluate(() => __game.npcs);
  for (let i = 0; i < 20 && a.length < 2; i++) { await sleep(500); a = await page.evaluate(() => __game.npcs); }
  await sleep(4000);
  const b = await page.evaluate(() => __game.npcs);
  const moved = a.length === 2 && b.length === 2 &&
    a.some((p, i) => Math.hypot(b[i].x - p.x, b[i].z - p.z) > 0.8);
  check('npcs: 2 present, at least one moving', moved,
    `${a.length} loaded; states ${b.map(n => n.state).join(',')}`);
}

// ---- proof (2b): rig lives — loader read-back + MEASURED joint motion ----
let rigInfo = null;
for (let i = 0; i < 50; i++) { rigInfo = await page.evaluate(() => __game.rig); if (rigInfo) break; await sleep(300); }
check('rig: character loaded through GLTFLoader', !!rigInfo && rigInfo.bones > 20,
  rigInfo ? `${rigInfo.bones} bones, foot bone "${rigInfo.footBone}"` : 'not loaded');
if (rigInfo) {
  const rel = async () => { const r = await page.evaluate(() => ({ f: __game.rig.foot, x: __game.x, z: __game.z }));
    return r.f ? [r.f[0] - r.x, r.f[1], r.f[2] - r.z] : null; };
  const accum = async (n) => { let prev = await rel(), acc = 0;
    for (let i = 0; i < n; i++) { await sleep(120); const c = await rel();
      acc += Math.hypot(c[0] - prev[0], c[1] - prev[1], c[2] - prev[2]); prev = c; } return acc; };
  const idleAcc = await accum(10);                      // baseline: idle sway only
  await kb.down('KeyW');
  const walkAcc = await accum(10);                      // legs must actually swing
  await kb.up('KeyW'); await sleep(150);
  check('rig: measured joint motion while walking', walkAcc > 0.4 && walkAcc > idleAcc * 1.5,
    `foot swing ${walkAcc.toFixed(2)} m walking vs ${idleAcc.toFixed(2)} m idle`);
}

// ---- landmark evidence helpers: face a heading / tilt, with real arrow keys ----
async function faceYaw(target) {
  for (let i = 0; i < 60; i++) {
    const s = await g();
    let err = target - s.yaw;
    while (err > Math.PI) err -= 2 * Math.PI;
    while (err < -Math.PI) err += 2 * Math.PI;
    if (Math.abs(err) < 0.1) break;
    const k = err > 0 ? 'ArrowLeft' : 'ArrowRight';
    await kb.down(k); await sleep(90); await kb.up(k);
  }
}
async function tiltTo(target) {
  for (let i = 0; i < 40; i++) {
    const p = await page.evaluate(() => __game.pitch);
    if (Math.abs(p - target) < 0.1) break;
    const k = target > p ? 'ArrowUp' : 'ArrowDown';
    await kb.down(k); await sleep(90); await kb.up(k);
  }
}

// ---- landmark evidence 1: turn round at the north end — the viaduct closes the slice ----
if (!FAULT) {
  await faceYaw(0);                       // face north
  await tiltTo(0.1);
  await sleep(300);
  await page.screenshot({ path: path.join(OUT, 'viaduct-north.png') });
  await faceYaw(Math.PI);                 // back to south
  await tiltTo(-0.25);
}

// ---- proof 2: route traversal with REAL held keys, steering feedback loop ----
const camSamples = new Set();
let stuckEvents = 0;
const t0 = Date.now();
await kb.down('KeyW'); await kb.down('ShiftLeft');
let lastPos = null, lastProgress = Date.now(), lastCp = -1, held = { L: false, R: false };
let routeDone = false, routeSecs = null;
while (Date.now() - t0 < ROUTE_TIMEOUT_MS) {
  const s = await g();
  camSamples.add(s.cam);
  if (s.done) { routeDone = true; routeSecs = s.secs; break; }
  const [cx, cz] = s.route[s.cp];
  const dx = cx - s.x, dz = cz - s.z;
  let err = Math.atan2(-dx, -dz) - s.yaw;
  while (err > Math.PI) err -= 2 * Math.PI;
  while (err < -Math.PI) err += 2 * Math.PI;
  const wantL = err > 0.08, wantR = err < -0.08;
  if (wantL !== held.L) { await (wantL ? kb.down('ArrowLeft') : kb.up('ArrowLeft')); held.L = wantL; }
  if (wantR !== held.R) { await (wantR ? kb.down('ArrowRight') : kb.up('ArrowRight')); held.R = wantR; }
  // big heading error: pause forward motion while turning
  if (Math.abs(err) > 0.9) { await kb.up('KeyW'); } else { await kb.down('KeyW'); }
  if (lastPos && Math.hypot(s.x - lastPos.x, s.z - lastPos.z) > 0.8) lastProgress = Date.now();
  if (Date.now() - lastProgress > 4000) {   // wall-stuck: strafe wiggle, alternating side
    stuckEvents++;
    const side = stuckEvents % 2 ? 'KeyA' : 'KeyD';
    await kb.down(side); await sleep(700); await kb.up(side);
    lastProgress = Date.now();
  }
  if (s.cp !== lastCp) {
    console.log(`  cp ${s.cp}/${s.route.length} reached, pos ${s.x.toFixed(0)},${s.z.toFixed(0)}, t+${((Date.now() - t0) / 1000).toFixed(0)}s`);
    if (!FAULT && s.cp === 3) await page.screenshot({ path: path.join(OUT, 'cp3-market.png') });
    if (!FAULT && s.cp === 9) {           // church forecourt: face the front, tilt up to the spire top
      for (const k of ['KeyW', 'ShiftLeft', 'ArrowLeft', 'ArrowRight']) await kb.up(k);
      held = { L: false, R: false };
      await faceYaw(Math.PI / 2);         // face west
      await tiltTo(1.25);
      await sleep(300);
      await page.screenshot({ path: path.join(OUT, 'church-spire.png') });
      await tiltTo(-0.25);
      await kb.down('KeyW'); await kb.down('ShiftLeft');
      lastProgress = Date.now();          // the photo stop is not a stuck event
    }
    lastCp = s.cp;
  }
  lastPos = s;
  await sleep(120);
}
for (const k of ['KeyW', 'ShiftLeft', 'ArrowLeft', 'ArrowRight', 'KeyA', 'KeyD']) await kb.up(k);
check('route: traversed end to end by walking', routeDone, routeDone ? `${routeSecs.toFixed(1)} s of play, ${stuckEvents} stuck-wiggles` : `stalled; last cp ${lastCp}`);
if (!FAULT && routeDone) await page.screenshot({ path: path.join(OUT, 'route-complete.png') });

// ---- proof (5): the Costermonger's Round — every mission verb pressed for real ----
if (routeDone) {
  const drive = async (tx, tz, tol, timeoutMs) => {
    const t0 = Date.now();
    await kb.down('KeyW'); await kb.down('ShiftLeft');
    let heldD = { L: false, R: false }, lastP = null, lastProg = Date.now(), wig = 0;
    let arrived = false;
    while (Date.now() - t0 < timeoutMs) {
      const s = await g();
      camSamples.add(s.cam);
      if (Math.hypot(s.x - tx, s.z - tz) < tol) { arrived = true; break; }
      let err = Math.atan2(-(tx - s.x), -(tz - s.z)) - s.yaw;
      while (err > Math.PI) err -= 2 * Math.PI;
      while (err < -Math.PI) err += 2 * Math.PI;
      const wL = err > 0.08, wR = err < -0.08;
      if (wL !== heldD.L) { await (wL ? kb.down('ArrowLeft') : kb.up('ArrowLeft')); heldD.L = wL; }
      if (wR !== heldD.R) { await (wR ? kb.down('ArrowRight') : kb.up('ArrowRight')); heldD.R = wR; }
      if (Math.abs(err) > 0.9) await kb.up('KeyW'); else await kb.down('KeyW');
      if (lastP && Math.hypot(s.x - lastP.x, s.z - lastP.z) > 0.8) lastProg = Date.now();
      if (Date.now() - lastProg > 3500) {
        const side = ++wig % 2 ? 'KeyA' : 'KeyD';
        await kb.down(side); await sleep(700); await kb.up(side);
        lastProg = Date.now();
      }
      lastP = s;
      await sleep(120);
    }
    for (const k of ['KeyW', 'ShiftLeft', 'ArrowLeft', 'ArrowRight']) await kb.up(k);
    return arrived;
  };
  // street-following waypoints per mission leg (targets come from the game's telemetry)
  const LEG_WAYPOINTS = [
    [[60, 280], [60, 155], [65, 150], [150, 150], [210, 150]],   // route end -> market
    [[200, 150], [180, 150]],                                    // market -> rookery door
    [[180, 150], [150, 150], [80, 150], [65, 150], [66, 184]],   // rookery -> gin palace
    [[55, 198]],                                                 // gin palace -> church
    [[60, 165], [65, 150], [150, 150], [210, 150]],              // church -> market
  ];
  let m = await page.evaluate(() => __game.mission);
  let ok = m.active === true;
  while (ok && m.target) {
    for (const [wx, wz] of LEG_WAYPOINTS[m.idx] ?? []) await drive(wx, wz, 6, 45_000);
    await drive(m.target[0], m.target[1], 3, 45_000);
    await kb.down('KeyE'); await sleep(120); await kb.up('KeyE'); await sleep(250);
    const next = await page.evaluate(() => __game.mission);
    if (next.idx === m.idx) { ok = false; break; }   // E did nothing => fail
    m = next;
  }
  check('mission: round completed with real E-interactions', ok && m.done,
    m.done ? `${m.seconds.toFixed(1)} s round` : `stalled at leg ${m.idx}/${m.total}`);
  if (!FAULT && m.done) await page.screenshot({ path: path.join(OUT, 'round-complete.png') });
}

// ---- proof 3: camera ownership across the whole session ----
check('camera: gameplay camera owned every sampled frame', camSamples.size === 1 && camSamples.has('gameplay'),
  `saw: ${[...camSamples].join(',') || 'none'}`);

// ---- disarm: harness releases everything and the app still responds ----
const d0 = await g();
await sleep(500);
const d1 = await g();
check('disarm: frames still advancing', d1.frames > 0 && d1.fpsMed > 20, `median ${d1.fpsMed?.toFixed(0)} fps`);
await kb.down('KeyX'); await sleep(60); await kb.up('KeyX'); await sleep(60);
const d2 = await g();
check('disarm: a fresh key still reaches the app', d2.downs === d1.downs + 1 && d2.ups === d1.ups + 1);
await kb.down('KeyW'); await sleep(400); await kb.up('KeyW'); await sleep(100);
const d3 = await g();
check('disarm: player still walkable after harness', Math.hypot(d3.x - d2.x, d3.z - d2.z) > 0.8);

await context.close();   // flushes the video
await browser.close();
const video = fs.readdirSync(OUT).find(f => f.endsWith('.webm'));
if (!FAULT && video) console.log(`video: out/${video}`);

const failed = checks.filter(c => !c.ok);
console.log(`\n${checks.length - failed.length}/${checks.length} checks passed${FAULT ? ` (fault=${FAULT}: this run SHOULD fail)` : ''}`);
process.exit(failed.length ? 1 : 0);
