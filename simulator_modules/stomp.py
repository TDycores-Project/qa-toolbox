# copied from pflotran and crunchflow code
import sys
import os
import numpy as np
from h5py import *

from qa_debug import *
from qa_common import *
from qa_solution import QASolutionWriter

from simulator_modules.simulator import QASimulator

eps = 1e-6
successful_exit_code = 86

time_mapping = {}
time_mapping['Aqueous Saturation'] = 'Liquid Saturation'
time_mapping['Aqueous Pressure, pa'] = 'Liquid Pressure'
n_variables = len(time_mapping)

class QASimulatorSTOMP(QASimulator):

    # check if we can use another input file name
    def __init__(self, path):
        debug_push('QASimulatorSTOMP init')
        super(QASimulatorSTOMP, self).__init__(path)
        self._name = 'input'
        debug_pop()

    def run(self, filename, annotation):
        debug_push('QASimulatorSTOMP _run')
        command = []
        command.append(self._get_full_executable_path())
        command.append(filename)
        debug_push('Running STOMP')
        status = self._submit_process(command, filename, annotation)
        debug_pop()
        solution_filename = self.convert_solution_to_common_h5(filename)
        debug_pop()
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

                    if ('Y-Direction Nodal Vertices, m' in line):
                        for line in fin:
                            line = line.strip()
                            words = line.split()
                            if not words:
                                break
                            # get y-centroid
                            y_centroid = (float(words[0]) + float(words[2])) * 0.5
                            y.append(y_centroid)

                    if ('Z-Direction Nodal Vertices, m' in line):
                        for line in fin:
                            line = line.strip()
                            words = line.split()
                            if not words:
                                break
                            # get z-centroid
                            z_centroid = (float(words[0]) + float(words[4])) * 0.5
                            z.append(z_centroid)

                fin.close()
                #check if all points are the same for one of the directions
                x_equal = all(elem == x[0] for elem in x)
                y_equal = all(elem == y[0] for elem in y)
                z_equal = all(elem == z[0] for elem in z)
                if x_equal:
                    x = [x[0]]
                if y_equal:
                    y = [y[0]]
                if z_equal:
                    z = [z[0]]
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

                for j, (key, v_name) in enumerate(time_mapping.items()):
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
                        solution.write_dataset(time,all_values_np, v_name,'Time Slice')
            fin.close()
        debug_pop()
        return solution_filename

