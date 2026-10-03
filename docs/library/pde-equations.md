1. **Heat conduction in metal rod** : \(T_t=\alpha T_{xx}\) : Second-order linear parabolic PDE; thermal diffusion through a one-dimensional solid.

2. **Heat conduction in 3D solid** : \(T_t=\alpha\nabla^2T\) : Second-order linear parabolic PDE; thermal diffusion in three spatial dimensions.

3. **Heat conduction with internal heating** : \(T_t=\alpha\nabla^2T+Q/(\rho c_p)\) : Second-order linear nonhomogeneous parabolic PDE; diffusion plus volumetric heat generation.

4. **Nonlinear heat conduction** : \(T_t=\nabla\cdot[k(T)\nabla T]/(\rho c_p)\) : Quasilinear second-order parabolic PDE; thermal conductivity depends on temperature.

5. **Diffusion of dissolved salt** : \(C_t=D\nabla^2C\) : Second-order linear parabolic PDE; molecular diffusion.

6. **Diffusion with chemical reaction** : \(C_t=D\nabla^2C-kC\) : Linear reaction–diffusion PDE; diffusion combined with first-order decay.

7. **Nonlinear reaction–diffusion medium** : \(u_t=D\nabla^2u+f(u)\) : Semilinear parabolic PDE; spatial diffusion plus nonlinear local kinetics.

8. **Fisher population wave** : \(u_t=D u_{xx}+ru(1-u/K)\) : Nonlinear reaction–diffusion PDE; population growth plus spatial dispersal.

9. **Belousov–Zhabotinsky reaction** : \(\mathbf u_t=D\nabla^2\mathbf u+\mathbf f(\mathbf u)\) : Coupled nonlinear reaction–diffusion PDEs; chemical oscillations and propagating reaction fronts.

10. **Neuronal cortical activity** : \(u_t=D\nabla^2u+f(u)\) : Nonlinear reaction–diffusion PDE; local neural dynamics coupled by spatial diffusion-like connectivity.

11. **Groundwater contaminant transport** : \(C_t+\mathbf v\cdot\nabla C=D\nabla^2C-R(C)\) : Advection–diffusion–reaction PDE; pollutant transport through porous media.

12. **Ocean pollutant dispersion** : \(C_t+\mathbf u\cdot\nabla C=D\nabla^2C\) : Linear advection–diffusion PDE; transport by ocean currents plus diffusion.

13. **Atmospheric pollutant transport** : \(C_t+\mathbf u\cdot\nabla C=\nabla\cdot(D\nabla C)+S\) : Nonhomogeneous advection–diffusion PDE; atmospheric transport with sources.

14. **Ink / dye in flowing water** : \(C_t+\mathbf u\cdot\nabla C=D\nabla^2C\) : Advection–diffusion PDE; moving fluid transports concentration while molecular diffusion smooths it.

15. **String vibration** : \(u_{tt}=c^2u_{xx}\) : Second-order linear hyperbolic PDE; transverse mechanical waves.

16. **Membrane vibration** : \(u_{tt}=c^2\nabla^2u\) : Two-dimensional wave PDE; vibration of stretched membranes.

17. **Acoustic pressure in air** : \(p_{tt}=c^2\nabla^2p\) : Second-order linear hyperbolic PDE; propagation of sound.

18. **Acoustic waves with damping** : \(p_{tt}+2\gamma p_t=c^2\nabla^2p\) : Damped hyperbolic PDE; acoustic propagation with energy loss.

19. **Elastic solid waves** : \(\rho\mathbf u_{tt}=(\lambda+\mu)\nabla(\nabla\cdot\mathbf u)+\mu\nabla^2\mathbf u\) : Coupled second-order linear PDE system; longitudinal and transverse elastic waves.

20. **Euler–Bernoulli beam** : \(\rho A y_{tt}+EIy_{xxxx}=q(x,t)\) : Fourth-order spatial, second-order temporal PDE; distributed beam vibration.

21. **Thin plate vibration** : \(\rho h w_{tt}+D\nabla^4w=p(x,y,t)\) : Fourth-order spatial, second-order temporal PDE; flexural waves in plates.

22. **Torsional wave in shaft** : \(\rho I_p\theta_{tt}=G I_p\theta_{xx}\) : Second-order linear hyperbolic PDE; rotational wave propagation.

23. **Water-surface waves** : \(\eta_{tt}-gh\nabla^2\eta=0\) : Linear wave PDE in shallow-water approximation.

24. **Shallow-water equations** : \(h_t+\nabla\cdot(h\mathbf u)=0,\quad\mathbf u_t+(\mathbf u\cdot\nabla)\mathbf u+g\nabla h=0\) : Coupled nonlinear first-order hyperbolic PDEs; free-surface gravity waves.

25. **Burgers fluid** : \(u_t+uu_x=\nu u_{xx}\) : Nonlinear advection–diffusion PDE; simplified model of viscous fluid flow.

26. **Incompressible Euler fluid** : \(\mathbf u_t+(\mathbf u\cdot\nabla)\mathbf u=-\nabla p/\rho,\quad\nabla\cdot\mathbf u=0\) : Nonlinear first-order PDE system; ideal fluid dynamics.

27. **Navier–Stokes fluid** : \(\rho(\mathbf u_t+\mathbf u\cdot\nabla\mathbf u)=-\nabla p+\mu\nabla^2\mathbf u+\mathbf f\) : Nonlinear second-order spatial, first-order temporal PDE system; viscous fluid dynamics.

28. **Vorticity dynamics** : \(\boldsymbol\omega_t+(\mathbf u\cdot\nabla)\boldsymbol\omega=(\boldsymbol\omega\cdot\nabla)\mathbf u+\nu\nabla^2\boldsymbol\omega\) : Nonlinear advection–stretching–diffusion PDE.

29. **Potential flow** : \(\nabla^2\phi=0\) : Second-order linear elliptic PDE; incompressible irrotational flow.

30. **Compressible Euler gas dynamics** : \(\mathbf U_t+\nabla\cdot\mathbf F(\mathbf U)=0\) : Nonlinear first-order hyperbolic conservation-law system; compressible inviscid gas.

31. **Compressible Navier–Stokes** : \(\mathbf U_t+\nabla\cdot\mathbf F(\mathbf U)=\nabla\cdot\mathbf F_v(\mathbf U,\nabla\mathbf U)\) : Nonlinear hyperbolic–parabolic PDE system; viscous compressible flow.

32. **Traffic flow** : \(\rho_t+(\rho v(\rho))_x=0\) : First-order nonlinear conservation-law PDE; vehicle-density propagation.

33. **Shock-wave propagation** : \(u_t+f(u)_x=0\) : Nonlinear first-order hyperbolic conservation law; discontinuities and shocks can form from smooth initial data.

34. **KdV shallow-water wave** : \(u_t+6uu_x+u_{xxx}=0\) : Nonlinear third-order dispersive PDE; solitary-wave propagation.

35. **Nonlinear Schrödinger wave packet** : \(i\psi_t+\psi_{xx}+g|\psi|^2\psi=0\) : Nonlinear dispersive PDE; wave-packet dispersion and self-focusing.

36. **Optical fiber pulse propagation** : \(iA_z+\frac{\beta_2}{2}A_{tt}+\gamma|A|^2A=0\) : Nonlinear dispersive PDE; optical dispersion balanced by Kerr nonlinearity.

37. **Linear Schrödinger particle** : \(i\hbar\psi_t=-\frac{\hbar^2}{2m}\nabla^2\psi+V\psi\) : First-order temporal, second-order spatial linear PDE; quantum wavefunction evolution.

38. **Gross–Pitaevskii Bose–Einstein condensate** : \(i\hbar\psi_t=-\frac{\hbar^2}{2m}\nabla^2\psi+V\psi+g|\psi|^2\psi\) : Nonlinear dispersive PDE; macroscopic quantum condensate dynamics.

39. **Electrostatic field** : \(\nabla^2V=-\rho/\epsilon\) : Second-order linear elliptic PDE; electric potential generated by charge density.

40. **Source-free electrostatic field** : \(\nabla^2V=0\) : Laplace equation; electrostatic potential in charge-free regions.

41. **Magnetostatic field** : \(\nabla^2\mathbf A=-\mu\mathbf J\) : Second-order linear elliptic PDE for magnetic vector potential under suitable gauge conditions.

42. **Electromagnetic waves in vacuum** : \(\nabla^2\mathbf E-\frac1{c^2}\mathbf E_{tt}=0\) : Second-order linear hyperbolic PDE; electromagnetic-wave propagation.

43. **Maxwell equations** : \(\nabla\times\mathbf E=-\mathbf B_t,\quad\nabla\times\mathbf H=\mathbf J+\mathbf D_t\) : Coupled first-order linear PDE system; full classical electromagnetic dynamics.

44. **Lossy transmission line** : \(V_{xx}=LCV_{tt}+(RC+LG)V_t+RGV\) : Second-order linear hyperbolic PDE with damping and attenuation.

45. **Plasma electrostatic oscillations** : \(\phi_{tt}+\omega_p^2\phi=0\) : Local wave-field equation; plasma electrons oscillate collectively.

46. **Vlasov–Poisson plasma** : \(f_t+\mathbf v\cdot\nabla_xf-\frac qm\nabla\phi\cdot\nabla_vf=0,\quad\nabla^2\phi=-\rho/\epsilon_0\) : Coupled kinetic hyperbolic–elliptic PDE system; collisionless charged-particle ensemble.

47. **Magnetohydrodynamics** : \(\rho(\mathbf u_t+\mathbf u\cdot\nabla\mathbf u)=-\nabla p+\mathbf J\times\mathbf B\), \(\mathbf B_t=\nabla\times(\mathbf u\times\mathbf B)+\eta\nabla^2\mathbf B\) : Coupled nonlinear fluid–electromagnetic PDE system.

48. **Diffusion of magnetic field in conductor** : \(\mathbf B_t=\eta\nabla^2\mathbf B\) : Second-order linear parabolic PDE; resistive magnetic diffusion.

49. **General elasticity** : \(\rho\mathbf u_{tt}=\nabla\cdot\boldsymbol\sigma+\mathbf f\) : Coupled second-order PDE system; deformation and stress evolution in solids.

50. **Linear elastic equilibrium** : \(\nabla\cdot\boldsymbol\sigma+\mathbf f=0\) : Second-order elliptic PDE system; static deformation of solids.

51. **Nonlinear elasticity** : \(\rho\mathbf u_{tt}=\nabla\cdot\mathbf P(\nabla\mathbf u)+\mathbf f\) : Nonlinear second-order PDE; finite deformation of solids.

52. **Porous-media flow — Darcy** : \(\nabla\cdot(K\nabla p)=q\) : Second-order elliptic PDE; pressure distribution in porous material.

53. **Porous-media transport** : \(\phi C_t+\nabla\cdot(\mathbf uC)=\nabla\cdot(D\nabla C)+R\) : Coupled advection–diffusion–reaction PDE; groundwater and reservoir transport.

54. **Oil-reservoir pressure diffusion** : \(\phi c_t p_t=\nabla\cdot(K\nabla p)+q\) : Second-order parabolic PDE; pressure evolution in petroleum reservoirs.

55. **Groundwater flow** : \(S_s p_t=\nabla\cdot(K\nabla p)+Q\) : Diffusion-type PDE for subsurface pressure/head evolution.

56. **Atmospheric fluid dynamics** : \(\frac{D\mathbf u}{Dt}+f\hat z\times\mathbf u=-\frac1\rho\nabla p+\mathbf g\) : Nonlinear first-order PDE system; large-scale atmospheric motion.

57. **Geostrophic flow** : \(f\hat z\times\mathbf u=-\frac1\rho\nabla p\) : First-order spatial PDE/algebraic differential balance; rotation balances pressure-gradient force.

58. **Ocean circulation** : \(\rho(\mathbf u_t+\mathbf u\cdot\nabla\mathbf u)+2\rho\mathbf\Omega\times\mathbf u=-\nabla p+\mu\nabla^2\mathbf u+\rho\mathbf g\) : Rotating Navier–Stokes PDE; planetary-scale ocean dynamics.

59. **Ocean internal waves** : \(\rho_{tt}+N^2\nabla_h^2\rho=0\) : Wave PDE arising from stratified-fluid buoyancy.

60. **Atmospheric gravity waves** : \(u_{tt}-c^2\nabla^2u+N^2u=0\) : Linear dispersive/wave PDE; buoyancy-modified atmospheric oscillations.

61. **Planetary Rossby waves** : \(\partial_t\nabla^2\psi+\beta\psi_x=0\) : First-order temporal, higher-order spatial linear PDE; large-scale waves caused by variation of Coriolis parameter with latitude.

62. **Earth mantle convection** : \(\rho c_pT_t+\rho c_p\mathbf u\cdot\nabla T=k\nabla^2T+Q\) : Advection–diffusion PDE coupled to nonlinear fluid momentum equations; mantle heat transport.

63. **Rayleigh–Bénard convection** : \(T_t+\mathbf u\cdot\nabla T=\kappa\nabla^2T\) plus Navier–Stokes : Coupled nonlinear PDE system; convection driven by thermal instability.

64. **Glacier / ice-sheet flow** : \(\nabla\cdot\boldsymbol\sigma+\rho\mathbf g=0,\quad\partial_t h+\nabla\cdot(h\mathbf u)=a\) : Coupled elliptic and conservation PDEs; continental-scale ice dynamics.

65. **Seismic P/S waves** : \(\rho\mathbf u_{tt}=(\lambda+\mu)\nabla(\nabla\cdot\mathbf u)+\mu\nabla^2\mathbf u\) : Elastic wave PDE; earthquake-generated waves through Earth.

66. **Seismic wave propagation through heterogeneous Earth** : \(\rho(\mathbf x)\mathbf u_{tt}=\nabla\cdot\mathbf C(\mathbf x):\nabla\mathbf u+\mathbf f\) : Variable-coefficient hyperbolic PDE; seismic waves crossing layered/heterogeneous geology.

67. **Earthquake rupture** : \(\rho u_{tt}=\nabla\cdot\sigma\) with frictional boundary/interface law : Nonlinear hyperbolic PDE with nonlinear friction; dynamic fault rupture.

68. **Gravitational potential of galaxy** : \(\nabla^2\Phi=4\pi G\rho\) : Second-order elliptic PDE; Newtonian gravitational field of extended matter.

69. **Self-gravitating collisionless galaxy** : \(f_t+\mathbf v\cdot\nabla_xf-\nabla\Phi\cdot\nabla_vf=0,\quad\nabla^2\Phi=4\pi G\int f\,d^3v\) : Coupled kinetic–elliptic PDE system; evolution of stellar systems.

70. **Cosmological matter fluid** : \(\rho_t+3H\rho+\frac1a\nabla\cdot(\rho\mathbf v)=0\) : First-order nonlinear conservation PDE; matter evolution in expanding universe.

71. **Cosmic fluid momentum equation** : \(\mathbf v_t+H\mathbf v+\frac1a(\mathbf v\cdot\nabla)\mathbf v=-\frac1a\nabla\Phi\) : Nonlinear first-order PDE; peculiar-velocity evolution in expanding universe.

72. **Cosmic Vlasov–Poisson system** : \(f_t+\frac{\mathbf p}{ma^2}\cdot\nabla_xf-m\nabla\Phi\cdot\nabla_pf=0,\quad\nabla^2\Phi=4\pi Ga^2\bar\rho\,\delta\) : Kinetic–elliptic PDE system for collisionless cosmological matter.

73. **Linear cosmological density perturbations** : \(\ddot\delta+2H\dot\delta-4\pi G\rho\delta=0\) : ODE after Fourier/spatial reduction; underlying perturbation theory originates from coupled PDEs.

74. **Einstein field equations** : \(G_{\mu\nu}+\Lambda g_{\mu\nu}=\frac{8\pi G}{c^4}T_{\mu\nu}\) : Nonlinear second-order tensor PDE system; spacetime geometry coupled to matter.

75. **Vacuum Einstein equations** : \(R_{\mu\nu}=0\) : Nonlinear second-order PDE system; gravitational spacetime dynamics without matter.

76. **Weak gravitational waves** : \(\Box h_{\mu\nu}=0\) : Linear second-order hyperbolic PDE; propagation of small spacetime perturbations.

77. **Gravitational waves with source** : \(\Box h_{\mu\nu}=16\pi G\,T_{\mu\nu}/c^4\) : Nonhomogeneous hyperbolic PDE; matter generates propagating spacetime perturbations.

78. **FLRW cosmology** : \(G_{\mu\nu}+\Lambda g_{\mu\nu}=8\pi GT_{\mu\nu}/c^4\rightarrow H^2=\frac{8\pi G}{3}\rho+\frac{\Lambda}{3}-\frac{Kc^2}{a^2}\) : Einstein PDEs reduced to nonlinear ODE by homogeneous/isotropic symmetry.

79. **Gravitational lensing potential** : \(\nabla_\perp^2\psi=2\kappa\) : Two-dimensional Poisson PDE; projected gravitational mass determines light deflection.

80. **Black-hole perturbations** : \(\Psi_{tt}-\Psi_{r_*r_*}+V_{\rm eff}(r)\Psi=0\) : Second-order linear hyperbolic PDE with position-dependent potential; perturbations of black-hole spacetime.

81. **Kerr black-hole perturbations** : \(\mathcal O_{\rm Teukolsky}\Psi=0\) : Second-order variable-coefficient PDE; electromagnetic/gravitational perturbations of rotating black holes.

82. **Relativistic stellar structure** : Einstein equations + fluid conservation : Coupled nonlinear tensor PDE system; under spherical static symmetry reduces to TOV ODEs.

83. **Neutron-star merger** : \(G_{\mu\nu}=8\pi GT_{\mu\nu}/c^4\) coupled to relativistic hydrodynamics : Fully nonlinear Einstein–matter PDE system; dynamical spacetime plus nuclear-density fluid.

84. **Binary-black-hole merger** : \(G_{\mu\nu}=8\pi GT_{\mu\nu}/c^4\) : Fully nonlinear second-order PDE system; numerical relativity evolves strongly dynamical spacetime.

85. **Relativistic hydrodynamics** : \(\nabla_\mu T^{\mu\nu}=0,\quad\nabla_\mu(\rho u^\mu)=0\) : Coupled nonlinear first-order PDE conservation system; relativistic fluid flow.

86. **Accretion disk** : \(\partial_t\Sigma+\frac1r\partial_r(r\Sigma v_r)=0\), with angular-momentum/energy equations : Coupled nonlinear PDEs; evolution of astrophysical disks.

87. **Astrophysical radiation transport** : \(\frac1cI_t+\mathbf n\cdot\nabla I=\eta-\chi I\) : First-order linear transport PDE; propagation, emission and absorption of radiation.

88. **Radiative transfer in stellar atmosphere** : \(\mu\frac{\partial I_\nu}{\partial\tau_\nu}=I_\nu-S_\nu\) : First-order linear PDE/transport equation; radiation through stellar material.

89. **Photon diffusion inside optically thick star** : \(U_t=D\nabla^2U+Q\) : Parabolic diffusion PDE; radiation behaves diffusively when optical depth is large.

90. **Solar plasma MHD** : \(\rho(\mathbf u_t+\mathbf u\cdot\nabla\mathbf u)=-\nabla p+\mathbf J\times\mathbf B+\rho\mathbf g\) plus induction equation : Coupled nonlinear PDE system; plasma dynamics on stellar scales.

91. **Solar coronal magnetic field** : \(\nabla\times\mathbf B=\mu_0\mathbf J,\quad\nabla\cdot\mathbf B=0\) : Elliptic/vector PDE system; magnetic-field geometry in magnetostatic approximation.

92. **Magnetic reconnection** : \(\mathbf B_t=\nabla\times(\mathbf u\times\mathbf B)+\eta\nabla^2\mathbf B\) : Nonlinear advection–diffusion PDE for magnetic fields; topology changes through resistive effects.

93. **Solar dynamo** : \(\mathbf B_t=\nabla\times(\mathbf u\times\mathbf B)+\eta\nabla^2\mathbf B\) with dynamo velocity field : Nonlinear/linear coupled PDE system; generation and evolution of large-scale stellar magnetic fields.

94. **Cosmic-ray transport** : \(f_t+\mathbf v_d\cdot\nabla f=\nabla\cdot(D\nabla f)-\nabla\cdot(\mathbf Vf)+Q\) : Advection–diffusion–reaction PDE; transport of energetic particles through astrophysical magnetic fields.

95. **Black-hole accretion radiation transport** : \(\frac1cI_t+\mathbf n\cdot\nabla I=\eta-\chi I\) coupled to GR fluid equations : Relativistic radiation-hydrodynamic PDE system; radiation and matter evolve together.

96. **Quantum field Klein–Gordon field** : \(\Box\phi-m^2\phi=0\) : Second-order linear hyperbolic PDE; relativistic scalar field propagation.

97. **Nonlinear Klein–Gordon field** : \(\Box\phi+m^2\phi+\lambda\phi^3=0\) : Second-order nonlinear hyperbolic PDE; self-interacting relativistic scalar field.

98. **Dirac field** : \((i\gamma^\mu\partial_\mu-m)\psi=0\) : First-order linear hyperbolic PDE system; relativistic spin-\(\frac12\) quantum field.

99. **Yang–Mills gauge field** : \(D_\mu F^{\mu\nu}=J^\nu\) : Nonlinear second-order PDE system; relativistic non-Abelian gauge fields.

100. **Einstein–Klein–Gordon system** : \(G_{\mu\nu}=8\pi GT_{\mu\nu}[\phi],\quad\Box_g\phi-V'(\phi)=0\) : Coupled nonlinear hyperbolic PDE system; scalar field and spacetime dynamically gravitate each other.

### Scale progression

$$
\boxed{\text{microscopic}\rightarrow\text{laboratory}\rightarrow\text{Earth}\rightarrow\text{planetary}\rightarrow\text{stellar}\rightarrow\text{galactic}\rightarrow\text{cosmological}}
$$

* **Microscopic:** Schrödinger, Gross–Pitaevskii, Dirac, reaction–diffusion.
* **Laboratory:** heat, diffusion, waves, Maxwell, elasticity, Navier–Stokes.
* **Earth:** groundwater, atmosphere, ocean, mantle, seismic waves.
* **Planetary:** shallow water, planetary atmosphere, ocean circulation, Rossby waves.
* **Stellar:** MHD, radiative transfer, stellar oscillations, relativistic hydrodynamics.
* **Galactic:** Poisson gravity, Vlasov–Poisson, galactic gas dynamics.
* **Cosmological:** Einstein equations, cosmological fluids, gravitational waves, relativistic perturbations.

Most important mathematical families represented here:

$$
\boxed{\text{elliptic}}
\quad
\boxed{\text{parabolic}}
\quad
\boxed{\text{hyperbolic}}
\quad
\boxed{\text{dispersive}}
\quad
\boxed{\text{transport}}
\quad
\boxed{\text{conservation laws}}
\quad
\boxed{\text{reaction--diffusion}}
\quad
\boxed{\text{kinetic}}
\quad
\boxed{\text{nonlinear coupled systems}}
$$

And one important hierarchy:

$$
\text{ODE}
\;\xleftarrow{\text{symmetry / modal reduction}}\;
\text{PDE}
$$

For example,

$$
\text{Einstein PDEs}
\rightarrow
\text{FLRW ODE},
$$

$$
\text{Einstein PDEs}
\rightarrow
\text{TOV ODE},
$$

$$
\text{wave PDE}
\rightarrow
\text{normal-mode ODE},
$$

$$
\text{Navier--Stokes PDE}
\rightarrow
\text{Poiseuille-flow ODE},
$$

$$
\text{Maxwell PDE}
\rightarrow
\text{RLC ODE}.
$$

This is why same ODE can describe systems separated by \(10^{30}\) in physical scale.
