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
        self._suffix = '.pqi'
        debug_pop()
        
    def run(self,filename,annotation,np):
        debug_push('QASimulatorPHREEQC _run')
        
        # Create the command to run phreeqc
        command = []
        command.append(self._get_full_executable_path())
        
        output_filename = filename.split('.')[0] + '.pqo'
        
        command.append(filename)
        command.append(output_filename)
        
        debug_push('Running PHREEQC')
        self._submit_process(command,filename,annotation)
        debug_pop()
        
        # convert the output file to the common h5 version
        solution_filename = self.convert_solution_to_common_h5(filename, output_filename)
        debug_pop()
        
        return solution_filename
    
    def convert_solution_to_common_h5(self,input_file_name, output_filename):
        debug_push('QASimulatorPHREEQC convert_solution_to_common_h5')
        solution_filename = get_h5_output_filename(input_file_name, self._name)
        solution = QASolutionWriter(solution_filename)
        """
        measurements = []
        measurement_units = []
        data_dict = {}
        h5_dataset_name_mapping = {'Temp': 'Temperature [C]', 
                                   'Depth': 'Depth [m]',
                                   'Head': 'Liquid Pressure',
                                   'Moisture' : 'Liquid Saturation'}
        group_name = 'Time Slice'  
        units_first = 1
        labels_first = 1
        coords_first = 1
        moisture_first = 1
        
        liquid_sat_denom = 1
        time = 0
        """
        try:
            with open(output_filename, 'r') as f:
                print("FOUND")
                """
                for line in f:
                    # Split each line into a list separated by whitespace
                    line = line.strip().split()
                    
                    # Find time units
                    if units_first and 'Units:' in line:
                        if 'seconds' in line:
                            solution.set_time_unit('s')
                        elif 'days' in line:
                            solution.set_time_unit('d')
                        elif 'months' in line:
                            solution.set_time_unit('m')
                        elif 'years' in line:
                            solution.set_time_unit('y')
                        units_first = 0
                        
                    # Find time
                    elif len(line) == 2 and 'Time:' == line[0]:
                        time = float(line[1])
                    
                    # Get list of measurements
                    elif labels_first and len(line) > 1 and line[0] == 'Node':
                        for label in line:
                            measurements.append(label)
                            
                    # Get list of measurement units
                    elif labels_first and len(line) == 10:
                        for label in line:
                            measurement_units.append(label)
                        labels_first = 0
                        
                    # Append data points to corresponding measurement key
                    elif len(line) == 11 and line[0] != 'Node':
                        for i, value in enumerate(line):
                            if i == 0:
                                continue
                            value = float(value)
                            
                            # convert from cm to m
                            if measurement_units[i-1] in ['[L]','[L/T]']: #cm
                                value *= 0.01
                            elif measurement_units[i-1] == '[1/L]': # 1/cm
                                value *= 100.
                            
                            # convert moisture to liquid saturation
                            if moisture_first and measurements[i] == 'Moisture':
                                liquid_sat_denom = value
                                moisture_first = 0    
                            if  measurements[i] == 'Moisture':
                                value /= liquid_sat_denom
                                
                            # convert head to liquid pressure:
                            if  measurements[i] == 'Head':
                                value = (value * 9780) + 101325
                            
                            # append data values to corresponding measurement key
                            if measurements[i] not in data_dict.keys():
                                data_dict[measurements[i]] = [value]
                            else:
                                data_dict[measurements[i]].append(value)
                    
                    # Write each dataset to solution for corresponding measurement
                    elif 'end' in line:
                        for key, values in data_dict.items():
                            if key in h5_dataset_name_mapping.keys():
                                dataset_name = h5_dataset_name_mapping[key]
                            else:
                                dataset_name = key
                                
                            data_dict[key] = np.array([[values]])
                            solution.write_dataset(time, data_dict[key], dataset_name, group_name)
                            
                            # Write the coords
                            if coords_first:
                                coords_first = 0
                                # for 1D tests
                                x = 0.5 * (np.arange(1) + 1)
                                y = 0.5 * (np.arange(1) + 1)
                                z = np.reshape(data_dict['Depth'], -1)
                                solution.write_coordinates(x, y, z)
                            
                        data_dict = {}  # reset the dict for next time value
                """
        except FileNotFoundError:
            print('output file not found')
                
        debug_pop()
        return solution_filename
