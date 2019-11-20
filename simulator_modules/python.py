import sys
import shutil

from qa_debug import *
from qa_common import *
import numpy as np

from simulator_modules.simulator import QASimulator

class QASimulatorPython(QASimulator):

    def __init__(self,path):
        debug_push('QASimulatorPython init')
        super(QASimulatorPython,self).__init__(path)
        self._name = 'python'
        self._suffix = '.py'
        debug_pop()

    def run(self,filename,annotation):
        debug_push('QASimulatorPython _run')
        command = []
        command.append(self._get_full_executable_path())
        command.append(filename)
        debug_push('Running Python')
        status = self._submit_process(command,filename,annotation)
        if status != 0:
            print_err_msg('Python simulator failed. Check {}_python.stdout'.format(filename.split('.')[0]))
        solution_filename = get_h5_output_filename(filename,self._name)
        return solution_filename

def get_python_solution_filename(script_name):
    return '{}_python.h5'.format(script_name.rstrip('.py'))
