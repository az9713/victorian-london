// Shoot inspect.html for model/angle pairs: node verify/inspect.mjs terrace1-4 back top ...
import { chromium } from 'playwright';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(here, 'look'); fs.mkdirSync(OUT, { recursive: true });
const [model, ...angles] = process.argv.slice(2);
const browser = await chromium.launch({ headless: true });
const page = await (await browser.newContext({ viewport: { width: 1280, height: 720 } })).newPage();
for (const a of angles.length ? angles : ['front', 'back', 'top', 'three4']) {
  await page.goto(`http://localhost:8123/verify/inspect.html?m=${model}&a=${a}`);
  await page.waitForFunction('window.__shot', { timeout: 30000 });
  await page.screenshot({ path: path.join(OUT, `${model}-${a}.png`) });
  console.log(`${model}-${a}.png`);
  if (a === (angles.length ? angles[0] : 'front'))
    console.log(JSON.stringify(await page.evaluate('window.__info'), null, 1));
}
await browser.close();
