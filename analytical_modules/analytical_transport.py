import sys

from qa_debug import *
from analytical_modules.analytical import Analytical

class AnalyticalTransport1D(Analytical):
  
    def __init__(self):
        debug_push('AnalyticalTransport1D init')
        super(Analytical,self).__init__()
        self._name = 'Analytical Transport 1D'
        self._nx = -999
        self._Lx = -999.
        self._v = -999.
        self._D = -999.
        self._c0 = -999.
        debug_pop()

    def set_velocity(self,v):
        self._v = v

    def set_diffusion(self,D):
        self._D = D

    def get_time_midpoint(self):
        debug_push('AnalyticalTransport1D get_time_midpoint')
        t = 0.5 * self._Lx / self._v
        debug_pop()
        return t

    def get_cell_centered_coordinates(self):
        debug_push('AnalyticalTransport1D get_cell_centered_coordinates')
        cell_centered = True
        x, y, z = self.get_coordinates(cell_centered)
        debug_pop()
        return x, y, z
        
    def get_node_centered_coordinates(self):
        debug_push('AnalyticalTransport1D get_node_centered_coordinates')
        cell_centered = False
        x, y, z = self.get_coordinates(cell_centered)
        debug_pop()
        return x, y, z
        
    def get_coordinates(self,cell_centered):
        debug_push('AnalyticalTransport1D get_coordinates')
        dx = self._Lx/self._nx
        x = self.get_rounded_even_spaced_numbers(dx,self._nx,cell_centered)
        y = [0., 1.]
        debug_pop()
        return x, y, y
