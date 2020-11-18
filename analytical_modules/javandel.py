# -*- coding: utf-8 -*-
"""
Created on Tue May  7 15:03:30 2019

@author: Glenn Hammond, Sandia National Laboratories, gehammo@sandia.gov

Anaytical solution of solute transport with a fixed or constant input 
concentration.

Source: Javandel, I., C. Doughty and C.F. Tsang (1984) Groundwater Transport:
        Handbook of Mathematical Models, Water Resources Monograph Series 10,
        American Geophysical Union, Washington DC.
        
Note that the analytical solutions used by Javandel et al. (1984) originate
from:

  van Genuchten, M. T. and W.J. Alves, (1982) Analytical solutions of the 
  one-dimensional convective-dispersive solute transport equation, USDA 
  Tech. Bull. 1661.

@author: gehammo
"""

import sys
import os
import math
import numpy as np
from scipy import special
import traceback

from qa_debug import *
from analytical_modules.analytical_transport import AnalyticalTransport1D
from analytical_modules.xerf import exp_erf

class Javandel(AnalyticalTransport1D):
  
    def __init__(self):
        debug_push('Javandel init')
        super(AnalyticalTransport1D,self).__init__()
        self._name = 'javandel'
        self._nx = 100
        self._Lx = 10.
        self._v = 1.         # pore water velocity [L/T]
        self._D = 1e-9        # effective dispersion coefficient [L^2/T]
        self._c0 = 1.        # boundary concentration
        self._t0 = 1e20      # time when boundary concentration changes to zero.
        self._alpha = 0.     # source decay coefficient [1/T]
        self._lambda = 0.    # decay coefficient [1/T]
        self._R = 1.
        debug_pop

    def set_alpha(self,a):
        self._alpha = a
   
    def set_lambda(self,lambda_):
        self._lambda = lambda_
   
    def set_R(self,R):
        self._R = R
   
    def get_solution(self,t): 
        debug_push('Javandel get_solution')
    
        epsilon_value = 1.e-40
    
        dx = self._Lx/self._nx
        c = np.zeros(self._nx)
        x = self.get_rounded_even_spaced_numbers(dx,self._nx)
    
        if self._alpha < epsilon_value and self._lambda < epsilon_value and \
           abs(self._R-1.) < epsilon_value: 
            # use Equation (45) - first-type
            for i in range(self._nx):
                c[i] = self.A3(x[i],t)
                if t > self._t0:
                    c[i] -= self.A3(x[i],t-self._t0)
        elif self._alpha < epsilon_value and self._lambda < epsilon_value:
            # use Equation (44) - first-type
            for i in range(self._nx): 
                c[i] = self.A2(x[i],t)
                if t > self._t0:
                    c[i] -= self.A2(x[i],t-self._t0)
        elif self._alpha < epsilon_value and self._lambda > epsilon_value:
            # use Equation (40) - first-type
            for i in range(self._nx): 
                c[i] = self.A1_constant(x[i],t)
                if t > self._t0:
                    c[i] -= self.A1_constant(x[i],t-self._t0)
        elif self._alpha > epsilon_value and self._lambda > epsilon_value:
            # Equation (35)
            if abs(self._alpha-self._lambda) > epsilon_value:
                # use Equation (36a) - third-type
                for i in range(self._nx): 
                    c[i] = math.exp(-self._alpha*t)*self.A1(x[i],t)
                    if t > self._t0:
                        c[i] -=  self._c0*math.exp(-self._alpha*(t-self._t0))* \
                                 self.A1(x[i],t-self._t0)* \
                                 math.exp(-self._alpha*self._t0)
            else:
                # use Equation (36b) - first-type
                for i in range(self._nx): 
                    c[i] = math.exp(-self._alpha*t)*self.A2(x[i],t)
                    if t > self._t0:
                        c[i] -=  self._c0*math.exp(-self._alpha*(t-self._t0))* \
                                 self.A2(x[i],t-self._t0)* \
                                 math.exp(-self._alpha*self._t0)
        else:
            sys.exit('Unknown combination of alpha, lambda and R')
        c[:] *= self._c0     
        debug_pop()
        return x, c
    
    # TODO(geh): simplify the 2*sqrt(DRt) below
    def A1(self,x,t): # third-type
        # Equation (38)
        U = math.sqrt(self._v*self._v+4.*self._D*self._R* \
                      (self._lambda-self._alpha))    
        # Equation (37)
        A1_ = \
            self._v/(self._v+U)* \
            exp_erf(0.5*x*(self._v-U)/self._D,
                    0.5*(self._R*x-U*t)/math.sqrt(self._D*self._R*t))+ \
            self._v/(self._v-U)* \
            exp_erf(0.5*x*(self._v+U)/self._D,
                    0.5*(self._R*x+U*t)/math.sqrt(self._D*self._R*t))+ \
            0.5*self._v*self._v/(self._D*self._R*(self._lambda-self._alpha))* \
            exp_erf(self._v*x/self._D+(self._alpha-self._lambda)*t,
                    0.5*(self._R*x+self._v*t)/math.sqrt(self._D*self._R*t))
        return A1_            

    def A1_constant(self,x,t): # first-type
        # Equation (42)
        U = math.sqrt(self._v*self._v + 4.*self._D*self._R*self._lambda)
        # Equation (41)
        A1_constant_ = \
            self._v/(self._v+U)* \
            exp_erf(0.5*x*(self._v-U)/self._D,
                    0.5*(self._R*x-U*t)/math.sqrt(self._D*self._R*t))+ \
            self._v/(self._v-U)* \
            exp_erf(0.5*x*(self._v+U)/self._D,
                    0.5*(self._R*x+U*t)/math.sqrt(self._D*self._R*t))+ \
            0.5*self._v*self._v/(self._D*self._R*self._lambda)* \
            exp_erf(self._v*x/self._D-self._lambda*t,
                    0.5*(self._R*x+self._v*t)/math.sqrt(self._D*self._R*t))
        return A1_constant_

    def A2(self,x,t): # first-type
        # Equation (39)
        A2_ = \
            0.5*math.erfc(0.5*(self._R*x-self._v*t)/ \
                          math.sqrt(self._D*self._R*t))+ \
            math.sqrt(self._v*self._v*t/(math.pi*self._D*self._R))* \
            math.exp(-0.25*(self._R*x-self._v*t)*(self._R*x-self._v*t)/ \
                     (self._D*self._R*t))- \
            0.5*(1.+self._v*x/self._D+self._v*self._v*t/(self._D*self._R))* \
            exp_erf(self._v*x/self._D,
                    0.5*(self._R*x+self._v*t)/math.sqrt(self._D*self._R*t))
        return A2_            

    def A3(self,x,t): # first-type
        # Equation (46)
        A3_ = \
            0.5*math.erfc(0.5*(x-self._v*t)/math.sqrt(self._D*t))+ \
            math.sqrt(self._v*self._v*t/(math.pi*self._D))* \
            math.exp(-0.25*(x-self._v*t)*(x-self._v*t)/(self._D*t)) - \
            0.5*(1.+self._v*x/self._D+self._v*self._v*t/self._D)* \
            exp_erf(self._v*x/self._D,
                    0.5*(x+self._v*t)/math.sqrt(self._D*t))
        return A3_            
  
def main(options):

    root_dir = os.getcwd()
    javandel = Javandel()
    print(javandel.get_solution())


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
