"use strict";

const fs = require("node:fs");
const path = require("node:path");

const pkgRoot = path.join(__dirname, "..");
const src = path.join(pkgRoot, "migrations");
const dest = path.join(pkgRoot, "dist", "migrations");

if (!fs.existsSync(path.join(src, "meta", "_journal.json"))) {
  console.error(`copy-migrations: missing ${src}/meta/_journal.json`);
  process.exit(1);
}

fs.mkdirSync(path.dirname(dest), { recursive: true });
fs.cpSync(src, dest, { recursive: true });
