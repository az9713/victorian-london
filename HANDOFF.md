# HANDOFF — resume point for victorian-london

**Read this first each new session.** Then `HANDOVER.md` (the shipped-build
document: how to play, what shipped, verification, perf, gotchas). Full
per-stage history and every judge-loop trajectory: `HANDOFF-HISTORY.md`.
Local git repo, NO remote by design — commits + tags are the durable record.

## Current state (as of 2026-09-02, commit after `ship-v1`)
- Six stages shipped at tag `ship-v1` (commit 051dedd). Gate `sandbox/verify/gate.mjs`
  16/16 on a quiet machine at that tag.
- **2026-09-02 finding (the operator):** the build did not match
  `research/victorian-london.md` §7/§10 (night pea-souper, gaslight pools, soot
  brick, crowds). Root cause: `refpack/README.md` took only the NUMBERS from the
  research; the atmosphere sections never became spec lines, and the approved
  tier-2 hero was a DAY market, so stage 4 graded to daylight.
- **Night grade applied** in `sandbox/index.html` (committed this session):
  sky+fog `0x3d3226`, fog 8→40 m, dim smog hemisphere + faint moon, one warm
  `PointLight` (2600 K, 40 cd, 14 m) per gas lamp, self-lit lamp head. Verified
  by loading in Chrome: dark street, warm pools, black between. No console errors.
- The teal column in play is the route checkpoint beacon (`index.html:342-344`,
  `MeshBasicMaterial`, unlit, so it now stands out at night). Not a defect.
- Gate NOT re-run after the night grade (lighting only; no collider change).

## Next task
- **Ambient richness pass — approved plan, the operator said "give a plan", not yet "go".**
  Confirm with the operator, then do in order (all in `sandbox/index.html` + `sandbox/assets.js`,
  no new files, no new deps, ~90 lines):
  1. Wet cobble sheen — ground material `roughness` 0.35 (`assets.js:164-175`).
  2. Soot brick — `MAT_TINT.brick` `0xb09c80` → ~`0x5a4a3a`; stone → ~`0x9a948a` (`assets.js:58`).
  3. Lamp glow halos — additive `Sprite` + radial `CanvasTexture` per lamp (~8 lines).
  4. Lamp flicker — keep lights in an array, intensity `40 + 6*sin(t*17+i)*rand` in tick.
  5. Crowd — ~10 more `spawnNPC` calls on Commercial St / Brick Lane / Dorset St / plaza;
     4-char change so `spawnNPC('')` loads `idle.glb`/`walk.glb` (costermonger).
     Mix 4 costermongers, 4 flower girls, 2 constables. Re-measure fps; iGPU risk.
  6. Sound layers in `startAmbience()` — crowd murmur (band-pass noise 300–2000 Hz),
     hooves (reuse `footstep()` in a 4-beat pattern every 20–40 s), church bell
     (220+440 Hz decaying, every 60 s). Procedural, no files.
  7. Ghost signs — `CanvasTexture` text planes ("BOVRIL", "PEAR'S SOAP") on 3 walls.
  8. Bollards — 0.85 m cylinders every 1.5 m along the Commercial St kerb, WITH colliders.
  9. Beacon opacity 0.28 → 0.10 (`index.html:343`).
  Then: play the route in Chrome; run `node sandbox/verify/gate.mjs` (step 8 adds
  colliders); read `__game.fps` at spawn — median under 60 → remove NPCs first.
  Commit + tag `ambient-v1`.
- Skipped on purpose: drifting fog patches, day/night cycle (`?day=1` switch if
  the old grade is wanted back), soot gradient by height, chimney smoke, barrows.
- If the user asks for anything else, that takes precedence.

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
  (lookdev tour → `verify/look/*.png`, all DAY-grade, stale), `inspect.mjs`,
  `datum.mjs` (perf). All need the server on 8123 and a VISIBLE Chrome window.
- Pipeline skills (plugin `remakebench-skills`): `game-production-stages` first.

## Session-transient scratch (nothing to regenerate)
Every tool this project used is committed under `sandbox/verify/`. The aerial
shot pattern: load `/?fault=cam` (fog-free 290 m debug camera) and screenshot.
`?fault=cam` drops fog but keeps the night lights — the aerial is now dark.

## How to work (essentials)
- Gate/perf only on a QUIET machine — Blender renders starve rAF and corrupt
  every measurement (walk measured 1.7 m/s vs 4.0 once).
- Judge loops: fresh judge per round, `model: sonnet`, batch = min score, exit is
  pass or operator stop. >90 min silent = TaskStop + respawn with a tighter brief.
  Tell judges clay renders cannot show texture, or they fail slate as "flat gray".
- Verify any judge finding on an untouched asset against file mtimes first.
- Commit + tag every playable milestone.
