import sys

import numpy as np

from qa_debug import *

class Analytical(object):
  
    def __init__(self):
        self._name = 'Analytical'
   
    def get_solution(self): 
        debug_push('Analytical get_solution')
        print('Analytical.get_solution must be extended')
        raise
        debug_pop()
        return ''

    def get_rounded_even_spaced_numbers(self,delta,n,cell_centered=True,
                                        precision=None):
        '''Floating  point numbers generated with float(i+0.5*delta) can
           have hanging digits (.e.g 1.50000000000001).  This routine
           prevents such'''
        debug_push('Analytical get_rounded_even_spaced_numbers')
        if precision:
            string = '%0.{}f'.format(precision)
        else:
            string = '%0.5f'
        nn = n
        shift = 0.5
        if not cell_centered:
            nn += 1
            shift = 0.
        array = np.zeros(nn)
        for i in range(nn):
            array[i] = float(string%(float(i+shift)*delta))
        debug_pop()
        return array
        

    def get_time_midpoint(self):
        debug_push('Analytical get_time_midpoint')
        print('Analytical.get_time_midpoint must be extended')
        raise
        debug_pop()
        return ''

