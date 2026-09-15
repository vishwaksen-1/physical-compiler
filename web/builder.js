// builder.js – builds EquationSpec from form inputs

export function buildEquationSpec(formData) {
  const order = parseInt(formData.get('order'), 10);
  const dependentVar = 'y';
  const independentVars = ['t'];

  // Build terms
  const terms = [];
  // coefficient inputs are named a0, a1, a2
  for (let i = 0; i <= order; i++) {
    const coeff = parseFloat(formData.get(`a${i}`)) || 0;
    if (coeff !== 0) {
      terms.push({
        derivative_order: i,
        wrt: ['t'], // ODE, single independent var
        coefficient: coeff
      });
    }
  }

  // Forcing
  const forcingType = formData.get('forcing-type');
  let forcingParams = {};
  let forcingExpr = null;

  switch (forcingType) {
    case 'zero':
    case 'const':
      // no extra params needed
      break;
    case 'sin':
    case 'cos':
      forcingParams = {
        amplitude: parseFloat(formData.get('amp')) || 1,
        frequency: parseFloat(formData.get('freq')) || 1,
        phase: parseFloat(formData.get('phase')) || 0
      };
      break;
    case 'step':
    case 'impulse':
      forcingParams = {
        amplitude: parseFloat(formData.get('amp')) || 1,
        time: parseFloat(formData.get('time')) || 0
      };
      break;
    case 'polynomial':
      forcingParams = {
        degree: parseInt(formData.get('degree'), 10) || 1,
        coefficients: [1] // simplified; we only store degree
      };
      break;
    case 'custom_expr':
      forcingExpr = formData.get('custom-expr') || '';
      break;
    default:
      break;
  }

  const forcing = {
    type: forcingType,
    params: forcingParams,
    expr: forcingExpr
  };

  // Initial conditions
  const initialConditions = {
    [dependentVar]: parseFloat(formData.get('y0')) || 0
  };
  if (order >= 2) {
    initialConditions[`${dependentVar}prime`] = parseFloat(formData.get('yprime0')) || 0;
  }

  // Boundary conditions – not used in this phase, leave null
  const boundaryConditions = null;

  return {
    spec_version: "1.0",
    domain_type: "ODE",
    independent_vars: independentVars,
    dependent_var: dependentVar,
    order: order,
    terms: terms,
    rhs_forcing: forcing,
    initial_conditions: initialConditions,
    boundary_conditions: boundaryConditions,
    input_source: "web_builder",
    raw_text: null
  };
}