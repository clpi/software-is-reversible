#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p dist/native dist/fused
cp index.html style.css app.mjs search.mjs reversal.mjs inference.mjs kernel.mjs incidence.mjs fused.mjs benchmark-run1.json benchmark-run2.json dist/
cp native/kernel.wasm native/receipt.json dist/native/
cp fused/fused.wasm fused/benchmark.json dist/fused/
