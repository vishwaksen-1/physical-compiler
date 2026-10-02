/**
 * wavepath.js — computes a seamlessly-looping sine-wave SVG path at
 * runtime, instead of baking a few thousand precomputed coordinates into
 * source (which is what this used to do, and looked exactly as bad in the
 * codebase as it sounds).
 *
 * "Seamless" here means: the path spans two full widths of the viewBox
 * (`2 * viewWidth`), and the CSS animation translates it by exactly one
 * viewWidth -- so as long as `viewWidth` is a whole multiple of `period`,
 * the loop has no visible seam. Both call sites below pick numbers that
 * divide evenly for exactly that reason.
 */

export function buildWavePath({ viewWidth, period, amplitude, center, step = 2 }) {
  const totalWidth = viewWidth * 2;
  const points = [];
  for (let x = 0; x <= totalWidth; x += step) {
    const y = center + amplitude * Math.sin((2 * Math.PI * x) / period);
    points.push(`${x} ${round4(y)}`);
  }
  return `M${points.join(" L")}`;
}

function round4(v) {
  return Math.round(v * 10000) / 10000;
}
