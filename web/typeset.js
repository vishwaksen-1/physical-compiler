/**
 * typeset.js — conventional physics notation for an EquationSpec-shaped
 * object (INTERFACE_CONTRACTS.md §1).
 *
 * Factored out of builder.js so the coefficient-builder and the raw-text
 * input mode render the exact same way once they agree on a spec, instead
 * of each having their own copy of this logic.
 */

export function typesetSpec(spec) {
  const depVar = spec.dependent_var || "y";
  const terms = [...(spec.terms || [])].sort((a, b) => b.derivative_order - a.derivative_order);
  const parts = [];

  for (const term of terms) {
    const value = Number(term.coefficient);
    if (!Number.isFinite(value) || value === 0) continue;

    const magnitude = Math.abs(value);
    const sign = value < 0 ? "\u2212" : "+";
    const coefText = magnitude === 1 ? "" : trimNumber(magnitude);
    const primes = term.derivative_order === 0 ? "" : "\u2032".repeat(term.derivative_order);

    if (parts.length > 0) {
      parts.push(`<span class="op">${sign}</span>`);
    } else if (value < 0) {
      parts.push(`<span class="op">\u2212</span>`);
    }
    parts.push(`<span class="coef">${coefText}</span><span class="var">${depVar}${primes}</span>`);
  }

  if (parts.length === 0) parts.push(`<span class="coef">0</span>`);

  const tName = (spec.independent_vars && spec.independent_vars[0]) || "t";
  const rhs = typesetForcing(spec.rhs_forcing, tName);
  return `${parts.join(" ")} <span class="op">=</span> ${rhs}`;
}

export function typesetForcing(forcing, tName = "t") {
  const type = forcing?.type ?? "zero";
  const p = forcing?.params ?? {};
  const n = (key, fallback = 1) => trimNumber(Number(p[key] ?? fallback));

  switch (type) {
    case "const":
      return `<span class="coef">${n("value")}</span>`;
    case "sin":
      return `<span class="coef">${n("amplitude")}</span> sin(<span class="coef">${n("frequency")}</span><span class="var">${tName}</span>${p.phase ? ` + ${n("phase", 0)}` : ""})`;
    case "cos":
      return `<span class="coef">${n("amplitude")}</span> cos(<span class="coef">${n("frequency")}</span><span class="var">${tName}</span>${p.phase ? ` + ${n("phase", 0)}` : ""})`;
    case "step":
      return `<span class="coef">${n("value")}</span> \u00b7 <span class="var">H</span>(<span class="var">${tName}</span>)`;
    case "impulse":
      return `<span class="coef">${n("value")}</span> \u00b7 <span class="var">\u03b4</span>(<span class="var">${tName}</span>)`;
    case "polynomial":
      return `<span class="coef">${n("slope")}</span><span class="var">${tName}</span>`;
    default:
      return `<span class="coef">0</span>`;
  }
}

export function trimNumber(v) {
  if (!Number.isFinite(v)) return "?";
  const rounded = Math.round(v * 10000) / 10000;
  return String(rounded);
}

/** Highest-order-first coefficient list, for the client-side RK4 preview. */
export function coefficientsFromSpec(spec) {
  const coeffs = [];
  for (let n = spec.order; n >= 0; n--) {
    const term = (spec.terms || []).find((t) => t.derivative_order === n);
    coeffs.push(term ? Number(term.coefficient) : 0);
  }
  return coeffs;
}
