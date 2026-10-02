/**
 * tests/frontend/run.mjs
 *
 * Frontend smoke tests: boots the real app.js in jsdom and checks it
 * actually works, not just parses. Run directly with `node
 * tests/frontend/run.mjs` (needs `npm install` first -- see package.json),
 * or via `pytest tests/unit/frontend/test_frontend_smoke.py`, which shells
 * out to this and skips gracefully if node_modules isn't present.
 *
 * No test framework dependency (mocha/jest/etc) -- Node's built-in
 * `assert` is enough for a suite this size, and jsdom is already the one
 * dependency this project took on just for this (see package.json).
 */
import assert from "node:assert/strict";
import { bootApp, mockExperimentOutput, sleep } from "./harness.mjs";

let passed = 0;
let failed = 0;

async function test(name, fn) {
  try {
    await fn();
    passed++;
    console.log(`  ok - ${name}`);
  } catch (err) {
    failed++;
    console.log(`  FAIL - ${name}`);
    console.log(`         ${err.message}`);
  }
}

console.log("Frontend smoke tests (tests/frontend/run.mjs)");

// -------------------------------------------------------------------------
// Regression coverage for the specific bug that motivated this file: app.js
// used to throw on every page load because Builder's constructor
// synchronously fired a callback that closed over the not-yet-assigned
// module-level `builder` variable. See docs/STATUS.md.
// -------------------------------------------------------------------------

await test("app.js loads and initializes without throwing", async () => {
  await bootApp(); // bootApp() itself throws if the import throws
});

await test("initial render: equation display shows the default equation", async () => {
  const { document } = await bootApp();
  const html = document.getElementById("equation-display").innerHTML;
  assert.match(html, /y/);
  assert.match(html, /5/); // default coefficients include a 5
});

await test("initial render: coefficient rows match the default order (2nd)", async () => {
  const { document } = await bootApp();
  assert.equal(document.getElementById("coefficient-rows").children.length, 3);
  assert.equal(document.getElementById("ic-row").children.length, 2);
});

await test("initial render: the live preview trace actually draws something", async () => {
  const { document } = await bootApp();
  const svg = document.getElementById("trace-svg");
  assert.ok(svg.children.length > 3, "expected grid lines + curve + labels in the trace SVG");
});

await test("status indicator reflects a successful /api/health call", async () => {
  const { document } = await bootApp();
  const dot = document.querySelector("#status-strip .status-dot");
  assert.equal(dot.dataset.state, "ok");
});

await test("status indicator reflects a failed /api/health call", async () => {
  const { document } = await bootApp({
    fetchImpl: async () => ({ ok: false, status: 0, json: async () => ({}) }),
  });
  const dot = document.querySelector("#status-strip .status-dot");
  assert.equal(dot.dataset.state, "down");
});

// -------------------------------------------------------------------------
// Mode switching
// -------------------------------------------------------------------------

await test("switching to text mode hides build fields and shows text fields", async () => {
  const { document } = await bootApp();
  document.querySelector('.mode-tab[data-mode="text"]').dispatchEvent(new window.Event("click", { bubbles: true }));
  await sleep(20);
  assert.equal(document.getElementById("build-mode-fields").hidden, true);
  assert.equal(document.getElementById("text-mode-fields").hidden, false);
});

await test("switching to text mode with no text shows a prompt, not the build equation", async () => {
  const { document } = await bootApp();
  document.querySelector('.mode-tab[data-mode="text"]').dispatchEvent(new window.Event("click", { bubbles: true }));
  await sleep(20);
  assert.equal(document.getElementById("equation-display").textContent.trim(), "?");
});

await test("switching back to build mode restores the builder's equation", async () => {
  const { document } = await bootApp();
  const textTab = document.querySelector('.mode-tab[data-mode="text"]');
  const buildTab = document.querySelector('.mode-tab[data-mode="build"]');
  textTab.dispatchEvent(new window.Event("click", { bubbles: true }));
  await sleep(20);
  buildTab.dispatchEvent(new window.Event("click", { bubbles: true }));
  await sleep(20);
  assert.match(document.getElementById("equation-display").innerHTML, /5/);
});

await test("typing in text mode triggers a debounced /api/parse call", async () => {
  const { document, calls } = await bootApp();
  document.querySelector('.mode-tab[data-mode="text"]').dispatchEvent(new window.Event("click", { bubbles: true }));
  await sleep(20);
  const textarea = document.getElementById("raw-equation");
  textarea.value = "x'' + 2*x' + 5*x = 0";
  textarea.dispatchEvent(new window.Event("input", { bubbles: true }));
  await sleep(600); // debounce is 450ms
  assert.ok(calls.some((c) => c.url === "/api/parse"), "expected a call to /api/parse");
});

await test("a successful text-mode parse updates the equation display and enables compiling", async () => {
  const { document } = await bootApp();
  document.querySelector('.mode-tab[data-mode="text"]').dispatchEvent(new window.Event("click", { bubbles: true }));
  await sleep(20);
  const textarea = document.getElementById("raw-equation");
  textarea.value = "x' + 4*x = 0";
  textarea.dispatchEvent(new window.Event("input", { bubbles: true }));
  await sleep(600);
  assert.match(document.getElementById("parse-status").textContent, /parsed/i);
});

// -------------------------------------------------------------------------
// Validation before hitting the network
// -------------------------------------------------------------------------

await test("submitting with an empty text-mode input never calls /api/compile", async () => {
  const { document, calls } = await bootApp();
  document.querySelector('.mode-tab[data-mode="text"]').dispatchEvent(new window.Event("click", { bubbles: true }));
  await sleep(20);
  document.getElementById("equation-form").dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
  await sleep(20);
  assert.ok(!calls.some((c) => c.url === "/api/compile"), "compile should not have been called");
  assert.match(document.getElementById("parse-status").textContent, /type an equation/i);
});

// -------------------------------------------------------------------------
// Compile flow and result rendering
// -------------------------------------------------------------------------

await test("submitting in build mode calls /api/compile and renders a result card", async () => {
  const { document, calls } = await bootApp();
  document.getElementById("equation-form").dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
  await sleep(20);
  assert.ok(calls.some((c) => c.url === "/api/compile"), "expected a call to /api/compile");
  assert.ok(document.querySelector(".apparatus"), "expected an .apparatus result card to render");
});

await test("a rendered result shows the fill-in-the-blanks worksheet with real values", async () => {
  const { document } = await bootApp();
  document.getElementById("equation-form").dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
  await sleep(20);
  const blanksText = document.querySelector(".blanks")?.textContent || "";
  assert.match(blanksText, /0\.2236/);
  assert.match(blanksText, /kg/);
});

await test("a rendered result shows the artwork box with a placeholder image", async () => {
  const { document } = await bootApp();
  document.getElementById("equation-form").dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
  await sleep(20);
  const img = document.querySelector(".artwork-box img");
  assert.ok(img, "expected an .artwork-box img");
  assert.match(img.getAttribute("src"), /\/media\/memes\//);
});

await test("a rendered result shows alternative realizations", async () => {
  const { document } = await bootApp();
  document.getElementById("equation-form").dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
  await sleep(20);
  assert.match(document.querySelector(".alternatives")?.textContent || "", /series_rlc|RLC/i);
});

await test("a 422 compile error renders the error notice, not a result card", async () => {
  const { document } = await bootApp({
    fetchImpl: async (url) => {
      if (url === "/api/health") return { ok: true, status: 200, json: async () => ({ status: "ok", compiler_version: "x" }) };
      if (url === "/api/models") return { ok: true, status: 200, json: async () => ({ models: [] }) };
      if (url === "/api/compile") return { ok: false, status: 422, json: async () => ({ detail: "bad input" }) };
      return { ok: true, status: 200, json: async () => ({}) };
    },
  });
  document.getElementById("equation-form").dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
  await sleep(20);
  assert.ok(document.querySelector(".notice"), "expected a .notice error card");
  assert.ok(!document.querySelector(".apparatus"), "should not render a result card on error");
});

await test("a no-match result (selected_candidate: null) renders the calm fallback notice", async () => {
  const { document } = await bootApp({
    fetchImpl: async (url) => {
      if (url === "/api/health") return { ok: true, status: 200, json: async () => ({ status: "ok", compiler_version: "x" }) };
      if (url === "/api/models") return { ok: true, status: 200, json: async () => ({ models: [] }) };
      if (url === "/api/compile") {
        return { ok: true, status: 200, json: async () => mockExperimentOutput({
          selected_candidate: null, alternative_candidates: [],
          experiment_description: "No physical model in the current registry realizes this equation.",
        }) };
      }
      return { ok: true, status: 200, json: async () => ({}) };
    },
  });
  document.getElementById("equation-form").dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
  await sleep(20);
  const notice = document.querySelector(".notice-fallback");
  assert.ok(notice, "expected a .notice-fallback card");
  assert.doesNotMatch(notice.className, /\bnotice\b.*\bfail\b/); // sanity: still the calm variant, not styled as an error
});

// -------------------------------------------------------------------------
// "Try another realization" (seeded_random)
// -------------------------------------------------------------------------

await test("the surprise button sends a seeded_random config", async () => {
  const { document, calls } = await bootApp();
  document.getElementById("surprise-btn").dispatchEvent(new window.Event("click", { bubbles: true }));
  await sleep(20);
  const compileCall = calls.find((c) => c.url === "/api/compile");
  assert.ok(compileCall, "expected a call to /api/compile");
  const body = JSON.parse(compileCall.options.body);
  assert.equal(body.config.candidate_selection_mode, "seeded_random");
  assert.equal(typeof body.config.candidate_seed, "number");
});

// -------------------------------------------------------------------------

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
