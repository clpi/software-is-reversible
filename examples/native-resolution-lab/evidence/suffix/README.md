# Native suffix DAG support count and witness pages

This is actual **Idol-generated Wasm** for a finite structured support
fixture. Given a topologically ordered suffix DAG, it computes count bounds
and returns only the requested lexicographic realization page. The browser
or Node host need not enumerate, score, rank or generate witnesses to
produce that page. JS in the receipt is an independent test oracle only.

- Tokens are 0, 1 and first EOS=2. Maximum declared horizon: 30. There are
  up to 128 suffix nodes. State 0 means no realizations, not a state.
- Node rows are [remaining depth, zero-child ID, one-child ID, EOS].
  Positive child IDs must precede the parent and have depth exactly one
  less. Child 0 means absent; -1 means unknown; a depth-one node has no
  children. EOS is 1 if known accepted, 0 if absent, -1 if unknown.
- Each shared child on a different labeled edge counts again, correctly,
  because histories with different first tokens are disjoint. Sharing
  suffix storage does not merge distinct token realizations.
- At any node, support sums over the disjoint zero, one and EOS terms.
  A known EOS contributes 1. An unknown EOS contributes [0,1]; an
  unknown non-EOS child at depth d contributes [0,2^(d-1)-1]. A bound is
  for the declared first-EOS scope and not an exact latent count.
- If lower differs from upper, a witness page refuses rather than
  silently skipping unknown paths that could alter ranks.
- Exact unranking checks whether rank is in the zero-child interval, then
  the one-child interval, then the optional EOS singleton. It emits the
  heap code for a single path; remove the leading binary 1 and append EOS.
  An exact count costs O(states), and each page costs O(states + page
  length × horizon), not O(number of supported realizations).

This module is **not** a neural model, a probability optimizer, or
deduplication for arbitrary equivalent weighted residuals. It neither
derives a suffix DAG from a real checkpoint nor asserts that a MAP
certificate materializes the support. To merge weighted residuals for
MAP, preserve complete stop/scope and conditional-weight semantics, not
just the positive support relation used here. The prior native finite
tensor decision covers MAP separately. Topological records can be prepared
by a host-controlled exact structural interner; fixture preprocessing is
not part of the native benchmark or a proof of global minimality.

## Packed linear-memory ABI

Export: idol_suffix__page(arena, nodes, root, horizon, start, limit) -> i64.
All arguments are BigInt signed i64 at the JS/Wasm boundary. The host owns
an aligned in-bounds arena of at least (6*nodes+2+limit) i64 words and does
not expose an arbitrary pointer to untrusted callers. The receipt uses byte
address 8192 in this module's exported memory; array view indices below are
zero-based (native indexing is one-based on this compiler).

    [0 .. 4*n)      input rows, four i64 words apiece, node IDs 1 .. n
    [4*n .. 6*n)    native scratch [lower,upper] per node
    [6*n .. 6*n+2)  root [lower,upper]
    [6*n+2 .. )     up to limit requested positive heap codes

Use start=0 and limit=0 for count-only, including unresolved bounds, which
returns 0. Otherwise 1 <= limit <= 32. The start rank is zero-based;
start == exact support is a valid empty page. Nonnegative return is the
actual page length; -1 is malformed scope/shape and leaves inputs/scratch
untouched, -2 refuses unresolved rank and publishes bounds, -3 reports
start greater than exact support and publishes the exact count. A direct
invalid raw address is outside this ABI contract and may Wasm-trap; arena
allocation is the host's responsibility. WASI calls are not needed.

## Reproduce

Compiler: preserved clpi/idol revision 5efca0e40430de5dfd592f534edf27f32305eb36.
Use the verified host compiler executable and unchanged serialization lock
from the containing artifact; this is not qualification of current main.

    sh "$LOCK" --timeout 0 -- "$IDOL" compile --no-cache --backend=wasm --target wasm32-wasi suffix.id -o suffix.wasm
    sh "$LOCK" --timeout 0 -- "$IDOL" compile --no-cache --backend=wasm --target wasm32-wasi suffix.id -o repeat.wasm
    cmp suffix.wasm repeat.wasm
    node check.mjs | cmp - receipt.json

The test covers 12-step baseline and three local edits, a 30-state fixture
standing for 1,073,741,823 paths, unresolved bounds, and 384 independent
small DAGs replayed with a separate exhaustive witness oracle. Receipt
overlap is not a benchmark, and test coverage is not a compiler proof.
