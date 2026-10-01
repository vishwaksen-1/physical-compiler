/**
 * builder.js — the equation-builder controls.
 *
 * Produces an EquationSpec exactly matching INTERFACE_CONTRACTS.md §1, which
 * is POSTed as `builder_state` to /api/compile. The server validates it with
 * the same validator the text parser is checked against (Agent C's
 * src/parser/validator.py), so the two input paths cannot silently drift.
 *
 * Also typesets the equation for display. This is not MathJax — it's a small
 * deliberate renderer producing the conventional physics notation
 * (italic serif variables, primes for derivatives) that the page's type
 * system is built around.
 */

import { typesetSpec } from "./typeset.js";

const FORCING_PARAMS = {
  zero: [],
  const: [{ key: "value", label: "Value", default: 1 }],
  sin: [
    { key: "amplitude", label: "Amplitude", default: 1 },
    { key: "frequency", label: "Frequency (rad/s)", default: 1 },
    { key: "phase", label: "Phase (rad)", default: 0 },
  ],
  cos: [
    { key: "amplitude", label: "Amplitude", default: 1 },
    { key: "frequency", label: "Frequency (rad/s)", default: 1 },
    { key: "phase", label: "Phase (rad)", default: 0 },
  ],
  step: [{ key: "value", label: "Step height", default: 1 }],
  impulse: [{ key: "value", label: "Impulse strength", default: 1 }],
  polynomial: [{ key: "slope", label: "Ramp rate", default: 1 }],
};

const COEFFICIENT_ROLES = {
  2: [
    { order: 2, symbol: "y″", role: "inertia — resists acceleration", default: 1 },
    { order: 1, symbol: "y′", role: "damping — removes energy", default: 2 },
    { order: 0, symbol: "y", role: "restoring — pulls back to zero", default: 5 },
  ],
  1: [
    { order: 1, symbol: "y′", role: "rate of change", default: 1 },
    { order: 0, symbol: "y", role: "restoring — pulls back to zero", default: 4 },
  ],
};

export class Builder {
  constructor(root, onChange) {
    this.form = root.querySelector("#equation-form");
    this.coefficientRows = root.querySelector("#coefficient-rows");
    this.forcingType = root.querySelector("#forcing-type");
    this.forcingParams = root.querySelector("#forcing-params");
    this.icRow = root.querySelector("#ic-row");
    this.equationDisplay = root.querySelector("#equation-display");
    this.equationNote = root.querySelector("#equation-note");
    this.onChange = onChange;
    // Gate so this controller's shared-element writes (equation display,
    // note) only happen while "Build with controls" is the active input
    // mode -- both this and TextMode write to the same #equation-display,
    // and both live inside the same <form> (so the other mode's input
    // events still reach this controller's form listener). Set by app.js
    // on mode switch.
    this.active = true;

    this.form.addEventListener("change", () => this.rebuildIfOrderChanged());
    this.form.addEventListener("input", () => this.emit());

    this.currentOrder = null;
    this.rebuildIfOrderChanged();
  }

  get order() {
    return Number(this.form.querySelector('input[name="order"]:checked').value);
  }

  rebuildIfOrderChanged() {
    const order = this.order;
    const forcing = this.forcingType.value;

    if (order !== this.currentOrder) {
      this.currentOrder = order;
      this.renderCoefficients(order);
      this.renderInitialConditions(order);
    }
    if (forcing !== this.currentForcing) {
      this.currentForcing = forcing;
      this.renderForcingParams(forcing);
    }
    this.emit();
  }

  renderCoefficients(order) {
    this.coefficientRows.textContent = "";
    for (const spec of COEFFICIENT_ROLES[order]) {
      const row = document.createElement("div");
      row.className = "coefficient-row";
      row.innerHTML = `
        <span class="coefficient-label">${spec.symbol}
          <small>${spec.role}</small>
        </span>
        <input type="number" step="any" data-coefficient="${spec.order}" value="${spec.default}" />
      `;
      this.coefficientRows.appendChild(row);
    }
  }

  renderInitialConditions(order) {
    this.icRow.textContent = "";
    const fields = order === 2
      ? [{ key: "y0", label: "y(0)" }, { key: "yp0", label: "y′(0)" }]
      : [{ key: "y0", label: "y(0)" }];
    for (const f of fields) {
      const wrap = document.createElement("div");
      wrap.className = "ic-field";
      wrap.innerHTML = `
        <label for="ic-${f.key}">${f.label}</label>
        <input type="number" step="any" id="ic-${f.key}" data-ic="${f.key}" value="${f.key === "y0" ? 1 : 0}" />
      `;
      this.icRow.appendChild(wrap);
    }
  }

  renderForcingParams(type) {
    this.forcingParams.textContent = "";
    for (const p of FORCING_PARAMS[type] ?? []) {
      const wrap = document.createElement("div");
      wrap.className = "param-field";
      wrap.innerHTML = `
        <label for="fp-${p.key}">${p.label}</label>
        <input type="number" step="any" id="fp-${p.key}" data-forcing-param="${p.key}" value="${p.default}" />
      `;
      this.forcingParams.appendChild(wrap);
    }
  }

  /** Coefficients highest-order first, for the solver. */
  coefficients() {
    const order = this.order;
    const values = [];
    for (let n = order; n >= 0; n--) {
      const input = this.coefficientRows.querySelector(`[data-coefficient="${n}"]`);
      values.push(input ? Number(input.value) : 0);
    }
    return values;
  }

  initialConditions() {
    const result = {};
    for (const input of this.icRow.querySelectorAll("[data-ic]")) {
      result[input.dataset.ic] = Number(input.value);
    }
    return result;
  }

  forcing() {
    const type = this.forcingType.value;
    const params = {};
    for (const input of this.forcingParams.querySelectorAll("[data-forcing-param]")) {
      params[input.dataset.forcingParam] = Number(input.value);
    }
    return { type, params, expr: null };
  }

  /** EquationSpec per INTERFACE_CONTRACTS.md §1. */
  buildEquationSpec() {
    const order = this.order;
    const terms = [];
    for (let n = order; n >= 0; n--) {
      const input = this.coefficientRows.querySelector(`[data-coefficient="${n}"]`);
      if (!input) continue;
      terms.push({
        derivative_order: n,
        wrt: "t",
        coefficient: Number(input.value),
      });
    }

    const ic = this.initialConditions();
    const initial_conditions = order === 2
      ? { "y(0)": ic.y0 ?? 0, "y'(0)": ic.yp0 ?? 0 }
      : { "y(0)": ic.y0 ?? 0 };

    return {
      spec_version: "1.0",
      domain_type: "ODE",
      independent_vars: ["t"],
      dependent_var: "y",
      order,
      terms,
      rhs_forcing: this.forcing(),
      initial_conditions,
      boundary_conditions: null,
      input_source: "web_builder",
      raw_text: null,
    };
  }

  /** Conventional physics typesetting of the current equation. */
  typeset() {
    this.equationDisplay.innerHTML = typesetSpec(this.buildEquationSpec());
  }

  setNote(text) {
    if (!this.active) return;
    this.equationNote.textContent = text;
  }

  emit() {
    if (!this.active) return;
    this.typeset();
    if (this.onChange) this.onChange(this.buildEquationSpec());
  }
}

