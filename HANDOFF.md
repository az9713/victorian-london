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

## ▶ RESUMED 2026-08-31 (session model Opus 5, subagents sonnet)
Pipeline restarted after the pause. Fresh builders `builder-B1-r5b` and
`builder-B3-r3u` spawned on `model: sonnet`, each briefed with
BRIEF-COMMON.md + batch brief + its fixlist verbatim + the WIP resume state
below. Orchestration only on Opus 5.

### Live loop state (update every round)
- **B3 trajectory: r2 min 3 → r3 min 2 → r4 IN FLIGHT.** r3 judged FAIL min 2.
  Scores r3: gy-flank 2, rookery 3, viaduct-module 3, gaslamp 3, pillarbox 4.
  The r2→r3 drop is NOT a regression — nothing was un-built. The r3 fixlist
  asked only for an EVIDENCE pass on gy-flank and never asked whether the door
  recess contains a door. It does not: an empty void, no leaf/hinge/handle/
  threshold. Scope gap in the fixlist, not a builder failure. Banked from r3:
  viaduct black hole closed + ring reads as a proud order, rookery boarded
  window PASSES (4 planks, real gaps), gaslamp's 3 black-void bugs fixed,
  gy-flank barred window would score 4-5 alone. Fixlist `B3-r4.md` (countable
  properties). `builder-B3-r4` running, gy-flank first (it is the minimum).
- **B1 r5 delivered (96287fa), under judgment by `judge-B1-r5`.** Builder
  verified 5 of 6 countable properties already passing; 2c (cord band) FAILED
  and was fixed — root cause was a collar of 2 rings only 0.0065 m apart both
  at +0.017 m proud, packing the bump into a knife-thin span that renders as a
  blade; now 3 rings with a cosine falloff. Plus an unplanned real fix: the
  trestle peg formula used `COUNTER_H*0.42`, placing it 0.158 m off the true
  leg crossing (z=0.22), leaving the seam open as up to 9,985 true-black
  pixels in stall_34/stall_detail. Fixed + strap-plate bracket. Those two
  frames had been provenance-CLEAN since 19:37 while containing that defect —
  clean provenance never means correct content.
- **Quiet budget breach caught by the parent inventory, not by any judge:**
  sacks.glb was 8,500 tris against an 8,000 prop budget through r3 and r4.
  Judges see renders, not tri counts. Now 7,956; stall 7,868. LESSON: the
  parent must diff tri counts against budget every round.

**WIP state measured at resume (precise mtimes, 2026-08-31 PT):**
- B1 stall: blend 19:37:06 → renders 19:37:12–40 → glb 19:37:41. CLEAN.
- B1 sacks: blend 19:30:57 → renders 19:31:11+ → glb 19:31:39. CLEAN.
  So B1's r5 rebuild IS delivered; only manifest (stale 19:07) + the
  countable-property pixel verification were missing → verify-first brief.
- B3 viaduct: blend 19:23 → renders 19:23–24 → glb 19:23. CLEAN.
- B3 gy-flank: blend 19:22 → renders 19:22–23 → glb 19:22. CLEAN, but item 4
  is an EVIDENCE requirement — provenance-clean ≠ requirements-met.
- B3 gaslamp: blend 19:37:49 NEWER than _detail/_vent (19:33) → those two
  frames STALE, must reshoot. _face/_34 (19:37:57/19:38:03) clean.
- B3 rookery: rookery.py 19:18:02 NEWER than rookery.blend 16:09:26 — the
  script was edited and NEVER RUN. All rookery frames stale (11:02–11:04),
  glb 16:09 stale. This is the real remaining work in B3.
- B3 manifest B3.md stale (10:31).

### ⏸ Previous pause (2026-08-31 19:40 PT, historical)
the operator paused the pipeline to change the session model (Fable was at 7% with
a reset >2 days out). **Session model is now Opus 5** (set 19:45 PT via
/model opus, saved as the default for new sessions). Both running builders
were TaskStop'd at 19:38; their WIP is committed (117c7b3).

**Model rule on resume:** keep spawning builders and judges with
`model: sonnet` explicitly — Sonnet has done every 2a round competently and
this keeps the expensive session model for orchestration only. Do NOT let
subagents inherit Opus 5 by default. Exception, and only if the operator approves:
B1's last two features (stall tie, sack neck) have failed 4 rounds on
Sonnet, so a single stronger-model builder on those two small features is
the sanctioned escalation if r5 fails again.

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
