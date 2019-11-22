import sys
import os
from h5py import *
import numpy as np
import math

from qa_test_error import QATestError
from qa_test_manager import QATestManager
from qa_debug import *

sys.path.append("..")

from simulator_modules.dataset import QASimulatorDatasetSin
from simulator_modules.dataset import QASimulatorDatasetCos

class QARegressionTest(object):
    
    def __init__(self):
        debug_push('QARegressionTest init')
        self._fail = False
        self._tolerance = 1e-12
        self._gold_filename_error_metrics = 'error_metrics.gold'
        self._gold_filename_absolute_error = 'absolute_error.gold'
        self._gold_filename_relative_error = 'relative_error.gold'
        debug_pop()
        
    
    def run_test(self,testlog): 
        root_dir = os.getcwd()
        simulators_dict = self._create_regression_simulator()

        config_file = root_dir+'/regression_tests/test.cfg'

  
        test_manager = QATestManager(simulators_dict)
        test_manager.process_config_file(config_file)
        test_manager.run_tests(testlog) 
        
        self._compare_values()


        
    def _create_regression_simulator(self):
        path=' '
        simulator_sin = QASimulatorDatasetSin(path)
        simulator_cos = QASimulatorDatasetCos(path)         
        simulator_dict = {}
        simulator_dict['dataset_cos'] = simulator_cos
        simulator_dict['dataset_sin'] = simulator_sin
        
        return simulator_dict


    def _compare_values(self):
        gold_dict = self._process_gold_files()
        test_dict = self._get_test_values()
        
        ##check to make sure same length
#        if len(all_test_values) != len(all_gold_values):
#            print('Size of test values (%d) does not match size of gold values (%d) in regression test' %
#                  (len(all_test_values),len(all_gold_values)))
#            exit(0)
#            
#        for i in range(len(all_gold_values)):
#            if len(all_test_values[i]) != len(all_gold_values[i]):
#                print('Size of test values (%d) does not match size of gold values (%d) in regression test' %
#                     (len(all_test_values[i]),len(all_gold_values[i])))
#                exit(0)
#                
#            for k in range(len(all_gold_values[i])):
#                gold_values = all_gold_values[i][k]
#                test_values = all_test_values[i][k]        
#
#                delta = abs(test_values-gold_values)
#                if delta>self._tolerance:
#                    self._fail = True


        fail_dict = {}            
        if test_dict.keys() != gold_dict.keys():
           raise Exception('test_values to not match gold values')            
        for key1,value1 in test_dict.items(): 
            gold_value = gold_dict[key1]
            test_value = value1
        
            delta = abs(test_value-gold_value) #####DEBUG

            if hasattr(delta, "__len__"):
                if max(delta)>self._tolerance:
                    self._fail = True
                    fail_dict[key1]=delta
            else:
                if delta>self._tolerance:
                    self._fail = True
                    fail_dict[key1]=delta
        
        
        if self._fail == True:
            with open('regression_test_output.txt','w') as f:
                for key,value in fail_dict.items():
                    f.write('{} difference = {} \n'.format(key,value))
            raise Exception('Regression test failed. Check regression_test_output.txt') #what did it fail on ##print out fail doc??
        else:
            print('Regression test passed, continuing with qa_tests')
            
            
            
            
    def _get_test_values(self):
        filename_cos = 'cos_dataset.h5'
        filename_sin = 'sin_dataset.h5'
        
        [times1,solution_cos] = self._get_values_from_h5file(filename_cos) ##time slice &obs point? 
        [times2,solution_sin] = self._get_values_from_h5file(filename_sin) ##time slice &obs point? 
        
        test_values = self._calc_error(times1,solution_cos,times2,solution_sin)
        
        return test_values

    
    def _get_values_from_h5file(self,filename):
        f = File(filename,'r')   ###best way to do this???
        group = '/Time Slice/Time: 0.000e+00 y'
        
        times = np.array(f['/Time Slice/Coordinates/X'])
        values = np.array(f[group+'/Pressure'])
        
        return times,values
        
        
    def _calc_error(self,times1,solution1,times2,solution2):
        
        ###better way   ---> store in stats file and read in from stats file??
        error = QATestError()

        error.calc_error_stats_1D(times1,solution1,times2,solution2)
        
#        error_metrics = []
#        error_metrics.append(error.average_absolute_error)
#        error_metrics.append(error.maximum_absolute_error)
#        error_metrics.append(error.maximum_relative_error)
#        error_metrics.append(error.average_relative_error)
#        error_metrics.append(error.absolute_relative_area)
        
        error_metrics = {}
        
        error_metrics['average absolute error'] = error.average_absolute_error
        error_metrics['maximum absolute error'] = error.maximum_absolute_error
        error_metrics['maximum relative error'] = error.maximum_relative_error
        error_metrics['average relative error'] = error.average_relative_error
        error_metrics['absolute relative area'] = error.absolute_relative_error   ###change area to error
    
        
        error_metrics['absolute error'] = error.absolute_error
        error_metrics['relative error'] = error.relative_error
        
#        test_values = []
#        test_values.append(error_metrics)
        
#        test_values.append(error.absolute_error)
#        test_values.append(error.relative_error)
        
        return error_metrics
    
    def _process_gold_files(self):
        all_gold_values = []
        
        gold_error_metrics = self._read_gold_error_metrics()
#        all_gold_values.append(gold_error_metrics)
        gold_dict= self._create_gold_dic(gold_error_metrics)
        
        gold_absolute_error = self._read_gold_error_array(self._gold_filename_absolute_error)
#        all_gold_values.append(gold_absolute_error)
        gold_dict['absolute error'] = gold_absolute_error
        
        gold_relative_error = self._read_gold_error_array(self._gold_filename_relative_error)
#        all_gold_values.append(gold_relative_error)
        gold_dict['relative error'] = gold_relative_error
        
        
        return gold_dict
    
    
    def _read_gold_error_metrics(self):
        values = []
        filename = self._gold_filename_error_metrics
        with open(filename,'r') as f:
            for line in f:
                row = (line.strip().split('='))
                values.append(float(row[-1]))

        return values
    
    def _read_gold_error_array(self,filename):
        values = np.loadtxt(filename)
        
        return values
    
    def _create_gold_dic(self,values):
        gold_dict={}

        
        gold_dict['average absolute error'] = values[0]
        gold_dict['maximum absolute error'] = values[1]
        gold_dict['maximum relative error'] = values[2]
        gold_dict['average relative error'] = values[3]
        gold_dict['absolute relative area'] = values[4]
        
        return gold_dict
