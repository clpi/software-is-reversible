import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const bytes=readFileSync(new URL('chat.wasm',import.meta.url));
const mod=new WebAssembly.Module(bytes);
const imp=WebAssembly.Module.imports(mod), exp=WebAssembly.Module.exports(mod);
const calls=[];
const env={};
for(const {module,name} of imp)(env[module]??={})[name]=()=>{calls.push(name);throw Error('unexpected import '+name);};
const kernel=new WebAssembly.Instance(mod,env).exports.idol_chat__decision;
const lanes=[[0,3],[3,4],[7,7],[14,13],[27,7],[34,13],[47,4],[51,4]];
const word=(a,b,z)=>a+4*b+16*z;
const row=w=>w===-1?null:[w%4,Math.floor(w/4)%4,Math.floor(w/16)];
const fractionEq=(n,d,N,D)=>BigInt(n)*D===N*BigInt(d);
const cmp=(a,b)=>a[0]*b[1]<b[0]*a[1]?-1:a[0]*b[1]>b[0]*a[1]?1:0;
const rank=toks=>toks.map(String).join('');
const bits=toks=>parseInt('1'+toks.map(String).join(''),2);
function oracle(values) {
  const [root,left,right,min,horizon]=values, vars=[row(left),row(right)];
  const endings=[], bound=[0n,1n], blockers=[];
  let known=0;
  const walk=(r,prior,path)=>{
    if(r===null){blockers.push(prior);return;}
    known++;
    const denom=BigInt(r.reduce((a,b)=>a+b));
    if(r[2]&&path.length+1>=min)endings.push({p:[...path,2],f:[prior[0]*BigInt(r[2]),prior[1]*denom]});
    if(path.length+1<horizon)for(const t of [0,1]) {
      if(r[t])walk(vars[t],[prior[0]*BigInt(r[t]),prior[1]*denom],[...path,t]);
    }
  };
  walk(row(root),[1n,1n],[]);
  endings.sort((a,b)=>cmp(b.f,a.f)||(rank(a.p)<rank(b.p)?-1:rank(a.p)>rank(b.p)?1:0));
  for(const f of blockers)if(cmp(f,bound)>0){bound[0]=f[0];bound[1]=f[1];}
  const best=endings[0];
  const score=best?.f??[0n,1n];
  const status=!best?(blockers.length?0:4):cmp(score,bound)<0?1:cmp(score,bound)===0?2:3;
  return {status,code:best?bits(best.p.slice(0,-1)):0,lower:score,
    upper:cmp(score,bound)>0?score:bound,known,unknown:blockers.length};
}
const statusCounts=[0,0,0,0,0];
let fixtures=0, scalarControl=0;
const cases=[];
function test(inp,scalar=false) {
  const in64=inp.map(BigInt);
  const packed=kernel(...in64,8n);
  assert(packed>=0n&&packed<1n<<55n);
  const actual=lanes.map(([s,n])=>Number(packed>>BigInt(s)&((1n<<BigInt(n))-1n)));
  const ref=oracle(inp);
  assert.deepEqual([actual[0],actual[1],actual[6],actual[7]],
                   [ref.status,ref.code,ref.known,ref.unknown],String(inp));
  assert(fractionEq(actual[2],actual[3],...ref.lower),'lower '+inp);
  assert(fractionEq(actual[4],actual[5],...ref.upper),'upper '+inp);
  statusCounts[actual[0]]++;
  if(scalar){
    const fields=Array.from({length:8},(_,j)=>Number(kernel(...in64,BigInt(j))));
    assert.deepEqual(fields,actual);
    scalarControl+=8;
    cases.push({rows:inp.slice(0,3),minStop:inp[3],horizon:inp[4],fields});
  }
  fixtures++;
}
for(const inp of [
  [word(3,0,2),word(1,0,3),word(2,2,3),1,3],
  [word(1,1,0),word(0,0,1),word(0,0,1),1,3],
  [word(1,1,1),word(1,1,1),word(1,1,1),2,4],
  [word(0,1,1),-1,-1,1,4],
  [word(0,2,1),-1,-1,1,4],
  [word(0,1,0),-1,-1,1,4],
  [word(0,1,0),word(1,0,0),word(0,1,0),1,4],
  [word(0,1,0),-1,-1,1,1],
  [word(0,0,1),-1,-1,1,4],
  [word(3,3,3),word(3,3,3),word(3,3,3),4,4],
])test(inp,true);
const reps=[-1,word(1,0,0),word(0,1,0),word(0,0,1),word(1,1,1),word(2,2,2),word(3,3,3),word(0,3,2)];
for(const r of reps)for(const a of reps)for(const b of reps)
  for(let h=1;h<=4;h++)for(let m=1;m<=h;m++)test([r,a,b,m,h]);
for(let r=1;r<=63;r++)for(const a of reps)
  for(let h=1;h<=4;h++)for(let m=1;m<=h;m++)test([r,a,64-r,m,h]);
let seed=0x22dec011;
function next(){seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return seed>>>0;}
const valid=[-1,...Array.from({length:63},(_,i)=>i+1)];
for(let i=0;i<8192;i++){
  const values=[0,0,0].map(()=>valid[next()%64]);
  const h=1+next()%4,m=1+next()%h;
  test([...values,m,h]);
}
const refusals=[[0,21,21,1,4,8],[64,21,21,1,4,8],[-2,21,21,1,4,8],[21,0,21,1,4,8],
 [21,21,0,1,4,8],[21,21,21,0,4,8],[21,21,21,3,2,8],[21,21,21,1,5,8],
 [21,21,21,1,4,-1],[21,21,21,1,4,9],[1n<<61n,21,21,1,4,8],
 [21,21,21,1n<<61n,4,8],[21,21,21,1,4,1n<<61n]];
for(const p of refusals)assert.equal(kernel(...p.map(BigInt)),-1n);
assert.equal(calls.length,0);
assert(statusCounts.every(c=>c>0));
console.log(JSON.stringify({qualifier:'finite modeled last-token tensor; no model inference',
 exactOracleFixtures:fixtures,scalarVsPackedFields:scalarControl,statusCounts,
 refusalCount:refusals.length,hostImportCalls:calls.length,abi:{import:imp,export:exp},
 wasmSHA256:createHash('sha256').update(bytes).digest('hex'),cases},null,2));
