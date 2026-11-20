import assert from 'node:assert/strict';
import fs from 'node:fs';
const b=fs.readFileSync(new URL('./planner.wasm',import.meta.url));
assert.deepEqual(b,fs.readFileSync(new URL('./repeat.wasm',import.meta.url)));
const m=new WebAssembly.Module(b);
const calls=[];
const stubs=Object.fromEntries(WebAssembly.Module.imports(m).map(x=>[x.name,()=>{calls.push(x.name);throw Error('host call');}]));
const {memory,idol_planner__plan:plan}=new WebAssembly.Instance(m,{wasi_snapshot_preview1:stubs}).exports;
const base=memory.grow(10)*65536;
const row=base,weights=row+32*72,work=weights+40,output=work+4096*72;
const view=new DataView(memory.buffer);
const out=new Uint8Array(memory.buffer,output,24+4096*72);
const put=(base,i,x)=>view.setBigInt64(base+8*i,BigInt(x),true);
const get=(base,i)=>Number(view.getBigInt64(base+8*i,true));
function native(rows,mask,max,w,mode,cap=4096,limit=4096){
 rows.flat().forEach((x,i)=>put(row,i,x));w.forEach((x,i)=>put(weights,i,x));
 out.fill(171);
 const a=Number(plan(...[row,rows.length,1,16,mode,mask,max,weights,work,cap,output,limit].map(BigInt)));
 if(a<0){assert.ok(out.every(x=>x===171));return a;}
 const n=get(output,0),pick=get(output,2);
 const rowsOut=Array.from({length:a},(_,i)=>Array.from({length:9},(_,j)=>get(output,3+i*9+j)));
 return {n,pick,rows:rowsOut};
}
// Independent brute-force oracle over the exact serialized graph primitive, not fixture keys.
function verify(rows,mask,max,w,mode){
 const layers=[1,2,3,4].map(s=>rows.flatMap((r,i)=>r[0]===s?[[r,i+1]]:[]));
 const candidates=[];
 function walk(step,known,ids,sum){
  if(step===4){if(known&16)candidates.push([...ids,...sum]);return;}
  for(const [r,i] of layers[step]){
   const [,need,give,flag,...objective]=r;
   if(!(flag&1)||(!mode&&(flag&2))||(need&known)!==need)continue;
   walk(step+1,known|give,[...ids,i],sum.map((x,j)=>x+objective[j]));
  }
 }
 walk(0,1,[],[0,0,0,0,0]);
 const using=[0,1,2,3,4].filter(i=>mask&(1<<i));
 const oriented=(r,i)=>r[4+i]*(max&(1<<i)?-1:1);
 const frontier=candidates.filter((b,j)=>!candidates.some((a,i)=>j!==i&&
   using.every(k=>oriented(a,k)<=oriented(b,k))&&
   (i<j||using.some(k=>oriented(a,k)<oriented(b,k)))));
 function score(r){return using.reduce((t,i)=>t+oriented(r,i)*w[i],0);}
 const p=frontier.reduce((best,r,i)=>best<0||score(r)<score(frontier[best])?i:best,-1);
 return {n:candidates.length,pick:p+1,rows:frontier};
}
const boundary=[1,2,3,4].flatMap(s=>Array.from({length:8},()=>[s,1<<(s-1),1<<s,1,1000000,1000000,1000000,1000000,1000000]));
assert.deepEqual(native(boundary,31,8,[1000000,1000000,1000000,1000000,1000000],1),{
 n:4096,pick:1,rows:[[1,9,17,25,4000000,4000000,4000000,4000000,4000000]]
});
assert.equal(native(boundary,31,8,[1,1,1,1,1],1,4095),-3);
assert.equal(native(boundary,31,8,[1,1,1,1,1],1,4096,4095),-3);
const wide=boundary.slice();wide[8]=[1,...wide[8].slice(1)];
assert.equal(native(wide,31,8,[1,1,1,1,1],1),-2);
let seed=0xe4176d;
function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;}
const check=[];
for(let i=0;i<100;i++){
 const rows=[1,2,3,4].flatMap(s=>Array.from({length:1+rand(5)},()=>[
   s,(1<<(s-1))|(rand(3)===0?32:0),(1<<s)|(rand(3)===0?32:0),[0,1,1,3][rand(4)],
   ...[0,1,2,3,4].map(()=>rand(20)),
 ]));
 const mask=1+rand(31),max=rand(32),mode=rand(2);
 const w=Array.from({length:5},()=>1+rand(1000000));
 const exp=verify(rows,mask,max,w,mode);
 assert.deepEqual(native(rows,mask,max,w,mode),exp);
 check.push({i,n:exp.n,front:exp.rows.length,mask,max,mode,rows});
}
assert.ok(check.some(x=>x.front>1));
assert.deepEqual(calls,[]);
console.log(JSON.stringify({identicalBuilds:true,maxPaths:4096,maxMetric:4000000,capacityRefusals:2,tooWideRefusal:1,syntheticIndependentGraphCases:check.length,completeOutputCanaryBytes:out.length,emptyGraphOutcomes:check.filter(x=>x.n===0).length,calls,observations:check},null,2));
