# Native deterministic tensor decision

The entire finite path search, exact-rational maximum, unknown frontier
bound, canonical tie-break, stop eligibility, and certification status run
inside Idol source compiled to Wasm. JavaScript validates input in the UI,
passes integers and unpacks numeric fields; the separate test oracle is
not used to make the native decision. No host imports were called, and
the decision does not use host-supplied memory addresses.

This is a first-EOS model over three synthetic tensor rows, not a trained
language model or a claim about any real prompt. The architecture has a
root row and two last-non-EOS-token rows. Each row is packed as
m0 + 4*m1 + 16*mEOS with integer masses 0 through 3 and positive total.
A sentinel -1 means a missing, unresolved row rather than zero mass.
The API permits 1 ≤ firststop ≤ horizon ≤ 4. As usual first EOS terminates;
early EOS is out of scope, not renormalized, and reaching the horizon
without EOS is not counted as completion.

Call the exported idol_chat__decision with six signed i64 BigInt values:
root, rowZero, rowOne, firstStop, horizon, field. A return of -1n rejects
invalid requests. Use field=8n for the single-execution packed receipt.
Fields 0–7 also exist for a control/diagnostic mode:

| Field | Bits in packed value | Semantics |
|---|---|---|
| 0 | 0–2 | 0 unknown/no incumbent, 1 provisional incumbent, 2 exact score but canonical tie unresolved, 3 exact canonical winner, 4 no accepted positive completion |
| 1 | 3–6 | positive heap code: strip leading binary 1, append EOS id 2, or code 0 for no incumbent |
| 2 | 7–13 | incumbent numerator (0 if absent) |
| 3 | 14–26 | incumbent denominator (1 if absent) |
| 4 | 27–33 | inclusive upper-bound numerator |
| 5 | 34–46 | inclusive upper-bound denominator |
| 6 | 47–50 | number of known reachable prefix nodes |
| 7 | 51–54 | number of first missing positive prefix nodes |

All compared rational products are under 9⁸ and the receipt fits 55 bits.
Each accepted complete path is either evaluated exactly or descends from
one first unknown positive-mass prefix. Multiplying by further normalized
masses cannot increase its probability, so that prefix bounds its subtree.
The best completion's mass and the largest unknown bound define the
inclusive upper bound; a strict gap protects both optimal score and tie
choice. A bounded equality gives exact score only. The canonical tie rule
among known outputs is lex order on vocabulary ids including EOS.
This proof rationale is not a claim of a verified Idol compiler.

## Reproduce

The frozen historical compiler is clpi/idol revision
5efca0e40430de5dfd592f534edf27f32305eb36 (see the encompassing archive for
its preserved executable and identity). Set IDOL and LOCK to the absolute
paths of that compiler and its legacy serialization lock; run here:

    sh "$LOCK" --timeout 0 -- "$IDOL" compile --no-cache --backend=wasm --target wasm32-wasi chat.id -o chat.wasm
    sh "$LOCK" --timeout 0 -- "$IDOL" compile --no-cache --backend=wasm --target wasm32-wasi chat.id -o repeat.wasm
    cmp chat.wasm repeat.wasm
    node check.mjs | cmp - receipt.json

Byte-identical rebuild SHA-256 is recorded in the receipt. In 18,362
valid test fixtures (bounded product strata plus deterministic seed),
the native decision agreed on all outputs with an independent recursive
exact-arithmetic oracle. All five statuses were exercised. The packed
receipt agreed with eighty scalar-field calls. Thirteen malformed
inputs refused, and zero WASI import calls were observed.
