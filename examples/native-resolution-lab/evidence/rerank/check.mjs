import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {AXES,STAGES,demoEvents,canonicalGraph,searchLab} from './oracle.mjs';
const read=n=>fs.readFileSync(new URL(n,import.meta.url));
const original=read('planner.wasm'), rerank=read('rerank.wasm');
assert.deepEqual(rerank,read('repeat.wasm'));
const calls=[];
function load(bytes,pages){
 const module=new WebAssembly.Module(bytes);
 const stubs=Object.create(null);
 for(const req of WebAssembly.Module.imports(module)){
  assert.ok(req.module==='wasi_snapshot_preview1'&&req.kind==='function');
  assert.ok(['fd_write','fd_read','proc_exit','args_sizes_get','args_get'].includes(req.name));
  stubs[req.name]=()=>{calls.push(req.name);throw Error('host call');};
 }
 const ex=new WebAssembly.Instance(module,{wasi_snapshot_preview1:stubs}).exports;
 const base=ex.memory.grow(pages)*65536,view=new DataView(ex.memory.buffer);
 return {ex,base,
  put:(base,i,x)=>view.setBigInt64(base+8*i,BigInt(x),true),
  get:(base,i)=>Number(view.getBigInt64(base+8*i,true))};
}
const plan=load(original,10), re=load(rerank,5);
const data=plan.base,initialWeights=data+32*9*8,work=initialWeights+40,output=work+4096*72;
const front=re.base,weight=front+(3+4096*9)*8;
const cmp=(x,y)=>x===y?0:x<y?-1:1;
function setup(events) {
 const graph=canonicalGraph(events);
 const rows=graph.records.filter(a=>a.kind==='action').sort((a,b)=>STAGES.indexOf(a.phase)-STAGES.indexOf(b.phase)||cmp(a.key,b.key));
 const names=[...new Set(['query','resolved',...rows.flatMap(a=>[...a.requires,...a.provides])])].sort(cmp);
 const facts=keys=>keys.reduce((m,k)=>m|(1<<names.indexOf(k)),0);
 rows.flatMap(e=>[STAGES.indexOf(e.phase)+1,facts(e.requires),facts(e.provides),(e.admission==='qualified-fixture'?1:0)+(e.holdout?2:0),...AXES.map(k=>e.metrics[k])]).forEach((x,i)=>plan.put(data,i,x));
 return {rows,graph,initial:facts(['query']),required:facts(['resolved'])};
}
function solve(fixture,mode,mask,w,maximum=8) {
 w.forEach((x,i)=>plan.put(initialWeights,i,x));
 const count=Number(plan.ex.idol_planner__plan(...[data,fixture.rows.length,fixture.initial,fixture.required,mode,mask,maximum,
  initialWeights,work,4096,output,4096].map(BigInt)));
 assert.ok(count>=0);
 return Array.from({length:3+9*count},(_,i)=>plan.get(output,i));
}
function cache(words) {words.forEach((x,i)=>re.put(front,i,x));}
function choose(rows,mask,max,w) {
 w.forEach((x,i)=>re.put(weight,i,x));
 return Number(re.ex.idol_rerank__winner(...[front,rows,mask,max,weight].map(BigInt)));
}
const events=demoEvents();
let checks=0, changes=0, empty=0;
for(const [name,input] of [
 ['all',events],['before receipt',events.filter(e=>e.key!=='full-receipt')],
 ['before witness',events.filter(e=>e.key!=='witness-index')],
 ['empty terminal',events.filter(e=>e.phase!=='record')]
])for(let mode=0;mode<=1;mode++)for(let mask=1;mask<32;mask++){
 const fixture=setup(input);
 const axes=AXES.filter((_,i)=>mask&(1<<i));
 const same=solve(fixture,mode,mask,[1,1,1,1,1]);
 const rows=same[1], originalWinner=same[2];
 cache(same);
 for(let t=0;t<9;t++){
  const w=AXES.map((a,i)=>t===0?1:t<=5?((t-1)===i?1000000:1):((i+2)**t)%999983);
  const pick=choose(rows,mask,8,w);
  const clean=solve(fixture,mode,mask,w);
  assert.equal(pick,clean[2],JSON.stringify({name,mode,mask,w}));
  assert.deepEqual([...same.slice(0,2),...same.slice(3)],[...clean.slice(0,2),...clean.slice(3)]);
  const truth=searchLab(fixture.graph,{mode:'exhaustive',profile:mode?'full':'narrow',axes,
   weights:Object.fromEntries(axes.map(a=>[a,w[AXES.indexOf(a)]]))});
  assert.ok(truth.certificate.exact);
  assert.equal(pick,truth.selected?1+truth.frontier.findIndex(p=>p.id===truth.selected.id):0);
  const decoded=truth.frontier.flatMap(p=>[
   ...p.actions.map(k=>fixture.rows.findIndex(r=>r.key===k)+1), ...AXES.map(k=>p.metrics[k])]);
  assert.deepEqual(clean.slice(3),decoded);
  assert.deepEqual(Array.from({length:same.length},(_,i)=>re.get(front,i)),same);
  checks++;changes+=+(pick!==originalWinner);empty+=+(rows===0);
 }
}
assert.ok(changes>100);
const fixture=setup(events), old=solve(fixture,1,31,[1,1,1,1,1]);
const n=old[1], ws=[1,1,1,1,1];
const clone=(i,v)=>old.map((x,j)=>i===j?v:x);
const refusal=[];
for(const [name,words,rows,mask,max,w,expected] of [
 ['rows-negative',old,-1,31,8,ws,-1],['empty mask',old,n,0,8,ws,-1],
 ['invalid maximize',old,n,31,32,ws,-1],['bad crowd',clone(0,n-1),n,31,8,ws,-2],
 ['bad frontier count',clone(1,n-1),n,31,8,ws,-2],['bad old winner',clone(2,0),n,31,8,ws,-2],
 ['bad row member',clone(3,0),n,31,8,ws,-2],['bad metric',clone(7,4000001),n,31,8,ws,-2],
 ['duplicate lexical row',[...old.slice(0,12),...old.slice(3,7),...old.slice(16)],n,31,8,ws,-2],
 ['none active',old,n,2,8,[1,0,1,1,1],-3],['weight overflow',old,n,31,8,[1000001,...ws.slice(1)],-3],
]) {
 cache(words);assert.equal(choose(rows,mask,max,w),expected,name);
 assert.deepEqual(Array.from({length:words.length},(_,i)=>re.get(front,i)),words);
 refusal.push({name,expected});
}
assert.deepEqual(calls,[]);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
console.log(JSON.stringify({checks,changes,empty,refusal,calls,source:sha(read('rerank.id')),wasm:sha(rerank),
 originalPlanner:sha(original),jsOracle:sha(read('oracle.mjs')),node:process.version,v8:process.versions.v8},null,2));
