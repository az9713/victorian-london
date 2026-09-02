# HANDOFF — resume point for victorian-london

**Read this first each new session.** Then `HANDOVER.md` (the shipped-build
document: how to play, what shipped, verification, perf, gotchas). Full
per-stage history and every judge-loop trajectory: `HANDOFF-HISTORY.md`.
Local git repo, NO remote by design — commits + tags are the durable record.

## Current state (as of commit 051dedd, tag `ship-v1`, 2026-09-02)
- **ALL SIX STAGES COMPLETE. The game is shipped.** Every stage tagged:
  `stage1-verified` → `stage2b-character-playable` → `2a-complete` →
  `stage3-assembly-pass` → `stage4-atmosphere` → `stage5-feel-pass` → `ship-v1`.
- Gate `sandbox/verify/gate.mjs`: **16/16** on a quiet machine; 3 fault-injection
  red-tests (`--fault=deadkeys|seal|cam`) each fail correctly.
- Perf datum (stage 6, quiet): idle 72.5 fps median / 69.4 p95-low; sprint play
  144.9 / 70.4; true 1280x720 dpr1, ANGLE D3D11 on the Intel iGPU, Chrome/151.
- Working tree clean. The 2026-09-01→02 session's goal ("finish stages 3-6")
  is met and its /goal loop is stopped.

## Play it
`cd ~/Downloads/projects/victorian-london && python -m http.server 8123 -d sandbox`
then open `http://localhost:8123` in Chrome. (Running it from inside `sandbox/`
with `-d sandbox` 404s — the flag is relative to cwd.)

## Next task
- **None required.** The build is shipped. If the operator wants more, the value-ordered
  open list is in `HANDOVER.md` § Open list — top item is deeper stage-4 mood
  (gas-lamp glow at dusk, drifting fog patches, crowd-murmur layers). All content
  wishes, no known defects.
- If the user asks for anything else, that takes precedence.

## Where to read things (reference, don't re-derive)
- `HANDOVER.md` — the ship document. Start here for anything about the build.
- `refpack/README.md` — the spatial authority (datum, landmarks, route).
- `sandbox/index.html` + `layout.js` + `assets.js` — the entire game (~700 lines).
- `sandbox/verify/` — `gate.mjs` (acceptance), `feel.mjs` (stage-5 probe),
  `look.mjs` (lookdev tour → `verify/look/*.png`), `inspect.mjs` (GLB prober),
  `datum.mjs` (perf). All need the server on 8123 and a VISIBLE Chrome window.
- Pipeline skills (plugin `remakebench-skills`): `game-production-stages` first.

## Session-transient scratch (nothing to regenerate)
Every tool this project used is committed under `sandbox/verify/`. The aerial
shot pattern: load `/?fault=cam` (fog-free 290 m debug camera) and screenshot.

## How to work (essentials)
- Gate/perf only on a QUIET machine — Blender renders starve rAF and corrupt
  every measurement (walk measured 1.7 m/s vs 4.0 once).
- Judge loops: fresh judge per round, `model: sonnet`, batch = min score, exit is
  pass or operator stop. >90 min silent = TaskStop + respawn with a tighter brief.
  Tell judges clay renders cannot show texture, or they fail slate as "flat gray".
- Verify any judge finding on an untouched asset against file mtimes first.
- Commit + tag every playable milestone.
