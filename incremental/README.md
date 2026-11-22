# Incremental recomputation: the meta-search (meta.py)

meta.py's 39 weighting configurations over three instances, as carried state:
each instance frontier, each (configuration, instance) selection (minimum and
winners), each configuration's measure vector, and the meta frontier over
configurations. A configuration join scores it on each frontier and joins the
meta frontier at 2(n-1) meta evaluations. An instance candidate that leaves
the instance frontier unchanged carries every selection at 0 evaluations;
one that enters scores only against carried minima, and a selection is
rescored in full only when a member that left was one of its winners.

The checker is meta.py's own main(), unmodified, with its printed rows and
meta-frontier parsed back. Run: `python3 -B incremental/gate.py meta`.

Measured (counts): build by joins 1,482 meta evaluations, the same as one full
recompute (39 x 38), so building saves nothing; a 40th configuration 78 vs
1,560; a dominated decoding candidate 0 and 0; a frontier-entering (3, 8) 40
score and 156 meta evaluations, 2 configurations change measures; (5, 5),
which knocks 'balanced' off the frontier, rescores 12 selections in full.
Every step agrees with meta.py. The spec and the other two systems are in
clpi/software-redundant-compute-expands examples/incremental-recomputation.
