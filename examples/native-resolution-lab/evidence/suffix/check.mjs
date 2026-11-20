import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const bytes=readFileSync(new URL('suffix.wasm',import.meta.url));
const mod=new WebAssembly.Module(bytes);
const hostCalls=[];
const env={};
for(const {module,name} of WebAssembly.Module.imports(mod))
  (env[module]??={})[name]=()=>{hostCalls.push(name);throw new Error(name);};
const {memory,idol_suffix__page:page}=new WebAssembly.Instance(mod,env).exports;
const ABI=8192, COUNT_SENTINEL=858993459n;
const view=new BigInt64Array(memory.buffer,ABI,6*128+2+32+1);
let returnsChecked=0, witnessCodesCompared=0, protectedCellsChecked=0;
function invoke(rows,root,h,start=0,limit=0,n=rows.length) {
  view.fill(COUNT_SENTINEL);
  for(let i=0;i<rows.length;i++)view.set(rows[i].map(BigInt),i*4);
  // Count/scratch bounds hold for the validated layout. No raw caller pointer
  // is accepted from test cases: this instance owns an aligned fixed arena.
  const status=Number(page(...[ABI,n,root,h,start,limit].map(BigInt)));
  const scratch=view.slice(rows.length*4);
  assert.deepEqual(Array.from(view.slice(0,rows.length*4)),rows.flat().map(BigInt));
  const endOfOutput=rows.length*6+2+Math.max(0,status);
  if(status===-1)assert(scratch.every(x=>x===COUNT_SENTINEL),'invalid input mutated scratch');
  else assert(view.slice(endOfOutput).every(x=>x===COUNT_SENTINEL),'write beyond returned page');
  protectedCellsChecked+=scratch.length;
  returnsChecked++;
  return {status,lower:Number(view[rows.length*6]),upper:Number(view[rows.length*6+1]),
          codes:Array.from(view.slice(rows.length*6+2,endOfOutput),Number)};
}

class SuffixFixture {
  constructor(h) {
    this.h=h;
    this.rows=[];
    this.keys=new Map();
    this.full=[0];
    for(let d=1;d<=h;d++)this.full.push(this.row([d,this.full[d-1],this.full[d-1],1]));
    this.root=this.full[h];
  }
  row(r) {
    const key=r.join(',');
    if(!this.keys.has(key)){this.rows.push(r);this.keys.set(key,this.rows.length);}
    return this.keys.get(key);
  }
  patch(prefix,input,newKid) {
    const walk=(at,suffix)=>{
      const row=this.rows[at-1].slice();
      if(suffix.length===0)row[input]=newKid;
      else {
        const index=suffix[0]==='0'?1:2;
        row[index]=walk(row[index],suffix.slice(1));
      }
      return this.row(row);
    };
    this.root=walk(this.root,prefix);
  }
  minimalReachable() {
    const out=[],map=new Map();
    const reindex=at=>{
      if(at<=0)return at;
      if(map.has(at))return map.get(at);
      const [d,z,o,e]=this.rows[at-1];
      const row=[d,reindex(z),reindex(o),e];
      out.push(row);
      map.set(at,out.length);
      return out.length;
    };
    return {rows:out,root:reindex(this.root)};
  }
}

// Independently expand complete witness paths for small fixtures only.
function oracle(rows,root) {
  function walk(node,code) {
    if(node===0)return [];
    const [,z,o,e]=rows[node-1];
    assert(z>=0&&o>=0&&e>=0);
    return walk(z,code*2).concat(walk(o,code*2+1),e?[code]:[]);
  }
  return walk(root,1);
}
function checkExact(rows,root,depth,pageSpec) {
  const expected=oracle(rows,root);
  for(const [start,limit] of pageSpec(expected.length)) {
    const observed=invoke(rows,root,depth,start,limit);
    const codes=expected.slice(start,start+limit);
    assert.deepEqual(observed,{status:codes.length,lower:expected.length,upper:expected.length,codes});
    witnessCodesCompared+=codes.length;
  }
  return expected.length;
}

const reproduced=[];
for(const [patch,count] of [[null,4095],['000000',4064],['0',3072],['1111111111',4094]]){
  const f=new SuffixFixture(12);
  if(patch!==null)f.patch(patch,2,0);
  const {rows,root}=f.minimalReachable();
  const total=checkExact(rows,root,12,n=>[[0,0],[0,32],[511,13],[n-10,32],[n,18]]);
  assert.equal(total,count);
  reproduced.push({removedOneChildAt:patch,distinctRealizations:total,suffixClasses:rows.length});
}

let seed=0x51ffabcd;
function next(){seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return seed>>>0;}
let randomDags=0,randomPages=0;
for(let k=0;k<384;k++){
  const h=1+(next()%8), rows=[];
  let recent=[];
  for(let d=1;d<=h;d++){
    const current=[];
    for(let j=0;j<1+(next()%4);j++){
      const pick=()=>recent.length?([0,...recent][next()%(recent.length+1)]):0;
      rows.push([d,pick(),pick(),next()%2]);
      current.push(rows.length);
    }
    recent=current;
  }
  const root=recent[recent.length-1];
  checkExact(rows,root,h,n=>{
    const specs=[[0,0],[0,7],[n===0?0:next()%n,1+(next()%32)],[n,32]];
    randomPages+=specs.length;
    return specs;
  });
  randomDags++;
}

const huge=new SuffixFixture(30);
const high=1073741823;
const atStart=invoke(huge.rows,huge.root,30,0,1);
const atEnd=invoke(huge.rows,huge.root,30,high-4,8);
assert.deepEqual(atStart,{status:1,lower:high,upper:high,codes:[2**29]});
assert.deepEqual(atEnd,{status:4,lower:high,upper:high,codes:[15,7,3,1]});
assert.equal(invoke(huge.rows,huge.root,30,high+1,8).status,-1);
const exactShort=new SuffixFixture(3);
assert.equal(invoke(exactShort.rows,exactShort.root,3,8,4).status,-3);

const unknownA=[[1,0,0,1],[2,1,-1,-1]];
const unknownB=[[1,0,0,0],[2,-1,0,1],[3,2,2,0]];
assert.deepEqual(invoke(unknownA,2,2),{status:0,lower:1,upper:3,codes:[]});
assert.deepEqual(invoke(unknownA,2,2,0,8),{status:-2,lower:1,upper:3,codes:[]});
assert.deepEqual(invoke(unknownB,3,3,0,8),{status:-2,lower:2,upper:4,codes:[]});

const malformed=[
  [[[1,0,0,1]],1,1,0,0,0],
  [[[1,0,0,1]],1,1,0,0,129],
  [[[1,0,0,1]],0,1,0,0],
  [[[1,0,0,1]],2,1,0,0],
  [[[1,0,0,1]],1,2,0,0],
  [[[1,0,0,1]],1,31,0,0],
  [[[0,0,0,1]],1,1,0,0],
  [[[1,1,0,1]],1,1,0,0],
  [[[1,-1,0,1]],1,1,0,0],
  [[[1,0,0,2]],1,1,0,0],
  [[[1,0,0,-2]],1,1,0,0],
  [[[1,0,0,1],[2,-2,1,0]],2,2,0,0],
  [[[1,0,0,1],[3,1,0,0]],2,3,0,0],
  [[[1,0,0,1]],1,1,-1,1],
  [[[1,0,0,1]],1,1,0,33],
  [[[1,0,0,1]],1,1,1,0],
  [[[1,0,0,1]],1,1,0,-1],
];
for(const x of malformed)assert.equal(invoke(...x).status,-1);
assert.equal(hostCalls.length,0);
console.log(JSON.stringify({
  scope:'synthetic exact first-EOS support only; no neural execution or MAP in this module',
  reproduced,largeCase:{states:huge.rows.length,support:high,first:atStart.codes,lastFour:atEnd.codes},
  unknownCases:[{lower:1,upper:3},{lower:2,upper:4}],
  randomDags,randomPages,witnessCodesCompared,returnsChecked,protectedCellsChecked,
  malformedRefused:malformed.length,hostImportCalls:hostCalls.length,
  exports:WebAssembly.Module.exports(mod),wasmSHA256:createHash('sha256').update(bytes).digest('hex'),
},null,2));
