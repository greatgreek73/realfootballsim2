#!/usr/bin/env node
import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";

const PROJECT_ROOT = process.env.PROJECT_ROOT || process.cwd();
const SRC_PAGES = path.join(PROJECT_ROOT, "src", "pages");
const TEMPLATE_ROOT = process.env.TEMPLATE_ZIP_EXTRACT;
const CONFLICT_MODE = process.env.CONFLICT_MODE || "skip"; // skip | demo
const APPLY = process.argv.includes("--apply");

if (!TEMPLATE_ROOT) {
  console.error("Set TEMPLATE_ZIP_EXTRACT env to template root (having src/pages).");
  process.exit(2);
}
const TEMPLATE_PAGES = path.join(TEMPLATE_ROOT, "src", "pages");
if (!fs.existsSync(TEMPLATE_PAGES)) {
  console.error(`Not found: ${TEMPLATE_PAGES}`);
  process.exit(2);
}
if (!fs.existsSync(SRC_PAGES)) {
  console.error(`Project pages not found: ${SRC_PAGES}`);
  process.exit(2);
}

async function listAllFiles(root) {
  const out = [];
  async function walk(dir) {
    const entries = await fsp.readdir(dir, { withFileTypes: true });
    for (const e of entries) {
      const full = path.join(dir, e.name);
      if (e.isDirectory()) await walk(full);
      else if (e.isFile()) out.push(full);
    }
  }
  await walk(root);
  return out;
}

function relPath(abs, base) {
  return path.relative(base, abs).replaceAll("\\", "/");
}

function targetPath(rel) {
  return path.join(SRC_PAGES, rel);
}

function demoTargetPath(rel) {
  const segs = rel.split("/");
  if (segs.length === 0 || rel === "") return path.join(SRC_PAGES, "demo_root");
  if (segs.length === 1) {
    return path.join(SRC_PAGES, "demo_root", segs[0]);
  }
  segs[0] = `demo_${segs[0]}`;
  return path.join(SRC_PAGES, segs.join("/"));
}

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function copyFileSync(src, dst) {
  ensureDir(path.dirname(dst));
  // Do not overwrite existing
  if (!fs.existsSync(dst)) fs.copyFileSync(src, dst);
}

const added = [];
const demoAdded = [];
const skipped = [];

const tplFilesAbs = await listAllFiles(TEMPLATE_PAGES);
const tplFiles = tplFilesAbs.map((f) => relPath(f, TEMPLATE_PAGES));

for (const rel of tplFiles) {
  const srcFile = path.join(TEMPLATE_PAGES, rel);
  const dstFile = targetPath(rel);
  if (fs.existsSync(dstFile)) {
    if (CONFLICT_MODE === "demo") {
      const demoDst = demoTargetPath(rel);
      if (!fs.existsSync(demoDst)) {
        if (APPLY) copyFileSync(srcFile, demoDst);
        demoAdded.push(relPath(demoDst, PROJECT_ROOT));
      } else {
        skipped.push(relPath(demoDst, PROJECT_ROOT));
      }
    } else {
      skipped.push(relPath(dstFile, PROJECT_ROOT));
    }
  } else {
    if (APPLY) copyFileSync(srcFile, dstFile);
    added.push(relPath(dstFile, PROJECT_ROOT));
  }
}

console.log("Planned additions:");
for (const f of added) console.log("  +", f);
if (CONFLICT_MODE === "demo") {
  for (const f of demoAdded) console.log("  +", f);
}
console.log("Skipped (existing):");
for (const f of skipped) console.log("  ~", f);
console.log("");
console.log("Run with --apply to perform copying.");

