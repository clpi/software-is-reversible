import assert from "node:assert/strict";
import {fixture, compactTensor, expandTensor, analyzeInference as run} from "./inference.mjs";

function eq(a,b) { assert.deepEqual(a,b); }
const base=run(), compact=compactTensor(fixture);
eq(base.map.tokens,[1,2]); eq(base.map.probability,"8/25"); eq(base.map.expanded,3);
eq(base.greedy.tokens,[0,0,2]); eq(base.greedy.probability,"1/5"); eq(base.greedyAgrees,false);
eq(base.map.stopReason,"strict-prefix-bound"); eq(base.map.remainingUpper,"1/5");
eq(base.qualification.status,"unqualified");
eq(run({threshold:"8/25"}).qualification.status,"qualified");
eq(run({threshold:"81/250"}).qualification.status,"unqualified");
eq(run({resolution:0}).obscurity.compatibilityCount,7);
eq(base.obscurity.compatibilityCount,3);
eq(run({resolution:2}).obscurity.compatibilityCount,1);
eq(run({tensor:compact}).map,base.map);
eq(expandTensor(compact).rows.map(x=>x.mass.map(Number)),fixture.rows.map(x=>x.mass));
eq(base.fullEqualsCompact,true);
eq(base.stages.tensor,{denseCells:45,explicitNonzero:21,denseBytes:632,sparseBytes:685});
for (const budget of [0,1,2]) {
  const limited=run({budget,threshold:0});
  eq(limited.map.certified,false);
  eq(limited.map.exactTies,null);
  eq(limited.qualification,{status:"unqualified",reason:"search incomplete",threshold:"0",
    requireUnique:false,externalEffectAuthorized:false});
}
eq(run({budget:3}).map,base.map); // Certificate is present exactly at the budget boundary.
const tie={horizon:2,reweight:{"":[1,"5/16",0]}, threshold:"4/25"};
const asc=run(tie), desc=run({...tie,tie:"descending"});
eq(asc.map.exactTies,[[0,2],[1,2]]); eq(desc.map.exactTies,[[1,2],[0,2]]);
eq(asc.map.probability,"4/25"); eq(asc.map.tokens,[0,2]); eq(desc.map.tokens,[1,2]);
eq(asc.obscurity.uniqueWinner,false); eq(asc.qualification.status,"qualified");
eq(run({...tie,requireUnique:true}).qualification.reason,"unique MAP required");
// Equality of prefix upper bound must not prune an exact tie.
const equalBound={vocabulary:[0,1],eos:[1],horizon:2,
  rows:[{prefix:[],mass:[1,1]},{prefix:[0],mass:[0,1]}]};
eq(run({tensor:equalBound}).map.exactTies,[[0,1],[1]]);
eq(run({tensor:equalBound,budget:1}).map.certified,false);
const imm={reweight:{"":[1,0,0]}};
eq(run(imm).map.tokens,[0,0,2]); eq(run(imm).map.probability,"2/5"); eq(run().map,base.map);
eq(run({reweight:{"":[7,7,7]}}).stages.reweight.rows,base.stages.reweight.rows);
eq(run({horizon:1}).map.tokens,[2]); eq(run({horizon:1}).map.probability,"1/10");
const noTerminal={vocabulary:[0,1],eos:[1],horizon:1,rows:[{prefix:[],mass:[1,0]}]};
eq(run({tensor:noTerminal,threshold:0}).qualification.reason,"no terminal sequence");
eq(run({tensor:noTerminal}).map.certified,true);
eq(run({tensor:noTerminal}).greedy.valid,false);
const huge="9".repeat(64);
const large={vocabulary:[0,1],eos:[1],horizon:2,
  rows:[{prefix:[],mass:[huge,0]},{prefix:[0],mass:[huge,1]}]};
eq(run({tensor:large,reweight:{"0":[huge,1]},threshold:0}).qualification.status,"qualified");
assert.match(run({tensor:large,reweight:{"0":[huge,1]}}).map.probability,/^1\/[0-9]{127,129}$/);
assert.throws(()=>run({reweight:{"":[0,0,0]}}),/exhausts row support/);
assert.throws(()=>run({reweight:{"":null}}),/one factor per token/);
assert.throws(()=>run({reweight:{"not in tensor":[1,1,1]}}),/unknown prefix/);
assert.throws(()=>run({reweight:{"":["0.1",1,1]}}),/exact nonnegative rational/);
assert.throws(()=>run({threshold:"2/1"}),/threshold exceeds one/);
assert.throws(()=>run({resolution:9}),/invalid projection resolution/);
assert.throws(()=>run({tie:"random"}),/invalid tie direction/);
assert.throws(()=>run({tensor:{...fixture,rows:fixture.rows.filter(r=>r.prefix.join()!=="0")}}),
  /missing reachable conditional row/);
assert.throws(()=>expandTensor({...compact,rows:[...compact.rows,compact.rows[0]]}),/duplicate row prefix/);
const hole=new Array(3); hole[0]=5; hole[2]=1;
assert.throws(()=>run({tensor:{...fixture,rows:[{...fixture.rows[0],mass:hole},...fixture.rows.slice(1)]}}),
  /mass row has wrong width/);

// Independent exhaustive oracle (small integer conditional matrices).
function brute(shape,h,descending) {
  const table=new Map(shape.rows.map(r=>[r.prefix.join(),r.mass]));
  const candidates=[];
  function visit(p,n,d) {
    const row=table.get(p.join());
    const total=BigInt(row.reduce((a,b)=>a+b,0));
    row.forEach((x,i)=>{
      if(!x)return;
      const t=shape.vocabulary[i], q=[...p,t];
      if(shape.eos.includes(t)) candidates.push({q,n:n*BigInt(x),d:d*total});
      else if(q.length<h) visit(q,n*BigInt(x),d*total);
    });
  }
  visit([],1n,1n);
  function ord(a,b) {
    let i=0;
    while(i<a.q.length&&i<b.q.length&&a.q[i]===b.q[i])i++;
    return (descending?-1:1)*(i===a.q.length||i===b.q.length?a.q.length-b.q.length:a.q[i]-b.q[i]);
  }
  function c(a,b) { const x=a.n*b.d-b.n*a.d; return x===0n?0:x>0n?-1:1; }
  candidates.sort((a,b)=>c(a,b)||ord(a,b));
  const a=candidates[0];
  return {best:a,ties:a ? candidates.filter(x=>c(x,a)===0).map(x=>x.q):[]};
}
let checks=0;
for(let seed=0;seed<25;seed++) for (const h of [1,2,3,4]) for (const tie of ["ascending","descending"]) {
  const rows=fixture.rows.map(({prefix},i)=>{
    const mass=fixture.vocabulary.map((_,j)=>(seed*7+i*13+j*11+(seed+2)*(j+7)*(i+1))%9);
    return {prefix,mass:mass.some(Boolean)?mass:[0,0,1]};
  });
  const tensor={...fixture,rows};
  const p = [[],[0],[1]][seed%3];
  const row = rows.find(r=>r.prefix.join()===p.join());
  const factors=[seed%4,(seed+1)%4,(seed+2)%4];
  if (!row.mass.some((m,i)=>m*factors[i])) factors.fill(1);
  for (const reweight of [{}, {[p.join()]:factors}]) {
  const got=run({tensor,horizon:h,tie,reweight}).map;
  const possiblyTilted={...tensor,rows:rows.map(r=>
    Object.hasOwn(reweight,r.prefix.join()) ? {...r,mass:r.mass.map((m,i)=>m*factors[i])} : r)};
  const expected=brute(possiblyTilted,h,tie==="descending");
  eq(got.certified,true);
  eq(got.exactTies,expected.ties);
  eq(got.tokens,expected.best?.q??null);
  if(expected.best) {
    const [n,d="1"]=got.probability.split("/");
    eq(BigInt(n)*expected.best.d,BigInt(d)*expected.best.n);
  }
  checks++;
  }
}
// Optional native comparator observes only i32 values and is checked against
// the BigInt oracle for each call. Runtime remains a reference solver.
const compareI32=(a,b)=>{
  assert(Number.isInteger(a)&&a>=0&&a<=2147483647);
  assert(Number.isInteger(b)&&b>=0&&b<=2147483647);
  return a===b?0:a<b?-1:1;
};
const hybrid=run({compareI32});
eq(hybrid.map,base.map);
assert(hybrid.stages.comparisonCounts.i32Hook>0);
eq(hybrid.stages.comparisonCounts.jsBigInt,0);
const mixed=run({compareI32,tensor:large,reweight:{"0":[huge,1]}});
assert(mixed.stages.comparisonCounts.i32Hook>0&&mixed.stages.comparisonCounts.jsBigInt>0);
assert.throws(()=>run({compareI32:()=>1}),/native comparison disagrees/);
console.log(`PASS exact tensor/qualification controls and ${checks} independent exhaustive comparisons`);
