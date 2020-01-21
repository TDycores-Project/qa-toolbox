import sys
import os
import numpy as np
import math
import re

from qa_debug import *
from qa_solution import QASolutionWriter

from simulator_modules.simulator import QASimulator

obs_mapping = {}
time_mapping = {}

class QASimulatorTDycore(QASimulator):

    def __init__(self,path):
        debug_push('QASimulatorTDycore init')
        super(QASimulatorTDycore,self).__init__(path)
        self._name = 'tdycore'
        self._suffix = '.in'
        debug_pop()

    def run(self,filename,annotation):
        debug_push('QASimulatorTDycore _run')
        command = []
        command.append(self._get_full_executable_path())
        command.append('-input')
        command.append(filename)
        command.append('-pc_type lu -ksp_type preonly')
        debug_push('Running TDycore')
        self._submit_process(command,filename,annotation)
        debug_pop()
        
        solution_filename=self.convert_solution_to_common_h5(filename)
        debug_pop()
        return solution_filename        


    def convert_solution_to_common_h5(self,filename):
        root = filename.rsplit('.',1)[0]
        solution_filename = '{}_tdycore.h5'.format(root)
        solution = QASolutionWriter(solution_filename)

#--------------------------------------------------
        # Assumptions:
        #   The results are on a 2D unit square. Calculate the descretization
        #   accordingly.
#        fin = open('{}.sol'.format(root), 'r')
        fin = open('{}.vtk'.format(root), 'r')
        all_values = []
        found = False
        for line in fin:
            if (found):
                try:
                    f = float(line)
                    all_values.append(f)
                except ValueError:
                    break
            if line.startswith("LOOKUP_TABLE"):
                found = True
        n = int(math.sqrt(len(all_values)))
        all_values = np.asarray(all_values,dtype=np.float64)
        all_values = np.reshape(all_values,(n,n))

        x = np.linspace(0.5/n,1.-0.5/n,n,dtype=np.float64)
        z = np.zeros(1)
        z[0] = 0.5
        solution.write_coordinates(x,x,z)
        time = 0.
#        time = 1.e6
        solution.set_time_unit('y')
        solution.write_dataset(time,all_values,'Liquid Pressure','Time Slice')
        fin.close()
        solution.destroy()
        return solution_filename

