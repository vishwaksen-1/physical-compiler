/**
 * schematics.js — line drawings of each apparatus in the registry.
 *
 * One drawing per model_id, keyed to the registry in src/physics/models/.
 * These are the "what am I actually building" answer: a schematic reads
 * faster than a parts list, and the whole point of the product is that
 * these five drawings all obey the same equation.
 *
 * Adding a model to the registry without adding a drawing here is fine —
 * `schematicFor()` falls back to null and the results panel just omits the
 * figure rather than breaking.
 */

const SCHEMATICS = {
  /* ------------------------------------------------ mass-spring-damper */
  mass_spring_damper: () => `
    <svg viewBox="0 0 440 170" role="img" aria-label="Mass on a rail, connected to a wall by a spring and a dashpot">
      <!-- wall -->
      <line class="schematic-line" x1="40" y1="20" x2="40" y2="140"/>
      ${hatch(40, 20, 140, "left")}
      <!-- spring -->
      <path class="schematic-accent" d="M40 55 h22 l8 -11 l16 22 l16 -22 l16 22 l16 -22 l16 22 l8 -11 h22"/>
      <text class="schematic-label" x="118" y="34">k</text>
      <!-- dashpot -->
      <line class="schematic-line" x1="40" y1="105" x2="92" y2="105"/>
      <rect class="schematic-fill" x="92" y="90" width="42" height="30" rx="2"/>
      <line class="schematic-line" x1="120" y1="95" x2="120" y2="115"/>
      <line class="schematic-line" x1="120" y1="105" x2="180" y2="105"/>
      <text class="schematic-label" x="104" y="140">c</text>
      <!-- mass -->
      <rect class="schematic-fill" x="180" y="48" width="86" height="72" rx="3"/>
      <text class="schematic-label" x="216" y="90">m</text>
      <!-- rail -->
      <line class="schematic-line" x1="150" y1="132" x2="400" y2="132"/>
      ${hatch(150, 132, 400, "below")}
      <!-- displacement arrow -->
      <line class="schematic-accent" x1="286" y1="84" x2="348" y2="84"/>
      <path class="schematic-arrow" d="M348 84 l-8 -5 v10 z"/>
      <text class="schematic-label" x="308" y="74">x</text>
    </svg>`,

  /* -------------------------------------------------------- series RLC */
  series_rlc: () => `
    <svg viewBox="0 0 440 170" role="img" aria-label="Series RLC circuit with a voltage source">
      <!-- loop -->
      <path class="schematic-line" d="M60 46 h48 M172 46 h34 M258 46 h54 M380 46 v78 M380 124 H60 M60 124 V46"/>
      <!-- inductor -->
      <path class="schematic-accent" d="M108 46 a10 10 0 0 1 16 0 a10 10 0 0 1 16 0 a10 10 0 0 1 16 0 a10 10 0 0 1 16 0"/>
      <text class="schematic-label" x="134" y="28">L</text>
      <!-- resistor -->
      <path class="schematic-accent" d="M206 46 l8 -12 l12 24 l12 -24 l12 24 l8 -12"/>
      <text class="schematic-label" x="232" y="28">R</text>
      <!-- capacitor -->
      <path class="schematic-line" d="M312 46 h18 M348 46 h32"/>
      <line class="schematic-accent" x1="330" y1="30" x2="330" y2="62"/>
      <line class="schematic-accent" x1="346" y1="30" x2="346" y2="62"/>
      <text class="schematic-label" x="330" y="80">C</text>
      <!-- source -->
      <circle class="schematic-fill" cx="60" cy="85" r="18"/>
      <path class="schematic-accent" d="M50 85 q5 -8 10 0 t10 0"/>
      <text class="schematic-label" x="14" y="122">V(t)</text>
      <!-- current arrow -->
      <path class="schematic-accent" d="M232 138 h34"/>
      <path class="schematic-arrow" d="M266 138 l-8 -5 v10 z"/>
      <text class="schematic-label" x="242" y="156">i</text>
    </svg>`,

  /* ---------------------------------------------------------- RC circuit */
  rc_circuit: () => `
    <svg viewBox="0 0 440 170" role="img" aria-label="Resistor and capacitor in series with a voltage source">
      <path class="schematic-line" d="M70 50 h60 M212 50 h96 M308 50 v14 M308 106 v18 M308 124 H70 M70 124 V50"/>
      <!-- resistor -->
      <path class="schematic-accent" d="M130 50 l10 -14 l14 28 l14 -28 l14 28 l10 -14"/>
      <text class="schematic-label" x="160" y="30">R</text>
      <!-- capacitor (vertical) -->
      <line class="schematic-accent" x1="288" y1="64" x2="328" y2="64"/>
      <line class="schematic-accent" x1="288" y1="82" x2="328" y2="82"/>
      <text class="schematic-label" x="342" y="80">C</text>
      <!-- source -->
      <circle class="schematic-fill" cx="70" cy="87" r="18"/>
      <path class="schematic-accent" d="M60 87 q5 -8 10 0 t10 0"/>
      <text class="schematic-label" x="8" y="124">V(t)</text>
      <!-- probe -->
      <line class="schematic-line" x1="308" y1="73" x2="392" y2="73" stroke-dasharray="3 3"/>
      <text class="schematic-label" x="360" y="64">V</text>
    </svg>`,

  /* -------------------------------------------------- torsional pendulum */
  torsional_pendulum: () => `
    <svg viewBox="0 0 440 180" role="img" aria-label="Disc suspended on a torsion wire">
      <!-- ceiling -->
      <line class="schematic-line" x1="140" y1="18" x2="300" y2="18"/>
      ${hatch(140, 18, 300, "above")}
      <!-- wire -->
      <line class="schematic-accent" x1="220" y1="18" x2="220" y2="92"/>
      <text class="schematic-label" x="232" y="60">k</text>
      <!-- disc -->
      <ellipse class="schematic-fill" cx="220" cy="112" rx="88" ry="24"/>
      <line class="schematic-line" x1="132" y1="112" x2="132" y2="126"/>
      <line class="schematic-line" x1="308" y1="112" x2="308" y2="126"/>
      <path class="schematic-line" d="M132 126 a88 24 0 0 0 176 0"/>
      <text class="schematic-label" x="212" y="118">I</text>
      <!-- rotation arrow -->
      <path class="schematic-accent" d="M318 148 a104 30 0 0 0 -60 22"/>
      <path class="schematic-arrow" d="M258 170 l10 -3 l-5 -8 z"/>
      <text class="schematic-label" x="330" y="146">θ</text>
    </svg>`,

  /* --------------------------------------------------- Newton's cooling */
  newtons_cooling: () => `
    <svg viewBox="0 0 440 170" role="img" aria-label="Heated vessel cooling toward ambient temperature">
      <!-- vessel -->
      <path class="schematic-line" d="M150 38 v86 a46 16 0 0 0 92 0 V38"/>
      <ellipse class="schematic-fill" cx="196" cy="38" rx="46" ry="15"/>
      <path class="schematic-wash" d="M152 62 v62 a44 15 0 0 0 88 0 V62 a44 15 0 0 1 -88 0 z"/>
      <text class="schematic-label" x="188" y="102">T</text>
      <!-- thermometer -->
      <line class="schematic-line" x1="272" y1="30" x2="272" y2="104"/>
      <circle class="schematic-fill" cx="272" cy="112" r="9"/>
      <line class="schematic-accent" x1="272" y1="70" x2="272" y2="104"/>
      <line class="schematic-line" x1="266" y1="44" x2="278" y2="44"/>
      <line class="schematic-line" x1="266" y1="58" x2="278" y2="58"/>
      <line class="schematic-line" x1="266" y1="72" x2="278" y2="72"/>
      <!-- ambient -->
      <path class="schematic-accent" d="M318 56 q12 -10 24 0 t24 0" stroke-dasharray="4 4"/>
      <path class="schematic-accent" d="M318 76 q12 -10 24 0 t24 0" stroke-dasharray="4 4"/>
      <text class="schematic-label" x="330" y="108">T_env</text>
      <!-- heat escaping -->
      <path class="schematic-accent" d="M252 46 q10 -12 20 -4"/>
      <path class="schematic-arrow" d="M272 42 l1 -9 l-8 5 z"/>
    </svg>`,
};

/** Cross-hatching along a wall or ground line. */
function hatch(from, coord, to, side) {
  const marks = [];
  const step = 12;
  if (side === "left") {
    for (let y = coord; y < to; y += step) {
      marks.push(`<line class="schematic-hatch" x1="${from}" y1="${y}" x2="${from - 9}" y2="${y + 9}"/>`);
    }
  } else if (side === "below") {
    for (let x = from; x < to; x += step) {
      marks.push(`<line class="schematic-hatch" x1="${x}" y1="${coord}" x2="${x - 9}" y2="${coord + 9}"/>`);
    }
  } else if (side === "above") {
    for (let x = from; x < to; x += step) {
      marks.push(`<line class="schematic-hatch" x1="${x}" y1="${coord}" x2="${x - 9}" y2="${coord - 9}"/>`);
    }
  }
  return marks.join("");
}

export function schematicFor(modelId) {
  const build = SCHEMATICS[modelId];
  return build ? build() : null;
}

export function hasSchematic(modelId) {
  return Boolean(SCHEMATICS[modelId]);
}
