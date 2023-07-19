from qa_debug import *
from qa_common import *
from qa_solution import QASolutionWriter
import numpy as np

from simulator_modules.simulator import QASimulator

"""

Calvin Madsen: 
"""
class QASimulatorPHREEQC(QASimulator):
    
    def __init__(self,path):
        debug_push('QASimulatorPHREEQC init')
        super(QASimulatorPHREEQC,self).__init__(path)
        self._name = 'phreeqc'
        self._suffix = '.in'
        debug_pop()
        
    def run(self,filename,annotation,np):
        debug_push('QASimulatorPHREEQC _run')
        
        # Create the command to run phreeqc
        command = []
        command.append(self._get_full_executable_path())
        
        root = filename.split('.')[0]
        output_filename = root + '.out'
        
        command.append(filename)
        command.append(output_filename)
        
        debug_push('Running PHREEQC')
        self._submit_process(command,filename,annotation)
        debug_pop()
        
        # convert the output file to the common h5 version
        solution_filename = self.convert_solution_to_common_h5(filename)
        debug_pop()
        
        return solution_filename
    
    def convert_solution_to_common_h5(self,input_filename):
        debug_push('QASimulatorPHREEQC convert_solution_to_common_h5')
        solution_filename = get_h5_output_filename(input_filename, self._name)
        selected_output = input_filename.split(self._name)[0].rstrip('_') + '.sel'

        solution = QASolutionWriter(solution_filename)
        # Ca+2 HCO3- H+
        # ['Calcite_Rate [mol_m^3_sec]', 'Calcite_VF [m^3 mnrl_m^3 bulk]', 'Free_Ca++ [M]', 'Free_H+ [M]', 'Free_HCO3- [M]', 'Material_ID', 'pH']
        # 1DCalcite-x&t.sel
        measurement_labels = []
        measurement_units = []
        data_dict = {}
        h5_dataset_name_mapping = {'m_Ca+2': 'Free_Ca++ [m]',
                                   'm_H+': 'Free_H+ [m]',
                                   'm_HCO3-' : 'Free_HCO3- [m]',
                                   'Ca+2' : 'Total_Ca++ [m]'}
        group_name = 'Time Slice'  
        units_first = 1
        labels_first = 1
        coords_first = 1

        time = 0
        time_index = 0
        dist_x_index = 0
        
        try:
            with open(selected_output, 'r') as f:
                
                for line in f:
                    # Split each line into a list separated by whitespace
                    line = line.strip().split()
                    
                    # Find measurement labels and time index (always on first line)
                    if labels_first:
                        for i, label in enumerate(line):
                            measurement_labels.append(label)
                            if label == 'step':
                                time_index = i
                            if label == 'dist_x':
                                dist_x_index = i
                        
                        labels_first = 0
                        continue
                    
                    # Set time units
                    solution.set_time_unit('y')
                        
                    # Find current time (step)
                    time = float(line[time_index])
                            
                    # Get list of measurement units
                    #elif labels_first and len(line) == 10:
                    #    for label in line:
                    #        measurement_units.append(label)
                    #    labels_first = 0
                        
                    # Append data points to corresponding measurement key
                    for i, value in enumerate(line):
                        value = float(value)
                        if measurement_labels[i] not in data_dict:
                            data_dict[measurement_labels[i]] = [value]
                        else:
                            data_dict[measurement_labels[i]].append(value)
                    
                    # Write each dataset to solution for corresponding measurement
                    if line[dist_x_index] == '100':
                        for key, values in data_dict.items():
                            if key in h5_dataset_name_mapping:
                                dataset_name = h5_dataset_name_mapping[key]
                            else:
                                dataset_name = key
                                
                            data_dict[key] = np.array([[values]])
                            data_dict[key] = np.reshape(data_dict[key], (102, 1, 1))
                            
                            solution.write_dataset(time, data_dict[key], dataset_name, group_name)
                            
                            # Write the coords
                            if coords_first:
                                coords_first = 0
                                # for 1D tests
                                x = np.reshape(data_dict['dist_x'], -1)
                                y = 0.05 * (np.arange(1) + 1)
                                z = 0.05 * (np.arange(1) + 1)
                                solution.write_coordinates(x, y, z)
                            
                        data_dict = {}  # reset the dict for next time value
                    
        except FileNotFoundError:
            print(f'selected output file {selected_output} not found')
                
        debug_pop()
        return solution_filename
