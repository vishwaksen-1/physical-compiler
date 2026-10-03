1. **Quantum harmonic oscillator** : \(\ddot x+\omega^2x=0\) : Second-order linear ODE with constant coefficient; \(x(t)=A\cos\omega t+B\sin\omega t\).

2. **Damped quantum oscillator / Caldeira–Leggett limit** : \(\ddot x+2\gamma\dot x+\omega_0^2x=0\) : Second-order linear ODE with constant coefficients; underdamped motion gives \(x(t)\sim e^{-\gamma t}\cos(\omega_dt+\phi)\).

3. **Driven quantum oscillator** : \(\ddot x+2\gamma\dot x+\omega_0^2x=F_0\cos\omega t\) : Second-order linear forced ODE; resonance and transient response are directly analog-computable.

4. **Time-dependent Schrödinger equation** : \(i\hbar\partial_t\psi=\hat H\psi\) : First-order linear PDE in time; spatial discretization converts it into coupled first-order ODEs.

5. **1D stationary Schrödinger equation** : \(-\frac{\hbar^2}{2m}\psi''+V(x)\psi=E\psi\) : Second-order linear ODE; equivalently \(\psi''+\frac{2m}{\hbar^2}(E-V)\psi=0\).

6. **Quantum particle in constant potential** : \(\psi''+k^2\psi=0\) : Second-order linear constant-coefficient ODE; \(k=\sqrt{2m(E-V)}/\hbar\).

7. **Quantum tunnelling through barrier** : \(\psi''-\kappa^2\psi=0\) : Second-order linear ODE with constant coefficient inside rectangular barrier; \(\psi=Ae^{\kappa x}+Be^{-\kappa x}\).

8. **WKB quantum tunnelling** : \(\psi''-\kappa^2(x)\psi=0\) : Second-order linear variable-coefficient ODE; semiclassical amplitude scales as \(e^{-\int\kappa(x)\,dx}\).

9. **Quantum particle in harmonic potential** : \(\psi''+\frac{2m}{\hbar^2}(E-\frac12m\omega^2x^2)\psi=0\) : Second-order linear variable-coefficient ODE; Hermite-function eigenmodes.

10. **Hydrogen radial Schrödinger equation** : \(u''+\left[\frac{2m}{\hbar^2}(E-V(r))-\frac{\ell(\ell+1)}{r^2}\right]u=0\) : Second-order linear variable-coefficient ODE with singular \(1/r^2\) term.

11. **Quantum well bound state** : \(\psi''+k^2(x)\psi=0\) : Piecewise second-order linear ODE; interface conditions determine discrete eigenvalues.

12. **Quantum scattering** : \(\psi''+k^2(x)\psi=0\) : Second-order linear variable-coefficient ODE; transmission and reflection emerge from boundary matching.

13. **Two-level Rabi oscillation** : \(\dot c_1=-i\frac{\Omega}{2}c_2,\quad\dot c_2=-i\frac{\Omega}{2}c_1\) : Coupled first-order linear ODE system; populations oscillate at Rabi frequency.

14. **Detuned Rabi dynamics** : \(\dot{\mathbf c}=-iH_{\rm eff}\mathbf c/\hbar\) : Coupled first-order linear ODE system with constant coefficients; eigenvalues determine generalized Rabi frequency.

15. **Optical Bloch equations** : \(\dot u=-\Delta v-\gamma_2u,\;\dot v=\Delta u-\Omega w-\gamma_2v,\;\dot w=\Omega v-\gamma_1(w-w_{\rm eq})\) : Coupled first-order linear ODEs; models driven two-level atoms with relaxation.

16. **Bloch spin precession** : \(\dot{\mathbf M}=\gamma\,\mathbf M\times\mathbf B\) : Three coupled first-order nonlinear ODEs; constant \(\mathbf B\) gives Larmor precession.

17. **Bloch equation with relaxation** : \(\dot{\mathbf M}=\gamma\mathbf M\times\mathbf B-\left(\frac{M_x}{T_2},\frac{M_y}{T_2},\frac{M_z-M_0}{T_1}\right)\) : Coupled first-order nonlinear ODEs with linear relaxation.

18. **Quantum master equation — Lindblad dynamics** : \(\dot\rho=-\frac{i}{\hbar}[H,\rho]+\sum_j\gamma_j\left(L_j\rho L_j^\dagger-\frac12\{L_j^\dagger L_j,\rho\}\right)\) : First-order linear ODE in density-matrix components; finite-dimensional truncation gives matrix ODE.

19. **Qubit amplitude damping** : \(\dot\rho_{ee}=-\Gamma\rho_{ee}\) : First-order linear ODE; \(\rho_{ee}(t)=\rho_{ee}(0)e^{-\Gamma t}\).

20. **Qubit pure dephasing** : \(\dot\rho_{eg}=-\Gamma_\phi\rho_{eg}\) : First-order linear ODE; coherence decays exponentially.

21. **Quantum Zeno dynamics** : \(\dot P(t)\) determined by repeated-measurement survival dynamics; short-time \(P(t)\approx1-(\Delta H)^2t^2/\hbar^2\) : Non-exponential short-time dynamics; useful nonlinear/time-dependent analog target after suitable state reduction.

22. **Quantum wavepacket propagation** : \(i\hbar\dot{\boldsymbol\psi}=H\boldsymbol\psi\) : Coupled first-order linear ODE system after spatial discretization; analog integrator network can represent Hamiltonian matrix.

23. **Gross–Pitaevskii / Bose–Einstein condensate** : \(i\hbar\partial_t\psi=\left[-\frac{\hbar^2}{2m}\nabla^2+V+g|\psi|^2\right]\psi\) : Nonlinear Schrödinger PDE; spatial discretization produces coupled nonlinear ODEs.

24. **Stationary Gross–Pitaevskii condensate** : \(-\frac{\hbar^2}{2m}\psi''+V(x)\psi+g|\psi|^2\psi=\mu\psi\) : Second-order nonlinear ODE; cubic nonlinearity can be represented by nonlinear analog circuitry.

25. **Nonlinear Schrödinger wave propagation** : \(i\psi_t+\alpha\psi_{xx}+\beta|\psi|^2\psi=0\) : Nonlinear dispersive PDE; spatial-mode truncation gives coupled nonlinear ODEs.

26. **Quantum probability-current equation** : \(j=\frac{\hbar}{m}\operatorname{Im}(\psi^*\psi')\) with \(\partial_t|\psi|^2+\partial_xj=0\) : First-order conservation PDE; discretization gives coupled rate equations.

27. **Fokker–Planck equation for nanoscale Brownian motion** : \(\partial_tP=-\partial_x[f(x)P]+D\partial_x^2P\) : Linear second-order PDE; finite-volume or finite-difference discretization yields first-order ODEs.

28. **Ornstein–Uhlenbeck Brownian particle** : \(\dot x=-\gamma x+\sqrt{2D}\,\xi(t)\) : First-order linear stochastic differential equation; deterministic analog solves mean dynamics \(\dot{\langle x\rangle}=-\gamma\langle x\rangle\).

29. **Langevin equation for nanoparticle motion** : \(m\ddot x+\gamma\dot x+U'(x)=\eta(t)\) : Second-order nonlinear stochastic ODE; inertial and overdamped regimes give different analog circuits.

30. **Overdamped Brownian dynamics** : \(\gamma\dot x=-U'(x)+\eta(t)\) : First-order nonlinear stochastic ODE; gradient-flow structure is directly realizable with integrator + nonlinear-force blocks.

31. **Double-well molecular switching** : \(\dot x=-ax+bx^3+\eta(t)\) : First-order nonlinear stochastic ODE; cubic feedback creates bistability.

32. **Chemical reaction kinetics at molecular scale** : \(\dot x_i=f_i(x_1,\ldots,x_n)\) : Coupled first-order nonlinear ODE system; mass-action reactions produce polynomial nonlinearities.

33. **Unimolecular decay** : \(\dot N=-kN\) : First-order linear ODE; \(N=N_0e^{-kt}\).

34. **Bimolecular reaction** : \(\dot A=-kA^2\) : First-order nonlinear ODE; \(A(t)=A_0/(1+kA_0t)\).

35. **Michaelis–Menten molecular kinetics** : \(\dot S=-\frac{V_{\max}S}{K_M+S}\) : First-order nonlinear rational ODE; saturation emerges from algebraic nonlinear feedback.

36. **Lotka–Volterra molecular reaction analogue** : \(\dot x=ax-bxy,\quad\dot y=-cy+dxy\) : Coupled first-order nonlinear ODE system; quadratic cross-coupling generates oscillations.

37. **Reaction–diffusion in nanoscale chemistry** : \(\partial_tu=D\nabla^2u+f(u)\) : Semilinear parabolic PDE; spatial discretization gives coupled first-order nonlinear ODEs.

38. **Nanoscale heat diffusion** : \(\partial_tT=\alpha\nabla^2T+Q/(\rho c)\) : Linear parabolic PDE; spatial discretization gives RC-network-equivalent first-order ODEs.

39. **1D thermal diffusion in nanowire** : \(\partial_tT=\alpha T_{xx}\) : Linear second-order PDE; discretization gives \(\dot T_i=\alpha(T_{i+1}-2T_i+T_{i-1})/\Delta x^2\).

40. **Phonon relaxation** : \(\dot n=-\frac{n-n_{\rm eq}}{\tau}\) : First-order linear ODE; exponential relaxation with time constant \(\tau\).

41. **Two-temperature model for ultrafast materials** : \(C_e\dot T_e=-G(T_e-T_l)+P(t),\quad C_l\dot T_l=G(T_e-T_l)\) : Coupled first-order linear ODEs; models electron–lattice energy transfer after ultrafast excitation.

42. **Electron diffusion in semiconductor** : \(\partial_t n=D_n\nabla^2n-\frac{n-n_0}{\tau_n}\) : Linear reaction–diffusion PDE; discretization gives coupled first-order ODEs.

43. **Hole diffusion** : \(\partial_t p=D_p\nabla^2p-\frac{p-p_0}{\tau_p}\) : Linear reaction–diffusion PDE; spatial discretization yields RC-like analog network.

44. **Semiconductor drift–diffusion** : \(\partial_t n=\frac1q\nabla\cdot J_n+G-R,\quad J_n=q\mu_n nE+qD_n\nabla n\) : Nonlinear PDE system coupled to electrostatics; discretization gives nonlinear ODE network.

45. **Poisson equation in semiconductor depletion region** : \(\phi''=-\rho(\phi)/\epsilon\) : Second-order nonlinear ODE; charge density introduces exponential or algebraic nonlinearities.

46. **Debye screening** : \(\phi''=\phi/\lambda_D^2\) : Second-order linear constant-coefficient ODE; \(\phi\propto e^{-x/\lambda_D}\).

47. **Poisson–Boltzmann electrostatics** : \(\phi''=\frac{2qn_0}{\epsilon}\sinh\left(\frac{q\phi}{k_BT}\right)\) : Second-order nonlinear ODE; hyperbolic-sine feedback models ionic screening.

48. **Josephson junction phase dynamics** : \(C\frac{\Phi_0}{2\pi}\ddot\phi+\frac1R\frac{\Phi_0}{2\pi}\dot\phi+I_c\sin\phi=I_{\rm bias}\) : Second-order nonlinear ODE; canonical superconducting analog-computer target.

49. **Josephson junction — normalized RCSJ model** : \(\beta_c\ddot\phi+\dot\phi+\sin\phi=i\) : Second-order nonlinear ODE with sinusoidal nonlinearity; maps directly to capacitor, resistor and nonlinear feedback.

50. **Josephson plasma oscillation** : \(\ddot\phi+\omega_p^2\sin\phi=0\) : Second-order nonlinear ODE; small-angle limit gives \(\ddot\phi+\omega_p^2\phi=0\).

51. **SQUID phase dynamics** : \(\ddot\phi+\alpha\dot\phi+\sin\phi+\beta\sin(2\pi f-\phi)=i(t)\) : Second-order nonlinear ODE; multiple sinusoidal feedback terms encode superconducting interference.

52. **Nanoelectromechanical resonator** : \(m\ddot x+\gamma\dot x+kx=F_{\rm ext}(t)\) : Second-order linear forced ODE; standard damped oscillator analog.

53. **Duffing nanomechanical resonator** : \(m\ddot x+\gamma\dot x+kx+\alpha x^3=F\cos\omega t\) : Second-order nonlinear ODE; cubic feedback produces amplitude-dependent resonance.

54. **MEMS/NEMS nonlinear beam mode** : \(\ddot q+\gamma\dot q+\omega_0^2q+\alpha q^3=F(t)\) : Second-order nonlinear ODE after modal reduction; reduced mechanics becomes single analog-computable state equation.

55. **Optomechanical cavity** : \(\dot a=(i\Delta-\kappa/2)a+igxa+\sqrt{\kappa_{\rm ex}}s_{\rm in}\) : First-order nonlinear complex ODE; optical amplitude couples multiplicatively to mechanical displacement.

56. **Linear optical cavity** : \(\dot a=-(\kappa/2+i\Delta)a+\sqrt{\kappa_{\rm ex}}s_{\rm in}\) : First-order linear complex ODE; exponential cavity ring-down.

57. **Cavity ring-down** : \(\dot I=-\kappa I\) : First-order linear ODE; \(I(t)=I_0e^{-\kappa t}\).

58. **Coupled optical cavities / coupled resonators** : \(\dot{\mathbf a}=M\mathbf a+\mathbf s(t)\) : Coupled first-order linear ODE system; eigenvalues give supermode frequencies and decay rates.

59. **Coupled quantum oscillators** : \(\ddot x_1+\omega_1^2x_1+\kappa x_2=0,\quad\ddot x_2+\omega_2^2x_2+\kappa x_1=0\) : Coupled second-order linear ODEs; normal modes arise from eigenvalues.

60. **Spin–spin exchange dynamics** : \(\dot{\mathbf S}_i=J\,\mathbf S_i\times\mathbf S_j\) : Coupled first-order nonlinear ODEs; classical spin-vector representation approximates finite-spin dynamics.

61. **Landau–Lifshitz magnetization dynamics** : \(\dot{\mathbf M}=-\gamma\mathbf M\times\mathbf H_{\rm eff}-\frac{\alpha\gamma}{M_s}\mathbf M\times(\mathbf M\times\mathbf H_{\rm eff})\) : Coupled first-order nonlinear ODEs; cross products and damping produce magnetic switching dynamics.

62. **Néel magnetization relaxation** : \(\dot m=-\Gamma(m-m_{\rm eq})\) : First-order linear ODE; exponential relaxation between magnetic states.

63. **Spin diffusion** : \(\partial_t\mathbf s=D_s\nabla^2\mathbf s-\mathbf s/\tau_s+\boldsymbol\Omega\times\mathbf s\) : Vector reaction–diffusion PDE; spatial discretization gives coupled first-order ODEs.

64. **Electron plasma oscillation** : \(\ddot x+\omega_p^2x=0\) : Second-order linear ODE; collective electron displacement oscillates at plasma frequency.

65. **Plasma Langmuir-wave mode** : \(\ddot n_k+\omega_p^2n_k=0\) : Second-order linear ODE after Fourier-mode reduction; each spatial Fourier mode behaves as oscillator.

66. **Debye plasma screening** : \(\phi''-\lambda_D^{-2}\phi=0\) : Second-order linear ODE; exponential spatial screening.

67. **Cold-plasma electron motion** : \(m\ddot x=-eE\) : Second-order linear ODE; external electric field directly drives microscopic charge displacement.

68. **Cyclotron motion** : \(m\dot{\mathbf v}=q\,\mathbf v\times\mathbf B\) : Coupled first-order linear ODEs for velocity components; constant magnetic field produces circular motion.

69. **Charged-particle motion with damping** : \(m\dot{\mathbf v}=q\mathbf v\times\mathbf B-\gamma\mathbf v\) : Coupled first-order linear ODEs; combines cyclotron rotation with exponential damping.

70. **Molecular vibrational mode** : \(\ddot q+2\gamma\dot q+\omega_0^2q=F(t)/m\) : Second-order linear ODE; normal vibrational coordinate behaves as damped oscillator.

71. **Anharmonic molecular vibration** : \(\ddot q+\omega_0^2q+\alpha q^2+\beta q^3=F(t)\) : Second-order nonlinear ODE; polynomial potential produces nonlinear spectroscopy effects.

72. **Molecular rotational dynamics** : \(I\ddot\theta=\tau(\theta,t)\) : Second-order ODE; torque law determines rotational dynamics.

73. **Dipole orientation in electric field** : \(I\ddot\theta+\gamma\dot\theta+pE\sin\theta=0\) : Second-order nonlinear ODE; pendulum-equivalent microscopic dipole dynamics.

74. **Brownian rotational diffusion** : \(\partial_tP=D_r\partial_\theta^2P\) : Linear diffusion PDE on angular coordinate; Fourier-mode decomposition gives independent first-order ODEs.

75. **Nanoparticle rotational Langevin dynamics** : \(I\ddot\theta+\gamma_r\dot\theta=\tau_{\rm ext}+\eta_r(t)\) : Second-order stochastic ODE; overdamped limit reduces to first-order Langevin equation.

76. **Molecular conformational transition** : \(\gamma\dot q=-\frac{dU}{dq}\) : First-order nonlinear gradient-flow ODE; arbitrary molecular potential becomes nonlinear feedback \(U'(q)\).

77. **Kramers escape dynamics** : \(\dot x=-\mu U'(x)+\sqrt{2D}\xi(t)\) : First-order nonlinear stochastic ODE; bistable escape and noise-driven switching.

78. **Chemical oscillator / Brusselator** : \(\dot x=A-(B+1)x+x^2y,\quad\dot y=Bx-x^2y\) : Coupled first-order nonlinear ODEs; cubic reaction-network dynamics generate limit cycles.

79. **Belousov–Zhabotinsky reduced kinetics** : \(\dot{\mathbf x}=\mathbf f(\mathbf x)\) : Coupled nonlinear ODE system; chemical concentrations form dynamical states.

80. **Enzyme autocatalytic kinetics** : \(\dot x=ax+bx^2-cx^3\) : First-order polynomial nonlinear ODE; saturation and bistability arise from competing nonlinear terms.

81. **Nanoresonator parametric excitation** : \(\ddot x+\gamma\dot x+\omega_0^2[1+h\cos(2\omega t)]x=0\) : Second-order linear time-periodic ODE; parametric resonance occurs near \(2\omega\approx2\omega_0\).

82. **Quantum parametric oscillator** : \(\ddot x+\omega^2(t)x=0\) : Second-order linear time-dependent ODE; frequency modulation produces squeezing/amplification.

83. **Parametric Josephson oscillator** : \(\ddot\phi+\alpha\dot\phi+[1+h\cos(\omega t)]\sin\phi=i(t)\) : Second-order nonlinear time-periodic ODE; combines Josephson nonlinearity with parametric driving.

84. **Quantum field mode** : \(\ddot q_k+\omega_k^2q_k=0\) : Second-order linear ODE after spatial Fourier decomposition; each field mode reduces to harmonic oscillator.

85. **Klein–Gordon mode equation** : \(\ddot\phi_k+(k^2+m^2)\phi_k=0\) : Second-order linear constant-coefficient ODE for each Fourier mode.

86. **Dirac equation in 1D** : \(i\hbar\partial_t\psi=(-i\hbar c\alpha\partial_x+\beta mc^2+V)\psi\) : First-order linear PDE; spatial discretization gives coupled first-order complex ODEs.

87. **Pauli spinor in magnetic field** : \(i\hbar\dot\psi=-\mu\,\boldsymbol\sigma\cdot\mathbf B\,\psi\) : First-order linear complex ODE system; equivalent to Bloch-vector precession.

88. **Andreev bound-state dynamics** : \(i\hbar\dot{\mathbf c}=H_{\rm BdG}\mathbf c\) : Coupled first-order linear ODE system; finite Bogoliubov–de Gennes truncation gives matrix dynamics.

89. **Bogoliubov quasiparticle mode** : \(\dot{\mathbf u}=M_{\rm BdG}\mathbf u\) : Coupled first-order linear ODE system; eigenvalues determine quasiparticle frequencies and instabilities.

90. **Quantum transport rate equation** : \(\dot P_i=\sum_j(W_{ij}P_j-W_{ji}P_i)\) : Coupled first-order linear ODE system; transition rates form a Markov generator.

91. **Single-electron tunnelling rate** : \(\dot P_1=-\Gamma P_1+\Gamma'P_0\) : First-order linear ODE; microscopic occupation probability relaxes exponentially toward stationary value.

92. **Quantum-dot occupation dynamics** : \(\dot n=\Gamma_{\rm in}(1-n)-\Gamma_{\rm out}n\) : First-order linear ODE; \(n_{\rm ss}=\Gamma_{\rm in}/(\Gamma_{\rm in}+\Gamma_{\rm out})\).

93. **Coulomb-blockade rate equation** : \(\dot P_N=\sum_{N'}W_{NN'}P_{N'}\) : Coupled first-order linear ODE system; discrete charge states form dynamical variables.

94. **Nanopore ion transport** : \(\partial_t c=Dc_{xx}-\mu zq(c\phi_x)_x+R(c)\) : Nonlinear drift–diffusion–reaction PDE; spatial discretization gives coupled nonlinear ODEs.

95. **Nernst–Planck transport** : \(J=-D\nabla c-\mu zq\,c\nabla\phi,\quad\partial_tc=-\nabla\cdot J\) : Coupled nonlinear PDEs; concentration–electric-field coupling generates nonlinear state equations.

96. **Poisson–Nernst–Planck system** : \(\partial_tc_i=-\nabla\cdot J_i,\quad\nabla^2\phi=-\rho/\epsilon\) : Coupled nonlinear PDE/elliptic system; discretization produces differential-algebraic equations.

97. **Nanochannel concentration relaxation** : \(\dot c=-kc\) : First-order linear ODE under well-mixed approximation; exponential molecular depletion.

98. **Surface adsorption — Langmuir model** : \(\dot\theta=k_aP(1-\theta)-k_d\theta\) : First-order linear ODE in coverage \(\theta\); adsorption approaches equilibrium exponentially.

99. **Nonlinear adsorption** : \(\dot\theta=k_aP(1-\theta)^n-k_d\theta^m\) : First-order nonlinear ODE; useful for modeling cooperative surface processes.

100. **Radiative two-level population dynamics** : \(\dot N_2=-A_{21}N_2+B_{12}\rho N_1-B_{21}\rho N_2\) : First-order linear population ODE under \(N_1+N_2=N\); spontaneous and stimulated transitions compete.

101. **Laser rate equations** : \(\dot N=P-\frac{N}{\tau}-G(N)S,\quad\dot S=\Gamma G(N)S-\frac{S}{\tau_p}+\beta\frac{N}{\tau}\) : Coupled first-order nonlinear ODEs; canonical microscopic optoelectronic dynamical system.

102. **Semiconductor carrier–photon dynamics** : \(\dot N=I/qV-R(N)-G(N)S,\quad\dot S=\Gamma G(N)S+ \beta R_{\rm sp}(N)-S/\tau_p\) : Coupled nonlinear first-order ODEs; models laser turn-on, relaxation oscillations and modulation.

103. **Exciton population dynamics** : \(\dot N_X=G-\frac{N_X}{\tau_X}-k_{\rm nr}N_X^2\) : First-order nonlinear ODE; linear radiative decay plus bimolecular annihilation.

104. **Exciton–exciton annihilation** : \(\dot N=-k_1N-k_2N^2\) : First-order nonlinear ODE; crossover from exponential to inverse-time-like decay.

105. **Carrier recombination** : \(\dot n=-An-Bn^2-Cn^3\) : First-order polynomial nonlinear ODE; Shockley–Read–Hall, radiative and Auger channels appear as successive powers.

106. **Optical polarization / Maxwell–Bloch reduction** : \(\dot P=-\gamma_\perp P+i\Delta P+i\alpha Ew\) : First-order linear/nonlinear complex ODE; microscopic polarization couples to field and population inversion.

107. **Maxwell wave equation in dielectric microstructure** : \(\partial_t^2E=c^2\nabla^2E/\epsilon_r\) : Second-order linear PDE; Fourier/modal decomposition converts each mode into oscillator ODE.

108. **Photonic-crystal mode amplitude** : \(\dot a=-i\omega a-\kappa a+\sum_jg_jb_j\) : Coupled first-order linear ODEs; finite-mode truncation produces matrix evolution.

109. **Acoustic nanomode** : \(\ddot q+2\gamma\dot q+\omega_m^2q=F_{\rm ac}(t)\) : Second-order linear forced ODE; mechanical phonon mode behaves as damped oscillator.

110. **Nonlinear acoustic nanomode** : \(\ddot q+\gamma\dot q+\omega_m^2q+\alpha q^3=F(t)\) : Second-order nonlinear ODE; Duffing-type phonon dynamics.

111. **Quantum Brownian oscillator** : \(\ddot x+\int_0^t\Gamma(t-\tau)\dot x(\tau)d\tau+\omega_0^2x=\xi(t)\) : Second-order integro-differential stochastic equation; memory kernel replaces Markovian damping.

112. **Viscoelastic nanoscale mode** : \(m\ddot x+\int_0^tK(t-\tau)\dot x(\tau)d\tau+kx=F(t)\) : Second-order integro-differential equation; internal material memory appears as convolution.

113. **Fractional nanoscale relaxation** : \(D_t^\alpha x=-\lambda x,\quad0<\alpha<1\) : Fractional first-order differential equation; Mittag–Leffler relaxation replaces exponential decay.

114. **Fractional diffusion** : \(\partial_t^\alpha u=D\nabla^2u\) : Fractional diffusion PDE; anomalous microscopic transport produces non-exponential temporal scaling.

115. **Anomalous molecular diffusion** : \(\dot x=\eta(t)\) with \(\langle x^2(t)\rangle\propto t^\alpha\) : Stochastic differential model with non-Brownian scaling; fractional/generalized Langevin formulations give explicit dynamical equations.

116. **Generalized Langevin molecular dynamics** : \(m\ddot x+\int_0^tK(t-\tau)\dot x(\tau)d\tau=F(x)+\eta(t)\) : Second-order stochastic integro-differential equation; microscopic bath memory enters through \(K(t)\).

117. **Molecular population transfer** : \(\dot P_i=\sum_jk_{ij}P_j-\sum_jk_{ji}P_i\) : Coupled first-order linear ODEs; kinetic-network dynamics reduce molecular transitions to matrix evolution.

118. **Förster energy-transfer kinetics** : \(\dot N_D=-k_DN_D-k_FN_D\) : First-order linear ODE; donor population decays through intrinsic and transfer channels.

119. **Excited-state population cascade** : \(\dot N_1=-k_1N_1,\quad\dot N_2=k_1N_1-k_2N_2\) : Coupled first-order linear ODEs; sequential molecular relaxation.

120. **Quantum annealing / transverse-field two-state system** : \(i\hbar\dot\psi=[-\Gamma(t)\sigma_x-\epsilon(t)\sigma_z]\psi\) : First-order linear time-dependent ODE system; controllable coefficients encode time-dependent quantum dynamics.
