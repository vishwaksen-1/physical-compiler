// app.js – connects builder and viewer, submits to /api/compile

import { buildEquationSpec } from './builder.js';
import { renderExperimentOutput } from './viewer.js';

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('equation-form');
  const resultsSection = document.getElementById('results');
  const resultsContent = document.getElementById('results-content');

  // Generate coefficient inputs based on initial order
  function updateCoefficients(order) {
    const container = document.getElementById('coefficients-container');
    container.innerHTML = '';
    // derivative orders: from highest to lowest for display
    for (let i = order; i >= 0; i--) {
      const div = document.createElement('div');
      div.className = 'field';
      const label = document.createElement('label');
      const suffix = i === 0 ? '' : `'`.repeat(i);
      label.textContent = `a${i} (y${suffix})`;
      const input = document.createElement('input');
      input.type = 'number';
      input.step = 'any';
      input.name = `a${i}`;
      input.value = i === order ? '1' : '0'; // default highest coefficient 1, others 0
      div.appendChild(label);
      div.appendChild(input);
      container.appendChild(div);
    }

    // Show/hide y'(0) field based on order
    const yprimeContainer = document.getElementById('yprime0-container');
    if (order >= 2) {
      yprimeContainer.style.display = 'block';
    } else {
      yprimeContainer.style.display = 'none';
    }
  }

  // Update forcing parameter fields based on type
  function updateForcingParams(type) {
    const container = document.getElementById('forcing-params');
    container.innerHTML = '';
    // Common fields for sin/cos/step/impulse
    const addField = (labelText, name, type = 'number', value = 1) => {
      const div = document.createElement('div');
      div.className = 'field';
      const label = document.createElement('label');
      label.textContent = labelText;
      const input = document.createElement('input');
      input.type = type;
      input.name = name;
      if (type === 'number') {
        input.step = 'any';
        input.value = value;
      } else {
        input.value = value;
      }
      div.appendChild(label);
      div.appendChild(input);
      container.appendChild(div);
    };

    switch (type) {
      case 'sin':
      case 'cos':
        addField('Amplitude', 'amp', 'number', 1);
        addField('Frequency', 'freq', 'number', 1);
        addField('Phase', 'phase', 'number', 0);
        break;
      case 'step':
      case 'impulse':
        addField('Amplitude', 'amp', 'number', 1);
        addField('Time', 'time', 'number', 0);
        break;
      case 'polynomial':
        addField('Degree', 'degree', 'number', 1);
        break;
      case 'custom_expr':
        addField('Expression (e.g., t**2 + 1)', 'custom-expr', 'text', '');
        break;
      default:
        // zero/const: no params
        break;
    }
  }

  // Initial setup
  const orderSelect = document.getElementById('order');
  updateCoefficients(parseInt(orderSelect.value, 10));
  updateForcingParams(document.getElementById('forcing-type').value);

  // Event listeners
  orderSelect.addEventListener('change', (e) => {
    updateCoefficients(parseInt(e.target.value, 10));
  });

  document.getElementById('forcing-type').addEventListener('change', (e) => {
    updateForcingParams(e.target.value);
  });

  // Submit handler
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const equationSpec = buildEquationSpec(formData);

    // Build the request payload (exactly one of raw_text/builder_state)
    const payload = {
      raw_text: null,
      builder_state: equationSpec, // web builder produces an EquationSpec directly
      config: {
        candidate_selection_mode: 'deterministic_top_rank',
        candidate_seed: null
      }
    };

    try {
      const response = await fetch('/api/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Compilation failed');
      }
      const result = await response.json();
      // Show results section
      resultsSection.style.display = 'block';
      renderExperimentOutput(result, resultsContent);
    } catch (error) {
      alert(`Error: ${error.message}`);
      console.error(error);
    }
  });
});