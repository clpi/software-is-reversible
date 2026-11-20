# Idol-compiled reversal decision loop

A pure bounded model for the demo, not an OS action executor, a string
adapter, or a wrapper around a JavaScript reversal implementation. All
admission, freshness tests, receipt construction/decoding, reinstatement,
and postcondition checks are in `reversal.id`. JavaScript in `check.mjs`
supplies an independent reference and observations for the test. The module
has no effect grant; imported functions throw if reached.

## Contract

The exported functions have signed i64 WebAssembly arguments and results.
The portable domain is much narrower: a frame is `8 * epoch + value`, with
a 7-bit generation `0..127` and a three-bit value `0..7`. A plan is 1 to 4
base-4 action digits, first action least significant. Each plan digit is
nonzero: 1 flips the low bit; 2 clears; 3 rotates left by one. Caps are bits
1, 2, 4 respectively. Clear restoration additionally requires the separate
bit 8, not a replay of clear permission. Reversal of flip and rotate requires
the same corresponding current capability.

| Entry | Safe meaning on nonnegative result |
| --- | --- |
| `prepare(expected, observed, plan, caps)` | Compute a bounded receipt only after checking all actions against the passed capabilities and exact observed frame. |
| `advance(receipt, retained, freshBefore, caps)` | Validate the supplied receipt against a separately retained original, recheck fresh before-frame and current plan capability, derive proposed after-frame. |
| `verify(receipt, retained, freshAfter)` | Validate the actual observed after-frame against the qualified receipt's target. |
| `inverse(receipt, retained, freshAfter, caps)` | Recheck receipt, exact after-frame and inverse capabilities; derive a restored value at a new generation. |
| `undoverify(receipt, retained, prior, fresh, caps)` | Re-derive the admitted inverse from its prior observation and verify the separately observed post-undo frame. |

Wasm labels have prefix `idol_reversal__`. Other exports are implementation
helpers, not entrypoints for admission. The host must supply authentic
capability masks, fresh observations of the correct subject, a separately
retained original receipt, and whatever effect dispatch/verification
boundary applies to the abstract machine. Supplying the same adversarial
receipt twice is not authentication. Frame equality cannot observe
unreported updates; both forward and backward commits in an actual runtime
would need atomic compare/admit/apply or an explicit partial/uncertain
outcome. This module never effects that commit and never guesses an inverse
for an arbitrary external side effect.

Receipt decimal value:

    plan + 256 * (residual + 6561 * (postValue + 8 * startEpoch))

The residual is base 9 with one digit per action. A clear digit is the
prior value plus 1; an invertible action has digit 0. Zero on clear is
missing, not prior state zero. Exactly three bits of semantic information
are needed to distinguish the eight preimages of clear at fixed generation,
exposure, and action. Base 9 provides an extra malformed/missing sentinel;
the entire packed wire is not claimed byte-minimal. Flip and rotation are
bijective and do not consume residual. Undo restores the value, not prior
time; generation increases. Exhaustion refuses rather than wrapping.
Independent inverse reauthorization is required; a valid forward receipt
does not grant undo on its own.

Refusals: -1 malformed wire; -2 stale observation; -3 missing capability;
-4 missing clear residual; -5 inconsistent or extra residual; -6 supplied
ticket differs from retained original; -7 generation would overflow.

## Reproduce

Retained historical compiler revision
`5efca0e40430de5dfd592f534edf27f32305eb36`, executable SHA256
`3ba4c432cea98a0ed63652424f626a1be4c761a8b3c8abcd976f07291953469c`.
This is not a current-main compiler build. Build in serial from this directory:

    "$IDOL" compile --no-cache --backend=wasm --target wasm32-wasi reversal.id -o reversal.wasm
    "$IDOL" compile --no-cache --backend=wasm --target wasm32-wasi reversal.id -o reproduce.wasm
    cmp reversal.wasm reproduce.wasm
    node check.mjs | cmp - receipt.json

Actual identical outputs are included. Test receipt covers all 120 legal
plans, 8 states, 128 generations, and 16 forward capability masks
(1,966,080 decisions), inverse/verification controls on all 442,656
qualifying cases under varying independently chosen backward masks, 136
malformed plan values, and 22 named adversarial controls. It also shows
the clear collision and correct restoration of its distinct origins.
No host import calls were observed; no real-world actuator was exercised.
This is full finite forward matrix testing, not a Lean refinement proof
or unrestricted device rollback claim.
