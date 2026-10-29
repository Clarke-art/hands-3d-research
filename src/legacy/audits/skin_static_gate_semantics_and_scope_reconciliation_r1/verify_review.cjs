// Exercise downloaded-response logic in a mocked DOM. No response is saved or treated as Human approval.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync(path.join(__dirname, 'SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT_HUMAN_REVIEW.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script); // Syntax check independent of a browser.
assert(!/<input[^>]*\schecked[\s>]/i.test(html));
assert.equal((html.match(/type="radio"/g) || []).length, 10);
async function scenario(values) {
  const events = {};
  const form = { addEventListener: (name, fn) => events[name] = fn,
    querySelector: selector => { const key = selector.match(/name="(Q\d)"/)[1]; return values[key] ? { value: values[key] } : null; },
    reportValidity: () => [1,2,3,4,5].every(i => values['Q' + i]) };
  const button = { disabled: true };
  const result = {};
  let blob, clicked = false;
  const document = { getElementById: id => ({ approval: form, download: button, notes: { value: 'MOCK_VALIDATION_ONLY' }, result })[id],
    createElement: () => ({ click: () => clicked = true }) };
  vm.runInNewContext(script, { document, Blob, Date, URL: { createObjectURL: b => { blob = b; return 'mock:validation'; }, revokeObjectURL: () => {} }, setTimeout: fn => fn() });
  events.change();
  events.submit({ preventDefault: () => {} });
  return { disabled: button.disabled, clicked, response: blob ? JSON.parse(await blob.text()) : null };
}
(async () => {
  const partial = await scenario({ Q1: 'YES' });
  assert(partial.disabled && !partial.clicked && partial.response === null);
  const yes = await scenario({ Q1:'YES', Q2:'YES', Q3:'YES', Q4:'YES', Q5:'YES' });
  assert(!yes.disabled && yes.clicked);
  assert.equal(yes.response.authorized_next_phase, 'TARGETED_RIG_AND_SKIN_DATA_REBUILD_R2');
  assert.equal(yes.response.automatic_apply, false);
  assert.equal(yes.response.Stage6_approved, false);
  assert.equal(yes.response.deformation_approved, false);
  const no = await scenario({ Q1:'YES', Q2:'YES', Q3:'NO', Q4:'YES', Q5:'YES' });
  assert.equal(no.response.all_accepted, false);
  assert.equal(no.response.authorized_next_phase, null);
  const status = JSON.parse(fs.readFileSync(path.join(__dirname, 'SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1_STATUS.json'), 'utf8'));
  assert.equal(yes.response.proposal_sha256, status.proposal_sha256);
  assert.equal(yes.response.candidate_R1_sha256, status.candidate_blend_sha256_before);
  console.log(JSON.stringify({ review_verification: 'PASS', no_preselected_answers: true,
    incomplete_response_blocked: true, reject_disables_authorization: true, exact_hashes_bound: true,
    automatic_apply: false, actual_Human_approval_created: false }));
})().catch(error => { console.error(error); process.exitCode = 1; });
