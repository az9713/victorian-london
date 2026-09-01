# HANDOFF — resume point for victorian-london

**Read this first each new session.** Local git repo, NO remote — commits are the
durable record.

## ACTIVE GOAL (session-scoped, 2026-08-31): finish the playable game autonomously.
Success = fully functional game, pleasant UX, verified by playing (CDP/Playwright/
claude-in-chrome). Meshy spend authorized (1408 credits). Stop only for: video-gen
quotes, or a judge loop that will not converge.

## Stage log
- **Stage 0 COMPLETE** (commit 34b5fef): refpack + congruence + operator-approved hero.
- **Stage 1 COMPLETE + VERIFIED** (tags `stage1-sandbox-playable`, `stage1-verified`):
  Three.js greybox sandbox (`sandbox/index.html` + `sandbox/layout.js` = single layout
  source). Gate `sandbox/verify/gate.mjs`: 10/10 checks, real Playwright CDP held-key
  input, full route walked, 3 fault-injection red-tests each fail correctly.
  Independent reviewer subagent PASSED the evidence (2 rounds; round 1 failed on
  never-framed viaduct/spire → fixed by capture, pitch clamp 1.3).
  Serve: `python -m http.server 8123 -d sandbox`. Gate: `node verify/gate.mjs`.
- **Stage 2c datum (greybox):** median 145 fps, p95 141, idle == sprint, 1280x720
  dpr1, ANGLE D3D11 on Intel UHD iGPU (NOT the RTX 3050), Chrome/151. `datum.mjs`.
- **Stage 2 IN FLIGHT** (commit 9f9b566): 5 Polyhaven 2K PBR sets in
  `sandbox/assets/pbr/` (scales in manifest.json). Character 2b: rigged costermonger
  + Idle(0)/Casual_Walk(30)/Run_02(14) clips in `meshy/costermonger/` (GLBs
  committed). NEXT: 2a builder batches (Blender headless → GLB), 2b Three.js
  integration (rig proof = measured joint motion through GLTFLoader).
- **Stage 2b DONE** (tag `stage2b-character-playable`): costermonger in-game,
  rig proven (24 bones, LeftFoot, 1.4 m foot swing measured). Camera occlusion in.
- **Assembly ready** (commit 8689300): `sandbox/assets.js` swaps greybox for GLBs
  at layout records when files appear in `sandbox/assets/models/`; shared PBR
  materials bound BY NAME (brick/slate/planks/plaster/stone/iron/glass/...);
  ground is cobbled. Builder GLB contract = briefs in `blender/briefs/`.
- **Stage 5 skeleton DONE** (tag `stage5-mission-skeleton`): Costermonger's Round
  mission (pickup + 3 deliveries + return, E-interact, ding, timer) unlocks after
  the route tour; procedural footsteps; gate = 14 checks incl. mission drive.
- **NPCs rigged**: `meshy/flowergirl/`, `meshy/constable/` (idle+walk GLBs).
  Wander behaviour still to write (stage 5 polish).
- **NPCs + mission live** (tag `stage5-mission-skeleton`, commit 2199e80): gate
  is 15 checks, all passing, incl. mission round + NPC motion (measured).
- **2a batches:** B4 PASSED (tag `2a-terraces-pass`), B2 PASSED (tag
  `2a-church-ginpalace-pass`). B1 and B3 still open — see PAUSED block below.
  The assembled game passes the 15/15 gate with current assets (48 fps median).

## ⏸ PAUSED by the operator 2026-08-31 19:40 PT — resume here
the operator paused the pipeline to switch the SESSION model to Sonnet (7% Fable
left until a reset >2 days out). Both running builders were TaskStop'd at
19:38; their WIP is committed (117c7b3). NO agents are running. On resume,
spawn subagents plain (no model override needed once the session is Sonnet).

**Loop mechanics (unchanged):** builder gets BRIEF-COMMON.md + batch brief +
fixlist verbatim; on "done" the parent runs `node scripts/glb_inventory.mjs`,
mtime-checks every render against its .blend (renders must postdate), commits
pre-judge, then spawns a FRESH judge with asset-judge-loop
references/judge-prompt.md + renders + manifest + inventory + refpack tiers,
threshold 4, batch = min score. Fresh judge and fresh builder every round.
Lessons that cost rounds: (1) builders die SILENTLY — file-silent >1h means
check ListAgents; (2) builders see intent, not pixels — fixlists must use
COUNTABLE properties (see B1-r5.md); (3) never message a dead/stopped
builder, spawn fresh from the fixlist.

**B1 (market/stall/barrel/crate/sacks):** r4 judged FAIL min 2 — but market
is now 5 (gable rib fan works), barrel 4, crate 4. ONLY two features remain:
stall tie (4 rounds: washers→clips→uniform rings) and sack-1 neck
(rod→beak). Fixlist `blender/fixlists/B1-r5.md` (countable properties).
Builder-B1-r5 was stopped MID-ROUND at 19:38: it had rebuilt stall tie
(stall.blend 19:37, glb exported, `_verify_tie_zoom.png` check frame) and
sacks (19:30) but NOT delivered/re-rendered final frames or manifest.
Resume: fresh builder, B1-r5.md verbatim, inherit the WIP blends, verify
each countable property in pixels, deliver. Then fresh judge (r5).
ESCALATION RULE: if r5 fails on the same two features, that is the "loop
will not converge" stop — bring the operator options (stronger model on these two
small features / operator eyeball / accept at 3) instead of a blind r6.

**B3 (rookery/viaduct/gy-flank/gaslamp/pillarbox):** r2 scores: pillarbox 4;
rookery/viaduct/gy-flank/gaslamp 3. Fixlist `blender/fixlists/B3-r3.md`.
Builder-B3-r3t was stopped MID-ROUND at 19:38 with real progress: viaduct
rebuilt (blend+glb 19:23), gy-flank rebuilt (19:22), gaslamp rebuilt with
NEW `gaslamp_vent.png` louvre frame (19:37); rookery blend last touched
16:09 with 4 stale frames (boarded/detail/ctx/yard predate the blend —
provenance broken) and rookery.glb possibly stale vs blend. Manifest B3.md
still stale (10:31). Resume: fresh builder, B3-r3.md verbatim + this state,
finish rookery + re-render all touched assets provenance-clean + rewrite
manifest, deliver. Then fresh judge (r3).

**After both batches pass:** re-run gate (`python -m http.server 8123 -d
sandbox`; `node sandbox/verify/gate.mjs`), commit, tag `2a-complete`, then
stage 3 per Next task below.

## What this project is
A playable third-person 3D world: **1880s Victorian London, Whitechapel/Spitalfields**,
built with the RemakeBench production pipeline. The stage map and gates come from the
plugin skill `remakebench-skills:game-production-stages` — load it FIRST every session,
then the specialist skill the current stage names.

## Current state (as of 2026-08-30, commit 34b5fef)
- **Stage 0 COMPLETE, gate passed:** operator (the operator) approved the hero (day
  Spitalfields market); congruence pass run and logged; spec exists as text.
  - `refpack/README.md` — THE AUTHORITY: datum, LEVEL-ground ruling, L1–L7
    landmark count table with heights, street widths, the route in words, the
    congruence log (viaduct is STRAIGHT; arch span 18.00 not the plate's 14.00).
  - `refpack/tier1/` 7 spec plates; `refpack/tier2/` 4 cinematics (hero.jpg =
    approved). Tier 1 wins over Tier 2 on placement/count/height; README wins
    over plates; generation prompts are non-authoritative.
  - `research/victorian-london.md` — 870-line cited research report (era,
    district, dimensions, materials, characters, sources).
- **Budget:** fal.ai credit was $4.66; spent $0.47 (12 images, nano-banana);
  ≈ **$4.19 left**. Key: `FAL_API_KEY` in project `.env` (gitignored). No
  KIE_API_KEY exists (not needed — this project runs on fal). Track spend;
  stop at the ceiling.
- **Meshy: AUTHORIZED 2026-08-30.** the operator: 1408 credits, "feel free to use it
  up." Use for stage 2 character/props (image→3D, rig, animate) as needed.
  Free fallbacks stay valid: blender-headless procedural, Mixamo rigs.
- Cross-model judges verified working this machine: `codex-sub` / `grok-sub`
  wrappers (remakebench plugin). Grok sandbox is a no-op on Windows — give grok
  a scratch `-C` dir. Details in auto-memory `grok-cli-headless-fix`.

## Next task (updated 2026-08-31 19:40 PT — supersedes the stage-1 text below)
- **Resume from the ⏸ PAUSED block above** — finish the two open judge loops
  (B1 r5, B3 r3), then re-run the gate (`node sandbox/verify/gate.mjs`, server:
  `python -m http.server 8123 -d sandbox`) and commit+tag `2a-complete`.
- **Then stage 3 assembly judge + lookdev:** known items — brick texel scale
  reads oversized/monotone in-game (assets.js binds PBR by material name; tune
  repeat or swap set), roofline clutter on terraces seen from Brick Lane,
  soot-darkening/grade AFTER geometry passes. Then stage 4 (fog/ambience),
  stage 5 feel polish, stage 6 ship gate (clean perf re-take on quiet machine,
  HANDOVER.md, final tag). Session goal active: complete the playable game
  autonomously; verify by playing (Playwright CDP gate + independent judges).

## Original stage-1 next-task (DONE — kept for context)
- **Stage 1 — playable sandbox.** Engine decision recommended and accepted by
  default: **Three.js in the browser** (verify via claude-in-chrome; rAF perf).
  Build: capsule third-person player (WASD + mouse orbit), greybox the 350×300 m
  slice FROM THE README FIGURES ONLY (never scale off a plate): street grid
  (Commercial St 18 m, Brick Lane/Dorset St 11 m, George Yard 4 m), boxes for
  L1–L7 at their printed heights, viaduct straight on the north edge, level
  ground +0.00. Collision from the same data. Core loop: walk the README route
  end to end.
  - **Exit gate:** `remakebench-skills:verify-by-playing` — real input, the
    route traversed, camera owned. Not screenshots of geometry.
  - Then stage 2 parallel tracks (assets + character + perf datum) per the map.
- Checkpoint with a git tag at every playable milestone.

## Where to read things (reference, don't re-derive)
- `refpack/README.md` — spatial spec + congruence log. The single build authority.
- `research/victorian-london.md` — why every number is what it is; source links.
- Pipeline skills: `game-production-stages` (router), then per stage:
  `verify-by-playing`, `asset-judge-loop`, `3d-asset-quality`,
  `reference-pack-authority`, `codex-subagent`, `grok-subagent`.
- Sibling project `~/Downloads/remakebench/` — the guide HTML about the pipeline
  itself (`remakebench-skills-guide.html`) and its own HANDOFF.md.

## Session-transient scratch (regenerate; durable record is committed output)
- Image generation scripts lived in the session scratchpad (`hero_gen.js`,
  `pack_gen.js`): Node + fal.ai queue API pattern from the `genmedia` skill
  (`fal-ai/nano-banana`, $0.039/img, poll status → download → sidecar JSON to
  `generations/`). Rebuild from the genmedia skill if more plates are needed;
  the committed `generations/*.json` sidecars hold every prompt.

## How to work (essentials)
- Greybox before assets; capsule before character. Clay test with textures off.
- Judge loops: fresh judge every round, batch score = minimum asset score, exit
  is the judge passing or the operator stopping — never round count.
- Lighting/grade only AFTER geometry passes its judge round (stage 3).
- Commit + tag every playable milestone; keep this file current with every
  active judge loop's score trajectory.
- Spend: quote video before generating; images fine under the ceiling.
