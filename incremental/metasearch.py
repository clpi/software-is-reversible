#!/usr/bin/env python3
"""The reversible repo's meta-search (meta.py, 39 weighting configurations
over three instances, at 12047b2), as incremental recomputation.

Carried state:
  - per instance, a Frontier (frontier.py) over its candidates, two axes,
    lower is better;
  - per (configuration, instance), the induced selection: the minimum
    score on that instance's frontier and the winners at that minimum;
  - per configuration, its measure vector (miss, tie excess, simplicity,
    family rank) and its place in a Frontier over configurations.

Cones:
  - a configuration's selection on an instance depends on that
    instance's frontier members only;
  - a meta pair depends on the two configurations' measure vectors only.

Joins:
  - configuration join: score it on each frontier, measure it, join it
    to the meta frontier (2(n-1) meta evaluations);
  - instance candidate join: join it to the instance frontier; if the
    frontier set is unchanged and no member's own vector moved, every
    selection on that instance carries (0 score evaluations); otherwise
    new members are scored against the carried minimum, and a selection
    is rescored over the whole frontier only when a member that left was
    one of its winners; a configuration re-joins the meta frontier only
    if its measure vector changed. A candidate already present with a
    new vector is a withdrawal plus a join: on the frontier before, it
    counts as leaving; on it after, as entering.

The checker is meta.py's own main(), run unmodified on the same
instances, with its printed meta-frontier parsed back.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import re

from frontier import Frontier


def load_meta(path):
    spec = importlib.util.spec_from_file_location("rev_meta", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class MetaEngine:
    def __init__(self, meta, ignore_moved_mutant=False):
        self.m = meta
        self._mutant = ignore_moved_mutant  # MUTANT: a member's own score change is not seen
        self.instances = []      # (name, middle)
        self.inst_front = []     # Frontier per instance
        self.inst_vec = []       # name -> (x, y) per instance
        self.sel = {}            # (config, idx) -> (best score, winners list)
        self.measures = {}
        self.meta_front = Frontier((-1, -1, -1, -1))
        self.score_evals = 0
        self.configs = []

    def _score(self, family, params, idx, name):
        self.score_evals += 1
        x, y = self.inst_vec[idx][name]
        return self.m.score(family, params, (name, x, y))

    def add_instance(self, name, cands, middle):
        idx = len(self.instances)
        self.instances.append((name, middle))
        self.inst_front.append(Frontier((-1, -1)))
        self.inst_vec.append({})
        for c in cands:
            self.inst_vec[idx][c[0]] = (c[1], c[2])
            self.inst_front[idx].join(c[0], (c[1], c[2]))

    def _select_full(self, cfg, idx):
        fam, params = cfg
        scored = [(self._score(fam, params, idx, n), n)
                  for n in self.inst_front[idx].frontier()]
        best = min(s for s, _ in scored)
        self.sel[(cfg, idx)] = (best, sorted(n for s, n in scored if s == best))

    def _measure(self, cfg):
        fam, params = cfg
        miss = tie = 0
        for idx, (_n, middle) in enumerate(self.instances):
            _b, winners = self.sel[(cfg, idx)]
            tie += len(winners) - 1
            pick = winners[0] if len(winners) == 1 else None
            if pick != middle:
                miss += 1
        return (miss, tie, self.m.simplicity(fam, params), self.m.FAMILY_RANK[fam])

    def join_config(self, cfg):
        if cfg not in self.configs:
            self.configs.append(cfg)
        for idx in range(len(self.instances)):
            self._select_full(cfg, idx)
        self.measures[cfg] = self._measure(cfg)
        return self.meta_front.join(cfg, self.measures[cfg])

    def join_candidate(self, idx, name, x, y):
        """Returns (configs rescored over the full frontier, configs whose
        measures changed)."""
        old = set(self.inst_front[idx].frontier())
        prev = self.inst_vec[idx].get(name)
        moved = prev is not None and prev != (x, y) and not self._mutant
        self.inst_vec[idx][name] = (x, y)
        self.inst_front[idx].join(name, (x, y))
        new = set(self.inst_front[idx].frontier())
        # A changed vector is a withdrawal plus a join here too: the old
        # score leaves every selection that saw it, the new one enters.
        # Unchanged frontier membership does not carry a member whose
        # own score moved.
        if new == old and not (moved and name in old):
            return 0, 0
        entered, left = new - old, old - new
        if moved and name in old:
            left = left | {name}
        if moved and name in new:
            entered = entered | {name}
        full = changed = 0
        for cfg in self.configs:
            best, winners = self.sel[(cfg, idx)]
            if left & set(winners):
                self._select_full(cfg, idx)
                full += 1
            else:
                for n in sorted(entered):
                    s = self._score(cfg[0], cfg[1], idx, n)
                    if s < best:
                        best, winners = s, [n]
                    elif s == best:
                        winners = sorted(winners + [n])
                self.sel[(cfg, idx)] = (best, winners)
            mv = self._measure(cfg)
            if mv != self.measures[cfg]:
                self.measures[cfg] = mv
                self.meta_front.join(cfg, mv)  # named: withdrawal plus join
                changed += 1
        return full, changed

    def picks(self, cfg):
        out = []
        for idx in range(len(self.instances)):
            w = self.sel[(cfg, idx)][1]
            out.append(w[0] if len(w) == 1 else "tie " + "/".join(w))
        return out


def checker(meta, instances, configs):
    """meta.py's main(), unmodified, on the given instances and
    configurations; returns (meta-frontier labels, configuration rows)."""
    saved_i, saved_c = meta.INSTANCES, meta.configurations
    meta.INSTANCES = instances
    meta.configurations = lambda: list(configs)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = meta.main()
    finally:
        meta.INSTANCES, meta.configurations = saved_i, saved_c
    text = buf.getvalue()
    front = []
    on = False
    for line in text.splitlines():
        if line.startswith("meta-frontier"):
            on = True
            continue
        if on:
            if not line.strip():
                break
            front.append(re.match(r"  (.*) measures ", line).group(1))
    return sorted(front), rc, text
