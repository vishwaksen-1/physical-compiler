/**
 * solver.js — client-side integration of the user's equation, purely for the
 * live preview curve.
 *
 * This is deliberately NOT part of the compiler contract: nothing here feeds
 * into EquationSpec or the /api/compile request. It exists so the page can
 * show what the equation *does* while you're still typing it, without a
 * round trip. The authoritative mathematics all lives in src/ on the server.
 *
 * Handles the same family the Phase 2 matcher handles: linear
 * constant-coefficient ODEs of order 1 or 2.
 */

const SAMPLES = 400;

/** Forcing f(t) for the spec's rhs_forcing block. */
export function forcingFunction(forcing) {
  const type = forcing?.type ?? "zero";
  const p = forcing?.params ?? {};
  const amp = Number(p.amplitude ?? 1);
  const freq = Number(p.frequency ?? 1);
  const phase = Number(p.phase ?? 0);
  const value = Number(p.value ?? 1);
  const slope = Number(p.slope ?? 1);

  switch (type) {
    case "const": return () => value;
    case "sin": return (t) => amp * Math.sin(freq * t + phase);
    case "cos": return (t) => amp * Math.cos(freq * t + phase);
    case "step": return (t) => (t >= 0 ? value : 0);
    // A true delta can't be sampled; use a narrow normalized pulse so the
    // preview shows the characteristic "kick then ring down" shape.
    case "impulse": return (t) => (t < 0.08 ? value / 0.08 : 0);
    case "polynomial": return (t) => slope * t;
    default: return () => 0;
  }
}

/**
 * Natural timescale of the system, used to pick a sensible time window so
 * the curve is legible whether it rings for milliseconds or minutes.
 */
function naturalTimescale(order, coeffs) {
  if (order === 1) {
    const [a1, a0] = coeffs;
    if (a0 === 0) return 10;
    return Math.abs(a1 / a0);
  }
  const [a2, a1, a0] = coeffs;
  if (a0 === 0) return 10;
  const omega = Math.sqrt(Math.abs(a0 / a2));
  return omega > 0 ? (2 * Math.PI) / omega : 10;
}

/**
 * Integrate with classic RK4.
 * coeffs are highest-order first: order 1 -> [a1, a0]; order 2 -> [a2, a1, a0].
 * Returns { ts, ys, tMax, diverged }.
 */
export function integrate(order, coeffs, forcing, initial) {
  const f = forcingFunction(forcing);
  const timescale = naturalTimescale(order, coeffs);
  const tMax = Math.min(Math.max(timescale * 4, 0.5), 5000);
  const dt = tMax / SAMPLES;

  const lead = coeffs[0];
  if (!Number.isFinite(lead) || lead === 0) {
    return { ts: [], ys: [], tMax, diverged: false, degenerate: true };
  }

  // state vector: order 1 -> [y]; order 2 -> [y, y']
  let state = order === 1
    ? [Number(initial.y0) || 0]
    : [Number(initial.y0) || 0, Number(initial.yp0) || 0];

  const derivative = (t, s) => {
    if (order === 1) {
      const [a1, a0] = coeffs;
      return [(f(t) - a0 * s[0]) / a1];
    }
    const [a2, a1, a0] = coeffs;
    return [s[1], (f(t) - a1 * s[1] - a0 * s[0]) / a2];
  };

  const add = (s, d, h) => s.map((v, i) => v + d[i] * h);

  const ts = [];
  const ys = [];
  let diverged = false;

  for (let i = 0; i <= SAMPLES; i++) {
    const t = i * dt;
    ts.push(t);
    ys.push(state[0]);

    if (!Number.isFinite(state[0]) || Math.abs(state[0]) > 1e12) {
      diverged = true;
      break;
    }

    const k1 = derivative(t, state);
    const k2 = derivative(t + dt / 2, add(state, k1, dt / 2));
    const k3 = derivative(t + dt / 2, add(state, k2, dt / 2));
    const k4 = derivative(t + dt, add(state, k3, dt));
    state = state.map(
      (v, j) => v + (dt / 6) * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j])
    );
  }

  return { ts, ys, tMax, diverged, degenerate: false };
}

/** Plain-language description of the qualitative regime. */
export function describeRegime(order, coeffs) {
  if (order === 1) {
    const [a1, a0] = coeffs;
    if (a0 === 0) return { name: "no restoring term", detail: "the state drifts rather than settling" };
    const tau = Math.abs(a1 / a0);
    if (a0 / a1 < 0) return { name: "runaway growth", detail: "the state grows without bound" };
    return { name: "exponential decay", detail: `settles with a time constant of about ${fmt(tau)} s` };
  }

  const [a2, a1, a0] = coeffs;
  if (a0 === 0) return { name: "no restoring term", detail: "the state drifts rather than oscillating" };

  const omega0 = Math.sqrt(Math.abs(a0 / a2));
  const zeta = a1 / (2 * Math.sqrt(Math.abs(a0 * a2)));

  if (zeta < -1e-9) return { name: "unstable", detail: "energy is fed in rather than removed, so the response grows" };
  if (Math.abs(zeta) < 1e-9) return { name: "undamped", detail: `rings forever at about ${fmt(omega0)} rad/s` };
  if (zeta < 1) {
    return {
      name: "underdamped",
      detail: `rings at about ${fmt(omega0 * Math.sqrt(1 - zeta * zeta))} rad/s while decaying (ζ = ${fmt(zeta)})`,
    };
  }
  if (Math.abs(zeta - 1) < 1e-6) return { name: "critically damped", detail: "returns to rest as fast as possible without overshooting" };
  return { name: "overdamped", detail: `creeps back to rest without oscillating (ζ = ${fmt(zeta)})` };
}

function fmt(v) {
  if (!Number.isFinite(v)) return "—";
  if (v === 0) return "0";
  const a = Math.abs(v);
  if (a >= 1000 || a < 0.01) return v.toExponential(2);
  return String(Math.round(v * 1000) / 1000);
}

const SVG_NS = "http://www.w3.org/2000/svg";

function el(name, attrs = {}) {
  const node = document.createElementNS(SVG_NS, name);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, String(v));
  return node;
}

/** Draw the integrated response into the given <svg>. */
export function renderTrace(svg, result, { animate = false } = {}) {
  const W = 560;
  const H = 240;
  const PAD = { l: 34, r: 12, t: 16, b: 24 };
  svg.textContent = "";

  const plotW = W - PAD.l - PAD.r;
  const plotH = H - PAD.t - PAD.b;

  if (result.degenerate || result.ts.length === 0) {
    const msg = el("text", { x: W / 2, y: H / 2, "text-anchor": "middle", class: "trace-label" });
    msg.textContent = "Set a non-zero leading coefficient to see the response.";
    svg.appendChild(msg);
    return;
  }

  const ys = result.ys;
  let yMax = Math.max(...ys.map(Math.abs));
  if (!Number.isFinite(yMax) || yMax === 0) yMax = 1;
  yMax *= 1.15;

  const x = (t) => PAD.l + (t / result.tMax) * plotW;
  const y = (v) => PAD.t + plotH / 2 - (v / yMax) * (plotH / 2);

  // horizontal grid
  for (let i = 0; i <= 4; i++) {
    const gy = PAD.t + (i / 4) * plotH;
    svg.appendChild(el("line", { x1: PAD.l, y1: gy, x2: W - PAD.r, y2: gy, class: "trace-grid" }));
  }
  // vertical grid
  for (let i = 0; i <= 6; i++) {
    const gx = PAD.l + (i / 6) * plotW;
    svg.appendChild(el("line", { x1: gx, y1: PAD.t, x2: gx, y2: PAD.t + plotH, class: "trace-grid" }));
  }

  // zero axis
  svg.appendChild(el("line", { x1: PAD.l, y1: y(0), x2: W - PAD.r, y2: y(0), class: "trace-axis" }));

  // axis labels
  const yTop = el("text", { x: PAD.l - 6, y: PAD.t + 4, "text-anchor": "end", class: "trace-label" });
  yTop.textContent = fmt(yMax);
  svg.appendChild(yTop);

  const yZero = el("text", { x: PAD.l - 6, y: y(0) + 4, "text-anchor": "end", class: "trace-label" });
  yZero.textContent = "0";
  svg.appendChild(yZero);

  const tEnd = el("text", { x: W - PAD.r, y: H - 6, "text-anchor": "end", class: "trace-label" });
  tEnd.textContent = `t = ${fmt(result.tMax)} s`;
  svg.appendChild(tEnd);

  // the curve
  const d = ys
    .map((v, i) => `${i === 0 ? "M" : "L"}${x(result.ts[i]).toFixed(2)},${y(v).toFixed(2)}`)
    .join(" ");
  const path = el("path", { d, class: "trace-curve" });
  svg.appendChild(path);

  if (animate && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const len = path.getTotalLength ? path.getTotalLength() : 1200;
    path.style.setProperty("--len", len);
    path.style.strokeDasharray = len;
    path.classList.add("drawing");
  }

  if (result.diverged) {
    const warn = el("text", { x: W - PAD.r, y: PAD.t + 12, "text-anchor": "end", class: "trace-label" });
    warn.textContent = "response diverges";
    svg.appendChild(warn);
  }
}
