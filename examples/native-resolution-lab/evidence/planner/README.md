# Exact bounded planner, compiled from Idol

This standalone experiment uses an actual historical clpi/idol executable:
revision 5efca0e40430de5dfd592f534edf27f32305eb36, tree
021f67fd8d7726c843d1369bd61015b061109f96, compiler SHA-256
3ba4c432cea98a0ed63652424f626a1be4c761a8b3c8abcd976f07291953469c.
No changes to the demo site or repositories.

The unmodified emitted artifact SHA-256 is
29ec5ab2b4027d5c37938fdd7af41e13b1136b42545832b053391f355617e417.
Two serial independent compiles produced identical bytes; Node/V8
validated/instantiated the same artifact. Declared WASI imports use
refusing stubs; no import call occurred. This is not current-main or
browser delivery qualification.

## ABI

All arguments/result are Wasm i64 (JavaScript BigInt).

    idol_planner__plan(data, rows, initial, required, mode, mask, maximum,
      weight, work, capacity, output, limit)

- Append snapshots may have different data records at every call. Each row
  is nine signed i64 words: stage 1–4, required-capability mask,
  provided-capability mask, flags, then latency/storage/risk/clarity/compute
  or any five nonnegative metric coordinates. Masks use low 16 bits,
  provides must be nonzero, each raw metric must be 0–1,000,000.
- Rows are grouped by stage, at most eight per stage and 32 total. The
  input row order within each stage defines structural lexical order.
  If textual identity is used, the serializer must preserve it in those
  ordinals; native IDs are row positions and are not source authentication.
- Flags bit 0 = qualified, bit 1 = holdout. Mode 0 excludes held-out rows;
  mode 1 includes qualified held-out rows. Unqualified rows always excluded.
  Host attests/transports input qualification facts; no host decision about
  whether those facts satisfy a plan's consequences.
- `initial` and `required` are low-16-bit masks, required nonzero. A path is
  resolved only if all required facts are present after four allowed rows.
- `mask` chooses active objectives (nonempty low-five-bit mask).
  `maximum` sets which of those maximize (e.g. clarity bit 8), all others
  minimize. `weight` contains five 0–1,000,000 i64 weights with at least
  one selected positive weight. Weights rank survivors, never change Pareto
  membership. Structural lexical order breaks score ties and collapses
  duplicate active objective vectors to one earliest witness.
- `work` holds 9 i64 words per capacity row. `output` needs 3+9*limit i64
  words. Both row limits are 0–4096. The current kernel requires both
  capacity and limit to cover the completed pool even when output could
  fit a smaller frontier; it refuses rather than partially returning it.
- Result >=0 is frontier row count. Output header is three words:
  resolved candidate count, frontier count, one-based selected frontier
  ordinal (0 when absent). Then nine words per survivor: four one-based
  action row IDs, five raw summed metrics.
- Result -1 invalid shape/mode/masks, -2 invalid row/weight, -3 capacity.
  On refusal output stays unchanged. Work scratch may have partial writes.
- Wasm caller owns fresh disjoint physical buffers in memory, verifies wasm32
  address/extent/alignment and no alias, and writes/reads little-endian i64.
  Pointer indices in Idol are 1-based. Passing an invalid physical pointer
  is outside the ABI and can trap or corrupt; do not pretend native logical
  validation recognizes arbitrary offsets. Only expose the main entry
  through an embedding API; compiler helper exports are not public entries.

The native kernel validates row shape, walks all four stages with joint
premises in order, accumulates exact bounded integer metrics, checks all
resolved candidates for dominance and tie order, emits survivors, and
calculates the witness selected by the weighted objective. It does not
qualify source authority, re-derive observation receipts, implement
incremental reuse, or optimize whole-application runtime.

## Evidence

- check.mjs captured 537 complete comparisons against an independently
  verified JS Cartesian oracle, across 31 masks, both profiles, two
  weight vectors, and four fixture revisions/states, plus 40 seeded
  alternate fresh inputs. Comparisons cover resolved counts, exact
  surviving action paths, all raw metrics and winner. 10 separately
  malformed/capacity inputs produced expected refusal, intact prefix.
- boundary.mjs checked another 100 arbitrary bounded graphs with separate
  brute-force raw-row oracle, changed maximize masks and weights. Bounded
  maximal input 4096 completed paths, 4,000,000 metric sums, and million
  weights preserved one structural tie representative. Under-provisioned
  work/output and over-wide stage refused; full 294,936-byte output
  canary was intact under each refusal.
- Two compiled damage arms changed lexical tie direction and removed
  prerequisite checking. Both compiled to actual Wasm, started, and failed
  the held oracle assertions, rather than failing compiler or runtime setup.
- No arithmetic decision is delegated to JavaScript in the planner. JS
  validates physical ABI extents, maps labels to graph table encodings
  and renders output; test JS is an independent oracle.

Build from this directory with the pinned compiler and unchanged lock:

    sh "$LOCK" --timeout 0 -- "$IDOL" compile --no-cache --backend=wasm --target wasm32-wasi planner.id -o planner.wasm
    sh "$LOCK" --timeout 0 -- "$IDOL" compile --no-cache --backend=wasm --target wasm32-wasi planner.id -o repeat.wasm
    cmp planner.wasm repeat.wasm
    node check.mjs
    node boundary.mjs

Keep numeric planner limits and negative controls visible. Being exact on
this bounded graph shape does not imply universal Pareto completeness.
