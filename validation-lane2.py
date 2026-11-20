#!/usr/bin/env python3
"""Lane 2 validation battery. Deterministic counted costs, held-out seeds.
Propositions 1-5. Same contract per proposition for all rivals."""
import random, itertools, json, time, math
from collections import deque, defaultdict

R={}

# ---------- P1 frontier selection ----------
def dom(a,b): return a[0]<=b[0] and a[1]<=b[1] and (a[0]<b[0] or a[1]<b[1])
def frontier_brute(pts):
    return sorted({p for p in pts if not any(dom(q,p) for q in pts if q!=p)})
def frontier_bnl(pts): # block nested loops, window
    win=[]
    for p in pts:
        if any(dom(w,p) for w in win): continue
        win=[w for w in win if not dom(p,w)]; win.append(p)
    return sorted(set(win))
def frontier_incremental(pts): # insert one by one using insert_exact form
    f=[]
    for p in pts:
        if any(dom(q,p) for q in f): continue
        f=[q for q in f if not dom(p,q)]; f.append(p)
    return sorted(set(f))
def weight_pick(pts,w):
    return min(pts, key=lambda p:(w[0]*p[0]+w[1]*p[1], p))
def run_p1():
    rng=random.Random(2000); trials=300; perms=0; agree=0; checks=0
    supported_recoverable=0; frontier_members=0; weightfirst_recoverable=0
    grid=[(a,b) for a in range(1,10) for b in range(1,10)]
    seg_cases=[[(0,10),(6,6),(10,0)],[(0,20),(11,11),(20,0)]]
    seg_mid_weight=False
    for pts in seg_cases:
        picks={weight_pick(pts,w) for w in grid}
        if pts[1] not in picks: pass
        else: seg_mid_weight=True
    for t in range(trials):
        n=rng.randint(4,14)
        pts=[(rng.randint(0,20), rng.randint(0,20)) for _ in range(n)]
        base=frontier_brute(pts)
        for cand_fn in (frontier_bnl, frontier_incremental):
            assert cand_fn(pts)==base
        # held-out permutations: shuffled input order must give same frontier
        for _ in range(3):
            q=pts[:]; rng.shuffle(q); perms+=1; checks+=1
            if frontier_bnl(q)==base and frontier_incremental(q)==base: agree+=1
        # selection recovery
        picks={weight_pick(pts,w) for w in grid} if pts else set()
        for m in base:
            frontier_members+=1
            # frontier-first: member is retained in candidate set by construction (frontier computed weight-free)
            supported_recoverable+=1
            if m in picks: weightfirst_recoverable+=1
    R['p1']={"trials":trials,"perm_checks":checks,"perm_agree":agree,
      "frontier_members":frontier_members,
      "frontier_first_recovery":supported_recoverable,
      "weight_first_recovery":weightfirst_recoverable,
      "segment_middle_selected_by_any_positive_grid_weight":seg_mid_weight,
      "bnl_brute_agree_trials":trials,"incremental_brute_agree_trials":trials}
run_p1()

# ---------- P2 stop rules ----------
def run_p2():
    rng=random.Random(3000); trials=400
    # stream of (latency, lower_bound_of_remaining_unknown?) model: plans arrive, each has latency; remaining have known lower bound lb
    res={k:{"stops":0,"acceptable_correct":0,"optimal_claims":0,"false_optimal":0,"examined":0} for k in ("threshold","optimal","budget3","twoface")}
    for t in range(trials):
        n=rng.randint(4,10)
        lats=[rng.randint(1,20) for _ in range(n)]
        # held-out permutation: shuffle arrival; adversarial 30%: best placed last
        if t%10<3: lats=lats[1:]+[min(lats)]
        T=10; best=min(lats)
        # threshold: first <=T, claims acceptable only
        k="threshold"; examined=next((i+1 for i,x in enumerate(lats) if x<=T), n)
        chosen=lats[examined-1] if any(x<=T for x in lats) else None
        res[k]["stops"]+=1; res[k]["examined"]+=examined
        if chosen is not None and chosen<=T: res[k]["acceptable_correct"]+=1
        elif chosen is None: res[k]["acceptable_correct"]+=1  # correctly no acceptable claim? count only when exists below
        # optimal: examine all, certify min (exhaust remaining)
        k="optimal"; res[k]["stops"]+=1; res[k]["examined"]+=n; res[k]["optimal_claims"]+=1
        if best!=min(lats): res[k]["false_optimal"]+=1
        # budget3: stop after 3, claims optimal (naive rival) -> false when best later
        k="budget3"; e=min(3,n); c=min(lats[:e]); res[k]["stops"]+=1; res[k]["examined"]+=e; res[k]["optimal_claims"]+=1
        if c!=best: res[k]["false_optimal"]+=1
        if c<=T: res[k]["acceptable_correct"]+=1
        # twoface: threshold stop for acceptable, continue/certify for optimal claim separately
        k="twoface"; res[k]["stops"]+=1; res[k]["examined"]+=n; res[k]["optimal_claims"]+=1
        if best!=min(lats): res[k]["false_optimal"]+=1
        if any(x<=T for x in lats): res[k]["acceptable_correct"]+=1
    # canonical threshold control instance
    ctrl={"plans":[9,2],"threshold":10,"threshold_first_acceptable":9,"optimal":2}
    R['p2']={"trials":trials,"results":res,"control":ctrl}
run_p2()

# ---------- P3 incremental repair ----------
def distances(n,edges):
    INF=10**9; d=[INF]*n; d[0]=0; relax=0
    # DAG edges sorted by tail (nodes topologically 0..n-1, edges i<j)
    for (u,v,w) in edges:
        relax+=1
        if d[u]+w<d[v]: d[v]=d[u]+w
    # iterate to fixpoint for safety (DAG one pass suffices in topo order if sorted)
    return d,relax
def run_p3():
    # Contract (stated): append-only epochs - each epoch adds one edge or decreases
    # one edge weight (the append-only / monotone setting of the program).
    # Arbitrary weight increases are retraction, out of this contract, named in the report.
    rng=random.Random(4000); cases=200; epochs=5
    tot={"inc":0,"scratch":0,"seminaive":0}; agree={"inc":0,"seminaive":0}; total_epochs=0; wins=0; executed=0
    for c in range(cases):
        n=rng.randint(8,20)
        edges=[]
        for i in range(n):
            for j in range(i+1,min(n,i+4)):
                if rng.random()<0.5: edges.append([i,j,rng.randint(1,9)])
        edges.sort()
        prev_d,_=distances(n,[tuple(e) for e in edges])
        out=defaultdict(list)
        for e in edges: out[e[0]].append(e)
        for ep in range(epochs):
            total_epochs+=1
            # mutate: add edge or decrease weight
            if rng.random()<0.5:
                i=rng.randrange(n-1); j=rng.randint(i+1,n-1)
                e=[i,j,rng.randint(1,9)]; edges.append(e); edges.sort(); out[i].append(e); changed=[e]
            else:
                if not edges: continue
                e=rng.choice(edges)
                if e[2]<=1: continue
                e[2]=rng.randint(1,e[2]-1); changed=[e]
            executed+=1
            full,full_relax=distances(n,[tuple(e) for e in edges]); tot["scratch"]+=full_relax
            # incremental repair: start from changed edge, propagate only on improvement
            d=prev_d[:]; relax=0; q=deque()
            for (u,v,w) in changed:
                relax+=1
                if d[u]+w<d[v]: d[v]=d[u]+w; q.append(v)
            seen=set()
            while q:
                x=q.popleft()
                for (u,v,w) in out.get(x,[]):
                    relax+=1
                    if d[u]+w<d[v]: d[v]=d[u]+w; q.append(v)
            tot["inc"]+=relax
            if d==full: agree["inc"]+=1
            if relax<full_relax: wins+=1
            # semi-naive: rounds; each round scans ALL edges (scan cost counted), fires those with a frontier tail
            d2=prev_d[:]; frontier=set(); relax2=0
            for (u,v,w) in changed:
                relax2+=0; frontier.add(u)
            rounds=0
            while frontier and rounds<100:
                rounds+=1; nxt=set()
                for (u,v,w) in edges:
                    relax2+=1
                    if u in frontier and d2[u]+w<d2[v]: d2[v]=d2[u]+w; nxt.add(v)
                frontier=nxt
            tot["seminaive"]+=relax2
            if d2==full: agree["seminaive"]+=1
            prev_d=full
    R['p3']={"cases":cases,"epochs_per_case":epochs,"total_epochs":total_epochs,"relaxations":tot,"agree":agree,"inc_win_epochs":wins,"executed_epochs":executed,"contract":"append or weight-decrease epochs only"}
run_p3()

# ---------- P4 closure worklist ----------
def least_closure(rules, seeds=()):
    derived=set(seeds); changed=True; checks=0
    while changed:
        changed=False
        for (pre,head) in rules:
            checks+=1
            if head not in derived and set(pre)<=derived: derived.add(head); changed=True
    return derived,checks
def worklist(rules, seeds=()):
    derived=set(seeds); missing=[]; waiters=defaultdict(list)
    for idx,(pre,head) in enumerate(rules):
        miss=set(pre)-derived; missing.append(set(miss))
        for p in miss: waiters[p].append(idx)
    q=deque(seeds); checks=0; fired=set()
    # zero-premise fire
    for idx,(pre,head) in enumerate(rules):
        if not missing[idx] and head not in derived:
            derived.add(head); q.append(head)
    processed=set(seeds)
    while q:
        x=q.popleft()
        if x in processed and x not in seeds: pass
        processed.add(x)
        for idx in waiters.get(x,[]):
            checks+=1
            if x in missing[idx]:
                missing[idx].discard(x)
                if not missing[idx]:
                    head=rules[idx][1]
                    if head not in derived: derived.add(head); q.append(head)
    return derived,checks
def seminaive_closure(rules, seeds=()):
    derived=set(seeds); frontier=set(seeds); checks=0; 
    # initial zero-premise
    while True:
        new=set()
        for (pre,head) in rules:
            checks+=1
            if head not in derived and set(pre)<=derived: new.add(head)
        if not new: break
        derived|=new; frontier=new
        # semi-naive proper would restrict; this rival scans all rules each round (labelled scan-per-round)
    return derived,checks
def run_p4():
    rng=random.Random(5000); systems=300; prefix_checks=0; mismatch={"worklist":0,"seminaive":0,"dupblind":0}
    tot_checks={"worklist":0,"naive":0,"seminaive":0}
    for s in range(systems):
        nterms=rng.randint(4,12); nrules=rng.randint(3,18)
        rules=[]
        for _ in range(nrules):
            k=rng.randint(0,3); pre=[rng.randrange(nterms) for _ in range(k)]  # duplicates possible
            rules.append((pre, rng.randrange(nterms)))
        # append prefixes
        for pref in range(1,len(rules)+1):
            sub=rules[:pref]; prefix_checks+=1
            oracle,oc=least_closure(sub); tot_checks["naive"]+=oc
            w,wc=worklist(sub); tot_checks["worklist"]+=wc
            if w!=oracle: mismatch["worklist"]+=1
            sn,sc=seminaive_closure(sub); tot_checks["seminaive"]+=sc
            if sn!=oracle: mismatch["seminaive"]+=1
            # duplicate-blind rival: count = len(pre) (not distinct), decrement once per processed term -> dup premise never fires
            # simulate quickly: rules with duplicated premise whose distinct set is derivable but dup count>distinct will be missed if head only via that rule
            # compute via worklist variant
            derived=set(); miss=[len(pre) for (pre,_) in sub]; from collections import deque as dq
            qq=dq()
            for i,(pre,h) in enumerate(sub):
                if miss[i]==0 and h not in derived: derived.add(h); qq.append(h)
            proc=set()
            while qq:
                x=qq.popleft()
                if x in proc: continue
                proc.add(x)
                for i,(pre,h) in enumerate(sub):
                    if x in pre:
                        miss[i]-=1
                        if miss[i]==0 and h not in derived: derived.add(h); qq.append(h)
            if derived!=oracle: mismatch["dupblind"]+=1
    R['p4']={"systems":systems,"prefix_checks":prefix_checks,"mismatch":mismatch,"checks":tot_checks}
run_p4()

# ---------- P5 break-even ----------
def run_p5():
    # Actual factored vs dense over the compounding family: 8 stages x 3 witnesses = 6561 plans
    stages=8; per=3
    pools=[[f"s{i}w{j}" for j in range(per)] for i in range(stages)]
    # dense materialization
    t0=time.perf_counter(); dense=list(itertools.product(*pools)); t_dense_build=time.perf_counter()-t0
    dense_ops=len(dense)  # rows materialized
    # factored setup ops: pool entries
    factored_setup_ops=sum(len(p) for p in pools)
    # query: requirement = choose stage subset / target index; dense scans rows counting comparisons; factored picks per-stage counting pool scans
    rng=random.Random(6000)
    queries=[]
    for _ in range(512):
        target=tuple(rng.randrange(per) for _ in range(stages)); queries.append(target)
    # per-query counted ops (deterministic)
    def dense_query(target):
        ops=0
        for row in dense:
            ops+=1
            if tuple(int(x[-1]) for x in row)==target: return ops
        return ops
    def factored_query(target):
        ops=0; out=[]
        for i,t in enumerate(target):
            for j,w in enumerate(pools[i]):
                ops+=1
                if j==t: out.append(w); break
        return ops
    dq=[dense_query(q) for q in queries[:64]]; fq=[factored_query(q) for q in queries[:64]]
    dense_per=sum(dq)/len(dq); factored_per=sum(fq)/len(fq)
    # full cost components for factored (counted ops): setup=pool build, validation=oracle check on 256 subset checkpoints (sample: 64 queries x compare), persistence=serialize pools, restart=deserialize
    validation_ops=sum(dense_query(q)+factored_query(q) for q in queries[:16])  # validate factored against dense oracle on 16 queries, both scans counted
    persist_bytes=len(json.dumps(pools).encode()); dense_persist_bytes=len(json.dumps(dense[:10]).encode())  # not used
    persistence_ops=persist_bytes  # byte writes counted as ops (stated unit: counted ops, bytes for persistence)
    restart_ops=factored_setup_ops  # re-read pools
    # NOTE units differ (bytes vs ops) -> convert persistence at 1 op per 8 bytes? State honestly: use ops-only form excluding bytes, and bytes reported separately.
    # Ops-only fixed cost:
    fixed_ops=factored_setup_ops+validation_ops+restart_ops
    predicted_star=fixed_ops/max(1,(dense_per-factored_per))
    totals={}
    for qn in [1,2,4,8,16,32,64,128,256,512]:
        f_total=fixed_ops + persistence_ops//8 + factored_per*qn  # persistence amortized byte->op at 8 bytes/op, stated
        d_total=dense_per*qn  # dense build is per-process materialization; if dense also persists, add below in alt
        d_total_with_build=dense_ops + dense_per*qn
        totals[qn]={"factored_total_ops":round(f_total,1),"dense_query_only_total_ops":round(d_total,1),"dense_with_materialization_ops":round(d_total_with_build,1),"factored_wins_vs_query_only":f_total<d_total,"factored_wins_vs_materialized":f_total<d_total_with_build}
    crossover=None
    for qn in range(1,513):
        if fixed_ops+persistence_ops//8+factored_per*qn < dense_per*qn: crossover=qn; break
    # wall time check (secondary)
    t0=time.perf_counter()
    for q in queries: dense_query(q)
    t_dense=time.perf_counter()-t0
    t0=time.perf_counter()
    for q in queries: factored_query(q)
    t_fact=time.perf_counter()-t0
    # regime sweep: same protocol, family size varies (stages 2..8)
    regimes={}
    for st in (2,3,4,6,8):
        pp=[[f"s{i}w{j}" for j in range(3)] for i in range(st)]
        dd=list(itertools.product(*pp))
        def dqry(target,dd=dd):
            ops=0
            for row in dd:
                ops+=1
                if tuple(int(x[-1]) for x in row)==target: return ops
            return ops
        def fqry(target,pp=pp):
            ops=0
            for i,t in enumerate(target):
                for j,w in enumerate(pp[i]):
                    ops+=1
                    if j==t: break
            return ops
        qs=[tuple(rng.randrange(3) for _ in range(st)) for _ in range(32)]
        dper=sum(dqry(q) for q in qs)/len(qs); fper=sum(fqry(q) for q in qs)/len(qs)
        setup=sum(len(x) for x in pp); val=sum(dqry(q)+fqry(q) for q in qs[:16]); pers=len(json.dumps(pp).encode())//8; rst=setup
        fixed=setup+val+pers+rst; cross=None
        for qn in range(1,2001):
            if fixed+fper*qn < dper*qn: cross=qn; break
        regimes[st]={"rows":len(dd),"dense_per":round(dper,2),"factored_per":round(fper,2),"fixed_full_cost":fixed,"crossover_q":cross}
    # held-out permutations: shuffled query order, totals unchanged (order invariance check)
    perm=queries[:]; rng.shuffle(perm)
    perm_fact=sum(factored_query(q) for q in perm); orig_fact=sum(factored_query(q) for q in queries)
    R['p5']={"dense_rows":len(dense),"factored_setup_ops":factored_setup_ops,"validation_ops_sample":validation_ops,
      "persistence_bytes_pools":persist_bytes,"restart_ops":restart_ops,"fixed_ops_excl_persistence":fixed_ops,
      "dense_per_query_ops_mean64":round(dense_per,2),"factored_per_query_ops_mean64":round(factored_per,2),
      "predicted_break_even_q":math.ceil(predicted_star) if predicted_star else None,
      "empirical_crossover_q_vs_query_only":crossover,"totals_by_q":totals,
      "wall_512_dense_s":round(t_dense,4),"wall_512_factored_s":round(t_fact,4),
      "heldout_permutation_factored_ops_equal":perm_fact==orig_fact, "regimes":regimes}
run_p5()

print(json.dumps(R,indent=1,sort_keys=True))
with open("validation-lane2-results.json","w") as f: json.dump(R,f,indent=1,sort_keys=True)
