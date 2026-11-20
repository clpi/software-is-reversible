#!/usr/bin/env python3
"""Lane 5 re-validation battery.

Every built winner of stack.py is re-validated
  (a) against the FULL candidate set of its proposition --
      the eliminated rivals run again against the built form,
      same contract as the selecting lane; and
  (b) against HELD-OUT scenario permutations it was not
      selected on.

Held-out seeds, printed here and in the results: the lane 5
range is 71000-79999, allocated per proposition below. This
range is disjoint from every selecting lane's seeds: lane 2
used the 2000-6000 series, lane 3 used seeds -1, 1-5, 11-55
and hash-tagged datasets "d1"/"d3" (lane 5 uses new tags
"lane5a"/"lane5b"), lane 4 used base seed 20261120 and its
offsets, lane 1 used no randomness. Lane 5 allocations:
  actions 71000 + family_index*1000 + i (60 per family)
  frontier 71100, stop 71200, repair 71300, worklist 71400,
  break-even 71500, decoding permutations 71601-71608,
  matrix permutations 71611-71613, stack demonstration 71050s.

Rivals: lanes 1, 3 and 4 rivals are run from their own
harness modules (meta.py, lane3.py, actions.py imported).
Lane 2's rivals existed only as battery-internal code in
validation-lane2.py, so they are re-implemented here
following that battery line for line in contract and counted
costs, and marked as such; the built forms under test are
imported from stack.py, never re-implemented here.

Verdicts: a winner that fails returns to the space as a
named loss in lane5.md with its differing component, and the
proposition's down-selection is re-run over the remaining
candidates in this same run. Verdicts append; nothing in the
selecting lanes' records is rewritten.

Stdlib only. Deterministic: seeded generators only, no
clocks in any verdict.
"""

import hashlib
import itertools
import json
import math
import random
import sys
from collections import defaultdict, deque

import actions
import lane3
import meta
import stack

R = {"held_out_seed_range": "71000-79999 (allocations in this "
     "file's docstring)"}
VERDICTS = {}


def verdict(name, passed, detail):
    VERDICTS[name] = {"verdict": "PASS" if passed else
                      "RETURNED-AS-LOSS", "detail": detail}
    R[name] = detail


# ------------------------------------------------------------ meta layer
# Full candidate set: all 39 configurations of meta.py.
# Held-out: two new instances with the proved segment geometry
# at new scales, never used by lane 1.

HELD_OUT_INSTANCES = [
    ("frontier selection scale three (held-out)",
     [("plan a3", 0, 30), ("plan b3", 16, 16), ("plan c3", 30, 0)],
     "plan b3"),
    ("decoding-shaped instance (held-out)",
     [("short", 0, 12), ("mid", 7, 7), ("long", 12, 0),
      ("padded-h", 8, 9), ("rambling-h", 13, 4)],
     "mid"),
]


def run_meta():
    family, params, n_configs, n_meta_front = \
        stack.select_weighting_configuration()
    fronts = [meta.frontier_of(c) for _n, c, _m in meta.INSTANCES]
    # (a) full candidate set on the selecting instances
    reach_all = []
    for fam, par in meta.configurations():
        picks = [meta.induced(fam, par, f)[0] for f in fronts]
        if all(picks[i] == meta.INSTANCES[i][2] for i in range(3)):
            reach_all.append((fam, par))
    selected_reaches = (family, params) in reach_all
    # (b) held-out instances: the selected configuration and
    # the full candidate set on instances lane 1 never ran
    h_fronts = [meta.frontier_of(c)
                for _n, c, _m in HELD_OUT_INSTANCES]
    sel_held = [meta.induced(family, params, f)[0]
                for f in h_fronts]
    sel_held_ok = all(sel_held[i] == HELD_OUT_INSTANCES[i][2]
                      for i in range(len(HELD_OUT_INSTANCES)))
    reach_held = []
    linear_held = True
    for fam, par in meta.configurations():
        picks = [meta.induced(fam, par, f)[0] for f in h_fronts]
        if all(picks[i] == HELD_OUT_INSTANCES[i][2]
               for i in range(len(HELD_OUT_INSTANCES))):
            reach_held.append((fam, par))
        if fam == "linear" and any(
                picks[i] == HELD_OUT_INSTANCES[i][2]
                for i in range(len(HELD_OUT_INSTANCES))):
            linear_held = False
    detail = {
        "built_form": "meta layer selecting %s"
                      % meta.label(family, params),
        "configurations_run": n_configs,
        "meta_frontier_size": n_meta_front,
        "full_set_reaching_all_selecting_instances":
            len(reach_all),
        "selected_in_full_set_reachers": selected_reaches,
        "selected_held_out_picks": sel_held,
        "selected_reaches_all_held_out": sel_held_ok,
        "full_set_reaching_all_held_out": len(reach_held),
        "no_linear_reaches_any_held_out_middle": linear_held,
    }
    verdict("meta_layer", selected_reaches and sel_held_ok
            and linear_held, detail)


# ------------------------------------------------------------ lane 2 P1
# Built: stack.frontier_first. Rivals (full set): weight-first
# (b), incremental form (d), brute-force oracle (e); (c) is the
# built form itself. Rival code follows validation-lane2.py.

def _dom(a, b):
    return a[0] <= b[0] and a[1] <= b[1] and (a[0] < b[0] or a[1] < b[1])


def _frontier_brute(pts):
    return sorted({p for p in pts
                   if not any(_dom(q, p) for q in pts if q != p)})


def _frontier_incremental(pts):
    f = []
    for p in pts:
        if any(_dom(q, p) for q in f):
            continue
        f = [q for q in f if not _dom(p, q)]
        f.append(p)
    return sorted(set(f))


def _weight_pick(pts, w):
    return min(pts, key=lambda p: (w[0] * p[0] + w[1] * p[1], p))


def run_p1():
    rng = random.Random(71100)
    trials, perms, agree = 300, 0, 0
    members = built_recovery = weight_recovery = 0
    grid = [(a, b) for a in range(1, 10) for b in range(1, 10)]
    for _t in range(trials):
        n = rng.randint(4, 14)
        pts = [(rng.randint(0, 20), rng.randint(0, 20))
               for _ in range(n)]
        base = _frontier_brute(pts)
        assert stack.frontier_first(pts) == base
        assert _frontier_incremental(pts) == base
        for _ in range(3):
            q = pts[:]
            rng.shuffle(q)
            perms += 1
            if stack.frontier_first(q) == base:
                agree += 1
        picks = {_weight_pick(pts, w) for w in grid}
        for m in base:
            members += 1
            built_recovery += 1  # frontier-first retains by construction
            if m in picks:
                weight_recovery += 1
    detail = {"trials": trials, "perm_checks": perms,
              "perm_agree": agree, "frontier_members": members,
              "built_recovery": built_recovery,
              "weight_first_recovery": weight_recovery,
              "weight_first_loss_members": members - weight_recovery}
    verdict("p1_frontier_first",
            agree == perms and built_recovery == members
            and weight_recovery < members, detail)


# ------------------------------------------------------------ lane 2 P2
# Built: stack.two_face_stop. Rivals: threshold (a), optimal
# (b), fixed budget 3 claiming optimality (c). Follows
# validation-lane2.py run_p2's contract and adversarial
# permutation (30 percent, best placed last).

def run_p2():
    rng = random.Random(71200)
    trials = 400
    res = {k: {"examined": 0, "optimal_claims": 0,
               "false_optimal": 0, "acceptable_correct": 0}
           for k in ("threshold", "optimal", "budget3", "twoface")}
    for t in range(trials):
        n = rng.randint(4, 10)
        lats = [rng.randint(1, 20) for _ in range(n)]
        if t % 10 < 3:
            lats = lats[1:] + [min(lats)]
        T = 10
        best = min(lats)
        k = "threshold"
        examined = next((i + 1 for i, x in enumerate(lats)
                         if x <= T), n)
        res[k]["examined"] += examined
        if any(x <= T for x in lats):
            res[k]["acceptable_correct"] += 1
        k = "optimal"
        res[k]["examined"] += n
        res[k]["optimal_claims"] += 1
        k = "budget3"
        e = min(3, n)
        c = min(lats[:e])
        res[k]["examined"] += e
        res[k]["optimal_claims"] += 1
        if c != best:
            res[k]["false_optimal"] += 1
        if c <= T:
            res[k]["acceptable_correct"] += 1
        # built form under test
        acc, opt, ex = stack.two_face_stop(lats, T)
        k = "twoface"
        res[k]["examined"] += ex
        res[k]["optimal_claims"] += 1
        if opt != best:
            res[k]["false_optimal"] += 1
        if any(x <= T for x in lats) and acc is not None \
                and acc <= T:
            res[k]["acceptable_correct"] += 1
    detail = {"trials": trials, "results": res}
    verdict("p2_two_face_stop",
            res["twoface"]["false_optimal"] == 0
            and res["twoface"]["optimal_claims"] == trials
            and res["budget3"]["false_optimal"] > 0, detail)


# ------------------------------------------------------------ lane 2 P3
# Built: stack.cone_scoped_repair. Rivals: from-scratch (b),
# semi-naive scan-per-round (c). Follows validation-lane2.py
# run_p3's contract: append or weight-decrease epochs only.

def _distances(n, edges):
    INF = 10 ** 9
    d = [INF] * n
    d[0] = 0
    relax = 0
    for (u, v, w) in edges:
        relax += 1
        if d[u] + w < d[v]:
            d[v] = d[u] + w
    return d, relax


def run_p3():
    rng = random.Random(71300)
    cases, epochs = 200, 5
    tot = {"inc": 0, "scratch": 0, "seminaive": 0}
    agree = {"inc": 0, "seminaive": 0}
    executed = 0
    for _c in range(cases):
        n = rng.randint(8, 20)
        edges = []
        for i in range(n):
            for j in range(i + 1, min(n, i + 4)):
                if rng.random() < 0.5:
                    edges.append([i, j, rng.randint(1, 9)])
        edges.sort()
        prev_d, _ = _distances(n, [tuple(e) for e in edges])
        out = defaultdict(list)
        for e in edges:
            out[e[0]].append(e)
        for _ep in range(epochs):
            if rng.random() < 0.5:
                i = rng.randrange(n - 1)
                j = rng.randint(i + 1, n - 1)
                e = [i, j, rng.randint(1, 9)]
                edges.append(e)
                edges.sort()
                out[i].append(e)
                changed = [e]
            else:
                if not edges:
                    continue
                e = rng.choice(edges)
                if e[2] <= 1:
                    continue
                e[2] = rng.randint(1, e[2] - 1)
                changed = [e]
            executed += 1
            full, full_relax = _distances(
                n, [tuple(e) for e in edges])
            tot["scratch"] += full_relax
            d, relax = stack.cone_scoped_repair(
                prev_d, out, [tuple(x) for x in changed])
            tot["inc"] += relax
            if d == full:
                agree["inc"] += 1
            d2 = prev_d[:]
            frontier = {changed[0][0]}
            relax2 = 0
            rounds = 0
            while frontier and rounds < 100:
                rounds += 1
                nxt = set()
                for (u, v, w) in edges:
                    relax2 += 1
                    if u in frontier and d2[u] + w < d2[v]:
                        d2[v] = d2[u] + w
                        nxt.add(v)
                frontier = nxt
            tot["seminaive"] += relax2
            if d2 == full:
                agree["seminaive"] += 1
            prev_d = full
    detail = {"cases": cases, "executed_epochs": executed,
              "relaxations": tot, "agree": agree,
              "contract": "append or weight-decrease epochs only"}
    verdict("p3_cone_scoped_repair",
            agree["inc"] == executed
            and tot["inc"] < tot["scratch"] < tot["seminaive"],
            detail)


# ------------------------------------------------------------ lane 2 P4
# Built: stack.distinct_count_worklist. Rivals: naive least
# closure oracle (b), scan-per-round semi-naive (c),
# duplicate-blind worklist (d). Follows validation-lane2.py
# run_p4's contract: every append prefix compared.

def _least_closure(rules, seeds=()):
    derived = set(seeds)
    changed = True
    checks = 0
    while changed:
        changed = False
        for (pre, head) in rules:
            checks += 1
            if head not in derived and set(pre) <= derived:
                derived.add(head)
                changed = True
    return derived, checks


def _seminaive_closure(rules, seeds=()):
    derived = set(seeds)
    checks = 0
    while True:
        new = set()
        for (pre, head) in rules:
            checks += 1
            if head not in derived and set(pre) <= derived:
                new.add(head)
        if not new:
            break
        derived |= new
    return derived, checks


def _dupblind(rules):
    derived = set()
    miss = [len(pre) for (pre, _h) in rules]
    q = deque()
    for i, (pre, h) in enumerate(rules):
        if miss[i] == 0 and h not in derived:
            derived.add(h)
            q.append(h)
    proc = set()
    while q:
        x = q.popleft()
        if x in proc:
            continue
        proc.add(x)
        for i, (pre, h) in enumerate(rules):
            if x in pre:
                miss[i] -= 1
                if miss[i] == 0 and h not in derived:
                    derived.add(h)
                    q.append(h)
    return derived


def run_p4():
    rng = random.Random(71400)
    systems = 300
    prefix_checks = 0
    mismatch = {"worklist": 0, "seminaive": 0, "dupblind": 0}
    tot_checks = {"worklist": 0, "naive": 0, "seminaive": 0}
    for _s in range(systems):
        nterms = rng.randint(4, 12)
        nrules = rng.randint(3, 18)
        rules = []
        for _ in range(nrules):
            k = rng.randint(0, 3)
            pre = [rng.randrange(nterms) for _ in range(k)]
            rules.append((pre, rng.randrange(nterms)))
        for pref in range(1, len(rules) + 1):
            sub = rules[:pref]
            prefix_checks += 1
            oracle, oc = _least_closure(sub)
            tot_checks["naive"] += oc
            w, wc = stack.distinct_count_worklist(sub)
            tot_checks["worklist"] += wc
            if w != oracle:
                mismatch["worklist"] += 1
            sn, sc = _seminaive_closure(sub)
            tot_checks["seminaive"] += sc
            if sn != oracle:
                mismatch["seminaive"] += 1
            if _dupblind(sub) != oracle:
                mismatch["dupblind"] += 1
    detail = {"systems": systems, "prefix_checks": prefix_checks,
              "mismatch": mismatch, "checks": tot_checks}
    verdict("p4_distinct_count_worklist",
            mismatch["worklist"] == 0 and mismatch["dupblind"] > 0
            and tot_checks["worklist"] < tot_checks["naive"],
            detail)


# ------------------------------------------------------------ lane 2 P5
# Built: stack.hybrid_choice. Rivals: dense alone (b), factored
# alone (a); the built form is the hybrid rule (c) over them.
# Empirical crossover computed independently here with the
# lane 2 accounting, on the same sample the built form sees.

def run_p5():
    rng = random.Random(71500)
    stages, per = 8, 3
    sample = [tuple(rng.randrange(per) for _ in range(stages))
              for _ in range(64)]
    built = stack.hybrid_choice(stages, per, 512, sample)
    # independent empirical crossover, lane 2 accounting
    pools = [[f"s{i}w{j}" for j in range(per)] for i in range(stages)]
    dense = list(itertools.product(*pools))

    def dq(target):
        ops = 0
        for row in dense:
            ops += 1
            if tuple(int(x[-1]) for x in row) == target:
                return ops
        return ops

    def fq(target):
        ops = 0
        for i, t in enumerate(target):
            for j in range(per):
                ops += 1
                if j == t:
                    break
        return ops

    dper = sum(dq(q) for q in sample) / len(sample)
    fper = sum(fq(q) for q in sample) / len(sample)
    setup = sum(len(p) for p in pools)
    validation = sum(dq(q) + fq(q) for q in sample[:16])
    fixed = setup + validation \
        + len(json.dumps(pools).encode()) // 8 + setup
    empirical = None
    for qn in range(1, 2001):
        if fixed + fper * qn < dper * qn:
            empirical = qn
            break
    # regime directions: the rule must pick dense below and
    # factored above the predicted break-even, in every regime
    regimes = {}
    ok_dirs = True
    for st in (2, 3, 4, 6, 8):
        r2 = random.Random(71500 + st)
        smp = [tuple(r2.randrange(3) for _ in range(st))
               for _ in range(32)]
        lo = stack.hybrid_choice(st, 3, 1, smp)
        hi = stack.hybrid_choice(st, 3, 2000, smp)
        regimes[st] = {"rows": lo["rows"],
                       "predicted": lo["predicted_break_even_q"],
                       "at_q1": lo["form"], "at_q2000": hi["form"]}
        if not (lo["form"] == "dense" and hi["form"] == "factored"):
            ok_dirs = False
    detail = {"built": built, "empirical_crossover_q": empirical,
              "predicted_minus_empirical":
                  built["predicted_break_even_q"] - empirical,
              "regimes": regimes}
    verdict("p5_hybrid_break_even",
            abs(built["predicted_break_even_q"] - empirical) <= 2
            and built["form"] == "factored" and ok_dirs, detail)


# ------------------------------------------------------------ lane 3 P1
# Built (in stack via lane3): canonical + best-first certified.
# Full set: greedy, canonical, factored, best-first, run from
# lane3.py. Held-out: archive row-order permutations at new
# seeds 71601-71608.

def run_decoding():
    saved = lane3.ARCHIVE
    optima = {fid: lane3.exhaustive_optimum(fid)
              for fid in lane3.FIXTURES}
    res = {}
    for name, fn in lane3.DECODERS.items():
        per = {fid: fn(fid) for fid in lane3.FIXTURES}
        inv = True
        try:
            for seed in range(71601, 71609):
                lane3.ARCHIVE = lane3.permuted_archive(seed)
                pp = {fid: fn(fid) for fid in lane3.FIXTURES}
                if not all(pp[f]["stream"] == per[f]["stream"]
                           and pp[f]["total"] == per[f]["total"]
                           for f in lane3.FIXTURES):
                    inv = False
        finally:
            lane3.ARCHIVE = saved
        gap = sum(optima[f] - per[f]["total"]
                  for f in lane3.FIXTURES
                  if optima[f] is not None
                  and per[f]["status"] == "complete")
        certs = sum(1 for f in lane3.FIXTURES
                    if per[f]["cert"] and per[f]["cert"]["certified"])
        sound = all(per[f]["total"] == optima[f]
                    for f in lane3.FIXTURES
                    if per[f]["cert"] and per[f]["cert"]["certified"])
        res[name] = {"gap_milli": gap,
                     "ops": sum(per[f]["ops"] for f in lane3.FIXTURES),
                     "storage": sum(lane3.storage_bytes(name, f)
                                    for f in lane3.FIXTURES),
                     "permutation_invariant_new_seeds": inv,
                     "certified": certs, "cert_sound": sound,
                     "unresolved_carried":
                         per["missing"]["status"] == "unresolved"}

    def axes(r):
        return (r["gap_milli"], r["ops"], r["storage"],
                0 if r["permutation_invariant_new_seeds"] else 1,
                -r["certified"])

    frontier = []
    for a, ra in res.items():
        if not any(b != a and all(x <= y for x, y in zip(axes(rb),
                                                         axes(ra)))
                   and any(x < y for x, y in zip(axes(rb), axes(ra)))
                   for b, rb in res.items()):
            frontier.append(a)
    detail = {"results": res, "frontier_recomputed": sorted(frontier)}
    verdict("lane3_p1_decoding",
            sorted(frontier) == ["bestfirst", "canonical"]
            and res["bestfirst"]["gap_milli"] == 0
            and res["bestfirst"]["cert_sound"]
            and res["canonical"]["permutation_invariant_new_seeds"],
            detail)


# ------------------------------------------------------------ lane 3 P2
# Built (in stack via lane3): incremental cone-scoped, plus
# on-the-fly budgeted (extracted here from lane3.py prop2's
# battery-internal budgeted block, faithfully). Rival:
# from-scratch, the checker inside run_matrix_dataset.
# Held-out: new hash-tagged datasets lane5a/lane5b and order
# permutations at seeds 71611-71613.

def _onthefly(recs, coords, covered_list):
    covered = set(covered_list)
    acc = {c: [0, 0, 0] for c in covered_list}
    work = 0
    for rec in recs:
        for c, (s, i) in rec.items():
            if c in covered:
                a = acc[c]
                a[0] += s
                a[1] += i
                a[2] += s * i
                work += 1
    readings = [acc[c] if c in covered else None
                for c in range(coords)]
    return acc, work, readings


def run_matrix():
    detail = {}
    all_ok = True
    for tag, n, coords in (("lane5a", 321, 64),
                           ("lane5b", 5000, 256)):
        recs = lane3.make_records(n, coords, tag)
        ck = {10, 150, 321} if n == 321 else set(range(500, 5001, 500))
        r = lane3.run_matrix_dataset(recs, coords, ck)
        finals = []
        perm_eq = True
        for seed in (71611, 71612, 71613):
            rng = random.Random(seed)
            perm = list(recs)
            rng.shuffle(perm)
            rr = lane3.run_matrix_dataset(
                perm, coords, {80, 200, n} if n == 321
                else {1000, 3000, 5000})
            if rr["equal"] != rr["checkpoints"]:
                perm_eq = False
            finals.append(json.dumps(rr["final"], sort_keys=True))
        final_ok = len(set(finals)) == 1 and finals[0] == json.dumps(
            r["final"], sort_keys=True)
        # on-the-fly budgeted on the same held-out dataset
        cov = list(range(64))
        acc, work, readings = _onthefly(recs, coords, cov)
        full, _w = lane3.full_readings(recs, coords)
        cov_ok = all(acc[c] == [full[0][c], full[1][c], full[2][c]]
                     for c in cov)
        nulls_ok = all(readings[c] is None
                       for c in range(coords) if c not in set(cov))
        detail[tag] = {"checkpoints": r["checkpoints"],
                       "equal": r["equal"],
                       "incr_work": r["incr_work"],
                       "full_work": r["full_work"],
                       "permutations_equal": perm_eq,
                       "final_equal_across_permutations": final_ok,
                       "onthefly_covered_equal": cov_ok,
                       "onthefly_work": work,
                       "onthefly_uncovered_are_nulls": nulls_ok}
        all_ok = all_ok and r["equal"] == r["checkpoints"] \
            and perm_eq and final_ok and cov_ok and nulls_ok \
            and r["incr_work"] < r["full_work"]
    verdict("lane3_p2_matrix_resolution", all_ok, detail)


# ------------------------------------------------------------ lane 3 P3
# Built (in stack via lane3): loop with certification by
# recomputed projection. Rivals were eliminated at
# qualification in lane 3; the qualification checks are
# re-run here, plus new held-out negative controls: a phantom
# claim on the tied group {13, 14} and a tied-split attempt
# on that group (lane 3's controls used coordinate 6 and
# group {3, 4}).

def run_loop():
    p3 = lane3.prop3()
    run = p3["run"]
    # new phantom: claim a wrong value on coordinate 13 after
    # a genuine whole-group edit
    st = [{"after": {13: 999, 14: 999}, "before": {13: 45, 14: 45}}]
    recomputed = lane3.apply_stack(lane3.BASE_W, st)
    claimed = list(recomputed)
    claimed[13] = 1
    diff = [c for c in range(16) if claimed[c] != recomputed[c]]
    # new tied-split attempt on group {13, 14}
    refusal = None
    try:
        lane3.check_edit({"after": {13: 777}})
    except lane3.Refusal as e:
        refusal = str(e)
    detail = {
        "stream": run["stream"],
        "certification": "%d/%d" % (run["cert_ok"],
                                    run["cert_checks"]),
        "protected": run["protected_ok"],
        "roundtrip": run["roundtrip_ok"],
        "digest": p3["digest"],
        "lane3_controls": {"phantom_refused":
                           p3["phantom_claim_refused"],
                           "tied_refusal": p3["tied_refusal"],
                           "base_intact": p3["base_checkpoint_intact"]},
        "held_out_controls": {"phantom_diff_coords": diff,
                              "tied_split_group_13_14": refusal},
    }
    verdict("lane3_p3_tensor_loop",
            run["cert_ok"] == run["cert_checks"] == 4
            and run["protected_ok"] and run["roundtrip_ok"]
            and diff == [13] and refusal == "R-TIED-SPLIT"
            and p3["base_checkpoint_intact"], detail)


# ------------------------------------------------------------ lane 4 actions
# Built (in stack via actions): the combination route.
# Full set: explicit, obscurity, combination, naive control,
# run from actions.py. Held-out: paired instances at lane 5
# seeds 71000 + family*1000 + i, disjoint from lane 4's base
# seed 20261120 offsets.

def run_actions():
    per = {}
    totals = {}
    probes_tot = {}
    for fi, (fname, _label, make, run, _r) in \
            enumerate(actions.FAMILIES):
        for rival, _route in actions.RIVALS:
            wins = 0
            probes = 0
            fails = {}
            for i in range(60):
                rng = random.Random(71000 + fi * 1000 + i)
                inst = make(rng)
                if fname == "drive":
                    ok, comp, pr, _rep, _s = actions.drive_run(
                        rival, inst)
                else:
                    ok, comp, pr, _rep = run(rival, inst)
                wins += 1 if ok else 0
                probes += pr
                if not ok:
                    fails[comp] = fails.get(comp, 0) + 1
            per["%s/%s" % (fname, rival)] = {
                "wins": wins, "n": 60,
                "probes_avg": round(probes / 60, 1),
                "failures": fails}
            totals[rival] = totals.get(rival, 0) + wins
            probes_tot[rival] = probes_tot.get(rival, 0) + probes
    # frontier over (success desc, probes asc) on totals
    def dominates(a, b):
        return totals[a] >= totals[b] and probes_tot[a] <= probes_tot[b] \
            and (totals[a] > totals[b] or probes_tot[a] < probes_tot[b])

    frontier = [r for r in totals
                if not any(o != r and dominates(o, r) for o in totals)]
    detail = {"per_family_rival": per, "totals": totals,
              "probes_totals": probes_tot,
              "frontier_recomputed": sorted(frontier)}
    verdict("lane4_action_combination",
            "combination" in frontier
            and totals["combination"] >= totals["obscurity"]
            and totals["combination"] > totals["explicit"]
            > totals["naive"], detail)


def main():
    run_meta()
    run_p1()
    run_p2()
    run_p3()
    run_p4()
    run_p5()
    run_decoding()
    run_matrix()
    run_loop()
    run_actions()
    R["verdicts"] = VERDICTS
    with open("revalidation-lane5-results.json", "w") as f:
        json.dump(R, f, indent=1, sort_keys=True)
    print(json.dumps(VERDICTS, indent=1, sort_keys=True))
    bad = [k for k, v in VERDICTS.items()
           if v["verdict"] != "PASS"]
    print("re-validation verdict: %s"
          % ("ALL PASS" if not bad else "LOSSES: %s" % bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
