# Common build order — victorian-london stage 2a (read before your batch brief)

You are a BUILDER in an asset-judge loop. A fresh independent judge will score your
delivered renders. Your own "done" is not a verdict. The judge fails batches on the
MINIMUM asset score — the weakest asset IS the batch score. Same bar for every asset:
NO hero/background tiering.

## The quality rule (from the 3d-asset-quality skill — binding)
Model what the object IS, not its outline. Every asset shows the parts that exist
because it functions: joined / supported / moves-opens / gripped / fixed / weathered /
maintained. Bevel every edge that catches light (2-5 mm wood, more on stone). Every
surface has thickness — no zero-thickness planes. The acceptance test renders CLAY
(textures off) at eye height (1.6 m), close: a stranger must answer "what is it /
how is it built / how is it used" from geometry alone. A box with a texture = FAIL
= rebuild, not adjust.

Openings: lintel + jambs + sill + reveal — doors/windows sit BACK in the wall
thickness, never coplanar. Roofs: overhanging eaves + visible rafter tails or
brackets + fascia + ridge cap + chimney stacks with pots (this is 1880s London —
the chimney line is the skyline). Walls meet ground at a plinth. Victorian brick is
soot-darkened London stock.

## Machine + tools
- Blender: "C:\Users\USERNAME\tools\blender-4.4.2-windows-x64\blender.exe" -b -P script.py
  (portable 4.4.2 — verified headless 2026-08-31; the Program Files path is dead
  and the Store alias is untrustworthy headless. Do not use either.)
  Always -t 4. Prefer bpy.data over bpy.ops (many ops fail headless).
- You own your batch folder blender/<batch>/ (scripts, .blend) — touch nothing else
  except your exports and renders. One .blend per batch, or per asset.
- Renders: Cycles CPU ONLY (device CPU, 32 samples + denoise, 960x540 is enough).
  NEVER Cycles GPU — the 4 GB card is shared. EEVEE also acceptable for clay if
  Cycles is slow, but keep a clear sun key + soft fill so bevels catch.

## Dimensions are law
Your brief quotes figures from refpack/README.md via sandbox/layout.js. Build to
those figures EXACTLY — the GLB drops onto the greybox footprint. Never scale off
a reference image; images are for look and function, printed figures for size.

## Materials / UVs (no textures embedded!)
UV-unwrap everything (smart-project acceptable for statics). Assign SHARED MATERIAL
NAMES only — the game binds PBR maps by name at load:
  brick  slate  cobble  planks  plaster  iron  glass  paint_dark  paint_green  stone
Use those exact names. No image textures inside the GLB (keeps files small).
Density target: 1 UV tile ≈ the pbr set scale in sandbox/assets/pbr/manifest.json
(brick 2 m, slate 3 m, planks 2 m, plaster 2 m, cobble 4 m).

## Export (per asset)
- GLB to sandbox/assets/models/<asset>.glb, +Y up (Blender glTF default), metres.
- Origin: your brief names the anchor (usually footprint centre, y=0 at ground).
- Poly budget: sensible low-poly game asset. Buildings < 60k tris, props < 8k.
  Bevels can be real geometry at these budgets.

## Acceptance renders (per asset, CLAY — no textures)
Use a neutral grey override material (view-layer override or replace materials in a
copy). Camera 1.6 m height, standing distance. Minimum 3 frames per asset:
face-on, three-quarter, and a DETAIL CROP on a join/opening/moving part. Assets
over 4 m: add one pulled-back context frame (judged on the eye-level ones).
Output: blender/renders/<batch>/<asset>_face.png, _34.png, _detail.png, _ctx.png.

## Manifest (deliverable)
Write blender/manifests/<batch>.md: per asset — what it is (one stranger line),
functional parts modelled (the seven prompts), render paths, YOUR three stranger
answers from the frames alone, verdict PASS/FAIL. Failed assets stay listed with a
rebuild note. Files on disk are not evidence; the renders + manifest are.

## Reference images (attached, look only — figures win over pixels)
- refpack/tier1/materials.jpg (9 material swatches)
- refpack/tier2/hero.jpg (approved day-market mood)
- plus per-batch plates named in your brief. All under
  C:/Users/USERNAME/Downloads/projects/victorian-london/refpack/
