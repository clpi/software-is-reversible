import assert from "node:assert/strict";
import fs from "node:fs";
import crypto from "node:crypto";

const first=fs.readFileSync(new URL("./kernel.wasm",import.meta.url));
const second=fs.readFileSync(new URL("./reproduce.wasm",import.meta.url));
assert.deepEqual(first,second);
assert.equal(WebAssembly.validate(first),true);
const module=new WebAssembly.Module(first);
const declarations=WebAssembly.Module.imports(module);
assert.deepEqual(declarations.map(x=>[x.module,x.name,x.kind]),[
 ["wasi_snapshot_preview1","fd_write","function"],["wasi_snapshot_preview1","proc_exit","function"],
 ["wasi_snapshot_preview1","fd_read","function"],["wasi_snapshot_preview1","args_sizes_get","function"],
 ["wasi_snapshot_preview1","args_get","function"]]);
const imports={wasi_snapshot_preview1:Object.create(null)};
const hostCalls=[];
for (const {name} of declarations) imports.wasi_snapshot_preview1[name]=()=>{hostCalls.push(name);throw Error("WASI unavailable");};
const instance=new WebAssembly.Instance(module,imports);
const {idol_kernel__flip:flip,idol_kernel__clear:clear,idol_kernel__compare:compare}=instance.exports;
assert.deepEqual(WebAssembly.Module.exports(module).map(x=>[x.name,x.kind]),[
 ["memory","memory"],["idol_kernel__flip","function"],["idol_kernel__clear","function"],["idol_kernel__compare","function"]]);
assert.throws(()=>flip(0),TypeError);
const states=[...Array(8).keys()].map(BigInt);
const signed=[-2147483648n,-2147483647n,...Array.from({length:65},(_,i)=>BigInt(i-32)),2147483646n,2147483647n];
const truth=(a,b)=>a===b?0n:a<b?-1n:1n;
const table=states.map(x=>({input:Number(x),flip:Number(flip(x)),clear:Number(clear(x))}));
for (const x of states) {
  assert.equal(flip(x),x^1n);
  assert.equal(clear(x),0n);
  assert.equal(flip(flip(x)),x);
}
assert.equal(new Set(table.map(x=>x.flip)).size,8);
assert.equal(new Set(table.map(x=>x.clear)).size,1);
for (const x of [-2147483648n,-1n,8n,2147483647n]) {
 assert.equal(flip(x),-1n);assert.equal(clear(x),-1n);
}
for (const a of signed) for (const b of signed) assert.equal(compare(a,b),truth(a,b));
assert.deepEqual(hostCalls,[]);
const digest=b=>crypto.createHash("sha256").update(b).digest("hex");
console.log(JSON.stringify({engine:{node:process.version,v8:process.versions.v8},sourceSha256:digest(fs.readFileSync(new URL("./kernel.id",import.meta.url))),compilerRevision:"5efca0e40430de5dfd592f534edf27f32305eb36",artifact:{bytes:first.length,sha256:digest(first),secondBuildEqual:true},declaredImports:declarations,calledImports:hostCalls,abi:WebAssembly.Module.exports(module),observations:{table,flipInvolutionCases:8,refusalCalls:8,comparePairs:signed.length**2},evidence:"bounded Node/V8 execution of actual Idol-generated Wasm; no browser navigation or current-main compiler claim"},null,2));
