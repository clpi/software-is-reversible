import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const roots=Object.fromEntries(['planner','chat','reversal'].map((n,i)=>[n,process.argv[i+2]||new URL(`../../wasm/${n}.wasm`,import.meta.url)]));
const reference=await import(process.argv[5]?pathToFileURL(process.argv[5]):new URL('../planner/oracle.mjs',import.meta.url));
const {demoEvents,canonicalGraph,searchLab,AXES,STAGES}=reference;
let hostCalls=0;
function open(name){
  const buf=readFileSync(roots[name]), mod=new WebAssembly.Module(buf);
  const imports=Object.create(null);
  for(const item of WebAssembly.Module.imports(mod)){
    assert.equal(item.kind,'function'); assert.equal(item.module,'wasi_snapshot_preview1');
    imports[item.module]??=Object.create(null);
    imports[item.module][item.name]=()=>{hostCalls++;throw Error('WASI forbidden');};
  }
  const exports=new WebAssembly.Instance(mod,imports).exports;
  const call=(f,...args)=>Number(exports[`idol_${name}__${f}`](...args.map(BigInt)));
  return {exports,call,sha256:createHash('sha256').update(buf).digest('hex')};
}
const planner=open('planner'), chat=open('chat'), reversal=open('reversal');
const arr=(n,f)=>Array.from({length:n},(_,i)=>f(i));
const cmp=(a,b)=>a<b?-1:a>b?1:0;
const ordered=(xs,ys)=>xs.map((x,i)=>cmp(x,ys[i])).find(s=>s!==0)??0;
let seed=0x2fa3ae50;
const rnd=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return Number((BigInt(seed)*BigInt(n))>>32n);};
const head={rows:0,initial:1,required:4,mode:1,mask:31,maximum:8,capacity:4096,limit:4096};
const sentinel=0xa5;
const base=65536, weightsPtr=69632, scratch=73728, output=368640;
const outputBytes=(3+9*4096)*8;
const memory=planner.exports.memory;
if(memory.buffer.byteLength<output+outputBytes) memory.grow(Math.ceil((output+outputBytes-memory.buffer.byteLength)/65536));
const mem=()=>new Uint8Array(memory.buffer);
const words=(ptr,n)=>arr(n,i=>Number(new DataView(memory.buffer).getBigInt64(ptr+8*i,true)));
const setWords=(ptr,items)=>items.forEach((v,i)=>new DataView(memory.buffer).setBigInt64(ptr+8*i,BigInt(v),true));
function runPlan(records,weights,opts={}){
  const h={...head,rows:records.length,...opts};
  setWords(base,records.flat());setWords(weightsPtr,weights);
  mem().fill(sentinel,output,output+outputBytes);
  const count=planner.call('plan',base,h.rows,h.initial,h.required,h.mode,h.mask,h.maximum,weightsPtr,scratch,h.capacity,output,h.limit);
  if(count<0){
    assert(mem().subarray(output,output+outputBytes).every(v=>v===sentinel),'planner refusal changed output');
    return count;
  }
  assert.equal(count,words(output,3)[1]);
  assert(mem().subarray(output+(3+9*count)*8,output+outputBytes).every(v=>v===sentinel),'planner wrote outside receipt');
  return {header:words(output,3),rows:arr(count,i=>words(output+(3+9*i)*8,9))};
}
function oracle(records,weights,opts={}){
  const o={...head,...opts}, pool=[];
  const axes=arr(5,i=>i).filter(i=>o.mask&1<<i);
  function visit(rows,have){
    const i=rows.length;
    if(i===4){
      if((have&o.required)!==o.required)return;
      const ms=arr(5,i=>rows.reduce((sum,r)=>sum+records[r][i+4],0));
      const vs=axes.map(i=>(o.maximum&1<<i)?-ms[i]:ms[i]);
      pool.push({ids:rows.map(r=>r+1),ms,vs,score:vs.reduce((sum,v,j)=>sum+v*weights[axes[j]],0)});
      return;
    }
    records.forEach(([stage,req,adds,admit],row)=>{
      if(stage!==i+1||!(admit&1)||(!o.mode&&(admit&2))||(req&have)!==req)return;
      visit([...rows,row],have|adds);
    });
  }
  visit([],o.initial);
  const keep=pool.filter(x=>!pool.some(y=>y!==x&&y.vs.every((v,j)=>v<=x.vs[j])&&(
    y.vs.some((v,j)=>v<x.vs[j])||ordered(y.ids,x.ids)<0)));
  keep.sort((x,y)=>ordered(x.ids,y.ids));
  const min=[...keep].sort((x,y)=>cmp(x.score,y.score)||ordered(x.ids,y.ids))[0];
  return {header:[pool.length,keep.length,keep.indexOf(min)+1],rows:keep.map(x=>[...x.ids,...x.ms])};
}
function normalizedPlanner(){
  const g=canonicalGraph(demoEvents()), a=g.records.filter(x=>x.kind==='action').sort((x,y)=>cmp(STAGES.indexOf(x.phase),STAGES.indexOf(y.phase))||cmp(x.key,y.key));
  const keys=[...new Set(['query','resolved',...a.flatMap(x=>[...x.requires,...x.provides])])].sort(cmp);
  const flags=ys=>ys.reduce((m,c)=>m|1<<keys.indexOf(c),0);
  return {g,a,records:a.map(x=>[STAGES.indexOf(x.phase)+1,flags(x.requires),flags(x.provides),x.admission==='qualified-fixture'?(x.holdout?3:1):0,...AXES.map(k=>x.metrics[k])]),
    opts:{initial:flags(['query']),required:flags(['resolved'])}};
}
const d=normalizedPlanner();
let plannerComparisons=0;
for(const mask of arr(31,i=>i+1))for(const mode of [0,1]){
  const weights=AXES.map((_,i)=>2+i*(mask%7));
  const opts={...d.opts,mask,mode};
  const actual=runPlan(d.records,weights,opts), expected=oracle(d.records,weights,opts);
  assert.deepEqual(actual,expected);
  const axes=AXES.filter((_,i)=>mask&1<<i);
  const old=searchLab(d.g,{mode:'exhaustive',profile:mode?'full':'narrow',axes,weights:Object.fromEntries(axes.map(a=>[a,weights[AXES.indexOf(a)]]))});
  assert(old.certificate.exact);
  assert.deepEqual(actual.rows.map(x=>x.slice(0,4).map(i=>d.a[i-1].key)),old.frontier.map(x=>x.actions));
  assert.deepEqual(actual.rows[actual.header[2]-1]?.slice(0,4).map(i=>d.a[i-1].key),old.selected?.actions);
  plannerComparisons++;
}
for(let iter=0;iter<160;iter++){
  const records=[];
  for(let stage=1;stage<=4;stage++)for(let j=0,count=1+rnd(4);j<count;j++){
    records.push([stage,rnd(4),rnd(7)+1,[0,1,3][rnd(3)],...arr(5,()=>rnd(13))]);
  }
  const weights=arr(5,()=>rnd(1000001)), opts={mask:1+rnd(31),maximum:rnd(32),mode:rnd(2),required:1+rnd(7),initial:rnd(8)};
  const atleast=weights.findIndex((w,j)=>w>0&&(opts.mask&(1<<j)));if(atleast<0)weights[0]=1,opts.mask|=1;
  assert.deepEqual(runPlan(records,weights,opts),oracle(records,weights,opts));
  plannerComparisons++;
}
const four=[[1,1,2,1,1000000,0,0,1000000,0],[2,2,2,1,1000000,0,0,1000000,0],[3,2,2,1,1000000,0,0,1000000,0],[4,2,4,1,1000000,0,0,1000000,0]];
assert.deepEqual(runPlan(four,arr(5,()=>1000000)),oracle(four,arr(5,()=>1000000)));
const gateCorruptors=[
  [-1,rs=>{}, {required:0}],[-1,rs=>{}, {mask:32}],[-1,rs=>{}, {capacity:4097}],[-1,rs=>{}, {rows:33}],
  [-2,rs=>{rs[0][0]=0;}],[-2,rs=>{rs[1][0]=0;}],[-2,rs=>{rs[1][2]=0;}],[-2,rs=>{rs[1][3]=4;}],
  [-2,rs=>{rs[2][4]=-1;}],[-2,rs=>{rs[2][8]=1000001;}],[-2,rs=>{}, {}, [-1,1,1,1,1]],
  [-2,rs=>{}, {mask:1}, [0,1,1,1,1]],[-3,rs=>{}, {capacity:0}],[-3,rs=>{}, {limit:0}],
];
for(const [code,change,opts={},weights=[1,1,1,1,1]] of gateCorruptors){
  const rows=structuredClone(four);change(rows);assert.equal(runPlan(rows,weights,opts),code);
}
const bypass=structuredClone(four);
bypass[0][3]=0;
assert.deepEqual(runPlan(bypass,[1,1,1,1,1]),{header:[0,0,0],rows:[]});
bypass[0][3]=3;
assert.deepEqual(runPlan(bypass,[1,1,1,1,1],{mode:0}),{header:[0,0,0],rows:[]});
assert.equal(runPlan(bypass,[1,1,1,1,1],{mode:1}).header[0],1);
// The ABI is not an admission authority: a caller that forges qualification bits
// or semantic capabilities can produce a result. Exercise that limitation explicitly.
const forged=structuredClone(four);forged[2][1]=0;
assert.equal(runPlan(forged,[1,1,1,1,1]).header[0],1);
const lowVector=[];
for(let i=0;i<4;i++)for(let j=0;j<2;j++) lowVector.push([i+1,0,4,1,1+j,0,0,10*j,0]);
const signedOpts={mask:9,maximum:8}, signedWeights=[1,0,0,1000000,0];
assert.deepEqual(runPlan(lowVector,signedWeights,signedOpts),oracle(lowVector,signedWeights,signedOpts));
const win=runPlan(lowVector,signedWeights,signedOpts).header[2];
assert.equal(win,5,'signed negative clarity sum must beat positive latency score');

function chatOracle(rows,first,h){
  const unpacked=rows.map(n=>n===-1?null:[n%4,(n>>2)%4,n>>4]);
  const open=[],term=[];
  let known=0;
  function walk(trail,row,pn,pd,path){
    if(trail.length>=h)return;
    if(row===null){open.push([pn,pd]);return;}
    known++;
    const total=row.reduce((a,v)=>a+v,0);
    if(trail.length+1>=first&&row[2]>0) term.push([pn*row[2],pd*total,[...trail,2],path]);
    row.slice(0,2).forEach((n,t)=>{
      if(n)walk([...trail,t],unpacked[t+1],pn*n,pd*total,path*2+t);
    });
  }
  const ratios=(x,y)=>cmp(x[0]*y[1],y[0]*x[1]);
  walk([],unpacked[0],1,1,1);
  term.sort((a,b)=>-ratios(a,b)||ordered(a[2],b[2]));
  open.sort((a,b)=>-ratios(a,b));
  const b=term[0]??[0,1,[],0], u=open[0]??[0,1];
  const status=b[3]?(ratios(b,u)>0?3:ratios(b,u)===0?2:1):open.length?0:4;
  const upper=ratios(b,u)>0?b:u;
  // Fallible implementations may choose equivalent unreduced numerators and denominators.
  return {status,path:b[3],value:b.slice(0,2),upper:upper.slice(0,2),known,unknown:open.length};
}
let chatCount=0;const statuses=new Set();
function checkChat(rows,first,h){
  const a=arr(8,i=>chat.call('decision',...rows,first,h,i)), e=chatOracle(rows,first,h);
  assert.deepEqual([a[0],a[1],a[6],a[7]],[e.status,e.path,e.known,e.unknown]);
  assert(a[3]>0&&a[5]>0);
  assert.equal(a[2]*e.value[1],a[3]*e.value[0]);assert.equal(a[4]*e.upper[1],a[5]*e.upper[0]);
  const word=BigInt(chat.call('decision',...rows,first,h,8));
  const fields=[[0,3],[3,4],[7,7],[14,13],[27,7],[34,13],[47,4],[51,4]];
  assert.deepEqual(fields.map(([shift,k])=>Number((word>>BigInt(shift))&((1n<<BigInt(k))-1n))),a);
  statuses.add(a[0]);chatCount++;
}
const packed=[-1,1,4,16,5,17,20,21,63];
for(const a of packed)for(const b of packed)for(const c of packed)for(let h=1;h<=4;h++)for(let f=1;f<=h;f++)checkChat([a,b,c],f,h);
for(let i=0;i<1500;i++){const h=1+rnd(4);checkChat(arr(3,()=>{const x=rnd(64);return x||-1;}),1+rnd(h),h);}
assert.deepEqual([...statuses].sort(cmp),[0,1,2,3,4]);
const chatBad=[[0,4,4,1,4,0],[64,4,4,1,4,0],[1,-2,4,1,4,0],[1,4,0,1,4,0],
 [1,4,4,0,4,0],[1,4,4,2,1,0],[1,4,4,1,5,0],[1,4,4,1,4,-1],[1,4,4,1,4,9]];
for(const args of chatBad)assert.equal(chat.call('decision',...args),-1);

const pack=xs=>xs.reduce((sum,a,i)=>sum+a*4**i,0);
const apply=(x,a)=>a===1?(x^1):a===2?0:((x<<1)|(x>>2))&7;
let reversalRoundTrips=0;
function testPlan(xs,depth=0){
  if(xs.length){
    const plan=pack(xs);
    for(let original=0;original<8;original++)for(const epoch of [0,13,127-xs.length*2]){
      let v=original, res=0;
      xs.forEach((x,i)=>{if(x===2)res+=(v+1)*9**i;v=apply(v,x);});
      const before=epoch*8+original, after=(epoch+xs.length)*8+v, back=(epoch+2*xs.length)*8+original;
      const receipt=plan+256*(res+6561*(v+8*epoch));
      const call=reversal.call;
      assert.equal(call('prepare',before,before,plan,15),receipt);
      assert.equal(call('advance',receipt,receipt,before,15),after);
      assert.equal(call('verify',receipt,receipt,after),after);
      assert.equal(call('inverse',receipt,receipt,after,15),back);
      assert.equal(call('undoverify',receipt,receipt,after,back,15),back);
      assert.equal(call('undoverify',receipt,receipt,after,back^1,15),-2);
      if(xs.includes(2))assert.equal(call('inverse',receipt,receipt,after,7),-3);
      reversalRoundTrips++;
    }
  }
  if(depth<4)for(const a of [1,2,3])testPlan([...xs,a],depth+1);
}
testPlan([]);
const rc=reversal.call, clear=rc('prepare',3,3,2,2), flip=rc('prepare',3,3,1,1), last=rc('prepare',126*8+3,126*8+3,1,1);
const reversalBad=[
  ['prepare',[3,11,1,15],-2], // same value, fresh epoch differs
  ['prepare',[3,3,4,15],-1], // zero interior digit
  ['prepare',[1024,1024,1,15],-1],['prepare',[3,3,1,-1],-1],['prepare',[3,3,2,9],-3],
  ['prepare',[127*8+3,127*8+3,1,15],-7],['advance',[flip,flip,11,15],-2],
  ['advance',[flip,flip+256,3,15],-6],['advance',[flip,flip,3,0],-3],
  ['verify',[clear,clear,16],-2],['verify',[clear,clear+256,8],-6],
  ['verify',[clear-256*4,clear,8],-4],['verify',[flip+256,flip+256,10],-5],
  ['inverse',[clear,clear,8,2],-3],['inverse',[last,last,127*8+2,15],-7],
  ['undoverify',[clear,clear,8,11,8],-2],['undoverify',[clear,clear,8,19,8],19],
];
for(const [op,args,out] of reversalBad)assert.equal(rc(op,...args),out);
assert.equal(hostCalls,0);
console.log(JSON.stringify({sha256:{planner:planner.sha256,chat:chat.sha256,reversal:reversal.sha256},
  planner:{plannerComparisons,casesRefusedWithoutOutputWrite:gateCorruptors.length,signedRawExtremes:true,
  qualifiedBitsAreTrustBoundary:true},chat:{chatCount,malformedRefused:chatBad.length,statuses:[...statuses].sort()},
  reversal:{reversalRoundTrips,adversarialCases:reversalBad.length},hostImportCalls:hostCalls},null,2));
