import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const P=path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Z]:)/i,'$1'));
const OUT=decodeURIComponent(P), ROOT=path.resolve(OUT,'../..'), PIANO=path.resolve(ROOT,'../piano');
const accepted=path.join(PIANO,'release/grand-piano-v1.1-rc-candidate');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const dump=(n,x)=>fs.writeFileSync(path.join(OUT,n),JSON.stringify(x,null,2));
const files={};
const grand=read(path.join(PIANO,'V1_1G_GRAND_CANDIDATE_MANIFEST.json'));
for(const f of grand.files){const p=path.join(accepted,f.path);if(sha(p)!==f.sha256)throw Error('FROZEN DRIFT '+p);files[p]=sha(p);}
const upright=read(path.join(PIANO,'04_blender/upright_exterior_master_v1_2b/V1_2B_ACCEPTED_BASELINE_LOCK.json'));
for(const f of upright.sourceMasterFiles){const p=path.join(PIANO,f.path);if(sha(p)!==f.sha256)throw Error('FROZEN DRIFT '+p);files[p]=sha(p);}
for(const name of ['RIGHT_HAND_PRODUCT_BASELINE.json','LEFT_HAND_PRODUCT_BASELINE.json']){
 const ptr=path.join(ROOT,'production_spec',name);files[ptr]=sha(ptr);const j=read(ptr);const a=j.asset;const p=path.join(ROOT,a.path);if(sha(p)!==a.sha256)throw Error('HAND DRIFT');files[p]=sha(p);
 if(j.historical_frozen_fallback){const f=j.historical_frozen_fallback;const p=path.join(ROOT,f.path);if(sha(p)!==f.sha256)throw Error('FALLBACK DRIFT');files[p]=sha(p);}
}
const rel='data/V1_1D_88_KEY_TARGET_MANIFEST.json', js='src/key_performance_layer_v1_1d.js';
for(const f of [rel,js]){const p=path.join(PIANO,'v1_2c0_integration',f);files[p]=sha(p);if(sha(p)!==sha(path.join(accepted,f)))throw Error('C0 NOT IDENTICAL');}
for(const f of ['V1_1G_ACCEPTED_BASELINE_LOCK.json','V1_1G_GRAND_CANDIDATE_MANIFEST.json','V1_2C0_HUMAN_APPROVAL_REPORT.md','CANONICAL_UPRIGHT_ACTION_LATEST_STAGE.json']){const p=path.join(PIANO,f);files[p]=sha(p);}
const manifest=read(path.join(accepted,rel));
const srcMaster=path.join(PIANO,manifest.authority.sourceBlend);files[srcMaster]=sha(srcMaster);
dump('PROTECTED_INPUTS_BEFORE_R1.json',files);
// Execute the approved constructor verbatim except for resolving its vendor import.
const vendor=pathToFileURL(path.join(accepted,'assets/vendor/three/build/three.module.js')).href;
const modulePath=path.join(OUT,'approved_runtime_import_adapter.mjs');
fs.writeFileSync(modulePath,fs.readFileSync(path.join(accepted,js),'utf8').replace("from 'three'",`from '${vendor}'`));
const THREE=await import(vendor);globalThis.fetch=async()=>({ok:true,json:async()=>manifest});
const {createKeyPerformanceLayer}=await import(pathToFileURL(modulePath));
const layer=await createKeyPerformanceLayer({scene:new THREE.Scene(),runtime:{loaded:()=>[]},audio:{snapshot:()=>({sustain:false})}});
layer.root.updateMatrixWorld(true);const keys=[];
for(const [midi,e] of layer.byMidi){
 const meshes=[];e.render.traverse(o=>{if(!o.isMesh)return;const p=o.geometry.attributes.position,vertices=[];for(let i=0;i<p.count;i++)vertices.push(new THREE.Vector3().fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld).toArray());meshes.push({name:o.name,vertices,triangles:Array.from(o.geometry.index.array),profile:o.userData});});
 keys.push({midi,manifest:e.key,meshes});
}
dump('KEYBOARD_RUNTIME_GEOMETRY_R1.json',{keys,constructor_sha256:sha(path.join(accepted,js)),source_manifest_sha256:sha(path.join(accepted,rel)),derivation:'EXECUTED_APPROVED_THREE_CONSTRUCTOR',adapter:'only import resolution changed; no geometry code changes'});
dump('KEYBOARD_AUTHORITY_R1.json',{KEYBOARD_AUTHORITY:'V1_1G_HUMAN_ACCEPTED_FROZEN_GRAND_88_KEY_PERFORMANCE_LAYER / V1_2C0_HUMAN_APPROVED_EQUIVALENT',KEYBOARD_SOURCE_SHA256:sha(path.join(accepted,rel)),runtime_sha256:sha(path.join(accepted,js)),source_master_sha256:sha(srcMaster),source_manifest:path.join(accepted,rel),runtime:path.join(accepted,js),authority_chain:['V1_1G_ACCEPTED_BASELINE_LOCK.json','V1_1G_GRAND_CANDIDATE_MANIFEST.json','V1_2C0_HUMAN_APPROVAL_REPORT.md'],C0_bytes_match_frozen:true,KEY_COUNT:keys.length,approved_unit_scale:manifest.authority.motionScale,excluded:'Current upright mechanism pointer is failed candidate, not keyboard authority.',asset_claim:'Equivalent-scale teaching keyboard; not manufacturer-calibrated metrology.'});
console.log('FROZEN VERIFIED',Object.keys(files).length,'KEYS',keys.length);
