import sys

from qa_debug import *

from simulator_modules.simulator import QASimulator

class QASimulatorTOUGH2(QASimulator):

    def __init__(self,path):
        debug_push('QASimulatorTOUGH2 init')
        super(QASimulatorTOUGH2,self).__init__(path)
        self._name = 'tough2'
        self._suffix = '.in'
        debug_pop()

    def run(self,filename,annotation):
        debug_push('QASimulatorTOUGH2 _run')
        command = []
        command.append(self._get_full_executable_path())
        command.append(filename+'.in')
        command.append(filename+'.out')
        debug_push('Running TOUGH2')
        self._submit_process(command,filename,annotation)
        debug_pop()        
        debug_pop()        

    def read_solution(self,filename,dataset_strings):
        debug_push('QASimulatorTOUGH2 read_solution')
        # I suggest only test 1D problems with TOUGH3
        # it is very difficult to process csv output for multiple dimensions.
        # we may have to implement such that TOUGH3 outputs TECPLOT data
        # and process TECPLOT format instead of csv format.
        # - Heeho Park
        tough_dict = {}
        temp_key = []
        time = ''
        with open('OUTPUT_ELEME.csv','r') as f:
            row = csv.reader(f)
            for line in row:
                if 'ELEM' in line[0].strip():
                    for key in line:
                        temp_key.append(key.strip())
                elif 'TIME' in line[0].strip():
                    time = line[0].split()
                    time = time[2].strip()
                    tough_dict[time] = {}
                    for key in temp_key:
                        tough_dict[time][key] = []
                elif '' == line[0].strip():
                    continue
                else:
                    for i in range(len(line)):
                        if i == 0:
                            tough_dict[time][temp_key[i]].append(
                                                          line[i].strip())
                        else:
                            tough_dict[time][temp_key[i]].append(
                                                          float(line[i]))

        for key1 in tough_dict.keys():
            for key2 in tough_dict[key1].keys():
                tough_dict[key1][key2] = np.array(tough_dict[key1][key2])

        # only suited for 1D comparisons (last 3 values are dummy and bc's)
        soln = np.zeros([len(dataset_strings),  # time
                         len(tough_dict[key1][key2][:-3]),  # x-dimension
                         1, 1])  # y- and z-dimensions
        isoln=0
        for string in dataset_strings:
            time = string.split('/')[0]
            variable = string.split('/')[1]
            # assuming last 3 values are dummy, boundary condition 1 and 2
            soln[isoln,:,0,0] = tough_dict[time][variable][:-3]
            isoln += 1

        debug_pop()
        return soln
