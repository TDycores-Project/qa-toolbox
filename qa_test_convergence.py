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
        
    def run(self,available_simulators):
        debug_push('QASolutionConvergence run')
        list_of_swap_dict=self._process_swap_options()
        self._check_simulators(available_simulators)

        i_attempt = 0
        passed = False

        cwd = os.getcwd()
        print(cwd)
        print(self.root_dir)
        print(cwd.replace(self.root_dir,''))
        doc = QATestDoc(cwd,cwd.replace(self.root_dir,''))
        doc.set_title(self.title)
        doc.set_template(self._template)

        self._values_dict = {}
        self.num_tries = 1
        self.test_pass = False
        
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
        
        for i in range(len(list_of_swap_dict)):
            run_number = self.num_tries 
            doc_run = QATestDocRun(run_number)
            
            swap_dict = list_of_swap_dict[i]
            if not swap_dict:
                print_err_msg('solution convergence specified in options file but '
                               'no swap options were set.')
            annotation = 'Run {}\n'.format(run_number)
            annotation += dict_to_string(swap_dict)
         
            solutions = {}
            isimulator = 0
            
            for simulator in self._simulators: 
             
                mapped_simulator_name = self._mapped_simulator_names[isimulator]
                if run_number == 1:
                    doc.add_simulator(mapped_simulator_name)
                 
                variable_string = ''
                for key, value in swap_dict.items(): 
                    variable_string = variable_string + ' {} = {}'.format(key,value)
                print_header('-',mapped_simulator_name+variable_string) 
                filename = self._swap(mapped_simulator_name,simulator.get_suffix(),
                                       run_number,swap_dict)
                 
                doc_run.set_input_filename(mapped_simulator_name,filename)
                if len(self.map_options) > 0:
                    simulator.update_dict(self.map_options)
                solutions[mapped_simulator_name] = \
                     simulator.run(filename,annotation)
                isimulator += 1
                
            compare_solutions =  \
            QASolutionComparison(solutions,self._output_options,
                                         self._mapped_simulator_names,
                                         self._template,run_number,
                                         doc_run)
            compare_solutions.process_opt_file()
            if self._convergence_observation:
                max_error = compare_solutions.get_observation_max_error()
            else:
                max_error = compare_solutions.get_time_slice_max_error() 
            print('Max Error = {}'.format(max_error))
            print('Attempt # = {}'.format(self.num_tries))
                  
            if max_error > self._tolerance:
                if self._verbose:
                    doc.add_run(doc_run)                    
                print('Max error above tolerance')
                self.num_tries += 1
                
            else:
                print('converged, aborting test')
                self.test_pass = True
                doc.add_run(doc_run) 
                break
                    
        if self._verbose:
            doc.write()
        elif self.test_pass:
            doc.write()

        if self.regression:
            regression_test=QARegressionTest()
            regression_test.compare_values()
            
        debug_pop()
