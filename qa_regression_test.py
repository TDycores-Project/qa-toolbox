import sys
import os
from h5py import *
import numpy as np
import math

#from qa_test_error import QATestError
#from qa_test_manager import QATestManager
from qa_debug import *
from qa_common import *

#sys.path.append("..")


class QARegressionTest(object):
    
    def __init__(self):
        debug_push('QARegressionTest init')
        self._fail = False
        self._tolerance = 1e-12
        debug_pop()

    def compare_values(self):
        gold_dict = self._process_gold_files()
        test_dict = self._get_test_values()

        fail_dict = {}            
        if test_dict.keys() != gold_dict.keys():
           raise Exception('test_values to not match gold values')            
        for key1,value1 in test_dict.items(): 
            gold_value = gold_dict[key1]
            test_value = value1
        
            delta = abs(test_value-gold_value) #####DEBUG
        
            if delta > self._tolerance:
                self._fail = True
                fail_dict[key1] = delta
                
        if self._fail == True:
            with open('regression_test/regression_test_output.txt','w') as f:
                for key,value in fail_dict.items():
                    f.write('{} difference = {} \n'.format(key,value))
            print_err_msg('Regression test failed. Check regression_test_output.txt') 
        else:
            print('Regression test passed, continuing with qa_tests')
            
    def _get_test_values(self):
        time_slice_filename = '0.0_Pressure_regression_run1_error.stat'
        observation_filename = '0.0_0.0_0.0_Pressure_regression_run1_error.stat'
        total_error_filename = 'Pressure_regression_run1_error_documentation.stat'
        
        time_slice_keys, time_slice_values = self._process_stat_file(time_slice_filename)
        observation_keys, observation_values = self._process_stat_file(observation_filename)
        total_error_keys, total_error_values = self._process_stat_file(total_error_filename)
        
        test_dict=self._create_dict(time_slice_keys,time_slice_values,
                                    observation_keys,observation_values,
                                    total_error_keys,total_error_values)
        
        return test_dict
    
    def _process_stat_file(self,filename):
        fin = open(filename,'r')
        
        keys = []
        values = []
        for line in fin:
            words = line.strip().split('=')
            keys.append(words[0])
            values.append(float(words[1].split()[0]))

        return keys, values
    
    def _create_dict(self,time_slice_keys,time_slice_values,observation_keys,
                     observation_values,total_error_keys,total_error_values):
        error_dict = {}
        
        for i in range(len(time_slice_keys)):
            error_dict['time_slice_{}'.format(time_slice_keys[i])] = time_slice_values[i]
            error_dict['observation_{}'.format(observation_keys[i])] = observation_values[i]
        
        for i in range(len(total_error_keys)):
            error_dict['{}'.format(total_error_keys[i])] = total_error_values[i]
            
        return error_dict
            
    
    def _process_gold_files(self):
        time_slice_filename = '0.0_Pressure_regression_run1_error.stat.gold'
        observation_filename = '0.0_0.0_0.0_Pressure_regression_run1_error.stat.gold'
        total_error_filename = 'Pressure_regression_run1_error_documentation.stat.gold'
        
        time_slice_keys, time_slice_values = self._process_stat_file(time_slice_filename)
        observation_keys, observation_values = self._process_stat_file(observation_filename)
        total_error_keys, total_error_values = self._process_stat_file(total_error_filename)

        gold_dict=self._create_dict(time_slice_keys,time_slice_values,
                                    observation_keys,observation_values,
                                    total_error_keys,total_error_values)

        
        return gold_dict
