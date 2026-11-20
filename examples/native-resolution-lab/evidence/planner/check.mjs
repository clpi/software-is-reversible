import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {AXES,STAGES,demoEvents,canonicalGraph,searchLab,EVIDENCE} from './oracle.mjs';

const bytes=fs.readFileSync(new URL('./planner.wasm',import.meta.url));
const module=new WebAssembly.Module(bytes);
const calls=[];
const stubs=Object.create(null);
for(const i of WebAssembly.Module.imports(module)) {
 assert.equal(i.module,'wasi_snapshot_preview1');
 assert.equal(i.kind,'function');
 assert.ok(['fd_write','fd_read','proc_exit','args_sizes_get','args_get'].includes(i.name));
 stubs[i.name]=()=>{calls.push(i.name);throw Error('no host effects');};
}
const {memory,idol_planner__plan:plan}=new WebAssembly.Instance(module,{wasi_snapshot_preview1:stubs}).exports;
assert.equal(plan.length,12);
const begin=memory.grow(10)*65536;
const data=begin, weights=data+32*9*8, work=weights+5*8, output=work+4096*9*8;
assert.ok(output+(3+4096*9)*8<=memory.buffer.byteLength);
const view=new DataView(memory.buffer);
const put=(base,idx,val)=>view.setBigInt64(base+8*idx,BigInt(val),true);
const take=(base,idx)=>Number(view.getBigInt64(base+8*idx,true));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const lexa=(a,b)=>a<b?-1:a>b?1:0;
const dims=mask=>AXES.filter((_,i)=>((mask>>i)&1)!==0);
const checkAll=[];
function layout(events){
 const graph=canonicalGraph(events);
 const caps=[...new Set(['query','resolved',...graph.records.filter(a=>a.kind==='action').flatMap(a=>[...a.requires,...a.provides])])].sort(lexa);
 assert.ok(caps.length<=16);
 const mask=xs=>xs.reduce((m,k)=>m | (1<<caps.indexOf(k)),0);
 const rows=graph.records.filter(e=>e.kind==='action').sort((a,b)=>STAGES.indexOf(a.phase)-STAGES.indexOf(b.phase)||lexa(a.key,b.key));
 const fields=rows.map(e=>[STAGES.indexOf(e.phase)+1,mask(e.requires),mask(e.provides),(e.admission==='qualified-fixture'?1:0)+(e.holdout?2:0),...AXES.map(a=>e.metrics[a])]);
 return {graph,caps,rows,fields,initial:mask(['query']),required:mask(['resolved'])};
}
function invoke(fixture,mode,mask,w,opts={}){
 const fields=opts.fields??fixture.fields;
 for(let i=0;i<fields.length;i++)for(let j=0;j<9;j++)put(data,i*9+j,fields[i][j]);
 for(let i=0;i<5;i++)put(weights,i,w[i]);
 for(let i=0;i<18;i++)put(output,i,-777);
 const args=[data,opts.rows??fields.length,fixture.initial,fixture.required,mode,mask,opts.maximum??8,weights,work,opts.capacity??4096,output,opts.limit??4096].map(BigInt);
 const answer=Number(plan(...args));
 if(answer<0){assert.deepEqual(Array.from({length:18},(_,i)=>take(output,i)),Array(18).fill(-777));return answer;}
 const header=Array.from({length:3},(_,i)=>take(output,i));
 assert.equal(header[1],answer);
 const values=Array.from({length:answer},(_,i)=>Array.from({length:9},(_,j)=>take(output,3+i*9+j)));
 return {count:header[0],winner:header[2],rows:values.map(r=>[r.slice(0,4).map(x=>fixture.rows[x-1]?.key),r.slice(4)])};
}
function compare(events,name,mode,mask,w,maximum=8){
 const fixture=layout(events);
 const answer=invoke(fixture,mode,mask,w,{maximum});
 const axes=dims(mask);
 const wt=Object.fromEntries(axes.map(a=>[a,w[AXES.indexOf(a)]]));
 const j=searchLab(fixture.graph,{mode:'exhaustive',axes,weights:wt,profile:mode?'full':'narrow'});
 assert.ok(j.certificate.exact,JSON.stringify({name,mode,mask}));
 const truth={count:j.stats.resolvedWitnessesBeforeFinalPareto,
  winner:j.selected?1+j.frontier.findIndex(e=>e.id===j.selected.id):0,
  rows:j.frontier.map(p=>[p.actions,AXES.map(a=>p.metrics[a])])};
 assert.deepEqual(answer,truth,JSON.stringify({name,mode,mask,w,answer,truth}));
 checkAll.push({name,mode,mask,w,resolved:truth.count,front:truth.rows.length,winner:truth.winner});
}
const events=demoEvents();
compare(events,'first smoke',1,31,[1,1,1,1,1]);
console.log('SMOKE',JSON.stringify(checkAll.at(-1)));
for(const [name,included] of [
 ['all',events],
 ['before receipt append',events.filter(e=>e.key!=='full-receipt')],
 ['before witness append',events.filter(e=>e.key!=='witness-index')],
 ['after empty terminal stage',events.filter(e=>e.phase!=='record')],
])for(let mode=0;mode<=1;mode++)for(let mask=1;mask<32;mask++)for(let skew=0;skew<=1;skew++){
 const w=AXES.map((_,i)=>((mask>>i)&1)===0?0:skew?(i+1)**3:1);
 compare(included,name,mode,mask,w);
}
const fixture=layout(events);
const w=[1,1,1,1,1];
const refusal=[];
for(const [name,mode,mask,weight,opt,expected] of [
 ['bad mode',2,31,w,{},-1],['empty objective',1,0,w,{},-1],['row count overflow',1,31,w,{rows:33},-1],
 ['bad weight',1,31,[-1,1,1,1,1],{},-2],['no active weights',1,1,[0,1,1,1,1],{},-2],
 ['bad stage',1,31,w,{fields:fixture.fields.map((r,i)=>i===0?[5,...r.slice(1)]:r)},-2],
 ['bad capability mask',1,31,w,{fields:fixture.fields.map((r,i)=>i===0?[r[0],65536,...r.slice(2)]:r)},-2],
 ['negative metric',1,31,w,{fields:fixture.fields.map((r,i)=>i===0?[...r.slice(0,8),-1]:r)},-2],
 ['work too short',1,31,w,{capacity:0},-3],['output too short',1,31,w,{limit:0},-3],
]) {
 assert.equal(invoke(fixture,mode,mask,weight,opt),expected);
 refusal.push({name,expected,intactCanaryWords:18});
}
let seed=0xac1209;
function rng(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed>>>16;}
for(let batch=0;batch<40;batch++){
 const esm=events.map(e=>e.kind==='scope'?e:{...e,metrics:Object.fromEntries(AXES.map(a=>[a,rng()%7])),
   holdout:(rng()&3)===0,admission:(rng()&7)===0?'unverified-proposal':'qualified-fixture'});
 const mask=1+(rng()%31);
 compare(esm,'generated '+batch,rng()%2,mask,AXES.map((_,i)=>1+i));
}
assert.deepEqual(calls,[]);
const receipt={engine:{node:process.version,v8:process.versions.v8},wasmSHA:sha(bytes),oracleSHA:sha(fs.readFileSync(new URL('./oracle.mjs',import.meta.url))),calls,pass:checkAll.length,refusals:refusal,observations:checkAll};
fs.writeFileSync(new URL('./checks.json',import.meta.url),JSON.stringify(receipt,null,2)+'\n');
console.log('PASS',checkAll.length,'native exact planner / JS independent oracle profiles; refusals',refusal.length);
