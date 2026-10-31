function renderCelestialBody(el, type, slotIndex) {
  el.className = `celestial-body ${type}`;
  el.innerHTML = "";

  const posPresets = [
    { top: `${rand(8, 35)}%`, left: `${rand(52, 78)}%` },
    { top: `${rand(52, 78)}%`, left: `${rand(8, 42)}%` }
  ];
  const pos = posPresets[slotIndex % posPresets.length];
  el.style.top = pos.top;
  el.style.left = pos.left;
  el.style.position = "absolute";
  el.style.borderRadius = "50%";
  el.style.pointerEvents = "none";

  let size;
  if (type === "galaxy") size = Math.floor(rand(85, 135));
  else if (type === "blackhole") size = Math.floor(rand(55, 105));
  else if (type === "starsystem") size = Math.floor(rand(50, 90));
  else size = Math.floor(rand(38, 85)); // planet

  el.style.width = `${size}px`;
  el.style.height = `${size}px`;

  if (type === "planet") {
    const hues = ["210, 60%, 55%", "6, 70%, 55%", "160, 65%, 45%", "270, 60%, 60%", "45, 80%, 55%"];
    const hue = hues[Math.floor(Math.random() * hues.length)];
    el.style.background = `radial-gradient(circle at 35% 30%, hsl(${hue}) 0%, hsl(${hue.split(",")[0]}, 40%, 15%) 80%)`;
    el.style.boxShadow = `0 0 18px rgba(255,255,255,0.2), inset -6px -6px 12px rgba(0,0,0,0.65)`;
    el.style.animation = `planet-drift ${rand(30, 50)}s ease-in-out infinite alternate`;
  } else if (type === "galaxy") {
    el.style.background = `radial-gradient(ellipse at center, rgba(255,240,200,0.95) 0%, rgba(140,80,255,0.65) 35%, rgba(60,120,255,0.3) 60%, transparent 75%)`;
    el.style.boxShadow = `0 0 35px rgba(140,80,255,0.55)`;
    el.style.animation = `galaxy-spin ${rand(40, 80)}s linear infinite`;

    const spiral = document.createElement("div");
    spiral.className = "galaxy-spiral";
    spiral.style.position = "absolute";
    spiral.style.inset = "-15%";
    spiral.style.borderRadius = "50%";
    spiral.style.background = `conic-gradient(from 0deg, transparent 0deg, rgba(242,184,75,0.45) 60deg, transparent 120deg, rgba(111,216,232,0.45) 240deg, transparent 300deg)`;
    spiral.style.filter = "blur(4px)";
    el.appendChild(spiral);
  } else if (type === "starsystem") {
    el.style.background = `radial-gradient(circle, #FFFFFF 0%, #F2B84B 35%, rgba(242,184,75,0.4) 65%, transparent 100%)`;
    el.style.boxShadow = `0 0 25px #F2B84B, 0 0 50px rgba(242,184,75,0.5)`;
    el.style.animation = `starsystem-pulse ${rand(3, 6)}s ease-in-out infinite alternate`;

    const starlet = document.createElement("div");
    starlet.className = "starlet-orbit";
    starlet.style.position = "absolute";
    starlet.style.inset = "-30%";
    starlet.style.animation = `orbit-spin ${rand(8, 15)}s linear infinite`;
    starlet.innerHTML = `<div style="width: 8px; height: 8px; background: #6FD8E8; border-radius: 50%; box-shadow: 0 0 8px #6FD8E8;"></div>`;
    el.appendChild(starlet);
  } else if (type === "blackhole") {
    el.style.background = `#000000`;
    el.style.boxShadow = `0 0 0 3px rgba(242,184,75,0.85), 0 0 22px #F2B84B, 0 0 48px #6FD8E8, inset 0 0 15px rgba(242,184,75,0.85)`;
    el.style.animation = `blackhole-pulse ${rand(4, 7)}s ease-in-out infinite alternate`;

    const ring = document.createElement("div");
    ring.className = "accretion-ring";
    ring.style.position = "absolute";
    ring.style.inset = "-25%";
    ring.style.borderRadius = "50%";
    ring.style.border = "2px solid rgba(242, 184, 75, 0.65)";
    ring.style.boxShadow = "0 0 15px #F2B84B";
    ring.style.transform = "rotateX(70deg)";
    el.appendChild(ring);
  }
}

export function buildStarfield(container) {
  if (!container) return;

  const celestialTypes = ["planet", "galaxy", "starsystem", "blackhole"];
  const chosen1 = celestialTypes[Math.floor(Math.random() * celestialTypes.length)];
  const chosen2 = celestialTypes[Math.floor(Math.random() * celestialTypes.length)];

  if (container.children.length > 0) {
    // Re-shuffle existing celestial body instances on session change
    const existingBodies = container.querySelectorAll(".celestial-body");
    if (existingBodies.length >= 2) {
      renderCelestialBody(existingBodies[0], chosen1, 0);
      renderCelestialBody(existingBodies[1], chosen2, 1);
      return;
    }
  }

  function generateBoxShadow(n) {
    let value = `${Math.floor(Math.random()*2000)}px ${Math.floor(Math.random()*2000)}px #FFF`;
    for(let i = 2; i <= n; i++) {
      value += `, ${Math.floor(Math.random()*2000)}px ${Math.floor(Math.random()*2000)}px #FFF`;
    }
    return value;
  }

  // Parallax stars
  const pSmall = document.createElement("div");
  pSmall.className = "parallax-layer";
  pSmall.style.width = "1px"; pSmall.style.height = "1px";
  pSmall.style.animationDuration = `${rand(40, 60)}s`;
  pSmall.style.boxShadow = generateBoxShadow(Math.floor(rand(50, 100)));
  container.appendChild(pSmall);

  const pMed = document.createElement("div");
  pMed.className = "parallax-layer";
  pMed.style.width = "2px"; pMed.style.height = "2px";
  pMed.style.animationDuration = `${rand(80, 120)}s`;
  pMed.style.boxShadow = generateBoxShadow(Math.floor(rand(20, 50)));
  container.appendChild(pMed);

  const pBig = document.createElement("div");
  pBig.className = "parallax-layer";
  pBig.style.width = "3px"; pBig.style.height = "3px";
  pBig.style.animationDuration = `${rand(120, 180)}s`;
  pBig.style.boxShadow = generateBoxShadow(Math.floor(rand(10, 20)));
  container.appendChild(pBig);

  // 2 random celestial body instances (planets, galaxies, starsystems, blackholes)
  const cb1 = document.createElement("div");
  renderCelestialBody(cb1, chosen1, 0);
  container.appendChild(cb1);

  const cb2 = document.createElement("div");
  renderCelestialBody(cb2, chosen2, 1);
  container.appendChild(cb2);

  // Shooting stars
  const shootingCount = Math.floor(rand(1, 4));
  for (let i = 0; i < shootingCount; i++) {
    const star = document.createElement("div");
    star.className = "shooting-star";
    star.style.top = `${rand(10, 80)}%`;
    star.style.left = "-100px";
    star.style.animationDelay = `${rand(0, 10)}s`;
    star.style.animationDuration = `${rand(3, 8)}s`;
    container.appendChild(star);
  }
}

export function buildAtomicField(container) {
  if (!container || container.children.length > 0) return;

  const floaters = document.createElement("div");
  floaters.id = "quantum-floaters";
  floaters.style.width = "100%";
  floaters.style.height = "100%";
  floaters.style.position = "absolute";
  
  const numBalls = Math.floor(rand(6, 12));
  for (let i = 0; i < numBalls; i++) {
    const ball = document.createElement("div");
    ball.className = "floating-shape";
    const size = rand(10, 25);
    ball.style.width = `${size}vmin`;
    ball.style.height = `${size}vmin`;
    ball.style.top = `${rand(10, 80)}%`;
    ball.style.left = `${rand(10, 80)}%`;
    ball.style.color = Math.random() > 0.5 ? "#7CF7C4" : "#FF6BD6"; // Match Antman palette
    ball.style.boxShadow = `${Math.random() > 0.5 ? 40 : -40}vmin 0 5.5vmin currentColor`;
    ball.style.transformOrigin = `${rand(-25, 25)}vw ${rand(-25, 25)}vh`;
    ball.style.animationDuration = `${rand(25, 60)}s`;
    ball.style.animationDelay = `-${rand(0, 40)}s`;
    ball.style.opacity = "0.4";
    floaters.appendChild(ball);
  }
  container.appendChild(floaters);
}

export function playQuantumCompile(container) {
  if (prefersReducedMotion()) return;
  const floaters = container.querySelector("#quantum-floaters");
  if (floaters) floaters.style.display = "none";

  const swirlWrap = document.createElement("div");
  swirlWrap.className = "quantum-swirl-wrap";

  const total = 100;
  for (let i = 0; i < total; i++) {
    const tri = document.createElement("div");
    tri.className = "swirl-tri";
    const size = Math.random() * 50;
    const rot = Math.random() * 360;
    // Pinks and teals
    const hue = Math.random() > 0.5 ? rand(150, 180) : rand(280, 330);
    tri.style.borderTop = `${size}px solid hsla(${hue}, 100%, 60%, 1)`;
    tri.style.borderRight = `${size}px solid transparent`;
    tri.style.borderLeft = `${size}px solid transparent`;
    tri.style.marginLeft = `-${size/2}px`;
    tri.style.marginTop = `-${size/2}px`;
    
    swirlWrap.appendChild(tri);

    tri.animate([
      { opacity: 1, transform: `rotate(${rot * 1.5}deg) translate3d(${rand(0, 1000)}px, ${rand(0, 1000)}px, 1000px) scale(1)` },
      { opacity: 0, transform: `rotate(${rot}deg) translate3d(0,0,-1500px) scale(0)` }
    ], {
      duration: 3000,
      iterations: Infinity,
      delay: i * -(3000/total)
    });
  }

  container.appendChild(swirlWrap);

  setTimeout(() => {
    swirlWrap.remove();
    if (floaters) floaters.style.display = "block";
  }, 3000);
}

export function playRipple(originEvent) {
  if (prefersReducedMotion()) return;

  const godTab = document.querySelector('[data-theme-tab="celestial"]');
  const rect = godTab ? godTab.getBoundingClientRect() : (originEvent?.target?.getBoundingClientRect?.() || null);
  const x = rect ? rect.left + rect.width / 2 : window.innerWidth / 2;
  const y = rect ? rect.top + rect.height / 2 : window.innerHeight / 2;
  const maxRadius = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y));

  // Fixed colors, randomized order per GodMode session
  const fixedPalette = [
    { color: "#F2B84B", fill: "rgba(242, 184, 75, 0.25)" },
    { color: "#6FD8E8", fill: "rgba(111, 216, 232, 0.22)" },
    { color: "#B87CFF", fill: "rgba(184, 124, 255, 0.20)" }
  ];

  const shuffled = [...fixedPalette].sort(() => Math.random() - 0.5);

  const rippleDuration = 1500;
  const staggerDelay = 150;

  shuffled.forEach((config, idx) => {
    const delay = idx * staggerDelay;
    const overlay = document.createElement("div");
    overlay.className = "mode-ripple";
    overlay.style.setProperty("--ripple-x", `${x}px`);
    overlay.style.setProperty("--ripple-y", `${y}px`);
    overlay.style.setProperty("--ripple-radius", `${maxRadius}px`);
    overlay.style.setProperty("--ripple-color", config.color);
    overlay.style.setProperty("--ripple-fill", config.fill);
    overlay.style.animationDelay = `${delay}ms`;
    overlay.style.animationDuration = `${rippleDuration}ms`;
    document.body.appendChild(overlay);

    overlay.addEventListener("animationend", () => overlay.remove(), { once: true });
    setTimeout(() => {
      if (overlay.parentNode) overlay.remove();
    }, delay + rippleDuration + 200);
  });
}

export function playGlitchSqueeze() {
  if (prefersReducedMotion()) return;
  document.documentElement.classList.add("glitch-squeeze");
  setTimeout(() => {
    document.documentElement.classList.remove("glitch-squeeze");
    document.documentElement.style.filter = "";
  }, 650);
}

function prefersReducedMotion() {
  return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function rand(min, max) { return min + Math.random() * (max - min); }

