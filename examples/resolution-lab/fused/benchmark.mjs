import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import os from 'node:os';
import crypto from 'node:crypto';
const lab=process.argv[2];
const {AXES,DIRECTIONS,dominates}=await import(pathToFileURL(path.join(lab,'search.mjs')));
const {loadKernel}=await import(pathToFileURL(path.join(lab,'kernel.mjs')));
const scalarKernel=await loadKernel(fs.readFileSync(path.join(lab,'native/kernel.wasm')));
const fused=fs.readFileSync(new URL('./fused.wasm',import.meta.url));
const module=new WebAssembly.Module(fused);
const imports={wasi_snapshot_preview1:Object.create(null)};
for(const x of WebAssembly.Module.imports(module)) imports.wasi_snapshot_preview1[x.name]=()=>{throw Error('unexpected WASI call');};
const raw=new WebAssembly.Instance(module,imports).exports.idol_fused__dominates;
const B=n=>{if(!Number.isInteger(n)||n < -2147483648||n>2147483647)throw Error('Outside signed i32');return BigInt(n);};
const pack=m=>[B(m.latency),B(m.storage),B(m.risk),B(-m.clarity),B(m.compute)];
const rawCall=(mask,a,b)=>raw(mask,a[0],a[1],a[2],a[3],a[4],b[0],b[1],b[2],b[3],b[4])===1n;
const fusedCall=(mask,a,b)=>raw(mask,
 B(a.latency),B(a.storage),B(a.risk),B(-a.clarity),B(a.compute),
 B(b.latency),B(b.storage),B(b.risk),B(-b.clarity),B(b.compute))===1n;
assert.deepEqual(AXES,['latency','storage','risk','clarity','compute']);
assert.deepEqual(AXES.map(a=>DIRECTIONS[a]),[1,1,1,-1,1]);
const P=32768, R=31;
let seed=0x764bf8;
const rand=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return seed>>>0;};
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const inputModes=[['mixed/5',AXES,'mixed'],['ties/5',AXES,'ties'],['early failure/5',AXES,'early'],['mixed/3',['latency','risk','clarity'],'mixed']];
const profiles={};
function stats(xs) {
 const s=xs.slice().sort((a,b)=>a-b);
 return {median:s[(s.length-1)>>1],min:s[0],p95:s[Math.ceil(s.length*.95)-1],max:s.at(-1),raw:xs};
}
for(const [title,axes,mode] of inputModes) {
 const pairs=[];
 const mask=BigInt(axes.reduce((sum,a)=>sum+(1<<AXES.indexOf(a)),0));
 for(let i=0;i<P;i++){
   const a={metrics:Object.fromEntries(AXES.map(k=>[k,rand()%1000000]))};
   const b={metrics:Object.fromEntries(AXES.map(k=>[k,mode==='ties'||(mode==='mixed'&&i%16===0)?a.metrics[k]:rand()%1000000]))};
   if(mode==='early')b.metrics.latency=a.metrics.latency-1;
   pairs.push({a,b});
 }
 const inputSha=hash(JSON.stringify(pairs));
 const preboxStart=process.hrtime.bigint();
 for(const row of pairs){row.p=pack(row.a.metrics);row.q=pack(row.b.metrics);}
 const preboxNs=Number(process.hrtime.bigint()-preboxStart)/P;
 const variants={
   js:row=>dominates(row.a,row.b,axes),
   scalarChecked:row=>dominates(row.a,row.b,axes,scalarKernel.compare),
   fusedChecked:row=>fusedCall(mask,row.a.metrics,row.b.metrics),
   fusedPreboxed:row=>rawCall(mask,row.p,row.q),
 };
 let truth=0;
 for(const row of pairs){
   const expected=variants.js(row);
   truth+=+expected;
   for(const [name,fn] of Object.entries(variants)) assert.equal(fn(row),expected,name);
 }
 let coordinateCalls=0;
 for(const row of pairs) dominates(row.a,row.b,axes,(a,b)=>{coordinateCalls++;return a===b?0:a<b?-1:1;});
 const samples=Object.fromEntries(Object.keys(variants).map(k=>[k,[]]));
 function measure(fn){
   const start=process.hrtime.bigint();
   let sum=0;
   for(const row of pairs)sum+=+fn(row);
   const ms=Number(process.hrtime.bigint()-start)/P;
   assert.equal(sum,truth);
   return ms;
 }
 for(let warm=0;warm<6;warm++)for(const fn of Object.values(variants))measure(fn);
 const order=Object.keys(variants);
 for(let i=0;i<R;i++){
   for(let j=order.length-1;j>0;j--){const k=rand()%(j+1);[order[j],order[k]]=[order[k],order[j]];}
   for(const name of order)samples[name].push(measure(variants[name]));
 }
 profiles[title]={pairCount:P,axisMask:Number(mask),inputSha256:inputSha,dominantPairs:truth,scalarCallCount:coordinateCalls,fusedCallCount:P,
   observedOnePassPreboxSetupNsPerPair:preboxNs,nsPerPair:Object.fromEntries(Object.entries(samples).map(([k,v])=>[k,stats(v)]))};
}
console.log(JSON.stringify({evidence:'Synthetic pair-kernel, matched results and same process; not browser end-to-end, not a speed claim beyond the measured fixtures. Native historical compiler. Main JS frontier/verifier unchanged.',
 toolchain:{node:process.version,v8:process.versions.v8,arch:process.arch,os:os.release(),cpu:os.cpus()[0]?.model},
 sha256:{search:hash(fs.readFileSync(path.join(lab,'search.mjs'))),scalarWrapper:hash(fs.readFileSync(path.join(lab,'kernel.mjs'))),scalarWasm:hash(fs.readFileSync(path.join(lab,'native/kernel.wasm'))),fusedWasm:hash(fused)},profiles},null,2));
