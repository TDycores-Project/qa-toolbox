import sys
import os
import numpy as np
import math

from qa_debug import *
from qa_common import *

from simulator_modules.simulator import QASimulator
from simulator_modules.solution import SolutionWriter

class QASimulatorDatasetSin(QASimulator):

    def __init__(self,path):
        debug_push('QASimulatorDataset init')
#        super(QASimulatorTOUGH3,self).__init__(path)
        self._name='dataset_sin'
        self._suffix='.py'
        debug_pop()
        
    def run(self,filename,annotation):
#        command = []
#        command.append(self._get_full_executable_path())
#        command.append(filename)
#        status = self._submit_process(command,filename,annotation)
#        
#        solution_filename='sin_dataset.h5'
        
        x = np.arange(0,17*math.pi/8,math.pi/8)
        y = np.array([0.5])
        z = np.array([0.5])
    
        solution_sin = np.sin(x)
        solution_filename='sin_dataset.h5'
        
        convert_to_h5_file(solution_filename,x,y,z,solution_sin)

        return solution_filename
    
        


    
class QASimulatorDatasetCos(QASimulator):

    def __init__(self,path):
        debug_push('QASimulatorDataset init')
#        super(QASimulatorTOUGH3,self).__init__(path)
        self._name='dataset_cos'
        self._suffix='.py'
        debug_pop()
        
    def run(self,filename,annotation):
#        command = []
#        command.append(self._get_full_executable_path())
#        command.append(filename)
#        status = self._submit_process(command,filename,annotation)
#        
#        solution_filename='cos_dataset.h5'
        x = np.arange(0,17*math.pi/8,math.pi/8)
        y = np.array([0.5])
        z = np.array([0.5])
    
        solution_cos = np.cos(x)
        solution_filename='cos_dataset.h5'
        
        convert_to_h5_file(solution_filename,x,y,z,solution_cos)
        
        return solution_filename
        
def convert_to_h5_file(filename,x,y,z,values):
    
    solution = SolutionWriter(filename)
    solution.write_coordinates(x,y,z)
    
    solution.write_dataset(0.0,values,'Pressure','Time Slice')
            
    solution.write_time(x)
    solution.write_dataset((0.0,0.0,0.0),values,'Pressure','Observation')
            
    solution.destroy()