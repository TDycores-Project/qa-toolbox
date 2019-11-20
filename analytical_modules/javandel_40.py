# -*- coding: utf-8 -*-
"""
Created on Tue May  7 14:10:24 2019

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
import traceback

class Analytical(object):
  
  def __init__(self):
    self._name = 'javandel 40'
    self._nx = 100
    self._Lx = 10.
    self._v = 1.
    self._D = 1.
    self.c0 = 1.
    self._t0 = 0.
    self._R = 1.
    self._lambda = 0.
      
  def get_solution(self):
    
    epsilon_value = 1.e-30
    
    dx = self._Lx/self._nx
    t = 0.5*self._Lx / self._v

    c = np.zeros(self._nx)
    x = -0.5*dx
    for i in range(self._nx):
      x += dx
      print(t,x)
      c[i] = self.c_over_c0(x,t)

    return c
    
  def c_over_c0(self,x,t):
    
    U = math.sqrt(self._v*self._v + 4.*self._D*self._R*self._lambda)
    
    print(self._v)    
    print(self._D)    
    print(self._R)    
    print(self._lambda)    
    
    c_over_c0_ = \
      self._v/(self._v+U)* \
      math.exp(0.5*x*(self._v-U)/self._D)* \
      math.erfc(0.5*(self._R*x-U*t)/math.sqrt(self._D*self._R*t))+ \
      self._v/(self._v-U)* \
      math.exp(0.5*x*(self._v+U)/self._D)* \
      math.erfc(0.5*(self._R*x+U*t)/math.sqrt(self._D*self._R*t))+ \
      0.5*self._v*self._v/(self._D*self_R*self._lambda)* \
      math.exp(self._v*x/self._D-self._lambda*t)* \
      math.erfc(0.5*(self._R*x+self._v*t)/math.sqrt(self._D*self._R*t))

    return c_over_c0_            
              
  
def main(options):

  root_dir = os.getcwd()

  analytical = Analytical()
  print(analytical.get_solution())


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