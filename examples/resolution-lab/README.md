# Idol Resolution Lab

An interactive first slice of the campaign. Serve `dist/` over localhost or HTTPS. `make-stage.sh` rebuilds it. The browser does not send prompts to an inference service, and dispatch is confined to an 8-state sandbox.

```sh
node --test *.test.mjs
node native/check.mjs | cmp - native/receipt.json
lean -DwarningAsError=true proof/CompositionalPruning.lean
sh make-stage.sh
```

See [METHODOLOGY.md](METHODOLOGY.md) for claims, invariants, counterexamples, and the required campaign gates. The binary was built by Idol at retained revision `5efca0e`, not current main. The interface, fixture orchestration, BigInt arithmetic, and oracle are JS; the executed flip, clear and signed scalar comparison exports are compiled Idol Wasm. Overflowing cross-products retain an explicit exact BigInt path. See `native/receipt.json` for the binary receipt and `native/README.md` for rebuilding.
