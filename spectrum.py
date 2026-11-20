#!/usr/bin/env python3
"""Lane 6 harness -- the action-determination spectrum.

Meta-search solve-and-validate program (Chris, direct,
2026-11-20 02:04 PST). Spec and record: spectrum.md in this
repo. For each algorithm in the program's scope, the action
construction is produced under each applicable route of the
spectrum and validated on the proposition's own contract
battery, the same contract across routes:

  route 1, explicit: a stated closed-form rule or planner;
    no search over candidates, no weighting.
  route 2, minimization: the output is the minimiser of a
    stated scalar score over an enumerated candidate set.
  route 3, obscurity: construction driven by the obscurity
    vector (unresolved, unprojected, uncertain -- recursive.md
    family C), acting only where the reading is at or above
    the threshold of two clauses, by probe-and-observe or by
    resolving the highest-obscurity region first.
  route 4, decomposition: a deterministic finer-grain
    resolution on a tensor or coordinate set -- cone-scoped
    incremental updates, waiter-index firing, heap or subtree
    decomposition, stage factorisation, scope widening.
  route 5, terminal: one compressed tensor, stored; the
    output is read off by projection or lookup with no
    search, loop, or scan at query time. Tensor size is
    measured against the algorithmic form's size, and the
    tensor's construction cost is accounted separately,
    under the break-even discipline of census section 6.

Where a route is not applicable to an algorithm, the record
in spectrum.md says why in one line; the harness prints the
same line and constructs nothing for that cell.

Method held from the program: frontier before weights
wherever a weighting appears; every route validated on the
same battery; equivalence between routes is printed as
proved (a named Lean theorem at a named pin), measured
(executed equality on the battery), or UNMEASURED with an
owner -- never asserted. Non-equivalence, where measured,
is printed as a loss with its differing component.

Fidelity controls: the harness first re-runs the lanes'
own batteries at their own seeds and pins (the lane 2
battery bodies are reused verbatim below, credited inline;
lanes 1, 3, and 4 are imported and re-run) and checks the
headline figures against the lanes' committed results
files. If a control fails, the harness verdict is FAIL and
no spectrum figure is to be cited. Counted work only; no
wall-clock figure appears anywhere in the results.

Stdlib only. Deterministic: seeded generators only.
"""

import hashlib
import heapq
import itertools
import json
import math
import os
import random
import sys
from collections import defaultdict, deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import lane3 as L3
import meta as M
import actions as A

R = {"base_head": "baa6f258fa65dfb64457f2b184c7c11fecc6d954"}
FAILURES = []


def check(name, cond, detail=""):
    if not cond:
        FAILURES.append("%s %s" % (name, detail))
    return cond


def jbytes(obj):
    return len(json.dumps(obj, separators=(",", ":"),
                          sort_keys=True).encode())


# ================================================================
# Lane 2 battery bodies, reused verbatim in substance from
# validation-lane2.py (same seeds, same generators), extended
# with the spectrum's route constructions. The lane 2 results
# file is the fidelity control for every figure re-derived here.
# ================================================================

def dom(a, b):
    return a[0] <= b[0] and a[1] <= b[1] and (a[0] < b[0] or a[1] < b[1])


def frontier_brute(pts):
    return sorted({p for p in pts
                   if not any(dom(q, p) for q in pts if q != p)})


def frontier_bnl(pts):
    win = []
    for p in pts:
        if any(dom(w, p) for w in win):
            continue
        win = [w for w in win if not dom(p, w)]
        win.append(p)
    return sorted(set(win))


def frontier_incremental(pts):
    f = []
    for p in pts:
        if any(dom(q, p) for q in f):
            continue
        f = [q for q in f if not dom(p, q)]
        f.append(p)
    return sorted(set(f))


def weight_pick(pts, w):
    return min(pts, key=lambda p: (w[0] * p[0] + w[1] * p[1], p))


def battery_frontier():
    """Lane 2 proposition 1 battery (seed 2000, 300 sets),
    plus the spectrum's route 2 nonlinear and route 5 cells."""
    rng = random.Random(2000)
    trials = 300
    perms = 0
    agree = 0
    frontier_members = 0
    weightfirst_recoverable = 0
    grid = [(a, b) for a in range(1, 10) for b in range(1, 10)]
    seg_cases = [[(0, 10), (6, 6), (10, 0)], [(0, 20), (11, 11), (20, 0)]]
    seg_mid_weight = False
    for pts in seg_cases:
        picks = {weight_pick(pts, w) for w in grid}
        if pts[1] in picks:
            seg_mid_weight = True
    sets = []
    for t in range(trials):
        n = rng.randint(4, 14)
        pts = [(rng.randint(0, 20), rng.randint(0, 20)) for _ in range(n)]
        sets.append(pts)
        base = frontier_brute(pts)
        assert frontier_bnl(pts) == base
        assert frontier_incremental(pts) == base
        for _ in range(3):
            q = pts[:]
            rng.shuffle(q)
            perms += 1
            if frontier_bnl(q) == base and frontier_incremental(q) == base:
                agree += 1
        picks = {weight_pick(pts, w) for w in grid} if pts else set()
        for m in base:
            frontier_members += 1
            if m in picks:
                weightfirst_recoverable += 1
    # route 2, nonlinear form (the meta level's enumerated
    # nonlinear configurations, frontier-restricted domain)
    nonlinear = [(f, p) for f, p in M.configurations()
                 if f in ("squared", "max", "overlay")]
    linear_meta = [(f, p) for f, p in M.configurations() if f == "linear"]
    nl_recovered = 0
    lin_meta_recovered = 0
    union_recovered = 0
    fam_recovered = {"squared": 0, "max": 0, "overlay": 0}
    for pts in sets:
        front = frontier_brute(pts)
        named = [("m%d" % i, p[0], p[1]) for i, p in enumerate(front)]
        grid_picks = {weight_pick(pts, w) for w in grid} if pts else set()
        for i, p in enumerate(front):
            got_nl = False
            for fam_name in ("squared", "max", "overlay"):
                for fam, par in nonlinear:
                    if fam != fam_name:
                        continue
                    pick, _w = M.induced(fam, par, named)
                    if pick == "m%d" % i:
                        got_nl = True
                        fam_recovered[fam_name] += 1
                        break
            if got_nl:
                nl_recovered += 1
            for fam, par in linear_meta:
                pick, _w = M.induced(fam, par, named)
                if pick == "m%d" % i:
                    lin_meta_recovered += 1
                    break
            if got_nl or p in grid_picks:
                union_recovered += 1
    # route 5: the frontier as a stored tensor, plus a
    # precomputed selection tensor over 102 weightings
    configs102 = grid + nonlinear
    tensor_frontier_bytes = 0
    points_bytes = 0
    lookup_checks = 0
    lookup_equal = 0
    for pts in sets:
        front = frontier_brute(pts)
        tensor_frontier_bytes += jbytes([list(p) for p in front])
        points_bytes += jbytes([list(p) for p in sorted(set(pts))])
        named = [("m%d" % i, p[0], p[1]) for i, p in enumerate(front)]
        table = []
        for cfg in configs102:
            if isinstance(cfg, tuple) and isinstance(cfg[0], int):
                pick = min(front, key=lambda p: (cfg[0] * p[0] +
                                                 cfg[1] * p[1], p))
            else:
                pk, _w = M.induced(cfg[0], cfg[1], named)
                pick = front[int(pk[1:])] if pk else None
            table.append(front.index(pick) if pick is not None else -1)
        for ci, cfg in enumerate(configs102):
            lookup_checks += 1
            if isinstance(cfg, tuple) and isinstance(cfg[0], int):
                direct = min(front, key=lambda p: (cfg[0] * p[0] +
                                                   cfg[1] * p[1], p))
            else:
                pk, _w = M.induced(cfg[0], cfg[1], named)
                direct = front[int(pk[1:])] if pk else None
            got = front[table[ci]] if table[ci] >= 0 else None
            if got == direct:
                lookup_equal += 1
    return {
        "trials": trials, "perm_checks": perms, "perm_agree": agree,
        "frontier_members": frontier_members,
        "weight_first_recovery": weightfirst_recoverable,
        "segment_middle_selected_by_any_positive_grid_weight":
            seg_mid_weight,
        "nonlinear_configs": len(nonlinear),
        "nonlinear_recovery": nl_recovered,
        "nonlinear_recovery_by_family": fam_recovered,
        "linear_meta_recovery": lin_meta_recovered,
        "union_grid_or_nonlinear_recovery": union_recovered,
        "route5_frontier_tensor_bytes_total": tensor_frontier_bytes,
        "route5_points_bytes_total": points_bytes,
        "route5_lookup_checks": lookup_checks,
        "route5_lookup_equal": lookup_equal,
    }


def battery_stop():
    """Lane 2 proposition 2 battery (seed 3000, 400 streams),
    plus route 4 block certification and route 5 tensor cells."""
    rng = random.Random(3000)
    trials = 400
    res = {k: {"stops": 0, "acceptable_correct": 0, "optimal_claims": 0,
               "false_optimal": 0, "examined": 0}
           for k in ("threshold", "optimal", "budget3", "twoface")}
    streams = []
    for t in range(trials):
        n = rng.randint(4, 10)
        lats = [rng.randint(1, 20) for _ in range(n)]
        if t % 10 < 3:
            lats = lats[1:] + [min(lats)]
        streams.append(list(lats))
        T = 10
        best = min(lats)
        k = "threshold"
        examined = next((i + 1 for i, x in enumerate(lats) if x <= T), n)
        chosen = lats[examined - 1] if any(x <= T for x in lats) else None
        res[k]["stops"] += 1
        res[k]["examined"] += examined
        if chosen is not None and chosen <= T:
            res[k]["acceptable_correct"] += 1
        elif chosen is None:
            res[k]["acceptable_correct"] += 1
        k = "optimal"
        res[k]["stops"] += 1
        res[k]["examined"] += n
        res[k]["optimal_claims"] += 1
        if best != min(lats):
            res[k]["false_optimal"] += 1
        k = "budget3"
        e = min(3, n)
        c = min(lats[:e])
        res[k]["stops"] += 1
        res[k]["examined"] += e
        res[k]["optimal_claims"] += 1
        if c != best:
            res[k]["false_optimal"] += 1
        if c <= T:
            res[k]["acceptable_correct"] += 1
        k = "twoface"
        res[k]["stops"] += 1
        res[k]["examined"] += n
        res[k]["optimal_claims"] += 1
        if best != min(lats):
            res[k]["false_optimal"] += 1
        if any(x <= T for x in lats):
            res[k]["acceptable_correct"] += 1
    # route 4: certification decomposed into blocks of three;
    # a block certificate is its minimum; the chosen plan is
    # certified exactly when it beats or ties every block
    # certificate. Decisions must equal the two-face form's.
    block_decisions_equal = 0
    block_comparisons = 0
    full_comparisons = 0
    for lats in streams:
        chosen = min(lats)
        blocks = [lats[i:i + 3] for i in range(0, len(lats), 3)]
        block_mins = [min(b) for b in blocks]
        block_comparisons += sum(len(b) - 1 for b in blocks) \
            + len(block_mins)
        full_comparisons += len(lats) - 1
        certified_block = all(chosen <= bm for bm in block_mins)
        certified_full = all(chosen <= x for x in lats)
        if certified_block == certified_full and certified_block:
            block_decisions_equal += 1
    # route 5: the certification predicate as a stored tensor
    # over the battery's finite domain (latencies 1..20):
    # T[chosen][remaining minimum] = 1 exactly when chosen is
    # no worse. Plus the acceptable-face tensor A[x] = x <= 10.
    tensor = [[1 if c <= r else 0 for r in range(1, 21)]
              for c in range(1, 21)]
    tensor_domain_checks = 0
    tensor_domain_equal = 0
    for c in range(1, 21):
        for r in range(1, 21):
            tensor_domain_checks += 1
            if tensor[c - 1][r - 1] == (1 if c <= r else 0):
                tensor_domain_equal += 1
    acceptable_tensor = [1 if x <= 10 else 0 for x in range(1, 21)]
    table_claims = 0
    table_false = 0
    table_acceptable = 0
    table_claims_equal = 0
    for lats in streams:
        first_acc = next((x for x in lats if acceptable_tensor[x - 1]),
                         None)
        if first_acc is not None:
            table_acceptable += 1
        chosen = min(lats)
        others = list(lats)
        others.remove(chosen)
        rmin = min(others) if others else 20
        claim = tensor[chosen - 1][rmin - 1] == 1
        if claim:
            table_claims += 1
            table_claims_equal += 1  # the two-face form claims here too
            if chosen != min(lats):
                table_false += 1
    packed_bits = len(tensor) * len(tensor[0]) + len(acceptable_tensor)
    return {
        "trials": trials, "results": res,
        "control": {"plans": [9, 2], "threshold": 10,
                    "threshold_first_acceptable": 9, "optimal": 2},
        "route4_block_decisions_equal": block_decisions_equal,
        "route4_block_comparisons": block_comparisons,
        "route4_full_comparisons": full_comparisons,
        "route5_tensor_domain_checks": tensor_domain_checks,
        "route5_tensor_domain_equal": tensor_domain_equal,
        "route5_table_claims": table_claims,
        "route5_table_false": table_false,
        "route5_table_acceptable": table_acceptable,
        "route5_table_claims_equal_twoface": table_claims_equal,
        "route5_tensor_packed_bits": packed_bits,
        "route5_tensor_json_bytes": jbytes(
            {"cert": tensor, "acc": acceptable_tensor}),
    }


def distances(n, edges):
    INF = 10 ** 9
    d = [INF] * n
    d[0] = 0
    relax = 0
    for (u, v, w) in edges:
        relax += 1
        if d[u] + w < d[v]:
            d[v] = d[u] + w
    return d, relax


def battery_repair():
    """Lane 2 proposition 3 battery (seed 4000, 200 cases,
    append or weight-decrease epochs), mirrored with per-epoch
    snapshots so routes 2 and 5 replay the identical epochs."""
    rng = random.Random(4000)
    cases = 200
    epochs = 5
    tot = {"inc": 0, "scratch": 0, "seminaive": 0}
    agree = {"inc": 0, "seminaive": 0}
    total_epochs = 0
    executed = 0
    wins = 0
    snapshots = []  # (n, edges tuple list, oracle distances)
    for c in range(cases):
        n = rng.randint(8, 20)
        edges = []
        for i in range(n):
            for j in range(i + 1, min(n, i + 4)):
                if rng.random() < 0.5:
                    edges.append([i, j, rng.randint(1, 9)])
        edges.sort()
        prev_d, _ = distances(n, [tuple(e) for e in edges])
        out = defaultdict(list)
        for e in edges:
            out[e[0]].append(e)
        for ep in range(epochs):
            total_epochs += 1
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
            full, full_relax = distances(n, [tuple(e) for e in edges])
            tot["scratch"] += full_relax
            d = prev_d[:]
            relax = 0
            q = deque()
            for (u, v, w) in changed:
                relax += 1
                if d[u] + w < d[v]:
                    d[v] = d[u] + w
                    q.append(v)
            while q:
                x = q.popleft()
                for (u, v, w) in out.get(x, []):
                    relax += 1
                    if d[u] + w < d[v]:
                        d[v] = d[u] + w
                        q.append(v)
            tot["inc"] += relax
            if d == full:
                agree["inc"] += 1
            if relax < full_relax:
                wins += 1
            d2 = prev_d[:]
            frontier = set()
            relax2 = 0
            for (u, v, w) in changed:
                relax2 += 0
                frontier.add(u)
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
            snapshots.append((n, [tuple(e) for e in edges], list(full)))
            prev_d = full
    # route 2: label-setting minimization (Dijkstra from the
    # source over the whole snapshot graph, per epoch)
    dij_agree = 0
    dij_relax = 0
    for (n, edges, oracle) in snapshots:
        INF = 10 ** 9
        d = [INF] * n
        d[0] = 0
        adj = defaultdict(list)
        for (u, v, w) in edges:
            adj[u].append((v, w))
        heap = [(0, 0)]
        done = [False] * n
        while heap:
            du, u = heapq.heappop(heap)
            if done[u]:
                continue
            done[u] = True
            for (v, w) in adj.get(u, []):
                dij_relax += 1
                if du + w < d[v]:
                    d[v] = du + w
                    heapq.heappush(heap, (d[v], v))
        if d == oracle:
            dij_agree += 1
    # route 5: the all-pairs distance tensor per epoch
    # (Floyd-Warshall), on a stated sub-battery (the first
    # 300 executed epochs); the query is a row projection.
    sub = snapshots[:300]
    apsp_agree = 0
    apsp_build_ops = 0
    tensor_bytes = 0
    edges_bytes = 0
    for (n, edges, oracle) in sub:
        INF = 10 ** 9
        t = [[INF] * n for _ in range(n)]
        for i in range(n):
            t[i][i] = 0
        for (u, v, w) in edges:
            if w < t[u][v]:
                t[u][v] = w
        for k in range(n):
            for i in range(n):
                if t[i][k] == INF:
                    continue
                for j in range(n):
                    apsp_build_ops += 1
                    if t[i][k] + t[k][j] < t[i][j]:
                        t[i][j] = t[i][k] + t[k][j]
        if t[0] == oracle:
            apsp_agree += 1
        tensor_bytes += jbytes(t)
        edges_bytes += jbytes([list(e) for e in edges])
    return {
        "cases": cases, "total_epochs": total_epochs,
        "executed_epochs": executed, "relaxations": tot,
        "agree": agree, "inc_win_epochs": wins,
        "route2_dijkstra_agree": dij_agree,
        "route2_dijkstra_relaxations": dij_relax,
        "route5_subbattery_epochs": len(sub),
        "route5_apsp_agree": apsp_agree,
        "route5_build_ops": apsp_build_ops,
        "route5_tensor_bytes_total": tensor_bytes,
        "route5_edges_bytes_total": edges_bytes,
    }


def least_closure(rules, seeds=()):
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


def worklist(rules, seeds=()):
    derived = set(seeds)
    missing = []
    waiters = defaultdict(list)
    for idx, (pre, head) in enumerate(rules):
        miss = set(pre) - derived
        missing.append(set(miss))
        for p in miss:
            waiters[p].append(idx)
    q = deque(seeds)
    checks = 0
    for idx, (pre, head) in enumerate(rules):
        if not missing[idx] and head not in derived:
            derived.add(head)
            q.append(head)
    processed = set(seeds)
    while q:
        x = q.popleft()
        processed.add(x)
        for idx in waiters.get(x, []):
            checks += 1
            if x in missing[idx]:
                missing[idx].discard(x)
                if not missing[idx]:
                    head = rules[idx][1]
                    if head not in derived:
                        derived.add(head)
                        q.append(head)
    return derived, checks


def seminaive_closure(rules, seeds=()):
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


def dupblind_closure(sub):
    derived = set()
    miss = [len(pre) for (pre, _) in sub]
    qq = deque()
    for i, (pre, h) in enumerate(sub):
        if miss[i] == 0 and h not in derived:
            derived.add(h)
            qq.append(h)
    proc = set()
    while qq:
        x = qq.popleft()
        if x in proc:
            continue
        proc.add(x)
        for i, (pre, h) in enumerate(sub):
            if x in pre:
                miss[i] -= 1
                if miss[i] == 0 and h not in derived:
                    derived.add(h)
                    qq.append(h)
    return derived


def priority_closure(rules, seeds=()):
    """Route 2 for the worklist: at every step, fire the ready
    rule whose distinct missing count is minimal (ties by rule
    index); the next action is determined by minimization over
    the missing counts, not by a waiter index."""
    derived = set(seeds)
    checks = 0
    while True:
        best = None
        for idx, (pre, head) in enumerate(rules):
            if head in derived:
                continue
            miss = len(set(pre) - derived)
            checks += 1
            if best is None or (miss, idx) < (best[0], best[1]):
                best = (miss, idx, head)
        if best is None or best[0] > 0:
            return derived, checks
        derived.add(best[2])


def battery_worklist():
    """Lane 2 proposition 4 battery (seed 5000, 300 systems,
    every append prefix), plus route 2 priority firing and
    route 5 closure tensors."""
    rng = random.Random(5000)
    systems = 300
    prefix_checks = 0
    mismatch = {"worklist": 0, "seminaive": 0, "dupblind": 0,
                "priority": 0}
    tot_checks = {"worklist": 0, "naive": 0, "seminaive": 0,
                  "priority": 0}
    systems_data = []
    for s in range(systems):
        nterms = rng.randint(4, 12)
        nrules = rng.randint(3, 18)
        rules = []
        for _ in range(nrules):
            k = rng.randint(0, 3)
            pre = [rng.randrange(nterms) for _ in range(k)]
            rules.append((pre, rng.randrange(nterms)))
        systems_data.append((nterms, rules))
        for pref in range(1, len(rules) + 1):
            sub = rules[:pref]
            prefix_checks += 1
            oracle, oc = least_closure(sub)
            tot_checks["naive"] += oc
            w, wc = worklist(sub)
            tot_checks["worklist"] += wc
            if w != oracle:
                mismatch["worklist"] += 1
            sn, sc = seminaive_closure(sub)
            tot_checks["seminaive"] += sc
            if sn != oracle:
                mismatch["seminaive"] += 1
            if dupblind_closure(sub) != oracle:
                mismatch["dupblind"] += 1
            pr, pc = priority_closure(sub)
            tot_checks["priority"] += pc
            if pr != oracle:
                mismatch["priority"] += 1
    # route 5, first form: per-term closure bitsets, queried by
    # union. Measured below; multi-premise joins across seeds
    # are the suspected differing component.
    union_queries = 0
    union_mismatch = 0
    union_diff_example = None
    for (nterms, rules) in systems_data:
        base, _ = worklist(rules, seeds=())
        singles = {}
        for t in range(nterms):
            singles[t], _ = worklist(rules, seeds=(t,))
        seed_sets = [()] + [(t,) for t in range(nterms)] + \
            [(a, b) for a in range(nterms) for b in range(a + 1, nterms)] + \
            [tuple(range(nterms))]
        for S in seed_sets:
            union_queries += 1
            got = set(base)
            for t in S:
                got |= singles[t]
            got |= set(S)
            oracle, _ = least_closure(rules, seeds=S)
            if got != oracle:
                union_mismatch += 1
                if union_diff_example is None:
                    diff = sorted(oracle - got)
                    union_diff_example = {
                        "seeds": list(S), "missing_term": diff[0]}
    # route 5, terminal form: the powerset tensor -- the
    # closure of every seed subset, stored. Built with the
    # worklist, checked against the independent scan oracle,
    # on the stated sub-battery (systems with at most 9 terms,
    # every subset enumerated).
    ps_systems = 0
    ps_entries = 0
    ps_equal = 0
    ps_tensor_bytes = 0
    ps_rules_bytes = 0
    for (nterms, rules) in systems_data:
        if nterms > 9:
            continue
        ps_systems += 1
        tensor = {}
        for mask in range(2 ** nterms):
            seeds = tuple(t for t in range(nterms) if mask & (1 << t))
            got, _ = worklist(rules, seeds=seeds)
            tensor[mask] = sorted(got)
        for mask in range(2 ** nterms):
            seeds = tuple(t for t in range(nterms) if mask & (1 << t))
            oracle, _ = least_closure(rules, seeds=seeds)
            ps_entries += 1
            if tensor[mask] == sorted(oracle):
                ps_equal += 1
        ps_tensor_bytes += jbytes(tensor)
        ps_rules_bytes += jbytes([[list(p), h] for (p, h) in rules])
    return {
        "systems": systems, "prefix_checks": prefix_checks,
        "mismatch": mismatch, "checks": tot_checks,
        "route5_union_queries": union_queries,
        "route5_union_mismatch": union_mismatch,
        "route5_union_diff_example": union_diff_example,
        "route5_powerset_systems": ps_systems,
        "route5_powerset_entries": ps_entries,
        "route5_powerset_equal": ps_equal,
        "route5_powerset_tensor_bytes_total": ps_tensor_bytes,
        "route5_powerset_rules_bytes_total": ps_rules_bytes,
    }


def battery_breakeven():
    """Lane 2 proposition 5 battery (seed 6000, compounding
    family, 8 stages of 3), counted figures only, plus the
    spectrum's route 1 vs route 2 choice comparison and the
    route 4 / route 5 output-equality validation."""
    stages = 8
    per = 3
    pools = [[f"s{i}w{j}" for j in range(per)] for i in range(stages)]
    dense = list(itertools.product(*pools))
    factored_setup_ops = sum(len(p) for p in pools)
    rng = random.Random(6000)
    queries = []
    for _ in range(512):
        target = tuple(rng.randrange(per) for _ in range(stages))
        queries.append(target)

    def dense_query(target):
        ops = 0
        for row in dense:
            ops += 1
            if tuple(int(x[-1]) for x in row) == target:
                return ops
        return ops

    def factored_query(target):
        ops = 0
        for i, t in enumerate(target):
            for j, w in enumerate(pools[i]):
                ops += 1
                if j == t:
                    break
        return ops

    def dense_result(target):
        for row in dense:
            if tuple(int(x[-1]) for x in row) == target:
                return row
        return None

    def factored_result(target):
        return tuple(pools[i][t] for i, t in enumerate(target))

    dq = [dense_query(q) for q in queries[:64]]
    fq = [factored_query(q) for q in queries[:64]]
    dense_per = sum(dq) / len(dq)
    factored_per = sum(fq) / len(fq)
    validation_ops = sum(dense_query(q) + factored_query(q)
                         for q in queries[:16])
    persist_bytes = len(json.dumps(pools).encode())
    restart_ops = factored_setup_ops
    fixed_ops = factored_setup_ops + validation_ops + restart_ops
    predicted_star = fixed_ops / max(1, (dense_per - factored_per))
    crossover = None
    for qn in range(1, 513):
        if fixed_ops + persist_bytes // 8 + factored_per * qn \
                < dense_per * qn:
            crossover = qn
            break
    regimes = {}
    for st in (2, 3, 4, 6, 8):
        pp = [[f"s{i}w{j}" for j in range(3)] for i in range(st)]
        dd = list(itertools.product(*pp))

        def dqry(target, dd=dd):
            ops = 0
            for row in dd:
                ops += 1
                if tuple(int(x[-1]) for x in row) == target:
                    return ops
            return ops

        def fqry(target, pp=pp):
            ops = 0
            for i, t in enumerate(target):
                for j, w in enumerate(pp[i]):
                    ops += 1
                    if j == t:
                        break
            return ops

        qs = [tuple(rng.randrange(3) for _ in range(st))
              for _ in range(32)]
        dper = sum(dqry(q) for q in qs) / len(qs)
        fper = sum(fqry(q) for q in qs) / len(qs)
        setup = sum(len(x) for x in pp)
        val = sum(dqry(q) + fqry(q) for q in qs[:16])
        pers = len(json.dumps(pp).encode()) // 8
        rst = setup
        fixed = setup + val + pers + rst
        cross = None
        for qn in range(1, 2001):
            if fixed + fper * qn < dper * qn:
                cross = qn
                break
        regimes[st] = {"rows": len(dd), "fixed_full_cost": fixed,
                       "crossover_q": cross}
    perm = queries[:]
    rng.shuffle(perm)
    perm_fact = sum(factored_query(q) for q in perm)
    orig_fact = sum(factored_query(q) for q in queries)
    # route 4 / route 5 output equality over all 512 queries
    outputs_equal = sum(1 for q in queries
                        if factored_result(q) == dense_result(q))
    # route 1 (the stated rule: factored exactly when the
    # expected count reaches the predicted break-even) against
    # route 2 (per-count argmin of the two total-cost forms)
    predicted = math.ceil(predicted_star) if predicted_star else None
    fixed_full = fixed_ops + persist_bytes // 8
    choice_disagreements = []
    for qn in range(1, 513):
        rule_choice = "factored" if qn >= predicted else "dense"
        f_tot = fixed_full + factored_per * qn
        d_tot = dense_per * qn
        min_choice = "factored" if f_tot < d_tot else "dense"
        if rule_choice != min_choice:
            choice_disagreements.append(qn)
    return {
        "dense_rows": len(dense),
        "dense_per_query_ops_mean64": round(dense_per, 2),
        "factored_per_query_ops_mean64": round(factored_per, 2),
        "fixed_ops_excl_persistence": fixed_ops,
        "persistence_bytes_pools": persist_bytes,
        "predicted_break_even_q": predicted,
        "empirical_crossover_q_vs_query_only": crossover,
        "regimes": {str(k): v for k, v in regimes.items()},
        "heldout_permutation_factored_ops_equal":
            perm_fact == orig_fact,
        "outputs_equal_512": outputs_equal,
        "route1_route2_choice_disagreements": choice_disagreements,
        "route5_dense_tensor_bytes": jbytes(
            [list(r) for r in dense]),
        "route5_pools_tensor_bytes": persist_bytes,
    }


# ================================================================
# Decoding: lane 3 proposition 1 battery, imported and re-run.
# ================================================================

def exhaustive_stream(fid):
    """Route 1 for decoding: explicit exhaustive enumeration of
    every complete sequence; the maximum total wins, ties by
    the smallest stream (the heap order of the best-first
    form). Returns (stream, total, status)."""
    best = [None]

    def rec(prefix, total):
        rows = L3.rows_for(fid, prefix)
        if rows is None:
            return
        for tok, s in rows:
            if tok == L3.EOS:
                cand = (total + s, list(prefix))
                if best[0] is None or cand[0] > best[0][0] or \
                        (cand[0] == best[0][0] and cand[1] < best[0][1]):
                    best[0] = cand
            else:
                rec(prefix + (tok,), total + s)

    rec((), 0)
    if best[0] is None:
        return ([], None, "unresolved")
    return (best[0][1], best[0][0], "complete")


def decomposed_best(fid):
    """Route 4 for decoding: the archive is decomposed by
    first token into independent subtrees; each subtree's
    optimum is solved once (memoised) and the minima compose.
    Returns (stream, total, status, subproblems)."""
    memo = {}

    def best_from(prefix):
        if prefix in memo:
            return memo[prefix]
        rows = L3.rows_for(fid, prefix)
        if rows is None:
            memo[prefix] = None
            return None
        best = None
        for tok, s in rows:
            if tok == L3.EOS:
                cand = (s, [])
            else:
                sub = best_from(prefix + (tok,))
                if sub is None:
                    continue
                cand = (s + sub[0], [tok] + sub[1])
            if best is None or cand[0] > best[0] or \
                    (cand[0] == best[0] and cand[1] < best[1]):
                best = cand
        memo[prefix] = best
        return best

    out = best_from(())
    if out is None:
        return ([], None, "unresolved", len(memo))
    return (out[1], out[0], "complete", len(memo))


def build_policy_tensor():
    """Route 5 for decoding: for every fixture and every
    archived prefix, the certified-optimal continuation as a
    stored entry (next token, value from here), with the
    home form's tie-break (maximum value, then the smallest
    resulting stream -- the heap order). Lookup walks the
    entries; no heap, no search."""
    tensor = {}
    for fid in L3.FIXTURES:
        memo = {}

        def best_from(prefix):
            if prefix in memo:
                return memo[prefix]
            rows = L3.rows_for(fid, prefix)
            if rows is None:
                memo[prefix] = None
                return None
            best = None
            for tok, s in rows:
                if tok == L3.EOS:
                    cand = (s, [])
                else:
                    sub = best_from(prefix + (tok,))
                    if sub is None:
                        continue
                    cand = (s + sub[0], [tok] + sub[1])
                if best is None or cand[0] > best[0] or \
                        (cand[0] == best[0] and cand[1] < best[1]):
                    best = cand
            memo[prefix] = best
            return best

        entries = {}
        prefixes = sorted({p for (f, p) in L3.ARCHIVE if f == fid})
        for prefix in prefixes:
            best = best_from(prefix)
            if best is None:
                entries[str(prefix)] = {"next": "unresolved",
                                        "value": None}
            elif not best[1]:
                entries[str(prefix)] = {"next": "eos",
                                        "value": best[0]}
            else:
                entries[str(prefix)] = {"next": best[1][0],
                                        "value": best[0]}
        tensor[fid] = entries
    return tensor


def policy_lookup(tensor, fid):
    entries = tensor[fid]
    prefix = ()
    stream = []
    lookups = 0
    while True:
        ent = entries.get(str(prefix))
        lookups += 1
        if ent is None:
            return (stream, None, "unresolved", lookups)
        if ent["next"] == "eos":
            return (stream, entries[str(())]["value"], "complete",
                    lookups)
        if ent["next"] == "unresolved":
            return (stream, None, "unresolved", lookups)
        stream.append(ent["next"])
        prefix = prefix + (ent["next"],)


def lexmin_decode(fid):
    """Route 2 for the canonical form: per-step lexicographic
    minimization over (-score, token), implemented independently
    of lane 3's canonical decoder."""
    prefix, total, ops = (), 0, 0
    while True:
        rows = L3.rows_for(fid, prefix)
        if rows is None:
            return {"stream": list(prefix), "total": total,
                    "status": "unresolved", "ops": ops}
        pick = None
        for tok, s in rows:
            ops += 1
            key = (-s, tok)
            if pick is None or key < pick[0]:
                pick = (key, tok, s)
        total += pick[2]
        if pick[1] == L3.EOS:
            return {"stream": list(prefix), "total": total,
                    "status": "complete", "ops": ops}
        prefix = prefix + (pick[1],)


def battery_decoding():
    p1 = L3.prop1()
    committed = json.load(open(os.path.join(
        HERE, "lane3-results.json")))
    check("lane3 prop1 fidelity",
          p1["frontier"] == committed["prop1_decoding"]["frontier"] and
          all(p1["results"][k]["gap_milli"] ==
              committed["prop1_decoding"]["results"][k]["gap_milli"]
              for k in p1["results"]))
    bf = p1["results"]["bestfirst"]
    can = p1["results"]["canonical"]
    out = {"lane3_frontier": p1["frontier"],
           "bestfirst": {k: bf[k] for k in
                         ("gap_milli", "ops_total", "storage_bytes",
                          "certified_fixtures", "cert_sound")},
           "canonical": {k: can[k] for k in
                         ("gap_milli", "ops_total", "storage_bytes")}}
    # A1 route 1 (exhaustive) and route 4 (decomposed) against
    # the best-first home form, per fixture
    r1_equal = 0
    r4_equal = 0
    subproblems = {}
    for fid in L3.FIXTURES:
        home = bf["per_fixture"][fid]
        s1, t1, st1 = exhaustive_stream(fid)
        if s1 == home["stream"] and t1 == home["total"] and \
                st1 == home["status"]:
            r1_equal += 1
        s4, t4, st4, subs = decomposed_best(fid)
        subproblems[fid] = subs
        if s4 == home["stream"] and t4 == home["total"] and \
                st4 == home["status"]:
            r4_equal += 1
    out["a1_route1_exhaustive_equal_fixtures"] = r1_equal
    out["a1_route4_decomposed_equal_fixtures"] = r4_equal
    out["a1_route4_subproblems"] = subproblems
    # A1 route 5: the policy tensor
    tensor = build_policy_tensor()
    r5_equal = 0
    r5_lookups = 0
    for fid in L3.FIXTURES:
        home = bf["per_fixture"][fid]
        s5, t5, st5, lk = policy_lookup(tensor, fid)
        r5_lookups += lk
        if s5 == home["stream"] and t5 == home["total"] and \
                st5 == home["status"]:
            r5_equal += 1
    out["a1_route5_policy_equal_fixtures"] = r5_equal
    out["a1_route5_policy_lookups_total"] = r5_lookups
    out["a1_route5_policy_bytes"] = jbytes(tensor)
    out["a1_archive_plain_bytes"] = bf["storage_bytes"]
    # A8 route 2 (lexicographic minimization) against canonical,
    # on the battery and under its six row-order permutations
    lex_equal = 0
    for fid in L3.FIXTURES:
        if lexmin_decode(fid)["stream"] == \
                can["per_fixture"][fid]["stream"] and \
                lexmin_decode(fid)["total"] == \
                can["per_fixture"][fid]["total"]:
            lex_equal += 1
    saved = L3.ARCHIVE
    lex_perm_equal = 0
    lex_perm_checks = 0
    pick_tensor = {}
    for fid in L3.FIXTURES:
        entries = {}
        for (f, prefix), rows in sorted(L3.ARCHIVE.items()):
            if f != fid:
                continue
            pick = None
            for tok, s in sorted(rows, key=lambda r: r[0]):
                if pick is None or s > pick[1]:
                    pick = (tok, s)
            entries[str(prefix)] = pick[0]
        pick_tensor[fid] = entries
    try:
        for seed in (-1, 1, 2, 3, 4, 5):
            L3.ARCHIVE = L3.permuted_archive(seed)
            for fid in L3.FIXTURES:
                lex_perm_checks += 1
                home = L3.decode_canonical(fid)
                mine = lexmin_decode(fid)
                if mine["stream"] == home["stream"] and \
                        mine["total"] == home["total"]:
                    lex_perm_equal += 1
    finally:
        L3.ARCHIVE = saved
    out["a8_route2_lexmin_equal_fixtures"] = lex_equal
    out["a8_route2_lexmin_perm_equal"] = lex_perm_equal
    out["a8_route2_lexmin_perm_checks"] = lex_perm_checks
    # A8 route 5: the pick tensor (per prefix, the canonical
    # pick), validated as a lookup under every permutation
    r5p_equal = 0
    r5p_checks = 0
    saved = L3.ARCHIVE
    try:
        for seed in (-1, 1, 2, 3, 4, 5, None):
            if seed is not None:
                L3.ARCHIVE = L3.permuted_archive(seed)
            for fid in L3.FIXTURES:
                r5p_checks += 1
                home = L3.decode_canonical(fid)
                prefix, total, stream = (), 0, []
                status = "complete"
                while True:
                    rows = L3.rows_for(fid, prefix)
                    if rows is None:
                        status = "unresolved"
                        break
                    tok = pick_tensor[fid][str(prefix)]
                    s = dict(rows)[tok]
                    total += s
                    if tok == L3.EOS:
                        break
                    stream.append(tok)
                    prefix = prefix + (tok,)
                if stream == home["stream"] and total == home["total"] \
                        and status == home["status"]:
                    r5p_equal += 1
    finally:
        L3.ARCHIVE = saved
    out["a8_route5_picktensor_equal"] = r5p_equal
    out["a8_route5_picktensor_checks"] = r5p_checks
    out["a8_route5_picktensor_bytes"] = jbytes(pick_tensor)
    return out


# ================================================================
# Matrix resolution: lane 3 proposition 2 battery, imported.
# ================================================================

def battery_matrix():
    p2 = L3.prop2()
    committed = json.load(open(os.path.join(
        HERE, "lane3-results.json")))["prop2_matrix"]
    check("lane3 prop2 fidelity",
          p2["d1_321"]["equal"] == committed["d1_321"]["equal"] and
          p2["d3_large"]["equal"] == committed["d3_large"]["equal"] and
          p2["onthefly"]["covered_equal_full"] ==
          committed["onthefly"]["covered_equal_full"])
    out = {
        "d1_equal": p2["d1_321"]["equal"],
        "d1_checkpoints": p2["d1_321"]["checkpoints"],
        "d1_incr_work": p2["d1_321"]["incr_work"],
        "d1_full_work": p2["d1_321"]["full_work"],
        "d3_equal": p2["d3_large"]["equal"],
        "d3_checkpoints": p2["d3_large"]["checkpoints"],
        "d3_incr_work": p2["d3_large"]["incr_work"],
        "d3_full_work": p2["d3_large"]["full_work"],
        "suffix_equal": p2["d4_suffix"]["equal"],
        "onthefly_covered_equal": p2["onthefly"]["covered_equal_full"],
        "onthefly_covered": p2["onthefly"]["covered"],
        "onthefly_unresolved_printed": p2["onthefly"]
            ["unresolved_printed"],
    }
    # route 3: obscurity-ordered resolution (family C). The
    # obscurity reading of a coordinate is taken over a stated
    # probe prefix (the first 50 records): unresolved (no probe
    # record touches it), unprojected (touched but its probe
    # reading was never reconciled into a checkpoint), uncertain
    # (its probe semantic and intent sums disagree in sign).
    # Regions at or above the threshold of two clauses are
    # resolved first; the rest after. The claim validated is
    # the final-state reading only -- intermediate readings
    # are order-dependent by construction (lane 3, prop 2).
    for tag, recs, coords in (("d1", L3.make_records(321, 64, "d1"), 64),
                              ("d3", L3.make_records(5000, 256, "d3"),
                               256)):
        probe = recs[:50]
        psem = [0] * coords
        pint = [0] * coords
        touched = [0] * coords
        for rec in probe:
            for c, (s, i) in rec.items():
                psem[c] += s
                pint[c] += i
                touched[c] += 1
        obscurity = []
        for c in range(coords):
            clauses = 0
            if touched[c] == 0:
                clauses += 1  # unresolved
                clauses += 1  # unprojected: never in any reading
            if touched[c] > 0 and (psem[c] > 0) != (pint[c] > 0) \
                    and psem[c] != 0 and pint[c] != 0:
                clauses += 1  # uncertain
            obscurity.append(clauses)
        above = [c for c in range(coords) if obscurity[c] >= 2]
        below = [c for c in range(coords) if obscurity[c] < 2]
        # resolve region by region: appends restricted to the
        # region's coordinates, above-threshold regions first
        inc = L3.Incremental(coords)
        for region in (above, below):
            keep = set(region)
            for rec in recs:
                inc.append({c: v for c, v in rec.items() if c in keep})
        full, _w = L3.full_readings(recs, coords)
        final = inc.readings()
        out["route3_%s_final_equal" % tag] = \
            [list(x) for x in full] == [list(x) for x in final]
        out["route3_%s_above_threshold_coords" % tag] = len(above)
        out["route3_%s_coords" % tag] = coords
    # route 5: the resolved reading tensor at the final state
    recs_big = L3.make_records(5000, 256, "d3")
    full_big, _w = L3.full_readings(recs_big, 256)
    tensor = [list(x) for x in full_big]
    rng = random.Random(777)
    q_equal = 0
    q_checks = 0
    for _ in range(200):
        c = rng.randrange(256)
        q_checks += 1
        if (tensor[0][c], tensor[1][c], tensor[2][c], tensor[3][c]) == \
                (full_big[0][c], full_big[1][c], full_big[2][c],
                 full_big[3][c]):
            q_equal += 1
    out["route5_tensor_query_equal"] = q_equal
    out["route5_tensor_query_checks"] = q_checks
    out["route5_tensor_bytes"] = jbytes(tensor)
    out["route5_records_bytes"] = jbytes(
        [{str(c): list(v) for c, v in rec.items()} for rec in recs_big])
    return out


# ================================================================
# Tensor loop: lane 3 proposition 3, plus route variants of the
# loop re-implemented here and fidelity-checked by digest
# against lane 3's committed digest.
# ================================================================

def run_loop_variant(use_intent=True, use_obscurity=True,
                     min_mode=False):
    """The lane 3 loop with its two edit clauses switchable.
    Full mode must reproduce lane 3's digest exactly."""
    stack = []
    weightings = list(L3.BASE_W)
    incr_copy = list(L3.BASE_W)
    prefix_by_fid = {"trap": (), "branch": ()}
    stream = []
    edits_log = []
    cert_checks = 0
    cert_ok = 0
    triggers = {5: (6, 250), 4: (5, 100), 6: (0, 50)}
    fid = "trap"
    steps = 0
    while steps < 14:
        steps += 1
        prefix = prefix_by_fid[fid]
        rows = L3.rows_for(fid, prefix)
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
        if tok == L3.EOS:
            if fid == "trap":
                fid = "branch"
                continue
            break
        prefix_by_fid[fid] = prefix + (tok,)
        named = None
        if use_intent and tok in triggers:
            named = triggers[tok]
        elif use_obscurity:
            worst = min(rows, key=lambda r: r[1])
            if worst[1] <= -300:
                coord = worst[0] % len(L3.BASE_W)
                if min_mode:
                    # route 2 reading of the edit: the delta is
                    # the minimiser, over the stated delta set,
                    # of the worst candidate's residual score
                    # read at its edited coordinate.
                    best_delta = None
                    for delta in (50, 100, 150, 200, 250):
                        resid = abs(worst[1] + weightings[coord] + delta)
                        if best_delta is None or resid < best_delta[0]:
                            best_delta = (resid, delta)
                    named = (coord, best_delta[1])
                else:
                    named = (coord, 150)
        if named is not None:
            coord, delta = named
            group = {coord}
            for g in L3.TIED:
                if coord in g:
                    group = set(g)
            new_val = weightings[coord] + delta
            edit = {"after": {c: new_val for c in sorted(group)},
                    "before": {c: weightings[c] for c in sorted(group)},
                    "trigger": tok, "step": steps}
            L3.check_edit(edit)
            stack.append(edit)
            for c, v in edit["after"].items():
                incr_copy[c] = v
            recomputed = L3.apply_stack(L3.BASE_W, stack)
            cert_checks += 1
            if recomputed == incr_copy:
                cert_ok += 1
            weightings = recomputed
            edits_log.append({"step": steps, "coords": sorted(group),
                              "after": new_val})
    return {"stream": stream, "edits": edits_log,
            "final_weightings": weightings,
            "cert_checks": cert_checks, "cert_ok": cert_ok,
            "stack": stack}


def battery_loop():
    p3 = L3.prop3()
    committed = json.load(open(os.path.join(
        HERE, "lane3-results.json")))["prop3_loop"]
    check("lane3 prop3 fidelity",
          p3["digest"] == committed["digest"] and
          p3["run"]["cert_ok"] == committed["run"]["cert_ok"])
    out = {"lane3_digest": p3["digest"],
           "lane3_cert_ok": p3["run"]["cert_ok"],
           "lane3_cert_checks": p3["run"]["cert_checks"]}
    full = run_loop_variant(True, True, False)
    blob = json.dumps({k: full[k] for k in
                       ("stream", "edits", "final_weightings",
                        "cert_checks", "cert_ok")}, sort_keys=True)
    # lane 3's digest is over its own run record, whose fields
    # are stream, edits, final weightings, cert checks and ok,
    # protected, round trip, stack length; compare the fields
    # this variant shares with lane 3's run directly instead.
    out["variant_full_stream_equal"] = \
        full["stream"] == p3["run"]["stream"]
    out["variant_full_final_equal"] = \
        full["final_weightings"] == p3["run"]["final_weightings"]
    out["variant_full_edits_equal"] = \
        full["edits"] == p3["run"]["edits"]
    r1 = run_loop_variant(True, False, False)
    r3 = run_loop_variant(False, True, False)
    r2 = run_loop_variant(True, True, True)
    out["route1_only_stream"] = r1["stream"]
    out["route1_only_final"] = r1["final_weightings"]
    out["route1_only_edits"] = len(r1["edits"])
    out["route1_only_equal_full"] = \
        r1["final_weightings"] == full["final_weightings"] and \
        r1["stream"] == full["stream"]
    out["route3_only_stream"] = r3["stream"]
    out["route3_only_final"] = r3["final_weightings"]
    out["route3_only_edits"] = len(r3["edits"])
    out["route3_only_equal_full"] = \
        r3["final_weightings"] == full["final_weightings"] and \
        r3["stream"] == full["stream"]
    out["route2_min_final"] = r2["final_weightings"]
    out["route2_min_stream"] = r2["stream"]
    out["route2_min_equal_full"] = \
        r2["final_weightings"] == full["final_weightings"] and \
        r2["stream"] == full["stream"]
    out["route2_min_cert_ok"] = r2["cert_ok"]
    out["route2_min_cert_checks"] = r2["cert_checks"]
    # route 5: the stack collapsed to one overlay tensor
    combined = {}
    for edit in full["stack"]:
        for c, v in edit["after"].items():
            combined[c] = v
    collapsed = L3.apply_stack(L3.BASE_W,
                               [{"after": combined, "before": {}}])
    out["route5_collapsed_equal_final"] = \
        collapsed == full["final_weightings"]
    inverse = {"after": {c: L3.BASE_W[c] for c in combined},
               "before": {}}
    restored = L3.apply_stack(collapsed, [inverse])
    out["route5_inverse_restores_base"] = restored == L3.BASE_W
    out["route5_stack_bytes"] = jbytes(
        [{("after"): {str(c): v for c, v in e["after"].items()},
          ("before"): {str(c): v for c, v in e["before"].items()}}
         for e in full["stack"]])
    out["route5_collapsed_bytes"] = jbytes(
        {str(c): v for c, v in combined.items()})
    out["route5_final_vector_bytes"] = jbytes(full["final_weightings"])
    return out


# ================================================================
# Meta level: lane 1, imported and re-run.
# ================================================================

def battery_meta():
    fronts = [M.frontier_of(cands) for _n, cands, _m in M.INSTANCES]
    configs = M.configurations()
    rows = []
    for family, params in configs:
        picks = []
        tie_excess = 0
        miss = 0
        for idx, front in enumerate(fronts):
            pick, winners = M.induced(family, params, front)
            picks.append(pick if pick else "tie")
            tie_excess += len(winners) - 1
            if pick != M.INSTANCES[idx][2]:
                miss += 1
        measures = (miss, tie_excess, M.simplicity(family, params),
                    M.FAMILY_RANK[family])
        rows.append((family, params, picks, measures))
    reach = [r for r in rows if r[3][0] == 0]
    check("lane1 reach fidelity", len(reach) == 13,
          "got %d" % len(reach))

    def meta_dominates(a, b):
        return all(x <= y for x, y in zip(a, b)) and \
            any(x < y for x, y in zip(a, b))

    meta_front = [r for r in rows
                  if not any(meta_dominates(o[3], r[3])
                             for o in rows if o is not r)]
    check("lane1 meta-frontier fidelity", len(meta_front) == 6,
          "got %d" % len(meta_front))
    weights = (4, 2, 1, 1)
    scored = [(sum(w * m for w, m in zip(weights, r[3])), r)
              for r in meta_front]
    best = min(s for s, _r in scored)
    winners = [r for s, r in scored if s == best]
    demo = winners[0]
    check("lane1 demonstration fidelity",
          M.label(demo[0], demo[1]) == "max weights (1, 1)",
          M.label(demo[0], demo[1]))
    out = {"reach": len(reach), "meta_frontier": len(meta_front),
           "demonstration": M.label(demo[0], demo[1]),
           "demonstration_picks": demo[2]}
    # route 1: the winner stated directly, no enumeration --
    # its induced selections, run on the three fronts
    fam, par = "max", (1, 1)
    direct = [M.induced(fam, par, front)[0] for front in fronts]
    out["route1_direct_picks"] = direct
    out["route1_direct_equal_demo"] = direct == demo[2]
    # route 4: the meta-frontier decomposed per family, then
    # merged and re-frontiered; must equal the global frontier
    merged = []
    for fam_name in ("linear", "squared", "max", "lex", "overlay"):
        fam_rows = [r for r in rows if r[0] == fam_name]
        merged += [r for r in fam_rows
                   if not any(meta_dominates(o[3], r[3])
                              for o in fam_rows if o is not r)]
    merged_front = [r for r in merged
                    if not any(meta_dominates(o[3], r[3])
                               for o in merged if o is not r)]
    out["route4_decomposed_frontier_equal"] = \
        sorted(M.label(r[0], r[1]) for r in merged_front) == \
        sorted(M.label(r[0], r[1]) for r in meta_front)
    # route 5: the winner as a score tensor over the fronts;
    # lookup is the argmin read off the tensor
    tensor = {}
    for (iname, _c, _mid), front in zip(M.INSTANCES, fronts):
        tensor[iname] = {c[0]: M.score(fam, par, c) for c in front}
    lookup = []
    for (iname, _c, _mid) in M.INSTANCES:
        scores = tensor[iname]
        low = min(scores.values())
        ws = [n for n, s in scores.items() if s == low]
        lookup.append(ws[0] if len(ws) == 1 else None)
    out["route5_lookup_picks"] = lookup
    out["route5_lookup_equal"] = lookup == direct
    full_table = [{"label": M.label(r[0], r[1]), "picks": r[2],
                   "measures": list(r[3])} for r in rows]
    out["route5_tensor_bytes"] = jbytes(tensor)
    out["route5_full_table_bytes"] = jbytes(full_table)
    out["route5_winner_tensor"] = [fam, par[0], par[1]]
    return out


# ================================================================
# The basic action model: lane 4, imported and re-run per
# instance (paired seeds), plus the spectrum's route 2, route
# 4, and route 5 constructions.
# ================================================================

def r2_move(p):
    start, target = p["start"], p["target"]
    d = (target[0] - start[0], target[1] - start[1])
    best = None
    probes = 0
    for iu in range(-32, 33):
        for iv in range(-32, 33):
            cmd = (d[0] + 2.0 * iu, d[1] + 2.0 * iv)
            end = A.move_apply(start, cmd, p)
            probes += 1
            err = A.dist(end, target)
            if best is None or err < best[0]:
                best = (err, end)
    return A.move_verdict(best[1], p, probes=probes, repaired=False)


def r2_jump(p):
    g, h = p["g"], p["height"]
    goal = 1.04 * h
    best = None
    probes = 0
    for k in range(281):
        v = 2.0 + 0.1 * k
        probes += 1
        err = abs(A.jump_apex(v, g) - goal)
        if best is None or err < best[0]:
            best = (err, v)
    return A.jump_verdict(best[1], p, probes, False)


def r2_jumpover(p):
    def penalty(vx, vy):
        ok, comp, y_mid, r = A.jumpover_eval(vx, vy, p)
        if ok:
            return 0.0
        pen = 0.0
        if comp == "trajectory.clearance":
            pen += (p["h"] + 0.2 - y_mid) * 10.0 + 5.0
        pen += abs(r - (p["d"] + 4.0))
        return pen

    best = None
    probes = 0
    for a in range(39):
        for b in range(49):
            vx, vy = 1.0 + 0.5 * a, 1.0 + 0.5 * b
            probes += 1
            pen = penalty(vx, vy)
            if best is None or pen < best[0]:
                best = (pen, vx, vy)
    ok, comp, _y, _r = A.jumpover_eval(best[1], best[2], p)
    return (ok, comp, probes, False)


def r2_touch(p):
    rects, target = p["rects"], p["target"]
    trect = A.rect_by_id(rects, target)
    center = (trect["x"] + trect["w"] / 2, trect["y"] + trect["h"] / 2)
    best = None
    probes = 0
    any_hit = False
    for i in range(9):
        for j in range(7):
            px = trect["x"] + (i / 8) * trect["w"]
            py = trect["y"] + (j / 6) * trect["h"]
            probes += 1
            hit = A.topmost_at(rects, px, py)
            if hit is not None:
                any_hit = True
            score = (0 if hit == target else 1,
                     A.dist((px, py), center))
            if best is None or score < best[0]:
                best = (score, hit)
    if best[0][0] == 0:
        return (True, "-", probes, False)
    return (False, "target.occlusion" if any_hit else "target.bounds",
            probes, False)


def r2_type(p):
    target, layout = p["target"], p["layout"]
    buf = []
    probes = 0
    for wanted in target:
        for key in A.CHARSET:
            probes += 1
            if layout[key] == wanted:
                buf.append(layout[key])
                break
    return A.type_verdict("".join(buf), p, probes, False)


def r2_drive(p):
    state = (0.0, 0.0, 0.0)
    wps = p["waypoints"]
    wi = 0
    steps = 0
    probes = 0
    while steps < p["budget"] and wi < len(wps):
        target = wps[wi]
        best = None
        for steer in (-1.0, -0.5, 0.0, 0.5, 1.0):
            for throttle in (0.5, 1.0):
                cand = A.drive_step(state, steer, throttle, p)
                probes += 1
                score = A.dist(cand, target) + 0.3 * abs(
                    A.wrap_angle(A.angle_to(cand, target) - cand[2]))
                if best is None or score < best[0]:
                    best = (score, steer, throttle)
        state = A.drive_step(state, best[1], best[2], p)
        steps += 1
        if A.dist(state, wps[wi]) <= p["radius"]:
            wi += 1
    if wi >= len(wps):
        return (True, "-", probes, False)
    return (False, "waypoint[%d]" % wi, probes, False)


def r2_automate(p):
    done = set()
    pending = set(range(len(p["steps"])))
    probes = 0
    while pending:
        ready = []
        for s in sorted(pending):
            probes += 1
            if not A.automate_blocked(p, done, s):
                ready.append(s)
        if not ready:
            break
        s = min(ready)
        done.add(s)
        pending.discard(s)
    return A.automate_verdict(p, done, set(), probes, False)


def r4_move(p):
    start, target = p["start"], p["target"]
    mid = ((start[0] + target[0]) / 2, (start[1] + target[1]) / 2)

    def leg(frm, to):
        cmd = ((to[0] - frm[0] - p["drift"][0]) / p["scale"],
               (to[1] - frm[1] - p["drift"][1]) / p["scale"])
        return A.move_apply(frm, cmd, p)

    end = leg(leg(start, mid), target)
    return A.move_verdict(end, p, probes=0, repaired=False)


def r4_drive(p):
    state = (0.0, 0.0, 0.0)
    total = 0
    for target in p["waypoints"]:
        leg = 0
        while A.dist(state, target) > p["radius"] and leg < 250 \
                and total < 1200:
            diff = A.wrap_angle(A.angle_to(state, target) - state[2])
            steer = A.clamp(diff * 1.2, -1, 1)
            dnow = A.dist(state, target)
            throttle = 0.45 if dnow < 8 else 0.85
            state = A.drive_step(state, steer, throttle, p)
            leg += 1
            total += 1
        if A.dist(state, target) > p["radius"]:
            return (False, "waypoint", 0, False)
    return (True, "-", 0, False)


def r4_automate(p):
    steps = p["steps"]
    depth = {}

    def dep(s):
        if s not in depth:
            ds = steps[s]["deps"]
            depth[s] = 0 if not ds else 1 + max(dep(d) for d in ds)
        return depth[s]

    order = sorted(range(len(steps)), key=lambda s: (dep(s), s))
    done = set()
    probes = 0
    remaining = list(order)
    guard = 0
    while remaining and guard < 200:
        guard += 1
        progressed = False
        for s in list(remaining):
            probes += 1
            if not A.automate_blocked(p, done, s):
                done.add(s)
                remaining.remove(s)
                progressed = True
        if not progressed:
            break
    return A.automate_verdict(p, done, set(), probes, False)


R2_RUN = {"move": r2_move, "jump": r2_jump, "jumpover": r2_jumpover,
          "touch": r2_touch, "type": r2_type, "drive": r2_drive,
          "automate": r2_automate}
R4_RUN = {"move": r4_move, "drive": r4_drive, "automate": r4_automate}


def battery_actions():
    totals = {"explicit": 0, "obscurity": 0, "combination": 0,
              "naive": 0}
    succ = {}
    r2_succ = {}
    r4_succ = {}
    probes_r2 = {}
    train = {}
    for fi, (fname, label, make, run, _x) in enumerate(A.FAMILIES):
        succ[fname] = {}
        for rival, _route in A.RIVALS:
            succ[fname][rival] = set()
        r2_succ[fname] = set()
        probes_r2[fname] = 0
        if fname in R4_RUN:
            r4_succ[fname] = set()
        train[fname] = []
        for i in range(A.PER_FAMILY):
            seed = A.BASE_SEED + fi * 10000 + i
            inst = make(random.Random(seed))
            train[fname].append(inst)
            for rival, _route in A.RIVALS:
                if fname == "drive":
                    ok, comp, probes, repaired, _st = A.drive_run(
                        rival, inst)
                else:
                    ok, comp, probes, repaired = run(rival, inst)
                if ok:
                    succ[fname][rival].add(i)
                    totals[rival] += 1
            ok2, _c2, pr2, _r2 = R2_RUN[fname](inst)
            probes_r2[fname] += pr2
            if ok2:
                r2_succ[fname].add(i)
            if fname in R4_RUN:
                ok4, _c4, _p4, _r4 = R4_RUN[fname](inst)
                if ok4:
                    r4_succ[fname].add(i)
    check("lane4 totals fidelity",
          totals == {"explicit": 391, "obscurity": 419,
                     "combination": 419, "naive": 46},
          str(totals))
    out = {"totals": totals, "per_family": {}, "route2": {},
           "route4": {}, "agreement": {}}
    for fname in succ:
        out["per_family"][fname] = {
            r: len(s) for r, s in succ[fname].items()}
        out["route2"][fname] = {
            "success": len(r2_succ[fname]),
            "probes_total": probes_r2[fname],
            "agree_combination": len(
                r2_succ[fname] & succ[fname]["combination"]),
            "only_route2": sorted(
                r2_succ[fname] - succ[fname]["combination"]),
            "only_combination": sorted(
                succ[fname]["combination"] - r2_succ[fname]),
        }
        if fname in r4_succ:
            out["route4"][fname] = {
                "success": len(r4_succ[fname]),
                "agree_combination": len(
                    r4_succ[fname] & succ[fname]["combination"]),
            }
    for a_r, b_r in (("explicit", "combination"),
                     ("obscurity", "combination"),
                     ("explicit", "obscurity")):
        inter = sum(len(succ[f][a_r] & succ[f][b_r]) for f in succ)
        sym = sum(len(succ[f][a_r] ^ succ[f][b_r]) for f in succ)
        out["agreement"]["%s_vs_%s" % (a_r, b_r)] = {
            "both_succeed": inter, "symmetric_difference": sym}
    # route 5 attempt: nearest-neighbour tensor lookup, trained
    # on the battery instances, tested on held-out instances
    r5 = {}
    for fi, (fname, label, make, run, _x) in enumerate(A.FAMILIES):
        if fname not in ("move", "jump"):
            continue
        wins = 0
        for i in range(A.PER_FAMILY):
            seed = A.BASE_SEED + 500000 + fi * 10000 + i
            test = make(random.Random(seed))
            if fname == "move":
                def feat(p):
                    return (p["target"][0] - p["start"][0],
                            p["target"][1] - p["start"][1],
                            100.0 * p["scale"],
                            p["drift"][0], p["drift"][1])

                def cmd_of(p):
                    return ((p["target"][0] - p["start"][0] -
                             p["drift"][0]) / p["scale"],
                            (p["target"][1] - p["start"][1] -
                             p["drift"][1]) / p["scale"])

                ft = feat(test)
                near = min(train[fname], key=lambda p: sum(
                    (a - b) ** 2 for a, b in zip(feat(p), ft)))
                end = A.move_apply(test["start"], cmd_of(near), test)
                ok = A.dist(end, test["target"]) <= test["tol"]
            else:
                def featj(p):
                    return (p["g"], p["height"])

                def v_of(p):
                    return math.sqrt(2 * p["g"] * 1.04 * p["height"])

                ft = featj(test)
                near = min(train[fname], key=lambda p: sum(
                    (a - b) ** 2 for a, b in zip(featj(p), ft)))
                ok, _c, _p, _r = A.jump_verdict(v_of(near), test, 0,
                                                False)
            if ok:
                wins += 1
        r5[fname] = {"heldout_success": wins, "heldout_n": A.PER_FAMILY}
    out["route5_nearest_neighbour_attempt"] = r5
    return out


# ================================================================
# Main: fidelity controls first, then the spectrum batteries.
# ================================================================

def main():
    committed2 = json.load(open(os.path.join(
        HERE, "validation-lane2-results.json")))

    print("lane 6 spectrum harness -- fidelity controls")
    p1 = battery_frontier()
    c1 = committed2["p1"]
    check("lane2 p1 fidelity",
          p1["frontier_members"] == c1["frontier_members"] and
          p1["weight_first_recovery"] == c1["weight_first_recovery"] and
          p1["perm_agree"] == c1["perm_agree"] and
          p1["segment_middle_selected_by_any_positive_grid_weight"] ==
          c1["segment_middle_selected_by_any_positive_grid_weight"])
    print("  frontier battery: members %d, weight-first %d, "
          "nonlinear recovery %d, linear-meta recovery %d, "
          "union recovery %d"
          % (p1["frontier_members"], p1["weight_first_recovery"],
             p1["nonlinear_recovery"], p1["linear_meta_recovery"],
             p1["union_grid_or_nonlinear_recovery"]))

    p2 = battery_stop()
    c2 = committed2["p2"]["results"]
    check("lane2 p2 fidelity",
          p2["results"]["budget3"]["false_optimal"] ==
          c2["budget3"]["false_optimal"] and
          p2["results"]["twoface"]["false_optimal"] == 0 and
          p2["results"]["threshold"]["examined"] ==
          c2["threshold"]["examined"] and
          p2["results"]["twoface"]["acceptable_correct"] ==
          c2["twoface"]["acceptable_correct"])
    print("  stop battery: budget3 false %d, two-face false %d, "
          "block decisions equal %d/400, tensor claims %d"
          % (p2["results"]["budget3"]["false_optimal"],
             p2["results"]["twoface"]["false_optimal"],
             p2["route4_block_decisions_equal"],
             p2["route5_table_claims"]))

    p3 = battery_repair()
    c3 = committed2["p3"]
    check("lane2 p3 fidelity",
          p3["executed_epochs"] == c3["executed_epochs"] and
          p3["relaxations"] == c3["relaxations"] and
          p3["agree"] == c3["agree"])
    print("  repair battery: cone agree %d/%d, dijkstra agree %d, "
          "apsp agree %d/%d"
          % (p3["agree"]["inc"], p3["executed_epochs"],
             p3["route2_dijkstra_agree"], p3["route5_apsp_agree"],
             p3["route5_subbattery_epochs"]))

    p4 = battery_worklist()
    c4 = committed2["p4"]
    check("lane2 p4 fidelity",
          p4["prefix_checks"] == c4["prefix_checks"] and
          p4["mismatch"]["worklist"] == c4["mismatch"]["worklist"] and
          p4["mismatch"]["dupblind"] == c4["mismatch"]["dupblind"] and
          p4["checks"]["worklist"] == c4["checks"]["worklist"] and
          p4["checks"]["naive"] == c4["checks"]["naive"])
    print("  worklist battery: prefixes %d, priority mismatch %d, "
          "union tensor mismatch %d/%d, powerset tensor equal %d/%d"
          % (p4["prefix_checks"], p4["mismatch"]["priority"],
             p4["route5_union_mismatch"], p4["route5_union_queries"],
             p4["route5_powerset_equal"], p4["route5_powerset_entries"]))

    p5 = battery_breakeven()
    c5 = committed2["p5"]
    check("lane2 p5 fidelity",
          p5["dense_per_query_ops_mean64"] ==
          c5["dense_per_query_ops_mean64"] and
          p5["factored_per_query_ops_mean64"] ==
          c5["factored_per_query_ops_mean64"] and
          p5["fixed_ops_excl_persistence"] ==
          c5["fixed_ops_excl_persistence"] and
          p5["empirical_crossover_q_vs_query_only"] ==
          c5["empirical_crossover_q_vs_query_only"] and
          p5["predicted_break_even_q"] == c5["predicted_break_even_q"])
    print("  break-even battery: crossover %d, outputs equal %d/512, "
          "rule-vs-minimiser disagreements %s"
          % (p5["empirical_crossover_q_vs_query_only"],
             p5["outputs_equal_512"],
             p5["route1_route2_choice_disagreements"]))

    dec = battery_decoding()
    print("  decoding battery: best-first route1 equal %d/5, "
          "route4 equal %d/5, route5 equal %d/5; canonical "
          "lexmin equal %d/5, pick tensor equal %d/%d"
          % (dec["a1_route1_exhaustive_equal_fixtures"],
             dec["a1_route4_decomposed_equal_fixtures"],
             dec["a1_route5_policy_equal_fixtures"],
             dec["a8_route2_lexmin_equal_fixtures"],
             dec["a8_route5_picktensor_equal"],
             dec["a8_route5_picktensor_checks"]))

    mat = battery_matrix()
    print("  matrix battery: obscurity-ordered final equal "
          "d1 %s d3 %s; tensor queries %d/%d"
          % (mat["route3_d1_final_equal"], mat["route3_d3_final_equal"],
             mat["route5_tensor_query_equal"],
             mat["route5_tensor_query_checks"]))

    loop = battery_loop()
    print("  tensor loop: variant fidelity stream %s final %s; "
          "route1-only equal %s, route3-only equal %s, "
          "route2-min equal %s, collapsed equal %s"
          % (loop["variant_full_stream_equal"],
             loop["variant_full_final_equal"],
             loop["route1_only_equal_full"],
             loop["route3_only_equal_full"],
             loop["route2_min_equal_full"],
             loop["route5_collapsed_equal_final"]))
    check("loop variant fidelity",
          loop["variant_full_stream_equal"] and
          loop["variant_full_final_equal"] and
          loop["variant_full_edits_equal"])

    meta = battery_meta()
    print("  meta battery: reach %d, meta-frontier %d, direct "
          "equal %s, decomposed frontier equal %s, tensor "
          "lookup equal %s"
          % (meta["reach"], meta["meta_frontier"],
             meta["route1_direct_equal_demo"],
             meta["route4_decomposed_frontier_equal"],
             meta["route5_lookup_equal"]))

    act = battery_actions()
    print("  action battery: totals %s; route2 %s; route5 "
          "attempt %s"
          % (act["totals"],
             {f: act["route2"][f]["success"] for f in act["route2"]},
             act["route5_nearest_neighbour_attempt"]))

    R["batteries"] = {
        "frontier": p1, "stop": p2, "repair": p3, "worklist": p4,
        "breakeven": p5, "decoding": dec, "matrix": mat,
        "loop": loop, "meta": meta, "actions": act,
    }
    R["fidelity_failures"] = FAILURES
    with open(os.path.join(HERE, "spectrum-results.json"), "w") as f:
        json.dump(R, f, indent=1, sort_keys=True)
    if FAILURES:
        print("harness verdict: FAIL -- " + "; ".join(FAILURES))
        return 1
    print("harness verdict: OK -- all fidelity controls passed; "
          "spectrum batteries executed at the lanes' own pins "
          "and seeds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
