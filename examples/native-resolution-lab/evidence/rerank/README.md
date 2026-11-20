# Isolated Idol reweighting of an already certified frontier

Weight-only operation. This does not certify a frontier, update its
qualification, revalidate an axis or cut change, process append/withdraw,
or prove cache identity. The embedding must bind the original admitted
graph snapshot, cut, active axes/directions and qualification context;
retain that certified frontier immutable; expose a *weights-only* input.
A caller-supplied shape-valid forged candidate list is not evidence.

Historical clpi/idol compiler revision 5efca0e40430de5dfd592f534edf27f32305eb36,
executable SHA-256
3ba4c432cea98a0ed63652424f626a1be4c761a8b3c8abcd976f07291953469c.
Byte-identical independent compile of rerank.wasm and repeat.wasm, each
4,526 bytes. Artifact SHA-256
459aad978f8509856582d1f45650ee6b1578f0a158c1cdea3a2e2b0945ed0b1f.

## ABI

    idol_rerank__winner(frontier, rows, mask, maximum, weight) -> i64

All parameters and result use Wasm i64 (JS BigInt). Data uses the existing
planner output layout: header [resolvedCount, frontCount, originalWinner],
then each nine-word [four path row IDs, five raw metrics] in ascending
structural/lexical order. Each row ID must be 1–32, increasing within a path.
Logical malformed shape/order/value fails. The original winner is shape-
checked only, not proof of admission. Mask/directions must be the values
bound to the original frontier, not new input. Weights are five i64 values
in 0..1,000,000 with at least one positive active weight. Metrics max
4,000,000; sums bounded by 20,000,000,000,000 in magnitude.

Returns one-based frontier ordinal; 0 for valid empty frontier.
Ties preserve first structural witness. -1 scalar shape/masks, -2 invalid
frontier, -3 invalid weights. Reads only, writes no output. Caller owns
canonical aligned u32 offsets, disjoint valid memory extents, little-endian
i64 encoding and address safety. Compiler helper exports are not product
entries; WASI symbols are import declarations with throwing stubs.

## Controls

- 2,232 weight/cut/profile/snapshot queries matched both full original
  native recomputation and independent JS verified Cartesian oracle.
  This included 420 changed winners and 558 empty selections.
- All retained frontier words, including the existing original winner,
  stayed unchanged across calls. Recomputed frontier vectors/rows matched.
- 11 invalid inputs refused; zero host import calls.
- A compiled control changed tie handling to choose the later witness;
  the independent behavior test caught it. Build success itself was not
  counted as a negative result.

No timing or performance claim. No site, production repository or prior
planner artifact modified. To reproduce, use the same retained compiler
and unchanged lock from the planner receipt, building rerank.id twice via
`compile --no-cache --backend=wasm --target wasm32-wasi` with no main, then
run `node check.mjs`.
