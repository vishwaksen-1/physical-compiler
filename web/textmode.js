/**
 * textmode.js — "Type the equation" input mode.
 *
 * The coefficient-builder is one valid way to specify a differential
 * equation, but it's not how anyone who already has an equation in mind
 * thinks about it. This is the other input path INTERFACE_CONTRACTS.md §1
 * already defines server-side (`parse_equation(raw_text)` /
 * `POST /api/parse`) -- the frontend just never exposed it before now.
 *
 * Validates live via the server's own text_parser (debounced), typesets the
 * result with the same shared renderer the builder uses, and offers a
 * handful of known-working example equations pulled directly from
 * src/parser's own test suite (tests/unit/parser) rather than invented
 * syntax that might not actually match the grammar.
 */

import { typesetSpec } from "./typeset.js";

const EXAMPLES = [
  "x'' + 2*x' + 5*x = 0",
  "x'' + 2*x' + 5*x = sin(t)",
  "x' + 4*x = 0",
  "d2x/dt2 + 2*dx/dt + 5*x = 0",
];

const DEBOUNCE_MS = 450;

export class TextMode {
  constructor(root, onChange) {
    this.textarea = root.querySelector("#raw-equation");
    this.chipsRoot = root.querySelector("#example-chips");
    this.statusEl = root.querySelector("#parse-status");
    this.equationDisplay = root.querySelector("#equation-display");
    this.equationNote = root.querySelector("#equation-note");
    this.onChange = onChange; // called with the parsed EquationSpec, or null

    this.active = false;
    this.lastSpec = null;
    this.timer = null;

    this.renderExamples();
    this.textarea.addEventListener("input", () => this.scheduleParse());
  }

  renderExamples() {
    this.chipsRoot.textContent = "";
    for (const example of EXAMPLES) {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "example-chip";
      chip.textContent = example;
      chip.addEventListener("click", () => {
        this.textarea.value = example;
        this.parseNow();
        this.textarea.focus();
      });
      this.chipsRoot.appendChild(chip);
    }
  }

  scheduleParse() {
    clearTimeout(this.timer);
    this.timer = setTimeout(() => this.parseNow(), DEBOUNCE_MS);
  }

  /** Re-run the live parse immediately -- called on activation too, so
   * switching into this mode with existing text shows its state right away
   * rather than waiting for the next keystroke. */
  async parseNow() {
    if (!this.active) return;

    const text = this.textarea.value.trim();
    if (!text) {
      this.lastSpec = null;
      this.setStatus("", "");
      this.equationDisplay.innerHTML = `<span class="op">?</span>`;
      this.equationNote.textContent = "Type an equation above, or pick an example.";
      this.onChange(null);
      return;
    }

    this.setStatus("checking\u2026", "pending");
    try {
      const res = await fetch("/api/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ raw_text: text }),
      });
      const data = await res.json();

      // The textarea may have changed again while this request was in
      // flight -- drop a stale response rather than flash an old result.
      if (this.textarea.value.trim() !== text) return;

      if (!res.ok) {
        this.lastSpec = null;
        this.setStatus(data.detail ?? "Couldn't parse that.", "error");
        this.onChange(null);
        return;
      }

      this.lastSpec = data;
      this.equationDisplay.innerHTML = typesetSpec(data);
      const orderWord = data.order === 1 ? "first" : data.order === 2 ? "second" : `order-${data.order}`;
      this.equationNote.textContent = `Parsed as a ${orderWord}-order ${data.domain_type} in ${data.dependent_var}.`;
      this.setStatus("parsed \u2713", "ok");
      this.onChange(data);
    } catch {
      this.lastSpec = null;
      this.setStatus("Couldn't reach the compiler to check this.", "error");
      this.onChange(null);
    }
  }

  setStatus(text, kind) {
    this.statusEl.textContent = text;
    this.statusEl.dataset.kind = kind || "";
  }

  activate() {
    this.active = true;
    this.parseNow();
  }

  deactivate() {
    this.active = false;
  }

  get rawText() {
    return this.textarea.value.trim();
  }

  hasValidSpec() {
    return this.lastSpec !== null;
  }
}
