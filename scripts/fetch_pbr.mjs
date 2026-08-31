// Fetch CC0 PBR sets from Polyhaven at 2K (browser-friendly) into sandbox/assets/pbr/<slug>/.
// Maps: diffuse, normal (GL), roughness, AO. Height skipped (not used in the Three.js build).
// Usage: node scripts/fetch_pbr.mjs
import { mkdirSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(ROOT, 'sandbox', 'assets', 'pbr');

// slug -> declared real-world scale (metres covered by one tile), recorded in manifest.json
const SETS = {
  cobblestone_03:     { scale: 4, use: 'streets and plaza ground' },
  brown_brick_02:     { scale: 2, use: 'sooty London stock brick walls' },
  roof_slates_02:     { scale: 3, use: 'slate roofs' },
  dark_wooden_planks: { scale: 2, use: 'stall boards, doors, viaduct hoardings' },
  beige_wall_001:     { scale: 2, use: 'gin palace / church plaster + stone' },
};
const MAPS = { Diffuse: 'diff', nor_gl: 'normal', Rough: 'rough', AO: 'ao' };

const manifest = {};
for (const [slug, meta] of Object.entries(SETS)) {
  const dir = join(OUT, slug);
  mkdirSync(dir, { recursive: true });
  const files = await (await fetch(`https://api.polyhaven.com/files/${slug}`)).json();
  manifest[slug] = { ...meta, maps: {}, source: `https://polyhaven.com/a/${slug}`, license: 'CC0' };
  for (const [key, short] of Object.entries(MAPS)) {
    const entry = files[key]?.['2k'];
    if (!entry) { console.log(`${slug}: no ${key}`); continue; }
    const pick = entry.jpg ?? entry.png;
    const ext = entry.jpg ? 'jpg' : 'png';
    const dest = join(dir, `${short}.${ext}`);
    if (!existsSync(dest)) {
      writeFileSync(dest, Buffer.from(await (await fetch(pick.url)).arrayBuffer()));
      console.log(`${slug}/${short}.${ext}  ${(pick.size / 1e6).toFixed(1)} MB`);
    }
    manifest[slug].maps[short] = `${slug}/${short}.${ext}`;
  }
}
writeFileSync(join(OUT, 'manifest.json'), JSON.stringify(manifest, null, 2));
console.log('PBR_OK', Object.keys(manifest).join(', '));
