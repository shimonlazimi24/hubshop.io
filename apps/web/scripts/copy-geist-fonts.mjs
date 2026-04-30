/* global console, process */
/**
 * Copies variable WOFF2 files from the official `geist` npm package into
 * public/fonts/ for self-hosted @font-face loading (Vite serves /fonts/...).
 *
 * If the package is missing (e.g. devDependencies omitted) but this repo
 * already has committed assets under public/fonts/, exits successfully so
 * `pnpm build` still works.
 *
 * Uses require.resolve("geist/font") because this package's "exports" field
 * does not expose package.json for resolution.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const webRoot = path.join(__dirname, "..");
const require = createRequire(import.meta.url);

const outDir = path.join(webRoot, "public", "fonts");
const sansDest = path.join(outDir, "geist-sans.woff2");
const monoDest = path.join(outDir, "geist-mono.woff2");
const licenseDest = path.join(outDir, "Geist-LICENSE.txt");

function committedFontAssetsPresent() {
  return (
    fs.existsSync(sansDest) &&
    fs.existsSync(monoDest) &&
    fs.existsSync(licenseDest)
  );
}

let geistFontsDir;
let geistPackageRoot;
try {
  const fontEntry = require.resolve("geist/font");
  const distDir = path.dirname(fontEntry);
  geistFontsDir = path.join(distDir, "fonts");
  geistPackageRoot = path.join(distDir, "..");
} catch {
  console.warn(
    "[copy-geist-fonts] Cannot resolve `geist/font` (install devDependencies to refresh fonts).",
  );
  if (committedFontAssetsPresent()) {
    console.log("[copy-geist-fonts] Using committed files in public/fonts/");
    process.exit(0);
  }
  console.error(
    "[copy-geist-fonts] No Geist package and no committed font assets in public/fonts/.",
  );
  process.exit(1);
}

const sansSrc = path.join(geistFontsDir, "geist-sans", "Geist-Variable.woff2");
const monoSrc = path.join(geistFontsDir, "geist-mono", "GeistMono-Variable.woff2");

fs.mkdirSync(outDir, { recursive: true });

const licenseSrc = path.join(geistPackageRoot, "LICENSE.txt");
if (fs.existsSync(licenseSrc)) {
  fs.copyFileSync(licenseSrc, licenseDest);
  console.log("[copy-geist-fonts] copied Geist-LICENSE.txt");
}

const pairs = [
  [sansSrc, sansDest, "geist-sans.woff2"],
  [monoSrc, monoDest, "geist-mono.woff2"],
];

let copyFailed = false;
for (const [src, dest, label] of pairs) {
  if (!fs.existsSync(src)) {
    console.warn(`[copy-geist-fonts] Missing source file: ${src}`);
    copyFailed = true;
    continue;
  }
  fs.copyFileSync(src, dest);
  console.log(`[copy-geist-fonts] copied ${label}`);
}

if (copyFailed) {
  if (committedFontAssetsPresent()) {
    console.warn(
      "[copy-geist-fonts] Copy incomplete; keeping existing public/fonts/ assets.",
    );
    process.exit(0);
  }
  process.exit(1);
}
