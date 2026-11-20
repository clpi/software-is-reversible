#!/usr/bin/env python3
"""Exact offline reversible-schedule experiment on deterministic finite traces."""
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from itertools import product
import json


@dataclass(frozen=True)
class Op:
    kind: str
    arg: int
    forward: int
    backward: int


@dataclass(frozen=True)
class Case:
    name: str
    bits: int
    initial: int
    ops: tuple[Op, ...]
    read: int
    snapshot_write: int
    receipt_write: int

    @property
    def mask(self):
        return (1 << self.bits) - 1


ACTIONS = (0, 1, 2, 3)
# Choice bits: 1 means replay instead of local inverse; 2 stores a snapshot.
AXES = ("extra_stored_bits", "extra_forward_cost", "sum_reverse_cost", "peak_reverse_cost")


def check(ok, why):
    if not ok:
        raise ValueError(why)


def forward(c, op, val):
    if op.kind == "add":
        return (val+op.arg)&c.mask
    if op.kind == "xor":
        return (val^op.arg)&c.mask
    if op.kind == "rot":
        return ((val<<op.arg)|(val>>(c.bits-op.arg)))&c.mask
    if op.kind == "keep":
        return val&((1<<op.arg)-1)
    if op.kind == "shift":
        return val>>op.arg
    if op.kind == "zero":
        return 0
    raise ValueError("unknown op")


def lost_bits(c, op):
    if op.kind == "keep":
        return c.bits-op.arg
    if op.kind == "shift":
        return op.arg
    if op.kind == "zero":
        return c.bits
    return 0


def log(c, op, val):
    n=lost_bits(c,op)
    if op.kind=="keep":
        return val>>op.arg
    return val&((1<<n)-1)


def invert(c, op, val, residual):
    n=lost_bits(c,op)
    check(type(residual) is int and 0<=residual<(1<<n), "out-of-width receipt")
    if op.kind=="add":
        old=(val-op.arg)&c.mask
    elif op.kind=="xor":
        old=(val^op.arg)&c.mask
    elif op.kind=="rot":
        old=((val>>op.arg)|(val<<(c.bits-op.arg)))&c.mask
    elif op.kind=="keep":
        old=(residual<<op.arg)|val
    elif op.kind=="shift":
        old=(val<<op.arg)|residual
    elif op.kind=="zero":
        old=residual
    else:
        raise ValueError("unknown op")
    check(0<=old<=c.mask and forward(c,op,old)==val, "inverse inconsistent")
    return old


def track(c):
    states=[c.initial]
    for op in c.ops:
        states.append(forward(c,op,states[-1]))
    return states


def check_reverse(c,plan):
    """Real inverse execution step by step; independently compare whole path."""
    states=track(c)
    cp={0:states[0]}
    undo={}
    for i,(op,choice) in enumerate(zip(c.ops,plan,strict=True)):
        if choice&2:
            cp[i]=states[i]
        if not choice&1:
            undo[i]=log(c,op,states[i])
    current=states[-1]
    for i in reversed(range(len(c.ops))):
        if i in undo:
            old=invert(c,c.ops[i],current,undo[i])
        else:
            start=max(p for p in cp if p<=i)
            old=cp[start]
            for op in c.ops[start:i]:
                old=forward(c,op,old)
        check(forward(c,c.ops[i],old)==current and old==states[i],
              f"recovered wrong state at step {i}")
        current=old
    check(current==c.initial,"initial state mismatch")
    return len(c.ops)


def step(c,i,prev,choice,prefix):
    cp=i if choice&2 and i else prev
    storage=overhead=0
    if cp!=prev:
        storage=c.bits+2   # model-relative fixed per-record tag
        overhead=c.snapshot_write
    if choice&1:
        reverse=c.read+prefix[i]-prefix[cp]
    else:
        n=lost_bits(c,c.ops[i])
        storage+=n+1 if n else 0  # nonzero residuals use one metadata bit
        overhead+=c.receipt_write if n else 0
        reverse=c.ops[i].backward
    return cp,(storage,overhead,reverse,reverse)


def join(a,b):
    return (a[0]+b[0],a[1]+b[1],a[2]+b[2],max(a[3],b[3]))


def oracle_cost(c,plan):
    """Independent direct formulation; no calls into step, join, or DP."""
    saved_positions=[0]+[i for i,v in enumerate(plan) if i and v in (2,3)]
    retained_indices=[i for i,v in enumerate(plan) if v in (0,2)]
    residuals=[lost_bits(c,c.ops[i]) for i in retained_indices]
    storage=(len(saved_positions)-1)*(c.bits+2)+sum(n+1 for n in residuals if n)
    overhead=(len(saved_positions)-1)*c.snapshot_write+sum(
        c.receipt_write for n in residuals if n)
    costs=[]
    for i, op in enumerate(c.ops):
        if i in retained_indices:
            costs.append(op.backward)
        else:
            start=max(p for p in saved_positions if p<=i)
            costs.append(c.read+sum(t.forward for t in c.ops[start:i]))
    return storage,overhead,sum(costs),max(costs)


def weakly_no_worse(a,b):
    return all(x<=y for x,y in zip(a,b))


def oracle(c):
    costs=defaultdict(list)
    for rest in product(ACTIONS,repeat=len(c.ops)-1):
        for first in (0,1):  # already hold start snapshot
            p=(first,)+rest
            costs[oracle_cost(c,p)].append(p)
    selected=[]
    # A dominating vector must lexically precede the dominated vector.
    for v in sorted(costs):
        if not any(weakly_no_worse(w,v) for w,p in selected):
            selected.append((v,min(costs[v])))
    return tuple(selected),sum(map(len,costs.values())),len(costs)


def nondominated(labels, partial=False):
    labels=sorted(set(labels))
    kept=[]
    for v,p in labels:
        if any(weakly_no_worse(w,v) and
                (not partial or q<=p or any(a<b for a,b in zip(w[:3],v[:3])))
                for w,q in kept):
            # Canonical ties: a strict advantage in the maximum alone can
            # disappear when a suffix incurs a larger maximum. Keep the
            # alternative prefix if it is lexically smaller.
            continue
        kept.append((v,p))
    return tuple(kept)


class Planner:
    # In-memory append-only frontier. Reuse requires identical prefix scope.
    def __init__(self, c):
        self.c = replace(c,ops=())
        self.prefix = [0]
        self.states = {0:(((0,0,0,0),()),)}
        self.extensions = 0

    def advance(self, c):
        n=len(self.c.ops)
        check(replace(c,ops=c.ops[:n])==self.c,"resumed trace prefix or scope changed")
        for i in range(n,len(c.ops)):
            op = c.ops[i]
            self.prefix.append(self.prefix[-1]+op.forward)
            candidates=defaultdict(list)
            for previous,labels in self.states.items():
                for v,p in labels:
                    for choice in (0,1) if i==0 else ACTIONS:
                        cp,cost=step(c,i,previous,choice,self.prefix)
                        candidates[cp].append((join(v,cost),p+(choice,)))
                        self.extensions+=1
            self.states={cp:nondominated(xs,partial=True) for cp,xs in candidates.items()}
        self.c = c
        return nondominated(pair for labels in self.states.values() for pair in labels)


def dp(c):
    engine = Planner(c)
    result = engine.advance(c)
    return result,engine.extensions


def fixture_cases():
    # Definition-level archetypes, not runtime or CPU benchmark claims.
    mix=(
        ("rot-add-alu",8, 173, ("rot","add","xor","add","rot","xor"),4,4,2),
        ("narrow-pipeline",10,657, ("add","keep","shift","xor","keep","rot"),3,5,2),
        ("reset-controller",12,3301,("xor","zero","add","zero","add","rot"),9,4,1),
        ("slow-replay-fast-undo",9,455,("add","keep","xor","shift","add","zero"),5,2,1),
        ("cheap-replay-expensive-undo",11,1201,("add","keep","xor","shift","add","zero"),1,7,3),
        ("mixed-bandwidth",7,111,("shift","keep","add","rot","zero","xor"),3,1,5),
    )
    for name,bits,initial,opnames,read,snapshot,receipt in mix:
        for variant in (0,1):
            ops=[]
            for j,kind in enumerate(opnames):
                n = (j*11+7+variant*9) % ((1<<bits)-1) if kind in ("add","xor") else (
                    0 if kind=="zero" else 1+(j*7+2+variant*5)%(bits-1))
                f,b=1+(j*5+variant) % 8,1+(j*3+variant*2)%7
                if "slow-replay" in name:
                    f,b=f*4,b
                if "cheap-replay" in name:
                    f,b=f,b*4
                ops.append(Op(kind,n,f,b))
            yield Case(f"{name}/{variant}",bits,initial^variant,tuple(ops),read,snapshot,receipt)


def controls(cases):
    increments=0
    for c in cases:
        for op in c.ops:
            values=defaultdict(int)
            for x in range(1<<c.bits):
                y=forward(c,op,x)
                check(invert(c,op,y,log(c,op,x))==x,"exhaustive inverse failed")
                values[y]+=1
                increments+=1
            check(max(values.values()) == 1 << lost_bits(c,op),"local receipt lower bound mismatch")
    # A historical strict peak lead vanishes after appending a common
    # larger peak; a tie-aware DP cannot discard the lexical winner.
    a=(2,3,10,4)
    b=(2,3,10,5)
    suffix=(0,0,7,7)
    check(a<b and join(a,suffix)==join(b,suffix),"peak erasure fixture drift")
    labels=nondominated([(a,(1,)),(b,(0,))],partial=True)
    check(len(labels)==2,"canonical tie lost")
    try:
        c=cases[1]
        invert(c,Op("zero",0,1,1),0,1<<c.bits)
    except ValueError:
        corrupt_refused=True
    else:
        corrupt_refused=False
    check(corrupt_refused,"corrupt residual accepted")
    planner=Planner(c)
    planner.advance(replace(c,ops=c.ops[:2]))
    changed=replace(c,ops=(replace(c.ops[0],forward=c.ops[0].forward+1),)+c.ops[1:])
    before=(planner.c,list(planner.prefix),dict(planner.states),planner.extensions)
    try:
        planner.advance(changed)
    except ValueError:
        check(before==(planner.c,planner.prefix,planner.states,planner.extensions),
              "failed scope check mutated the planner")
    else:
        raise ValueError("changed old trace admitted to append-only solver")
    return {"non_append_scope_change_refused":True,"exhaustive_local_input_inverse_checks":increments,
            "peak_tie_erasure":True,"out_of_width_receipt_refused":True}


def main():
    cases=list(fixture_cases())
    metrics=Counter()
    results=[]
    for c in cases:
        exact,enumerated,distinct=oracle(c)
        candidate,extensions=dp(c)
        check(exact==candidate, "frontier differs from exhaustive oracle")
        engine=Planner(c)
        reexpansions=0
        for l in range(1,len(c.ops)+1):
            prefix=replace(c,ops=c.ops[:l])
            warm=engine.advance(prefix)
            cold,cost=dp(prefix)
            check(warm==cold==oracle(prefix)[0],"append-only prefix comparison disagrees")
            reexpansions+=cost
            metrics["independent_prefix_frontier_matches"]+=1
        check(engine.extensions==extensions,"append-only planner did duplicated work")
        metrics["resident_append_extensions"]+=engine.extensions
        metrics["cold_prefix_extensions"]+=reexpansions
        for v,p in exact:
            metrics["independently_reversed_frontier_steps"]+=check_reverse(c,p)
        n=len(c.ops)
        methods={"local_inverse":(0,)*n, "replay_from_root":(1,)*n,
                 "snapshot_every_step":(1,)+(3,)*(n-1),
                 "periodic_snapshot":tuple(3 if i and i%3==0 else 1 for i in range(n))}
        observations={}
        for kind,p in methods.items():
            v=oracle_cost(c,p)
            check_reverse(c,p)
            dominating=[w for w,q in exact if w!=v and weakly_no_worse(w,v)]
            observations[kind]={"cost":v,"dominated":bool(dominating),
                                "one_dominator":dominating[0] if dominating else None}
            metrics[kind+"_dominated"]+=int(bool(dominating))
        metrics.update({"cases":1,"exhaustive_plans":enumerated,"dp_extensions":extensions,
                        "pareto_points":len(exact),"cases_with_multiple_pareto_points":int(len(exact)>1)})
        # Zero-storage lower bound follows trivially from nonnegative
        # storage; root-only is a witness. The coordinatewise minima
        # are exact within the exhaustive, declared plan family.
        mins=tuple(map(min,zip(*(v for v,p in exact))))
        check(mins[0]==0,"missing constructive zero-cost storage witness")
        joint_min=any(v==mins for v,p in exact)
        metrics["coordinate_minima_not_jointly_attained"]+=int(not joint_min)
        results.append({"case":c.name,"word_bits":c.bits,"initial":c.initial,
                        "cost_model":{"read":c.read,"snapshot_write":c.snapshot_write,
                                      "receipt_write":c.receipt_write},
                        "ops":[vars(op) for op in c.ops],
                        "enumerated":enumerated,"different_objective_vectors":distinct,
                        "dp_extensions":extensions,"coordinate_minima":mins,
                        "minima_jointly_attained":joint_min,"strategy_results":observations,
                        "pareto":[{"cost":v,"choices":p} for v,p in exact]})
    print(json.dumps({"axes":AXES,"model":"synthetic conditional costs; no host data",
                      "scope":"known deterministic trace; fixed start/final values and plan metadata excluded",
                      "totals":dict(metrics),"controls":controls(cases),"cases":results},
                     indent=2,sort_keys=True))


if __name__=="__main__":
    main()
