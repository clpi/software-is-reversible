"""Exact-rational masked tensor edits and whitening/reweight observations.

Run without arguments to emit the receipt; --check only compares.
Edit roots name raw tensor identity. Packet observations with the residual
omitted are projections, not weight identity, and gain normalization is also
noninjective. Digests are checked bindings, not signatures or authorization.
All data are synthetic. No checkpoint or inference runtime is used.
"""
from dataclasses import asdict, dataclass, is_dataclass, replace
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from math import isqrt
from pathlib import Path
import argparse
import json

def check(assertion, message):
    if not assertion:
        raise ValueError(message)

def encode(value):
    def adapt(x):
        if isinstance(x, F):
            return [x.numerator, x.denominator]
        if is_dataclass(x):
            return asdict(x)
        raise TypeError(type(x))
    return (json.dumps(value, default=adapt, sort_keys=True, indent=2) + "\n").encode()

def digest(domain,value):
    return sha256(encode(["tensor-bridge/v1",domain,value])).hexdigest()

def tensor_root(w):
    return digest("tensor",w)

def plan_root(p):
    return digest("observation-plan",p)

def dot(a, b):
    return sum((x*y for x,y in zip(a,b,strict=True)), F(0))

def axis_roots(q):
    check(q > 0, "singular calibration")
    n, d = isqrt(q.numerator), isqrt(q.denominator)
    check(n*n == q.numerator and d*d == q.denominator, "nonrational calibration square root")
    return F(n,d)

@dataclass(frozen=True)
class Plan:
    mean: tuple
    lower: tuple
    mask: tuple
    gain: tuple

    def __post_init__(self):
        n = len(self.mean)
        check(n > 0 and len(self.lower) == len(self.gain) == len(self.mask) == n
              and all(len(row) == n for row in self.lower), "invalid plan dimensions")
        check(all(self.lower[i][i] > 0 and all(not self.lower[i][j] for j in range(i+1,n))
                  for i in range(n)), "invalid whitening basis")
        check(all(type(b) is bool for b in self.mask), "invalid observation mask")

    @property
    def enabled(self):
        return tuple(i for i,(keep,g) in enumerate(zip(self.mask,self.gain,strict=True))
                     if keep and g)

def covariance(rows):
    check(bool(rows) and bool(rows[0]), "empty calibration")
    n = len(rows[0])
    check(all(len(row) == n for row in rows), "calibration shape mismatch")
    m = tuple(sum((row[i] for row in rows), F(0))/len(rows) for i in range(n))
    cov = tuple(tuple(sum(((r[i]-m[i])*(r[j]-m[j]) for r in rows), F(0))/len(rows)
                      for j in range(n)) for i in range(n))
    return m,cov

def fit(rows, mask, gain):
    mean,cov = covariance(rows)
    n = len(mean)
    lower = [[F(0)]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            x = cov[i][j] - dot(lower[i][:j],lower[j][:j])
            lower[i][j] = axis_roots(x) if i == j else x/lower[j][j]
    return Plan(mean, tuple(map(tuple,lower)), tuple(mask), tuple(map(F,gain)))

def white(row, p):
    check(len(row) == len(p.mean), "tensor width mismatch")
    y = []
    for i,x in enumerate(row):
        y.append((x-p.mean[i]-dot(p.lower[i][:i],y))/p.lower[i][i])
    return tuple(y)

def unwhite(row,p):
    return tuple(m+dot(weights,row) for m,weights in zip(p.mean,p.lower,strict=True))

def calibrated(n, variant):
    # A known integer nonsingular triangular mix of the complete ±1 cube.
    lower = tuple(tuple(F(0 if j>i else 2+variant+i if j==i else (i+j+variant)%3-1)
                        for j in range(n)) for i in range(n))
    mean = tuple(F(3*i-variant,2) for i in range(n))
    return tuple(tuple(m+dot(weights,z) for m,weights in zip(mean,lower,strict=True))
                 for z in product((-1,1),repeat=n))

@dataclass(frozen=True)
class Packet:
    plan: str
    observation: tuple
    residual: tuple
    tensor: str

def observe(w,p):
    have = set(p.enabled)
    y = tuple(white(row,p) for row in w)
    show = tuple(tuple(v*p.gain[i] if i in have else None for i,v in enumerate(row))
                 for row in y)
    keep = tuple(tuple(None if i in have else v for i,v in enumerate(row)) for row in y)
    return Packet(plan_root(p),show,keep,tensor_root(w))

def restore(encoded,p):
    check(encoded.plan == plan_root(p), "stale parameter plan")
    check(len(encoded.observation) == len(encoded.residual), "bad row count")
    have = set(p.enabled)
    rows = []
    for show,keep in zip(encoded.observation,encoded.residual,strict=True):
        check(len(show) == len(keep) == len(p.mean), "bad packet width")
        y = []
        for i,(v,r) in enumerate(zip(show,keep,strict=True)):
            check((v is not None and r is None) if i in have else (v is None and r is not None),
                  "missing or overlapping residual")
            y.append(v/p.gain[i] if i in have else r)
        rows.append(unwhite(y,p))
    w = tuple(rows)
    check(tensor_root(w) == encoded.tensor, "reconstruction root mismatch")
    return w

def tilt(row,p,factors):
    # Independent finite mass experiment, not an inverse normalizer.
    y = white(row,p)
    factors = tuple(map(F,factors))
    check(len(factors) == len(y) and all(t >= 0 for t in factors), "invalid tilt")
    support = set(p.enabled)
    weights = tuple((1+v*v)*t if i in support else F(0)
                    for i,(v,t) in enumerate(zip(y,factors,strict=True)))
    denom = sum(weights)
    check(denom > 0, "tilt exhausted support")
    return tuple(w/denom for w in weights)

@dataclass(frozen=True)
class Edit:
    old: str
    new: str
    mask: tuple
    patches: tuple

def make_edit(w,mask,patches):
    mask = tuple(sorted(mask))
    patches = tuple(sorted(patches))
    check(len(mask) == len(set(mask)) and all(
          0 <= r < len(w) and 0 <= c < len(w[r]) for r,c in mask), "bad edit mask")
    check(bool(patches) and len({(r,c) for r,c,a in patches}) == len(patches), "bad patch keys")
    check(all((r,c) in mask and F(a) != w[r][c] for r,c,a in patches), "edit outside mask or no-op")
    out = [list(row) for row in w]
    before_after = []
    for r,c,a in patches:
        a = F(a)
        before_after.append((r,c,w[r][c],a))
        out[r][c] = a
    return Edit(tensor_root(w),tensor_root(tuple(map(tuple,out))),mask,tuple(before_after))

def replay(w,edit,reverse=False):
    start,end = (edit.new,edit.old) if reverse else (edit.old,edit.new)
    check(tensor_root(w) == start, "stale tensor root")
    check(bool(edit.patches) and len(edit.mask)==len(set(edit.mask)), "invalid edit schema")
    out = [list(row) for row in w]
    keys = set()
    for r,c,old,new in edit.patches:
        check((r,c) in edit.mask and (r,c) not in keys and
              0 <= r < len(w) and 0 <= c < len(w[r]), "invalid resolved edit")
        keys.add((r,c))
        a,b = (new,old) if reverse else (old,new)
        check(a != b and w[r][c] == a, "stale edit cell")
        out[r][c] = b
    w1 = tuple(map(tuple,out))
    check(tensor_root(w1) == end, "result tensor root mismatch")
    return w1

def expect_refusal(f,message):
    try:
        f()
    except ValueError as e:
        check(str(e) == message, "wrong refusal: "+str(e))
    else:
        raise ValueError("refusal did not happen: "+message)

def case(n,seed):
    # Immutable synthetic tensor, separate from calibration data.
    w = tuple(tuple(F(((r+1)*(j+3)+13*seed) % 19-7,8)
                    for j in range(n)) for r in range(4))
    p0 = fit(calibrated(n,0), [True]*(n-1)+[False], [1]*n)
    p1 = fit(calibrated(n,1), [True]*n, [1]+[2 if i%2 else -3 for i in range(1,n)])
    p2 = fit(calibrated(n,2), [True]*n, [0]+[F(1,3)]*(n-1))
    plans = (p0,p1,p2)
    for i,p in enumerate(plans):
        m,cov = covariance(tuple(white(row,p) for row in calibrated(n,i)))
        check(m == (F(0),)*n and cov == tuple(tuple(F(a==b) for b in range(n)) for a in range(n)),
              "whitening is not exact identity covariance")
    first = make_edit(w,((0,n-1),(1,n-1)), ((0,n-1,w[0][-1]+F(3,4)),(1,n-1,w[1][-1]-F(1,2))))
    w1 = replay(w,first)
    base,after = observe(w,p0),observe(w1,p0)
    check(base.observation == after.observation and base.residual != after.residual
          and base.tensor != after.tensor, "masked edit should be invisible only to coarse view")
    check(restore(base,p0) == w and restore(after,p0) == w1, "residual not sufficient")
    check(observe(w,p1).observation != observe(w1,p1).observation, "changed plan misses prior masked edit")
    expect_refusal(lambda: restore(after,p1),"stale parameter plan")
    expect_refusal(lambda: restore(replace(after,residual=base.residual),p0),"reconstruction root mismatch")
    blank = tuple(tuple(None for _ in row) for row in after.observation)
    expect_refusal(lambda: restore(replace(after,residual=blank),p0),"missing or overlapping residual")
    # Next edit is made after changing whitening, mask and gains. The edits
    # may overlap raw cells, and replay still treats their order as a premise.
    second = make_edit(w1,((0,n-1),(3,0)), ((0,n-1,w1[0][-1]+F(1,8)),(3,0,w1[3][0]-1)))
    w2 = replay(w1,second)
    mid = replay(w2,second,True)
    original = replay(mid,first,True)
    check(mid == w1 and original == w, "ordered reverse failed")
    check(all(restore(observe(wi,p),p) == wi for wi,p in product((w,w1,w2),plans)),
          "full packet roundtrip under parameter edit failed")
    check(observe(mid,p1) == observe(w1,p1) and observe(original,p0) == base
          and observe(original,p2) == observe(w,p2), "observations not restored at stated plan")
    expect_refusal(lambda:replay(w2,first,True),"stale tensor root")
    expect_refusal(lambda:replay(w1,first),"stale tensor root")
    expect_refusal(lambda:make_edit(w,((1,0),),((0,0,F(91)),)),"edit outside mask or no-op")
    expect_refusal(lambda:replay(w,replace(first,patches=())),"invalid edit schema")
    r,c,old,new = first.patches[0]
    expect_refusal(lambda:replay(w,replace(first,patches=((r,c,old+1,new),))),"stale edit cell")
    expect_refusal(lambda:replay(w,replace(first,patches=((r,c,old,new+1),))),"result tensor root mismatch")
    # Forward at exact old tensor root is independent of observation plans.
    check(replay(w,first) == w1 and replay(replay(w,first),second) == w2, "forward replay drift")
    unit = (1,)*n
    weighted = (2,)+(1,)*(n-1)
    prior = tilt(w[0],p1,unit)
    tilted = tilt(w[0],p1,weighted)
    check(prior != tilted and sum(tilted)==1, "reweight should change normalized row")
    check(tilt(w[0],p1,tuple(3*t for t in weighted)) == tilted, "global tilt scaling should collapse")
    check(tilt(w[0],p1,unit) == prior and tilt(w[0],p2,weighted)[0] == 0,
          "absolute reweight rollback / zero gain support")
    expect_refusal(lambda:tilt(w[0],p1,(0,)*n),"tilt exhausted support")
    check(tensor_root(w)==base.tensor, "original weights changed")
    return {"width":n,"seed":seed,"calibration_rows":2**n,"tensor_rows":len(w),
            "weights":tuple(map(tensor_root,(w,w1,w2))),"plans":tuple(map(plan_root,plans)),
            "edits":(first,second),"coarse_display_equal":True,"changed_plan_separates":True,
            "residual_differs":True,"ordered_inverse_exact":True,
            "tensor_view_roundtrips":9,"exact_whitening":3,"named_refusals":10,
            "coordinate_partition":[{"observed":list(p.enabled),
                "residual":[i for i in range(n) if i not in p.enabled]} for p in plans],
            "first_row_evidence":{"tensor_before":w[0],"tensor_after":w1[0],
                "coarse_display_before":base.observation[0],
                "coarse_display_after":after.observation[0],
                "residual_before":base.residual[0],"residual_after":after.residual[0],
                "changed_plan_before":observe(w,p1).observation[0],
                "changed_plan_after":observe(w1,p1).observation[0]},
            "normalized_observation": {"base":prior,"retuned":tilted,"joint_scale_equal":True,
                                        "old_policy_exact":True}}

def run():
    rows = tuple(case(n,s) for n,s in product((3,4,5),range(3)))
    expect_refusal(lambda:fit(((F(1),F(1)),)*4,(True,True),(1,1)),"singular calibration")
    expect_refusal(lambda:fit(((F(0),),(F(1),),(F(2),)),(True,),(1,)),
                   "nonrational calibration square root")
    return {"schema":"exact-offline-tensor-reversibility/v1","cases":rows,
            "model_inference_runs":0,"checkpoint_bytes_read":0,"checkpoint_bytes_written":0,
            "calibration_refusals":["singular calibration","nonrational calibration square root"],
            "summary":{"cases":len(rows),"exact_white_covariance_checks":3*len(rows),
                       "exact_tensor_view_roundtrips":9*len(rows),"named_refusals":10*len(rows)+2}}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true",help="compare generated bytes to receipt")
    args = parser.parse_args()
    result = run()
    content = encode(result)
    if args.check:
        target = Path(__file__).with_name("tensor-bridge.json")
        check(content == target.read_bytes(),"receipt differs byte-for-byte")
        print("PASS:",result["summary"])
    else:
        import sys
        sys.stdout.buffer.write(content)
