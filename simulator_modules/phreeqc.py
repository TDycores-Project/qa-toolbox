from qa_debug import *
from qa_common import *
from qa_solution import QASolutionWriter
import numpy as np

from simulator_modules.simulator import QASimulator

"""
Class for running the PHREEQC simulator. Should work for observation and
time slice file comparisons. In the .opt file used for tests, should specify
the time units with plot_time_units. This class is under the assumption
PHREEQC calculates in seconds. Additional variables needed to display 
should be added to the mapping dicitonaries in the convert_solution_to_common_h5
function.

Calvin Madsen: 7/19/23
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
        status = self._submit_process(command,filename,annotation)
        debug_pop()
        if status != 0:
            print_err_msg('PHREEQC simulator failed. Check {}'.format(filename))
        
        # convert the output file to the common h5 version
        solution_filename = self.convert_solution_to_common_h5(filename)
        debug_pop()
        
        return solution_filename
    
    def convert_solution_to_common_h5(self,input_filename):
        debug_push('QASimulatorPHREEQC convert_solution_to_common_h5')
        solution_filename = get_h5_output_filename(input_filename, self._name)
        selected_output = input_filename.split(self._name)[0].rstrip('_') + '.sel'
        options_file = input_filename.split(self._name)[0].rstrip('_') + '.opt'

        solution = QASolutionWriter(solution_filename)

        group_name = 'Time Slice' # Default
        time_units = 'y' # Default
        locations = []
        measurement_labels = []
        data_dict = {}
        
        # analyze .opt file
        with open(options_file, 'r') as f:
            for line in f:
                line = line.strip().split()
                if line[0] == 'plot_type':
                        group_name = line[2].capitalize()
                        if group_name == 'Time':
                            group_name = 'Time Slice'
                if line[0] == 'locations':
                    for i in range(2, len(line)):
                        locations.append(float(line[i]))
                if line[0] == 'plot_time_units':
                    time_units = line[2]
        
        # mapping from phreeqc to pflotran labels
        h5_dataset_name_mapping = {'m_Ca+2': 'Free_Ca++ [m]',
                                   'm_H+': 'Free_H+ [m]',
                                   'm_HCO3-' : 'Free_HCO3- [m]'
                                   }
        if group_name == 'Observation':
            obs_dataset_name_mapping = {'m_Ca+2': 'Free Ca++ [M] all (1) ({} {} {})'.format(*locations),
                                        'm_H+': 'Free H+ [M] all (1) ({} {} {})'.format(*locations),
                                        'm_HCO3-' : 'Free HCO3- [M] all (1) ({} {} {})'.format(*locations)
                                        }
        labels_first = 1
        labels_first_dist = 1
        coords_first = 1
        
        try:
            with open(selected_output, 'r') as f:   
                # Find the max distance in dist_x    
                max_dist = 0
                if group_name == 'Time Slice':
                    for line in f:
                        line = line.strip().split()  
                        if labels_first_dist:
                            for i, label in enumerate(line):
                                measurement_labels.append(label)             
                            labels_first_dist = 0
                            continue
                        
                        for i, value in enumerate(line):
                            value = float(value)
                            if measurement_labels[i] not in data_dict:
                                data_dict[measurement_labels[i]] = [value]
                            else:
                                data_dict[measurement_labels[i]].append(value)
                    max_dist = np.max(data_dict['dist_x'])
                    data_dict = {}
                    measurement_labels = []
                    f.seek(0)  

                # Reset after max dist is found        
                for line in f:
                    # Split each line into a list separated by whitespace
                    line = line.strip().split()                    
                    
                    # Find measurement labels and time index (always on first line)
                    if labels_first:
                        for i, label in enumerate(line):
                            measurement_labels.append(label)             
                        labels_first = 0
                        continue
                    
                    # Append data points to corresponding measurement key
                    for i, value in enumerate(line):
                        value = float(value)
                        if measurement_labels[i] not in data_dict:
                            data_dict[measurement_labels[i]] = [value]
                        else:
                            data_dict[measurement_labels[i]].append(value)
                                                        
                    # Set time units
                    solution.set_time_unit(time_units)
                                
                    if group_name == 'Time Slice':
                        # Find current time (step)
                        time = float(data_dict['step'][-1])

                        # Write each dataset to solution for corresponding measurement
                        if data_dict['dist_x'][-1] == max_dist: 
                            for key, values in data_dict.items():
                                if key in h5_dataset_name_mapping:
                                    dataset_name = h5_dataset_name_mapping[key]
                                else:
                                    dataset_name = key
                                    
                                data_dict[key] = np.array([[values]])
                                
                                solution.write_dataset(time, data_dict[key], dataset_name, group_name)
                                
                                # Write the coords
                                if coords_first:
                                    coords_first = 0
                                    # for 1D tests
                                    x = np.reshape(data_dict['dist_x'], -1)
                                    y = 1 * (np.arange(1) + 1)
                                    z = 1 * (np.arange(1) + 1)
                                    solution.write_coordinates(x, y, z)
                                
                            data_dict = {}  # reset the dict for next time value
                            
                if group_name == 'Observation':
                    for key, values in data_dict.items():
                        if key in obs_dataset_name_mapping:
                            dataset_name = obs_dataset_name_mapping[key]
                        else:
                            dataset_name = key
                            
                        data_dict[key] = np.array(values)
                        
                        solution.write_dataset(dimension=locations, soln=data_dict[key], dataset_name=dataset_name, group=group_name)
                        
                    # configure times, assuming phreeqc calculates in seconds
                    data_dict['time'][data_dict['time'] < 0] = 0 # make negative times 0
                    if time_units == 'd':
                        data_dict['time'] /= (3600 * 24)
                    elif time_units == 'm':
                        data_dict['time'] /= (3600 * 24 * 30)
                    elif time_units == 'y':
                        data_dict['time'] /= (3600 * 24 * 365)
                        
                    solution.write_time(data_dict['time'])
                    
        except FileNotFoundError:
            print(f'selected output file {selected_output} not found')
                
        debug_pop()
        return solution_filename
