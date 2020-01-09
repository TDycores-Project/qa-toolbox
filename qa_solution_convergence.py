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

class QASolutionConvergence(QATest):
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
        self.num_tries = 0
        self.test_pass = False
        
#        max_tries = qa_lookup(self._convergence_options, 'max_tries','fail_on_missing_keyword')
        tolerance = qa_lookup(self._convergence_options, 'tolerance','fail_on_missing_keyword')
#        increment_value = qa_lookup(self._convergence_options, 'increment_value','fail_on_missing_keyword')
#         self._variable = qa_lookup(self.convergence_dict, 'variable','fail_on_missing_keyword')
        self._verbose = qa_lookup(self._convergence_options, 'verbose','True')
        self._convergence_observation = qa_lookup(self._convergence_options, 'observation','False')
         
        self._convergence_options.pop('max_tries',None)
        self._convergence_options.pop('tolerance',None)
        self._convergence_options.pop('increment_value',None)
        self._convergence_options.pop('verbose',None)
        self._convergence_options.pop('observation',None)
         
#        self._max_tries = string_to_number(max_tries)
        self._tolerance = string_to_number(tolerance)
#        self._increment_value = string_to_number(increment_value)
         
         #going to need to user error proof this
#        for key,value in self._convergence_options.items():
#            self._values_dict[key] = string_to_number(value)
        
        plot_error = qa_lookup(self._output_options,'plot_error',False)
        print_error = qa_lookup(self._output_options,'print_error',False)
        
        if not plot_error:
            self._output_options['plot_error'] = True
        if not print_error:
            self._output_options['print_error'] = True
        
        for i in range(len(list_of_swap_dict)):
         # while self.test_pass == False and self.num_tries < self._max_tries:
            run_number = self.num_tries + 1
            doc_run = QATestDocRun(run_number)
            
            swap_dict = list_of_swap_dict[i]
            
            annotation = 'Run {}\n'.format(run_number)
            annotation += dict_to_string(swap_dict)
         
            solutions = {}
            isimulator = 0
            
            for simulator in self._simulators: 
             
                mapped_simulator_name = self._mapped_simulator_names[isimulator]
                if run_number == 1:
                    doc.add_simulator(mapped_simulator_name)
                 
                variable_string = ''
#addbackinlater                for key, value in self._values_dict.items():
#                    variable_string = variable_string + ' {} = {}'.format(key,value)
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
              max_error = compare_solutions.get_time_slice_max_error() ##name better?
            print('Max Error = {}'.format(max_error))
            print('Attempt # = {}'.format(self.num_tries))
                  
            if max_error > self._tolerance:
#                for key,value in self._values_dict.items():
#                    self._values_dict[key] = value*self._increment_value
#                self.num_tries = self.num_tries + 1
                if self._verbose == True:
                    doc.add_run(doc_run)
                    
#                if self.num_tries >= self._max_tries:
#                    print('Maximum number of tries reached, aborting test')
#                else:
                print('continuing tests')
            else:
                print('converged, aborting test')
                self.test_pass = True
                doc.add_run(doc_run) 
                break
                    
        if self._verbose == True:
            doc.write()
        elif self.test_pass == True:
            doc.write()

#            if self.regression == True:
#                regression_test=QARegressionTest()
#                regression_test.compare_values()
            
        debug_pop()
