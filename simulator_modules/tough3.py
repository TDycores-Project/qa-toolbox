import sys
import os
import csv 
import numpy as np

from qa_debug import *
from qa_common import *
from qa_solution import QASolutionWriter

from simulator_modules.simulator import QASimulator

time_mapping = {}
time_mapping['PRES'] = 'Liquid Pressure'
time_mapping['SAT_L'] = 'Liquid Saturation'

obs_mapping = {}
obs_mapping['PRES'] = 'Liquid Pressure'
obs_mapping['SAT_L'] = 'Liquid Saturation'

eps=1e-3

class QASimulatorTOUGH3(QASimulator):

    def __init__(self,path):
        debug_push('QASimulatorTOUGH3 init')
        super(QASimulatorTOUGH3,self).__init__(path)
        self._name = 'tough3'
        self._suffix = '.in'
#        self._observation_point = False
#        self._time_slice = True
        self._elements = None
        self.locations = None
        debug_pop()
        
    def output_file_patterns(self):
        patterns = ['FOFT*','OUTPUT*','GENER','SAVE','TABLE','MESHA',
                  'MESHB','MESHB','INCON','.*_run\d*_tough3\.h5']
        return patterns 

    def run(self,filename,annotation,np):
        debug_push('QASimulatorTOUGH3 _run')
        command = []
        command.append(self._get_full_executable_path())
        command.append(filename)#+'.in')
##        command.append(filename+'.out')
        debug_push('Running TOUGH3')
        #uncomment below if have tough3 simulator
        #status=self._submit_process(command,filename,annotation)
        debug_pop()        
       # if status != 0:
       #     print_err_msg('Tough3 simulator failed. Check {}_tough3.stdout'.format(filename.split('.')[0]))
        solution_filename = self.convert_solution_to_common_h5(filename)
        debug_pop()        
        return solution_filename

    def convert_solution_to_common_h5(self,filename):
        root = filename.rsplit('.',1)[0]
        solution_filename = '{}_tough3.h5'.format(root)
        solution = QASolutionWriter(solution_filename)
        
        tough_obs = []
        for root, dire, files in os.walk('.'):
            for name in files:
                if (name.startswith('FOFT')) \
                    and (name.endswith('.csv')):
                        tough_obs.append(name)

        self._process_output_time_slice('OUTPUT_ELEME.csv',solution)
                       
        if len(tough_obs) > 0:
            self._process_output_observation_file(solution,tough_obs)
            
        solution.destroy()
        return solution_filename

    def update_dict(self,output_options):
        debug_push('QASimulatorTOUGH3 update_dict')

        for key, value in output_options.items():
            time_mapping[key.strip()] = value.strip()
            obs_mapping[key.strip()] = value.strip()
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
        var= False
        with open(filename,'r') as f:
            row = csv.reader(f)
            all_values = []
            for line in row:
                if 'Z' in line[0].strip():

                    if var==False:
                      variables = [x.strip() for x in line[1:]]
                      var = True
                elif 'TIME' in line[0].strip():
                    if len(all_values) != 0:
                        all_values = np.asarray(all_values, dtype=np.float64).transpose()
                        ###remove dummy variables
                     #   all_values = self._remove_bad_values(all_values)
                        for n in range(1,len(all_values)):
                            if variables[n-1] in time_mapping:
                                new_key = time_mapping[variables[n-1]]
                            else:
                                new_key = variables[n-1]

                            solution.write_dataset(time,all_values[n], new_key,'Time Slice')
                        all_values = []
                    time_info = line[0].split()
                    time = float(time_info[2].strip())
                    time_unit = time_info[1].strip().strip('[').strip(']')
                    if first == True:
                        solution.set_time_unit(time_unit)
                        first = False
                elif 'Z' in line[0].strip() or '(M)' in line[0].strip():
                    continue
                else:     
                    values = line[0:]
                    all_values.append(values)                     
        all_values = np.asarray(all_values, dtype=np.float64).transpose()
        ##remove dummy variables
     #   all_values = self._remove_bad_values(all_values)

        z = all_values[0]
        x = 0.5 * np.ones(len(all_values[0]))
        y = 0.5 * np.ones(len(all_values[0]))
#        y = all_values[1]
#        z = all_values[2]
               
        solution.write_coordinates(x,y,z)
        #####change
      #  for n in range(3,len(all_values)):

        for n in range(1,len(all_values)):
            if variables[n-1] in time_mapping:
                new_key = time_mapping[variables[n-1]]
            else:
                new_key = variables[n-1]
            solution.write_dataset(time,all_values[n], new_key,'Time Slice')
        
    def _process_output_observation_file(self,solution,tough_obs):
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
        number_to_delete = len(bad_mesh_values) 
        return number_to_delete
                











