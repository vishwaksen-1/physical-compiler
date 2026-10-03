export function buildStarfield(container) {
  if (!container || container.children.length > 0) return;

  for (const layer of [
    { count: 90, sizeRange: [1, 2], speed: 90, opacity: [0.3, 0.7] },
    { count: 40, sizeRange: [2, 3], speed: 55, opacity: [0.5, 1] },
  ]) {
    const div = document.createElement("div");
    div.className = "starfield-layer";
    div.style.animationDuration = `${layer.speed}s`;
    for (let i = 0; i < layer.count; i++) {
      const star = document.createElement("span");
      star.className = "star";
      const size = rand(...layer.sizeRange);
      star.style.width = star.style.height = `${size}px`;
      // Placed across TWO screen-widths so a -100% translateX drift loops
      // seamlessly -- same seamless-tiling idea as wavepath.js's sine wave.
      star.style.left = `${rand(0, 200)}%`;
      star.style.top = `${rand(0, 100)}%`;
      star.style.opacity = String(rand(...layer.opacity));
      star.style.animationDelay = `${rand(0, 4)}s`;
      star.style.animationDuration = `${rand(2, 5)}s`;
      div.appendChild(star);
    }
    container.appendChild(div);
  }

  // A couple of decorative planets.
  for (const p of [
    { size: 46, top: "12%", left: "78%", hue: "210, 60%, 55%" },
    { size: 26, top: "68%", left: "12%", hue: "6, 70%, 55%" },
  ]) {
    const planet = document.createElement("div");
    planet.className = "planet";
    planet.style.width = planet.style.height = `${p.size}px`;
    planet.style.top = p.top;
    planet.style.left = p.left;
    planet.style.background = `radial-gradient(circle at 35% 30%, hsl(${p.hue}) 0%, hsl(${p.hue.split(",")[0]}, 40%, 20%) 75%)`;
    planet.style.animationDuration = `${rand(30, 50)}s`;
    container.appendChild(planet);
  }
}

const SVG_NS = "http://www.w3.org/2000/svg";

function buildAtomIcon() {
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.setAttribute("viewBox", "0 0 60 60");
  svg.classList.add("atom-icon");

  const nucleus = document.createElementNS(SVG_NS, "circle");
  nucleus.setAttribute("cx", "30"); nucleus.setAttribute("cy", "30"); nucleus.setAttribute("r", "4");
  nucleus.classList.add("atom-nucleus");
  svg.appendChild(nucleus);

  for (const rotation of [0, 60, 120]) {
    const group = document.createElementNS(SVG_NS, "g");
    group.classList.add("atom-orbit-group");
    group.style.transformOrigin = "30px 30px";
    group.setAttribute("transform", `rotate(${rotation} 30 30)`);

    const ellipse = document.createElementNS(SVG_NS, "ellipse");
    ellipse.setAttribute("cx", "30"); ellipse.setAttribute("cy", "30");
    ellipse.setAttribute("rx", "24"); ellipse.setAttribute("ry", "9");
    ellipse.classList.add("atom-orbit");
    group.appendChild(ellipse);

    const electron = document.createElementNS(SVG_NS, "circle");
    electron.setAttribute("r", "2.4");
    electron.classList.add("atom-electron");
    const anim = document.createElementNS(SVG_NS, "animateMotion");
    anim.setAttribute("dur", `${rand(3, 6).toFixed(1)}s`);
    anim.setAttribute("repeatCount", "indefinite");
    anim.setAttribute("path", "M 6,30 A 24 9 0 1 1 54,30 A 24 9 0 1 1 6,30");
    electron.appendChild(anim);
    group.appendChild(electron);
  }
  return svg;
}

export function buildAtomicField(container) {
  if (!container || container.children.length > 0) return;

  const positions = [
    [10, 20], [85, 15], [75, 80], [25, 70], [45, 45],
    [5, 85], [95, 55], [35, 5]
  ];
  for (const [left, top] of positions) {
    const icon = buildAtomIcon();
    icon.style.left = `${left}%`;
    icon.style.top = `${top}%`;
    icon.style.width = icon.style.height = `${rand(40, 80)}px`;
    icon.style.animationDuration = `${rand(14, 28)}s`;
    icon.style.animationDirection = Math.random() < 0.5 ? "normal" : "reverse";
    container.appendChild(icon);
  }
}

export function playRipple(originEvent) {
  if (prefersReducedMotion()) return;
  const rect = originEvent?.target?.getBoundingClientRect?.();
  const x = rect ? rect.left + rect.width / 2 : window.innerWidth / 2;
  const y = rect ? rect.top + rect.height / 2 : window.innerHeight / 2;
  const maxRadius = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y));

  const overlay = document.createElement("div");
  overlay.className = "mode-ripple";
  overlay.style.setProperty("--ripple-x", `${x}px`);
  overlay.style.setProperty("--ripple-y", `${y}px`);
  overlay.style.setProperty("--ripple-radius", `${maxRadius}px`);
  document.body.appendChild(overlay);

  overlay.addEventListener("animationend", () => overlay.remove(), { once: true });
  setTimeout(() => overlay.remove(), 1200); // safety net if animationend never fires
}

export function playGlitchSqueeze() {
  if (prefersReducedMotion()) return;
  document.documentElement.classList.add("glitch-squeeze");
  setTimeout(() => document.documentElement.classList.remove("glitch-squeeze"), 650);
}

function prefersReducedMotion() {
  return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function rand(min, max) { return min + Math.random() * (max - min); }
