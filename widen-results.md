# Widening the configuration space — harness results

Harness: the widen file in this repo (Python, stdlib only)
Run command: python3 widen.py
Base pin: 12047b21f0af62f4dc3272199dec5184d14cfd3a (master, before this lane's append)
Exit code: 0. Output is deterministic (two consecutive runs byte-identical; the machine results file's hash is unchanged across runs).
Spec: the widen spec file in this repo, written in full before any new family's selection was executed. Every parameter grid in the spec is derived from the battery's stated coordinate range (integers 0 to 20) or from the family's own construction. The identities of the 28 were reconstructed before the families were defined (that is the task's order), and no grid was fit to them: the grids cover the whole stated axis range uniformly. The centered form is the one family whose parameter is a member by definition; it is counted apart throughout.

## Scope honesty

The battery is the lane 2 proposition 1 battery as the spectrum harness runs it: 300 point sets, seed 2000 series, coordinates integers 0 to 20, 695 frontier members. The 28 live on this battery, not on the meta level's three instances, where the old enumerated space already selects all 9 frontier members and the unselectable count is 0. The decoding fixture of the meta level enters only through the dominated control below; no result here is a claim about any decoder system.

## Exact run output

```
battery: members 695, grid 620, nonlinear 545, union 667, missing 28
family eps: total 695, of the 28: 28
family lex: total 543, of the 28: 22
family cheby: total 695, of the 28: 28
family pmax: total 695, of the 28: 28
family power: total 469, of the 28: 0
family rand: total 645, of the 28: 22
family center: total 695, of the 28: 28
union over old and new fixed families: 28 of 28; remaining 0
union with the centered form: 28 of 28; remaining 0
linear classes over 695: {'unique': 645, 'weak': 4, 'none': 46}
verdict: OK
```

## Per-family results

Totals are frontier members selected (unique minimiser) over the whole battery; the second count is how many of the 28 the family selects.

| family | configurations | of 695 | of the 28 |
|---|---|---|---|
| eps | 42 | 695 | 28 |
| lex | 2 | 543 | 22 |
| cheby | 441 | 695 | 28 |
| pmax | 1888 | 695 | 28 |
| power | 162 | 469 | 0 |
| rand | 4000 | 645 | 22 |
| center (counted apart) | per instance | 695 | 28 |

- The epsilon form, the achievement form, and weighted max with wide weights each select every frontier member of the battery. For the epsilon form this is the classical completeness of that method, executed here: the bound equal to a member's own coordinate makes that member the unique feasible minimiser on its frontier. For weighted max it matches the construction the harness verifies separately on all 695 members (weights formed from the member's own coordinates crossed, or an extreme ratio for a zero coordinate).
- The power sum family (exponents 3 and 4, weights 1 to 9) selects nothing new among the 28, and is reported as such. Its 469 total sits below the old squared family's reach on this battery's extremes: power sums favour balanced points, and the 28 are mostly extremes.
- The random linear family selects exactly the 645 members of the unique linear class (see below) and 22 of the 28. Its total equals the class count exactly: at 4000 samples the linear class is saturated on this battery, and the family's ceiling is the class, as the spec stated before the run.
- Lexicographic over the two permuted orders selects the same 22 of the 28 as the random linear family. Each of those 22 is an axis extreme of its frontier (least first axis or least second axis); lexicographic selection is exactly extreme selection, and the remaining 6 are interior or tied members no axis order reaches first.

## The 28, identified and classified

Instance is the battery trial index in generation order. The span is the exact interval of positive linear weight ratios (first weight over second weight) under which the member is a linear minimiser at all, computed in exact rational arithmetic; an empty span (lower bound above upper bound) is the certificate of the none class. Power classes are the same question for the power sum families over all positive weights.

| instance | member | frontier | linear | span | squared | cube | fourth | selected by (new) |
|---|---|---|---|---|---|---|---|---|
| 9 | (1, 13) | (0, 15), (1, 13), (4, 7), (14, 5) | weak | [2, 2] | unique | unique | unique | eps, cheby, pmax, center |
| 24 | (19, 1) | (0, 18), (2, 2), (19, 1) | unique | [0, 1/17] | unique | unique | unique | all seven |
| 56 | (1, 20) | (1, 20), (2, 2), (7, 1) | unique | [18, inf] | unique | unique | unique | all seven |
| 63 | (2, 11) | (2, 11), (3, 0) | unique | [11, inf] | unique | unique | unique | all seven |
| 83 | (15, 2) | (0, 10), (2, 7), (6, 3), (15, 2) | unique | [0, 1/9] | unique | unique | unique | all seven |
| 86 | (9, 1) | (0, 2), (9, 1) | unique | [0, 1/9] | unique | unique | unique | all seven |
| 90 | (2, 9) | (0, 15), (2, 9), (3, 4) | none | empty [5, 3] | unique | unique | unique | eps, cheby, pmax, center |
| 105 | (18, 3) | (1, 16), (3, 4), (18, 3) | unique | [0, 1/15] | unique | unique | unique | all seven |
| 115 | (2, 17) | (0, 18), (2, 17), (5, 6), (8, 0) | none | empty [11/3, 1/2] | none | unique | unique | eps, cheby, pmax, center |
| 127 | (0, 18) | (0, 18), (1, 8), (3, 0) | unique | [10, inf] | unique | unique | unique | all seven |
| 135 | (13, 2) | (2, 8), (4, 4), (13, 2), (16, 0) | none | empty [2/3, 2/9] | unique | unique | unique | eps, cheby, pmax, center |
| 136 | (3, 18) | (3, 18), (4, 2), (7, 0) | unique | [16, inf] | unique | unique | unique | all seven |
| 168 | (2, 19) | (2, 19), (3, 3), (16, 0) | unique | [18, inf] | unique | unique | unique | all seven |
| 171 | (4, 15) | (3, 17), (4, 15), (5, 2), (12, 1) | none | empty [13, 2] | none | none | unique | eps, cheby, pmax, center |
| 172 | (19, 1) | (1, 2), (19, 1) | unique | [0, 1/18] | unique | unique | unique | all seven |
| 178 | (0, 17) | (0, 17), (1, 5), (5, 1) | unique | [12, inf] | unique | unique | unique | all seven |
| 186 | (2, 17) | (2, 17), (3, 6), (5, 5), (20, 4) | unique | [11, inf] | unique | unique | unique | all seven |
| 186 | (20, 4) | (2, 17), (3, 6), (5, 5), (20, 4) | unique | [0, 1/15] | unique | unique | unique | all seven |
| 207 | (20, 0) | (1, 12), (6, 5), (9, 1), (20, 0) | unique | [0, 1/11] | unique | unique | unique | all seven |
| 216 | (4, 15) | (0, 17), (4, 15), (5, 1) | none | empty [14, 1/2] | none | none | none | eps, cheby, pmax, center |
| 234 | (0, 10) | (0, 10), (1, 0) | unique | [10, inf] | unique | unique | unique | all seven |
| 268 | (18, 0) | (2, 18), (6, 10), (7, 1), (18, 0) | unique | [0, 1/11] | unique | unique | unique | all seven |
| 271 | (3, 16) | (3, 16), (4, 1), (8, 0) | unique | [15, inf] | unique | unique | unique | all seven |
| 275 | (18, 0) | (0, 1), (18, 0) | unique | [0, 1/18] | unique | unique | unique | all seven |
| 276 | (19, 0) | (0, 1), (19, 0) | unique | [0, 1/19] | unique | unique | unique | all seven |
| 280 | (17, 3) | (2, 4), (17, 3) | unique | [0, 1/15] | unique | unique | unique | all seven |
| 281 | (20, 0) | (0, 1), (20, 0) | unique | [0, 1/20] | unique | unique | unique | all seven |
| 295 | (0, 19) | (0, 19), (1, 9), (14, 0) | unique | [10, inf] | unique | unique | unique | all seven |

Per-instance breakdown: the 28 sit on 27 of the 300 instances (instance 186 holds two; every other listed instance holds one). After the union of old and new fixed families, no instance holds an unselectable member.

## Why the 28 were unselectable — the geometry

Three distinct causes, separated by the exact classification (over the whole battery the linear classes are: unique 645, weak 4, none 46):

1. Ratio range (22 members). Each is the unique linear minimiser for an interval of ratios lying wholly outside the old grids: either wholly above 9 (the linear grid's greatest ratio, and above the nonlinear grids' 3) or wholly below 1/9. Two of them (instances 83 and 86) have span ending exactly at 1/9: the grid ratio 1/9 makes them tied minimisers only, and the grid's tie-break pick takes the smaller point instead. These members were never a geometry problem; the enumeration was too coarse and too narrow. Any of a wider grid, a random sample, a lexicographic order, or the complete families finds them.
2. The tied member (1 member). Instance 9's (1, 13) lies exactly on the segment between its neighbours (0, 15) and (4, 7): its span is the single ratio 2, at which all three are tied minimisers. No linear weighting makes it the unique minimiser, and the grid's tie-break never falls to it. It is selectable at once by any genuinely nonlinear family whose level sets bend (its squared, cube, and fourth classes are all unique), and the old nonlinear grids missed it only because their few weight pairs happen not to bend the right way at this point — the old squared family over all weights would have found it; its enumerated 1 to 3 grid did not.
3. The proved unreachable class (5 members). Instances 90, 115, 135, 171, and 216: each point lies strictly above the chord between its frontier neighbours, so every positive linear weighting prefers a neighbour; the span is empty. This is the Lean core's counterexample geometry at random scale, and no linear configuration of any resolution can select these members — verified in the run by the grid and the 4000-sample family selecting none of them (and none of the 46 none-class members anywhere on the battery). Within the class the power classes separate further: instances 90 and 135 are unique for every power sum from squared up; instance 115 needs the cube; instance 171 needs the fourth power; instance 216's (4, 15) is in the none class for the linear family and for the squared, cube, and fourth power sum families alike — it is selectable only by families whose form is not a weighted sum of monotone axis transforms at these exponents: the epsilon form, the achievement form, weighted max, and the centered form all select it.

## Remaining unselectable

None. The union of the old enumerated space and the new fixed families selects 28 of the 28 (and 695 of 695 over the battery); the count is the same with the centered form added. There is no remainder to carry as an open item on this battery. The strong statement the battery supports: no frontier member here is unselectable in the strong sense for the enlarged class — three structurally distinct fixed families (epsilon, achievement, wide weighted max) are each complete on it, while the linear family's incompleteness is exact and classified (46 none, 4 weak, of 695).

## Controls

- Fidelity: the harness reproduces the committed spectrum figures exactly before any new family runs (695 members; grid 620; nonlinear 545 with squared 413, weighted max 541, overlay 306; union 667; permutation agreement 900 of 900). Any difference would have failed the run.
- Dominated: no configuration, old or new, selects a dominated candidate. On the battery, every one of the 695 frontier members is verified undominated by every candidate of its instance, and every selection is drawn from the frontier by construction. On the meta level's decoding fixture, the two dominated continuations are selected by no new configuration (checked over every family's selections on all three meta instances).
- Linear agreement with the proved class: the linear grid selects no middle member of the two proved segment cases; the grid and the random linear family each select zero members of the none class over the whole battery; and on the meta level's three instances no positive linear weighting on the 1 to 9 grid selects any middle member (the meta harness's own control, re-run unchanged in this lane: its verdict is OK, with its three controls passing).
- Weighted max construction: the crossed-weights construction of the spec selects all 695 members under direct execution.
- Meta instances appendix: on the meta level's three instances, the middle members are selected by the epsilon, achievement, weighted max, power, and centered families (3 of 3 instances each) and by neither the lexicographic family nor the random linear family (0 of 3) — the latter two are the expected readings, since lexicographic selection is extreme selection and the random family is linear and the middles are in its proved unreachable class.

## What stands UNMEASURED, with owners

As stated in the spec: the widened space over any other battery (owner: lane 1 successor with the decoding line); a Lean form of any statement here (owner: lane 1); the balance overlay family over all positive constants, unclassified (owner: lane 1 successor). The classifications in this file are exact executed arithmetic over this finite battery, not theorems.
