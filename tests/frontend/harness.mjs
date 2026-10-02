/**
 * tests/frontend/harness.mjs
 *
 * Loads the REAL web/index.html and executes the REAL app.js against a real
 * DOM (jsdom), with a mocked fetch serving realistic API responses. This
 * exists because a real bug -- app.js throwing on every single page load,
 * silently breaking the entire frontend -- went through two prior sessions
 * undetected by syntax-checking and CSS validation, and was only found by
 * actually running the code (see docs/STATUS.md's constructor-race-crash
 * entry). This harness productizes that ad hoc check into something
 * committed and re-runnable, instead of a one-off script in a scratch
 * directory.
 *
 * No browser is available in the environment these tests were developed
 * in (Chrome/Chromium/Firefox all ship as snap-only stubs on the sandboxed
 * Ubuntu image used, and snapd doesn't run there) -- jsdom is a genuine,
 * if imperfect, substitute: it implements enough of the DOM and module
 * loading to catch reference errors, wiring bugs, and DOM-shape mismatches,
 * even though it doesn't render CSS or lay anything out visually. It is
 * NOT a substitute for an actual visual check in a real browser.
 */
import { JSDOM } from "jsdom";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const REPO_ROOT = path.resolve(__dirname, "..", "..");
export const WEB_DIR = path.join(REPO_ROOT, "web");

/** A schema-shaped mock ExperimentOutput, matching what compile_equation()
 * actually produces (cross-checked against tests/integration/
 * test_phase2_pipeline.py's real assertions, not invented). Used so the
 * harness can exercise the full render path without a live backend. */
export function mockExperimentOutput(overrides = {}) {
  return {
    compiler_version: "0.3.0",
    model_database_version: "0.1.0",
    config: { candidate_selection_mode: "deterministic_top_rank", candidate_seed: null },
    input_equation_spec: {
      spec_version: "1.0", domain_type: "ODE", independent_vars: ["t"],
      dependent_var: "y", order: 2,
      terms: [
        { derivative_order: 2, wrt: "t", coefficient: 1 },
        { derivative_order: 1, wrt: "t", coefficient: 2 },
        { derivative_order: 0, wrt: "t", coefficient: 5 },
      ],
      rhs_forcing: { type: "zero", params: {}, expr: null },
      initial_conditions: null, boundary_conditions: null,
      input_source: "web_builder", raw_text: null,
    },
    canonical_ir: { order: 2, linearity: "linear", homogeneity: "homogeneous", domain_type: "ODE" },
    selected_candidate: {
      candidate_id: "mass_spring_damper_0", model_id: "mass_spring_damper",
      parameter_values: { m: 0.2236, c: 0.4472, k: 1.118 },
      verification_status: "EXACT", residual_expr: "0",
      assumptions: [], score: { exactness: 1, feasibility: 1, simplicity: 0.7, total: 0.865 },
      transformation_trace: { symbolic_derivation_steps: ["Matched the class.", "Solved for m, c, k."] },
    },
    alternative_candidates: [
      { candidate_id: "series_rlc_1", model_id: "series_rlc", parameter_values: { L: 1, R: 10, C: 0.001 }, verification_status: "EXACT" },
    ],
    experiment_description: "This second-order linear ODE is physically realizable as a Mass-Spring-Damper.",
    description_blanks: [
      { symbol: "m", label: "mass", template: "mass (m)", value: "0.2236", unit: "kg" },
      { symbol: "c", label: "viscous damping coefficient", template: "viscous damping coefficient (c)", value: "0.4472", unit: "N*s/m" },
      { symbol: "k", label: "spring constant", template: "spring constant (k)", value: "1.118", unit: "N/m" },
    ],
    build_instructions: {
      components: ["a low-friction cart", "a calibrated spring"],
      estimated_build_time_hours: 3, estimated_cost_usd: 120,
      artwork: { status: "missing", ratio: "1:1", url: "/media/memes/shrug.svg", is_placeholder: true, reason: null },
    },
    measurement_plan: {},
    warnings: [],
    ...overrides,
  };
}

export function mockModels() {
  return {
    models: [
      { model_id: "mass_spring_damper", display_name: "Mass-Spring-Damper (linear rail)", domain: "mechanical", artwork: { status: "missing", ratio: "1:1", url: "/media/memes/shrug.svg", is_placeholder: true, reason: null } },
      { model_id: "series_rlc", display_name: "Series RLC Circuit", domain: "electrical", artwork: { status: "missing", ratio: "1:1", url: "/media/memes/under-construction.svg", is_placeholder: true, reason: null } },
    ],
  };
}

/**
 * Boots a fresh DOM with app.js loaded and running. `fetchImpl` receives
 * (url, options) and should return a Response-shaped object; defaults to a
 * simple router covering /api/health, /api/models, /api/parse, /api/compile
 * with the mocks above, which is enough for most tests -- override for
 * error-path or slow-response tests.
 */
export async function bootApp({ fetchImpl } = {}) {
  const html = readFileSync(path.join(WEB_DIR, "index.html"), "utf8");
  const dom = new JSDOM(html, { url: "http://localhost/", pretendToBeVisual: true });

  const calls = [];
  const defaultFetch = async (url, options) => {
    calls.push({ url, options });
    if (url === "/api/health") {
      return jsonResponse({ status: "ok", compiler_version: "0.3.0" });
    }
    if (url === "/api/models") {
      return jsonResponse(mockModels());
    }
    if (url === "/api/parse") {
      const body = JSON.parse(options.body);
      if (!body.raw_text || !body.raw_text.includes("=")) {
        return jsonResponse({ detail: "Could not parse equation" }, 422);
      }
      return jsonResponse(mockExperimentOutput().input_equation_spec);
    }
    if (url === "/api/compile") {
      return jsonResponse(mockExperimentOutput());
    }
    throw new Error(`unmocked fetch: ${url}`);
  };

  dom.window.fetch = fetchImpl || defaultFetch;
  dom.window.matchMedia = dom.window.matchMedia || (() => ({ matches: false }));
  // jsdom implements SVGPathElement.getTotalLength as a throwing stub
  // ("not implemented"); the app checks truthiness before calling it, but
  // a plain existing-function-reference is truthy, so it still gets
  // called. Give it a real (fake) return value instead.
  if (dom.window.SVGPathElement) {
    dom.window.SVGPathElement.prototype.getTotalLength = () => 100;
  }

  global.window = dom.window;
  global.document = dom.window.document;
  global.fetch = dom.window.fetch;
  global.SVGPathElement = dom.window.SVGPathElement;

  const appPath = path.join(WEB_DIR, "app.js");
  await import(`${appPath}?t=${Date.now()}-${Math.random()}`); // cache-bust: each test gets a fresh module evaluation

  // let the initial loadHealth()/loadModels() microtasks settle
  await sleep(30);

  return { window: dom.window, document: dom.window.document, calls };
}

export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function jsonResponse(body, status = 200) {
  return { ok: status >= 200 && status < 300, status, json: async () => body };
}
