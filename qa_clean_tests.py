import sys
import re
import os

import configparser

#Define directories and files
toolbox_dir = os.getcwd()
main_dir = sys.argv[1] #input argument for where running tests


sim_file = 'simulators.sim'
config_file = 'config_files.txt'

if not os.path.exists(config_file):
    config_file = 'default_config_files.txt'
    
if not os.path.exists(sim_file):
    sim_file = 'default_simulators.sim'


#Patterns to match
patterns = ['.*\.stat(?!\.gold)','.*_doc\.rst','^include_.*\.rst','^intro_.*\.rst',
                 'successful_tests.log','successful_regression_tests.log',
                 '.*\.tec','.*\.stdout','.*\.out','.*\_run\d.*\.png','.*\.in']
python_patterns = ['.*_run\d*\.py','.*_run\d*_python\.h5']
pflotran_patterns = ['.*_run\d*_pflotran\.h5','.*_run\d*_pft\.h5']
tough_patterns = ['FOFT*','OUTPUT*','GENER','SAVE','TABLE','MESHA',
                  'MESHB','MESHB','INCON','.*_run\d*_tough3\.h5']
tdycore_patterns = ['.*_run\d*_tdycore\.h5']
crunch_patterns = ['.*_run\d*_crunchflow\.h5']



#######################
#process simulators.sim
#######################

config = configparser.ConfigParser()
config.read(sim_file)
simulators = config.items('simulators')
for simulator, path in simulators:
    if simulator == 'pflotran':
        patterns = patterns + pflotran_patterns
    if simulator == 'python':
        patterns = patterns + python_patterns
    if simulator == 'tough3':
        patterns = patterns + tough_patterns
    if simulator == 'crunchflow':
        patterns = patterns + crunch_patterns
    if simulator == 'tdycore':
        patterns = patterns + tdycore_patterns



#########################
#process config_files.txt
#########################


test_paths=[]

for line in open(config_file):
    line=line.strip()
    if len(line) > 0 and not line.startswith('#'):
        if line.startswith('/'):
            full_path = line.rstrip()
        else:
            full_path = toolbox_dir+'/'+line.rstrip()
        test_paths.append(full_path) 

dir_expression = '^'+ toolbox_dir + '(?!/\.\.).'            
for test in test_paths:   
    if not re.match(dir_expression,test):
        path, filename = os.path.split(test)
        for root, dirs, files in os.walk(path):
            for pattern in patterns:
                for filename in filter(lambda x: re.match(pattern,x),files):
                    try:
                        os.remove(os.path.join(root,filename))
                    except:
                        print('{}/{} not found'.format(root,filename))


#############################################
#delete files in qatoolbox and main directory
#############################################
                    
                    
for root, dirs, files in os.walk(toolbox_dir):
    for pattern in patterns:
        for filename in filter(lambda x: re.match(pattern,x),files):
            try:
                os.remove(os.path.join(root,filename))
            except:
                print('{}/{} not found'.format(root,filename))
            
            
            
if main_dir != toolbox_dir:
    for root, dirs, files in os.walk(main_dir):
        for pattern in patterns:
            for filename in filter(lambda x: re.match(pattern,x),files):
                try:
                    os.remove(os.path.join(root,filename))
                except:
                    print('{}/{} not found'.format(root,filename))