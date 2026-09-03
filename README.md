# victorian-london

A playable third-person 3D slice of 1880s Whitechapel and Spitalfields. It runs
in a browser. It has no build step and no framework — three.js from a CDN, one
HTML file, two JavaScript modules.

Walk a 10-checkpoint route through fog and gaslight. Finish it and **The
Costermonger's Round** unlocks: collect a basket at the market, make three
deliveries, return. The round is timed and keeps your best.

Built with the **[RemakeBench skills pipeline](https://github.com/RemakeBench/skills)**
— see [Credit](#credit) below.

## Play it

```bash
cd <this folder>
python -m http.server 8123 -d sandbox
```

Open `http://localhost:8123` in Chrome.

| Input | Action |
|---|---|
| `WASD` | Move |
| `Shift` | Sprint |
| Mouse drag, or arrow keys | Camera |
| Click | Mouse-look |
| `E` | Interact at a beacon |

Press any key once to start the audio. Browsers block sound until the first
input.

> Serve from the project root with `-d sandbox`, as shown. Running the command
> from inside `sandbox/` returns 404 — the flag is relative to the working
> directory.

## What is in it

**The world.** A 350 × 300 m slice. A railway viaduct closes the north edge. A
glazed market hall sits at the centre. Christ Church carries a +50 m spire. There
is a gin palace, a rookery court, the twin flank walls of George Yard, about 50
terrace modules, a pillar box and 11 gas lamps. Every figure comes from
`refpack/README.md`. Nothing was scaled off a picture.

**The assets.** 18 judged GLB models. Shared 2K PBR textures from Polyhaven,
bound by material name at world-scale texel density. The player is a rigged
Meshy costermonger, 24 bones, with measured joint motion. Twelve NPCs walk beat
paths with idle pauses and soft-body collision that pushes the player, not them.

**The atmosphere.** A coal-smog night. Fog from 8 to 40 m. Soot-darkened brick.
Wet cobbles that catch the lamps. Each gas lamp has a warm point light, a glow
halo, a wide corona for distance, and a flame flicker. Fog patches drift along
the streets. The gin palace windows are the one bright spot on Commercial Street.
Ghost signs — BOVRIL, PEAR'S SOAP, TRUMAN'S ALES — sit high on blank walls.

**The sound.** All procedural WebAudio. No audio files. A city rumble and wind
bed, cobble footsteps, a crowd murmur, a cab that passes with hooves and axle
rattle, a church bell each minute, and a train that rumbles over the viaduct
every few minutes — louder when you stand near it.

## Repository map

| Path | What it holds |
|---|---|
| `sandbox/` | **The entire game.** `index.html`, `layout.js`, `assets.js` — about 700 lines. |
| `sandbox/verify/` | The test instruments. `gate.mjs` is the acceptance gate. |
| `refpack/` | The spatial authority: datum, landmark counts, heights. Text outranks every plate. |
| `research/` | `victorian-london.md` — the period research. Sections 7 and 10 are the atmosphere spec. |
| `blender/` | Builder scripts and the fixlists that drove the asset judge rounds. |
| `meshy/`, `generations/` | Character generation and reference-image generation. |
| `HANDOVER.md` | The ship document: what shipped, verification detail, gotchas. |
| `HANDOFF.md` | The live resume point. **Read this first in a new session.** |
| `HANDOFF-HISTORY.md` | Every stage and judge-loop trajectory, in full. |

## How it was built

The [RemakeBench skills](https://github.com/RemakeBench/skills) pipeline runs a
game through seven production gates. The rules that shaped this build:

1. **Greybox before assets.** The layout records in `layout.js` are the single
   source of truth. They drive the greybox meshes, the colliders, and the later
   GLB placements. Collision never moved when the art landed.
2. **A playable sandbox before production art.** The route was walkable while
   every building was still a grey box.
3. **Builders never sign off their own work.** Each asset batch went to a fresh
   judge that saw only renders, a manifest and the references. A batch scores
   the *minimum* of its assets, so effort cannot be diluted across a set.
4. **Prove it by playing.** A green test suite is not evidence. The gate drives
   real held keys through Chrome DevTools Protocol and walks the route.

Stage tags mark each milestone: `stage1-sandbox-playable` through `ship-v1`, then
`ambient-v1`.

## Verification

`sandbox/verify/gate.mjs` is the acceptance instrument. It launches Chrome
through Playwright and plays the game with real key events.

```bash
node sandbox/verify/gate.mjs          # 16/16 expected
node sandbox/verify/gate.mjs --fault=seal    # must FAIL
```

It checks input liveness with an unbound key, measures walk and sprint distance,
measures foot-bone travel to prove the rig animates, walks all 10 checkpoints,
drives the mission with real `E` presses, replays it, and samples camera
ownership every frame. Three fault injections (`deadkeys`, `seal`, `cam`) each
make it fail correctly — that is what proves the gate can detect a defect.

Other instruments: `look.mjs` shoots a waypointed lookdev tour, `feel.mjs` probes
NPC collision and the sprint FOV kick, `inspect.mjs` renders a single GLB as
clay, `datum.mjs` measures frame rate.

> **Measure on a quiet machine.** Close any other tab showing the game first. A
> backgrounded Chrome window throttles the animation frame callback, and the gate
> then reads 1 fps and mis-steers the route. Frame rate also swings from 68 to 49
> under load with no code change.

## Performance

About 68 fps median at 1280 × 720, on Intel UHD integrated graphics through
ANGLE D3D11. The 12-NPC crowd costs roughly 2 fps. The drifting fog sprites and
the gin palace lights measured at zero cost.

## Credit

The production method comes from **[RemakeBench/skills](https://github.com/RemakeBench/skills)**,
a plugin of seven skills for building playable 3D worlds: `game-production-stages`,
`reference-pack-authority`, `3d-asset-quality`, `asset-judge-loop`,
`verify-by-playing`, `codex-subagent` and `grok-subagent`. The skills came out of
[this RemakeBench video](https://www.youtube.com/watch?v=MsFYd8EdAXw) and its
measured findings about where agent-built 3D worlds fail.

This repository is the first full run of that pipeline.

Period detail comes from `research/victorian-london.md`, which cites its sources.

## A lesson worth repeating

The build shipped once, at `ship-v1`, and looked wrong. The reference pack had
kept only the *numbers* from the research — widths, heights, counts. The
atmosphere sections never became spec lines, and the approved hero image was a
daylight market. So the world graded to a bright afternoon when the research
described a night pea-souper with gaslight pools and soot-black brick.

Fixing it took a night grade and an ambient pass, shipped as `ambient-v1`.

**For the next world: write an Atmosphere block into the reference pack before
stage 1.** A reference pack that carries only measurements will produce a
correctly proportioned world that feels like nowhere.
