import sys
import os
import configparser
import re

import numpy as np

from qa_common import *
from qa_debug import *

successful_tests = 'successful_tests.log'
root_directory = os.getcwd()
    
class QATestDoc(object):
    
    def __init__(self,doc_dir):
        debug_push('QATestDoc init')
        
        self.doc_dir = doc_dir
        self.title = ''
        self.filename_root = ''

        self.output_dicts = []
        self.cfg_dicts = []
        self.swap_dicts = []
        self.test_names = []
        self.folders = []
        self._path = []
        self.folder_dict = {}
        self.rst_file_list = []
        
        debug_pop()
        

    def create_doc_file(self,test_path):
        debug_push("QATestDoc create_doc_file")
        test = test_path.replace('{}/'.format(self.doc_dir),'')
        self._process_test_cfg_files_doc(test)
        debug_pop()
            
    def create_index_file(self):
        debug_push("QATestDoc create_index_file")
        os.chdir(root_directory)
        test_cfgs = []

        self.test_names = []
        self.folders = []

        try:
            f = open('successful_tests.log','r')
        except:
            print("File {} not found".format(successful_tests))

        # cannot place for loop inside try statement as any failure will
        # cause the File {} not found exception, and this can be misleading
        for line in f:
            if line.strip():   ####get rid of blank lines
                test_cfgs.append(line)
                self._process_test_cfg_files_index(line)
        f.close()
        
        self._create_folder_test_dict(test_cfgs)
        ###append test_cfgs that were not run but in successful test to index file
        ##group based on folder
        test_names = self.test_names
        if debug_verbose():
            print(test_names)
        
        os.chdir(self.doc_dir)
        filename='index.rst'
        
        intro = """
***************************
QA Test Suite Documentation        
***************************

.. toctree::
   :maxdepth: 2
   
   test_suite_instructions.rst
   crunchtope_instructions.rst
"""
        intro_docs = []
        for key in self.folder_dict:
#            pretty_name=key.replace('_',' ').title()
            intro_docs.append("""
   /qa_tests/intro_{}.rst
            """.format(key))

        toctree = """
.. toctree::
   :hidden:
        
"""
        toctree_list = []
        
        for i in range(len(test_names)):
#            pretty_name=key.replace('_',' ').title()
            toctree_list.append("""
   include_toctree_{}.rst
            """.format(test_names[i]))
            
######save file in documentation folder        
        f = open(filename, 'w')
        f.write(intro)
        for i in range(len(self.folder_dict)):
                f.write(intro_docs[i])
                
        f.write(toctree)
        for i in range(len(test_names)):
                f.write(toctree_list[i])
        f.close()
        
        self._create_include_toc_tree_file()
        self._create_intro_test_file()
        debug_pop()

                
    def _process_test_cfg_files_index(self,test_cfg):
        debug_push("QATestDoc _process_test_cfg_files_index")

        _path, cfg_name = os.path.split(test_cfg)

        os.chdir(_path)

        config = configparser.ConfigParser()
        if debug_verbose():
            print(cfg_name)
        config.read(cfg_name.strip())
        
        sections = config.sections()
        
        for section in sections:

            opt_file = section+'.opt'#root_dir+'/'+section +'.opt'
            config_opt = configparser.ConfigParser()
            config_opt.read(opt_file)
            if debug_verbose():
                print(opt_file)
            output_options = \
                  self._section_from_file(config_opt,'output_options') ####faster way to do this probably...

             
            self.folders.append(_path)
            title = output_options['plot_title'] ####space between fine?????
            if debug_verbose():
                print('title: {}'.format(title))
            if title not in self.test_names:    #faster way??? ### can not have two tests with same name
                 self.test_names.append(title)
        debug_pop()
                
    
    def _process_test_cfg_files_doc(self,test_cfg):
        debug_push("QATestDoc _process_test_cfg_files_doc")

        self.folder, cfg_name = os.path.split(test_cfg)

        os.chdir(self.folder)

        config = configparser.ConfigParser()
        config.read(cfg_name.strip())
            
        sections = config.sections()
            
            
        for section in sections:
            cfg_options = \
                 self._section_from_file(config,section)
            opt_file = section+'.opt'
            config_opt = configparser.ConfigParser()
            config_opt.read(opt_file)
            self.output_options = \
                  self._section_from_file(config_opt,'output_options') ####faster way to do this probably...
            self.swap_options = \
                  self._section_from_file(config_opt,'swap_options')
 
                 

            title = self.output_options['plot_title'] ####space between fine?????
                
            if title not in self.test_names:    #faster way??? ### can not have two tests with same name
                 self.test_names.append(title)

            self.template = cfg_options['template']
            simulators = cfg_options['simulators'].split(',')
            self.simulators = [x.strip(' ') for x in simulators]

            self._get_input_parameters(self.output_options,self.swap_options)
    
            self._format_intro()
            self._format_results_summary()
            self._format_description() 
            self._format_detailed_results() ####see if observation file exsists if not....
            self._format_simulator_files()
    
            self._write_doc_file() 
        debug_pop()
    
    def _get_input_parameters(self,output_options,swap_options):

        debug_push('QATestDoc _get_input_parameters')
        self._get_input_from_options(output_options)
        self._get_input_from_swap_options(swap_options)
        debug_pop()

    def _get_input_from_options(self,output_options):
        debug_push('QATestDoc _get_input_from_options')
        self.variable = output_options['variables']   ###need to take into account more than 1 variable
        self.time_units = output_options['plot_time_units']
        self.title = output_options['plot_title']   ##better way to do this
        self.title.strip()
        self.filename_root = self.title.lower().replace(" ","_")
        self.times = time_strings_to_float_list_for_documentation(
                    output_options['times'].split(',')) ###need to make this handle if no time slice
        loc=qa_lookup(output_options,'locations',[])

        if len(loc)>0: 
            self.locations = location_strings_to_float_list(qa_lookup(output_options,'locations',[]))
        else:
            self.locations=loc
        debug_pop()
        
        
    def _get_input_from_swap_options(self,swap_options):
        debug_push('QATestDoc _get_input_from_swap_options')
        ###see if it's empty.... count how many scenarios
        self.num_scenarios = self._process_swap_options(swap_options)
        debug_pop()
    
    def _format_intro(self):
        debug_push('QATestDoc _format_intro')
        
        simulators = self.simulators
        intro = """
.. _{0}:
    
{1}
{2}
{1}
:ref:`{0}-results summary`

:ref:`{0}-description`

:ref:`{0}-detailed results`
""".format(self.filename_root,'*'*len(self.title),self.title)

        simulator_intro = [None] * len(simulators)
        for i in range(len(simulators)):
            simulator_intro[i] = """
:ref:`{}-{} Input File`

""".format(self.filename_root,simulators[i])

        self.intro = intro
        self.simulator_intro = simulator_intro
        debug_pop()
    
    
    def _format_results_summary(self):
        debug_push('QATestDoc _format_results_summary')
        
        times = self.times
        num_scenarios = self.num_scenarios
        variable = self.variable
        template = self.template

        
        results_summary_intro = """
.. _{}-results summary:
    
Results Summary
===============

""".format(self.filename_root)         
        
        results_summary=[' ']*num_scenarios
        
        for i in range(num_scenarios):
            
            error_values,error_times,error_locations,index_list=self._get_error_and_index_list(variable,template,i,times)
            
            if error_values != None:
                results_summary[i] = """
    
Scenario {}
{}
    
.. list-table::
   :widths: 40 35 10 20
   :header-rows: 1
   
   * - 
     - Value
     - Time
     - Location
   * - :ref:`Maximum Absolute Error <{}_figure{}>`
     - {}
     - {}
     - {}
   * - :ref:`Maximum Relative Error <{}_figure{}>`
     - {}
     - {}
     - {}
   * - :ref:`Maximum Average Absolute Error <{}_figure{}>`
     - {}
     - {}
     - 
   * - :ref:`Maximum Average Relative Error <{}_figure{}>`
     - {}
     - {}
     - 


""".format(i+1,'-'*(len(str(i+1))+9),template,index_list[0],error_values[0],error_times[0],error_locations[0],template,index_list[1],error_values[1],error_times[1],\
           error_locations[1],template,index_list[2],error_values[2],error_times[2],template,index_list[3],error_values[3],error_times[3])

        
        self.results_summary_intro = results_summary_intro
        self.results_summary = results_summary
        debug_pop()


    def _format_description(self):
        debug_push('QATestDoc _format_description')

        description_file = 'description_{}.txt'.format(self.filename_root) ##make so this is try--> don't need it ###written in markup --> description of problem description_template... what if don't want description etc...

        try:
            with open(description_file,'r') as file:
                description_text = file.read()
        except:
            description_text = "TO BE ADDED LATER"
        
        
        description = """
.. _{}-description:
    
The Problem Description
=======================

{}


""".format(self.filename_root,description_text)

        self.description=description
        debug_pop()

    def _format_detailed_results(self):      
        debug_push('QATestDoc _format_detailed_results')
        #######assuming only two simulators..... change to accomadate variable amounts
        folder = self.folder
        num_scenarios = self.num_scenarios
        times = self.times
        locations = self.locations
        simulators = self.simulators
        time_unit = self.time_units
        variable = self.variable
        template = self.template
        
        detailed_results_intro = """

.. _{}-detailed results:

Detailed Results
================

""".format(self.filename_root)

        k = 1

        #detailed_results_heading=[None]*len(spacing)
        detailed_results = [[None] * num_scenarios for i in range(len(times))]
        observation_results = [[None] * num_scenarios for i in range(len(locations))]

        for i in range(num_scenarios):
            first = True
            for j in range(len(times)):
                if first == True:
        
                    detailed_results[j][i]="""
Scenario {}
{}
            
Comparison of {} vs {} at {} {} with scenario {}.
            
.. literalinclude:: ../{}/{}_{}_{}_run{}_error.stat
            
.. _{}_figure{}:
                
.. figure:: ../{}/{}_{}_{}_run{}.png
   :width: 60 %
               
.. figure:: ../{}/{}_{}_{}_run{}_error.png
   :width: 60 %
            
            
""".format(i+1,'-'*(len(str(i+1))+9),simulators[0],simulators[1],times[j],time_unit, \
                                                  i+1,folder,times[j],variable,template,i+1, \
                                                  template,k,folder,times[j],variable,template, i+1, \
                                                  folder,times[j],variable,template,i+1)
                    first = False
                    k=k+1
                    
                else:
        
                    detailed_results[j][i]="""
Comparison of {} vs {} at {} {} with scenario{}.
            
.. literalinclude:: ../{}/{}_{}_{}_run{}_error.stat
            
.. _{}_figure{}:
                
.. figure:: ../{}/{}_{}_{}_run{}.png
   :width: 60 %
               
.. figure:: ../{}/{}_{}_{}_run{}_error.png
   :width: 60 %


""".format(simulators[0],simulators[1],times[j],time_unit, \
                               i+1,folder,times[j],variable,template,i+1, \
                               template,k,folder,times[j],variable,template, i+1, \
                               folder,times[j],variable,template,i+1)
                    k=k+1
                    
        
        
            if len(locations) > 0:
                for j in range(len(locations)):
                    observation_results[j][i] = """
Observation Point
^^^^^^^^^^^^^^^^^

Comparison of {} vs {} at {} m, {} m, {} m with scenario {}

.. literalinclude:: ../{}/{}_{}_{}_{}_{}_run{}_error.stat

.. figure:: ../{}/{}_{}_{}_{}_{}_run{}.png  
   :width: 60 %  
   
.. figure:: ../{}/{}_{}_{}_{}_{}_run{}_error.png
   :width: 60 %
   
""".format(simulators[0],simulators[1],locations[j][0],locations[j][1],locations[j][2], \
           i+1, folder, locations[j][0], locations[j][1],locations[j][2], \
           variable,template, i+1,folder, \
           locations[j][0],locations[j][1],locations[j][2], \
           variable,template,i+1,folder,locations[j][0],locations[j][1], \
           locations[j][2],variable,template,i+1)


            self.detailed_results_intro = detailed_results_intro
            self.detailed_results = detailed_results
            self.observation_results = observation_results

        debug_pop()

    def _format_simulator_files(self):
        debug_push('QATestDoc _format_simulator_files')
        simulators = self.simulators
        folder = self.folder
        template = self.template
        
        simulator_files = [None]*len(simulators)

        for i in range(len(simulators)):
            
            simulator_files[i] = """
.. _{}-{} Input File:
    
{} Input File
{}

.. literalinclude:: ../{}/{}.{}


""".format(self.filename_root,simulators[i],simulators[i].upper(),'='*(len(simulators[i])+11),folder,template,simulators[i].lower())

        self.simulator_files = simulator_files
        debug_pop()


    def _get_error_and_index_list(self,variable,template,i,times):
        debug_push('QATestDoc _get_error_and_index_list')


        file = '{}_{}_run{}_error_documentation.stat'.format(variable,template,i+1)
        try:
            fin = open(file,'r')
            error_times = []
            error_values = []
            error_locations = []
            
            for line in fin:
                words = line.strip().split('=')
            
                
                if ('Time ' in words):
                    error_times.append(words[-1])
                elif ('Location ' in words):
                    error_locations.append(words[-1])
                else:
                    error_values.append(words[1])
                    
            index_list = []        
            for j in range(len(error_times)):
                raw_time = error_times[j].strip().split()
                raw_time = float(raw_time[0])
            
                index = times.index(raw_time)
                
                index = index+1+(i*len(times))
                index_list.append(index)
        except:
            error_values = None
            error_times = None
            error_locations = None
            index_list = None
            
        debug_pop()
        return error_values,error_times,error_locations,index_list

    def _write_doc_file(self):
        debug_push('QATestDoc _write_doc_file')
        num_scenarios = self.num_scenarios
        simulators = self.simulators
        times = self.times
        locations = self.locations

        
        filename = 'documentation_{}.rst'.format(self.filename_root)
        
        f = open(filename, 'w')
        
        f.write(self.intro)
        for i in range(len(simulators)):
            f.write(self.simulator_intro[i])
        f.write(self.results_summary_intro) 
        for i in range(num_scenarios):
            f.write(self.results_summary[i])
        f.write(self.description)
        f.write(self.detailed_results_intro)
        for i in range(num_scenarios):
            for j in range(len(times)):
                f.write(self.detailed_results[j][i])
            for j in range(len(locations)):
                f.write(self.observation_results[j][i])
        for i in range(len(simulators)):
            f.write(self.simulator_files[i])
        f.close()
        debug_pop()
        
    
    def _create_include_toc_tree_file(self):
        debug_push('QATestDoc _create_include_toc_tree_file')

        for i in range(len(self.test_names)):

            filename = 'include_toctree_{}.rst'.format(self.test_names[i])
            toctree=[None]*len(self.test_names)

            toctree = """
.. include:: ../{}/documentation_{}.rst                
                """.format(self.folders[i],self.test_names[i])
                
            f = open(filename, 'w')

            f.write(toctree)
        debug_pop()
                
        
    def _create_intro_test_file(self):
        debug_push('QATestDoc _create_intro_test_file')
        os.chdir(self.doc_dir + '/qa_tests') ###requires them to be there already
        

        for key, value in self.folder_dict.items():
            pretty_name = key.replace('_',' ').title()
            filename = 'intro_{}.rst'.format(key)
            intro = """
.. {}-qa-tests:

{} QA Tests
{}

            """.format(key,pretty_name,'='*(len(key)+9))
            
            intro_links = [None]*len(value)
            if len(value) == 1:
                intro_links[0] = """
* :ref:`{}`
                """.format(value[0])
            else:
                for i in range(len(value)):
                    intro_links[i] = """
{}
{}
* :ref:`{}`
                """.format(value[i],'-'*len(value[i]),value[i])
                
            f = open(filename, 'w')
            f.write(intro)
            for i in range(len(value)):
                f.write(intro_links[i])
        debug_pop()
                
            
    def _create_folder_test_dict(self,test_cfgs):
        debug_push('QATestDoc _create_folder_test_dict')

        folders = self.folders
        

        for i in range(len(folders)):

            if folders[i] in self.folder_dict.keys():
                self.folder_dict[folders[i]].append(self.test_names[i])
            else:
                self.folder_dict[folders[i]] = [self.test_names[i]]
        debug_pop()
       
    def _section_from_file(self,config,key):
        debug_push('QATestDoc _section_from_file')
        xx_options = {}
        try:
            xx_options = list_to_dict(config.items(key))
        except Exception as error:
            pass
        debug_pop()
        return xx_options

    
    def _process_swap_options(self,swap_options):   
        debug_push('QATestDoc _process_swap_options')
        
        max_attempts = 1
        if swap_options:

           if 'method' in swap_options:
               swap_method = swap_options['method']     ####should we be popping?
               swap_options.pop('method', None)
           else:
               swap_method = 'list'
        
           if swap_method == 'list':
               item_len = len(list(swap_options.values())[0].split(','))
               max_attempts = item_len

           
           elif self._swap_method == 'iterative':
                max_attempts = int(swap_options['max_attempts'])
                swap_options.pop('max_attempts', None)


        debug_pop()
        return max_attempts
    
#    def _append_rst_list_to_file(self): #self.rst_file_list
#        filename='conf.py'
        


