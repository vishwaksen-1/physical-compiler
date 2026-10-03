1. **Free particle** : \(m\ddot{x}=0\) : Second-order homogeneous ODE with constant coefficients; zero restoring/dissipative terms.

2. **Simple harmonic oscillator (mass–spring)** : \(\ddot{x}+\omega_0^2x=0\) : Second-order homogeneous ODE with constant coefficients; sinusoidal oscillation.

3. **Damped harmonic oscillator** : \(\ddot{x}+2\gamma\dot{x}+\omega_0^2x=0\) : General second-order homogeneous linear ODE with constant coefficients; underdamped, critically damped, overdamped regimes.

4. **Driven damped oscillator** : \(\ddot{x}+2\gamma\dot{x}+\omega_0^2x=f(t)\) : General second-order linear nonhomogeneous ODE with constant coefficients and arbitrary forcing.

5. **Series RLC circuit** : \(\ddot{q}+\frac{R}{L}\dot q+\frac{1}{LC}q=\frac{V(t)}{L}\) : Second-order linear nonhomogeneous ODE with constant coefficients and external forcing.

6. **LC circuit** : \(\ddot q+\frac{1}{LC}q=0\) : Second-order homogeneous ODE with constant coefficients; electrical analogue of SHM.

7. **RC circuit** : \(\dot V+\frac{1}{RC}V=\frac{V_{\rm in}(t)}{RC}\) : First-order linear nonhomogeneous ODE with constant coefficients.

8. **RL circuit** : \(\dot I+\frac{R}{L}I=\frac{V(t)}{L}\) : First-order linear nonhomogeneous ODE with constant coefficients.

9. **Thermal lumped-capacitance system** : \(\dot T+k(T-T_a)=Q(t)/C\) : First-order linear ODE with constant coefficients; Newtonian heating/cooling.

10. **Ideal pendulum, small-angle** : \(\ddot\theta+\frac{g}{\ell}\theta=0\) : Second-order homogeneous linear ODE with constant coefficients.

11. **Nonlinear pendulum** : \(\ddot\theta+\frac{g}{\ell}\sin\theta=0\) : Second-order nonlinear autonomous ODE.

12. **Projectile under quadratic drag** : \(m\dot{\mathbf v}=\mathbf F_g-c|\mathbf v|\mathbf v\) : Coupled first-order nonlinear ODEs; nonlinear velocity-dependent damping.

13. **Projectile under linear drag** : \(m\dot{\mathbf v}=\mathbf F_g-c\mathbf v\) : Coupled first-order linear nonhomogeneous ODEs with constant coefficients.

14. **Logistic population growth** : \(\dot N=rN\left(1-\frac{N}{K}\right)\) : First-order nonlinear autonomous ODE; quadratic self-limiting growth.

15. **Radioactive decay** : \(\dot N=-\lambda N\) : First-order homogeneous linear ODE with constant coefficient.

16. **Chemical first-order reaction** : \(\dot C=-kC\) : First-order homogeneous linear ODE; exponential decay.

17. **Chemical second-order reaction** : \(\dot C=-kC^2\) : First-order nonlinear ODE; quadratic reaction rate.

18. **Michaelis–Menten reaction** : \(\dot S=-\frac{V_{\max}S}{K_M+S}\) : First-order nonlinear rational ODE; saturating reaction rate.

19. **Lotka–Volterra predator–prey system** : \(\dot x=\alpha x-\beta xy,\quad\dot y=\delta xy-\gamma y\) : Coupled first-order nonlinear ODE system with bilinear interaction terms.

20. **SIR epidemic model** : \(\dot S=-\beta SI,\quad\dot I=\beta SI-\gamma I,\quad\dot R=\gamma I\) : Coupled first-order nonlinear ODE system; bilinear infection dynamics.

21. **Newtonian orbital motion** : \(\ddot{\mathbf r}=-\frac{GM}{r^3}\mathbf r\) : Coupled second-order nonlinear autonomous ODEs; inverse-square central force.

22. **Charged particle in uniform magnetic field** : \(m\dot{\mathbf v}=q\mathbf v\times\mathbf B\) : Coupled first-order linear ODE system with constant coefficients.

23. **Charged particle in electric + magnetic fields** : \(m\dot{\mathbf v}=q(\mathbf E+\mathbf v\times\mathbf B)\) : Coupled first-order affine linear ODE system with constant coefficients.

24. **Falling viscous fluid / Stokes settling** : \(m\dot v=mg-kv\) : First-order linear nonhomogeneous ODE with constant coefficients.

25. **Mixing tank** : \(\dot C=\frac{Q}{V}(C_{\rm in}-C)\) : First-order linear ODE with constant coefficients; conservation-driven concentration dynamics.

26. **Heated stirred tank with heat loss** : \(C\dot T=P-h(T-T_a)\) : First-order affine linear ODE with constant coefficients and constant forcing.

27. **Beam static deflection** : \(EI\,y''''(x)=q(x)\) : Fourth-order linear ODE; spatial boundary-value problem.

28. **Euler–Bernoulli beam vibration** : \(EI\,y_{xxxx}+\rho A\,y_{tt}=f(x,t)\) : Fourth-order-in-space, second-order-in-time linear PDE.

29. **String vibration** : \(y_{tt}=c^2y_{xx}\) : Second-order linear hyperbolic PDE; wave propagation.

30. **Heat conduction in rod** : \(T_t=\alpha T_{xx}\) : Second-order linear parabolic PDE; diffusion.

31. **Laplace electrostatic problem** : \(\nabla^2V=0\) : Second-order linear elliptic PDE; source-free potential field.

32. **Poisson electrostatic problem** : \(\nabla^2V=-\rho/\epsilon\) : Second-order linear nonhomogeneous elliptic PDE.

33. **Diffusion with reaction** : \(C_t=D\nabla^2C-kC\) : Second-order linear PDE with reaction term.

34. **Wave equation with damping** : \(u_{tt}+2\gamma u_t=c^2\nabla^2u\) : Second-order linear PDE with first-order dissipative term.

35. **Electromagnetic wave propagation** : \(\nabla^2\mathbf E-\frac{1}{c^2}\mathbf E_{tt}=0\) : Second-order linear hyperbolic PDE.

36. **Viscous fluid flow — Navier–Stokes** : \(\rho(\mathbf u_t+\mathbf u\cdot\nabla\mathbf u)=-\nabla p+\mu\nabla^2\mathbf u+\mathbf f\) : Coupled nonlinear second-order-in-space, first-order-in-time PDE system.

37. **Heat conduction with internal generation** : \(T_t=\alpha\nabla^2T+\dot q/(\rho c_p)\) : Second-order linear nonhomogeneous parabolic PDE.

38. **Membrane vibration** : \(u_{tt}=c^2\nabla^2u\) : Second-order linear hyperbolic PDE in two spatial dimensions.

39. **Diffusion of solute through medium** : \(C_t=D\nabla^2C\) : Second-order linear homogeneous parabolic PDE.

40. **Pendulum with nonlinear damping** : \(\ddot\theta+b|\dot\theta|\dot\theta+\omega_0^2\sin\theta=0\) : Second-order nonlinear autonomous ODE with nonlinear damping and restoring force.

41. **Duffing oscillator** : \(\ddot x+\delta\dot x+\alpha x+\beta x^3=F\cos\omega t\) : Second-order nonlinear nonhomogeneous ODE; cubic stiffness and periodic forcing.

42. **Van der Pol oscillator** : \(\ddot x-\mu(1-x^2)\dot x+x=0\) : Second-order nonlinear autonomous ODE; amplitude-dependent negative/positive damping.

43. **Furuta pendulum** : Coupled nonlinear second-order ODEs of form \(M(q)\ddot q+C(q,\dot q)\dot q+G(q)=\tau\) : Nonlinear coupled mechanical system with configuration-dependent inertia, Coriolis and gravity terms.

44. **Rotational rigid body — Euler equations** : \(I_1\dot\omega_1+(I_3-I_2)\omega_2\omega_3=\tau_1\), cyclic : Coupled first-order nonlinear ODEs with quadratic state coupling.

45. **Ideal gas piston with nonlinear pressure law** : \(m\ddot x=A\,P(x)-F\) : Second-order nonlinear ODE produced by state-dependent thermodynamic pressure.

46. **Buckling column — Euler model** : \(EI\,y''+P y=0\) : Second-order linear spatial ODE with constant coefficients; eigenvalue/boundary-value problem.

47. **Torsional shaft vibration** : \(J\ddot\theta+c\dot\theta+k\theta=\tau(t)\) : Second-order linear nonhomogeneous ODE with constant coefficients; rotational analogue of damped driven oscillator.

48. **Two-mass spring–damper system** : \(M\ddot{\mathbf x}+C\dot{\mathbf x}+K\mathbf x=\mathbf f(t)\) : Coupled second-order linear ODE system with constant matrices; multiple normal modes.

49. **Transmission line — telegrapher's equations** : \(\partial_xV=-L\partial_tI-RI,\quad\partial_xI=-C\partial_tV-GV\) : Coupled first-order linear PDE system.

50. **Flexible beam / Euler–Bernoulli dynamics** : \(\rho A\,y_{tt}+EI\,y_{xxxx}=q(x,t)\) : Linear fourth-order spatial, second-order temporal PDE; distributed mechanical dynamics.

No. There are many more. The useful classification is by **ODE/PDE structure**, because physical systems can realize almost every standard differential-equation class.

Additional systems, avoiding equation types already represented:

51. **Constant-acceleration motion** : \(\ddot x=a\) : Second-order nonhomogeneous ODE with constant forcing.

52. **Harmonic oscillator with time-varying stiffness** : \(\ddot x+\omega^2(t)x=0\) : Second-order homogeneous linear ODE with variable coefficient.

53. **Parametrically driven pendulum** : \(\ddot\theta+[\,\omega_0^2+a\cos(\Omega t)\,]\theta=0\) : Second-order linear ODE with periodic coefficient.

54. **Foucault pendulum** : \(\ddot x-2\Omega\dot y+\omega_0^2x=0,\quad\ddot y+2\Omega\dot x+\omega_0^2y=0\) : Coupled second-order linear ODEs with gyroscopic coupling.

55. **Gyroscope** : \(I\dot{\boldsymbol\omega}+\boldsymbol\omega\times(I\boldsymbol\omega)=\boldsymbol\tau\) : Coupled first-order nonlinear ODE system with rotational quadratic coupling.

56. **RC transmission / distributed RC line** : \(V_t=D V_{xx}\) : Second-order linear parabolic PDE arising from distributed electrical resistance and capacitance.

57. **Lossy transmission line** : \(V_{xx}=LCV_{tt}+(RC+LG)V_t+RGV\) : Second-order linear PDE with damping and mixed dissipation.

58. **Acoustic pressure in tube** : \(p_{tt}=c^2p_{xx}\) : Second-order linear wave PDE.

59. **Acoustic wave with attenuation** : \(p_{tt}+2\alpha p_t=c^2p_{xx}\) : Second-order linear damped hyperbolic PDE.

60. **Shallow-water waves** : \(\eta_t+h u_x=0,\quad u_t+g\eta_x=0\) : Coupled first-order linear hyperbolic PDE system.

61. **Nonlinear shallow-water flow** : \(\eta_t+[(h+\eta)u]_x=0,\quad u_t+uu_x+g\eta_x=0\) : Coupled first-order nonlinear hyperbolic PDE system.

62. **Burgers fluid** : \(u_t+uu_x=\nu u_{xx}\) : First-order nonlinear, second-order spatial PDE; nonlinear advection plus diffusion.

63. **Reaction–diffusion medium** : \(u_t=D\nabla^2u+f(u)\) : Semilinear parabolic PDE; diffusion plus nonlinear local dynamics.

64. **Fisher population wave** : \(u_t=D u_{xx}+ru(1-u/K)\) : Nonlinear reaction–diffusion PDE combining diffusion and logistic growth.

65. **Nonlinear heat conduction** : \(T_t=\nabla\cdot(k(T)\nabla T)\) : Quasilinear second-order parabolic PDE with state-dependent conductivity.

66. **Nonlinear pendulum with external torque** : \(\ddot\theta+\omega_0^2\sin\theta=\tau(t)/I\) : Second-order nonlinear nonhomogeneous ODE.

67. **Coulomb-friction oscillator** : \(m\ddot x+kx+F_c\,\operatorname{sgn}(\dot x)=F(t)\) : Second-order nonlinear, nonsmooth ODE.

68. **Dry-friction sliding block** : \(m\ddot x=-\mu mg\,\operatorname{sgn}(\dot x)\) : Second-order piecewise-defined nonlinear ODE.

69. **Relativistic free particle** : \(\frac{d}{dt}\left(\frac{m\dot x}{\sqrt{1-\dot x^2/c^2}}\right)=F\) : First-order nonlinear ODE in momentum/velocity.

70. **Charged particle in nonlinear magnetic field** : \(m\dot{\mathbf v}=q\mathbf v\times\mathbf B(\mathbf r)\) : Coupled first-order nonlinear ODE system with position-dependent coefficients.

71. **Diode RC circuit** : \(C\dot V+\frac{V}{R}+I_s(e^{V/V_T}-1)=I_{\rm in}(t)\) : First-order nonlinear nonhomogeneous ODE.

72. **Tunnel-diode circuit** : \(C\dot V=I_{\rm in}-I(V)\) : First-order nonlinear ODE with non-monotonic constitutive relation.

73. **Op-amp integrator** : \(\dot V_{\rm out}=-V_{\rm in}/RC\) : First-order ODE directly implementing temporal integration.

74. **Op-amp differentiator** : \(V_{\rm out}=-RC\,\dot V_{\rm in}\) : First-order differential relation directly implementing differentiation.

75. **PLL phase dynamics** : \(\dot\phi=\Delta\omega-K\sin\phi\) : First-order nonlinear autonomous ODE.

76. **Josephson junction** : \(\ddot\phi+\alpha\dot\phi+\sin\phi=I/I_c\) : Second-order nonlinear driven damped ODE.

77. **Population with harvesting** : \(\dot N=rN(1-N/K)-H(N)\) : First-order nonlinear nonhomogeneous ODE with state-dependent removal.

78. **Chemical autocatalytic reaction** : \(\dot x=kx(A-x)\) : First-order nonlinear ODE with quadratic autocatalytic dynamics.

79. **CSTR nonlinear reactor** : \(\dot C=f(C,T),\quad\dot T=g(C,T)\) : Coupled first-order nonlinear ODE system.

80. **Predator–prey with logistic prey** : \(\dot x=rx(1-x/K)-axy,\quad\dot y=bxy-dy\) : Coupled first-order nonlinear ODEs containing quadratic interactions and saturation.

81. **Two-compartment pharmacokinetic model** : \(\dot{\mathbf C}=A\mathbf C+\mathbf u(t)\) : Coupled first-order linear ODE system with constant matrix coefficients.

82. **Electrical transformer transient** : \(L_1\dot i_1+Mi_2'+R_1i_1=v_1(t)\) etc. : Coupled first-order linear ODE system with inductive coupling.

83. **Coupled LC resonators** : \(\ddot{\mathbf q}+K\mathbf q=0\) : Coupled second-order homogeneous linear ODE system; normal-mode dynamics.

84. **Mass–spring lattice** : \(m\ddot x_n=k(x_{n+1}-2x_n+x_{n-1})\) : Infinite coupled second-order linear ODE system; discrete wave dynamics.

85. **Electrical ladder network** : \(L\ddot q_n+\cdots=0\) : Coupled linear ODE lattice; discrete analogue of wave/telegraph equations.

86. **Elastic rod longitudinal vibration** : \(u_{tt}=c^2u_{xx}\) : Second-order linear hyperbolic PDE.

87. **Euler beam under axial load** : \(EIy''''+Py''+\rho Ay_{tt}=0\) : Fourth-order spatial, second-order temporal linear PDE with prestress.

88. **Plate vibration** : \(D\nabla^4w+\rho h\,w_{tt}=p(x,y,t)\) : Fourth-order spatial, second-order temporal linear PDE.

89. **Kirchhoff–Love plate bending** : \(D\nabla^4w=p(x,y)\) : Fourth-order linear elliptic PDE.

90. **Elasticity of solid body** : \(\rho\mathbf u_{tt}=(\lambda+\mu)\nabla(\nabla\cdot\mathbf u)+\mu\nabla^2\mathbf u+\mathbf f\) : Coupled second-order linear PDE system.

91. **Maxwell electromagnetic system** : \(\nabla\times\mathbf E=-\mathbf B_t,\quad\nabla\times\mathbf H=\mathbf J+\mathbf D_t\) : Coupled first-order linear PDE system.

92. **Ideal incompressible potential flow** : \(\nabla^2\phi=0\) : Second-order linear elliptic PDE.

93. **Nonlinear pendulum chain** : \(\ddot\theta_n+\omega_0^2\sin\theta_n+\kappa(2\theta_n-\theta_{n-1}-\theta_{n+1})=0\) : Coupled nonlinear second-order ODE lattice.

94. **Fermi–Pasta–Ulam lattice** : \(m\ddot x_n=k(x_{n+1}-2x_n+x_{n-1})+\alpha[(x_{n+1}-x_n)^2-(x_n-x_{n-1})^2]\) : Coupled nonlinear second-order ODE system with nonlinear nearest-neighbour coupling.

95. **Lorenz fluid-convection model** : \(\dot x=\sigma(y-x),\quad\dot y=x(\rho-z)-y,\quad\dot z=xy-\beta z\) : Three-dimensional coupled first-order nonlinear autonomous ODE system.

96. **Rössler chemical oscillator** : \(\dot x=-y-z,\quad\dot y=x+ay,\quad\dot z=b+z(x-c)\) : Three-dimensional nonlinear autonomous ODE system.

97. **Van der Pol–Duffing oscillator** : \(\ddot x+\mu(x^2-1)\dot x+\alpha x+\beta x^3=F(t)\) : Second-order nonlinear nonhomogeneous ODE combining nonlinear damping and stiffness.

98. **Nonlinear pendulum with quadratic potential approximation** : \(\ddot x+\alpha x+\beta x^2=0\) : Second-order nonlinear autonomous ODE with polynomial restoring force.

99. **Simple RC spatial diffusion analogue** : \(u_t=D u_{xx}\) : Second-order spatial, first-order temporal linear PDE.

100. **Schrödinger particle in potential** : \(i\hbar\psi_t=-\frac{\hbar^2}{2m}\nabla^2\psi+V\psi\) : First-order temporal, second-order spatial linear PDE.

101. **Gross–Pitaevskii condensate** : \(i\hbar\psi_t=-\frac{\hbar^2}{2m}\nabla^2\psi+V\psi+g|\psi|^2\psi\) : Nonlinear dispersive PDE with cubic nonlinearity.

102. **Nonlinear optical fiber** : \(iA_z+\frac{\beta_2}{2}A_{tt}+\gamma|A|^2A=0\) : Nonlinear dispersive second-order PDE; temporal dispersion plus Kerr nonlinearity.

103. **KdV shallow-water wave** : \(u_t+6uu_x+u_{xxx}=0\) : Nonlinear third-order spatial dispersive PDE.

104. **Beam under distributed nonlinear foundation** : \(EIy''''+ky+\alpha y^3=q(x)\) : Fourth-order nonlinear boundary-value ODE.

105. **Rotating fluid / vorticity equation** : \(\omega_t+\mathbf u\cdot\nabla\omega=\nu\nabla^2\omega\) : Nonlinear advection–diffusion PDE.

106. **Incompressible Euler fluid** : \(\mathbf u_t+\mathbf u\cdot\nabla\mathbf u=-\nabla p/\rho\), \(\nabla\cdot\mathbf u=0\) : First-order nonlinear PDE system with incompressibility constraint.

107. **Black–Scholes financial analogue** : \(V_t+\frac12\sigma^2S^2V_{SS}+rSV_S-rV=0\) : Second-order linear parabolic PDE.
