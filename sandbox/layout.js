// Single source of truth for the victorian-london slice layout.
// Figures come from refpack/README.md — never scale off a plate.
// Consumed by: sandbox/index.html (greybox meshes + colliders) and the stage-2
// asset assembly scripts (GLB placements). Greybox AABBs stay the collision
// truth through stage 3; assets are visual replacements at the same records.
// Coordinates: x west->east [0,350], z north->south [0,300], y up, +0.00 ground.

export function buildLayout() {
  const boxes = [];   // {kind,x1,z1,x2,z2,y0,y1,collide}
  const box = (kind, x1, z1, x2, z2, y0, y1, collide = true) =>
    boxes.push({ kind, x1, z1, x2, z2, y0, y1, collide });

  // L4 viaduct — STRAIGHT, west-east, north edge; arch 9.00 x 18.00, deck +15.00
  for (let cx = 2; cx <= 348; cx += 22) box('viaduct-pier', cx - 2, 4, cx + 2, 16, 0, 9);
  box('viaduct-deck', 0, 3, 350, 17, 9, 15, false);

  // L1 market building: plaza x[184.5,284.5] z[120,180]; 84x44, eaves +9, ridge +14
  const MB = { x1: 192.5, x2: 276.5, z1: 128, z2: 172 };
  box('market-wall', MB.x1, MB.z1, MB.x2, MB.z1 + 1, 0, 9);
  box('market-wall', MB.x1, MB.z2 - 1, MB.x2, MB.z2, 0, 9);
  for (const [wx1, wx2] of [[MB.x1, MB.x1 + 1], [MB.x2 - 1, MB.x2]]) {
    box('market-wall', wx1, MB.z1, wx2, 144, 0, 9);
    box('market-wall', wx1, 156, wx2, MB.z2, 0, 9);
  }
  for (let cx = MB.x1 + 10; cx < MB.x2 - 4; cx += 12)
    for (const cz of [140, 160]) box('market-column', cx - .4, cz - .4, cx + .4, cz + .4, 0, 9);

  // L2 Christ Church — faces Commercial St from the WEST, front x=39 (12 m setback)
  box('church-nave', 9, 192, 31, 223, 0, 18);
  box('church-tower', 31, 203.5, 39, 211.5, 0, 35);

  // L3 gin palace — Commercial St EAST side, parapet +11
  box('ginpalace', 69, 178, 84, 198, 0, 11);
  box('ginpalace-front', 69.05, 180, 69.3, 196, 0, 3.5, false);

  // L5 rookery — Dorset St south side, EAST of George Yard; +14.50, court 3.70
  box('rookery', 152, 155.5, 190, 164.5, 0, 14.5);
  box('rookery', 152, 168.2, 190, 177, 0, 14.5);
  box('rookery-wall', 190, 155.5, 191, 177, 0, 14.5);

  // L6 George Yard — 4.00 slot x[148,152], flank walls +12
  box('gy-flank', 140, 26, 148, 144.5, 0, 12);
  box('gy-flank', 152, 26, 160, 144.5, 0, 12);

  // fill terraces: frontage 5.00, parapets 10.50-14.00 (seeded, stable)
  let seed = 42;
  const rnd = () => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
  function terraces(axis, f1, f2, from, to, gaps, face) {   // face: which way fronts point
    for (let a = from; a + 5 <= to; a += 5) {
      if (gaps.some(g => a < g[1] && a + 5 > g[0])) { rnd(); rnd(); continue; }
      const h = 10.5 + rnd() * 3.5; const v = (rnd() * 3) | 0;   // v: facade variant 0..2
      if (axis === 'z') box('terrace' + v, f1, a, f2, a + 5, 0, h);
      else box('terrace' + v, a, f1, a + 5, f2, 0, h);
      boxes[boxes.length - 1].face = face;
    }
  }
  terraces('z', 37, 51, 26, 300, [[185, 230]], '+x');            // faces Commercial St
  terraces('z', 69, 83, 26, 300, [[144.5, 155.5], [178, 198], [120, 180]], '-x');
  terraces('z', 270.5, 284.5, 26, 300, [[120, 180]], '+x');      // faces Brick Lane
  terraces('z', 295.5, 309.5, 26, 300, [], '-x');
  terraces('x', 26, 40, 0, 350, [[51, 69], [140, 160], [284.5, 295.5]], '-z'); // viaduct street
  terraces('x', 130.5, 144.5, 69, 140, [], '+z');                // faces Dorset St
  terraces('x', 130.5, 144.5, 160, 184.5, [], '+z');
  terraces('x', 155.5, 169.5, 84, 152, [], '-z');
  terraces('x', 106, 120, 184.5, 284.5, [], '+z');               // faces plaza
  terraces('x', 180, 194, 184.5, 284.5, [[190, 200]], '-z');

  // invisible slice bounds
  for (const b of [[-2, -2, 352, 0], [-2, 300, 352, 302], [-2, -2, 0, 302], [350, -2, 352, 302]])
    box('bounds', b[0], b[1], b[2], b[3], 0, 3);

  return {
    boxes,
    market: MB,                                  // roof + interior details derive from this
    spire: { x: 35, z: 207.5, baseY: 35, topY: 50, halfBase: 5.2 },   // pyramid, apex +50
    lamps: [
      ...[30, 95, 160, 225, 290].flatMap(z => [{ x: 52.5, z }, { x: 294.5, z }]),
      { x: 151, z: 85 },                         // George Yard's single lamp
    ],
    pillarbox: { x: 52.8, z: 172, h: 1.4, r: 0.25 },
    route: [
      ['Head south down Brick Lane', 290, 40],
      ['Market plaza, east edge', 280, 150],
      ['Inside the market building', 234, 150],
      ['Dorset Street, plaza west exit', 180, 150],
      ['Past the rookery (L5)', 160, 150],
      ['George Yard mouth (L6)', 150, 150],
      ['Commercial Street junction', 65, 150],
      ['The gin palace (L3)', 66, 188],
      ['Christ Church forecourt (L2)', 45, 207],
      ['Slice exit, Commercial St south end', 60, 296],
    ],
    spawn: { x: 290, z: 20, yaw: Math.PI },
    bounds: { x: 350, z: 300 },
  };
}
