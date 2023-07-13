import sys
import re
import os

import configparser
from simulator_modules.simulator_factory import locate_simulators

from simulator_modules.crunchflow import QASimulatorCrunchFlow
from simulator_modules.pflotran import QASimulatorPFLOTRAN
from simulator_modules.python import QASimulatorPython
from simulator_modules.tough2 import QASimulatorTOUGH2
from simulator_modules.tough3 import QASimulatorTOUGH3
from simulator_modules.tdycore import QASimulatorTDycore

#Define directories and files
toolbox_dir = os.getcwd()
main_dir = sys.argv[1] #input argument for where running tests
config_dir = sys.argv[2]

sim_file = 'simulators.sim'

if not os.path.exists(config_dir):
    config_dir = 'default_config_files.txt'
    
if not os.path.exists(sim_file):
    sim_file = 'default_simulators.sim'


#Patterns to match
patterns = ['.*\.stat(?!\.gold)','.*_doc\.rst','^include_.*\.rst','^intro_.*\.rst',
                 'successful_tests.log','successful_regression_tests.log',
                 '.*\.tec','.*\.stdout','.*\.out','.*\_run\d.*\.png','.*\.in']


#######################
#process simulators.sim
#######################

sim_dict = locate_simulators(sim_file,None)
for simulator in sim_dict.values():
    patterns = patterns + simulator.output_file_patterns()

#########################
#process config_files.txt
#########################


test_paths=[]

for line in open(config_dir):
    line=line.strip()
    if len(line) > 0 and not line.startswith('#'):
        if line.startswith('/'):
            full_path = line.rstrip()
        else:
            full_path = toolbox_dir+'/'+line.rstrip()
        test_paths.append(full_path) 

toolbox_expression = '^'+ toolbox_dir + '(?!/\.\.).'   
main_expression = '^'+ main_dir + '(?!/\.\.).'
config_expression = '^'+ config_dir + '(?!/\.\.).'         
for test in test_paths:   
    if not (re.match(toolbox_expression,test) or not re.match(main_expression,test) or not re.match(config_expression,test)):
        path, filename = os.path.split(test)
        for pattern in patterns:
            for file in filter(lambda x: re.match(pattern,x),os.listdir(path)):
                try:
                    os.remove(os.path.join(path,file))
                except:
                    print('{}/{} not found'.format(path,file))
        


#############################################
#delete files in qatoolbox and main directory
#############################################
directories = [toolbox_dir]
if main_dir != toolbox_dir:
    directories.append(main_dir)

if config_dir != main_dir or config_dir != toolbox_dir:
    directories.append(main_dir)
    
                
for i in range(len(directories)):   
    for root, dirs, files in os.walk(directories[i]):
        for pattern in patterns:
            for filename in filter(lambda x: re.match(pattern,x),files):
                try:
                    os.remove(os.path.join(root,filename))
                except:
                    print('{}/{} not found'.format(root,filename))

                 
