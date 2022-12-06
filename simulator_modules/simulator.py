import sys
import time
import subprocess

from h5py import *
import numpy as np

from qa_debug import *
from qa_common import *

eps = 1e-6

class QASimulator:

    def __init__(self,path):
        debug_push('QASimulator init')
        self._name = ''
        self._suffix = ''
        self._path = path
        self._timeout = 3000000000000.
        debug_pop()

    def get_name(self):
        return(self._name)

    def set_name(self,name):
        self._name = name

    def get_suffix(self):
        return(self._suffix)

    def _get_full_executable_path(self):
        return self._path

    def _create_stdout_filename(self,filename):
        root = filename.split('.')[0]
        return root+'_'+self._name+'.stdout'

    def _add_annotation(self,f_stdout,annotation):
        if annotation:
            f_stdout.write(annotation)
        
    def run(self,filename,annotation=None,np=1):
        debug_push('QASimulator _run')
        print('QASimulator.run must be extended') 
        raise
        debug_pop()
        return ''

    def _submit_process(self,command,filename,annotation):
        debug_push('QASimulator _submit_process')
        f_stdout = open(self._create_stdout_filename(filename), 'w')

        self._add_annotation(f_stdout,annotation)

        print('QASimulator submitting: "{}"'.format(' '.join(command)))
        start = time.time()
        proc = subprocess.Popen(command,
                                shell=False,
                                stdout=f_stdout,
                                stderr=subprocess.STDOUT)
        while proc.poll() is None:
            time.sleep(0.1)
            if time.time() - start > self._timeout:
                proc.kill()
                time.sleep(0.1)
  #              message = self._txtwrap.fill(
  #                        "ERROR: job '{0}' has exceeded timeout limit of "
  #                        "{1} seconds.".format(filename, self._timeout))
  #              print(''.join(['\n', message, '\n']))#, file=testlog)
        finish = time.time()
        print("    # {0} : {1} : run time : {2:.2f} seconds".\
                    format(self._name , filename, finish - start))
        simulator_status = abs(proc.returncode)
        f_stdout.close()
        debug_pop()
        return simulator_status

    def get_solution(self,filename,time,variable):
        debug_push('QASimulator get_solution')
        print('QASimulator.get_solution must be extended') 
        raise
        debug_pop()

