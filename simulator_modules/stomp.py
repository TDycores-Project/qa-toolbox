# copied from pflotran and crunchflow code
import sys
import os
import numpy as np
from h5py import *

from qa_debug import *
from qa_common import *
from qa_solution import QASolutionWriter

from simulator_modules.simulator import QASimulator

successful_exit_code = 86

time_slice_mapping = {}
time_slice_mapping['Aqueous Saturation'] = 'Liquid Saturation'
time_slice_mapping['Aqueous Pressure, pa'] = 'Liquid Pressure'
time_slice_mapping['Rock/Soil Type'] = 'Material_ID'

class QASimulatorSTOMP(QASimulator):

    def __init__(self, path):
        debug_push('QASimulatorSTOMP init')
        super(QASimulatorSTOMP, self).__init__(path)
        self._name = 'input'
        debug_pop()

    def run(self, filename, annotation):
        debug_push('QASimulatorSTOMP _run')
        command = []
        os.symlink(filename, 'input')
        command.append(self._get_full_executable_path())
        debug_push('Running STOMP')
        status = self._submit_process(command, filename, annotation)
        debug_pop()
        solution_filename = self.convert_solution_to_common_h5(filename)
        debug_pop()
        os.unlink('input')

        # Rename output files
        # List of output files that can't fail
        output_required = ['output', 'connect']
        for i in range(len(output_required)):
            try:
                new_name = filename + '_' + output_required[i]
                os.rename(output_required[i], new_name)
            except OSError:
                print('ERROR: STOMP output file {} does not exist.'.format(output_required[i]))
        
        output_optional = ['surface']
        # Go through files in the directory and look for files starting with plot
        for r, dirct, files in os.walk('.'):
            for name in files:
                if name.startswith('plot'):
                    output_optional.append(name)

        for i in range(len(output_optional)):
            try:
                new_name = filename + '_' + output_optional[i]
                os.rename(output_optional[i], new_name)
            except OSError:
                pass

        # If you think we don't need to set "try" for the optional filenmanes,
        # we can just join lines 58-63 into the os.walk, with something like this:

        # output_optional = ['surface', 'plot']
        # for r, dirct, files in os.walk('.'):
        #     for name in files:
        #         for i in range(len(output_optional)):
        #             if name.startswith(output_optional[i]):
        #                 new_name = filename + '_' + output_optional[i]
        #                 os.rename(output_optional[i], new_name)

        return solution_filename

    def output_file_patterns(self):
        patterns = ['plot*','surface', 'output', 'connect', '.*_run\d*_stomp\.h5']
        return patterns 

    def convert_solution_to_common_h5(self, filename):
        debug_push('QASimulatorSTOMP convert_solution_to_common_h5')
        solution_filename = '{}_stomp.h5'.format(filename)
        solution = QASolutionWriter(solution_filename)

        tslice_out = []
        x = []
        y = []
        z = []
        dim = [''] * 3
        first_file = True

        for r, dirct, files in os.walk('.'):
            for name in files:
                if name.startswith('plot') and not name.endswith('.dat'):
                    tslice_out.append(name)

        for i in range(len(tslice_out)):
            if first_file:
                fin = open(tslice_out[i], 'r')
                for line in fin:
                    line = line.strip()
                    if line == []:
                        continue
                    #get dimensions
                    if ('Number of X' in line):
                        words = line.split('=')
                        n = words[1].split()
                        dim[0] = int(n[0])
                    if ('Number of Y' in line):
                        words = line.split('=')
                        n = words[1].split()
                        dim[1] = int(n[0]) 
                    if ('Number of Z' in line):
                        words = line.split('=')
                        n = words[1].split()
                        dim[2] = int(n[0])

                    #get coordinates
                    if ('X-Direction Nodal Vertices, m' in line):
                        for line in fin:
                            line = line.strip()
                            words = line.split()
                            if not words:
                                break
                            # get x-centroid
                            x_centroid = (float(words[0]) + float(words[1])) * 0.5
                            x.append(x_centroid)
                        x = x[:dim[0]]

                    if ('Y-Direction Nodal Vertices, m' in line):
                        for line in fin:
                            line = line.strip()
                            words = line.split()
                            if not words:
                                break
                            # get y-centroid
                            y_centroid = (float(words[0]) + float(words[2])) * 0.5
                            y.append(y_centroid)
                        start = 0
                        stop = dim[0]*dim[1]
                        step = dim[0]
                        keep_ind = np.arange(start,stop,step)
                        y = [y[ind] for ind in keep_ind]

                    if ('Z-Direction Nodal Vertices, m' in line):
                        for line in fin:
                            line = line.strip()
                            words = line.split()
                            if not words:
                                break
                            # get z-centroid
                            z_centroid = (float(words[0]) + float(words[3])) * 0.5
                            z.append(z_centroid)
                        start = 0
                        stop = dim[0]*dim[1]*dim[2]
                        step = dim[0]*dim[1]
                        keep_ind = np.arange(start,stop,step)
                        z = [z[ind] for ind in keep_ind]

                fin.close()
                #check if one of the coordinates is empty and if so, populate with a (0.5 value)
                #Note: For 2D problems, Stomp only output 2 of the 3 dimensions
                if not x:
                    x = [0.5]
                if not y:
                    y = [0.5]
                if not z:
                    z = [0.5]

                solution.write_coordinates(x,y,z)
                first_file = False
            # read file
            fin = open(tslice_out[i], 'r')
            time = None
            all_values = []
            for line in fin:
                line = line.strip()
                if line == []:
                    continue
                # get time
                if ('Time =  ' in line):
                    words = line.split()
                    time_units = words[5].split(',')
                    time = float(time_units[0])
                    t_units = time_units[1]
                    solution.set_time_unit(t_units)

                for j, (key, v_name) in enumerate(time_slice_mapping.items()):
                    all_values = []
                    if (key in line):
                        for line in fin:
                            line = line.strip()
                            words = line.split()
                            if not words:
                                break
                            for var_values in words:
                                all_values.append(float(var_values))
                        all_values_np = np.asarray(all_values, dtype=np.float64).transpose()
                        all_values_np = np.reshape(all_values_np, (dim[0], dim[1], dim[2]), order='F')
                        solution.write_dataset(time,all_values_np, v_name,'Time Slice')
            fin.close()
        debug_pop()
        return solution_filename

