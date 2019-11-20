import sys
import os
import csv 
import numpy as np

from qa_debug import *
from qa_common import *

from simulator_modules.simulator import QASimulator
from simulator_modules.solution import SolutionWriter

time_mapping = {}
time_mapping['PRES'] = 'Liquid_Pressure'
time_mapping['SAT_L'] = 'Liquid_Saturation'

obs_mapping = {}
obs_mapping['PRES'] = 'Liquid_Pressure'
obs_mapping['SAT_L'] = 'Liquid_Saturation'

eps=1e-3

class QASimulatorTOUGH3(QASimulator):

    def __init__(self,path):
        debug_push('QASimulatorTOUGH3 init')
        super(QASimulatorTOUGH3,self).__init__(path)
        self._name = 'tough3'
        self._suffix = '.in'
        self._observation_point = False
        self._time_slice = True
        self._elements = None
        self.locations = None
        self.delete_values = False
        debug_pop()

    def run(self,filename,annotation):
        debug_push('QASimulatorTOUGH3 _run')
        command = []
        command.append(self._get_full_executable_path())
        command.append(filename)#+'.in')
#        command.append(filename+'.out')
        debug_push('Running TOUGH3')
        status=self._submit_process(command,filename,annotation)
        if status != 0:
            print_err_msg('Tough3 simulator failed. Check {}_tough3.stdout'.format(filename.split('.')[0]))
        solution_filename = self.convert_solution_to_common_h5(filename)
        debug_pop()        
        return solution_filename

    def convert_solution_to_common_h5(self,filename):
        root = filename.rsplit('.',1)[0]
        solution_filename = '{}_tough3.h5'.format(root)
        solution = SolutionWriter(solution_filename)
        
        tough_obs = []
        for root, dire, files in os.walk('.'):
            for name in files:
                if (name.startswith('FOFT')) \
                    and (name.endswith('.csv')):
                        tough_obs.append(name)

        
        if self._time_slice == True:
            self._process_output_time_slice('OUTPUT_ELEME.csv',solution)
            
           
        if self._observation_point == True or len(tough_obs)>0:
            self._process_output_observation_file(solution,tough_obs)
            
        solution.destroy()
        return solution_filename

    def update_dict(self,output_options):
        debug_push('QASimulatorTOUGH3 update_dict')
#        for value in output_options.values():
#            new_entry = [x.strip() for x in value.split(',')]
#            time_mapping[new_entry[0]] = new_entry[1]
#            obs_mapping[new_entry[0]] = new_entry[1]
        for key, value in output_options.items():
#            new_entry=value.strip()
            time_mapping[key.strip()] = value.strip()
            obs_mapping[key.strip()] = value.strip()
        debug_pop()
    
    def process_tough_options(self,tough_options,output_options):
        debug_push('QASimulatorTOUGH process_tough_options')
#        self._observation_point = tough_options['observation_point']
        self._observation_point = qa_lookup(tough_options,'observation_point',False)
        if self._observation_point == True:
            if 'elements' in tough_options.keys():
                self._elements = [x.strip() for x in tough_options['elements'].split(',')]
            else:
                self.locations = location_strings_to_float_list(output_options['locations'])  
            
        self._time_slice = qa_lookup(tough_options,'time_slice',True)
        self.delete_values = qa_lookup(tough_options,'delete_values',False)

        
        debug_pop()
        
    def _get_location_from_element(self,output_file,element):
      location = None
      with open(output_file,'r') as f:
          row = csv.reader(f)
            
          for line in row:                  
              if line[0].strip() == element:
                  location = [float(x) for x in line[1:4]]
                  break
          if location == None:
              print_err_msg('Element {} not found in tough3 output file'.format(element))
        
      return location
  
    def _get_element_from_filename(self,filename):
        filename = filename.replace('.','_')
        filename = filename.split('_')

        s = ' '  
        element = s.join(filename[1:-1])
        element = element.strip()
        
        return element
  
    def _process_output_time_slice(self,filename,solution):
        first = True
        with open(filename,'r') as f:
            row = csv.reader(f)
            all_values = []
            for line in row:
                if 'ELEM' in line[0].strip():
                    variables = [x.strip() for x in line[1:]]
                elif 'TIME' in line[0].strip():
                    if len(all_values) != 0:
                        all_values = np.asarray(all_values, dtype=np.float64).transpose()
                        if self.delete_values == True:
                            all_values = self._remove_bad_values(all_values)
                        for n in range(3,len(all_values)):
                            if variables[n] in time_mapping:
                                new_key = time_mapping[variables[n]]
                            else:
                                new_key = variables[n]

                            solution.write_dataset(time,all_values[n], new_key,'Time Slice')
                        all_values = []
                    time_info = line[0].split()
                    time = float(time_info[2].strip())
                    time_unit = time_info[1].strip().strip('[').strip(']')
                    if first == True:
                        solution.set_time_unit(time_unit)
                        first = False
                elif '' == line[0].strip():
                    continue
                else:
                    values = line[1:]
                    all_values.append(values)
                
                
        all_values = np.asarray(all_values, dtype=np.float64).transpose()
        if self.delete_values == True:
            all_values = self._remove_bad_values(all_values)
        
        x = all_values[0]
        y = all_values[1]
        z = all_values[2]
               
        solution.write_coordinates(x,y,z)
        
        for n in range(3,len(all_values)):
            if variables[n] in time_mapping:
                new_key = time_mapping[variables[n]]
            else:
                new_key = variables[n]
            solution.write_dataset(time,all_values[n], new_key,'Time Slice')
          
            
        
    def _process_output_observation_file(self,solution,tough_obs):
        if len(tough_obs) > 0:
            self._search_observation_foft_file(solution,tough_obs)

        else:   
            if self._elements != None:
                self._search_output_observation_element(solution)
          
            else:
                self._search_output_observation_location(solution)
                  
                  
    
    def _search_observation_foft_file(self,solution,tough_obs):
        first = True
        for k in range(len(tough_obs)):
            with open(tough_obs[k],'r') as f:

                all_values = []
                row = csv.reader(f)
                header = next(row)
                variables = [x.strip() for x in header]
                time_unit = variables[0].strip(')').split('(')
                time_unit = time_unit[1]
    
                for line in row:
                    values = line
                    all_values.append(values)
                
            all_values = np.asarray(all_values, dtype=np.float64).transpose()
          
            element=self._get_element_from_filename(tough_obs[k])
            location=self._get_location_from_element('OUTPUT_ELEME.csv',element)
          
            if first == True:
                solution.write_time(all_values[0])
                solution.set_time_unit(time_unit)
                first = False                
          
            for n in range(1,len(all_values)):
                if variables[n] in obs_mapping:
                    new_key = time_mapping[variables[n]]
                else:
                    new_key = variables[n] 
                solution.write_dataset(location,
                                       all_values[n],new_key,'Observation')

        
    def _search_output_observation_element(self,solution):
        first = True
        for i in range(len(self._elements)):
            with open('OUTPUT_ELEME.csv','r') as f:
                time_array = []
                all_values = []

        
                row = csv.reader(f)
        
                for line in row:           
                    if 'ELEM' in line[0].strip():     ####better way to do this?
                        if first == True:            
                            variables = [x.strip() for x in line[1:]]              
                    elif 'TIME' in line[0].strip(): 
                        if first == True:
                            time_info = line[0].split()
                            time = float(time_info[2].strip())
                            time_unit = time_info[1].strip().strip('[').strip(']')
 
                            time_array.append(time)
                    elif '' == line[0].strip():
                        continue
                    else:
                        if line[0].strip() == self._elements[i]:
                            values = [float(x) for x in line[1:]]
                            all_values.append(values)
                            location = [float(x) for x in line[1:4]]
                      
                              ##add in error raise if all_values is empty

            all_values = np.asarray(all_values, dtype=np.float64).transpose()
            if first == True:
                solution.write_time(time_array)
                solution.set_time_unit(time_unit)
                first = False
        
            for n in range(3,len(all_values)):
                if variables[n] in obs_mapping:
                    new_key = time_mapping[variables[n]]
                else:
                    new_key = variables[n] 
                solution.write_dataset(location,
                             all_values[n],new_key,'Observation')

    
    
    def _search_output_observation_location(self,solution):
        first = True
        location = self.locations
        if location == None:
            raise Exception('No Tough observation file found or tough options specified in options block')
        for i in range(len(location)):
            with open('OUTPUT_ELEME.csv','r') as f:
                time_array = []
                all_values = []
        
                row = csv.reader(f)
        
                for line in row: 
           
                    if 'ELEM' in line[0].strip():
                        if first == True:
                            variables = [x.strip() for x in line[1:]]              
                    elif 'TIME' in line[0].strip(): 
                        if first == True:
                            time_info = line[0].split()
                            time = float(time_info[2].strip())
                            time_unit = time_info[1].strip().strip('[').strip(']')
 
                            time_array.append(time)
                    elif '' == line[0].strip():
                        continue
                    else:
              
                        values = [float(x) for x in line[1:]]

                        if ((abs(values[0]-location[i][0]) < eps) and 
                            (abs(values[1]-location[i][1]) < eps) and 
                            (abs(values[2]-location[i][2]) < eps)): 
                            all_values.append(values)
                
          ##add in error raise if all_values is empty
            all_values = np.asarray(all_values, dtype=np.float64).transpose()
            if first == True:
                solution.write_time(time_array)
                solution.set_time_unit(time_unit)
                first = False
        
            for n in range(3,len(all_values)):
                if variables[n] in obs_mapping:
                    new_key = time_mapping[variables[n]]
                else:
                    new_key = variables[n] 
                solution.write_dataset(location[i],
                                       all_values[n],new_key,'Observation')
    def _remove_bad_values(self,input_matrix):
        number_to_delete = self._search_mesh()    

        array_indices = []
        column_length=len(input_matrix[0])-1
        for i in range(number_to_delete):
            array_indices.append(column_length-i)
        output_matrix = np.delete(input_matrix, array_indices,1)

        
        return output_matrix
                
    def _search_mesh(self): ###delete elements without any mesh values
        bad_mesh_values=[]
        fin = open('MESH','r')

        for line in fin:
            values=line.strip().split()
            if len(values)!=0 and len(values)<4:
                if 'CONNE' in values:
                    break
                bad_mesh_values.append(values)
        number_to_delete = len(bad_mesh_values) ###or search by element to delete???
        return number_to_delete
                










