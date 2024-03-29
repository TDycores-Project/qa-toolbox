import sys
import re
import os

import subprocess
import textwrap
import csv
import shutil

from h5py import *
import numpy as np

import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
   mpl.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from matplotlib.ticker import FormatStrFormatter

from qa_swapper import Swapper
from qa_debug import *
from qa_common import *
from qa_test_error import *
from qa_solution import QASolutionReader
from qa_test_doc import *

class QASolutionComparison(object):
    
    def __init__(self,solution_dictionary,output_options,
                 mapped_simulator_names,template,run_number,doc_run):
        debug_push('QACompareSolutions init')
        
        self.solution_dictionary = solution_dictionary
        self.output_options = output_options
        self.mapped_simulator_names = mapped_simulator_names
        self.template = template
        self.run_number = run_number
        self.doc_run = doc_run
        
        debug_pop()
        
    def process_opt_file(self):
        debug_push('QACompareSolutions process_opt_file')
        if debug_verbose():
            print(self.solution_dictionary)
        
        self.plot_dimension = qa_lookup(self.output_options, 'plot_dimension','fail_on_missing_keyword')
        x_string = qa_lookup(self.output_options,'plot_x_label','fail_on_missing_keyword').split(',')
        y_string = qa_lookup(self.output_options,'plot_y_label','fail_on_missing_keyword').split(',')
        self.title = qa_lookup(self.output_options,'plot_title','fail_on_missing_keyword')
        self.variables = [x.strip() for x in qa_lookup(self.output_options,'variables','fail_on_missing_keyword').split(',')]
            
        plot_type = [x.strip() for x in qa_lookup(self.output_options,'plot_type','time slice').split(',')]   
        
        plot_error = qa_lookup(self.output_options,'plot_error',False)
        print_error = qa_lookup(self.output_options,'print_error',False)
        self.plot_to_screen = qa_lookup(self.output_options,'plot_to_screen',False)
        self.variable_units = qa_lookup(self.output_options,'variable_units',' ')

        for i in range(len(plot_type)):
            plot = plot_type[i]
            if plot == 'observation':                
                    
                locations = location_strings_to_float_list(self.output_options['locations'])
                self.x_string_observation = x_string[i]
                self.y_string_observation = y_string[i]
                self.plot_observation_file(locations,plot_error,print_error)

                
            elif plot=='time slice':

                times = time_strings_to_float_list(
                    qa_lookup(self.output_options,'times','fail_on_missing_keyword').split(','))
                
                self.x_string_time_slice = x_string[i]
                self.y_string_time_slice = y_string[i]
                self.plot_time_slice(times,plot_error,print_error)
                                
            else:
                print_err_msg('{} specified in output_options as plot_type not recognized. '
                              'Available options are: time slice or observation'.format(plot))
                              
        debug_pop()      
              
    def plot_time_slice(self,times,plot_error,print_error):
        debug_push('QACompareSolutions plot_time_slice')
               
        stat_files_by_var_dict = {}
        for time in times:
            plot_time_units = ''
            converted_time = -999.     
            if time < 0.: 
                # time < 0 indicates steady state
                if len(times) > 1:
                    print_err_msg('QACompareSolutions: Negative time in times '
                                  'array indicates steady state. Yet, there '
                                  'is more than one time.')
                doc_slice = QATestDocTimeSlice('steady state',plot_time_units)
            else:
                plot_time_units = self.output_options['plot_time_units']
                sec_over_tunits = unit_conversion(plot_time_units)
                converted_time = time/sec_over_tunits
                doc_slice = QATestDocTimeSlice(converted_time,plot_time_units)
            for variable in self.variables:
                doc_var = QATestDocVariable(variable)
            
                x_min = 1e20
                x_max = -1.e20
                y_min = 1e20
                y_max = -1.e20
                z_min = 1e20
                z_max = -1.e20
                s_min = 1e20
                s_max = -1.e20

                solution_handles = []
                solution = []
                isimulator = 0
              
                solutions = []
                x_loc = []
                y_loc = []
                z_loc = []
                              
                for simulator in self.mapped_simulator_names:

                    filename = self.solution_dictionary[simulator]
                    solution_object = QASolutionReader(filename)
                    x, y, z = solution_object.get_coordinates()

                    solution = solution_object.get_solution(time,variable,Time_Slice=True)
                    solution_object.destroy()
                    solution = solution.transpose()
               
                    if plot_error or print_error:

                        solutions.append(solution)
                        x_loc.append(x)
                        y_loc.append(y)
                        z_loc.append(z)
                        if len(solutions) > 2:
                            print('WARNING: More than two '
                                          'simulators run yet error set to True. '
                                          'Can only compare two solutions at a time.')

                    s_min = min(s_min,(np.amin(solution)))
                    s_max = max(s_max,(np.amax(solution)))
                
                    if self.plot_dimension == '1D':

                        if isimulator == 0:
                            plt.figure(figsize=(11,9))

                        x_axis = find_axis_1D(x,y,z)                       

                        x_min = min(x_min,math.floor(np.amin(x_axis)))
                        x_max = max(x_max,math.ceil(np.amax(x_axis)))
                        line, = plt.plot(x_axis,solution,
                                    label=simulator) 
                 
                        solution_handles.append(line)
                                            
                    elif self.plot_dimension == '2D':
                        x_axis, y_axis = find_axis_2D(x,y,z)
                        
                        x_min = min(x_min,math.floor(np.amin(x_axis)))
                        x_max = max(x_max,math.ceil(np.amax(x_axis)))
                        
                        y_min = min(y_min,math.floor(np.amin(y_axis)))
                        y_max = max(y_max,math.ceil(np.amax(y_axis)))
                        if isimulator == 0:
                            plt.figure(figsize=(8,6))
                            levels = np.linspace(s_min,s_max,11)
                            X,Y = np.meshgrid(x_axis,y_axis)
                            surface = plt.contourf(X,Y,solution[:,:],
                                                 levels,alpha=0.75)
                            x_axis_old=x_axis
                            y_axis_old=y_axis
                            #cbar = plt.colorbar()
                            if np.mean(solution[:,:]) < 1:
                                cbar = plt.colorbar(format='%.2e')
                  
                            if (np.mean(solution[:,:]) >= 1) and (np.mean(solution[:,:]) < 1000):
                                cbar = plt.colorbar(format='%.2f')
                                
                            if np.mean(solution[:,:] >= 1000):
                                cbar = plt.colorbar(format='%.2e')
                                
                            cbar.ax.tick_params(labelsize=14)
                            if self.variable_units == ' ':
                                cbar.set_label('{}'.format(variable),rotation=90,fontsize=16)
                            else:
                                cbar.set_label('{} [{}]'.format(variable,self.variable_units),rotation=90,fontsize=16)
                            fill_legend = '{} (fill)'.format(simulator)
                        else:
                            check_coordinates_2D(x_axis,x_axis_old,y_axis,y_axis_old)
                            surface = plt.contour(X,Y,solution[:,:],levels,
                                                colors='black',
                                                linewidth=0.5)
                            plt.clabel(surface,inline=True,fontsize=10)
                            contour_legend = '{} (contour)'.format(simulator)

                        solution_handles.append(surface)
                                                    
                    elif self.plot_dimension == '3D':

                        y_min = min(y_min,math.floor(np.amin(y)))
                        y_max = max(y_max,math.ceil(np.amax(y)))
                        z_min = min(z_min,math.floor(np.amin(z)))
                        z_max = max(z_max,math.ceil(np.amax(z)))

                        if isimulator == 0:
                            fig=plt.figure()
                            ax = fig.gca(projection='3d')
                            X,Y= np.meshgrid(x,y)
                            surface=ax.contourf(Y,X,solution[0,:,:],zdir='z',offset =z_max)
                            surface1=ax.contourf(Y,X,solution[1,:,:],zdir='z',offset =0)
                            surface1=ax.contourf(Y,X,solution[2,:,:],zdir='z',offset =0.2)
                            ax.set_zlim((0.,1.))
                            plt.colorbar(surface)
                        else:
                            surface=ax.contour(Y,X,solution[0,:,:],zdir='z',offset=z_max,colors='black')
                            plt.clabel(surface,inline=True,fontsize=18)
                    else:
                        print_err_msg('{} not recognized for plot_dimension in '
                                      'options file. Available options include: '
                                      '1D, 2D, or 3D')
                    isimulator += 1
                    
                ax = plt.gca()
                
                if self.plot_dimension == '1D': 
                    ###buffer is 5% of total axis on both sides
                    buffer=abs(x_max-x_min)*0.05 
                    plt.xlim([x_min-buffer,x_max+buffer])
                    buffer=abs(s_max-s_min)*0.05
                    plt.ylim([s_min-buffer,s_max+buffer])
                    plt.legend(handles=solution_handles,fontsize=14)
                    
                    if abs((s_max-s_min)/2.) < 1:
                        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
                        
                    if abs((s_max-s_min)/2.) >= 1 and abs((s_max-s_min)/2.) < 1000: 
                        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
          
                    if abs((s_max-s_min)/2.) > 1000:
                        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
                    
                elif self.plot_dimension == '2D':

                    placeholder = 1
                    
                
                plt.xlabel(self.x_string_time_slice,fontsize=16)
                plt.ylabel(self.y_string_time_slice,fontsize=16)
                
                ax.tick_params(labelsize=14)
                temp_title = self.title
                if not time < 0.:
                    plot_converted_time = format_floating_number(converted_time)
                    temp_title += ' @ {} {}'.format(plot_converted_time,plot_time_units)
                if self.plot_dimension == '2D':
                    plt.annotate('{} \n'                                 
                                 '{}, {} \n'.format(temp_title,fill_legend,contour_legend),                                
                                 xy=(.03, .990),
                                 xycoords='figure fraction',
                                 horizontalalignment='left',
                                 verticalalignment='top',fontsize=16)
                    
                else:
                    plt.annotate(temp_title, 
                                 xy=(.03, .990),
                                 xycoords='figure fraction',
                                 horizontalalignment='left',
                                 verticalalignment='top',fontsize=16)
                prefix = 'ss'
                if not time < 0.:
                    prefix = '{}'.format(converted_time)
                variable_string = variable.replace(" ","_")
                filename = '{}_{}_{}_run{}.png'.format(prefix,variable_string,
                               self.template,self.run_number) 
                doc_var.add_solution_png(filename)

                plt.savefig(filename)
                if self.plot_to_screen==True:
                    plt.show()
                plt.close()
              
                error = QATestError(prefix,variable,self.template,self.run_number,self.plot_to_screen,self.variable_units,False,self.plot_dimension)
                if plot_error:                                     
                    filename = error.plot_error(x_loc[0],y_loc[0],z_loc[0],solutions[0],x_loc[1],y_loc[1],z_loc[1],solutions[1],self.x_string_time_slice,self.y_string_time_slice)
                    doc_var.add_error_png(filename)
                if print_error:   
                    filename = error.print_error(x_loc[0],y_loc[0],z_loc[0],solutions[0],x_loc[1],y_loc[1],z_loc[1],solutions[1]) 
                    if variable in stat_files_by_var_dict.keys():
                        stat_files_by_var_dict[variable].append(filename)
                    else:
                        stat_files_by_var_dict[variable] = [filename]
                    doc_var.set_error_stat(filename)
                    
                doc_slice.add_variable(doc_var)
            self.doc_run.add_time_slice(doc_slice)
            
        if print_error:
            for variable in stat_files_by_var_dict.keys():
                error.calc_error_metrics_over_all_times(stat_files_by_var_dict[variable],plot_time_units)
                self.doc_run.add_max_absolute_error(variable, error)
                self.doc_run.add_max_relative_error(variable,error)
                self.doc_run.add_max_average_absolute_error(variable,error)
                self.doc_run.add_max_average_relative_error(variable,error)
     
                self.time_slice_error_solution_convergence = error.maximum_relative_error_all_times
        
        debug_pop()        
        
    def plot_observation_file(self,locations,plot_error,print_error):
        debug_push('QACompareSolutions plot_observation_file')
        
        stat_files_by_var_dict = {}
        for location in locations:
            location_string = '{}, {}, {}'.format(location[0],location[1],
                                                  location[2])
            doc_obs = QATestDocObservation(location_string)
            
            
            for variable in self.variables:
                doc_var = QATestDocVariable(variable) 
                t_min = 1e20
                t_max = -1e20
                s_min = 1e20
                s_max = -1.e20

                solution_handles = []
                isimulator = 0
              
                solutions = []
                times = []
              
                for simulator in self.mapped_simulator_names:
                    filename = self.solution_dictionary[simulator]

                    solution_object = QASolutionReader(filename)
                    time = solution_object.get_time()
                    time_unit = solution_object.get_time_unit()
                    
                    solution = solution_object.get_solution(location,variable,Observation=True)
                    solution_object.destroy()
                  
                    if plot_error or print_error:
                        solutions.append(solution)
                        times.append(time)
                        if len(solutions) > 2:
                            print('WARNING: More than two '
                                          'simulators run yet error set to True. '
                                          'Can only compare two solutions at a time.')
                 
                    t_min = min(t_min,(np.amin(time)))
                    t_max = max(t_max,(np.amax(time)))
                    s_min = min(s_min,(np.amin(solution)))
                    s_max = max(s_max,(np.amax(solution))) 
                    if isimulator == 0:
                        plt.figure(figsize=(12,8))
                    line, = plt.plot(time,solution,label=simulator)
                    solution_handles.append(line)
                  
                    isimulator += 1
                    
                ax = plt.gca() 
                ###buffer is 5% of total axis on both sides
                buffer=abs(t_max-t_min)*0.05 
                plt.xlim([t_min-buffer,t_max+buffer])
                buffer=abs(s_max-s_min)*0.05
                plt.ylim([s_min-buffer,s_max+buffer])
                plt.legend(handles=solution_handles)
                    
                if abs((s_max-s_min)/2.) < 1:
                    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
                        
                if abs((s_max-s_min)/2.) >= 1 and abs((s_max-s_min)/2.) < 1000: 
                    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
          
                if abs((s_max-s_min)/2.) > 1000:
                    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))

                plt.legend(handles=solution_handles,fontsize=14)
              
                plt.xlabel(self.x_string_observation, fontsize=16)
                plt.ylabel(self.y_string_observation, fontsize=16)
                
                ax.tick_params(labelsize=14)
                temp_title=  self.title+' '+location_string
                
                plt.annotate(temp_title, 
                             xy=(.03, .990),
                             xycoords='figure fraction',
                             horizontalalignment='left',
                             verticalalignment='top',fontsize=14)
                variable_string = variable.replace(" ","_")
                filename = '{}_{}_{}_{}_{}_run{}.png'.format(
                          location[0],location[1],location[2],variable_string,
                          self.template,self.run_number)
                doc_var.add_solution_png(filename)
                plt.savefig(filename)
                if self.plot_to_screen:
                    plt.show()
                plt.close()
                
                error = QATestError(location,variable,self.template,self.run_number,self.plot_to_screen,self.variable_units,observation=True)  
                if plot_error:                                     
                    filename = error.plot_error_1D(times[0],solutions[0],times[1],solutions[1],self.x_string_observation)
                    doc_var.add_error_png(filename)
                if print_error: 
                    filename = error.print_error_1D(times[0],solutions[0],times[1],solutions[1],time_unit)
                    if variable in stat_files_by_var_dict.keys():
                        stat_files_by_var_dict[variable].append(filename)
                    else:
                        stat_files_by_var_dict[variable] = [filename]
                    doc_var.set_error_stat(filename)
                    
                doc_obs.add_variable(doc_var)
            self.doc_run.add_observation(doc_obs)
        if print_error:
            for variable in stat_files_by_var_dict.keys():
                error.calc_error_metrics_over_all_locations(stat_files_by_var_dict[variable],time_unit) ##check correct time_unit
                self.doc_run.add_max_absolute_error_observation(variable,error)
                self.doc_run.add_max_relative_error_observation(variable,error)
                self.doc_run.add_max_average_absolute_error_observation(variable, error) 
                self.doc_run.add_max_average_relative_error_observation(variable, error)

                self.observation_error_solution_convergence = error.maximum_relative_error_all_locations

        debug_pop()
                
    def get_time_slice_max_error(self):
        error_solution_convergence = self.time_slice_error_solution_convergence.split()[0]
        return string_to_number(error_solution_convergence)
    
    def get_observation_max_error(self):
        try:
            error_solution_convergence = self.observation_error_solution_convergence.split()[0]
        except:
            print_err_msg('Observation comparison requested in solution convergence but no observation data recieved in options file')
        return string_to_number(error_solution_convergence)

