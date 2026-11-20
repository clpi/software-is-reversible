"""Finite witnessed trace reconstruction, after-effect refusal, and exact fiber bounds."""
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json


def digest(x):
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def bits(n):
    return (n-1).bit_length()


def trace(initial, fs):
    out = [initial]
    for f in fs:
        out.append(f(out[-1]))
    return tuple(out)


def partition(rows):
    out = defaultdict(list)
    for t in rows:
        out[t[-1]].append(t)
    return {last: sorted(set(paths)) for last, paths in out.items()}


def minwidth(fs, universe):
    rows = sorted({trace(x, fs) for x in universe})
    fibers = partition(rows)
    required = max(map(len, fibers.values()))
    # On this finite declared trace set, ranks are a minimal fixed-width
    # residual. Index size/build and replay work are separate costs.
    direct = {(t[-1], i): t for t0 in fibers.values() for i,t in enumerate(t0)}
    require(len(direct)==len(rows), "fiber encoding collision")
    for t in rows:
        require(direct[(t[-1], fibers[t[-1]].index(t))]==t, "wrong complete trace")
    # Adversarial construction: modulo any smaller alphabet necessarily
    # collides on this largest exhaustive fiber; check each smaller width.
    worst = max(fibers.values(), key=len)
    for b in range(bits(required)):
        candidate_labels = {i % (1<<b) for i in range(len(worst))}
        require(len(candidate_labels)<len(worst), "lower-bound control failed")
    rolling = 0
    for i in range(len(fs)):
        local_pairs = {t[i:i+2] for t in rows}
        local = defaultdict(set)
        for p,q in local_pairs:
            local[q].add(p)
        rolling += bits(max(map(len,local.values())))
    return {"traces_verified":len(rows),"fibers":len(fibers),
            "max_fiber":required,"trace_residual_bits":bits(required),
            "sum_of_per_step_fixed_width_bits":rolling,
            "rank_table_bound_entries":len(direct)}


@dataclass(frozen=True)
class Transition:
    scope: str
    pre: str
    post: str
    residual: int
    effects: tuple[str,...]


def undo_record(expected_scope, live_state, receipt, reversible_model):
    require(receipt.scope==expected_scope, "wrong scope")
    require(not receipt.effects, "external effect has no reversal contract")
    require(digest(live_state)==receipt.post, "stale post-state")
    prior = reversible_model(receipt.residual, live_state)
    require(digest(prior)==receipt.pre, "inverse did not restore verified observation")
    return prior


def run():
    cases = {
        "inj-xor-rotate": (range(64), (lambda x:x^15,lambda x:((x<<2)|(x>>4))&63)),
        "nibbles-projection": (range(64), (lambda x:x&15,lambda x:x&3)),
        # Paths restricted by predecessor observations; local maxima may be
        # incompatible. The whole trace can need fewer bits than any sum.
        "alternating-lost-axes": (range(64), (lambda x:0 if x<32 else x+1,lambda x:int(x!=0))),
        "flat-choice": (range(64), (lambda x:0,)),
        "correlated-structured-record": ([(i,i^(i>>1)) for i in range(16)],
                                         (lambda x:x[1],lambda x:x%2)),
    }
    result = {n:minwidth(fs,u) for n,(u,fs) in cases.items()}
    require(result["alternating-lost-axes"]["trace_residual_bits"]==5 and
            result["alternating-lost-axes"]["sum_of_per_step_fixed_width_bits"]==10,
            "strict global coding control")
    controls = 0
    for scope,start,end in product(("read","other"),range(16),range(16)):
        cert=Transition(scope,digest(start),digest(end),start,())
        back=undo_record(scope,end,cert,lambda residual,_:residual)
        require(back==start,"inverse round trip")
        for target,now,receipt in [
            (scope,end^1,cert),("wrong",end,cert),
            (scope,end,Transition(scope,cert.pre,cert.post,start^1,())),
            (scope,end,Transition(scope,cert.pre,cert.post,start,("external delivery",)))]:
            try:
                undo_record(target,now,receipt,lambda residual,_:residual)
            except ValueError:
                controls+=1
            else:
                raise ValueError("unsafe undo accepted")
    return {"schema":"software-is-reversible.fibers.v1","synthetic_only":True,
            "cases":result,"scoped_round_trips":512,"unsafe_reversals_refused":controls,
            "metrics":"residual widths for declared finite domains, not file sizes or latency"}


if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
