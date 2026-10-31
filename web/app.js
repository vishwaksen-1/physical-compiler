/**
 * app.js — entry point. Wires the builder, the raw-text mode, the live
 * solver preview, and the results viewer to the HTTP contract in
 * INTERFACE_CONTRACTS.md §9.
 *
 * Loaded as the single ES module entry (`<script type="module" src="app.js">`);
 * it imports the other modules itself. Loading these as three plain <script>
 * tags throws a SyntaxError on the first import/export and silently breaks
 * the page — see docs/STATUS.md.
 */

import { Builder } from "./builder.js";
import { TextMode } from "./textmode.js";
import { coefficientsFromSpec } from "./typeset.js";
import { integrate, renderTrace, describeRegime } from "./solver.js";
import { renderOutput, renderCompiling, renderError } from "./viewer.js";
import { buildWavePath } from "./wavepath.js";
import { buildStarfield, buildAtomicField, playRipple, playGlitchSqueeze, playQuantumCompile } from "./modefx.js";

const statusStrip = document.getElementById("status-strip");
const traceSvg = document.getElementById("trace-svg");
const traceCaption = document.getElementById("trace-caption");
const resultsRoot = document.getElementById("results-root");
const compileBtn = document.getElementById("compile-btn");
const surpriseBtn = document.getElementById("surprise-btn");
const seedNote = document.getElementById("seed-note");
const versionLine = document.getElementById("version-line");
const buildFields = document.getElementById("build-mode-fields");
const textFields = document.getElementById("text-mode-fields");
const modeTabs = Array.from(document.querySelectorAll(".mode-tab"));

/** model_id -> summary, from GET /api/models. */
const models = new Map();

let builder;
let textMode;
let mode = "build"; // "build" | "text"
let theme = "classical"; // "classical" | "celestial" | "quantum"

const themeTabs = Array.from(document.querySelectorAll("[data-theme-tab]"));
const backdropCelestial = document.getElementById("backdrop-celestial");
const backdropQuantum = document.getElementById("backdrop-quantum");

/* ------------------------------------------------------------- live preview */

/** Read the (shared, see index.html's field-note) starting-conditions
 * inputs directly -- deliberately NOT a Builder method, since this needs
 * to work even while Builder itself is still being constructed (its
 * constructor synchronously fires the first refreshPreview() call, before
 * the module-level `builder` variable's assignment below completes). */
function readInitialConditions() {
  const result = { y0: 0, yp0: 0 };
  for (const input of document.querySelectorAll("#ic-row [data-ic]")) {
    result[input.dataset.ic] = Number(input.value);
  }
  return result;
}

/** Re-run the client-side RK4 preview from whichever spec is current.
 * `spec` is an EquationSpec-shaped object from either input path -- once
 * both modes agree on that shape, the preview doesn't care which produced it. */
function refreshPreview(spec) {
  if (!spec) {
    clearPreview();
    return;
  }

  const coeffs = coefficientsFromSpec(spec);
  const ic = readInitialConditions();
  const result = integrate(spec.order, coeffs, spec.rhs_forcing, { y0: ic.y0, yp0: ic.yp0 });
  renderTrace(traceSvg, result);

  if (result.degenerate) {
    traceCaption.textContent = "The highest-order coefficient can't be zero — that's what makes it an equation of this order.";
    return;
  }

  const regime = describeRegime(spec.order, coeffs);
  traceCaption.innerHTML = "";
  const strong = document.createElement("strong");
  strong.textContent = capitalize(regime.name);
  traceCaption.append(strong, document.createTextNode(` — ${regime.detail}.`));

  const note = spec.rhs_forcing?.type === "zero" || !spec.rhs_forcing
    ? "Released from its starting conditions and left alone."
    : "Driven continuously by the term on the right.";
  // `builder` may still be mid-construction on the very first call (its
  // own constructor is what triggers this) -- guard, don't assume it's assigned yet.
  if (mode === "build" && builder) builder.setNote(note);
}

function clearPreview() {
  traceSvg.textContent = "";
  traceCaption.textContent = "";
}

const DEFAULT_EMPTY_STATE = `
  <div class="empty-state" id="empty-state">
    <svg class="empty-mark" viewBox="0 0 120 80" aria-hidden="true">
      <path d="M8 40 Q 30 8, 52 40 T 96 40" fill="none" stroke="currentColor" stroke-width="1.5" opacity=".5"/>
      <circle cx="112" cy="40" r="3" fill="currentColor" opacity=".5"/>
    </svg>
    <p>The curve above is computed in your browser from the coefficients on the left.
       Compile to find out which real apparatus obeys the same equation.</p>
  </div>
`;

function clearResults() {
  resultsRoot.innerHTML = DEFAULT_EMPTY_STATE;
  seedNote.hidden = true;
  seedNote.textContent = "";
}

/* ------------------------------------------------------------------- modes */

function setMode(next) {
  if (next === mode) return;
  mode = next;

  clearResults();

  buildFields.hidden = mode !== "build";
  textFields.hidden = mode !== "text";
  for (const tab of modeTabs) tab.setAttribute("aria-selected", String(tab.dataset.mode === mode));

  if (mode === "build") {
    textMode.deactivate();
    builder.active = true;
    builder.emit(); // repaint the shared equation display/preview for the builder's current state
  } else {
    builder.active = false;
    textMode.activate(); // re-parses immediately, repainting the shared display
  }
}

function setTheme(next, originEvent) {
  if (next === theme) return;
  const previous = theme;
  theme = next;

  clearResults();

  for (const tab of themeTabs) {
    const isActive = tab.dataset.themeTab === theme;
    tab.classList.toggle("active", isActive);
    tab.setAttribute("aria-selected", String(isActive));
  }
  document.body.dataset.theme = theme; // CSS hook for Phase 04's dark palettes
  document.documentElement.style.filter = ""; // Clear any leftover glitch filters

  if (theme === "celestial") {
    buildStarfield(backdropCelestial);
    playRipple(originEvent);
  } else if (theme === "quantum") {
    buildAtomicField(backdropQuantum);
    playGlitchSqueeze();
  }

  textMode.setExampleTheme(theme);
}

/** The current spec, from whichever mode is active, or null if the text
 * mode doesn't have a valid parse yet. */
function currentSpec() {
  return mode === "build" ? builder.buildEquationSpec() : textMode.lastSpec;
}

/* -------------------------------------------------------------- API calls */

async function loadHealth() {
  try {
    const res = await fetch("/api/health");
    if (!res.ok) throw new Error(String(res.status));
    const data = await res.json();
    setStatus("ok", `compiler ${data.compiler_version}`);
    versionLine.textContent =
      `Compiler ${data.compiler_version} — deterministic by construction: the same equation always compiles to the same apparatus.`;
  } catch {
    setStatus("down", "compiler unreachable");
  }
}

async function loadModels() {
  try {
    const res = await fetch("/api/models");
    if (!res.ok) return;
    const data = await res.json();
    for (const m of data.models ?? []) models.set(m.model_id, m);
  } catch {
    /* the results view falls back to raw model_ids — not worth blocking on */
  }
}

async function compile({ seed = null } = {}) {
  const config = seed === null
    ? { candidate_selection_mode: "deterministic_top_rank", candidate_seed: null }
    : { candidate_selection_mode: "seeded_random", candidate_seed: seed };
  if (theme !== "classical") config.theme = theme;

  // Exactly one of raw_text / builder_state, per INTERFACE_CONTRACTS.md §9.
  const body = mode === "text"
    ? { raw_text: textMode.rawText, builder_state: null, config }
    : { raw_text: null, builder_state: builder.buildEquationSpec(), config };

  setBusy(true);
  renderCompiling(resultsRoot);

  if (theme === "quantum") {
    playQuantumCompile(backdropQuantum);
  }

  try {
    const res = await fetch("/api/compile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    if (!res.ok) {
      renderError(resultsRoot, data.detail ?? `The compiler returned ${res.status}.`);
      return;
    }

    renderOutput(resultsRoot, data, models);

    // Redraw the trace with the draw-on animation as the single orchestrated
    // moment of the compile: the curve completes as the apparatus appears.
    // Prefer the server's own parsed input_equation_spec so the animated
    // curve matches exactly what got compiled, in either mode.
    const spec = data.input_equation_spec ?? currentSpec();
    if (spec) {
      const ic = builder.initialConditions();
      const result = integrate(spec.order, coefficientsFromSpec(spec), spec.rhs_forcing, ic);
      renderTrace(traceSvg, result, { animate: true });
    }

    const echoed = data.config?.candidate_seed;
    if (echoed != null) {
      seedNote.hidden = false;
      seedNote.textContent = `seed ${echoed} — re-running with this seed gives this exact apparatus again`;
    } else {
      seedNote.hidden = true;
    }
  } catch (err) {
    renderError(
      resultsRoot,
      "Couldn't reach the compiler. If you're running locally, check that the API is up on the same origin."
    );
  } finally {
    setBusy(false);
  }
}

/* ---------------------------------------------------------------- plumbing */

function setStatus(state, text) {
  statusStrip.querySelector(".status-dot").dataset.state = state;
  statusStrip.querySelector(".status-text").textContent = text;
}

function setBusy(busy) {
  compileBtn.disabled = busy;
  surpriseBtn.disabled = busy;
  compileBtn.textContent = busy ? "Compiling…" : "Compile to apparatus";
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

/* ------------------------------------------------------------------- start */

const mastheadWave = document.querySelector(".masthead-wave-path");
if (mastheadWave) {
  mastheadWave.setAttribute(
    "d",
    buildWavePath({ viewWidth: 800, period: 100, amplitude: 11, center: 30 })
  );
}

builder = new Builder(document, (spec) => refreshPreview(spec));
textMode = new TextMode(document, (spec) => refreshPreview(spec));

for (const tab of modeTabs) {
  tab.addEventListener("click", () => setMode(tab.dataset.mode));
}

for (const tab of themeTabs) {
  tab.addEventListener("click", (e) => setTheme(tab.dataset.themeTab, e));
}

document.getElementById("equation-form").addEventListener("submit", (e) => {
  e.preventDefault();
  if (mode === "text" && !textMode.hasValidSpec()) {
    textMode.setStatus(textMode.rawText ? "Fix the equation above before compiling." : "Type an equation first.", "error");
    return;
  }
  compile();
});

surpriseBtn.addEventListener("click", () => {
  if (mode === "text" && !textMode.hasValidSpec()) {
    textMode.setStatus(textMode.rawText ? "Fix the equation above before compiling." : "Type an equation first.", "error");
    return;
  }
  // The seed is generated client-side and echoed back by the server, per
  // INTERFACE_CONTRACTS.md §6 — so any result stays reproducible.
  compile({ seed: Math.floor(Math.random() * 1_000_000) });
});

refreshPreview(builder.buildEquationSpec());
loadHealth();
loadModels();
