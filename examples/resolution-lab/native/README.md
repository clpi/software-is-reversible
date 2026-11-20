# Idol-generated numerical kernel

This is actual compiled Idol, not hand-encoded Wasm or a JavaScript numerical
stand-in. The compiler is the retained historical clpi/idol revision
5efca0e40430de5dfd592f534edf27f32305eb36, tree
021f67fd8d7726c843d1369bd61015b061109f96. The archived compiler's executable
SHA-256 is 3ba4c432cea98a0ed63652424f626a1be4c761a8b3c8abcd976f07291953469c.
The original preservation archive SHA-256 is
9563418b6f90d9e0f76b4ca4a2944e142eeec3a9d4d0503a45e4217ef6524e4a.
All retained archive manifest hashes and all 170 source Git blob receipts
were verified against their recorded identity. This is a retained compiler
and focused demo, not a current-main build or a compiler reproducibility claim.

## Build and validate

Run from this directory with absolute paths to the retained compiler and
unchanged serialization lock:

    sh "$LOCK" --timeout 0 -- "$IDOL" compile --no-cache --backend=wasm --target wasm32-wasi kernel.id -o kernel.wasm
    sh "$LOCK" --timeout 0 -- "$IDOL" compile --no-cache --backend=wasm --target wasm32-wasi kernel.id -o reproduce.wasm
    cmp kernel.wasm reproduce.wasm
    node check.mjs > receipt.json

The two builds were serial and byte-identical. Their logs are retained.
Node/V8 executes the same standard Wasm module and reports the actual module
imports, exports, controlled test cases and hashes. Browser DOM integration
is separate.

## ABI and effects

- idol_kernel__flip(i64) -> i64: x XOR 1 on the three-bit domain.
- idol_kernel__clear(i64) -> i64: zero on the three-bit domain.
- Both return -1 for tested values outside that domain.
- idol_kernel__compare(i64,i64) -> i64: signed comparison, -1/0/+1.
- The source types are i32; on this compiler pin the emitted Wasm ABI is
  i64, so JavaScript must supply BigInt after validating signed i32.
- The module declares five WASI function imports. The host supplies only
  throwing stubs and validation records zero host import calls. The module
  grants no console, file, environment, networking or process capability.
- Exported memory is not accessed by the supported calls.

Controls exhaust the three-bit domain and verify flip involution and clear
collisions, eight named refusal calls, and 4,761 signed comparison pairs.
This is bounded execution evidence, not universal compiler qualification.
