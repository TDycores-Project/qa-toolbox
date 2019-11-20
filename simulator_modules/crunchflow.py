import sys
import os
import numpy as np
import re

from qa_debug import *
from qa_common import *
from qa_solution import QASolutionWriter

from simulator_modules.simulator import QASimulator

obs_mapping = {}
time_mapping = {}

class QASimulatorCrunchFlow(QASimulator):

    def __init__(self,path):
        debug_push('QASimulatorCrunchFlow init')
        super(QASimulatorCrunchFlow,self).__init__(path)
        self._name = 'crunchflow'
        self._suffix = '.in'
        debug_pop()

    def run(self,filename,annotation):
        debug_push('QASimulatorCrunchFlow _run')
        command = []
        command.append(self._get_full_executable_path())
        command.append(filename) #+'.in')
        debug_push('Running CrunchFlow')
        status=self._submit_process(command,filename,annotation)
        if status != 0:
            print_err_msg('Crunchflow simulator failed. Check {}'.format(filename))
        solution_filename = self.convert_solution_to_common_h5(filename)
        debug_pop()
        return solution_filename        


    def convert_solution_to_common_h5(self,filename):
        root = filename.rsplit('.',1)[0]
        solution_filename = '{}_crunchflow.h5'.format(root)
        solution = QASolutionWriter(solution_filename)

        c_out = [] 
        obs_out = []
        
        for root, dire, files in os.walk('.'):
            for name in files:
                if (name.startswith('conc') or
                    name.startswith('saturation')) \
                    and (name.endswith('.out') or   ###not gonna work
                    name.endswith('.tec')):
                    c_out.append(name)
                if (name.startswith('crunch_observation') and
                    name.endswith('.out')):
                    obs_out.append(name)                    
                    
        first = True
        

        for i in range(len(c_out)):
            fin = open(c_out[i], 'r')
            log = False
            
            time = None
            variables = None
            
            all_values = []
            for line in fin:
                words = line.strip().split()
                if words == []:
                    continue
                if ('Time' in words):
                    time = float(words[-1].strip())
                if ('Distance' in words):
                    variables = words
                if ('VARIABLES' in words): 
                    variables = [x.strip('"') for x in words]
                    variables = variables[2:]
                    
                if ('Log10' in words):
                    log = True
                if words[0][0].isdigit():
                    values = words
                    
                    all_values.append(values)
            
            all_values = np.asarray(all_values, dtype=np.float64).transpose()
            
            if not variables:
                print ('ERROR: headers could not be found in %s.opt file' 
                         % c_out[i])
                sys.exit(0)
            
            if not time:
                num = re.findall(r'\d+', c_out[i])
                time, time_unit = self._find_time_tecplot(filename,int(num[0])) ##return time unit
            else:
                time_unit = self._find_time_unit_outfile(filename)
             
            solution.set_time_unit(time_unit)
            
            if variables[0]=='Distance':
               #write_coordinates
                if first == True:

                    x = all_values[0]
                    y = np.ones(len(all_values[0]))
                    z = np.ones(len(all_values[0]))
                   
                    solution.write_coordinates(x,y,z)
                    first = False
               
                for n in range(1,len(all_values)):
                    if variables[n] in time_mapping:
                        new_key = time_mapping[variables[n]]
                    else:
                        new_key = variables[n] 
                   
                    if log == True: #####TECPLOT DOESN'T RECORD IF ITS LOG OR NOT?????

                        solution.write_dataset(time,10**all_values[n], new_key,'Time Slice')
                    else:
                        solution.write_dataset(time,all_values[n], new_key,'Time Slice') 
               
            else:
                if first == True:
                    x = all_values[0]
                    y = all_values[1]
                    z = all_values[2]
                 
                    first = False
                    solution.write_coordinates(x,y,z)
               
                for n in range(3,len(all_values)):
                    if variables[n] in time_mapping:
                        new_key = time_mapping[variables[n]]
                    else:
                        new_key = variables[n] 
                    if log == True:
                     
                        all_values[n] == 10**all_values

                    solution.write_dataset(time,all_values[n],new_key,'Time Slice')
                 
        first = True         
        for i in range(len(obs_out)):

            counter = 0
            fin = open(obs_out[i], 'r')
            all_values = []

            for line in fin:
                words = line.strip().split()
                if counter == 0:
                    location = words[-3:]   
                    location = self._convert_location(filename,location)
                if counter == 1:
                    if ('VARIABLES' in words):
                        variables = [x.strip('"').strip('(').strip(')') for x in words]
                        variables = [val for val in variables if val.isalnum()]
                        variables = variables[1:]
                        solution.set_time_unit(variables[1])
                        variables.pop(1)
                    else:
                        variables = words
                        solution.set_time_unit(variables[0].strip(')').split('(')[1])
                if words[0][0].isdigit():
                    values = words
                    all_values.append(values)
                counter = counter+1
            all_values = np.asarray(all_values, dtype=np.float64).transpose()
            
            
            if first == True:
                solution.write_time(all_values[0])
                first = False
              
            
            for n in range(1,len(all_values)):
                if variables[n] in obs_mapping:
                    new_key = time_mapping[variables[n]]
                else:
                    new_key = variables[n] 
                solution.write_dataset(location,
                                       all_values[n],new_key,'Observation')
            
        solution.destroy()
        return solution_filename


    def _convert_location(self,filename,location):
        fin = open(filename,'r')
        x_new = 1
        y_new = 1
        z_new = 1
        for line in fin:
            words=line.strip().split()
            if 'xzones' in words: ##make case insensitive
                node_num = 0
                x_new = 0
                nodes_left = int(location[0])
                for i in range(1,len(words),2):
                    node_num = node_num+float(words[i] )
                    if node_num > int(location[0]):
                        break
                    else:
                        x_new = x_new+float(words[i])*float(words[i+1])
                        nodes_left = nodes_left-float(words[i])
                x_new = x_new + nodes_left * float(words[i+1])
            if 'yzones' in words:
                node_num = 0
                y_new = 0
                nodes_left = int(location[1])
                for i in range(1,len(words),2):
                    node_num = node_num + float(words[i]) 
                    if node_num>int(location[1]):
                        break
                    else:
                        y_new = y_new + float(words[i]) * float(words[i+1])
                        nodes_left = nodes_left-float(words[i])
                y_new = y_new + nodes_left * float(words[i+1])
                
            if 'zzones' in words:
                node_num = 0
                z_new = 0
                nodes_left = int(location[2])
                for i in range(1,len(words),2):
                    node_num = node_num + float(words[i]) 
                    if node_num>int(location[2]):
                        break
                    else:
                        z_new = z_new + float(words[i]) * float(words[i+1])
                        nodes_left = nodes_left-float(words[i])
                z_new = z_new + nodes_left * float(words[i+1])
        new_location = [x_new,y_new,z_new] ############ yzones and zzones when comparing???
        
        return new_location
    
    
    def update_dict(self,output_options):
        debug_push('QASimulatorCRUNCHFLOW update_dict')
#        for value in output_options.values():
#            new_entry = [x.strip() for x in value.split(',')]
#            time_mapping[new_entry[0]] = new_entry[1]
#            obs_mapping[new_entry[0]] = new_entry[1]
        for key, value in output_options.items():
#            new_entry=value.strip()
            time_mapping[key.strip()] = value.strip()
            obs_mapping[key.strip()] = value.strip()
        debug_pop()
    
    def _find_time_tecplot(self,filename,num):
        fin = open(filename, 'r')
        time = None
        time_units = None
        block = False
        for line in fin: 
            words = line.strip().split()
            
            if ('OUTPUT') in words:
                block = True
              
            if block == True:
                if 'time_units' in words:
                    time_units = words[1]
                    block = False
                if 'END' in words:
                    block = False
            if ('spatial_profile_at_time' or 'spatial_profile') in words:              
                time = float(words[num])
        if not time:
            print ('ERROR: time could not be found in {} file'.format(filename))
            sys.exit(0)
        if not time_units:
            print ('ERROR: time units could not be found in {} file'.format(filename))
            sys.exit(0)
          
        return time, time_units
    
    def _find_time_unit_outfile(self,filename):
        fin = open(filename, 'r')
        block = False
        
        time_units = None
        
        for line in fin:
            words = line.strip().split()

            if ('OUTPUT') in words:
                block = True
            if block == True:
                if 'time_units' in words:
                    time_units = words[1]
                    block = False
                if 'END' in words:
                    block = False
        if not time_units:
            print ('ERROR: time could not be found in {} file'.format(filename))
            sys.exit(0)
    
        return time_units
    

