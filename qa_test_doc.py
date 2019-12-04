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

    def set_input_filename(self,simulator,filename):
        self._filenames[simulator] = filename

    def add_time_slice(self,doc_time_slice):
        self._time_slices.append(doc_time_slice)
    
    def add_observation(self,doc_observation):
        self._observations.append(doc_observation)
    
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

        # -------------------------------
        # results summary need to go here
        # -------------------------------

        description_file = 'description_{}.txt'.format(self._filename_root) ##make so this is try--> don't need it ###written in markup --> description of problem description_template... what if don't want description etc...

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
        n = 1

        for run in self._runs:
            scenario_string = 'Scenario {}'.format(run._run_number)
            f.write("{}\n".format(scenario_string))
            f.write("{}\n".format('-'*len(scenario_string)))
            f.write("\n")
            simulators = self._simulators
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
                    f.write(".. literalinclude:: ..{}/{}\n\n".format(
                                                         self._local_path,
                                              variable._error_stat))
                    f.write(".. _figure{}:\n".format(n))
                    f.write("\n")
                    f.write(".. figure:: ..{}/{}\n   :width: {} %\n\n".format(
                                   self._local_path,variable._solution_png[0],width_percent))
                    f.write(".. figure:: ..{}/{}\n   :width: {} %\n\n".format(
                                   self._local_path,variable._error_png[0],width_percent))
                    n = n+1
          
        f.close()

class QATestDocIndex(object):
    
    def __init__(self,testlog):
        self.testlog = testlog
        
    def write_index(self):#,testlog_file):
        file_dict = self.testlog.read_contents()
        
        self.write_toctree(file_dict)
        self.write_introfiles(file_dict)
        
        f = open('../docs/index.rst','w')
        
        intro = """
***************************
QA Test Suite Documentation        
***************************

.. toctree::
   :maxdepth: 2
""" 
        
        f.write(intro)
        
        for folder in file_dict.keys():
            f.write("""
   intro_{}.rst
            """.format(folder))

            
            
        toctree_intro = """
.. toctree::
   :hidden:
"""
        f.write(toctree_intro)
        for folder,tests in file_dict.items():          
            for i in range(len(tests)):
                toctree="""
   include_toctree_{}_{}.rst""".format(folder,tests[i])
                f.write(toctree)                
        f.close()
        
    def write_toctree(self,file_dict):
        
        for folder,tests in file_dict.items():
            ###RELATIVE PATHS.... MAY NEED TO CHANGE THIS LATER.....            
            for i in range(len(tests)):
                filename = '../docs/include_toctree_{}_{}.rst'.format(folder,tests[i])
                f = open(filename, 'w')
                toctree = """
.. include:: ../{}/{}.rst                
                """.format(folder,tests[i])
                f.write(toctree)
                f.close()
        
    def write_introfiles(self, file_dict):        
        for folder, test in file_dict.items():
#            pretty_name = test.replace('_',' ').title()
            filename = '../docs/intro_{}.rst'.format(folder)
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
        
      