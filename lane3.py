#!/usr/bin/env python3
"""Lane 3 validation harness — meta-search solve-and-validate, set B.

Three propositions, one contract per proposition, every rival
executed on the same battery, frontier computed weight-free
before any weighting selects.

Proposition 1 — deterministic decoding rivals: greedy, canonical
tie-break, factored recipe, best-first certified. Fixtures are
synthetic archived next-token rows keyed by the behavioral key
(prefix, token, checkpoint, protocol). Scores are integer
milli-log-probs; arithmetic is exact.

Proposition 2 — semantic and intent matrix resolution rivals:
from-scratch, incremental cone-scoped, on-the-fly budgeted.
Paired readings over one coordinate list; equality is exact.

Proposition 3 — the tensor-rewriting loop: a deterministic token
stream drives overlay edits that produce new weightings on the
fly. Overlay algebra mirrors the proved algebra in
Reversible.lean (protection, application, round trip, tied
preservation). Certification rule: a target-vector claim stands
only on a recomputed projection.

Stdlib only. Deterministic: seeded generators only, no clocks
in any verdict (timing is not measured; counted work is).
"""

import hashlib
import heapq
import json
import subprocess
import sys

CKPT = "synth-ckpt-1"
PROTO = "archived-rows-v1"
EOS = 0

# ------------------------------------------------------------ fixtures

def build_archive():
    """prefix tuple -> list of (token, score milli), row order as
    archived (deliberately scrambled where ties matter)."""
    arc = {}
    # chain: single path
    arc[("chain", ())] = [(1, -100)]
    arc[("chain", (1,))] = [(2, -100)]
    arc[("chain", (1, 2))] = [(EOS, -100)]
    # tie: three equal maxima, scrambled row order
    arc[("tie", ())] = [(3, -500), (2, -500), (1, -500)]
    for t in (1, 2, 3):
        arc[("tie", (t,))] = [(EOS, -100)]
    # trap: greedy first step leads to a bad continuation
    arc[("trap", ())] = [(4, -100), (5, -200)]
    arc[("trap", (4,))] = [(EOS, -2000)]
    arc[("trap", (5,))] = [(6, -100)]
    arc[("trap", (5, 6))] = [(EOS, -100)]
    # missing: continuation row absent -> unresolved branch
    arc[("missing", ())] = [(7, -300)]
    # branch: deterministic generated tree, depth 4, width 3
    def gen(fid, prefix, depth):
        if depth == 0:
            arc[(fid, prefix)] = [(EOS, -150)]
            return
        rows = []
        for k in range(3):
            tok = 10 + (sum(prefix) * 7 + k * 13 + depth * 29) % 40
            h = hashlib.sha256(
                ("branch|%s|%s" % (prefix, tok)).encode()).digest()
            score = -(100 + h[0] % 400)
            rows.append((tok, score))
        arc[(fid, prefix)] = rows
        for tok, _ in rows:
            gen(fid, prefix + (tok,), depth - 1)
    gen("branch", (), 4)
    return arc

ARCHIVE = build_archive()
FIXTURES = ["chain", "tie", "trap", "missing", "branch"]

def rows_for(fid, prefix):
    return ARCHIVE.get((fid, prefix))

def exhaustive_optimum(fid, prefix=(), depth=0):
    """Oracle: best complete-sequence total score, or None."""
    rows = rows_for(fid, prefix)
    if rows is None:
        return None
    best = None
    for tok, s in rows:
        if tok == EOS:
            cand = s
        else:
            sub = exhaustive_optimum(fid, prefix + (tok,), depth + 1)
            if sub is None:
                continue
            cand = s + sub
        if best is None or cand > best:
            best = cand
    return best

# ------------------------------------------------------------ decoders

def decode_greedy(fid):
    prefix, total, ops = (), 0, 0
    while True:
        rows = rows_for(fid, prefix)
        if rows is None:
            return {"stream": list(prefix), "total": total,
                    "status": "unresolved", "ops": ops, "cert": None}
        best = None
        for tok, s in rows:
            ops += 1
            if best is None or s > best[1]:
                best = (tok, s)
        total += best[1]
        if best[0] == EOS:
            return {"stream": list(prefix), "total": total,
                    "status": "complete", "ops": ops, "cert": None}
        prefix = prefix + (best[0],)

def decode_canonical(fid):
    prefix, total, ops = (), 0, 0
    while True:
        rows = rows_for(fid, prefix)
        if rows is None:
            return {"stream": list(prefix), "total": total,
                    "status": "unresolved", "ops": ops, "cert": None}
        pick = None
        for tok, s in sorted(rows, key=lambda r: r[0]):
            ops += 1
            if pick is None or s > pick[1]:
                pick = (tok, s)
        total += pick[1]
        if pick[0] == EOS:
            return {"stream": list(prefix), "total": total,
                    "status": "complete", "ops": ops, "cert": None}
        prefix = prefix + (pick[0],)

def factored_encode(fid):
    """Factored recipe form: per row, tokens sorted, scores as
    deltas from the row maximum. Exact reconstruction."""
    out = {}
    for (f, prefix), rows in sorted(ARCHIVE.items()):
        if f != fid:
            continue
        srt = sorted(rows, key=lambda r: r[0])
        mx = max(s for _, s in srt)
        out[str(prefix)] = [mx, [[t, s - mx] for t, s in srt]]
    return out

def factored_rows(enc, prefix):
    if str(prefix) not in enc:
        return None
    mx, deltas = enc[str(prefix)]
    return [(t, mx + d) for t, d in deltas]

def decode_factored(fid):
    enc = factored_encode(fid)
    prefix, total, ops = (), 0, 0
    while True:
        rows = factored_rows(enc, prefix)
        if rows is None:
            return {"stream": list(prefix), "total": total,
                    "status": "unresolved", "ops": ops, "cert": None}
        pick = None
        for tok, s in rows:
            ops += 1  # one delta application + compare per token
            if pick is None or s > pick[1]:
                pick = (tok, s)
        total += pick[1]
        if pick[0] == EOS:
            return {"stream": list(prefix), "total": total,
                    "status": "complete", "ops": ops, "cert": None}
        prefix = prefix + (pick[0],)

def decode_bestfirst(fid):
    # heap entries: (-total, prefix, complete_flag)
    heap = [(0, (), False)]
    ops = 0
    unresolved_bounds = []
    while heap:
        neg, prefix, complete = heapq.heappop(heap)
        total = -neg
        if complete:
            heap_max = -heap[0][0] if heap else None
            cert_ok = (heap_max is None or total >= heap_max) and \
                all(total >= b for b in unresolved_bounds)
            return {"stream": list(prefix), "total": total,
                    "status": "complete", "ops": ops,
                    "cert": {"certified": bool(cert_ok),
                             "heap_max_at_cert": heap_max,
                             "unresolved_bounds": unresolved_bounds}}
        rows = rows_for(fid, prefix)
        if rows is None:
            unresolved_bounds.append(total)  # carried, never dropped
            continue
        for tok, s in rows:
            ops += 1
            if tok == EOS:
                heapq.heappush(heap, (-(total + s), prefix, True))
            else:
                heapq.heappush(heap, (-(total + s), prefix + (tok,), False))
    return {"stream": [], "total": None, "status": "unresolved",
            "ops": ops, "cert": {"certified": False,
                                 "unresolved_bounds": unresolved_bounds}}

DECODERS = {"greedy": decode_greedy, "canonical": decode_canonical,
            "factored": decode_factored, "bestfirst": decode_bestfirst}

def storage_bytes(name, fid):
    if name == "factored":
        blob = json.dumps(factored_encode(fid), separators=(",", ":"),
                          sort_keys=True)
    else:
        rows = {str(p): r for (f, p), r in sorted(ARCHIVE.items()) if f == fid}
        blob = json.dumps(rows, separators=(",", ":"), sort_keys=True)
    return len(blob.encode())

def permuted_archive(seed):
    """Return a copy of ARCHIVE with each row's order permuted
    deterministically; used for the permutation-invariance axis.
    Seed -1 is the full reversal, which guarantees every tie's
    row order flips."""
    import random
    out = {}
    if seed == -1:
        for k, rows in ARCHIVE.items():
            out[k] = list(reversed(rows))
        return out
    rng = random.Random(seed)
    for k, rows in ARCHIVE.items():
        r = list(rows)
        rng.shuffle(r)
        out[k] = r
    return out

def prop1():
    global ARCHIVE
    results = {}
    optima = {fid: exhaustive_optimum(fid) for fid in FIXTURES}
    for name, fn in DECODERS.items():
        per = {}
        for fid in FIXTURES:
            per[fid] = fn(fid)
        # repeat determinism
        again = {fid: fn(fid) for fid in FIXTURES}
        det = json.dumps(per, sort_keys=True) == json.dumps(again, sort_keys=True)
        # permutation invariance: outputs must survive every
        # row-order permutation tried (reversal + five shuffles)
        saved = ARCHIVE
        inv = True
        try:
            for seed in (-1, 1, 2, 3, 4, 5):
                ARCHIVE = permuted_archive(seed)
                per_perm = {fid: fn(fid) for fid in FIXTURES}
                if not all(per_perm[f]["stream"] == per[f]["stream"] and
                           per_perm[f]["total"] == per[f]["total"]
                           for f in FIXTURES):
                    inv = False
        finally:
            ARCHIVE = saved
        gap = 0
        for fid in FIXTURES:
            if optima[fid] is not None and per[fid]["status"] == "complete":
                gap += optima[fid] - per[fid]["total"]
        certs = sum(1 for fid in FIXTURES
                    if per[fid]["cert"] and per[fid]["cert"]["certified"])
        # verify every issued certificate against the oracle
        cert_sound = True
        for fid in FIXTURES:
            c = per[fid]["cert"]
            if c and c["certified"]:
                if per[fid]["total"] != optima[fid]:
                    cert_sound = False
                if c["heap_max_at_cert"] is not None and \
                        per[fid]["total"] < c["heap_max_at_cert"]:
                    cert_sound = False
        results[name] = {
            "per_fixture": per, "gap_milli": gap,
            "ops_total": sum(per[f]["ops"] for f in FIXTURES),
            "storage_bytes": sum(storage_bytes(name, f) for f in FIXTURES),
            "deterministic_repeat": det,
            "permutation_invariant": inv,
            "certified_fixtures": certs, "cert_sound": cert_sound,
            "unresolved_carried": per["missing"]["status"] == "unresolved",
        }
    # frontier: minimize gap, ops, storage; maximize invariant, certs
    def axes(r):
        return (r["gap_milli"], r["ops_total"], r["storage_bytes"],
                0 if r["permutation_invariant"] else 1,
                -r["certified_fixtures"])
    frontier = []
    for a, ra in results.items():
        dominated = False
        for b, rb in results.items():
            if a == b:
                continue
            xa, xb = axes(ra), axes(rb)
            if all(x <= y for x, y in zip(xb, xa)) and \
                    any(x < y for x, y in zip(xb, xa)):
                dominated = True
        if not dominated:
            frontier.append(a)
    return {"optima": optima, "results": results, "frontier": frontier}

# ------------------------------------------------------------ prop 2

def make_records(n, coords, seedtag, density=8):
    recs = []
    for i in range(n):
        entries = {}
        for k in range(density):
            h = hashlib.sha256(("%s|%d|%d" % (seedtag, i, k)).encode()).digest()
            c = h[0] % coords
            sv = (h[1] % 17) - 8
            iv = (h[2] % 13) - 6
            if c in entries:
                s0, i0 = entries[c]
                entries[c] = (s0 + sv, i0 + iv)
            else:
                entries[c] = (sv, iv)
        recs.append(entries)
    return recs

def full_readings(recs, coords):
    sem = [0] * coords
    intent = [0] * coords
    joint = [0] * coords
    cnt = [0] * coords
    work = 0
    for rec in recs:
        for c, (s, i) in rec.items():
            sem[c] += s
            intent[c] += i
            joint[c] += s * i
            cnt[c] += 1
            work += 1
    return (sem, intent, joint, cnt), work

class Incremental:
    def __init__(self, coords):
        self.coords = coords
        self.sem = [0] * coords
        self.intent = [0] * coords
        self.joint = [0] * coords
        self.cnt = [0] * coords
        self.work = 0
    def append(self, rec):
        for c, (s, i) in rec.items():
            self.sem[c] += s
            self.intent[c] += i
            self.joint[c] += s * i
            self.cnt[c] += 1
            self.work += 1
    def readings(self):
        return (list(self.sem), list(self.intent),
                list(self.joint), list(self.cnt))

def run_matrix_dataset(recs, coords, checkpoints):
    """Returns equality verdicts and counted work for full vs incr."""
    inc = Incremental(coords)
    eq = 0
    full_work_total = 0
    seen = 0
    for idx, rec in enumerate(recs, 1):
        inc.append(rec)
        if idx in checkpoints:
            full, w = full_readings(recs[:idx], coords)
            full_work_total += w
            if list(full[0]) == inc.readings()[0] and \
               list(full[1]) == inc.readings()[1] and \
               list(full[2]) == inc.readings()[2] and \
               list(full[3]) == inc.readings()[3]:
                eq += 1
            seen += 1
    return {"checkpoints": seen, "equal": eq,
            "incr_work": inc.work, "full_work": full_work_total,
            "final": inc.readings()}

def prop2():
    out = {}
    # D1: 321-record analogue scale
    recs321 = make_records(321, 64, "d1")
    ck = {10, 150, 321}
    out["d1_321"] = run_matrix_dataset(recs321, 64, ck)
    # D2: held-out permutations of D1 order
    import random
    finals = []
    perm_runs = []
    base_final = None
    for seed in (11, 22, 33, 44, 55):
        rng = random.Random(seed)
        perm = list(recs321)
        rng.shuffle(perm)
        r = run_matrix_dataset(perm, 64, {80, 200, 321})
        perm_runs.append({"seed": seed, "equal": r["equal"],
                          "checkpoints": r["checkpoints"]})
        finals.append(json.dumps(r["final"], sort_keys=True))
        if base_final is None:
            base_final = finals[-1]
    out["d2_permutations"] = {
        "runs": perm_runs,
        "final_equal_across_permutations": len(set(finals)) == 1,
        "final_equal_to_unpermuted": finals[0] == json.dumps(
            out["d1_321"]["final"], sort_keys=True)}
    # D3: larger synthetic matrix
    recs_big = make_records(5000, 256, "d3")
    ck_big = set(range(500, 5001, 500))
    out["d3_large"] = run_matrix_dataset(recs_big, 256, ck_big)
    # D4: suffix form — prior 2000 carried, 3000 appended
    inc = Incremental(256)
    for rec in recs_big[:2000]:
        inc.append(rec)
    for rec in recs_big[2000:]:
        inc.append(rec)
    full_big, _ = full_readings(recs_big, 256)
    out["d4_suffix"] = {
        "equal": list(inc.readings()) == [list(x) for x in full_big]}
    # on-the-fly budgeted candidate on D3 final state
    budget_coords = list(range(64))  # 64 of 256 covered
    sem = [None] * 256
    intent = [None] * 256
    joint = [None] * 256
    work = 0
    covered = set(budget_coords)
    acc = {c: [0, 0, 0] for c in budget_coords}
    for rec in recs_big:
        for c, (s, i) in rec.items():
            if c in covered:
                a = acc[c]
                a[0] += s
                a[1] += i
                a[2] += s * i
                work += 1
    for c in budget_coords:
        sem[c], intent[c], joint[c] = acc[c]
    full_sem, full_int, full_joint, _ = full_big
    covered_ok = all(sem[c] == full_sem[c] and intent[c] == full_int[c]
                     and joint[c] == full_joint[c] for c in budget_coords)
    unresolved = [c for c in range(256) if c not in covered]
    out["onthefly"] = {
        "covered": len(budget_coords), "coords": 256,
        "covered_equal_full": covered_ok,
        "unresolved_printed": len(unresolved),
        "unresolved_are_none_not_placeholder":
            all(sem[c] is None for c in unresolved),
        "work": work}
    out["frontier_note"] = {
        "incr_work_d3": out["d3_large"]["incr_work"],
        "full_work_d3": out["d3_large"]["full_work"],
        "onthefly_work": work}
    return out

# ------------------------------------------------------------ prop 3

BASE_W = [0, 120, -40, 200, 200, 60, -80, 30,
          0, 0, 90, -150, 45, 45, -20, 10]  # coords 3,4 tied; 13,14 tied
TIED = [{3, 4}, {13, 14}]

class Refusal(Exception):
    pass

def check_edit(edit):
    coords = set(edit["after"].keys())
    for group in TIED:
        hit = coords & group
        if hit and hit != group:
            raise Refusal("R-TIED-SPLIT")
        if hit == group:
            vals = {edit["after"][c] for c in group}
            if len(vals) != 1:
                raise Refusal("R-TIED-SPLIT")

def apply_stack(base, stack):
    w = list(base)
    for edit in stack:
        for c, v in edit["after"].items():
            w[c] = v
    return w

def run_loop():
    """Stream -> edit -> reweight -> next token, over the trap and
    branch archives under current weightings (bias = weightings)."""
    stack = []
    weightings = list(BASE_W)
    incr_copy = list(BASE_W)
    prefix_by_fid = {"trap": (), "branch": ()}
    stream = []
    edits_log = []
    cert_checks = 0
    cert_ok = 0
    # Derived-vector edit rule, stated once and followed exactly:
    # (a) intent-named edits: a decoded token in the trigger table
    #     names an edit on the table's coordinate;
    # (b) obscurity-named edits: where the decoded row contains
    #     a candidate scoring at or below -300, the row's
    #     obscurity reading is above threshold and the derived
    #     vector names an edit of +150 on the worst candidate's
    #     coordinate (token mod width). Clause (a) takes
    #     precedence where both fire.
    # An edit whose coordinate sits in a tied group is constructed
    # over the whole group at one value, preserving the tie.
    triggers = {5: (6, 250), 4: (5, 100), 6: (0, 50)}
    fid = "trap"
    steps = 0
    while steps < 14:
        steps += 1
        prefix = prefix_by_fid[fid]
        rows = rows_for(fid, prefix)
        if rows is None:
            stream.append(("unresolved", fid))
            break
        pick = None
        for tok, s in sorted(rows, key=lambda r: r[0]):
            eff = s + (weightings[tok] if tok < len(weightings) else 0)
            if pick is None or eff > pick[1]:
                pick = (tok, eff, s)
        tok = pick[0]
        stream.append(tok)
        if tok == EOS:
            if fid == "trap":
                fid = "branch"
                continue
            break
        prefix_by_fid[fid] = prefix + (tok,)
        named = None
        if tok in triggers:
            named = triggers[tok]
        else:
            worst = min(rows, key=lambda r: r[1])
            if worst[1] <= -300:
                named = (worst[0] % len(BASE_W), 150)
        if named is not None:
            coord, delta = named
            group = {coord}
            for g in TIED:
                if coord in g:
                    group = set(g)
            new_val = weightings[coord] + delta
            edit = {"after": {c: new_val for c in sorted(group)},
                    "before": {c: weightings[c] for c in sorted(group)},
                    "trigger": tok, "step": steps}
            check_edit(edit)
            stack.append(edit)
            for c, v in edit["after"].items():
                incr_copy[c] = v
            # certification: recomputed projection from pinned base
            recomputed = apply_stack(BASE_W, stack)
            cert_checks += 1
            if recomputed == incr_copy:
                cert_ok += 1
            weightings = recomputed
            edits_log.append({"step": steps, "coords": sorted(group),
                              "after": new_val})
    protected_ok = all(
        weightings[c] == BASE_W[c] or
        any(c in e["after"] for e in stack)
        for c in range(len(BASE_W)))
    roundtrip_ok = apply_stack(BASE_W, []) == BASE_W and \
        apply_stack(BASE_W, stack) == weightings
    return {"stream": stream, "edits": edits_log,
            "final_weightings": weightings,
            "cert_checks": cert_checks, "cert_ok": cert_ok,
            "protected_ok": protected_ok, "roundtrip_ok": roundtrip_ok,
            "stack_len": len(stack)}

def prop3():
    r1 = run_loop()
    r2 = run_loop()
    blob1 = json.dumps(r1, sort_keys=True)
    det_same_process = blob1 == json.dumps(r2, sort_keys=True)
    digest = hashlib.sha256(blob1.encode()).hexdigest()
    # certification negative control: phantom edit claim
    stack = []
    w = list(BASE_W)
    edit = {"after": {6: BASE_W[6] + 250}, "before": {6: BASE_W[6]},
            "trigger": 5, "step": 1}
    stack.append(edit)
    claimed = list(w)
    claimed[6] = BASE_W[6] + 999  # proposing vector's claim, not the edit
    recomputed = apply_stack(BASE_W, stack)
    diff = [c for c in range(len(BASE_W)) if claimed[c] != recomputed[c]]
    phantom_refused = len(diff) > 0
    # tied-split refusal control
    refusal = None
    stack_before = json.dumps(stack, sort_keys=True)
    try:
        check_edit({"after": {3: 777}})
    except Refusal as e:
        refusal = str(e)
    refusal_clean = json.dumps(stack, sort_keys=True) == stack_before
    # checkpoint untouched: BASE_W never mutated
    base_intact = BASE_W == [0, 120, -40, 200, 200, 60, -80, 30,
                             0, 0, 90, -150, 45, 45, -20, 10]
    return {"run": r1, "deterministic_repeat": det_same_process,
            "digest": digest,
            "phantom_claim_refused": phantom_refused,
            "phantom_diff_coords": diff,
            "phantom_claimed_coord6": claimed[6],
            "phantom_recomputed_coord6": recomputed[6],
            "tied_refusal": refusal, "refusal_applied_nothing": refusal_clean,
            "base_checkpoint_intact": base_intact}

def main():
    if "--loop-digest" in sys.argv:
        print(hashlib.sha256(
            json.dumps(run_loop(), sort_keys=True).encode()).hexdigest())
        return
    p1 = prop1()
    p2 = prop2()
    p3 = prop3()
    # cross-process determinism for the loop
    proc = subprocess.run([sys.executable, __file__, "--loop-digest"],
                          capture_output=True, text=True)
    p3["cross_process_digest"] = proc.stdout.strip()
    p3["deterministic_cross_process"] = \
        proc.stdout.strip() == p3["digest"]
    out = {"repo_pin": "d05ff699511099e6b4b28b2ae50e5c7cd590507e",
           "prop1_decoding": p1, "prop2_matrix": p2, "prop3_loop": p3}
    with open("lane3-results.json", "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(json.dumps({
        "p1_frontier": p1["frontier"],
        "p1": {k: {kk: v[kk] for kk in
                    ("gap_milli", "ops_total", "storage_bytes",
                     "permutation_invariant", "certified_fixtures",
                     "cert_sound", "unresolved_carried",
                     "deterministic_repeat")}
               for k, v in p1["results"].items()},
        "p2_d1": {k: p2["d1_321"][k] for k in ("checkpoints", "equal", "incr_work", "full_work")},
        "p2_perm": p2["d2_permutations"],
        "p2_d3": {k: p2["d3_large"][k] for k in ("checkpoints", "equal", "incr_work", "full_work")},
        "p2_suffix": p2["d4_suffix"], "p2_onthefly": p2["onthefly"],
        "p3": {k: p3[k] for k in
               ("deterministic_repeat", "deterministic_cross_process",
                "digest", "phantom_claim_refused", "phantom_diff_coords",
                "tied_refusal", "refusal_applied_nothing",
                "base_checkpoint_intact")},
        "p3_run": {k: p3["run"][k] for k in
                   ("stream", "cert_checks", "cert_ok", "protected_ok",
                    "roundtrip_ok", "stack_len")},
    }, indent=1))

if __name__ == "__main__":
    main()
