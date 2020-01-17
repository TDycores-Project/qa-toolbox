#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 17:34:00 2020

@author: rleone
"""

import sys
import os
import re
from filecmp import *

import numpy as np

from qa_common import *
from qa_debug import *
from qa_test_log import QATestLog
from qa_test_doc import *

#root_dir = '../regression_tests/documentation_test'
#doc_dir = '/regression_tests/documentation_test/docs'
run_number = 1
converted_time = 0.0
plot_time_units = "y"
variable = 'variable'
png_filename = 'dummy.png'
stat_filename = 'dummy.stat'

class QADocumentationRegressionTest(object):
    def __init__(self,root_dir):
        full_path = root_dir + '/regression_tests/documentation_test'
        doc = QATestDoc(full_path,full_path.replace(root_dir,''))
        
        os.chdir(full_path)
        
        doc.set_title('title')
        doc.set_template('template')
        doc.add_simulator('simulator1')
        doc.add_simulator('simulator2')
        
        doc_run = QATestDocRun(run_number)
        
        doc_slice = QATestDocTimeSlice(converted_time,plot_time_units)
        
        doc_var = QATestDocVariable(variable)
        doc_var.add_solution_png(png_filename)
        doc_var.add_error_png(png_filename)
        
        doc_var.set_error_stat(stat_filename)
        
        doc_slice.add_variable(doc_var)
        doc_run.add_time_slice(doc_slice)
        
        error = DocumentationError()
        
        doc_run.add_max_absolute_error(variable, error)
        doc_run.add_max_relative_error(variable,error)
        doc_run.add_max_average_absolute_error(variable,error)
        doc_run.add_max_average_relative_error(variable,error)
        
        doc.add_run(doc_run)
        doc.write()
        
        self.root_dir = root_dir
        
    def write_index_file(self,doc_dir):
        testlog = QATestLog(self.root_dir)  ###
        testlog.log_success(self.root_dir+'/regression_tests/documentation_test','title')
#        doc_dir = self.root_dir + '/regression_tests/documentation_test/docs'
        doc = QATestDocIndex(testlog,doc_dir)
        doc.write_index()
        
        
    def compare_files(self):
        rst_files = ['title.rst','docs/index.rst','docs/intro_documentation_test.rst','docs/include_toctree_documentation_test_title.rst']
        
        for i in range(len(rst_files)):
            match = cmp(rst_files[i],rst_files[i]+'.gold')
            if not match:
                print_err_msg('no match with {}'.format(rst_files[i]))
                
        print('match')
        
#        cmp('title.rst','title.rst.gold')
#        cmp('docs/index.rst','docs/index.rst.gold')
#        cmp('docs/intro_documentation_test.rst','docs/intro_documentation_test.rst.gold')
#        cmp('docs/include_toctree_documentation_test_title.rst','docs/iinclude_toctree_documentation_test_title.rst.gold')
        
        
class DocumentationError(object):
    def __init__(self):
        self.maximum_absolute_error_all_times = '3 Pa'
        self.maximum_absolute_error_time = '0.0 y'
        self.maximum_absolute_error_location_all_times = '5 m'
        self.maximum_absolute_error_index = 0
        
        self.maximum_relative_error_all_times = '4 %'
        self.maximum_relative_error_time = '0.0 y'
        self.maximum_relative_error_location_all_times = '6 m'
        self.maximum_relative_error_index = 0
        
        self.maximum_average_absolute_error = '1 Pa'
        self.maximum_average_absolute_error_time = '0.0 y'
        self.maximum_average_absolute_error_index = 0
        
        self.maximum_average_relative_error = '2 %'
        self.maximum_average_relative_error_time = '0.0 y'
        self.maximum_average_relative_error_index = 0
    