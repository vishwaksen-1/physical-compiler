// viewer.js – renders ExperimentOutput with JSON toggle

export function renderExperimentOutput(data, container) {
  // Clear container
  container.innerHTML = '';

  // Description (from data.experiment_description)
  const desc = data.experiment_description || 'No description available.';
  const descDiv = document.createElement('div');
  descDiv.className = 'description-text';
  descDiv.textContent = desc;
  container.appendChild(descDiv);

  // Toggle button
  const toggleBtn = document.createElement('button');
  toggleBtn.className = 'toggle-btn';
  toggleBtn.textContent = 'Show raw JSON';
  container.appendChild(toggleBtn);

  // JSON pre block (hidden initially)
  const pre = document.createElement('pre');
  pre.className = 'hidden';
  pre.textContent = JSON.stringify(data, null, 2);
  container.appendChild(pre);

  // Toggle handler
  toggleBtn.addEventListener('click', () => {
    const isHidden = pre.classList.contains('hidden');
    pre.classList.toggle('hidden');
    toggleBtn.textContent = isHidden ? 'Hide raw JSON' : 'Show raw JSON';
  });
}