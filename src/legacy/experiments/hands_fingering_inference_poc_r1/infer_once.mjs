import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {performance} from 'node:perf_hooks';
import {createRequire} from 'node:module';
import * as ort from 'onnxruntime-node';
import {predictFingerings} from '@lumikey/piano-fingering-model';
import {loadModels} from '@lumikey/piano-fingering-model/node';
const require=createRequire(import.meta.url);
const out=path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1'));
const here=path.dirname(require.resolve('./package.json'));
const read=n=>JSON.parse(fs.readFileSync(path.join(here,n),'utf8').replace(/^\uFEFF/,''));
const write=(n,x)=>fs.writeFileSync(path.join(here,n),JSON.stringify(x,null,2)+'\n',{flag:'wx'});
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if(fs.existsSync(path.join(here,'RAW_MODEL_PREDICTIONS.json')))throw Error('Official inference already exists; no rerun permitted');
const notes=read('MODEL_INPUT_UNCONSTRAINED.json');
if(notes.length!==23||notes.some(n=>Object.hasOwn(n,'finger')))throw Error('Invalid unconstrained input');
const before=JSON.stringify(notes);
const runtime={task:'PIANO_AUTOMATIC_FINGERING_INFERENCE_POC_R1',started_utc:new Date().toISOString(),node:process.version,platform:process.platform,arch:process.arch,os:os.version(),cpu:os.cpus()[0].model,logical_cpu_count:os.cpus().length,onnxruntime_node:read('node_modules/onnxruntime-node/package.json').version,onnxruntime_common:read('node_modules/onnxruntime-common/package.json').version,official_predict_calls:0,python_fallback:false};
const traces=[];let models;
try{
 // Keep official loadModels() and enforce CPU by supplying only CPU in its session factory.
 // This changes session initialization options only, never preprocessing, weights or predictions.
 const common=require('onnxruntime-common');
 const factory=common.InferenceSession.create; let sessionId=0;
 common.InferenceSession.create=async function(buffer,options){return factory.call(this,buffer,{...options,executionProviders:['cpu'],enableProfiling:true,profileFilePrefix:path.join(here,'onnxruntime_profile_'+(++sessionId))});};
 const startLoad=performance.now();
 try{models=await loadModels();}finally{common.InferenceSession.create=factory;}
 runtime.model_load_ms=performance.now()-startLoad;
 runtime.execution_providers_requested=['cpu'];
 runtime.session_metadata=Object.fromEntries(Object.entries(models).map(([h,m])=>[h,{inputNames:m.inputNames,outputNames:m.outputNames}]));
 const wrapped={};
 for(const [hand,session] of Object.entries(models)){
  wrapped[hand]={run:async inputs=>{
   const t=performance.now();const result=await session.run(inputs);
   traces.push({hand,hand_note_index:traces.filter(x=>x.hand===hand).length,input_shape:inputs.tokens.dims,input_tokens:Array.from(inputs.tokens.data),logits:Array.from(result.logits.data),run_ms:performance.now()-t});
   return result;
  }};
 }
 const startPredict=performance.now();runtime.official_predict_calls=1;
 const raw=await predictFingerings(notes,wrapped);
 runtime.predict_ms=performance.now()-startPredict;
 // Save the direct return array immediately, with no reordering, IDs or edits added.
 write('RAW_MODEL_PREDICTIONS.json',raw);
 write('RAW_ONNX_LOGITS_AND_TOKENS.json',traces);
 runtime.raw_output_sha256=sha(path.join(here,'RAW_MODEL_PREDICTIONS.json'));
 runtime.input_unchanged=before===JSON.stringify(notes);
 runtime.output_count=raw.length;runtime.onnx_session_run_count=traces.length;
 runtime.invalid_finger_count=raw.filter(n=>!Number.isInteger(n.finger)||n.finger<1||n.finger>5).length;
 runtime.exception=null;
 console.log(JSON.stringify({runtime,predictions:raw}));
}catch(e){runtime.exception={name:e.name,message:e.message,stack:e.stack};console.error(e);process.exitCode=1;}
finally{
 if(models)for(const m of Object.values(models)){try{await m.endProfiling();await m.release();}catch(e){runtime.cleanup_exception=String(e);}}
 runtime.finished_utc=new Date().toISOString();write('INFERENCE_RUNTIME_RECEIPT.json',runtime);
}


