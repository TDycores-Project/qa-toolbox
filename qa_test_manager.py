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
from qa_regression_test import QARegressionTest

class QATestManager(object):
    """
    Class to open and process a configuration file and run the tets within.
    """
    def __init__(self,simulators_dict):
        self._path = None
        self._config_filename = None
        self._tests = OrderedDict()
        self.available_simulators = simulators_dict
        self._regression_dict = OrderedDict()
        
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
        debug_pop() #QATestManager process_config_file parse
        
        sections = config.sections()
        for section in sections:
            name = section
            section_dict = list_to_dict(config.items(section))
            test = QATest(name,root_dir,section_dict)
            self._tests[name] = test
            self._regression_dict[name]=qa_lookup(section_dict,'regression_test',False)
        debug_pop() #QATestManager process_config_file
            
    def run_tests(self,testlog):
        debug_push('QATestManager run_tests')
        for key, test_case in self._tests.items():
            test_case.run(self.available_simulators)
            testlog.log_success(self._path,test_case.name)
            if self._regression_dict[key] == True:
                regression_test=QARegressionTest()
                regression_test.compare_values()
        debug_pop()
