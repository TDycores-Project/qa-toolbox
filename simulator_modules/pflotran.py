import sys
import numpy as np
from h5py import *

from qa_debug import *
from qa_common import *
from qa_solution import QASolutionWriter

from simulator_modules.simulator import QASimulator

eps = 1e-6
successful_exit_code = 86

#update these names??
h5_mapping = {}
h5_mapping['liquid_pressure'] = 'Liquid Pressure'
h5_mapping['liquid_saturation'] = 'Liquid Saturation'
h5_mapping['Total_Tracer [M]'] = 'Tracer'
h5_mapping['Material_ID'] = 'Material_ID'
h5_mapping['Liquid_Pressure [Pa]'] = 'Liquid Pressure'
h5_mapping['Liquid_Saturation'] = 'Liquid Saturation'


obs_mapping = {}
obs_mapping['Liquid_Pressure'] ='Liquid Pressure'
obs_mapping['Liquid_Saturation'] = 'Liquid Saturation'
obs_mapping['Liquid Pressure [Pa]'] = 'Liquid Pressure'


class QASimulatorPFLOTRAN(QASimulator):

    def __init__(self,path):
        debug_push('QASimulatorPFLOTRAN init')
        super(QASimulatorPFLOTRAN,self).__init__(path)
        self._name = 'pflotran'
        self._suffix = '.in'
        debug_pop()

    def run(self,filename,annotation):
        debug_push('QASimulatorPFLOTRAN _run')
        root = filename.rsplit('.',1)[0]
        command = []
        command.append(self._get_full_executable_path())
        command.append('-input_prefix')
        command.append(root)
        command.append('-successful_exit_code')
        command.append('{}'.format(successful_exit_code))
        command.append('-output_prefix')
        command.append('{}_pft'.format(root))
        debug_push('Running PFLOTRAN')
        status = self._submit_process(command,filename,annotation)
        debug_pop()        
        if status != 86:
            print_err_msg('Pflotran simulator failed. Check {}_pflotran.stdout'.format(root))
        solution_filename = self.convert_solution_to_common_h5(root)
        debug_pop()        
        return solution_filename
    
    def convert_solution_to_common_h5(self,root):
      debug_push('QASimulatorPFLOTRAN convert_solution_to_common_h5')
      solution_filename = \
            '{}_pflotran.h5'.format(root)
      solution = QASolutionWriter(solution_filename)
      h5_filename = '{}_pft.h5'.format(root)
      tec_filename = '{}_pft-obs-0.tec'.format(root)
      time_slice = False
      observation_file = False      
      
      try: 
          f = File(h5_filename,'r')
          time_slice = True
      except:
          print ('No time slice file found, checking for observation file')

      if time_slice: 
          x, y, z = self.get_cell_centered_coordinates_h5(h5_filename)
          solution.write_coordinates(x,y,z)
        
          first = True
          group_name = 'Time Slice'

          for tkey in list(f.keys()):
              if tkey.startswith('Time'):
                  w = tkey.split()
                  time_string = float(w[1])
                  if first:
                      first = False
                      if len(w) < 3:
                          print('Time without unit in {}.'.format(h5_filename))
                          raise
                  solution.set_time_unit(w[2])
                  for dkey in list(f[tkey].keys()):

                      if dkey in h5_mapping:
                          new_key = h5_mapping[dkey]
                      else:
                          new_key = dkey
                      solution.write_dataset(time_string,
                                             np.array(f[tkey+'/'+dkey]),new_key,group_name)
                    
          f.close()
      
      try:
          fin = open(tec_filename,'r')
          observation_file = True
      except:
          print('No observation file found')
      
      if observation_file:
          group_name = 'Observation'        
          header = []
          all_values = []
          for line in fin:

              if ('Time' in line):
                  header = [x.strip('"').strip().strip(' "') for x in line.split(',')]
              else:
                  values = line.strip().split()
                  all_values.append(values)
    
          all_values = np.asarray(all_values, dtype=np.float64).transpose()
        
          solution.set_time_unit(header[0].split()[1].strip('[').strip(']'))
          solution.write_time(all_values[0])
        
          for i in range(1,len(header)):
         
              s = [x.strip(')').strip('(') for x in header[i].split()]

              location_string = s[-3:]
              location_floats = [float(i) for i in location_string]
              variable = all_values[i]
          
              dkey = header[i].split(' obs_pt')[0]
              
              if dkey in obs_mapping:
                  new_key = obs_mapping[dkey]
              else: 
                  new_key = dkey
              solution.write_dataset(location_floats,
                                     variable,new_key,group_name)
      debug_pop()                     
      return solution_filename   

        
    def get_cell_centered_coordinates_h5(self,filename):
        debug_push('QASimulatorPFLOTRAN get_cell_centered_coordinates_h5')
        x, y, z = self.get_coordinates_h5(filename,True)
        debug_pop()
        return x, y, z

    def get_coordinates_h5(self,filename,cell_centered=False):
        debug_push('QASimulatorPFLOTRAN get_coordinates_h5')
        try:
            f = File(filename,'r')
        except:
            print('Unable to read {}'.format(filename))
            raise

        keys = f.keys()
        list_of_keys = list(keys)

        x = []
        y = []
        z = []
        found = False
        for ckey in list(f.keys()):
            if ckey.startswith('Coordinates'):
                found = True
                for dkey in list(f[ckey].keys()):
                    full_key = ckey+'/'+dkey
                    if dkey.startswith('X'):
                        x = np.array(f[full_key])
                    elif dkey.startswith('Y'):
                        y = np.array(f[full_key])
                    elif dkey.startswith('Z'):
                        z = np.array(f[full_key])
                    else:
                        raise ValueError('Unrecognized key in ',
                                             'get_coordinates_h5')
        if not found:
            raise ValueError('Coordinates group not found in ',
                              '{}.'.format(filename))
        if x.size == 0:
            raise ValueError('X coordinates dataset not found in ',
                              '{}.'.format(filename))
        if y.size == 0:
            raise ValueError('Y coordinates dataset not found in ',
                              '{}.'.format(filename))
        if z.size == 0:
            raise ValueError('Z coordinates dataset not found in ',
                              '{}.'.format(filename))
        if cell_centered:
            xc = np.zeros(x.size-1,'=f8')
            yc = np.zeros(y.size-1,'=f8')
            zc = np.zeros(z.size-1,'=f8')
            for i in range(xc.size):
                xc[i] = 0.5*(x[i]+x[i+1])
            for i in range(yc.size):
                yc[i] = 0.5*(y[i]+y[i+1])
            for i in range(zc.size):
                zc[i] = 0.5*(z[i]+z[i+1])
            x = xc
            y = yc
            z = zc
        debug_pop()
        return x, y, z


    def update_dict(self,output_options):
        debug_push('QASimulatorPFLOTRAN update_dict')
#        for value in output_options.values():
#            new_entry=[x.strip() for x in value.split(',')]
#            h5_mapping[new_entry[0]]=new_entry[1]
#            obs_mapping[new_entry[0]]=new_entry[1]
        for key, value in output_options.items():
#            new_entry=value.strip()
            h5_mapping[key.strip()] = value.strip()
            obs_mapping[key.strip()] = value.strip()

        debug_pop()


