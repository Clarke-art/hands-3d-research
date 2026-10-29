import * as THREE from 'file:///D:/codex%20one/3D%20interactive%20components/piano/release/grand-piano-v1.1-rc-candidate/assets/vendor/three/build/three.module.js';

const KEY_RENDER_NAMES = new Set(['GP_KEYBOARD_GEO_MAT_G5A6_WHITE', 'GP_KEYBOARD_GEO_MAT_G5A6_BLACK']);
const EXTERIOR_PEDAL_MESH = 'GP_PEDALS_GEO_MAT_GP_PEDAL_METAL';
const MODEL_METRES_PER_UNIT = ((2.75 / 5.1997) + (1.60 / 2.983743)) * 0.5;
const PEDAL_FRONT_TRAVEL_SCENE = 0.010 / MODEL_METRES_PER_UNIT;
const PEDAL_LOCAL_PIVOT = Object.freeze({ x: .16, y: .314, z: -.276 });
const PEDAL_FRONT_Z = .222;
const PEDAL_PRESS_ANGLE = Math.asin(PEDAL_FRONT_TRAVEL_SCENE / (PEDAL_FRONT_Z - PEDAL_LOCAL_PIVOT.z));
const ease = (current, target, amount) => current + (target - current) * amount;
const PEDAL_LAYOUT = Object.freeze([
  { id: 'UNA_CORDA', x: -.16, minX: -Infinity, maxX: -.08 },
  { id: 'SOSTENUTO', x: 0, minX: -.08, maxX: .08 },
  { id: 'SUSTAIN', x: .16, minX: .08, maxX: Infinity },
]);

export async function createKeyPerformanceLayer({ scene, camera, renderer, controls, runtime, audio, materials = null, manifestUrl = './data/V1_1D_88_KEY_TARGET_MANIFEST.json' }) {
  const response = await fetch(manifestUrl);
  if (!response.ok) throw new Error(`88-key manifest HTTP ${response.status}`);
  const manifest = await response.json();
  if (manifest.status !== 'PASS' || manifest.keys?.length !== 88) throw new Error('88-key target manifest failed validation');

  const root = new THREE.Group();
  root.name = 'GP_V11D_88_KEY_PERFORMANCE_LAYER';
  root.visible = false;
  scene.add(root);
  const renderRoot = new THREE.Group(); renderRoot.name = 'GP_V11D_KEY_RENDER_ROOT'; root.add(renderRoot);
  const hitRoot = new THREE.Group(); hitRoot.name = 'GP_V11D_KEY_HIT_ROOT'; root.add(hitRoot);
  const pedalRoot = new THREE.Group(); pedalRoot.name = 'GP_V11D_SUSTAIN_PEDAL_ROOT'; root.add(pedalRoot);

  const whiteMaterial = materials?.WHITE_KEY || new THREE.MeshStandardMaterial({ color: 0xeee9df, roughness: .44, metalness: 0 });
  const blackMaterial = materials?.BLACK_KEY || new THREE.MeshStandardMaterial({ color: 0x101519, roughness: .32, metalness: .06 });
  const invisible = new THREE.MeshBasicMaterial({ transparent: true, opacity: 0, colorWrite: false, depthWrite: false });
  const raycaster = new THREE.Raycaster();
  const ndc = new THREE.Vector2();
  const byMidi = new Map();
  const keyHitTargets = [];
  const pedalHitTargets = [];
  const captures = new Map();
  const pedalBindings = new Map();
  const pedalAngles = new Map(PEDAL_LAYOUT.map(pedal => [pedal.id, 0]));
  const pedalTargetAngles = new Map(PEDAL_LAYOUT.map(pedal => [pedal.id, 0]));
  const pedalOwners = new Map(PEDAL_LAYOUT.map(pedal => [pedal.id, new Set()]));
  let focus = false;

  function whiteKeyRender(key, material) {
    const [minX, minY, minZ] = key.worldBounds.min;
    const [maxX, maxY, maxZ] = key.worldBounds.max;
    const pivotX = (minX + maxX) * .5;
    const height = maxY - minY;
    const overlappingBlack = manifest.keys.filter(candidate => candidate.color === 'BLACK'
      && candidate.worldBounds.max[0] > minX && candidate.worldBounds.min[0] < maxX);
    if (!overlappingBlack.length) {
      const mesh = new THREE.Mesh(new THREE.BoxGeometry(maxX - minX, height, maxZ - minZ), material);
      mesh.name = key.renderTarget;
      mesh.position.z = (maxZ - minZ) * .5;
      mesh.castShadow = false; mesh.receiveShadow = true;
      mesh.userData = { profile: 'WHITE_KEY_FULL_WIDTH_NO_ADJACENT_BLACK' };
      return mesh;
    }
    const splitZ = Math.max(...overlappingBlack.map(candidate => candidate.worldBounds.max[2]));
    let rearMinX = minX, rearMaxX = maxX;
    for (const black of overlappingBlack) {
      const blackCenter = (black.worldBounds.min[0] + black.worldBounds.max[0]) * .5;
      if (blackCenter < pivotX) rearMinX = Math.max(rearMinX, black.worldBounds.max[0]);
      else rearMaxX = Math.min(rearMaxX, black.worldBounds.min[0]);
    }
    const group = new THREE.Group();
    group.name = key.renderTarget;
    const front = new THREE.Mesh(new THREE.BoxGeometry(maxX - minX, height, maxZ - splitZ), material);
    front.name = `${key.renderTarget}_FRONT`;
    front.position.set(0, 0, (splitZ + maxZ) * .5 - minZ);
    const rear = new THREE.Mesh(new THREE.BoxGeometry(rearMaxX - rearMinX, height, splitZ - minZ), material);
    rear.name = `${key.renderTarget}_REAR_NOTCHED`;
    rear.position.set((rearMinX + rearMaxX) * .5 - pivotX, 0, (splitZ - minZ) * .5);
    for (const mesh of [front, rear]) { mesh.castShadow = false; mesh.receiveShadow = true; group.add(mesh); }
    group.userData = { profile: 'WHITE_KEY_NOTCHED_FROM_LOCKED_BLACK_BOUNDS', rearMinX, rearMaxX, splitZ };
    return group;
  }

  for (const key of manifest.keys) {
    const [minX, minY, minZ] = key.worldBounds.min;
    const [maxX, maxY, maxZ] = key.worldBounds.max;
    const width = maxX - minX, height = maxY - minY, depth = maxZ - minZ;
    const pivot = new THREE.Group();
    pivot.name = key.keyId;
    pivot.position.fromArray(key.pivot.world);
    pivot.userData = { midi: key.midi, color: key.color, restAngle: 0, pressedAngle: key.pressedTransform.rotationRad[0], targetAngle: 0, owners: new Set() };
    const render = key.color === 'WHITE'
      ? whiteKeyRender(key, whiteMaterial)
      : new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), blackMaterial);
    if (key.color === 'BLACK') {
      render.name = key.renderTarget;
      render.position.z = depth / 2;
      render.castShadow = false;
      render.receiveShadow = true;
    }
    pivot.add(render);
    renderRoot.add(pivot);

    const hitGeometry = new THREE.BoxGeometry(width * (key.color === 'BLACK' ? 1.08 : .98), height + .016, depth * .995);
    const hit = new THREE.Mesh(hitGeometry, invisible);
    hit.name = key.hitTarget;
    hit.position.copy(pivot.position);
    hit.position.z += depth / 2;
    hit.userData = { kind: 'PIANO_KEY', midi: key.midi, color: key.color, keyId: key.keyId, productionReady: true };
    // Raycaster intersects explicit targets even when they are not submitted to WebGL.
    // Keeping hit geometry non-rendered avoids 88 otherwise-empty draw calls.
    hit.visible = false;
    hit.renderOrder = key.color === 'BLACK' ? 20 : 10;
    hitRoot.add(hit);
    keyHitTargets.push(hit);
    byMidi.set(key.midi, { key, pivot, render, hit });
  }

  // Interaction stays in the V1.1D layer, but learner-visible geometry is the
  // approved normal three-pedal assembly. No fourth/duplicate pedal is rendered.
  const pedalHits = new Map();
  for (const pedal of PEDAL_LAYOUT) {
    const hit = new THREE.Mesh(new THREE.BoxGeometry(.14, .12, .30), invisible);
    hit.name = pedal.id === 'SUSTAIN' ? 'GP_V11D_SUSTAIN_PEDAL_HIT' : `GP_V11F_${pedal.id}_PEDAL_HIT`;
    hit.position.set(pedal.x, .295, .10);
    hit.userData = {
      kind: 'EXTERIOR_PEDAL', pedalId: pedal.id, componentId: 'GP_PEDALS',
      productionReady: true, visualAuthority: EXTERIOR_PEDAL_MESH,
    };
    hit.visible = false;
    pedalRoot.add(hit);
    pedalHitTargets.push(hit);
    pedalHits.set(pedal.id, hit);
  }
  // Keep the V1.1D named sustain hit target as a compatibility authority.
  const pedalHit = pedalHits.get('SUSTAIN');
  pedalHit.visible = false;

  const keyboardBox = new THREE.Box3().setFromObject(renderRoot);

  function exteriorPedalMeshes() {
    const found = [];
    for (const level of runtime.loaded()) {
      for (const object of runtime.objectsOf('GP_PEDALS', level)) {
        object.traverse?.(child => { if (child.isMesh && child.name === EXTERIOR_PEDAL_MESH && !found.includes(child)) found.push(child); });
      }
    }
    return found;
  }

  function bindExteriorPedal(mesh) {
    if (pedalBindings.has(mesh)) return pedalBindings.get(mesh);
    mesh.geometry = mesh.geometry.clone();
    const position = mesh.geometry.attributes.position;
    const normal = mesh.geometry.attributes.normal;
    const binding = {
      mesh,
      position,
      normal,
      basePosition: new Float32Array(position.array),
      baseNormal: normal ? new Float32Array(normal.array) : null,
      selectedByPedal: new Map(PEDAL_LAYOUT.map(pedal => [pedal.id, new Uint8Array(position.count)])),
    };
    for (let index = 0; index < position.count; index += 1) {
      const offset = index * 3;
      const x = binding.basePosition[offset], y = binding.basePosition[offset + 1];
      // The approved metal mesh is fused, so the three authored lever/shoe
      // regions are selected by their stable local X ranges below the rod field.
      for (const pedal of PEDAL_LAYOUT) {
        binding.selectedByPedal.get(pedal.id)[index] = x > pedal.minX && x <= pedal.maxX && y < .34 ? 1 : 0;
      }
    }
    mesh.geometry.attributes.position.setUsage(THREE.DynamicDrawUsage);
    if (normal) normal.setUsage(THREE.DynamicDrawUsage);
    pedalBindings.set(mesh, binding);
    return binding;
  }

  function applyPedalAngles(binding) {
    for (let index = 0; index < binding.position.count; index += 1) {
      const offset = index * 3;
      const x = binding.basePosition[offset], y = binding.basePosition[offset + 1], z = binding.basePosition[offset + 2];
      const pedal = PEDAL_LAYOUT.find(item => binding.selectedByPedal.get(item.id)[index]);
      if (!pedal) { binding.position.setXYZ(index, x, y, z); if (binding.normal) binding.normal.setXYZ(index, binding.baseNormal[offset], binding.baseNormal[offset + 1], binding.baseNormal[offset + 2]); continue; }
      const angle = pedalAngles.get(pedal.id) || 0;
      const cos = Math.cos(angle), sin = Math.sin(angle);
      const dy = y - PEDAL_LOCAL_PIVOT.y, dz = z - PEDAL_LOCAL_PIVOT.z;
      binding.position.setXYZ(index, x, PEDAL_LOCAL_PIVOT.y + dy * cos - dz * sin, PEDAL_LOCAL_PIVOT.z + dy * sin + dz * cos);
      if (binding.normal) {
        const nx = binding.baseNormal[offset], ny = binding.baseNormal[offset + 1], nz = binding.baseNormal[offset + 2];
        binding.normal.setXYZ(index, nx, ny * cos - nz * sin, ny * sin + nz * cos);
      }
    }
    binding.position.needsUpdate = true;
    if (binding.normal) binding.normal.needsUpdate = true;
    binding.mesh.geometry.computeBoundingBox();
    binding.mesh.geometry.computeBoundingSphere();
  }

  function fusedMeshes() {
    const found = [];
    for (const level of runtime.loaded()) for (const object of runtime.objectsOf('GP_KEYBOARD', level)) if (KEY_RENDER_NAMES.has(object.name)) found.push(object);
    return found;
  }

  function syncVisibility() {
    root.visible = focus;
    for (const mesh of fusedMeshes()) mesh.visible = !focus && runtime.active === mesh.userData?.level || !focus;
  }

  function setFocus(on) {
    focus = !!on;
    syncVisibility();
    if (!focus) releaseAll('focus-exit');
    return focus;
  }

  function pick(clientX, clientY) {
    if (!focus) return null;
    const rect = renderer.domElement.getBoundingClientRect();
    ndc.set(((clientX - rect.left) / rect.width) * 2 - 1, -((clientY - rect.top) / rect.height) * 2 + 1);
    raycaster.setFromCamera(ndc, camera);
    const hits = raycaster.intersectObjects([...keyHitTargets, pedalHits.get('SUSTAIN')], false);
    if (!hits.length) return null;
    hits.sort((a, b) => a.distance - b.distance || (b.object.userData.color === 'BLACK' ? 1 : 0) - (a.object.userData.color === 'BLACK' ? 1 : 0));
    const data = { ...hits[0].object.userData };
    if (data.pedalId === 'SUSTAIN') data.kind = 'SUSTAIN_PEDAL';
    return { ...data, object: hits[0].object, point: hits[0].point.clone(), distance: hits[0].distance };
  }

  function pickPedal(clientX, clientY, allowed = PEDAL_LAYOUT.map(pedal => pedal.id)) {
    const allow = new Set(allowed);
    const rect = renderer.domElement.getBoundingClientRect();
    ndc.set(((clientX - rect.left) / rect.width) * 2 - 1, -((clientY - rect.top) / rect.height) * 2 + 1);
    raycaster.setFromCamera(ndc, camera);
    const hits = raycaster.intersectObjects(pedalHitTargets.filter(hit => allow.has(hit.userData.pedalId)), false);
    if (!hits.length) return null;
    const hit = hits.sort((a, b) => a.distance - b.distance)[0];
    return { ...hit.object.userData, object: hit.object, point: hit.point.clone(), distance: hit.distance };
  }

  function press(midi, owner) {
    const entry = byMidi.get(midi);
    if (!entry) return false;
    entry.pivot.userData.owners.add(owner);
    entry.pivot.userData.targetAngle = entry.pivot.userData.pressedAngle;
    return true;
  }

  function release(midi, owner) {
    const entry = byMidi.get(midi);
    if (!entry) return false;
    entry.pivot.userData.owners.delete(owner);
    if (!entry.pivot.userData.owners.size) entry.pivot.userData.targetAngle = 0;
    return true;
  }

  function pressPedal(pedalId, owner = 'programmatic') {
    const owners = pedalOwners.get(pedalId);
    if (!owners) return false;
    owners.add(owner);
    pedalTargetAngles.set(pedalId, PEDAL_PRESS_ANGLE);
    if (pedalId === 'SUSTAIN') audio.setSustain(true);
    return true;
  }

  function releasePedal(pedalId, owner = 'programmatic') {
    const owners = pedalOwners.get(pedalId);
    if (!owners) return false;
    owners.delete(owner);
    if (!owners.size) {
      pedalTargetAngles.set(pedalId, 0);
      if (pedalId === 'SUSTAIN') audio.setSustain(false);
    }
    return true;
  }

  function setPedal(on) {
    return on ? pressPedal('SUSTAIN', 'legacy-performance') : releasePedal('SUSTAIN', 'legacy-performance');
  }

  function releaseAll(reason = 'release-all') {
    captures.clear();
    for (const entry of byMidi.values()) { entry.pivot.userData.owners.clear(); entry.pivot.userData.targetAngle = 0; }
    for (const pedal of PEDAL_LAYOUT) { pedalOwners.get(pedal.id).clear(); pedalTargetAngles.set(pedal.id, 0); }
    audio.allNotesOff(reason);
  }

  function update() {
    if (focus) syncVisibility();
    for (const entry of byMidi.values()) {
      const data = entry.pivot.userData;
      entry.pivot.rotation.x = Math.abs(entry.pivot.rotation.x - data.targetAngle) < .00005 ? data.targetAngle : ease(entry.pivot.rotation.x, data.targetAngle, .42);
    }
    for (const pedal of PEDAL_LAYOUT) {
      const angle = pedalAngles.get(pedal.id) || 0;
      const target = pedalTargetAngles.get(pedal.id) || 0;
      pedalAngles.set(pedal.id, Math.abs(angle - target) < .0001 ? target : ease(angle, target, target ? .36 : .24));
    }
    for (const mesh of exteriorPedalMeshes()) applyPedalAngles(bindExteriorPedal(mesh));
  }

  function snapshot() {
    const pressed = [...byMidi.entries()].filter(([, entry]) => entry.pivot.userData.owners.size).map(([midi]) => midi).sort((a, b) => a - b);
    return {
      focus, registryStatus: manifest.status, keyCount: byMidi.size,
      white: manifest.validation.white, black: manifest.validation.black,
      pressedMidi: pressed,
      pointerCaptures: [...captures.entries()].map(([pointerId, capture]) => ({ pointerId, kind: capture.kind, midi: capture.midi || null })),
      sustain: audio.snapshot().sustain,
      fusedKeyboardHidden: focus && fusedMeshes().every(mesh => !mesh.visible),
      independentTransforms: new Set([...byMidi.values()].map(entry => entry.pivot.uuid)).size,
      pedalVisualAuthority: EXTERIOR_PEDAL_MESH,
      duplicatePedalRender: false,
      pedalAngleRad: pedalAngles.get('SUSTAIN'),
      pedalAnglesRad: Object.fromEntries(PEDAL_LAYOUT.map(pedal => [pedal.id, pedalAngles.get(pedal.id)])),
      pedalPressed: Object.fromEntries(PEDAL_LAYOUT.map(pedal => [pedal.id, pedalOwners.get(pedal.id).size > 0])),
      independentPedalRegions: PEDAL_LAYOUT.length,
    };
  }

  return {
    root, manifest, box: keyboardBox, byMidi, captures, controls,
    pedalHit, pedalHits, setFocus, pick, pickPedal,
    press, release, setPedal, pressPedal, releasePedal, releaseAll, update, snapshot, syncVisibility,
  };
}
