// Meshy pipeline: multi-image → 3D model → rig → animation clips.
// Usage: node meshy.mjs <name> <img1> [img2..img4] [--anims 0,14,103] [--height 1.0]
// Outputs to ../meshy/<name>/: model.glb, model.fbx, rigged.glb, rigged.fbx, anim_<id>.fbx/.glb
// Env: MESHY_API_KEY from nearest .env (walks up from cwd).
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "fs";
import { dirname, join, resolve } from "path";
import { fileURLToPath } from "url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");

// ponytail: 3-line .env parse, no dotenv
for (const p of [join(process.cwd(), ".env"), join(ROOT, ".env")]) {
  if (existsSync(p))
    for (const l of readFileSync(p, "utf8").split(/\r?\n/)) {
      const m = l.match(/^([A-Z_]+)=(.+)$/);
      if (m && !process.env[m[1]]) process.env[m[1]] = m[2].trim();
    }
}
const KEY = process.env.MESHY_API_KEY;
if (!KEY) { console.error("MESHY_API_KEY missing"); process.exit(1); }

const API = "https://api.meshy.ai/openapi/v1";
const H = { Authorization: `Bearer ${KEY}`, "Content-Type": "application/json" };

const args = process.argv.slice(2);
const flags = {};
const pos = [];
for (let i = 0; i < args.length; i++)
  args[i].startsWith("--") ? (flags[args[i].slice(2)] = args[++i]) : pos.push(args[i]);
const [name, ...images] = pos;
const anims = (flags.anims ?? "").split(",").filter(Boolean).map(Number);
const height = parseFloat(flags.height ?? "1.0");
if (!name || !images.length) { console.error("usage: meshy.mjs <name> <img..> [--anims ids] [--height m]"); process.exit(1); }

const OUT = join(ROOT, "meshy", name);
mkdirSync(OUT, { recursive: true });

const dataUri = (p) =>
  `data:image/${p.endsWith(".png") ? "png" : "jpeg"};base64,${readFileSync(p).toString("base64")}`;

async function post(path, body, base = API) {
  const r = await fetch(`${base}/${path}`, { method: "POST", headers: H, body: JSON.stringify(body) });
  const j = await r.json();
  if (!r.ok) throw new Error(`POST ${path} ${r.status}: ${JSON.stringify(j)}`);
  return j.result;
}

async function poll(path, id, label, base = API) {
  for (;;) {
    const r = await fetch(`${base}/${path}/${id}`, { headers: H });
    const j = await r.json();
    if (j.status === "SUCCEEDED") { console.log(`${label}: done (${j.consumed_credits ?? "?"} credits)`); return j; }
    if (["FAILED", "CANCELED"].includes(j.status))
      throw new Error(`${label} ${j.status}: ${JSON.stringify(j.task_error ?? j)}`);
    console.log(`${label}: ${j.status} ${j.progress ?? 0}%`);
    await new Promise((s) => setTimeout(s, 10000));
  }
}

async function dl(url, file) {
  if (!url) return;
  const r = await fetch(url);
  writeFileSync(join(OUT, file), Buffer.from(await r.arrayBuffer()));
  console.log(`saved ${file}`);
}

// 1. multi-image → 3D (or resume a paid task with --gen-id)
let genId = flags["gen-id"];
if (!genId) {
  genId = await post("multi-image-to-3d", {
    image_urls: images.map(dataUri),
    should_texture: true,
    topology: "triangle",
    target_polycount: 15000,
    target_formats: ["glb", "fbx"],
  });
  console.log("gen task", genId);
}
const gen = await poll("multi-image-to-3d", genId, "generate");
await dl(gen.model_urls?.glb, "model.glb");
await dl(gen.model_urls?.fbx, "model.fbx");
await dl(gen.thumbnail_url, "thumb.png");

// 1b. remesh — generation ignores target_polycount; rigging caps at 320k faces.
// Error message says v2; docs say v1. Try v2, fall back to v1.
let remeshId = flags["remesh-id"];
if (!remeshId) {
  // v1 works; the API's own 400 error names a v2 path that 404s
  remeshId = await post("remesh", { input_task_id: genId, target_polycount: 15000, topology: "triangle", target_formats: ["glb", "fbx"] });
  console.log("remesh task", remeshId);
}
const rm = await poll("remesh", remeshId, "remesh");
await dl(rm.model_urls?.glb, "remeshed.glb");

// 2. rig — input_task_id of a remesh task 422s ("Pose estimation failed"); model_url (data URI or
// hosted URL via fal_upload.mjs) works. 422s can be transient — retry a couple of times.
let rigId = flags["rig-id"];
if (!rigId) {
  const tries = [
    () => post("rigging", { input_task_id: remeshId, height_meters: height }),
    ...(flags["model-url"] ? [() => post("rigging", { model_url: flags["model-url"], height_meters: height })] : []),
    () => post("rigging", { model_url: `data:model/gltf-binary;base64,${readFileSync(join(OUT, "remeshed.glb")).toString("base64")}`, height_meters: height }),
    () => post("rigging", { model_url: `data:model/gltf-binary;base64,${readFileSync(join(OUT, "remeshed.glb")).toString("base64")}`, height_meters: height }),
  ];
  let lastErr;
  for (const t of tries) {
    try { rigId = await t(); break; } catch (e) { lastErr = e; console.log("rig attempt failed:", e.message); }
  }
  if (!rigId) throw lastErr;
}
console.log("rig task", rigId);
const rig = await poll("rigging", rigId, "rig");
const rr = rig.result ?? rig;
console.log("rig url keys:", JSON.stringify(Object.keys(rr)));
await dl(rr.rigged_character_glb_url, "rigged.glb");
await dl(rr.rigged_character_fbx_url, "rigged.fbx");
const basicAnims = rr.basic_animations ?? {};
for (const [k, v] of Object.entries(basicAnims)) if (typeof v === "string") await dl(v, `basic_${k}`.replace(/[^\w.]/g, "_") + (v.includes(".glb") ? ".glb" : ".fbx"));

// 3. animation clips
for (const id of anims) {
  const aId = await post("animations", { rig_task_id: rigId, action_id: id });
  const a = await poll("animations", aId, `anim ${id}`);
  const ar = a.result ?? a;
  await dl(ar.animation_fbx_url, `anim_${id}.fbx`);
  await dl(ar.animation_glb_url, `anim_${id}.glb`);
}
console.log("MESHY_OK", OUT);
