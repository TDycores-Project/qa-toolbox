Problem Description Setup
=========================

In order to properly document the problem set up create a text file using the following file format ``description_template.txt`` where template is defined in the configuration file. Type in what you wish to be displayed under problem description such as reference for test, grid spacing, initial conditions, material properties etc. Equations can be specified using sphinx math format.

An example problem description:

This problem is adapted from *Kolditz, et al. (2015), 
Thermo-Hydro-Mechanical-Chemical Processes in Fractured Porous Media: 
Modelling and Benchmarking, Closed Form Solutions, Springer International 
Publishing, Switzerland.* Section 2.2.9, pg.35, "A Transient 1D 
Pressure Distribution, Non-Zero Initial Pressure, Boundary Conditions of 
1st and 2nd Kind."

The domain is a 100x1x1 meter rectangular beam extending along the positive x-axis. Two different grid spacings were tested. The first is made up of 10x1x1 hexahedral grid cells with dimensions 10x1x1 meters. The second is made up of 50x1x1 hexahedral grid cells with dimensions 2x1x1 meters.

The domain is composed of a single material and is assigned the 
following properties: porosity :math:`\phi` = 0.20; permeability :math:`k` = 
1.0e-14 m^2; rock density :math:`\rho` = 2,000 kg/m^3; fluid compressibility
:math:`K` = 1.0e-9 1/Pa; fluid viscosity :math:`\mu` = 1.728e-3 Pa-sec.

The pressure is initially distributed according to p(x,t=0)=f(x), where
f(x) is defined (in units of MPa) as

.. math:: 
   f(x) = 0  \hspace{0.25in} 0 \leq x < {L \over 10}
   
   f(x) = {{10x} \over {3L}}-{1 \over 3}  \hspace{0.25in} {L \over 10} \leq x < {{4L} \over 10}
   
   f(x) = 1  \hspace{0.25in} {{4L} \over 10} \leq x < {{6L} \over 10}
   
   f(x) = 3-{{10x} \over {3L}}  \hspace{0.25in} {{6L} \over 10} \leq x < {{9L} \over 10}
   
   f(x) = 0  \hspace{0.25in} {{9L} \over 10} \leq x \leq L

At the two boundaries, a no fluid flux condition is applied,

.. math::
   q(0,t) = 0
   
   q(L,t) = 0

where L = 100 m. The transient pressure distribution is governed by,

.. math:: 
   {\phi K} {{\partial p} \over {\partial t}} = {k \over \mu} {{\partial^{2} p} \over {\partial x^{2}}}

With the initial pressure given, the solution is defined by,

.. math:: 
   p(x,t) = {1 \over 2} + \sum_{n=1}^{\infty} exp\left({-\chi n^2 \pi^2 {t \over L^2}}\right)\left({80 \over {3(n\pi)^2}}\right) cos{{n \pi y} \over L} cos{{n\pi} \over 2} sin{{n\pi} \over 4} sin{{3n\pi} \over 20} 
  
  \chi = {{k} \over {\phi \mu K}}
