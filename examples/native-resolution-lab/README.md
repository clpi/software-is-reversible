# Idol native resolution lab

The bounded decision engines in `source/` are Idol compiled to Wasm. They accept changing data, not just a fixed precomputed outcome. The browser adapter serializes fields, fences host imports, exposes no device effect authority, and renders native results. HTML, CSS, and the browser byte/DOM bridge are not Idol. No JavaScript solver fallback.

The exact planner exhaustively recomputes the declared cut (up to 8 rows per stage, 4 stages, 16 capabilities, 5 objectives). An isolated native reranker reuses a retained frontier only for the same unchanged cut, axes and admission profile; changing any of those forces a new solve. The tensor engine accepts three packed transition rows, one unknown-row symbol and parameters for within-scope stopping. Reversal checks mono-generation observations in an 8-state sandbox against the retained ticket and current capability masks. It derives targets; none of these targets is an external effect receipt.

The raw planner consumes declared observation/qualification flags, not authenticated external evidence. The reversible sandbox observes its own state, not an independent I/O device. The compiler is the retained 5efca0e build rather than a current-main compiler. Native execution is not a whole-site language claim.

## Reproduce

- Serve this directory over HTTPS or localhost, loading `index.html`. No package install, external service, or model needed.
- `node check-adapter.mjs` exercises final published wires and altered-module refusals.
- `cd evidence/planner && node check.mjs && node boundary.mjs` replays the independent planner comparisons.
- `cd evidence/chat && node check.mjs | cmp - receipt.json` and `cd evidence/reversal && node check.mjs | cmp - receipt.json` replay compiled controls. The `evidence/` subdirectories include exact build pairs and pins.
- `lean -DwarningAsError=true proof/ProductFrontier.lean` and `lean -DwarningAsError=true proof/ActionConsensus.lean` check the two compounding proof lanes. Theorems are not claims that the current native planner implements resumption.
- See [DIRECTIONS.md](DIRECTIONS.md) for the high-payoff bets, how they compose, and the tests that can falsify each.

Browser shipping must verify the installed binary hashes, independent oracle parity, visibly working app and exact serving endpoint. Owner-only preview and public custom domain are distinct states.

The shared suffix engine counts support or returns a bounded exact witness page without materializing the support. Unknown transitions preserve lower and upper bounds; a page that might misorder unknown witnesses is refused. Its topological input is preconstructed for the demo, not a native interner for real models. Run `node evidence/suffix/check.mjs | cmp - evidence/suffix/receipt.json` for four local-edit controls, a 30-state billion-witness case, and seeded independent exhaustive checks.

The two full planner corpora in Git are gzip-compressed; `gzip -dc` extracts them. The checker recomputes the JSON corpus.
