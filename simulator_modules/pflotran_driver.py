#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 09:02:15 2021

@author: hamm495
"""
import os
import sys

try:
    pflotran_dir = os.environ['PFLOTRAN_DIR']
except KeyError:
    print('PFLOTRAN_DIR must point to PFLOTRAN installation directory and '+
          'be defined in system environment variables.')
    sys.exit(1)
    
try:
    qa_toolbox_dir = os.environ['QA_TOOLBOX_DIR']
except KeyError:
    print('QA_TOOLBOX_DIR must point to qa-toolbox installation directory and '+
          'be defined in system environment variables.')
    sys.exit(1)
sys.path.append(qa_toolbox_dir)

if len(sys.argv) != 2:
    sys.exit('ERROR: A PFLOTRAN input file must be included on the '
             'command line.\n\nExample usage:\n\n'
             '  python3 pflotran_driver.py pflotran.in')

# qa_toolbox_dir must be appended to path before simulator_modules can be
# accessed
from simulator_modules.pflotran import QASimulatorPFLOTRAN

pflotran_input_filename = sys.argv[1]
if not os.path.isfile(pflotran_input_filename):
    sys.exit('ERROR: PFLOTRAN input file {0} does not exist.'.format(
            pflotran_input_filename))

path_and_executable = pflotran_dir+'/src/pflotran/pflotran'
pflotran_simulator = QASimulatorPFLOTRAN(path_and_executable)

annotation = ''
pflotran_simulator.run(pflotran_input_filename,annotation)

print('PFLOTRAN Driver is finished.')