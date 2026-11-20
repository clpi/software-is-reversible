/** Exact reference demo for a constructed finite tensor; no checkpoint or inference. */
const MAX_ROWS = 4096;
const MAX_HORIZON = 16;
const MAX_TERMINALS = 32768;
const Z = Object.freeze({n: 0n, d: 1n});
const O = Object.freeze({n: 1n, d: 1n});

function demand(ok, message) { if (!ok) throw new RangeError(message); }
function gcd(a, b) { while (b) [a, b] = [b, a % b]; return a; }
function rational(n, d = 1n) {
  demand(n >= 0n && d > 0n, "invalid nonnegative rational");
  if (!n) return Z;
  const g = gcd(n, d);
  return {n: n / g, d: d / g};
}
function nat(x) {
  return typeof x === "number" && Number.isSafeInteger(x) && x >= 0;
}
function readRational(x) {
  if (nat(x)) return rational(BigInt(x));
  demand(typeof x === "string" && /^(0|[1-9][0-9]{0,63})(\/([1-9][0-9]{0,63}))?$/.test(x),
         "expected an exact nonnegative rational string or safe integer");
  return fromCanonical(x);
}
function fromCanonical(x) {
  const [a, b = "1"] = x.split("/");
  return rational(BigInt(a), BigInt(b));
}
function add(a, b) { return rational(a.n*b.d+b.n*a.d, a.d*b.d); }
function mul(a, b) { return rational(a.n*b.n, a.d*b.d); }
function div(a, b) { return rational(a.n*b.d, a.d*b.n); }
function comparator(native) {
  demand(native===undefined||typeof native==="function","compareI32 must be callable");
  const counts={i32Hook:0,jsBigInt:0}, i32=2147483647n;
  function compare(a,b) {
    const x=a.n*b.d, y=b.n*a.d;
    const expected=x===y?0:x<y?-1:1;
    if(native!==undefined && x<=i32 && y<=i32) {
      const observed=native(Number(x),Number(y));
      demand(observed===expected, "native comparison disagrees with exact reference");
      counts.i32Hook++;
      return observed;
    }
    counts.jsBigInt++;
    return expected;
  }
  return {compare,counts};
}
function show(a) { return a.d === 1n ? String(a.n) : `${a.n}/${a.d}`; }
function lex(a, b, direction = 1) {
  for (let i=0; i<Math.min(a.length,b.length); i++) {
    if (a[i] !== b[i]) return direction*(a[i] < b[i] ? -1 : 1);
  }
  return direction*(a.length-b.length);
}
function key(p) { return p.join(","); }
function plain(x) { return x !== null && typeof x === "object" && !Array.isArray(x); }
function packed(x) { return Array.isArray(x)&&[...x.keys()].every(i=>Object.hasOwn(x,i)); }
function sortedRows(rows) { return rows.sort((a,b) => a.prefix.length-b.prefix.length || lex(a.prefix,b.prefix)); }

const generated = (() => {
  const h=4, rows=[{prefix:[],mass:[5,4,1]}, {prefix:[0],mass:[2,2,1]}, {prefix:[1],mass:[1,1,8]}];
  for (const r of [[0,0],[0,1],[1,0],[1,1]]) {
    rows.push({prefix:r,mass:[0,0,1]});
    for (const t of [0,1]) rows.push({prefix:[...r,t],mass:[0,0,1]});
  }
  return {vocabulary:[0,1,2], eos:[2], horizon:h, rows:sortedRows(rows)};
})();
for (const r of generated.rows) { Object.freeze(r.prefix); Object.freeze(r.mass); Object.freeze(r); }
Object.freeze(generated.rows); Object.freeze(generated.vocabulary); Object.freeze(generated.eos);
export const fixture = Object.freeze(generated);

function header(incoming, expected) {
  demand(plain(incoming) && packed(incoming.rows) && incoming.rows.length <= MAX_ROWS &&
         (incoming.encoding === undefined || incoming.encoding === expected), "invalid tensor carrier");
  const {vocabulary:v,eos,horizon:h} = incoming;
  demand(packed(v) && v.length>0 && v.length<=64 && v.every(nat) &&
         new Set(v).size===v.length, "invalid vocabulary");
  demand(packed(eos) && eos.length>0 && eos.every(t=>v.includes(t)) &&
         new Set(eos).size===eos.length, "invalid terminal tokens");
  demand(nat(h) && h>0 && h<=MAX_HORIZON, "invalid tensor horizon");
  return {vocabulary:[...v], eos:[...eos].sort((a,b)=>a-b), horizon:h};
}
function canonical(incoming, sparse = false) {
  const out = header(incoming, sparse ? "sparse" : "dense");
  const v = out.vocabulary, rows = new Map(), terminal = new Set(out.eos);
  for (const r of incoming.rows) {
    demand(plain(r)&&packed(r.prefix)&&r.prefix.length<out.horizon &&
           r.prefix.every(t=>v.includes(t)&&!terminal.has(t)), "invalid row prefix");
    const p = key(r.prefix);
    demand(!rows.has(p), "duplicate row prefix");
    let m;
    if (sparse) {
      demand(packed(r.nonzero), "sparse row omitted nonzero entries");
      m = v.map(()=>Z);
      const seen = new Set();
      for (const entry of r.nonzero) {
        demand(packed(entry)&&entry.length===2&&v.includes(entry[0])&&!seen.has(entry[0]),
               "invalid or duplicate sparse coordinate");
        seen.add(entry[0]);
        const val=readRational(entry[1]);
        demand(val.n>0n, "zero entered in sparse support");
        m[v.indexOf(entry[0])]=val;
      }
    } else {
      demand(packed(r.mass)&&r.mass.length===v.length, "mass row has wrong width");
      m=r.mass.map(readRational);
    }
    demand(m.some(x=>x.n), "empty conditional support");
    rows.set(p,{prefix:[...r.prefix],mass:m});
  }
  demand(rows.has(""), "root row missing");
  for (const {prefix,mass} of rows.values()) {
    if (prefix.length+1 >= out.horizon) continue;
    for (let j=0; j<v.length; j++) {
      if (mass[j].n && !terminal.has(v[j])) {
        demand(rows.has(key([...prefix,v[j]])), "missing reachable conditional row");
      }
    }
  }
  return {...out,rows:sortedRows([...rows.values()])};
}
function jsonDense(x) {
  return {...x, rows:x.rows.map(r=>({prefix:r.prefix,mass:r.mass.map(show)}))};
}
export function compactTensor(full) {
  const x=canonical(full);
  return {encoding:"sparse",...x,rows:x.rows.map(({prefix,mass})=>({
    prefix, nonzero:mass.flatMap((m,i)=>m.n ? [[x.vocabulary[i],show(m)]] : [])
  }))};
}
export function expandTensor(compact) { return jsonDense(canonical(compact,true)); }

function normalized(x,reweight) {
  demand(plain(reweight),"reweight must map prefixes to exact factors");
  const names=new Set(x.rows.map(r=>key(r.prefix)));
  for (const p of Object.keys(reweight)) demand(names.has(p), "reweight references unknown prefix");
  const out=new Map();
  for (const {prefix,mass} of x.rows) {
    const p=key(prefix);
    const changed=Object.hasOwn(reweight,p);
    const factors=changed ? reweight[p] : null;
    demand(!changed||packed(factors)&&factors.length===mass.length,
           "reweight needs one factor per token");
    const tilted=!changed?mass:mass.map((m,i)=>mul(m,readRational(factors[i])));
    const total=tilted.reduce(add,Z);
    demand(total.n>0n,"reweight exhausts row support");
    const row=tilted.flatMap((m,i)=>m.n ? [{token:x.vocabulary[i],p:div(m,total)}] : []);
    out.set(p,row);
  }
  return out;
}
function greedy(rows,eos,h,dir,cmp) {
  const tokens=[];
  let mass=O;
  while(tokens.length<h) {
    const best=[...rows.get(key(tokens))].sort((a,b)=>cmp(b.p,a.p)||lex([a.token],[b.token],dir))[0];
    tokens.push(best.token);
    mass=mul(mass,best.p);
    if(eos.has(best.token)) return {tokens,probability:show(mass),valid:true};
  }
  return {tokens,probability:show(mass),valid:false};
}
function solve(rows,eos,h,dir,budget,cmp) {
  const queue=[{tokens:[],mass:O}], winners=[], discarded=[];
  let upper=null, best=null, visited=0, stopReason="exhausted";
  const visits=[];
  while(queue.length) {
    queue.sort((a,b)=>cmp(b.mass,a.mass)||lex(a.tokens,b.tokens,dir));
    upper=queue[0].mass;
    if(best!==null && cmp(upper,best)<0) { stopReason="strict-prefix-bound"; break; }
    if(visited>=budget) { stopReason="budget"; break; }
    const node=queue.shift();
    visited++;
    visits.push({prefix:node.tokens,upper:show(node.mass)});
    for (const {token,p} of rows.get(key(node.tokens))) {
      const tokens=[...node.tokens,token], mass=mul(node.mass,p);
      if(eos.has(token)) {
        const d=best===null ? 1 : cmp(mass,best);
        if(d>0) { best=mass; winners.length=0; }
        if(d>=0) winners.push(tokens);
      } else if(tokens.length<h) queue.push({tokens,mass});
      else discarded.push(tokens);
    }
  }
  winners.sort((a,b)=>lex(a,b,dir));
  return {tokens:winners[0]??null,probability:best===null?null:show(best),certified:stopReason!=="budget",
          exactTies:stopReason==="budget"?null:winners,expanded:visited,visits,stopReason,
          remainingUpper:queue.length?show(upper):null,remainingPrefixes:queue.length,
          horizonRefusals:discarded.length};
}
function compatible(rows,eos,h,depth,tokens,dir) {
  if (tokens===null) return [];
  const shown=tokens.slice(0,depth), found=[];
  function go(p) {
    for(const {token} of rows.get(key(p))) {
      const next=[...p,token];
      if(lex(next.slice(0,Math.min(shown.length,next.length)),shown.slice(0,next.length))) continue;
      if(eos.has(token)) {
        if(lex(next.slice(0,depth),shown)===0) found.push(next);
      } else if(next.length<h) go(next);
      demand(found.length <= MAX_TERMINALS,"projection fiber exceeds demo limit");
    }
  }
  go([]);
  return found.sort((a,b)=>lex(a,b,dir));
}
function observation(rows) {
  return [...rows].map(([prefix,terms])=>({prefix:prefix===""?[]:prefix.split(",").map(Number),
    p:terms.map(({token,p})=>[token,show(p)])}));
}
function verdict(map,threshold,requireUnique,cmp) {
  if(!map.certified) return {status:"unqualified",reason:"search incomplete"};
  if(map.tokens===null) return {status:"unqualified",reason:"no terminal sequence"};
  if(cmp(fromCanonical(map.probability),threshold)<0) return {status:"unqualified",reason:"below exact threshold"};
  if(requireUnique&&map.exactTies.length!==1) return {status:"unqualified",reason:"unique MAP required"};
  return {status:"qualified",reason:"certified finite MAP meets the configured gate"};
}
/** Fixed inputs and all parameter changes use clean exact composition. */
export function analyzeInference(options={}) {
  const {tensor=fixture,horizon=tensor.horizon,reweight={},threshold="1/2",
         tie="ascending",resolution=1,budget=MAX_ROWS,requireUnique=false,compareI32} = options;
  const {compare:cmp,counts}=comparator(compareI32);
  const full=canonical(tensor,tensor.encoding==="sparse"), dense=jsonDense(full);
  const compact=compactTensor(dense), expanded=expandTensor(compact);
  demand(nat(horizon)&&horizon>0&&horizon<=full.horizon,"invalid active horizon");
  demand(nat(resolution)&&resolution<=horizon,"invalid projection resolution");
  demand(nat(budget)&&budget<=MAX_ROWS,"invalid expansion budget");
  demand(tie==="ascending"||tie==="descending","invalid tie direction");
  demand(typeof requireUnique==="boolean","requireUnique must be boolean");
  const limit=readRational(threshold);
  demand(cmp(limit,O)<=0,"threshold exceeds one");
  const active=normalized(full,reweight);
  const expandedRows=normalized(canonical(expanded),reweight);
  const dir=tie==="ascending"?1:-1, eos=new Set(full.eos);
  const map=solve(active,eos,horizon,dir,budget,cmp);
  const compressed=solve(expandedRows,eos,horizon,dir,budget,cmp);
  const compatibilityFiber=compatible(active,eos,horizon,resolution,map.tokens,dir);
  const naive=greedy(active,eos,horizon,dir,cmp);
  const authority=verdict(map,limit,requireUnique,cmp);
  return {kind:"constructed-finite-demo", fullEqualsCompact:JSON.stringify(dense)===JSON.stringify(expanded)
               && JSON.stringify(map)===JSON.stringify(compressed),
    map,greedy:naive,greedyAgrees:map.certified&&map.tokens!==null&&naive.valid&&lex(map.tokens,naive.tokens)===0,
    obscurity:{resolution,visiblePrefix:map.tokens?.slice(0,resolution)??null,
      uniqueWinner:map.exactTies===null?null:map.exactTies.length===1,exactTies:map.exactTies,
      compatibilityFiber,compatibilityCount:compatibilityFiber.length},
    qualification:{...authority,threshold:show(limit),requireUnique,externalEffectAuthorized:false},
    stages:{tensor:{denseCells:full.rows.length*full.vocabulary.length,
                    explicitNonzero:compact.rows.reduce((n,r)=>n+r.nonzero.length,0),
                    denseBytes:JSON.stringify(dense).length,sparseBytes:JSON.stringify(compact).length},
            reweight:{overriddenPrefixes:Object.keys(reweight).sort(),rows:observation(active)},
            resolution:{horizon,resolution,tie,budget},
            stop:{reason:map.stopReason,remainingUpper:map.remainingUpper},
            comparisonCounts:counts}};
}
