# -*- coding: utf-8 -*-
"""
QA test class

@author: gehammo
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


class QATest(object):
    """
    Class to collect data about a test, run the test, and plot results
    """
    _wall_time_re = re.compile(r"Time \(seconds\)")

    def __init__(self,name,root_dir,section_dict=None):
        debug_push('QATest init')
        print_header('*',name)
        self._txtwrap = textwrap.TextWrapper(width=78, subsequent_indent=4*" ")
        self._timeout = 300.
        self._section_dict = section_dict
        self.name = name
        self.root_dir = root_dir
        try:
            self.title = self._section_dict['title']
        except:
            self.title = self.name
        self._simulators = []
        self._mapped_simulator_names = []
        self._max_attempts = 1  # 1 is default
        self._swap_method = list  # 1 is max_iter, 2 is list_size
        self._swap_available = False
        self._swap_options = {}
        self._output_options = {}
        self.map_options={}
        self._process_opt_file()
        self.swap_dict = {}
        self._template = self._section_dict['template']
        self.regression=qa_lookup(self._section_dict,'regression_test',False)
        debug_pop()

    def __str__(self):
        string = '    QA Test : '+self.name+'\n'
        string += dict_to_string(self._options)+'\n'
        return string

    def _process_opt_file(self):
        debug_push('QATest _process_opt_file')
        filename = self.name+'.opt'
        if not os.path.isfile(filename):
            print_err_msg('Options file name {} does not exist in folder {}'.format(filename,os.getcwd()))

        config = configparser.ConfigParser()
        debug_push('QATest _process_opt_file parse')
        config_mapping=config
        config_mapping.optionxform = str
        config_mapping.read([filename])
        config.read([filename])
        if debug_verbose():
            print('sections of opt file')
            sections = config.sections()
            for section in sections:
                print('  {}'.format(section))
        debug_pop()
        
        self._swap_options = \
            self._section_from_opt_file(config,'swap_options')
        self._output_options = \
            self._section_from_opt_file(config,'output_options')
        self.map_options = \
            self._section_from_opt_file(config_mapping,'mapping_options')
        self._convergence_options = \
            self._section_from_opt_file(config,'solution_convergence')
        if len(self._output_options) == 0:
            print_err_msg('No output_options defined in options file {} in \
                           folder'.format(filename,os.getcwd()))            
        debug_pop()
        
    def _section_from_opt_file(self,config,key):
        xx_options = {}
        try:
            xx_options = list_to_dict(config.items(key))
        except Exception as error:
            pass
        return xx_options

    def _process_swap_options(self):   
        debug_push('QATest _process_swap_options')
        number_dict = {}
        list_of_swap_dict = []

        if self._swap_options:

           if 'method' in self._swap_options:
               self._swap_method = self._swap_options['method']
               self._swap_options.pop('method', None)
           else:
               self._swap_method = 'list'
        
           if self._swap_method == 'list':
               item_len = len(list(self._swap_options.values())[0].split(','))
               self._max_attempts = item_len

               for key,value in self._swap_options.items():
                   if len(value.split(',')) != item_len:
                       print_err_msg('ERROR %s should have the same length as all swap variables' % key)
                   number_dict[key] = []
                   value = value.split(',')
           
           
                   for i in range(self._max_attempts):
                        number_dict[key].append(string_to_number(value[i]))
           
           elif self._swap_method == 'iterative':
               if 'max_attempts' in self._swap_options:
                   self._max_attempts = int(self._swap_options['max_attempts'])
                   self._swap_options.pop('max_attempts', None)
               else:
                   print_err_msg('ERROR: max_attempts not defined in %s.opt file' 
                         % self.name)
               for key, value in self._swap_options.items():
                   if len(value.split(',')) != 2:
                       print_err_msg('ERROR: %s should have first value and '
                           'increment defined. e.g. nx = 12,2' % key)
                   number_dict[key] = []
                   value = value.split(',')  
               
                   first_value = string_to_number(value[0])
                   multiplier = string_to_number(value[1])
                   for i in range(self._max_attempts):
                       number_dict[key].append(first_value*(multiplier**(i)))
           else: 
               print_err_msg('Error: swap method unknown or undefined in %s.opt file'
                   % self.name)

        for i in range(self._max_attempts):
            dict_to_append = {}

            for key, value in number_dict.items():
                dict_to_append[key] = value[i]
 
            list_of_swap_dict.append(dict_to_append)
        debug_pop()
        return list_of_swap_dict

    def _check_simulators(self,available_simulators):
        debug_push('QATest check simulators')
        if debug_verbose():
            print (self._section_dict)
        simulator_list = self._section_dict['simulators'].split(',')
        num_simulators = 0

        self._simulators = []
        self._mapped_simulator_names = []
        debug_simulator_list = []
        for simulator in simulator_list:
            s = re.split(r'\s*:\s*',simulator.strip())
            simulator_name = s[0]
            if len(s) > 1:
                mapped_simulator_name = s[1]
            else:
                mapped_simulator_name = s[0]
            if simulator_name not in available_simulators:
                print_err_msg('Simulator {} requested in .cfg file, section [{}] not found \
                              among available simulators.'.format(simulator_name,self.name))

            else:
                num_simulators += 1
                s = available_simulators[simulator_name]
                self._simulators.append(s)
                self._mapped_simulator_names.append(mapped_simulator_name)
                debug_simulator_list.append(mapped_simulator_name)
        if num_simulators < 2:
            print_err_msg('Insufficient number of available simulators in '
                            '.cfg file, section [{}].'.format(self.name))
        print('simulators: '+list_to_string(debug_simulator_list))
        debug_pop()

    def initialize_run(self,available_simulators):
        debug_push('QATest initialize_run')
        list_of_swap_dict=self._process_swap_options()
        self._check_simulators(available_simulators)

        cwd = os.getcwd()
#        print(cwd)
#        print(self.root_dir)
#        print(cwd.replace(self.root_dir,''))

        self.doc = QATestDoc(cwd,cwd.replace(self.root_dir,''))
        self.doc.set_title(self.title)
        self.doc.set_template(self._template)
        
        debug_pop()
        
        return list_of_swap_dict
        
    def run(self,list_of_swap_dict):
        debug_push('QATest run')

        for i in range(len(list_of_swap_dict)):  
            doc_run = self.run_single(i,list_of_swap_dict)
            self.doc.add_run(doc_run)

        #compare gold file results for regression tests
        if self.regression == True:
                regression_test = QARegressionTest()
                regression_test.compare_values()
        self.doc.write()
        debug_pop()
        
    def run_single(self,i,list_of_swap_dict):
        debug_push('QATest run_single')
        run_number = i+1
        doc_run = QATestDocRun(run_number)
  
        swap_dict = None
        if len(list_of_swap_dict) > 0:
            #if len(list_of_swap_dict) > 1:
            #    run_number += 1
            swap_dict = list_of_swap_dict[i]
        annotation = None
        if swap_dict:
            annotation = 'Run {}\n'.format(run_number)
            annotation += dict_to_string(swap_dict)
        solutions = {}
        isimulator = 0
        
        for simulator in self._simulators:
            mapped_simulator_name = self._mapped_simulator_names[isimulator]
            if run_number == 1:
                 self.doc.add_simulator(mapped_simulator_name)
            print_header('-',mapped_simulator_name)
            filename = self._swap(mapped_simulator_name,simulator.get_suffix(),
                                  run_number,swap_dict)
            doc_run.set_input_filename(mapped_simulator_name,filename)
            if len(self.map_options) > 0:
                simulator.update_dict(self.map_options)
            solutions[mapped_simulator_name] = \
                simulator.run(filename,annotation)
            isimulator += 1
        #self._compare_solutions(solutions)
        ##pass in template and run number
        compare_solutions = \
            QASolutionComparison(solutions,self._output_options,
                                 self._mapped_simulator_names,
                                 self._template,run_number,
                                 doc_run)
        compare_solutions.process_opt_file()
        self.compare_solutions = compare_solutions
        
        debug_pop()
        
        return doc_run
    

    def _swap(self,simulator_mapped_name,simulator_suffix,run_number,
              swap_dict=None):
        debug_push('QATest _swap')
        in_filename = self._template+'.'+simulator_mapped_name
        run_number_string = '_run{}'.format(run_number)
        out_filename = self._template+'_'+simulator_mapped_name+ \
                       run_number_string+simulator_suffix
        if os.path.isfile(in_filename):
            if debug_verbose():
                print(in_filename+' found')
            swapper = Swapper()
            if debug_verbose():
                if swap_dict:
                    print(dict_to_string(swap_dict))
                else:
                    print('swap_dict empty')
            swapper.swap_new(in_filename,out_filename,
                             swap_dict)
        else:
            print_err_msg('{} defined in .cfg file, section [{}] not found in {}'.format(in_filename, self.name, os.getcwd()))

        debug_pop()
        return out_filename
    
