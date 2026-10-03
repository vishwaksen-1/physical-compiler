1. **Keplerian two-body orbit** : \(\ddot{\mathbf r}=-\frac{\mu}{r^3}\mathbf r\) : Second-order nonlinear autonomous ODE; inverse-square gravitational attraction. Already appeared in Newtonian orbital motion, but this is canonical celestial-mechanics form.

2. **Kepler orbit in polar coordinates** : \(\ddot r-r\dot\theta^2=-\frac{\mu}{r^2},\quad r\ddot\theta+2\dot r\dot\theta=0\) : Coupled second-order nonlinear ODEs in radial/angular coordinates; conservation of angular momentum produces \(r^2\dot\theta=\text{const}\).

3. **Restricted three-body problem** : \(\ddot{\mathbf r}=-GM_1\frac{\mathbf r-\mathbf r_1}{|\mathbf r-\mathbf r_1|^3}-GM_2\frac{\mathbf r-\mathbf r_2}{|\mathbf r-\mathbf r_2|^3}\) : Second-order nonlinear nonautonomous ODE; test body moves in gravitational field of two massive bodies. ([Wikipedia][1])

4. **Circular restricted three-body problem** : \(\ddot x-2n\dot y=\Omega_x,\quad\ddot y+2n\dot x=\Omega_y\) : Coupled second-order nonlinear ODEs in rotating frame; Coriolis and centrifugal terms plus two-body gravity.

5. **Lagrange-point dynamics** : \(\delta\ddot{\mathbf r}=A\,\delta\mathbf r+B\,\delta\dot{\mathbf r}\) : Linearized coupled second-order ODE around equilibrium \(L_1,\ldots,L_5\); determines local stability and libration.

6. **Planetary \(N\)-body system** : \(m_i\ddot{\mathbf r}_i=-G\sum_{j\neq i}m_im_j\frac{\mathbf r_i-\mathbf r_j}{|\mathbf r_i-\mathbf r_j|^3}\) : Coupled nonlinear second-order ODE system; each body's acceleration depends on every other body's position. ([Wikipedia][1])

7. **Solar-System post-Newtonian dynamics** : \(\ddot{\mathbf r}_i=\mathbf a_{N,i}+\frac{1}{c^2}\mathbf a_{1PN,i}+\frac{1}{c^4}\mathbf a_{2PN,i}+\cdots\) : Perturbative nonlinear second-order ODE system; Newtonian gravity plus relativistic corrections. Post-Newtonian celestial mechanics is used for high-precision Solar-System dynamics. ([APS Journals][2])

8. **Einstein–Infeld–Hoffmann \(N\)-body system** : \(\ddot{\mathbf r}_i=\mathbf a_{N,i}+c^{-2}\mathbf a_{1PN,i}\) : First post-Newtonian coupled second-order nonlinear ODE system; weak-field, slow-motion approximation to GR.

9. **Mercury perihelion precession** : \(\frac{d^2u}{d\phi^2}+u=\frac{GM}{h^2}+\frac{3GM}{c^2}u^2\) : Second-order nonlinear ODE in orbital angle; GR correction \(3GMu^2/c^2\) produces relativistic perihelion precession.

10. **Schwarzschild geodesic** : \(\frac{d^2x^\mu}{d\tau^2}+\Gamma^\mu_{\alpha\beta}\frac{dx^\alpha}{d\tau}\frac{dx^\beta}{d\tau}=0\) : Four coupled second-order nonlinear ODEs; timelike/free-fall trajectories in curved spacetime.

11. **Photon orbit near Schwarzschild black hole** : \(\frac{d^2u}{d\phi^2}+u=3Mu^2\) : Second-order nonlinear ODE for null geodesics; describes gravitational light bending and photon trajectories.

12. **Gravitational lensing** : \(\beta=\theta-\frac{D_{LS}}{D_S}\alpha(\theta)\) : Nonlinear/algebraic lens equation; maps source position to observed image positions through gravitational deflection.

13. **Black-hole radial free fall** : \(\left(\frac{dr}{d\tau}\right)^2=E^2-\left(1-\frac{2GM}{rc^2}\right)\left(c^2+\frac{L^2}{r^2}\right)\) : First-order nonlinear ODE after exploiting conserved energy and angular momentum.

14. **Relativistic two-body binary** : \(\ddot{\mathbf r}=\mathbf a_N+\frac{1}{c^2}\mathbf a_{1PN}+\frac{1}{c^3}\mathbf a_{2.5PN}+\cdots\) : Second-order nonlinear ODE with conservative and dissipative relativistic corrections; \(2.5PN\) term represents gravitational-radiation reaction.

15. **Inspiralling compact binary** : \(\dot a=f(a,e),\quad\dot e=g(a,e)\) : Coupled first-order nonlinear secular ODEs; orbital radius and eccentricity evolve due to gravitational-wave energy/angular-momentum loss.

16. **Quasi-circular gravitational-wave inspiral** : \(\dot\Omega\propto\Omega^{11/3}\) : First-order nonlinear ODE for orbital frequency; chirp frequency accelerates as binary loses orbital energy.

17. **Binary pulsar orbital decay** : \(\dot P_b=f(m_1,m_2,e,P_b)\) : First-order secular ODE for orbital period; gravitational radiation causes \(P_b\) to decrease.

18. **Gravitational-wave propagation** : \(\Box h_{\mu\nu}=0\) : Second-order linear hyperbolic PDE for weak spacetime perturbations in vacuum.

19. **Gravitational waves on expanding universe** : \(h''+2\frac{a'}a h'+(k^2+2K)h=0\) : Second-order linear ODE with time-dependent coefficients; tensor perturbation evolves on FLRW background. ([OUP Academic][3])

20. **FLRW cosmic expansion** : \(\left(\frac{\dot a}{a}\right)^2=\frac{8\pi G}{3}\rho+\frac{\Lambda}{3}-\frac{Kc^2}{a^2}\) : First-order nonlinear ODE for cosmic scale factor \(a(t)\). ([Springer][4])

21. **FLRW cosmic acceleration** : \(\frac{\ddot a}{a}=-\frac{4\pi G}{3}\left(\rho+\frac{3p}{c^2}\right)+\frac{\Lambda}{3}\) : Second-order nonlinear ODE for cosmic expansion. ([Springer][4])

22. **Matter-dominated universe** : \(\dot a^2\propto a^{-1}\) : First-order nonlinear autonomous ODE; gives \(a(t)\propto t^{2/3}\).

23. **Radiation-dominated universe** : \(\dot a^2\propto a^{-2}\) : First-order nonlinear autonomous ODE; gives \(a(t)\propto t^{1/2}\).

24. **Dark-energy-dominated universe** : \(\dot a=Ha\) : First-order linear ODE with constant coefficient when \(\Lambda\) dominates; \(a(t)\propto e^{Ht}\).

25. **Cosmological density evolution** : \(\dot\rho+3H\left(\rho+\frac{p}{c^2}\right)=0\) : First-order nonlinear ODE coupled to equation of state \(p(\rho)\). ([Springer][4])

26. **Cosmological perturbation growth** : \(\ddot\delta+2H\dot\delta-4\pi G\rho\,\delta=0\) : Second-order linear ODE with time-dependent coefficients; evolution of small matter-density perturbations.

27. **Jeans gravitational instability** : \(\ddot\delta+2H\dot\delta+\left(\frac{c_s^2k^2}{a^2}-4\pi G\rho\right)\delta=0\) : Second-order linear variable-coefficient ODE; pressure competes with self-gravity.

28. **Tolman–Oppenheimer–Volkoff neutron star** : \(\frac{dp}{dr}=-\frac{G(\rho+p/c^2)(m+4\pi r^3p/c^2)}{r^2(1-2Gm/rc^2)},\quad\frac{dm}{dr}=4\pi r^2\rho\) : Coupled first-order nonlinear ODEs for relativistic stellar structure.

29. **Newtonian stellar structure** : \(\frac{dm}{dr}=4\pi r^2\rho,\quad\frac{dp}{dr}=-\frac{Gm\rho}{r^2}\) : Coupled first-order nonlinear ODEs; hydrostatic equilibrium of stars.

30. **Lane–Emden star model** : \(\frac1{\xi^2}\frac{d}{d\xi}\left(\xi^2\frac{d\theta}{d\xi}\right)=-\theta^n\) : Second-order nonlinear ODE; self-gravitating polytropic fluid.

31. **Chandrasekhar white-dwarf structure** : \(\frac1{\xi^2}\frac{d}{d\xi}\left(\xi^2\frac{d\theta}{d\xi}\right)=-\left(\theta^2+\cdots\right)^{3/2}\) : Second-order nonlinear ODE from hydrostatic equilibrium plus relativistic electron degeneracy.

32. **Relativistic stellar oscillations** : \(\ddot q_n+\omega_n^2q_n=0\) : Second-order homogeneous ODE for each normal mode; relativistic star supports discrete oscillation modes.

33. **Tidal deformation of planet/star** : \(\ddot Q+\gamma\dot Q+\omega_f^2Q=F_{\rm tidal}(t)\) : Second-order driven damped ODE for quadrupolar deformation.

34. **Tidal orbital evolution** : \(\dot a=f(a,e,\Omega_{\rm spin}),\quad\dot e=g(a,e,\Omega_{\rm spin})\) : Coupled first-order nonlinear secular ODEs; tides exchange angular momentum and energy between orbit and spin.

35. **Spin–orbit coupling** : \(\dot{\mathbf S}=\boldsymbol\tau,\quad\dot{\mathbf L}=-\boldsymbol\tau\) : Coupled first-order vector ODEs enforcing angular-momentum exchange.

36. **Lense–Thirring orbital precession** : \(\dot{\mathbf L}=\boldsymbol\Omega_{\rm LT}\times\mathbf L\) : First-order linear vector ODE; orbital plane precesses due to rotating central mass.

37. **Gyroscopic relativistic frame dragging** : \(\dot{\mathbf S}=\boldsymbol\Omega_{\rm LT}\times\mathbf S\) : First-order linear vector ODE; spin/vector orientation undergoes relativistic precession.

38. **Relativistic binary spin precession** : \(\dot{\mathbf S}_1=\boldsymbol\Omega_1(\mathbf r,\mathbf v,\mathbf S_2)\times\mathbf S_1\) : First-order nonlinear vector ODE with state-dependent precession frequency.

39. **Kerr black-hole geodesic** : \(\frac{d^2x^\mu}{d\tau^2}+\Gamma^\mu_{\alpha\beta}(x)\frac{dx^\alpha}{d\tau}\frac{dx^\beta}{d\tau}=0\) : Coupled second-order nonlinear ODEs in rotating curved spacetime.

40. **Kerr black-hole photon orbit** : \(\dot r^2=R(r),\quad\dot\theta^2=\Theta(\theta)\) : Coupled first-order nonlinear ODEs after separation of geodesic equations.

41. **Accretion disk radial dynamics** : \(\dot r=f(r,\rho,P,\nu)\) : Nonlinear first-order ODE after reduction of mass, angular-momentum and energy conservation.

42. **Galactic rotation curve** : \(v_c^2(r)=r\,d\Phi/dr\) : First-order spatial differential relation between gravitational potential and circular velocity.

43. **Galactic gravitational potential** : \(\nabla^2\Phi=4\pi G\rho\) : Second-order linear elliptic PDE; Newtonian gravitational field generated by mass density.

44. **Self-gravitating collisionless matter** : \(\nabla^2\Phi=4\pi G\rho,\quad f_t+\mathbf v\cdot\nabla_xf-\nabla\Phi\cdot\nabla_vf=0\) : Coupled elliptic–hyperbolic PDE system; Vlasov–Poisson description of stellar systems/dark matter.

45. **Cosmological large-scale structure** : \(\ddot{\delta}+2H\dot{\delta}=4\pi G\rho\delta\) : Second-order linear variable-coefficient ODE in linear perturbation theory.

46. **Gravitational collapse of a dust sphere** : \(\ddot R=-GM/R^2\) : Second-order nonlinear ODE for collapsing/expanding spherical shells.

47. **Relativistic gravitational collapse** : \(G_{\mu\nu}=\frac{8\pi G}{c^4}T_{\mu\nu}\) : Coupled nonlinear second-order PDEs for spacetime metric; full Einstein field equations.

48. **Einstein field equations** : \(R_{\mu\nu}-\frac12Rg_{\mu\nu}+\Lambda g_{\mu\nu}=\frac{8\pi G}{c^4}T_{\mu\nu}\) : Nonlinear second-order tensor PDE system governing spacetime geometry and matter.

49. **Static spherical Einstein equations** : \(\frac{dm}{dr}=4\pi r^2\rho,\quad\frac{d\Phi}{dr}=f(m,p,r)\) : Coupled first-order nonlinear ODE reduction of Einstein equations under spherical symmetry.

50. **Null geodesic / light propagation in curved spacetime** : \(\frac{d^2x^\mu}{d\lambda^2}+\Gamma^\mu_{\alpha\beta}\frac{dx^\alpha}{d\lambda}\frac{dx^\beta}{d\lambda}=0\) : Second-order nonlinear ODE; light follows spacetime geodesics.

51. **Shapiro time delay** : \(\frac{dt}{dr}=f(r,M)\) : First-order nonlinear ODE for coordinate-time propagation of light through gravitational potential.

52. **Gravitational redshift along radial trajectory** : \(\frac{d\ln\nu}{dr}=f(r,M)\) : First-order spatial ODE describing frequency evolution along curved spacetime trajectory.

53. **Solar-system light propagation in post-Newtonian gravity** : \(\frac{d^2x^i}{dt^2}=F^i(\mathbf x,\dot{\mathbf x},M,c^{-2},\ldots)\) : Coupled second-order nonlinear ODE with relativistic corrections; used in precision ranging and navigation. ([APS Journals][5])

54. **Cosmic photon propagation** : \(\frac{d}{dt}(aE)=0\) : First-order linear ODE; photon energy redshifts as \(E\propto a^{-1}\).

55. **Comoving-distance light propagation** : \(\dot\chi=c/a(t)\) : First-order nonhomogeneous ODE whose coefficient is determined by cosmic expansion.

56. **Hubble-flow separation** : \(\dot r=H(t)r\) : First-order linear ODE with time-dependent coefficient.

57. **Relativistic cosmological perturbation modes** : \(h_k''+2\mathcal Hh_k'+(k^2+a^2m^2)h_k=0\) : Second-order linear variable-coefficient ODE; mode evolution in expanding spacetime.

58. **Primordial scalar-field cosmology** : \(\ddot\phi+3H\dot\phi+V'(\phi)=0\) : Second-order nonlinear ODE; homogeneous scalar field evolves with Hubble damping.

59. **Inflationary scale factor + scalar field** : \(\dot H=-4\pi G\dot\phi^2,\quad\ddot\phi+3H\dot\phi+V'(\phi)=0\) : Coupled nonlinear ODE system for cosmic expansion and inflaton dynamics.

60. **Black-hole ringdown** : \(\ddot h+2\gamma\dot h+\omega_R^2h=0\) : Second-order damped linear ODE for each quasinormal mode; exponentially decaying oscillation.

61. **Gravitational-wave detector response** : \(\ddot x+2\gamma\dot x+\omega_0^2x=F_{\rm GW}(t)/m\) : Second-order driven damped ODE; GW strain acts as external tidal forcing.

62. **Binary black-hole waveform phase** : \(\dot\phi=\Omega,\quad\dot\Omega=F(\Omega)\) : Coupled first-order nonlinear ODEs; orbital phase and frequency evolve through inspiral.

63. **Post-Newtonian orbital elements** : \(\dot a=f(a,e),\quad\dot e=g(a,e),\quad\dot\omega=h(a,e)\) : Coupled first-order secular ODEs; useful for long-timescale evolution of relativistic binaries. ([ResearchGate][6])

64. **Solar-system ephemeris dynamics** : \(\ddot{\mathbf r}_i=\mathbf a_{\rm Newtonian}+\mathbf a_{\rm PN}+\mathbf a_{\rm tides}+\mathbf a_{\rm oblateness}+\cdots\) : Large coupled nonlinear second-order ODE system; practical high-precision celestial mechanics. ([APS Journals][5])

65. **Expanding-universe \(N\)-body dynamics** : \(\ddot{\mathbf x}+2H\dot{\mathbf x}=-\frac{1}{a^2}\nabla\Phi,\quad\nabla^2\Phi=4\pi Ga^2\bar\rho\,\delta\) : Coupled nonlinear ODE–PDE system; gravitationally interacting matter evolving while universe expands.

66. **Newtonian cosmological fluid** : \(\dot\rho+3H\rho+\frac1a\nabla\cdot(\rho\mathbf v)=0\) : First-order nonlinear conservation PDE for cosmic matter.

67. **Cosmic Euler equation** : \(\dot{\mathbf v}+H\mathbf v+\frac1a(\mathbf v\cdot\nabla)\mathbf v=-\frac1a\nabla\Phi\) : First-order nonlinear vector PDE for large-scale cosmic matter flow.

68. **Cosmic Vlasov–Poisson system** : \(f_t+\mathbf v\cdot\nabla_xf-\nabla\Phi\cdot\nabla_vf=0,\quad\nabla^2\Phi=4\pi G\int f\,d^3v\) : Coupled nonlinear kinetic PDE + elliptic gravitational field equation.

69. **Primordial gravitational-wave mode** : \(h_k''+2\frac{a'}a h_k'+k^2h_k=0\) : Second-order linear ODE with time-dependent damping; each Fourier mode behaves like a time-dependent oscillator. ([OUP Academic][3])

70. **Universe as dynamical system** : \(\dot a=aH,\quad\dot H=-4\pi G(\rho+p/c^2)+Kc^2/a^2\) : Coupled first-order nonlinear ODE system; converts cosmological evolution into phase-space dynamics. ([Springer][4])

<!-- 

This is where differential-equation physics becomes especially rich: **same mathematical form can recur across radically different scales**, while symmetry reduction can turn Einstein's PDEs into ODEs, just as spherical symmetry turns stellar structure into TOV ODEs and two-body symmetry reduces orbital dynamics to a small nonlinear ODE system. ([APS Journals][2])

[1]: https://en.wikipedia.org/wiki/Three-body_problem?utm_source=chatgpt.com "Three-body problem"
[2]: https://journals.aps.org/prd/abstract/10.1103/PhysRevD.43.3273?utm_source=chatgpt.com "General-relativistic celestial mechanics. I. Method and definition of reference systems | Phys. Rev. D"
[3]: https://academic.oup.com/ptep/article/2018/11/113E03/5206050?utm_source=chatgpt.com "Exact solutions of primordial gravitational waves | Progress of Theoretical and Experimental Physics | Oxford Academic"
[4]: https://link.springer.com/article/10.1140/epjc/s10052-020-08482-x?utm_source=chatgpt.com "Gravitational theory of cosmology, galaxies and galaxy clusters | The European Physical Journal C | Springer Nature Link"
[5]: https://journals.aps.org/prd/abstract/10.1103/PhysRevD.86.064004?utm_source=chatgpt.com "Celestial ephemerides in an expanding universe | Phys. Rev. D"
[6]: https://www.researchgate.net/publication/318460819_On_the_foundations_of_general_relativistic_celestial_mechanics?utm_source=chatgpt.com "(PDF) On the foundations of general relativistic celestial mechanics"

-->
