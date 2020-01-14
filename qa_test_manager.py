# -*- coding: utf-8 -*-
"""
QA test class

@author: gehammo
"""

import os
import sys

import configparser

from collections import OrderedDict
from qa_test import QATest
from qa_debug import *
from qa_common import *
from qa_test_log import QATestLog
from qa_test_convergence import QATestConvergence


class QATestManager(object):
    """
    Class to open and process a configuration file and run the tets within.
    """
    def __init__(self,simulators_dict):
        self._path = None
        self._config_filename = None
        self._tests = OrderedDict()
        self.available_simulators = simulators_dict

        
    def __str__(self):
        string = 'QA Test Manager :\n'
        string += '    configuration file : {0}\n'.format(self._config_filename)
        string += '    tests : \n'
        for key, value in self._tests.items():
            string += str(value)
        return string
        
    def process_config_file(self,root_dir,config_file):
        debug_push('QATestManager process_config_file')
        if config_file is None:
            raise RuntimeError("Error, must provide a config filename")
        if not os.path.isfile(config_file):
            print('.cfg file '+config_file+' not found in '
                  'QATestManager.process_config_file.')
        self._path, filename = os.path.split(config_file)
        os.chdir(self._path)
        self._config_filename = filename
        config = configparser.ConfigParser()
        debug_push('QATestManager process_config_file parse')
        config.read(self._config_filename)
        debug_pop() 
        
        sections = config.sections()
        for section in sections:
            name = section
            solution_convergence = self.check_options(name)

            if solution_convergence:
                test = QATestConvergence(name,root_dir,list_to_dict(config.items(section)))
            else:
                test = QATest(name,root_dir,list_to_dict(config.items(section)))
            self._tests[name] = test
        debug_pop()
            
    def run_tests(self,testlog):
        debug_push('QATestManager run_tests')
        for key, test_case in self._tests.items():
            test_case.run(self.available_simulators)
            testlog.log_success(self._path,test_case.title)
        debug_pop()
        
    def check_options(self,name):
        debug_push('QATestManager check_options')
        filename = name +'.opt'
        if not os.path.isfile(filename):
            print_err_msg('Options file name {} does not exist in folder {}'.format(filename,os.getcwd()))
        config = configparser.ConfigParser()
        config.read(filename)
        sections = config.sections()
        
        qa_solution_convergence = False
        for section in sections:
            if section == 'solution_convergence':
                qa_solution_convergence = True
                
        debug_pop()   

        return qa_solution_convergence
        
              
