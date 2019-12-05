#!/bin/env python
"""
Program to manage and run QA tests.

@author: Glenn Hammond <gehammo@sandia.gov>
"""
import sys
if sys.version_info[0] < 3:
    print('\n  Python2 is not supported. Please run with python3.\n')
    sys.exit(1)

import hashlib
import os
import pprint
import re
import shutil
import subprocess
import time
import traceback
import difflib


import argparse
import datetime
import textwrap

from qa_test_log import QATestLog
from qa_test_doc import QATestDocIndex
from qa_test_manager import QATestManager
from qa_common import *
from simulator_modules.simulator_factory import locate_simulators
from regression_tests.qa_regression_test import QARegressionTest

def commandline_options():
    """
    Process the command line arguments and return them as a dict.
    """
    parser = argparse.ArgumentParser(description='Run a suite of QA tests.')

    parser.add_argument('--doc_dir', action='store',
                        help='directory for documenting test results')
                        
#    parser.add_argument('-a', '--all', action='store_true',
#                         help='run all tests.')

#    parser.add_argument('-m', '--mpiexec', nargs=1, default=None,
#                        help="path to the executable for mpiexec (mpirun, etc)"
#                        "on the current machine.")

    options = parser.parse_args()
    return options


def check_options(options):
    """
    Run some sanity checks on the commandline options.
    """
    # add error messages here, e.g.
#    if options.update and options.recursive_search is not None:
#        if not options.advanced:
#            raise RuntimeError("ERROR: can not update gold regression files "
#                                         "during a recursive search for config files.")

def scanfolder(parent_dir,extension):
    file_list = []
    # find all files with an extension under parent dir and its sub dirs
    for path, subdirs, files in os.walk(parent_dir):
        for target_file in files:
            # probably not the best way to find file extensions but it works
            # to some extent
            if target_file.endswith(extension):
                file_list.extend([os.path.join(path,target_file)])
    #return file_path strings in lists
    return file_list

def main(options):
    txtwrap = textwrap.TextWrapper(width=78, subsequent_indent=4*" ")
    
    root_dir = os.getcwd()
       
    check_options(options)
    print(options)
    

    print("Running QA tests :") 
    
    config_files = []
    if os.path.exists('config_files.txt'):
      filename = 'config_files.txt'
    else:
      filename='default_config_files.txt'
      
    for line in open(filename,'r'):
      line=line.strip()
        # rstrip to remove EOL. otherwise, errors when opening file
      if len(line) > 0 and not line.startswith('#'):
        full_path = root_dir+'/'+line.rstrip()
        config_files.append(full_path) 

    simulators_dict = locate_simulators() 


    testlog = QATestLog(root_dir)

    ##before run tests, run regression tests
    regression_test = QARegressionTest()
    regression_test.run_test(testlog)
    

    # loop through config files, cd into the appropriate directory,
    # read the appropriate config file and run the various tests.
    start = time.time()
    report = {}
    for config_file in config_files:
        os.chdir(root_dir)
        print(config_file)
        
        test_manager = QATestManager(simulators_dict)
        test_manager.process_config_file(root_dir,config_file)
        test_manager.run_tests(testlog)



    doc = QATestDocIndex(testlog)
    doc.write_index()
    debug_finalize()
    stop = time.time()
    status = 0

    return status

if __name__ == "__main__":
    cmdl_options = commandline_options()
    try:
        suite_status = main(cmdl_options)
        print("success")
        sys.exit(suite_status)
    except Exception as error:
        print(str(error))
#        if cmdl_options.backtrace:
#            traceback.print_exc()
        traceback.print_exc()
        print("failure")
        sys.exit(1)
