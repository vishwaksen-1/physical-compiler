/**
 * viewer.js — renders an ExperimentOutput (INTERFACE_CONTRACTS.md §5) into
 * the apparatus panel.
 *
 * The structural priority here is the mapping: which equation coefficient
 * became which physical component, with what value and what unit. That table
 * is the product. Everything else (derivation trace, raw JSON) is folded into
 * disclosures so it's available without competing for attention.
 */

import { buildWavePath } from "./wavepath.js";

const DOMAIN_LABEL = {
  mechanical: "mechanical apparatus",
  electrical: "electrical circuit",
  thermal: "thermal apparatus",
  optomechanical: "optomechanical apparatus",
  magnetic: "magnetic-resonance apparatus",
  other: "apparatus",
};



export function renderCompiling(root) {
  root.textContent = "";
  const d = buildWavePath({ viewWidth: 280, period: 40, amplitude: 8, center: 22 });
  const box = document.createElement("div");
  box.className = "compiling";
  box.innerHTML = `
    <svg viewBox="0 0 280 44" preserveAspectRatio="none" aria-hidden="true">
      <path class="probe" d="${d}" fill="none"/>
    </svg>
    <p>Searching the registry for apparatus that obey this equation…</p>
  `;
  root.appendChild(box);
}

export function renderError(root, message) {
  root.textContent = "";
  const box = document.createElement("div");
  box.className = "notice";
  box.innerHTML = `
    <h3>That didn't compile</h3>
    <p></p>
  `;
  box.querySelector("p").textContent = message;
  root.appendChild(box);
}

export function renderOutput(root, output, models) {
  root.textContent = "";

  const selected = output.selected_candidate;
  if (!selected) {
    const box = document.createElement("div");
    box.className = "notice notice-fallback";
    box.innerHTML = `<h3>Can't compile this one yet</h3><p></p>`;
    box.querySelector("p").textContent =
      output.experiment_description ||
      "This equation's class isn't in the registry yet.";
    root.appendChild(box);
    return;
  }

  root.appendChild(buildApparatus(output, selected, models));

  const cautions = buildCautions(output.warnings);
  if (cautions) root.appendChild(cautions);

  const alternatives = buildAlternatives(output, models);
  if (alternatives) root.appendChild(alternatives);
}

/* ------------------------------------------------------------------ parts */

function buildApparatus(output, candidate, models) {
  const model = models.get(candidate.model_id);
  const displayName = model?.display_name ?? candidate.model_id;
  const domain = DOMAIN_LABEL[model?.domain] ?? "apparatus";

  const section = document.createElement("article");
  section.className = "apparatus";

  const head = document.createElement("div");
  head.className = "apparatus-head";
  head.innerHTML = `
    <div>
      <h3 class="apparatus-name"></h3>
      <span class="apparatus-domain"></span>
    </div>
    <span class="verdict" data-status="${candidate.verification_status}"></span>
  `;
  head.querySelector(".apparatus-name").textContent = displayName;
  head.querySelector(".apparatus-domain").textContent = domain;
  head.querySelector(".verdict").textContent = verdictLabel(candidate);
  section.appendChild(head);

  const body = document.createElement("div");
  body.className = "apparatus-body";

  // The natural-language experiment description is the actual deliverable
  // of this project (deterministic DE -> NL experiment writeup) -- it leads.
  if (output.experiment_description) {
    const recipe = document.createElement("div");
    recipe.className = "recipe";
    const p = document.createElement("p");
    p.textContent = output.experiment_description;
    recipe.appendChild(p);
    body.appendChild(recipe);
  }

  // The fill-in-the-blanks worksheet: the same template, with the
  // compiler's own solved numbers dropped into each blank.
  body.appendChild(buildFillInBlanks(candidate, output.description_blanks));

  // The apparatus image is a secondary reference figure, not the headline
  // -- it comes after the description and worksheet, not before them.
  // Prefers a real, validated model photo; falls back to an honest
  // placeholder (with a caption explaining why) rather than the old
  // hand-drawn SVG schematics, per the human's request to move to images.
  const artwork = output.build_instructions?.artwork;
  if (artwork?.url) {
    body.appendChild(buildArtwork(artwork, displayName));
  }

  const steps = candidate.transformation_trace?.symbolic_derivation_steps ?? [];
  if (steps.length) {
    body.appendChild(
      disclosure("How these values were derived", (container) => {
        const ol = document.createElement("ol");
        ol.className = "steps";
        for (const step of steps) {
          const li = document.createElement("li");
          li.textContent = step;
          ol.appendChild(li);
        }
        container.appendChild(ol);
      })
    );
  }

  const components = output.build_instructions?.components ?? [];
  if (components.length) {
    body.appendChild(
      disclosure("What you'd need to build it", (container) => {
        const ul = document.createElement("ul");
        ul.className = "steps";
        for (const c of components) {
          const li = document.createElement("li");
          li.textContent = c;
          ul.appendChild(li);
        }
        container.appendChild(ul);

        const bi = output.build_instructions;
        if (bi?.estimated_cost_usd != null || bi?.estimated_build_time_hours != null) {
          const meta = document.createElement("p");
          meta.className = "alt-params";
          const bits = [];
          if (bi.estimated_build_time_hours != null) bits.push(`about ${bi.estimated_build_time_hours} h to build`);
          if (bi.estimated_cost_usd != null) bits.push(`roughly $${bi.estimated_cost_usd}`);
          meta.textContent = bits.join(" · ");
          container.appendChild(meta);
        }
      })
    );
  }

  body.appendChild(
    disclosure("Full compiler output (JSON)", (container) => {
      const pre = document.createElement("pre");
      pre.className = "json-dump";
      pre.textContent = JSON.stringify(output, null, 2);
      container.appendChild(pre);
    })
  );

  section.appendChild(body);
  return section;
}

/**
 * The apparatus image box. Exactly two window shapes exist — square (1:1)
 * and widescreen (16:9), per the human's spec — chosen from the server's
 * own validated `artwork.ratio`, never computed client-side (the frontend
 * doesn't have the image's real pixel dimensions, only the server does,
 * from src/physics/models/artwork.py). `object-fit: contain` (in CSS)
 * scales the image up or down to fill that fixed window without cropping
 * or distorting it — "stretch smaller images to fit, keep the ratio
 * fixed" is exactly what that CSS property does.
 */
function buildArtwork(artwork, displayName) {
  const ratioClass = artwork.ratio === "16:9" ? "artwork-16-9" : "artwork-1-1";

  const figure = document.createElement("figure");
  figure.className = `artwork-box ${ratioClass}`;

  const img = document.createElement("img");
  img.src = artwork.url;
  img.alt = artwork.is_placeholder ? "No photo available yet for this apparatus" : displayName;
  img.loading = "lazy";
  figure.appendChild(img);

  if (artwork.is_placeholder) {
    const caption = document.createElement("figcaption");
    caption.className = "artwork-caption";
    caption.textContent = artwork.reason || "No photo submitted for this apparatus yet.";
    figure.appendChild(caption);
  }

  return figure;
}

function buildFillInBlanks(candidate, blanks) {
  const wrap = document.createElement("div");
  wrap.className = "blanks";

  const heading = document.createElement("p");
  heading.className = "blanks-heading";
  heading.textContent = "Fill in the setup:";
  wrap.appendChild(heading);

  const list = document.createElement("ul");
  list.className = "blanks-list";

  // Prefer the server's own ordered template data; fall back to a plain
  // sorted dump of parameter_values if it's missing for any reason (e.g. an
  // older API response), so the worksheet never just renders empty.
  const rows = blanks?.length
    ? blanks
    : Object.entries(candidate.parameter_values ?? {})
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([symbol, value]) => ({ symbol, label: symbol, template: symbol, value: formatValue(value), unit: "" }));

  for (const row of rows) {
    const li = document.createElement("li");
    li.className = "blank-row";
    li.innerHTML = `
      <span class="blank-template"></span>
      <span class="blank-fill"><span class="blank-value"></span><span class="blank-unit"></span></span>
    `;
    li.querySelector(".blank-template").textContent = `${row.template}:`;
    li.querySelector(".blank-value").textContent = row.value;
    li.querySelector(".blank-unit").textContent = row.unit ? ` ${row.unit}` : "";
    list.appendChild(li);
  }

  wrap.appendChild(list);
  return wrap;
}

function buildCautions(warnings) {
  if (!warnings?.length) return null;

  return disclosureBlock("Before you build it", () => {
    const ul = document.createElement("ul");
    ul.className = "cautions";
    for (const w of warnings) {
      const li = document.createElement("li");
      const isSafety = w.startsWith("Safety:");
      li.dataset.kind = isSafety ? "safety" : "note";
      li.textContent = isSafety ? w.slice("Safety:".length).trim() : w;
      ul.appendChild(li);
    }
    return ul;
  });
}

function buildAlternatives(output, models) {
  const alts = output.alternative_candidates ?? [];
  if (!alts.length) return null;

  const section = document.createElement("section");
  section.className = "alternatives";

  const h3 = document.createElement("h3");
  h3.textContent = "The same equation, built differently";
  section.appendChild(h3);

  const p = document.createElement("p");
  p.textContent =
    "These machines are made of different stuff and measure different quantities, " +
    "yet each one is governed by the equation you entered.";
  section.appendChild(p);

  const grid = document.createElement("div");
  grid.className = "alt-grid";

  for (const alt of alts) {
    const model = models.get(alt.model_id);
    const card = document.createElement("div");
    card.className = "alt-card";

    const name = document.createElement("h4");
    name.textContent = model?.display_name ?? alt.model_id;

    const params = document.createElement("span");
    params.className = "alt-params";
    params.textContent = Object.entries(alt.parameter_values ?? {})
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => `${k} = ${formatValue(v)}`)
      .join("   ");

    const status = document.createElement("span");
    status.className = "alt-status";
    status.dataset.status = alt.verification_status;
    status.textContent = verdictLabel(alt);

    card.append(name, params, status);
    grid.appendChild(card);
  }

  section.appendChild(grid);
  return section;
}

/* ----------------------------------------------------------------- helpers */

function disclosure(summaryText, fill) {
  const details = document.createElement("details");
  details.className = "disclosure";
  const summary = document.createElement("summary");
  summary.textContent = summaryText;
  details.appendChild(summary);
  fill(details);
  return details;
}

function disclosureBlock(title, buildContent) {
  const section = document.createElement("section");
  section.className = "alternatives";
  const h3 = document.createElement("h3");
  h3.textContent = title;
  section.appendChild(h3);
  section.appendChild(buildContent());
  return section;
}

function verdictLabel(candidate) {
  switch (candidate.verification_status) {
    case "EXACT": return "Verified exact";
    case "APPROXIMATE": return "Close, not exact";
    case "FAILED": return "Doesn't hold";
    default: return candidate.verification_status;
  }
}

function formatValue(v) {
  if (typeof v !== "number" || !Number.isFinite(v)) return String(v);
  if (v === 0) return "0";
  const a = Math.abs(v);
  if (a >= 1e5 || a < 1e-3) return v.toExponential(3);
  return String(Math.round(v * 1e5) / 1e5);
}
