#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p dist/native
cp index.html style.css app.mjs search.mjs reversal.mjs inference.mjs kernel.mjs incidence.mjs benchmark-run1.json benchmark-run2.json dist/
cp native/kernel.wasm native/receipt.json dist/native/
