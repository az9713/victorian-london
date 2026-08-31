// T-pose turnaround for the costermonger player character (Meshy input).
// fal-ai/nano-banana/edit with the committed character sheet as reference.
// Usage: node scripts/turnaround.mjs   → generations/turnaround-costermonger_*.jpg + sidecar
import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
for (const l of readFileSync(join(ROOT, '.env'), 'utf8').split(/\r?\n/)) {
  const m = l.match(/^([A-Z_]+)=(.+)$/); if (m && !process.env[m[1]]) process.env[m[1]] = m[2].trim();
}
const KEY = process.env.FAL_API_KEY;
if (!KEY) { console.error('FAL_API_KEY missing'); process.exit(1); }

const SHEET = join(ROOT, 'generations', 't1-characters_nano-banana_1788152732763.jpg');
const refUri = `data:image/jpeg;base64,${readFileSync(SHEET).toString('base64')}`;

const FIGS = {
  costermonger: 'ONLY the first figure from the reference (the costermonger: corduroy jacket ' +
    'and trousers, striped waistcoat, bright red neckerchief, small flat cap, worn leather ' +
    'boots, 1880s London street vendor)',
  flowergirl: 'ONLY the second figure from the reference (the flower girl: patterned shawl ' +
    'over a blouse, long apron over a striped skirt, small straw bonnet worn close to the ' +
    'head, flat shoes, 1880s London street seller). NO basket, NO flowers',
  constable: 'ONLY the third figure from the reference (the Victorian police constable: dark ' +
    'blue high-collar tunic with two button rows, white belt with buckle, dark trousers, ' +
    'black boots). IMPORTANT: replace the tall helmet with a small flat pillbox cap so the ' +
    'head is compact',
};
const who = process.argv[2] || 'costermonger';
if (!FIGS[who]) { console.error('unknown figure', who); process.exit(1); }
const prompt =
  `Character turnaround sheet of ${FIGS[who]}. One 16:9 image, exactly three full-body ` +
  'views side by side: FRONT view, SIDE view facing left, BACK view. STRICT T-POSE in all ' +
  'three views: both arms straight out horizontally at shoulder height, clearly separated ' +
  'from the body and any headwear, legs straight and slightly apart. No props, no text, ' +
  'no labels. Plain light-gray background, even flat lighting, consistent scale.';

const submit = await fetch('https://queue.fal.run/fal-ai/nano-banana/edit', {
  method: 'POST', headers: { Authorization: `Key ${KEY}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt, image_urls: [refUri], aspect_ratio: '16:9' }),
});
const sub = await submit.json();
if (!submit.ok) { console.error('submit failed', submit.status, JSON.stringify(sub)); process.exit(1); }
console.log('request', sub.request_id);

// poll on the BASE model path (subpath models poll on the base — meshy skill note)
let result;
for (;;) {
  await new Promise(r => setTimeout(r, 4000));
  const st = await (await fetch(`https://queue.fal.run/fal-ai/nano-banana/requests/${sub.request_id}/status`, {
    headers: { Authorization: `Key ${KEY}` } })).json();
  console.log('status', st.status);
  if (st.status === 'COMPLETED') {
    result = await (await fetch(`https://queue.fal.run/fal-ai/nano-banana/requests/${sub.request_id}`, {
      headers: { Authorization: `Key ${KEY}` } })).json();
    break;
  }
  if (st.status === 'FAILED' || st.status === 'ERROR') { console.error('failed', JSON.stringify(st)); process.exit(1); }
}

const url = result.images?.[0]?.url;
if (!url) { console.error('no image url', JSON.stringify(result).slice(0, 500)); process.exit(1); }
const stamp = Date.now();
const base = `turnaround-${who}_nano-banana_${stamp}`;
writeFileSync(join(ROOT, 'generations', `${base}.jpg`), Buffer.from(await (await fetch(url)).arrayBuffer()));
writeFileSync(join(ROOT, 'generations', `${base}.json`), JSON.stringify({
  prompt, model: 'fal-ai/nano-banana/edit', provider: 'fal',
  refs: ['t1-characters_nano-banana_1788152732763.jpg'], params: { aspect_ratio: '16:9' },
  cost_usd: 0.039, created: new Date().toISOString(),
}, null, 2));
console.log('saved generations/' + base + '.jpg');
