# One Wasm call for a five-coordinate dominance predicate

This is a research alternative, not the default planner. In `fused.id`, the low five bits choose minimization axes. Supply already oriented signed i32 coordinates. On this historical emitter's JS ABI, pass 11 BigInt values: a mask from 1 to 31, the five A coordinates, then the five B coordinates. Return 1 for strict dominance, 0 for no dominance or a tie, -1 for a malformed mask.

The same retained compiler as the original demo produced two byte-identical binaries. Run `node fused/test.mjs | cmp - fused/tests.json` from the lab. This checks every pair of vectors over {-1,0,1} across all 31 masks, 20,000 held-out signed-i32 pairs, endpoint and refusal cases. It is not a proof of compiler correctness or of unmeasured architectures.

Run `node fused/benchmark.mjs "$PWD"` from the lab for the paired Node microbenchmark. The raw receipt includes payoffs and losses. Fused validation beat scalar validation on three of four profiles; JS still beat fused validation in three profiles. Prepacked calling was faster in the timed loop but excluded 1.3–4.4 μs/pair of measured packing in these trials. Do not deploy prepacking on that evidence alone. Count conversion, memory, and repeated calls on a fixed snapshot before selection.
