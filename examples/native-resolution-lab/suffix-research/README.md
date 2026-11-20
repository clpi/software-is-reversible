# Economic test: separate an exact count from evidence disclosure

`SuffixPage.lean` models EOS-last ordered labeled transitions. Seven checks cover recurrence mass versus explicit enumeration, exact rank selection, exact page selection, out-of-range refusal, and distinctness under unique outgoing labels. It does not claim verified lowering to Wasm.

The two receipts time a requested page of eight, comparing an independent full enumeration then slicing with the pinned Idol Wasm algorithm that computes counts and un-ranks only requested items. The full and suffix-row JSON formats are deliberately different data layouts and both recover all supported strings in this scope. Reproduced four declared cuts, fixed request size, rotated order, 21 paired retained batches of 100 each per profile per process, both paths returned identical outputs checked for a near-tail page. Native time includes host marshalling and reading results. Input construction, weighted interning, compilation, browser DOM and external I/O are not measured.

On the 12-level unedited case, the expanded representation encoded 94,205 bytes and the shared input 128 bytes. The measured median query on two runs was 45–53 µs by enumeration and 3.1–3.5 µs via the native count/page, roughly 13–17× on this workload. Those are not global optimality or cross-venue claims. The 30-level control checks a count exceeding one billion and an exact selective tail page; it did not allocate one billion witnesses, nor compare that allocation in a benchmark.

From this directory, run `node benchmark.mjs "$(cd .. && pwd)"` when the parent is the native lab source (requires its pinned Wasm files). Check the formal model with `lean -DwarningAsError=true SuffixPage.lean`.
