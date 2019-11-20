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
import matplotlib.pyplot as plt

from qa_swapper import Swapper
from qa_debug import *
from qa_common import *
from qa_solution_comparison import *

class QATest(object):
    """
    Class to collect data about a test, run the test, and plot results
    """
    _wall_time_re = re.compile(r"Time \(seconds\)")

    def __init__(self,name,section_dict=None):
        debug_push('QATest init')
        print_header('*',name)
        self._txtwrap = textwrap.TextWrapper(width=78, subsequent_indent=4*" ")
        self._timeout = 300.
        self._name = name
        self._section_dict = section_dict
        self._simulators = []
        self._mapped_simulator_names = []
        self._max_attempts = 1  # 1 is default
        self._swap_method = list  # 1 is max_iter, 2 is list_size
        self._swap_available = False
        self._swap_options = {}
        self._output_options = {}
        self.map_options={}
        self.tough_options={}
        self._process_opt_file()
        self.swap_dict = {}
        

        debug_pop()

    def __str__(self):
        string = '    QA Test : '+self._name+'\n'
        string += dict_to_string(self._options)+'\n'
        return string

    def _process_opt_file(self):
        debug_push('QATest _process_opt_file')
        filename = self._name+'.opt'
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
        self.tough_options = \
            self._section_from_opt_file(config,'tough_options')
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

    def _get_template(self):
        return self._section_dict['template']

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
                         % self._name)
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
                   % self._name)

        for i in range(self._max_attempts):
            dict_to_append = {}

            for key, value in number_dict.items():
                dict_to_append[key] = value[i]
 
            list_of_swap_dict.append(dict_to_append)
        return list_of_swap_dict
        debug_pop()

    def _check_simulators(self,available_simulators):
        debug_push('QATest check simulators')
        print (self._section_dict)
        simulator_list = self._section_dict['simulators'].split(',')
        num_simulators = 0

        self._simulators = []
        self._mapped_simulator_names = []
        debug_simulator_list = []
        for simulator in simulator_list:
            s = re.split(r's*:s*',simulator.strip())
            simulator_name = s[0]
            if len(s) > 1:
                mapped_simulator_name = s[1]
            else:
                mapped_simulator_name = s[0]
            if simulator_name not in available_simulators:
                print_err_msg('Simulator {} requested in .cfg file, section [{}] not found \
                              among available simulators.'.format(simulator_name,self._name))

            else:
                num_simulators += 1
                s = available_simulators[simulator_name]
                self._simulators.append(s)
                self._mapped_simulator_names.append(mapped_simulator_name)
                debug_simulator_list.append(mapped_simulator_name)
        if num_simulators < 2:
            print_err_msg('Insufficient number of available simulators in '
                            '.cfg file, section [{}].'.format(self._name))
        print('simulators: '+list_to_string(debug_simulator_list))
        debug_pop()

    def run(self,available_simulators):
        debug_push('QATest run')
        list_of_swap_dict=self._process_swap_options()
        self._check_simulators(available_simulators)

        i_attempt = 0
        passed = False
#        list_of_swap_dict = self._list_of_swap_dict 

        for i in range(len(list_of_swap_dict)):
            run_number = i+1
  
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
                mapped_name = self._mapped_simulator_names[isimulator]
                print_header('-',mapped_name)
                filename = self._swap(mapped_name,simulator.get_suffix(),
                                      run_number,swap_dict)

                if len(self.map_options) > 0:
                    simulator.update_dict(self.map_options)
                if len(self.tough_options) > 0 and mapped_name == 'tough3':
                    simulator.process_tough_options(self.tough_options,self._output_options)
                solutions[mapped_name] = \
                    simulator.run(filename,annotation)
                isimulator += 1
            #self._compare_solutions(solutions)
            template = self._get_template()
            ##pass in template and run number
            compare_solutions=QASolutionComparison(solutions,self._output_options,self._mapped_simulator_names,template,run_number)
            compare_solutions.process_opt_file()
        debug_pop()


    def _swap(self,simulator_mapped_name,simulator_suffix,run_number,
              swap_dict=None):
        debug_push('QATest _swap')
        template = self._get_template()
        in_filename = template+'.'+simulator_mapped_name
        #run_number_string = ''
        #if run_number > 0:
        run_number_string = '_run{}'.format(run_number)
        out_filename = template+'_'+simulator_mapped_name+ \
                       run_number_string+simulator_suffix
        if os.path.isfile(in_filename):
            print(in_filename+' found')
            swapper = Swapper()
            if swap_dict:
                print(dict_to_string(swap_dict))
            else:
                print('swap_dict empty')
            swapper.swap_new(in_filename,out_filename,
                             swap_dict)
#        elif os.path.isfile(in_filename):
#            shutil.copy(in_filename, out_filename)
        else:
            print_err_msg('{} defined in .cfg file, section [{}] not found in {}'.format(in_filename, self._name, os.getcwd()))

        debug_pop()
        return out_filename

   
