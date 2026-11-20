const sha='10b532aba971dfde38292b7e04aaf133b5f1f77c1e098ce926a8a291a8ba1544';
export async function loadFused(bytes) {
  if(!bytes){
    const r=await fetch(new URL('./fused/fused.wasm',import.meta.url));
    if(!r.ok)throw new Error('Fused Wasm unavailable');
    bytes=await r.arrayBuffer();
  }
  const actual=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(actual!==sha)throw new Error('Fused Wasm digest mismatch');
  const mod=await WebAssembly.compile(bytes);
  const approved=['fd_write','proc_exit','fd_read','args_sizes_get','args_get'];
  const stubs=Object.create(null);
  for(const i of WebAssembly.Module.imports(mod)){
    if(i.module!=='wasi_snapshot_preview1'||i.kind!=='function'||!approved.includes(i.name))throw new Error('Unapproved import');
    stubs[i.name]=()=>{throw new Error('WASI unavailable in demo sandbox');};
  }
  const result=await WebAssembly.instantiate(mod,{wasi_snapshot_preview1:stubs});
  const f=result.exports.idol_fused__dominates;
  if(typeof f!=='function')throw new Error('Missing native dominance export');
  const box=v=>{if(!Number.isInteger(v)||v< -2147483648||v>2147483647)throw new Error('Outside signed i32');return BigInt(v);};
  return (mask,a,b)=>{
    if(!Number.isInteger(mask)||mask<1||mask>31||a.length!==5||b.length!==5)throw new Error('Invalid projection');
    const ok=f(BigInt(mask),...Array.from(a,box),...Array.from(b,box));
    if(ok!==0n&&ok!==1n)throw new Error('Invalid native verdict');
    return ok===1n;
  };
}
