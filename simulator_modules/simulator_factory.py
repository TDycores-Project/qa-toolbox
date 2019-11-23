import sys
import shutil
import os
import configparser

from qa_common import *
from qa_debug import *

from simulator_modules.crunchflow import QASimulatorCrunchFlow
from simulator_modules.pflotran import QASimulatorPFLOTRAN
from simulator_modules.python import QASimulatorPython
from simulator_modules.tough2 import QASimulatorTOUGH2
from simulator_modules.tough3 import QASimulatorTOUGH3
from simulator_modules.tdycore import QASimulatorTDycore

from simulator_modules.dataset import QASimulatorDatasetSin
from simulator_modules.dataset import QASimulatorDatasetCos

def locate_simulators():
    debug_push('simulator_factory.locate_simulators')
    if os.path.exists('simulators.sim'):
      sim_file = 'simulators.sim'
    else:
      sim_file='default_simulators.sim'
    config = configparser.ConfigParser()
    config.read(sim_file)
    simulators = config.items('simulators')
    simulator_dict = {}
    to_be_removed = []
    for simulator, path in simulators:
        if debug_verbose():
            print('Searching for "{}" mapped to "{}".'.format(path,simulator))
        if not os.path.isfile(path):
            if debug_verbose():
                print('  "{}" not found among simulator paths. Checking '
                      'in machine PATH.'.format(path))
            if shutil.which(path):
                if debug_verbose():
                    print('  "{}" found in PATH...'.format(path))
                simulator_dict[simulator] = create_simulator(simulator,path)
            else:
                if debug_verbose():
                    print('  "{}" not found in path either. Removing it '
                          'from list of available simulators.'.format(path))
                to_be_removed.append(path)
        else:
            if debug_verbose():
                print('  {} found...'.format(path))
            simulator_dict[simulator] = create_simulator(simulator,path)
    debug_pop()
    return simulator_dict

def create_simulator(simulator_name,path):
    debug_push('simulator_factory.create_simulator')
    simulator = ''
    if simulator_name == 'crunchflow':
         simulator = QASimulatorCrunchFlow(path)
    elif simulator_name == 'pflotran':
         simulator = QASimulatorPFLOTRAN(path)
    elif simulator_name == 'python':
         simulator = QASimulatorPython(path)
    elif simulator_name == 'tough2':
         simulator = QASimulatorTOUGH2(path)
    elif simulator_name == 'tough3':
         simulator = QASimulatorTOUGH3(path)
    elif simulator_name == 'tdycore':
         simulator = QASimulatorTDycore(path)
    elif simulator_name == 'dataset_cos':
         simulator = QASimulatorDatasetCos(path)
    elif simulator_name == 'dataset_sin':
         simulator = QASimulatorDatasetSin(path)
    else:
        print_err_msg('Simulator {} not recognized in simulator_factor.py.'
              .format(simulator_name))
    debug_pop()
    return simulator
