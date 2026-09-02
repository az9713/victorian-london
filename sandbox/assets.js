// Stage 2a/3 assembly: swap greybox visuals for delivered GLBs at the layout
// records. Colliders are NOT touched — greybox AABBs stay the collision truth.
// Missing GLBs are skipped silently (progressive upgrade as builders deliver).
// Shared PBR materials are bound BY NAME from sandbox/assets/pbr/manifest.json;
// builder GLBs carry material names only, no textures.

const MODEL_BASE = 'assets/models/';

// material name -> pbr set (null = flat color material stays as exported)
const MAT_PBR = {
  brick: 'brown_brick_02', slate: 'roof_slates_02', cobble: 'cobblestone_03',
  planks: 'dark_wooden_planks', plaster: 'beige_wall_001', stone: 'beige_wall_001',
};

// Texel density. The builders UV with smart_project, which packs EVERY object's
// islands into the 0-1 square — so one texture tile stretches across a whole
// 20 m facade and brick reads metres-per-brick. UV area 1 therefore maps to the
// object's entire surface area A, so repeat = sqrt(A) / metres-per-tile restores
// real-world texel size. Density is uniform across an object (one pack for all
// its islands), so ONE repeat per object is correct for all its materials.
const triAreaOf = geom => {          // local-space surface area, cached on the geometry
  if (geom.__area != null) return geom.__area;
  const p = geom.attributes.position, idx = geom.index;
  const n = idx ? idx.count : p.count, gi = i => (idx ? idx.getX(i) : i);
  let a = 0;
  for (let i = 0; i + 2 < n; i += 3) {
    const i0 = gi(i), i1 = gi(i + 1), i2 = gi(i + 2);
    const ax = p.getX(i1) - p.getX(i0), ay = p.getY(i1) - p.getY(i0), az = p.getZ(i1) - p.getZ(i0);
    const bx = p.getX(i2) - p.getX(i0), by = p.getY(i2) - p.getY(i0), bz = p.getZ(i2) - p.getZ(i0);
    a += 0.5 * Math.hypot(ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx);
  }
  return (geom.__area = a);
};
const MAT_FLAT = {   // color/rough/metal for non-textured names
  iron:        { color: 0x2a2c2e, roughness: 0.55, metalness: 0.85 },
  // sooty glazing: dark enough to hide hollow module interiors, light enough that
  // the market's glazed roof still reads luminous (assembly judge note)
  glass:       { color: 0x5a6672, roughness: 0.10, metalness: 0.0, transparent: true, opacity: 0.55 },
  paint_dark:  { color: 0x25321f, roughness: 0.6 },
  paint_green: { color: 0x2e4a34, roughness: 0.55 },
  postbox_red: { color: 0x8a1c1c, roughness: 0.5 },
  cloth:       { color: 0x8d8069, roughness: 0.95 },
};

export async function upgradeWorld({ THREE, GLTFLoader, scene, L, kindMeshes }) {
  const loader = new GLTFLoader();
  const tl = new THREE.TextureLoader();
  const report = { placed: [], missing: [] };

  // ---- shared materials ----
  const pbrManifest = await (await fetch('assets/pbr/manifest.json')).json();
  const shared = {};
  const loadTex = (p, srgb) => { const t = tl.load('assets/pbr/' + p);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t; };
  // tints multiply the map: stone lifts toward weathered Portland (Christ Church
  // is Portland ashlar, not tan plaster); brick pulls toward sooty London stock
  // hero.jpg palette: London stock brick is desaturated YELLOW-brown, not red
  const MAT_TINT = { stone: 0xd6d2c8, brick: 0xb09c80 };
  for (const [name, slug] of Object.entries(MAT_PBR)) {
    const set = pbrManifest[slug]; if (!set) continue;
    shared[name] = new THREE.MeshStandardMaterial({
      name, map: set.maps.diff && loadTex(set.maps.diff, true),
      color: MAT_TINT[name] ?? 0xffffff,
      normalMap: set.maps.normal && loadTex(set.maps.normal),
      roughnessMap: set.maps.rough && loadTex(set.maps.rough),
      aoMap: set.maps.ao && loadTex(set.maps.ao),
      side: THREE.DoubleSide,   // builder walls are single-sided; the player walks both sides
    });
  }
  for (const [name, def] of Object.entries(MAT_FLAT))
    shared[name] = new THREE.MeshStandardMaterial({ name, side: THREE.DoubleSide, ...def });

  // metres covered by one texture tile, per bound material name
  const MAT_TILE = {};
  for (const [name, slug] of Object.entries(MAT_PBR))
    MAT_TILE[name] = pbrManifest[slug]?.scale ?? 2;
  // brown_brick_02 at its declared 2 m holds ~9 courses -> 22 cm bricks, ~2.5x
  // life size. 1.2 m/tile puts courses at ~13 cm without obvious tiling repeats.
  MAT_TILE.brick = 1.2;

  // repeat-corrected variants, cached so instanced terraces share materials
  const tiled = {};
  const atRepeat = (name, r) => {
    const base = shared[name];
    if (!base?.map || !MAT_TILE[name]) return base;      // flat colours need no repeat
    const key = `${name}|${r.toFixed(2)}`;
    if (tiled[key]) return tiled[key];
    const m = base.clone();
    for (const k of ['map', 'normalMap', 'roughnessMap', 'aoMap']) {
      if (!m[k]) continue;
      m[k] = m[k].clone(); m[k].repeat.set(r, r); m[k].needsUpdate = true;
    }
    return (tiled[key] = m);
  };

  const bindMaterials = (root, scaleY = 1) => root.traverse(o => {
    if (!o.isMesh) return;
    // ponytail: non-uniform scale.y folded in as a linear area factor, not exact
    // per-triangle. Terraces stretch 11.25->14 m at most, so the error is <5%.
    const area = triAreaOf(o.geometry) * scaleY;
    const repeatFor = name => Math.max(1, Math.sqrt(area) / (MAT_TILE[name] ?? 2));
    const swap = m => {
      const name = m.name?.toLowerCase().replace(/\.\d+$/, '');
      return shared[name] ? atRepeat(name, repeatFor(name)) : m;
    };
    o.material = Array.isArray(o.material) ? o.material.map(swap) : swap(o.material);
    if (o.geometry.attributes.uv && !o.geometry.attributes.uv2)
      o.geometry.setAttribute('uv2', o.geometry.attributes.uv);   // aoMap needs uv2
    o.castShadow = o.receiveShadow = true;
  });

  const tryLoad = url => new Promise(res =>
    loader.load(MODEL_BASE + url, g => res(g), undefined, () => res(null)));

  const removeKinds = (...kinds) => {
    for (const k of kinds) for (const m of (kindMeshes[k] ?? [])) scene.remove(m);
  };
  const place = (glb, x, z, rotY = 0, scaleY = 1) => {
    const inst = glb.scene.clone(true);
    inst.position.set(x, 0, z); inst.rotation.y = rotY;
    if (scaleY !== 1) inst.scale.y = scaleY;
    bindMaterials(inst, scaleY); scene.add(inst); return inst;
  };

  // ---- landmark placements (origins per the builder briefs) ----
  const jobs = [
    ['market.glb',  g => { removeKinds('market-wall', 'market-column', 'market-roof'); place(g, 234.5, 150); }],
    ['church.glb',  g => { removeKinds('church-nave', 'church-tower', 'church-spire'); place(g, 24, 207.5); }],
    ['ginpalace.glb', g => { removeKinds('ginpalace', 'ginpalace-front'); place(g, 76.5, 188); }],
    ['rookery.glb', g => { removeKinds('rookery', 'rookery-wall'); place(g, 171.5, 166.25); }],
    ['viaduct-module.glb', g => { removeKinds('viaduct-pier', 'viaduct-deck');
      for (let cx = 2; cx <= 348; cx += 22) place(g, cx, 10); }],
    ['gy-flank.glb', g => { removeKinds('gy-flank');
      place(g, 144, 85.25, 0); place(g, 156, 85.25, Math.PI); }],
    ['gaslamp.glb', g => { removeKinds('lamp');
      for (const l of L.lamps) place(g, l.x, l.z); }],
    ['pillarbox.glb', g => { removeKinds('pillarbox');
      place(g, L.pillarbox.x, L.pillarbox.z); }],
  ];
  for (const [file, fn] of jobs) {
    const g = await tryLoad(file);
    if (g) { fn(g); report.placed.push(file); } else report.missing.push(file);
  }

  // ---- terraces: 6 module variants, rotated to face their street ----
  const FACE_ROT = { '-z': 0, '+z': Math.PI, '+x': -Math.PI / 2, '-x': Math.PI / 2 };
  const terraceGlbs = {};
  for (const v of [0, 1, 2]) for (const s of [3, 4]) {
    const g = await tryLoad(`terrace${v}-${s}.glb`);
    if (g) terraceGlbs[`${v}-${s}`] = g; else report.missing.push(`terrace${v}-${s}.glb`);
  }
  if (Object.keys(terraceGlbs).length === 6) {
    removeKinds('terrace0', 'terrace1', 'terrace2');
    for (const b of L.boxes) {
      const m = b.kind.match(/^terrace(\d)$/); if (!m) continue;
      const h = b.y1, s = h < 12.5 ? 3 : 4, base = s === 3 ? 11.25 : 13.25;
      const g = terraceGlbs[`${m[1]}-${s}`];
      place(g, (b.x1 + b.x2) / 2, (b.z1 + b.z2) / 2, FACE_ROT[b.face] ?? 0, h / base);
    }
    report.placed.push('terraces x6');
  }

  // ---- ground: cobbles everywhere (PBR, declared scale) ----
  if (shared.cobble && kindMeshes.ground?.[0]) {
    const gmesh = kindMeshes.ground[0];
    const matG = shared.cobble.clone();
    const rx = L.bounds.x / (pbrManifest.cobblestone_03?.scale ?? 4);
    const rz = L.bounds.z / (pbrManifest.cobblestone_03?.scale ?? 4);
    for (const k of ['map', 'normalMap', 'roughnessMap', 'aoMap']) {
      if (!matG[k]) continue;
      matG[k] = matG[k].clone(); matG[k].repeat.set(rx, rz); matG[k].needsUpdate = true;
    }
    gmesh.geometry.setAttribute('uv2', gmesh.geometry.attributes.uv);
    gmesh.material = matG;
    report.placed.push('ground-cobbles');
  }

  console.log('upgradeWorld:', JSON.stringify(report));
  return report;
}
