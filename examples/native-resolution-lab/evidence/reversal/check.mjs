import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";

const moduleBytes=readFileSync(new URL("reversal.wasm",import.meta.url));
const reproduced=readFileSync(new URL("reproduce.wasm",import.meta.url));
assert(moduleBytes.equals(reproduced),"compiler commit does not reproduce the artifact");
const wasm=new WebAssembly.Module(moduleBytes);
const imports=WebAssembly.Module.imports(wasm);
let hostCalls=0;
const blocked=function(){hostCalls++; throw Error("no foreign effects permitted");};
const imported={};
for(const {module,name,kind} of imports){
  assert.equal(module,"wasi_snapshot_preview1");
  assert.equal(kind,"function");
  imported[module]??={};
  imported[module][name]=blocked;
}
const e=new WebAssembly.Instance(wasm,imported).exports;
const dial=name=>(...args)=>Number(e["idol_reversal__"+name](...args.map(BigInt)));
const prepare=dial("prepare"), advance=dial("advance"), verify=dial("verify"), inverse=dial("inverse"),
  undoverify=dial("undoverify"), predecessor=dial("predecessor");

function code(ops){return ops.reduceRight((r,v)=>4*r+v,0);}
function frame(epoch,value){return 8*epoch+value;}
function permit(caps,bit){return (caps&bit)!==0;}
function receipt(plan,states,value,epoch){
  const residual=states.reduceRight((acc,b)=>9*acc+b,0);
  return plan+256*residual+1679616*value+13436928*epoch;
}
const actions={
  1:value=>value^1,
  2:()=>0,
  3:value=>parseInt(value.toString(2).padStart(3,"0").replace(/(.)(..)/,"$2$1"),2),
};
function refForward(ops,value,caps){
  const digits=[];
  for(const a of ops){
    if(!permit(caps,1<<(a-1)))return null;
    digits.push(a===2?1+value:0);
    value=actions[a](value);
  }
  return {value,digits};
}
function refInverseAllowed(ops,caps){
  return ops.every(a=>permit(caps,{1:1,2:8,3:4}[a]));
}
function plans(n){
  if(n===0)return [[]];
  return plans(n-1).flatMap(v=>[1,2,3].map(op=>[...v,op]));
}
const catalogue=[1,2,3,4].flatMap(plans);
const legalWire=new Set(catalogue.map(code));
const checks={prepare:0,predecessor:0,advance:0,verify:0,inverse:0,undoverify:0,
  malformedPlan:0,realized:0,inversesRealized:0,adversarial:0};
for(let epoch=0;epoch<128;epoch++) {
  for(let value=0;value<8;value++) {
    const before=frame(epoch,value);
    for(const ops of catalogue) {
      const plan=code(ops), endEpoch=epoch+ops.length;
      for(let caps=0;caps<16;caps++){
        const forward=refForward(ops,value,caps);
        if(endEpoch>127) {
          assert.equal(prepare(before,before,plan,caps),-7);
          checks.prepare++; continue;
        }
        if(forward===null) {
          assert.equal(prepare(before,before,plan,caps),-3);
          checks.prepare++; continue;
        }
        const stamp=receipt(plan,forward.digits,forward.value,epoch), after=frame(endEpoch,forward.value);
        assert.equal(prepare(before,before,plan,caps),stamp);
        checks.prepare++; checks.realized++;
        assert.equal(predecessor(stamp),before);
        checks.predecessor++;
        assert.equal(advance(stamp,stamp,before,caps),after);
        checks.advance++;
        assert.equal(verify(stamp,stamp,after),after);
        checks.verify++;
        // Separate backward capabilities, independent of the forward capability mask.
        const undoCaps=15-caps^(((epoch+value+ops.length)&1)?3:0);
        const backEpoch=endEpoch+ops.length;
        const back=backEpoch>127?-7:refInverseAllowed(ops,undoCaps)?frame(backEpoch,value):-3;
        assert.equal(inverse(stamp,stamp,after,undoCaps),back);
        checks.inverse++;
        if(back>=0){
          assert.equal(undoverify(stamp,stamp,after,back,undoCaps),back);
          checks.inversesRealized++;
        } else {
          assert.equal(undoverify(stamp,stamp,after,after,undoCaps),back);
        }
        checks.undoverify++;
      }
    }
  }
}
for(let p=0;p<=255;p++){
  if(!legalWire.has(p)){assert.equal(prepare(0,0,p,15),-1);checks.malformedPlan++;}
}
const negative=[];
function refuse(label,got,want){
  assert.equal(got,want,label); negative.push({label,observed:got});checks.adversarial++;
}
const stamp=prepare(13,13,2,15), other=prepare(12,12,2,15);
const after=advance(stamp,stamp,13,15), otherAfter=advance(other,other,12,15);
assert.equal(after,otherAfter);
assert.notEqual(stamp,other);
const undone=inverse(stamp,stamp,after,8), otherUndone=inverse(other,other,after,8);
assert.equal(undone%8,5); assert.equal(otherUndone%8,4);
refuse("stale same-value generation",prepare(13,21,2,15),-2);
refuse("stale same-generation value",prepare(13,12,2,15),-2);
refuse("late action forbidden before target",prepare(13,13,code([1,3]),1),-3);
refuse("permission revoked before target",advance(stamp,stamp,13,0),-3);
refuse("stale forward reuse",advance(stamp,stamp,after,15),-2);
refuse("wrong independent observed outcome",verify(stamp,stamp,after+1),-2);
refuse("wrong independent observed undo outcome",undoverify(stamp,stamp,after,undone-1,8),-2);
refuse("no repeated undo after generation advances",inverse(stamp,stamp,undone,8),-2);
refuse("clear grant not a restore grant",inverse(stamp,stamp,after,2),-3);
refuse("stale otherwise valid receipt",inverse(other,stamp,after,8),-6);
refuse("tampered otherwise valid receipt",verify(other,stamp,after),-6);
refuse("missing clear residual",inverse(stamp-6*256,stamp,after,8),-4);
refuse("excess trailing residual",inverse(stamp+9*256,stamp,after,8),-5);
refuse("clear receipt impossible post state",inverse(stamp+1679616,stamp,after,8),-5);
const flipped=prepare(13,13,1,1);
refuse("unexpected residual on bijection",predecessor(flipped+256),-5);
refuse("invalid capability mask",prepare(13,13,2,16),-1);
refuse("bad frame upper limit",prepare(1024,1024,2,15),-1);
refuse("negative frame",prepare(-1,-1,2,15),-1);
refuse("negative wire receipt",verify(-1,-1,0),-1);
refuse("wire upper limit",verify(1719926784,1719926784,0),-1);
refuse("forward generation exhaustion",prepare(1021,1021,1,15),-7);
const lastStamp=prepare(1013,1013,1,15);
const last=advance(lastStamp,lastStamp,1013,15);
assert(last>=1016);
refuse("undo generation exhaustion",inverse(lastStamp,lastStamp,last,15),-7);
assert.equal(hostCalls,0);
const sha=b=>createHash("sha256").update(b).digest("hex");
console.log(JSON.stringify({schema:"idol-reversal-sandbox-receipt/v1",source:"reversal.id",
  source_sha256:sha(readFileSync(new URL("reversal.id",import.meta.url))),
  compiler_sha256:"3ba4c432cea98a0ed63652424f626a1be4c761a8b3c8abcd976f07291953469c",
  compiler_revision:"5efca0e40430de5dfd592f534edf27f32305eb36",wasm_sha256:sha(moduleBytes),
  serial_builds_byte_identical:true,domains:{plans:catalogue.length,stateValues:8,epochs:128,capMasks:16},
  dispatch:"pure target derivation; no device calls, trusted external fresh observation and retained ticket",
  hostImports:imports,hostCalls,checks,negative,clearCollision:{sameAfter:after,
    origins:[13,12],retained:[stamp,other],undo:[undone,otherUndone]}},null,2));
