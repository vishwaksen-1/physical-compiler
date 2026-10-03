export function buildStarfield(container) {
  if (!container || container.children.length > 0) return;

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
  setTimeout(() => {
    document.documentElement.classList.remove("glitch-squeeze");
    const filters = ["hue-rotate(90deg)", "invert(0.2)", "hue-rotate(-90deg)", "invert(0.1)"];
    document.documentElement.style.filter = filters[Math.floor(Math.random() * filters.length)];
  }, 650);
}

function prefersReducedMotion() {
  return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function rand(min, max) { return min + Math.random() * (max - min); }
