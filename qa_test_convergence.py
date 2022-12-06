"""
Created on Wed Jan  8 14:10:00 2020

@author: rleone
"""

import sys
import re
import os
import time
import subprocess
import textwrap
import csv
import shutil

import configparser

from h5py import *
import numpy as np

from qa_swapper import Swapper
from qa_debug import *
from qa_common import *
from qa_solution_comparison import *
from qa_test_doc import *
from qa_regression_test import QARegressionTest
from qa_test import QATest

class QATestConvergence(QATest):
    def __init__(self,name,root_dir,section_dict=None):
        super().__init__(name,root_dir,section_dict)
        
        self.num_tries = 1
        self.test_pass = False
        
    def process_convergence_options(self):
        tolerance = qa_lookup(self._convergence_options, 'tolerance','fail_on_missing_keyword')

        self._verbose = qa_lookup(self._convergence_options, 'verbose','True')
        self._convergence_observation = qa_lookup(self._convergence_options, 'observation','False')
         
        self._tolerance = string_to_number(tolerance)
        
        plot_error = qa_lookup(self._output_options,'plot_error',False)
        print_error = qa_lookup(self._output_options,'print_error',False)
        
        if not plot_error:
            self._output_options['plot_error'] = True
        if not print_error:
            self._output_options['print_error'] = True
        
    def run(self,list_of_swap_dict):
        debug_push('QASolutionConvergence run')
        
        self.process_convergence_options()

        for i in range(len(list_of_swap_dict)):
            doc_run = self.run_single(i,list_of_swap_dict)
        
            if self._convergence_observation:
                max_error = self.compare_solutions.get_observation_max_error()
            else:
                max_error = self.compare_solutions.get_time_slice_max_error() 
            print('Max Error = {}'.format(max_error))
            print('Attempt # = {}'.format(self.num_tries))
            #add in relative error under curve, multiple simulators all must pass   
            if max_error > self._tolerance:
                if self._verbose:
                    self.doc.add_run(doc_run)                    
                print('Max error above tolerance')
                self.num_tries += 1
                
            else:
                print('converged, aborting test')
                self.test_pass = True
                self.doc.add_run(doc_run) 
                break
                    
        if self._verbose:
            self.doc.write()
        elif self.test_pass:
            self.doc.write() ##add in test pass statistics....

            
        debug_pop()
