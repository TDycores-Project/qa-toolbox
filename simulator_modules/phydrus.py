import sys
import shutil
import os

import h5py
from qa_debug import *
from qa_common import *
import numpy as np

from simulator_modules.simulator import QASimulator

class QASimulatorPhydrus(QASimulator):
    
    def __init__(self,path):
        debug_push('QASimulatorPython init')
        super(QASimulatorPhydrus,self).__init__(path)
        self._name = 'phydrus'
        self._suffix = ''
        debug_pop()
        
    def output_file_patterns(self):
        patterns = ['BALANCE.OUT', 'I_CHECK.OUT', 'NOD_INF.OUT', 
                    'OBS_NODE.OUT', 'PROFILE.OUT', 'RUN_INF.OUT', 
                    'T_LEVEL.OUT']
        return patterns 
    
    def run(self,filename,annotation,np):
        debug_push('QASimulatorPhydrus _run')
        
        command = []
        command.append(self._get_full_executable_path())
        input_file_path = filename + '_folder'
        command.append(input_file_path)
        command.append('-1')
        
        debug_push('Running Phydrus')
        self._submit_process(command,input_file_path,annotation)
        debug_pop()
        
        solution_filename = self.convert_solution_to_common_h5(filename)
        debug_pop()
        return solution_filename
    
    def convert_solution_to_common_h5(self,input_file_path):
        debug_push('QASimulatorPHydrus convert_solution_to_common_h5')
        output_file = input_file_path + '/NOD_INF.OUT'
        
        #output_file = h5py.File(input_file_path+".hdf5", "w")
        
        #Output file which we are supposed to test against
        output_file = os.getcwd() + "/vsat_flow_th_pflotran_run1_pflotran.h5"
        
        debug_pop()
        return output_file
