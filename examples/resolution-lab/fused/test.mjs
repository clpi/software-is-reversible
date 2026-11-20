import assert from 'node:assert/strict';
import fs from 'node:fs';
const b=fs.readFileSync(new URL('./fused.wasm',import.meta.url));
assert.deepEqual(b,fs.readFileSync(new URL('./repeat.wasm',import.meta.url)));
const m=new WebAssembly.Module(b);
const calls=[];
const moduleImports={wasi_snapshot_preview1:Object.create(null)};
const imports=WebAssembly.Module.imports(m);
for(const x of imports) {
  assert.equal(x.module,'wasi_snapshot_preview1');
  assert.ok(['fd_write','proc_exit','fd_read','args_sizes_get','args_get'].includes(x.name));
  assert.equal(x.kind,'function');
  moduleImports.wasi_snapshot_preview1[x.name]=()=>{calls.push(x.name);throw Error('unexpected WASI call');};
}
const ex=new WebAssembly.Instance(m,moduleImports).exports;
const raw=ex.idol_fused__dominates;
assert.equal(raw.length,11);
assert.throws(()=>raw(31,0n,0n,0n,0n,0n,0n,0n,0n,0n,0n), TypeError);
const oracle=(a,b,mask)=>{
  const selected=[0,1,2,3,4].filter(i=>(mask & (2**i))!==0);
  return selected.every(i=>a[i]<=b[i])&&selected.some(i=>a[i]<b[i]);
};
const inputs=Array.from({length:3**5},(_,k)=>Array.from({length:5},(_,i)=>Math.floor(k/3**i)%3-1));
const args=inputs.map(v=>v.map(BigInt));
let cases=0, held=0, ties=0, yes=0;
for(let mask=1;mask<32;mask++){
 const bit=BigInt(mask);
 for(let l=0;l<inputs.length;l++)for(let r=0;r<inputs.length;r++){
  const got=raw(bit,...args[l],...args[r]);
  const expected=oracle(inputs[l],inputs[r],mask);
  assert.equal(got,expected?1n:0n);
  cases++;if(l===r)ties++;if(expected)yes++;
 }
}
let seed=0x5fca0e;
const rng=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed|0;};
for(let t=0;t<20000;t++){
 const a=[],b=[];
 for(let i=0;i<5;i++){
  a.push(rng());
  b.push(t%5===0?a[i]:rng());
 }
 const mask=1+(rng()>>>0)%31;
 assert.equal(raw(BigInt(mask),...a.map(BigInt),...b.map(BigInt)),oracle(a,b,mask)?1n:0n);held++;
}
const min=-2147483648n,max=2147483647n;
for(let b=0;b<5;b++){
 const a=[0n,0n,0n,0n,0n], z=[0n,0n,0n,0n,0n];a[b]=min;z[b]=max;
 assert.equal(raw(1n<<BigInt(b),...a,...z),1n);
 assert.equal(raw(1n<<BigInt(b),...z,...a),0n);
}
for(const mask of [-2147483648n,-1n,0n,32n,2147483647n])
 assert.equal(raw(mask,0n,0n,0n,0n,0n,0n,0n,0n,0n,0n),-1n);
assert.deepEqual(calls,[]);
console.log(JSON.stringify({cases,syntheticInputAlphabet:[-1,0,1],masks:31,equalVectorCases:ties,strictDominance:yes,heldout32BitCases:held,endpointCalls:10,maskRefusals:5,exports:WebAssembly.Module.exports(m),imports,calledImports:calls},null,2));
