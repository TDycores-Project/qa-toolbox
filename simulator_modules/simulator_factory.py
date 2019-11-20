import sys
import os

from qa_common import *
from qa_debug import *

from simulator_modules.crunchflow import QASimulatorCrunchFlow
from simulator_modules.pflotran import QASimulatorPFLOTRAN
from simulator_modules.python import QASimulatorPython
from simulator_modules.tough2 import QASimulatorTOUGH2
from simulator_modules.tough3 import QASimulatorTOUGH3
from simulator_modules.tdycore import QASimulatorTDycore

if sys.version_info[0] == 2:
    from ConfigParser import SafeConfigParser as config_parser
else:
    from configparser import ConfigParser as config_parser

def locate_simulators():
    debug_push('simulator_factory.locate_simulators')
    if os.path.exists('simulators.sim'):
      sim_file = 'simulators.sim'
    else:
      sim_file='default_simulators.sim'
    config = config_parser()
    config.read(sim_file)
    simulators = config.items('simulators')
    simulator_dict = {}
    to_be_removed = []
    for simulator, path in simulators:
        if not os.path.isfile(path):
            print('{} not found among simulator paths.'.format(path))
            to_be_removed.append(simulator)
        else:
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
    else:
        print('Simulator {} not recognized in simulator_factor.py.'
              .format(simulator_name))
        raise
    debug_pop()
    return simulator
