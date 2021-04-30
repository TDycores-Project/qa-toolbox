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

# update these names??
h5_mapping = {}
h5_mapping['liquid_pressure'] = 'Liquid Pressure'
h5_mapping['liquid_saturation'] = 'Liquid Saturation'
h5_mapping['Total_Tracer [M]'] = 'Tracer'
h5_mapping['Material_ID'] = 'Material_ID'
h5_mapping['Liquid_Pressure [Pa]'] = 'Liquid Pressure'
h5_mapping['Liquid_Saturation'] = 'Liquid Saturation'
h5_mapping['Liquid_Pressure'] = 'Liquid Pressure'

obs_mapping = {}
obs_mapping['Liquid_Pressure'] = 'Liquid Pressure'
obs_mapping['Liquid_Saturation'] = 'Liquid Saturation'
obs_mapping['Liquid Pressure [Pa]'] = 'Liquid Pressure'


class QASimulatorSTOMP(QASimulator):

    # check if we can use another input file name
    def __init__(self, path):
        debug_push('QASimulatorSTOMP init')
        super(QASimulatorSTOMP, self).__init__(path)
        self._name = 'input'
        debug_pop()

    # Check if this function is needed:
    def output_file_patterns(self):
        patterns = ['.*_run\d*_pflotran\.h5', '.*_run\d*_pft\.h5']
        return patterns

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

    def convert_solution_to_common_h5(self, filename):
        debug_push('QASimulatorSTOMP convert_solution_to_common_h5')
        root = filename.rsplit('.', 1)[0]
        solution_filename = '{}_stomp.h5'.format(root)
        solution = QASolutionWriter(solution_filename)

        tslice_out = []
        for root, dire, files in os.walk('.'):
            for name in files:
                if (name.startswith('plot'):
                    tslice_out.append(name)

        for i in range(len(tslice_out)):
            # read file
            fin = open(tslice_out[i], 'r')
            for line in fin:
                line = line.strip()
                if line == []:
                    continue
                # get time
                if ('Time =  ' in line):
                    words = line.split()
                    time_units = words[5].split(',')
                    time = time_units[0]
                    units = time_units[1]
                #get coordinates
                if ('X-Direction Nodal Vertices, m' in line):
                    # continue reading the following lines
                    for line in fin:
                        line = line.strip()
                        words = line.split()
                        # get x-centroid
                        x_centroid = (float(words[0]) + float(words[1])) * 0.5
                        x.append(x_centroid)
                        if not words:
                            break
                if ('Y-Direction Nodal Vertices, m' in line):
                    # continue reading the following lines
                    for line in fin:
                        line = line.strip()
                        words = line.split()
                        line_counter += 1
                        # get y-centroid
                        y_centroid = (float(words[0]) + float(words[2])) * 0.5
                        y.append(y_centroid)
                        if not words:
                            break
                if ('Z-Direction Nodal Vertices, m' in line):
                    # continue reading the following lines
                    for line in fin:
                        line = line.strip()
                        words = line.split()
                        # get z-centroid
                        z_centroid = (float(words[0]) + float(words[4])) * 0.5
                        z.append(z_centroid)
                        if not words:
                            break
                if ('Aqueous Saturation' in line):
                    # continue reading the following lines
                    for line in fin:
                        line = line.strip()
                        words = line.split()
                        # get saturation
                        for sat in words:
                            saturation.append(float(sat))
                        if not words:
                            break
                if ('Aqueous Pressure, pa' in line):
                    for line in fin:
                        line = line.strip()
                        words = line.split()
                        # get pressure
                        for pres in words:
                            pressure.append(float(pres))
                        if not words:
                            break
            fin.close()

    def update_dict(self, output_options):
        debug_push('QASimulatorSTOMP update_dict')
#        for value in output_options.values():
#            new_entry=[x.strip() for x in value.split(',')]
#            h5_mapping[new_entry[0]]=new_entry[1]
#            obs_mapping[new_entry[0]]=new_entry[1]
        for key, value in output_options.items():
            #            new_entry=value.strip()
            h5_mapping[key.strip()]=value.strip()
            obs_mapping[key.strip()]=value.strip()

        debug_pop()
