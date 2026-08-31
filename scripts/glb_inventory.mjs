// Parent-made scene inventory for judge rounds: parse each GLB's JSON chunk and
// list node/mesh/material names + counts. Never supplied by a builder.
// Usage: node scripts/glb_inventory.mjs [glob-dir]   (default sandbox/assets/models)
import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const DIR = process.argv[2] ?? join(ROOT, 'sandbox', 'assets', 'models');

for (const f of readdirSync(DIR).filter(f => f.endsWith('.glb')).sort()) {
  const buf = readFileSync(join(DIR, f));
  if (buf.readUInt32LE(0) !== 0x46546C67) { console.log(`${f}: not a GLB`); continue; }
  const jsonLen = buf.readUInt32LE(12);
  const j = JSON.parse(buf.subarray(20, 20 + jsonLen).toString('utf8'));
  const tris = (j.meshes ?? []).flatMap(m => m.primitives).reduce((a, p) =>
    a + (p.indices !== undefined ? (j.accessors[p.indices].count / 3) : 0), 0);
  console.log(`${f}: ${j.nodes?.length ?? 0} nodes, ${j.meshes?.length ?? 0} meshes, ` +
    `${Math.round(tris)} tris, materials: [${(j.materials ?? []).map(m => m.name).join(', ')}]`);
  const named = (j.nodes ?? []).map(n => n.name).filter(Boolean);
  if (named.length) console.log(`  nodes: ${named.slice(0, 40).join(', ')}${named.length > 40 ? ` … +${named.length - 40}` : ''}`);
}
