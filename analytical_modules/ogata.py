# -*- coding: utf-8 -*-
"""
@author: Glenn Hammond, Sandia National Laboratories, gehammo@sandia.gov

Anaytical solution of solute transport with a fixed or constant input 
concentration and a first-type boundary condition.

Source: Ogata, A. and R.B. Banks (1961) A Solution of the Differential
        Equation of Longitudinal Dispersion in Porous Media, Fluid
        Movement in Earth Materials, Geological Survey Professional 
        Paper 411-A, US Dept. of Interior.
        
"""

import sys
import os
import math
import numpy as np
from scipy import special
import traceback

from qa_debug import *
from analytical_modules.xerf import exp_erf
from analytical_modules.analytical_transport import AnalyticalTransport1D
from analytical_modules.analytical import Analytical

class Ogata(AnalyticalTransport1D):
  
    def __init__(self):
        debug_push('Ogata init')
        super(AnalyticalTransport1D,self).__init__()
        self._name = 'Ogata'
        self._nx = 100
        self._Lx = 10.
        self._v = 1.         # pore water velocity [L/T]
        self._D = 1e-9       # effective dispersion coefficient [L^2/T]
        self._c0 = 1.        # boundary concentration
        debug_pop
   
    def get_solution(self,t): 
        debug_push('Ogata get_solution')

        dx = self._Lx/self._nx
        c = np.zeros(self._nx)
        x = self.get_rounded_even_spaced_numbers(dx,self._nx)

        # Equations following (12), but prior ot (13)
        for i in range(self._nx):
            xx = x[i]
            twosqrtDT = 2.*math.sqrt(self._D*t)
            c[i] = 0.5*(special.erfc((xx-self._v*t)/twosqrtDT) + \
                        exp_erf(self._v*xx/self._D, \
                                (xx+self._v*t)/twosqrtDT))
        c[:] *= self._c0
        debug_pop()
        return x, c
    
def main(options):

    root_dir = os.getcwd()
    ogata = Ogata()
    t = ogata.get_time_midpoint()
    x, c = ogata.get_solution(t)
    x, y, z = ogata.get_node_centered_coordinates()
    solution = PythonSolution('ogata.h5','s')
    solution.write_coordinates(x,y,z)
    solution.write_dataset(t,c,'A')
    solution.close()

if __name__ == "__main__":
  cmdl_options = ''
  try:
    suite_status = main(cmdl_options)
    print("success")
    sys.exit(suite_status)
  except Exception as error:
    print(str(error))
#    if cmdl_options.backtrace:
#      traceback.print_exc()
    traceback.print_exc()
    print("failure")
    sys.exit(1)
