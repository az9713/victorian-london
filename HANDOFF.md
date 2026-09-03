# HANDOFF — resume point for victorian-london

**Read this first each new session.** Then `HANDOVER.md` (the shipped-build
document: how to play, what shipped, verification, perf, gotchas). Full
per-stage history and every judge-loop trajectory: `HANDOFF-HISTORY.md`.
Local git repo, NO remote by design — commits + tags are the durable record.

## Current state (as of 2026-09-02, tag `ambient-v1`, commit 35ff0bf)
- Six stages shipped at `ship-v1` (051dedd), then night grade (20cab0a), then the
  ambient pass (35ff0bf = `ambient-v1`). Gate 16/16 at `ambient-v1`. Tree clean.
- **Why the atmosphere work happened (2026-09-02 finding, from the operator):** the shipped
  build did not match `research/victorian-london.md` §7/§10 — night pea-souper,
  gaslight pools, soot brick, crowds. Root cause: `refpack/README.md` took only the
  NUMBERS from the research; the atmosphere sections never became spec lines, and
  the approved tier-2 hero was a DAY market, so stage 4 graded to daylight.
  **Lesson for the next world: write an Atmosphere block into the refpack before
  stage 1.**
- Night grade now in `sandbox/index.html`: sky+fog `0x3d3226`, fog 8→40 m,
  `HemisphereLight(0x4a4030, 0x3a3226, 3.5)`, moon 0.4, one warm `PointLight`
  (2600 K, 40 cd, 14 m) per gas lamp, self-lit lamp head.
- The teal column in play is the route checkpoint beacon (`MeshBasicMaterial`,
  unlit, opacity 0.10). Not a defect.

## Ambient pass — DONE 2026-09-02, tag `ambient-v1` (commit 35ff0bf), gate 16/16
All in `sandbox/index.html` + `sandbox/assets.js`, no new files/deps:
- Wet cobbles (`roughness` 0.35), soot brick tint `0x7a6a58` / stone `0x9a948a`
  (`0x5a4a3a` rendered walls black), lamp halo sprite 3 m + far corona 9 m, flicker,
  12 NPCs (4 costermonger `spawnNPC('')`, 5 flower girls, 3 constables), ghost signs
  BOVRIL / PEAR'S SOAP / TRUMAN'S ALES, 107 bollards x=52 z 26–185 WITH colliders
  (not z>185: route crosses that kerb at z≈248), beacon opacity 0.10.
- Sound in `startAmbience()`: murmur 300–2000 Hz, cab pass (hooves + axle rattle)
  every 20–40 s, bell every 60 s, viaduct train rumble every 2–4 min scaled by
  distance to z=10. `footstep(sprint, vol)` — `vol!==1` calls skip `stepCount`.
- **Black-wall fix:** cause was light level, not normals (walls got 0.5 × near-black
  hemisphere ground term). Now `HemisphereLight(0x4a4030, 0x3a3226, 3.5)`, moon 0.4.
  Characters are emissive `[1,1,1]` in the GLB, so they read bright regardless.
- Gin palace: warm glazing strip on the x=69 front + 3 PointLights + halos.
- Drifting fog: 36 sprites on 6 street axes, `fogTick()`; `fog:false` halos.
- `verify/gate.mjs` NPC check is now `>= 2` (was `=== 2`).
- Perf: idle 68 fps with crowd vs 70 without on a quiet run; a later run read 49 on
  a loaded machine (37% CPU idle, 36 chrome procs). A/B: fog sprites and palace lights
  cost 0. Re-measure with `verify/datum.mjs` on a quiet machine before trusting.
- **Do not open the game in a second Chrome window while gate/look/datum run** —
  the hidden window's rAF throttles to 1 fps and the tour fails.

## Next task
Remaining atmosphere items, in order (from research §7/§10):
1. Vendor cries (needs audio files or speech synth — no file-free path). Ask the operator.
2. Handheld lantern on one constable (one PointLight parented; iGPU cost).
3. Content: barrows, horse troughs, crates; chimney smoke; soot gradient by height.
4. `?day=1` switch only if the old grade is wanted back.
Then judge: fresh look tour (`node sandbox/verify/look.mjs`) vs refpack, on a quiet machine.

## Play it
`cd ~/Downloads/projects/victorian-london && python -m http.server 8123 -d sandbox`
then open `http://localhost:8123` in Chrome. (Running it from inside `sandbox/`
with `-d sandbox` 404s — the flag is relative to cwd.)

## Where to read things (reference, don't re-derive)
- `HANDOVER.md` — the ship document (as of `ship-v1`; predates the night grade).
- `research/victorian-london.md` — the atmosphere target: §7 (fog, gaslight,
  sound, smell) and §10 "Five Visual Signatures". Treat as spec now, not background.
- `refpack/README.md` — the spatial authority (datum, landmarks, route). Numbers only.
- `sandbox/index.html` + `layout.js` + `assets.js` — the entire game (~700 lines).
- `sandbox/verify/` — `gate.mjs` (acceptance), `feel.mjs`, `look.mjs`
  (lookdev tour → `verify/look/*.png`; brick-lane / rookery / ginpalace are
  current night-grade shots, the rest are stale DAY-grade), `inspect.mjs`,
  `datum.mjs` (perf). All need the server on 8123 and a VISIBLE Chrome window.
- Pipeline skills (plugin `remakebench-skills`): `game-production-stages` first.

## Session-transient scratch (regenerate; durable record is `sandbox/verify/`)
Every committed tool lives under `sandbox/verify/`. Two throwaway patterns used
on 2026-09-02, deliberately NOT committed:
- **Fast idle-fps probe** (`datum.mjs` takes 85 s; this takes 20 s and records no
  video): a ~10-line Playwright script — launch headed 1280x720, goto
  `http://localhost:8123/` + optional query, `sleep 20_000`, print
  `__game.fps` and `__game.npcs.length`. Drop it in `verify/`, run, delete.
- **A/B a feature's fps cost:** `sed -i` the loop bound or array to empty
  (e.g. `for (let i=0;i<6;i++)` → `i<0`), re-probe, `sed -i` it back, then
  `grep -c` to confirm the restore. Verified fog sprites and gin-palace lights
  each cost 0 fps this way.
- **Aerial shot:** load `/?fault=cam` (290 m debug camera, fog off) and screenshot.
  It keeps the night lights, so the aerial is now dark.

## How to work (essentials)
- Gate/perf only on a QUIET machine — Blender renders starve rAF and corrupt
  every measurement (walk measured 1.7 m/s vs 4.0 once).
- Judge loops: fresh judge per round, `model: sonnet`, batch = min score, exit is
  pass or operator stop. >90 min silent = TaskStop + respawn with a tighter brief.
  Tell judges clay renders cannot show texture, or they fail slate as "flat gray".
- Verify any judge finding on an untouched asset against file mtimes first.
- Commit + tag every playable milestone.
