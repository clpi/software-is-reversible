#!/bin/sh
set -eu
cd "$(dirname "$0")"
out=$1
mkdir -p "$out/wasm"
cp index.html style.css app.mjs native-abi.mjs pins.json fixture.json suffix-fixtures.json DIRECTIONS.md "$out"
cp wasm/*.wasm "$out/wasm/"
