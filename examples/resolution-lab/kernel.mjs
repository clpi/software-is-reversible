const sha='3806bcd211f200fe976732c2ddedd7e8304e2d034021dabe0610058d0555335e';
export async function loadKernel(bytes) {
  if(!bytes) {
    const r=await fetch(new URL('./native/kernel.wasm',import.meta.url));
    if(!r.ok)throw new Error('Wasm unavailable');
    bytes=await r.arrayBuffer();
  }
  const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(digest!==sha)throw new Error('Wasm digest mismatch');
  const module=await WebAssembly.compile(bytes);
  const allowed=new Set(['fd_write','proc_exit','fd_read','args_sizes_get','args_get']);
  const stubs=Object.create(null);
  for(const item of WebAssembly.Module.imports(module)){
    if(item.module!=='wasi_snapshot_preview1'||item.kind!=='function'||!allowed.has(item.name))throw new Error('Unapproved Wasm import');
    stubs[item.name]=()=>{throw new Error('WASI unavailable in demo sandbox');};
  }
  const {exports}=await WebAssembly.instantiate(module,{wasi_snapshot_preview1:stubs});
  const bind=name=>{
    const f=exports['idol_kernel__'+name];
    if(typeof f!=='function')throw new Error('Missing Idol export');
    return (...args)=>Number(f(...args.map(x=>{
      if(!Number.isInteger(x)||x< -2147483648||x>2147483647)throw new Error('Outside signed i32');
      return BigInt(x);
    })));
  };
  return Object.freeze({flip:bind('flip'),clear:bind('clear'),compare:bind('compare')});
}
