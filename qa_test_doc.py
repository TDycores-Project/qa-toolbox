import sys
import os
import configparser
import re

import numpy as np

from qa_common import *
from qa_debug import *

class QATestDocVariable():
    def __init__(self,name):
        self._name = name
        self._solution_png = []
        self._error_png = []
        self._error_stat = None

    def add_solution_png(self,png_filename):
        self._solution_png.append(png_filename)
        
    def add_error_png(self,png_filename):
        self._error_png.append(png_filename)
        
    def set_error_stat(self,stat_filename):
        self._error_stat = stat_filename

class QATestDocTimeSlice():
    def __init__(self,time,time_unit):
        self._time = time
        self._time_unit = time_unit
        self._variables = []

    def add_variable(self,variable):
       self._variables.append(variable)

class QATestDocObservation():
    def __init__(self,location):
        self._location = location
        self._variables = []

    def add_variable(self,variable):
       self._variables.append(variable)       

class QATestDocRun():
    def __init__(self,run_number):
        self._run_number = run_number
        self._time_slices = []
        self._observations = []
        self._overall = []
        self._filenames = {}
        self._rst_filename = ''
        
        #####time slice
        self._maximum_absolute_errors = {}
        self._maximum_absolute_error_times = {}
        self._maximum_absolute_error_locations = {}
        self._maximum_absolute_error_index = {}  
        
        self._maximum_relative_errors = {}
        self._maximum_relative_error_times = {}
        self._maximum_relative_error_locations = {}
        self._maximum_relative_error_index = {}
        
        self._maximum_average_absolute_errors = {}
        self._maximum_average_absolute_error_times = {}
        self._maximum_average_absolute_error_index = {}
        
        self._maximum_average_relative_errors = {}
        self._maximum_average_relative_error_times = {}
        self._maximum_average_relative_error_index = {}
        
        ####observation point
        self._maximum_absolute_errors_observation = {}
        self._maximum_absolute_error_times_observation = {}
        self._maximum_absolute_error_locations_observation = {}
        self._maximum_absolute_error_index_observation = {}  
        
        self._maximum_relative_errors_observation = {}
        self._maximum_relative_error_times_observation = {}
        self._maximum_relative_error_locations_observation = {}
        self._maximum_relative_error_index_observation = {}
        
        self._maximum_average_absolute_errors_observation = {}
        self._maximum_average_absolute_error_location_observation = {}
        self._maximum_average_absolute_error_index_observation = {}
        
        self._maximum_average_relative_errors_observation = {}
        self._maximum_average_relative_error_location_observation = {}
        self._maximum_average_relative_error_index_observation = {}

    def set_input_filename(self,simulator,filename):
        self._filenames[simulator] = filename

    def add_time_slice(self,doc_time_slice):
        self._time_slices.append(doc_time_slice)
    
    def add_observation(self,doc_observation):
        self._observations.append(doc_observation)
        
    def add_max_absolute_error(self,variable,error):
        maximum_absolute_error_all_times = self._format_documentation_values(error.maximum_absolute_error_all_times)
        
        self._maximum_absolute_errors[variable]= maximum_absolute_error_all_times
        self._maximum_absolute_error_times[variable] = error.maximum_absolute_error_time
        self._maximum_absolute_error_locations[variable] = error.maximum_absolute_error_location_all_times
        self._maximum_absolute_error_index[variable] = error.maximum_absolute_error_index
    
    def add_max_relative_error(self,variable,error):
        maximum_relative_error_all_times = self._format_documentation_values(error.maximum_relative_error_all_times)

        self._maximum_relative_errors[variable] = maximum_relative_error_all_times
        self._maximum_relative_error_times[variable] = error.maximum_relative_error_time
        self._maximum_relative_error_locations[variable] = error.maximum_relative_error_location_all_times
        self._maximum_relative_error_index[variable] = error.maximum_relative_error_index
        
    def add_max_average_absolute_error(self,variable,error):
        maximum_average_absolute_error = self._format_documentation_values(error.maximum_average_absolute_error)
        
        self._maximum_average_absolute_errors[variable] = maximum_average_absolute_error
        self._maximum_average_absolute_error_times[variable] = error.maximum_average_absolute_error_time
        self._maximum_average_absolute_error_index[variable] = error.maximum_average_absolute_error_index
        
    def add_max_average_relative_error(self,variable,error):
        maximum_average_relative_error = self._format_documentation_values(error.maximum_average_relative_error)
        
        self._maximum_average_relative_errors[variable] = maximum_average_relative_error
        self._maximum_average_relative_error_times[variable] = error.maximum_average_relative_error_time
        self._maximum_average_relative_error_index[variable] = error.maximum_average_relative_error_index
        
    def add_max_absolute_error_observation(self,variable,error):
        maximum_absolute_error_all_locations = self._format_documentation_values(error.maximum_absolute_error_all_locations)
        
        self._maximum_absolute_errors_observation[variable]= maximum_absolute_error_all_locations
        self._maximum_absolute_error_times_observation[variable] = error.maximum_absolute_error_time_all_locations
        self._maximum_absolute_error_locations_observation[variable] = error.maximum_absolute_error_locations
        self._maximum_absolute_error_index_observation[variable] = error.maximum_absolute_error_observation_index
    
    def add_max_relative_error_observation(self,variable,error):
        maximum_relative_error_all_locations = self._format_documentation_values(error.maximum_relative_error_all_locations)
        
        self._maximum_relative_errors_observation[variable] = maximum_relative_error_all_locations
        self._maximum_relative_error_times_observation[variable] = error.maximum_relative_error_time_all_locations
        self._maximum_relative_error_locations_observation[variable] = error.maximum_relative_error_locations
        self._maximum_relative_error_index_observation[variable] = error.maximum_relative_error_observation_index
        
    def add_max_average_absolute_error_observation(self,variable,error):
        maximum_average_absolute_error_observation = self._format_documentation_values(error.maximum_average_absolute_error_observation)
        
        self._maximum_average_absolute_errors_observation[variable] = maximum_average_absolute_error_observation
        self._maximum_average_absolute_error_location_observation[variable] = error.maximum_average_absolute_error_location
        self._maximum_average_absolute_error_index_observation[variable] = error.maximum_average_absolute_error_observation_index
        
    def add_max_average_relative_error_observation(self,variable,error):
        maximum_average_relative_error_observation = self._format_documentation_values(error.maximum_average_relative_error_observation)

        self._maximum_average_relative_errors_observation[variable] = maximum_average_relative_error_observation
        self._maximum_average_relative_error_location_observation[variable] = error.maximum_average_relative_error_location
        self._maximum_average_relative_error_index_observation[variable] = error.maximum_average_relative_error_observation_index


    def _format_documentation_values(self,error_string):
        split_array = error_string.split()
        error_float = float(split_array[0])
        
        truncated_error = format_floating_number(error_float)
        
        try:
            new_error_string = truncated_error + ' ' + split_array[1]
        except:
            new_error_string = truncated_error
        
        return new_error_string

    
class QATestDoc(object):
    
    def __init__(self,doc_dir,local_path):
        debug_push('QATestDoc init')
        
        self._doc_dir = doc_dir
        self._local_path = local_path
        self._title = ''
        self._template = ''
        self._filename_root = ''
        self._simulators = []
        self._runs = []
        debug_pop()

    def set_title(self,title):
        debug_push('QATestDoc set_title')
        self._title = title
        self._filename_root = self._title.lower().replace(" ","_")
        debug_pop()
        
    def set_template(self,template):
        debug_push('QATestDoc set_template')
        self._template = template
        debug_pop()
        
    def add_simulator(self,simulator):
        debug_push('QATestDoc add_simulator')
        self._simulators.append(simulator)
        debug_pop()
        
    def add_run(self,run):
        debug_push('QATestDoc add_comparison')
        self._runs.append(run)
        debug_pop()

    def write(self):   

        f = open(self._filename_root+'.rst','w')
        f.write("""
.. _{0}:
    
{1}
{2}
{1}
:ref:`{0}-results summary`

:ref:`{0}-description`

:ref:`{0}-detailed results`
""".format(self._filename_root,'*'*len(self._title),self._title))
     
        f.write("""
.. _{}-results summary:            
    
Results Summary
===============

""".format(self._filename_root))
                    
        for run in self._runs:
                f.write('\n')
                scenario_string = 'Scenario {}'.format(run._run_number)
                f.write("{}\n".format(scenario_string))
                f.write("{}\n".format('-'*len(scenario_string)))
                                
                variable_num = 0
                if run._maximum_absolute_error_index:
                    for variable in run._time_slices[0]._variables:
                        variable_string = variable._name 
                        f.write("\n")
                        f.write("Variable: {}".format(variable_string))
                    
                        f.write("""
                        
.. list-table::
   :widths: 40 25 25 25
   :header-rows: 1
   
   * - 
     - Value
     - Time
     - Location
   * - :ref:`Maximum Absolute Error <{}_{}_{}_figure{}>`
     - {}
     - {}
     - {}
   * - :ref:`Maximum Relative Error <{}_{}_{}_figure{}>`
     - {}
     - {}
     - {}
   * - :ref:`Maximum Average Absolute Error <{}_{}_{}_figure{}>`
     - {}
     - {}
     - 
   * - :ref:`Maximum Average Relative Error <{}_{}_{}_figure{}>`
     - {}
     - {}
     -
     
     
         """.format(self._filename_root,run._run_number,variable_string,
                    run._maximum_absolute_error_index[variable_string],
                    run._maximum_absolute_errors[variable_string],
                    run._maximum_absolute_error_times[variable_string],
                    run._maximum_absolute_error_locations[variable_string],
                    self._filename_root,run._run_number,variable_string,
                    run._maximum_relative_error_index[variable_string],
                    run._maximum_relative_errors[variable_string],
                    run._maximum_relative_error_times[variable_string],
                    run._maximum_relative_error_locations[variable_string],
                    self._filename_root,run._run_number,variable_string,
                    run._maximum_average_absolute_error_index[variable_string],
                    run._maximum_average_absolute_errors[variable_string],
                    run._maximum_average_absolute_error_times[variable_string],
                    self._filename_root,run._run_number,variable_string,
                    run._maximum_average_relative_error_index[variable_string],
                    run._maximum_average_relative_errors[variable_string],
                    run._maximum_average_relative_error_times[variable_string]))
                
                if run._maximum_absolute_error_index_observation:
                    f.write("""
Observation Point
^^^^^^^^^^^^^^^^^

""")
                    for variable in run._observations[0]._variables:       
                        variable_string = variable._name 
                        f.write("\n")
                        f.write("Variable: {}".format(variable_string))

                        f.write("""
                        
.. list-table::
   :widths: 40 25 25 25
   :header-rows: 1
   
   * - 
     - Value
     - Time
     - Location
   * - :ref:`Maximum Absolute Error <{}_{}_{}_observation_figure{}>`
     - {}
     - {}
     - {}
   * - :ref:`Maximum Relative Error <{}_{}_{}_observation_figure{}>`
     - {}
     - {}
     - {}
   * - :ref:`Maximum Average Absolute Error <{}_{}_{}_observation_figure{}>`
     - {}
     - 
     - {}
   * - :ref:`Maximum Average Relative Error <{}_{}_{}_observation_figure{}>`
     - {}
     - 
     - {}
     
     
         """.format(self._filename_root,run._run_number,variable_string,
                    run._maximum_absolute_error_index_observation[variable_string],
                    run._maximum_absolute_errors_observation[variable_string],
                    run._maximum_absolute_error_times_observation[variable_string],
                    run._maximum_absolute_error_locations_observation[variable_string],
                    self._filename_root,run._run_number,variable_string,
                    run._maximum_relative_error_index_observation[variable_string],
                    run._maximum_relative_errors_observation[variable_string],
                    run._maximum_relative_error_times_observation[variable_string],
                    run._maximum_relative_error_locations_observation[variable_string],
                    self._filename_root,run._run_number,variable_string,
                    run._maximum_average_absolute_error_index_observation[variable_string],
                    run._maximum_average_absolute_errors_observation[variable_string],
                    run._maximum_average_absolute_error_location_observation[variable_string],
                    self._filename_root,run._run_number,variable_string,
                    run._maximum_average_relative_error_index_observation[variable_string],
                    run._maximum_average_relative_errors_observation[variable_string],
                    run._maximum_average_relative_error_location_observation[variable_string]))
                        
        description_file = '{}/description_{}.txt'.format(self._doc_dir,self._template) ##make so this is try--> don't need it ###written in markup --> description of problem description_template... what if don't want description etc...

        try:
            with open(description_file,'r') as file:
                description_text = file.read()
        except:
            description_text = "TO BE ADDED LATER"

        f.write("""
.. _{}-description:
    
The Problem Description
=======================

{}


""".format(self._filename_root,description_text))

        f.write("""

.. _{}-detailed results:

Detailed Results
================

""".format(self._filename_root))

        width_percent = 60
                
        for run in self._runs:
            scenario_string = 'Scenario {}'.format(run._run_number)
            f.write("{}\n".format(scenario_string))
            f.write("{}\n".format('-'*len(scenario_string)))
            f.write("\n")
            simulators = self._simulators
           
            n = 0
            for time_slice in run._time_slices:
                time_string = '{} {}'.format(time_slice._time,
                                             time_slice._time_unit)
                for variable in time_slice._variables:                    
                    variable_string = variable._name
                    f.write("Comparison of {} at {} for {}: {}".format(
                                   variable_string,time_string,scenario_string,
                                  simulators[0]))
                    for i in range(1,len(simulators)):
                        f.write(" vs {}\n".format(simulators[i]))
                    f.write("\n")
                    # absolute here make it relative to the top source dir
                    # in the sphinx repo (usually: sphinx/doc/source/.)
                    f.write(".. literalinclude:: /{}/{}\n\n".format(
                                                         self._doc_dir,
                                              variable._error_stat))
                    f.write(".. _{}_{}_{}_figure{}:\n".format(self._filename_root,
                                                run._run_number,variable_string,n))
                    f.write("\n")

                    f.write(".. figure:: /{}/{}\n   :width: {} %\n\n".format(
                                   self._doc_dir,variable._solution_png[0],width_percent))
                    f.write(".. figure:: /{}/{}\n   :width: {} %\n\n".format(
                                   self._doc_dir,variable._error_png[0],width_percent))
                n = n+1
                

                    
            if len(run._observations) > 0:
                f.write("""
Observation Point
^^^^^^^^^^^^^^^^^

""")
            k = 0    
            for observation in run._observations:              
                observation_string = '{}'.format(observation._location)
                for variable in observation._variables:
                    variable_string = variable._name
                    f.write("Comparison of {} at {} for {}: {}".format(
                                 variable_string,observation_string,scenario_string,
                                 simulators[0]))
                    for i in range(1,len(simulators)):
                        f.write(" vs {}\n".format(simulators[i]))
                    f.write("\n")

                    f.write(".. _{}_{}_{}_observation_figure{}:\n".format(self._filename_root,
                                                            run._run_number,variable_string,k))
                    f.write("\n")

                    f.write(".. literalinclude:: /{}/{}\n\n".format(
                                 self._doc_dir,variable._error_stat))
                    f.write(".. figure:: /{}/{}\n   :width: {} %\n\n".format(
                                 self._doc_dir,
                                 variable._solution_png[0],width_percent))
                    f.write(".. figure:: /{}/{}\n   :width: {} %\n\n".format(
                                 self._doc_dir,
                                 variable._error_png[0],width_percent))
                k = k+1

        f.close()

class QATestDocIndex(object):
    
    def __init__(self,testlog,_doc_dir):
        self.testlog = testlog
        if _doc_dir == None:
            self._doc_dir = '../docs'
        else:
            self._doc_dir = _doc_dir
        if not os.path.isdir(self._doc_dir):
            print_err_msg('Document Directory Path: {} does not exsist'.format(self._doc_dir))
        
        
    def write_index(self):#,testlog_file):
        file_dict = self.testlog.read_contents()
        
        self.write_toctree(file_dict)
        self.write_introfiles(file_dict)
        
        f = open('{}/index.rst'.format(self._doc_dir),'w')
        
        intro = """
***************************
QA Test Suite Documentation        
***************************

.. toctree::
   :maxdepth: 2
""" 
        
        f.write(intro)
        
        for folder_path in file_dict.keys():
            folder = folder_path.strip().split('/')[-1]
            f.write("""
   intro_{}.rst
            """.format(folder))

            
            
        toctree_intro = """
.. toctree::
   :hidden:
"""
        f.write(toctree_intro)
        for folder_path,tests in file_dict.items(): 
            folder = folder_path.strip().split('/')[-1]
            for i in range(len(tests)):
                toctree="""
   include_toctree_{}_{}.rst""".format(folder,tests[i])
                f.write(toctree)                
        f.close()
        
    def write_toctree(self,file_dict):
        
        for folder_path,tests in file_dict.items():
            folder = folder_path.strip().split('/')[-1]            
            for i in range(len(tests)):
                filename = '{}/include_toctree_{}_{}.rst'.format(self._doc_dir,folder,tests[i])
                f = open(filename, 'w')
                toctree = """
.. include:: //{}/{}.rst                
                """.format(folder_path,tests[i])
                f.write(toctree)
                f.close()
        
    def write_introfiles(self, file_dict):        
        for folder_path, test in file_dict.items():
            folder = folder_path.strip().split('/')[-1]
            filename = '{}/intro_{}.rst'.format(self._doc_dir,folder)
            intro = """
.. {}-qa-tests:

{} QA Tests
{}

            """.format(folder,folder,'='*(len(folder)+9))
            
            intro_links = [None]*len(test)
            if len(test) == 1:
                intro_links[0] = """
* :ref:`{}`
                """.format(test[0])
            else:
                for i in range(len(test)):
                    intro_links[i] = """
{}
{}
* :ref:`{}`
                """.format(test[i],'-'*len(test[i]),test[i])
                
            f = open(filename, 'w')
            f.write(intro)
            for i in range(len(test)):
                f.write(intro_links[i])
            f.close()
        
      