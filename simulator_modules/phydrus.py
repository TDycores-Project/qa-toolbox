import sys
import shutil
import os

import h5py
from qa_debug import *
from qa_common import *
from qa_solution import QASolutionWriter
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
        
        solution_filename = self.convert_solution_to_common_h5(input_file_path)
        debug_pop()
        return solution_filename
    
    def convert_solution_to_common_h5(self,input_file_path):
        debug_push('QASimulatorPHydrus convert_solution_to_common_h5')
        solution_raw_data = input_file_path + '/NOD_INF.OUT'
        input_file = input_file_path.split('_folder')[0]
        solution_filename = get_h5_output_filename(input_file, self._name)
        solution = QASolutionWriter(solution_filename)
        
        group_name = 'Time Slice'
                
        times = []
        measurements = []
        measurement_units = []
        data_dict = {}
        h5_dataset_name_mapping = {'Temp': 'Temperature [C]', 
                                   'Depth': 'Depth [m]',
                                   'Head': 'Head [m]'}
        
        i = 0
        skip = 0
        first = 1
        time = 0
        
    
        try:
            with open(solution_raw_data, 'r') as f:
                # TODO:figure out where phydrus lists coords / where pflotran gets this from
                x = 0.5 * (np.arange(1) + 1)
                y = 0.5 * (np.arange(1) + 1)
                z = np.linspace(-0.9995, -0.0005, num = 101)

                solution.write_coordinates(x, y, z)
                
                for line in f:
                    line = line.strip().split()
                    if not skip and 'Units:' in line:
                        if 'seconds' in line:
                            solution.set_time_unit('s')
                        elif 'days' in line:
                            print('days')
                            solution.set_time_unit('d')
                        elif 'months' in line:
                            solution.set_time_unit('m')
                        elif 'years' in line:
                            solution.set_time_unit('y')
                        skip = 1
                    
                    elif len(line) == 2 and 'Time:' == line[0]:
                        time = float(line[1])
                        np.append(times, time)
                        print(time)
                    
                    else:
                        # Get list of measurements
                        if first and len(line) > 1 and line[0] == 'Node':
                            for i, label in enumerate(line):
                                measurements.append(label)
                        # Get list of measurement units
                        elif first and len(line) == 10:
                            for i, label in enumerate(line):
                                measurement_units.append(label)
                            first = 0
                        # Append data points to corresponding measurement key
                        elif len(line) == 11 and line[0] != 'Node':
                            for i, value in enumerate(line):
                                if i == 0:
                                    continue
                                value = float(value)
                                
                                # convert from cm to m
                                if measurement_units[i-1] in ['[L]','[L/T]']: #cm
                                    value *= 0.01
                                elif measurement_units[i-1] == '[1/L]':
                                    value *= 100.
                                        
                                if measurements[i] not in data_dict.keys():
                                    data_dict[measurements[i]] = [value]
                                else:
                                    data_dict[measurements[i]].append(value)
                        
                        # Write each dataset to solution for corresponding measurement
                        elif 'end' in line:
                            for key, value in data_dict.items():
                                if key in h5_dataset_name_mapping.keys():
                                    dataset_name = h5_dataset_name_mapping[key]
                                else:
                                    dataset_name = key
                                if key == 'Temp':
                                    data_dict[key].reverse()
                                    
                                data_dict[key] = np.array([[value]])
                                solution.write_dataset(time, data_dict[key], dataset_name, 'Time Slice')
                            data_dict = {}   
                            
        except FileNotFoundError:
            print('NOD_INF.OUT file found')
                
        #output_file = h5py.File(input_file_path+".hdf5", "w")
        
        #Output file which we are supposed to test against
        output_file = os.getcwd() + "/vsat_flow_th_pflotran_run1_pflotran.h5"
        
        debug_pop()
        return solution_filename
