import os
from sys import *
from math import *
from numpy import *

import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
   mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

from qa_debug import *
from qa_common import *


class QATestError(object):
    
    def __init__(self,converted_time=None,variable=None,template=None,
                 run_number=None,plot_to_screen=False,units=' ',
                 observation=False,dimension='1D'):
        debug_push('QATestError init')
        self.converted_time = converted_time
        self.variable = variable
        self.template = template
        self.run_number = run_number
        self.plot_to_screen = plot_to_screen
        self.dimension = dimension
        self.observation = observation
        self.units = units
        debug_pop()
    
    def _LineSegmentsIntersect(self,line1,line2,tstart,tend):
        if abs(line1.m-line2.m) > 1e-40:
            x = (line2.b-line1.b)/(line1.m-line2.m)
            if x >= tstart and x >= tstart and \
               x < tend and x < tend:
                return [True,x]
        return [False,-999.]
  
    def plot_error(self,dimension,values,analytical,x_label='x',y_label='y',difference_string='all'):
        debug_push('QAPlotError init')

        if self.dimension == '1D':
   #         dimension1 = find_axis_1D(x1,y1,z1)
   #         dimension2 = find_axis_1D(x2,y2,z2) find dimension ahead of this
                
            filename = self.plot_error_1D(dimension,values,analytical,x_label,difference_string)
            
        elif self.dimension == '2D':
        #    dimension1,dimension2 = find_axis_2D(x1,y1,z1)                
            filename = self._plot_error_2D(dimension,values[0],values[1],x_label,y_label)
        
        debug_pop()
        return filename
        
        
    def plot_error_1D(self,times,values,analytical,x_label,difference_string='all'):
        f,ax = plt.subplots(2,1,figsize=(11,9))  #9,8
        plt.subplots_adjust(hspace=0.5)

        if analytical:
            maximum_absolute_error = -999.0
            maximum_relative_error = 0.0
            absolute_area_total = 0.0
            absolute_time_span = 0.0
            relative_area_total = 0.0
            relative_time_span = 0.0
            for i in range(len(values)):
                [absolute_area,absolute_times,absolute_values] = self._calc_absolute_error(analytical[1],analytical[0],times[i],values[i],difference_string)
                [relative_times,relative_values] = self._calc_relative_error(analytical[1],analytical[0],times[i],values[i],difference_string)
                ax[0].plot(absolute_times,absolute_values,marker='x')
                ax[1].plot(relative_times,relative_values*100,marker='x')
                maximum_absolute_error_simulator = self._get_maximum_error(absolute_values)
                maximum_relative_error_simulator = self._get_maximum_error(relative_values)
                if maximum_absolute_error_simulator > maximum_absolute_error:
                    maximum_absolute_error = maximum_absolute_error_simulator
                if maximum_relative_error_simulator > maximum_relative_error:
                    maximum_relative_error = maximum_relative_error_simulator
                absolute_area_total = absolute_area_total + absolute_area
                absolute_time_span = absolute_time_span + (max(absolute_times)-min(absolute_times))
                [relative_area,relative_area_times]=self._calc_average_relative_error(relative_times,relative_values)
                relative_area_total = relative_area_total + relative_area
                relative_time_span = relative_time_span + (max(relative_area_times)-min(relative_area_times))
            average_absolute_error = self._get_average_absolute_error(absolute_area_total,absolute_time_span)
            average_relative_error = self._get_average_absolute_error(relative_area_total,relative_time_span) #change name of this function to be more general
        else:
            #error messaging if no analytical solution can only calculate error for 2 simulators
            [absolute_area,absolute_times,absolute_values] = self._calc_absolute_error(times[0],values[0],times[1],values[1],difference_string)
            [relative_times,relative_values] = self._calc_relative_error(times[0],values[0],times[1],values[1],difference_string)

            ax[0].plot(absolute_times,absolute_values,marker='x')
            ax[1].plot(relative_times,relative_values*100,marker='x')
            maximum_absolute_error = self._get_maximum_error(absolute_values)
            maximum_relative_error = self._get_maximum_error(relative_values)
      
            average_absolute_error = self._get_average_absolute_error(absolute_area,(max(absolute_times)-min(absolute_times)))
            [relative_area,relative_area_times] = self._calc_average_relative_error(relative_times,relative_values)
            average_relative_error = self._get_average_absolute_error(relative_area,(max(relative_area_times)-min(relative_area_times)))
              
      
        ax[0].set_xlabel(x_label,fontsize=14) 
        if self.units == ' ':
            ax[0].set_ylabel('Absolute Error',fontsize=14)
        else:
            ax[0].set_ylabel('Absolute Error [{}]'.format(self.units),fontsize=14)
        ax[1].set_xlabel(x_label,fontsize=14)
        ax[1].set_ylabel('Relative Error (%)',fontsize=14)
      
        if abs(average_absolute_error) < 1:
            ax[0].yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
        
        if abs(average_relative_error) < 1:
            ax[1].yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
        
        if (abs(average_absolute_error)) >= 1 and abs(average_absolute_error) < 1000: 
            ax[0].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
          
        if (abs(average_relative_error)) >= 1 and (abs(average_relative_error) < 1000):
            ax[1].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
          
        if abs(average_absolute_error) > 1000:
            ax[0].yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
          
        if abs(average_relative_error) >= 1000:
            ax[1].yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
      
        ax[0].annotate('Maximum Absolute Error = {:.2g} \n'    
                       'Average Absolute Error = {:.2g} \n'.format \
                       (maximum_absolute_error, average_absolute_error), 
                     xy=(.03, .940),
                     xycoords='figure fraction',
                     horizontalalignment='left',
                     verticalalignment='top',fontsize=14)


                      
        ax[1].annotate('Maximum Relative Error = {:.2g}% \n' 
                       'Average Relative Error = {:.2g}%'.format \
                       (maximum_relative_error*100, average_relative_error*100), 
                     xy=(.03, .48),
                     xycoords='figure fraction',
                     horizontalalignment='left',
                     verticalalignment='top',fontsize=14)

      
        ax[0].tick_params(labelsize=14)
        ax[1].tick_params(labelsize=14)
        
        f.suptitle(self.variable,fontsize=14)
        variable_string = self.variable.replace(" ","_")
        if self.observation == True:
            filename = '{}_{}_{}_{}_{}_run{}_error.png'.format(self.converted_time[0],self.converted_time[1],self.converted_time[2],variable_string,self.template,self.run_number)
        else:
            filename = '{}_{}_{}_run{}_error.png'.format(self.converted_time,variable_string,self.template,self.run_number)
        plt.savefig(filename)
        if self.plot_to_screen == True:
            plt.show()
        plt.close()
        return filename 
      
    def print_error(self,dimension,values,analytical):
        if self.dimension == '1D':
         #   dimension1 = find_axis_1D(x1,y1,z1)
         #   dimension2 = find_axis_1D(x2,y2,z2)

            filename = self.print_error_1D(dimension,values,analytical)
                        
        elif self.dimension=='2D':           
         #   dimension1, dimension2 = find_axis_2D(x1,y1,z1)
    
            filename = self.print_error_2D(dimension[0],dimension[1],values[0],values[1])
            
        return filename
            
    def print_error_2D(self,dimension1,dimension2,values1,values2):

        variable_string = self.variable.replace(" ","_")
        
        self.calc_error_stats_2D(dimension1,dimension2,values1,values2)

        if self.observation == True:
            filename='{}_{}_{}_{}_{}_run{}_error.stat'.format(self.converted_time[0],self.converted_time[1],self.converted_time[2],variable_string,self.template,self.run_number)
        else:
            filename = '{}_{}_{}_run{}_error.stat'.format(self.converted_time,variable_string,self.template,self.run_number)
      
      ###save to write to text file
        with open(filename,'w') as f:
          f.write('Average Absolute Error = {} {} \n'.format(self.average_absolute_error, self.units))
          f.write('Average Relative Error = {} % \n'.format(self.average_relative_error*100.))
          f.write('Maximum Absolute Error = {} {} \n'.format(self.maximum_absolute_error, self.units)) 
          f.write('Maximum Relative Error = {} % \n'.format(self.maximum_relative_error*100.))
          f.write('X Location of Maximum Absolute Error = {} m \n'.format(self.maximum_absolute_error_location_x)) 
          f.write('Y Location of Maximum Absolute Error = {} m \n'.format(self.maximum_absolute_error_location_y))
          f.write('X Location of Maximum Relative Error = {} m \n'.format(self.maximum_relative_error_location_x))
          f.write('Y Location of Maximum Relative Error = {} m \n'.format(self.maximum_relative_error_location_y))
              
        return filename
        
    def print_error_1D(self,dimension,values,analytical,time_unit = ' ', difference_string='all'):
        self.calc_error_stats_1D(dimension,values,analytical,difference_string)

        variable_string = self.variable.replace(" ","_")
        
        if self.observation == True:
            filename = '{}_{}_{}_{}_{}_run{}_error.stat'.format(self.converted_time[0],self.converted_time[1],self.converted_time[2],variable_string,self.template,self.run_number)
        else:
            filename = '{}_{}_{}_run{}_error.stat'.format(self.converted_time,variable_string,self.template,self.run_number)
      
      ###save to write to text file
        with open(filename,'w') as f:
          f.write('Average Absolute Error = {} {} \n'.format(self.average_absolute_error,self.units))
          f.write('Average Relative Error = {} % \n'.format(self.average_relative_error*100.))
          f.write('Maximum Absolute Error = {} {} \n'.format(self.maximum_absolute_error,self.units)) 
          f.write('Maximum Relative Error = {} % \n'.format(self.maximum_relative_error*100.))
          
          if self.observation == True:
              f.write('Time of Maximum Absolute Error = {} {} \n'.format(self.maximum_absolute_error_location,time_unit)) 
              f.write('Time of Maximum Relative Error = {} {} \n'.format(self.maximum_relative_error_location,time_unit))
          else:
              f.write('Location of Maximum Absolute Error = {} m \n'.format(self.maximum_absolute_error_location)) 
              f.write('Location of Maximum Relative Error = {} m \n'.format(self.maximum_relative_error_location))
                
        return filename
    
    def _NonOverlappingAreaOfNonIntersectingLines(self,tstart,tend,line1,line2):
#        if tend <= tstart:
#            if tend < tstart:
#                print('Error in NonOverlappingAreaOfNonIntersectingLines:')
#                print('  end time (%f) < start time (%f)' % (tend,tstart))
#                exit(0)
#            return 0.
        return abs((line1.ValueYAtX(tstart)+line1.ValueYAtX(tend))-
                   (line2.ValueYAtX(tstart)+line2.ValueYAtX(tend)))/2.*(tend-tstart)
  #combine from below... redundant code              
    def _calc_relative_error(self,times1,values1,times2,values2,difference_string):  
        difference_flag = 3
        if difference_string.startswith('first') or \
           difference_string.startswith('one'):
            difference_flag = 1
        elif difference_string.startswith('second') or \
             difference_string.startswith('two'):
            difference_flag = 2
        elif difference_string.startswith('all'):
            difference_flag = 4
        
        if times1.size != values1.size:
            print('Size of times1 (%d) does not match size of values1 (%d)' %
                  (times1.size,values1.size))
            exit(0)
        if times2.size != values2.size:
            print('Size of times1 (%d) does not match size of values1 (%d)' %
                  (times1.size,values1.size))
            exit(0)
   #     times1=abs(times1)
   #     times2=abs(times2)
        max_time = min(amax(times1),amax(times2))
        min_time = max(amin(times1),amin(times2))
        size1 = times1.size
        size2 = times2.size
        times3 = zeros(3,dtype='f8')
        values3 = zeros(3,dtype='f8')
       # Evaluate over segments between 0 and maximum time
        tstart = min_time
        i1 = 0
        i2 = 0
        count3 = 0
    #    times1 = times1[::-1]
        inds1=argsort(times1)
        inds2=argsort(times2)
        times1 = times1[inds1]
   #     values1 = values1[::-1]
        values1 = values1[inds1]
        times2=times2[inds2]
        values2=values2[inds2]
        while tstart < max_time:
            while tstart >= times1[i1+1]:
                i1 += 1
            while tstart >= times2[i2+1]:
                i2 += 1
            if i1+1 >= size1 and i2+1 >= size2:
                break
            tstart = max(times1[i1],times2[i2])
            tend = min(times1[i1+1],times2[i2+1])
         
            line1 = Line(times1[i1],values1[i1],times1[i1+1],values1[i1+1])
            line2 = Line(times2[i2],values2[i2],times2[i2+1],values2[i2+1])
                  
            # it is possible that three values could be appended
             # therefore, we increase size of count+3 is greater than existing size
            if count3+3 >= times3.size:
                times3.resize(times3.size*2)
                values3.resize(values3.size*2)
                # zero values beyond original values
                times3[count3:times3.size] = 0.
                values3[count3:values3.size] = 0.        
            if count3 == 0:
                times3[count3] = tstart
                if abs(line1.ValueYAtX(tstart)) > 0:
                    values3[count3] = (line2.ValueYAtX(tstart) - line1.ValueYAtX(tstart))/abs(line1.ValueYAtX(tstart))
                else:
                    values3[count3] = 1.e20
                count3 += 1
            [they_intersect,time_of_intersection] = \
                self._LineSegmentsIntersect(line1,line2,tstart,tend)
            if they_intersect:
                if difference_flag > 3:
                    times3[count3] = time_of_intersection
             
                    if abs(line1.ValueYAtX(time_of_intersection)) > 0:
                        values3[count3] = (line2.ValueYAtX(time_of_intersection) - \
                               line1.ValueYAtX(time_of_intersection))/abs(line1.ValueYAtX(time_of_intersection))
                    else:
                        values3[count3] = 1.e20
                    count3 += 1

            if difference_flag >= 3 or \
              (difference_flag == 1 and abs(tend-times1[i1+1]) < 1.e-20) or \
              (difference_flag == 2 and abs(tend-times2[i2+1]) < 1.e-20):
                times3[count3] = tend
           
                if abs(line1.ValueYAtX(tend)) > 0:
                    values3[count3] = (line2.ValueYAtX(tend) - line1.ValueYAtX(tend))/abs(line1.ValueYAtX(tend))
                else:
                    values3[count3] = 1.e20
                count3 += 1
            tstart = tend
        times3.resize(count3)
        values3.resize(count3)
       
        return times3,values3
        
    def _calc_absolute_error(self,times1,values1,times2,values2,difference_string):
        difference_flag = 3
        if difference_string.startswith('first') or \
            difference_string.startswith('one'):
            difference_flag = 1
        elif difference_string.startswith('second') or \
            difference_string.startswith('two'):
            difference_flag = 2
        elif difference_string.startswith('all'):
            difference_flag = 4
                      
        if times1.size != values1.size:
            print('Size of times1 (%d) does not match size of values1 (%d)' %
                 (times1.size,values1.size))
            exit(0)
        if times2.size != values2.size:
            print('Size of times1 (%d) does not match size of values1 (%d)' %
                 (times1.size,values1.size))
            exit(0)

        max_time = min(amax(times1),amax(times2))
        min_time = max(amin(times1),amin(times2))

        size1 = times1.size
        size2 = times2.size
        times3 = zeros(3,dtype='f8')
        values3 = zeros(3,dtype='f8')
         # Evaluate over segments between 0 and maximum time
        tstart = min_time
        i1 = 0
        i2 = 0
        count3 = 0
        total_area = 0.

        inds1=argsort(times1)
        inds2=argsort(times2)
        times1 = times1[inds1]
        values1 = values1[inds1]
        times2=times2[inds2]
        values2=values2[inds2]

        while tstart < max_time:

            while tstart >= times1[i1+1]:
                i1 += 1
            while tstart >= times2[i2+1]:

                i2 += 1
            if i1+1 >= size1 and i2+1 >= size2:
                break
            tstart = max(times1[i1],times2[i2])
            tend = min(times1[i1+1],times2[i2+1])

            segment_area = 0.
            line1 = Line(times1[i1],values1[i1],times1[i1+1],values1[i1+1])
            line2 = Line(times2[i2],values2[i2],times2[i2+1],values2[i2+1])

           # it is possible that three values could be appended
           # therefore, we increase size of count+3 is greater than existing size
            if count3+3 >= times3.size:
                times3.resize(times3.size*2)
                values3.resize(values3.size*2)
                 # zero values beyond original values
                times3[count3:times3.size] = 0.
                values3[count3:values3.size] = 0.        
            if count3 == 0:
                times3[count3] = tstart
                values3[count3] = line2.ValueYAtX(tstart) - line1.ValueYAtX(tstart)
                count3 += 1
            [they_intersect,time_of_intersection] = \
                self._LineSegmentsIntersect(line1,line2,tstart,tend)
            if they_intersect:

                segment1_area = \
                 self._NonOverlappingAreaOfNonIntersectingLines(tstart,time_of_intersection,
                                                 line1,line2)
                segment_area += segment1_area 

                if difference_flag > 3:
                    times3[count3] = time_of_intersection
                    values3[count3] = line2.ValueYAtX(time_of_intersection) - \
                                      line1.ValueYAtX(time_of_intersection)
                    count3 += 1
                segment2_area = \
                  self._NonOverlappingAreaOfNonIntersectingLines(time_of_intersection,tend,
                                                               line1,line2)
                segment_area += segment2_area

            else:
                segment_area += \
                  self._NonOverlappingAreaOfNonIntersectingLines(tstart,tend,line1,line2)
            total_area += segment_area

            if difference_flag >= 3 or \
              (difference_flag == 1 and abs(tend-times1[i1+1]) < 1.e-20) or \
              (difference_flag == 2 and abs(tend-times2[i2+1]) < 1.e-20):
                times3[count3] = tend
                values3[count3] = line2.ValueYAtX(tend) - line1.ValueYAtX(tend)
                count3 += 1
            tstart = tend
        times3.resize(count3)
        values3.resize(count3)
       
        return total_area,times3,values3
             
    def _calc_absolute_relative_error(self,times1,values1,absolute_difference_area):   
        times2 = times1
        values2 = zeros(len(values1))
        
        [solution_area,times3,values3] = self._calc_absolute_error(times1,values1,times2,values2,'all')

        if abs(solution_area) > 0:
            relative_error = absolute_difference_area / solution_area
        else:
            relative_error = 1.e20
        
        return relative_error
  
    #change to calculate relative area, or just put in relative area calculation, make one function
    def _calc_average_relative_error(self,relative_times,relative_values):
        #calculate average relative error given relative error
        times2 = relative_times
        values2 = zeros(len(relative_values))
        
        [relative_area,times3,values3] = self._calc_absolute_error(relative_times,relative_values,times2,values2,'all')
        
        return relative_area, times3

  #      average_relative_error = relative_area / (max(times3)-min(times3)) 
        
 #       return average_relative_error
        
    def _get_maximum_error(self,values):
        return amax(abs(values))
    
    def _get_index_max_error(self,values):
        index = unravel_index(argmax(abs(values)),values.shape)
        return index
        
    def _get_average_absolute_error(self,absolute_area,absolute_time_span):
        return absolute_area / (absolute_time_span)
        
    def calc_error_stats_1D(self,times,values,analytical,difference_string='all'):
        
        if analytical:
            self.maximum_absolute_error = -999.0
            self.maximum_relative_error = 0.0
            absolute_area_total = 0.0
            absolute_time_span = 0.0
            relative_area_total = 0.0
            relative_time_span = 0.0
            for i in range(len(values)):
                [absolute_area,absolute_times,absolute_values] = self._calc_absolute_error(analytical[1],analytical[0],times[i],values[i],difference_string)
                [relative_times,relative_values] = self._calc_relative_error(analytical[1],analytical[0],times[i],values[i],difference_string)
                maximum_absolute_error_simulator = self._get_maximum_error(absolute_values)
                maximum_relative_error_simulator = self._get_maximum_error(relative_values)
                if maximum_absolute_error_simulator > self.maximum_absolute_error:
                    self.maximum_absolute_error = maximum_absolute_error_simulator
                    maximum_absolute_error_index = self._get_index_max_error(absolute_values)
                    self.maximum_absolute_error_location = absolute_times[maximum_absolute_error_index]
                    #add in which simulator maybe....
                if maximum_relative_error_simulator > self.maximum_relative_error:
                    self.maximum_relative_error = maximum_relative_error_simulator
                    maximum_relative_error_index = self._get_index_max_error(relative_values)
                    self.maximum_relative_error_location = relative_times[maximum_relative_error_index]
                absolute_area_total = absolute_area_total + absolute_area
                absolute_time_span = absolute_time_span + (max(absolute_times)-min(absolute_times))
                [relative_area,relative_area_times]=self._calc_average_relative_error(relative_times,relative_values)
                relative_area_total = relative_area_total + relative_area
                relative_time_span = relative_time_span + (max(relative_area_times)-min(relative_area_times))
            self.average_absolute_error = self._get_average_absolute_error(absolute_area_total,absolute_time_span)
            self.average_relative_error = self._get_average_absolute_error(relative_area_total,relative_time_span) 
        else:
            [absolute_area,absolute_times,absolute_values] = self._calc_absolute_error(times[0],values[0],times[1],values[1],difference_string)
            [relative_times,relative_values] = self._calc_relative_error(times[0],values[0],times[1],values[1],difference_string)

            self.maximum_absolute_error = self._get_maximum_error(absolute_values)
            self.maximum_relative_error = self._get_maximum_error(relative_values)
            self.average_absolute_error = self._get_average_absolute_error(absolute_area,(max(absolute_times)-min(absolute_times)))
            [relative_area,relative_area_times] = self._calc_average_relative_error(relative_times,relative_values)
            self.average_relative_error = self._get_average_absolute_error(relative_area,(max(relative_area_times)-min(relative_area_times)))
#commented out below does not get used anywhere       
#        self.absolute_relative_error = self._calc_absolute_relative_error(times1,values1,absolute_area)
        
 #       self.absolute_error = absolute_values
 #       self.relative_error = relative_values
        
            maximum_absolute_error_index = self._get_index_max_error(absolute_values)
            maximum_relative_error_index = self._get_index_max_error(relative_values)
        
            self.maximum_absolute_error_location = absolute_times[maximum_absolute_error_index]
            self.maximum_relative_error_location = relative_times[maximum_relative_error_index]
                
    def calc_error_stats_2D(self,x,y,values1,values2,difference_string='all'):

        [absolute_error,relative_error,absolute_area,total_area] = self._calc_error_2D(x,y,values1,values2)
        
        self.maximum_absolute_error = self._get_maximum_error(absolute_error)
        self.maximum_relative_error = self._get_maximum_error(relative_error)
        
        self.average_absolute_error = self._get_average_absolute_error_2D(absolute_area,total_area)
        self.average_relative_error = self._calc_average_relative_error_2D(x,y,relative_error)

        self.absolute_relative_error = self._calc_absolute_relative_error_2D(x,y,values1,absolute_area)
       
        self.absolute_error = absolute_error
        self.relative_error = relative_error
        
        maximum_absolute_error_index = self._get_index_max_error(absolute_error)
        maximum_relative_error_index = self._get_index_max_error(relative_error)
        
        self.maximum_absolute_error_location_x = x[maximum_absolute_error_index[1]] 
        self.maximum_absolute_error_location_y = y[maximum_absolute_error_index[0]]
        
        self.maximum_relative_error_location_x = x[maximum_relative_error_index[1]] 
        self.maximum_relative_error_location_y = y[maximum_relative_error_index[0]]
        
    def _get_average_absolute_error_2D(self,absolute_area,total_area):
        return absolute_area/total_area
    
    def _calc_absolute_relative_error_2D(self,x,y,solution1,absolute_area):
        #calculate average relative error given relative error
        solution2 = zeros_like(solution1)
        
        [abs_error,rel_error,relative_area,total_area] = self._calc_error_2D(x,y,solution1,solution2)
        
        if (abs(relative_area)) > 0:
            absolute_relative_error = absolute_area/relative_area
        else:
            absolute_relative_error = 1e20
        
        return absolute_relative_error
     
    def _calc_average_relative_error_2D(self,x,y,relative_error):
        #calculate average relative error given relative error
        solution2 = zeros_like(relative_error)
        
        [abs_error,rel_error,relative_area,total_area] = self._calc_error_2D(x,y,relative_error,solution2)
        
        average_relative_error = relative_area / total_area
        
        return average_relative_error
      
    def _plot_error_2D(self,dimension,solution1,solution2,xlabel,ylabel):

        x = dimension[0]
        y = dimension[1]
        [absolute_error,relative_error,absolute_area,total_area] = self._calc_error_2D(x,y,solution1,solution2)
        
        maximum_absolute_error = self._get_maximum_error(absolute_error)
        maximum_relative_error = self._get_maximum_error(relative_error)
        
        average_absolute_error = self._get_average_absolute_error_2D(absolute_area,total_area)
        average_relative_error = self._calc_average_relative_error_2D(x,y,relative_error)
        
        X,Y = np.meshgrid(x,y)

        fig, ax = plt.subplots(2,1,figsize=(8,13))
        plt.subplots_adjust(hspace=0.5)

        c1 = ax[0].contourf(X,Y,absolute_error)
        ax[0].set_xlabel(xlabel,fontsize=14)
        ax[0].set_ylabel(ylabel,fontsize=14)

        ax[0].annotate('Maximum Absolute Error = {:.2g} \n'    

                       'Average Absolute Error = {:.2g} \n'.format \
                       (maximum_absolute_error, average_absolute_error), 
                     xy=(.03, .950),
                     xycoords='figure fraction',
                     horizontalalignment='left',
                     verticalalignment='top',fontsize=14)
        if abs(average_absolute_error) < 1:
            cbar = fig.colorbar(c1,format='%.2e',ax=ax[0])
                
        if (abs(average_absolute_error)) >= 1 and abs(average_absolute_error < 1000): 
            cbar = fig.colorbar(c1,format='%.2f',ax=ax[0])
          
        if abs(average_absolute_error > 1000):
            cbar = fig.colorbar(c1,format='%.2e',ax=ax[0])

        cbar.ax.tick_params(labelsize=14)
        if self.units == ' ':
            cbar.set_label('Absolute Error',rotation=90,fontsize=14)
        else:
            cbar.set_label('Absolute Error [{}]'.format(self.units),rotation=90,fontsize=14)

        c2= ax[1].contourf(X,Y,relative_error*100)
        ax[1].set_xlabel(xlabel,fontsize=14)
        ax[1].set_ylabel(ylabel,fontsize=14)

        ax[1].annotate('Maximum Relative Error = {:.2g}% \n'    #update precision
                       'Average Relative Error = {:.2g}% \n'.format \
                       (maximum_relative_error*100, average_relative_error*100), 
                     xy=(.03, .480),
                     xycoords='figure fraction',
                     horizontalalignment='left',
                     verticalalignment='top',fontsize=14)
        
        if abs(average_relative_error) < 1:
            cbar = fig.colorbar(c2,format='%.2e',ax=ax[1])
                  
        if (abs(average_relative_error)) >= 1 and (abs(average_relative_error) < 1000):
            cbar = fig.colorbar(c2,format='%.2f',ax=ax[1])
                             
        if abs(average_relative_error >= 1000):
            cbar = fig.colorbar(c2,format='%.2e',ax=ax[1])
            
        variable_string = self.variable.replace(" ","_")
            
        ax[0].tick_params(labelsize=14)
        ax[1].tick_params(labelsize=14)
                                    
        cbar.ax.tick_params(labelsize=14)
        cbar.set_label('Relative Error %',rotation=90,fontsize=14)

        plt.suptitle(self.variable,fontsize=14)

        filename = '{}_{}_{}_run{}_error.png'.format(self.converted_time,variable_string,self.template,self.run_number)
        plt.savefig(filename)
        if self.plot_to_screen == True:
            plt.show()
        plt.close()
        return filename
                
    def _calc_error_2D(self,x,y,solution1,solution2):
        absolute_error = solution1-solution2
        
        ###take into account if solution 1 is zero
        relative_error = (solution1-solution2)/solution1

        ####assume uniform structured grid and we are inputting cell centered coordinates
                
        area_of_cell = abs(x[-1]+x[0])/len(x)*abs(y[-1]+y[0])/len(y)

        total_absolute_error = abs(absolute_error).sum()*area_of_cell
        total_area = area_of_cell*len(x)*len(y)
                
        return absolute_error,relative_error,total_absolute_error,total_area


####diff class?
class QATestErrorCompile():
    def __init__(self,template,run_number,variable,units=' ',dimension='1D'):
        debug_push('QATestErrorCompile init')
        self.variable = variable
        self.template = template
        self.run_number = run_number
        self.dimension = dimension
        self.units = units
        debug_pop()
        
    def calc_error_metrics_over_all_times(self,stat_file,tunit):
        
        if self.dimension == '1D':
            self._calc_error_metrics_over_all_times_1D(stat_file,tunit)
            
        elif self.dimension == '2D':
            self._calc_error_metrics_over_all_times_2D(stat_file,tunit)
                    
    def _calc_error_metrics_over_all_times_1D(self,stat_file,tunit):
           
        maximum_absolute_error = []
        maximum_relative_error = []
        average_absolute_error = []
        average_relative_error = []
        maximum_absolute_error_location = []
        maximum_relative_error_location = []
        times = []
           
        for i in range(len(stat_file)):

            filename = stat_file[i]

            if len(tunit) > 0:
                split_filename = filename.split('_')
                times.append(float(split_filename[0]))

            fin = open(stat_file[i],'r')
            for line in fin:
                words = line.strip().split()

                index = words.index('=')+1
                value = float(words[index])
                if ('Maximum' in words):
                    if ('Absolute' in words):
                        if ('Location' in words):
                            maximum_absolute_error_location.append(value)
                        else:
                            maximum_absolute_error.append(value)
                    elif ('Relative' in words):
                        if ('Location' in words):
                            maximum_relative_error_location.append(value)
                        else:
                            maximum_relative_error.append(value)                
            
                elif ('Average' in words):
                    if ('Absolute' in words):
                        average_absolute_error.append(value)
                    elif ('Relative' in words):
                        average_relative_error.append(value)

        maximum_absolute_error_all_times = max(maximum_absolute_error)
        index = argmax(maximum_absolute_error) 
        self.maximum_absolute_error_index = index
        
        maximum_absolute_error_location_all_times = maximum_absolute_error_location[index]
        if len(tunit) > 0:
            maximum_absolute_error_time = times[index]
            self.maximum_absolute_error_time = '{} {}'.format(maximum_absolute_error_time,tunit)
        else:
            self.maximum_absolute_error_time = ' '
        
        maximum_relative_error_all_times = max(maximum_relative_error)
        index = argmax(maximum_relative_error)
        self.maximum_relative_error_index = index
        
        maximum_relative_error_location_all_times = maximum_relative_error_location[index]
        if len(tunit) > 0:
            maximum_relative_error_time = times[index]
            self.maximum_relative_error_time = '{} {}'.format(maximum_relative_error_time,tunit)
        else:
            self.maximum_relative_error_time = ' '
        
        maximum_average_absolute_error = max((average_absolute_error))
        index = argmax(average_absolute_error)
        self.maximum_average_absolute_error_index = index
        
        if len(tunit) > 0:
            maximum_average_absolute_error_time = times[index]
            self.maximum_average_absolute_error_time = '{} {}'.format(maximum_average_absolute_error_time,tunit)
        else:
            self.maximum_average_absolute_error_time = ' '
        
        maximum_average_relative_error = max((average_relative_error))
        index = argmax(average_relative_error)
        self.maximum_average_relative_error_index = index
        
        if len(tunit) > 0:
            maximum_average_relative_error_time = times[index]
            self.maximum_average_relative_error_time = '{} {}'.format(maximum_average_relative_error_time,tunit)
        else:
            self.maximum_average_relative_error_time = ' '
        
        filename = '{}_{}_run{}_error_documentation.stat'.format(self.variable,self.template,self.run_number)
      
        self.maximum_absolute_error_all_times = '{} {}'.format(maximum_absolute_error_all_times,self.units)
        self.maximum_absolute_error_location_all_times = '{} m'.format(maximum_absolute_error_location_all_times)
        
        self.maximum_relative_error_all_times = '{} %'.format(maximum_relative_error_all_times)
        self.maximum_relative_error_location_all_times = '{} m'.format(maximum_relative_error_location_all_times)
        
        self.maximum_average_absolute_error = '{} {}'.format(maximum_average_absolute_error,self.units)
        
        self.maximum_average_relative_error = '{} %'.format(maximum_average_relative_error)

        with open(filename,'w') as f:
            f.write('Maximum Absolute Error = {} \n'.format(self.maximum_absolute_error_all_times))
            if len(tunit) > 0:
                f.write('Time = {} \n'.format(self.maximum_absolute_error_time))
            f.write('Location = {} \n'.format(self.maximum_absolute_error_location_all_times))
            f.write('Maximum Relative Error = {} \n'.format(self.maximum_relative_error_all_times))
            if len(tunit) > 0:
                f.write('Time = {} \n'.format(self.maximum_relative_error_time))
            f.write('Location = {} \n'.format(self.maximum_relative_error_location_all_times))
            f.write('Maximum Average Absolute Error = {} \n'.format(self.maximum_average_absolute_error))
            if len(tunit) > 0:
                f.write('Time = {} \n'.format(self.maximum_average_absolute_error_time))
            f.write('Maximum Average Relative Error = {} \n'.format(self.maximum_average_relative_error))
            if len(tunit) > 0:
                f.write('Time = {} \n'.format(self.maximum_average_relative_error_time))
        
    def _calc_error_metrics_over_all_times_2D(self,stat_file,tunit):
           
        maximum_absolute_error = []
        maximum_relative_error = []
        average_absolute_error = []
        average_relative_error = []
        maximum_absolute_error_location_x = []
        maximum_absolute_error_location_y = []
        maximum_relative_error_location_x = []
        maximum_relative_error_location_y = []
        times = []
                   
        for i in range(len(stat_file)):
            filename = stat_file[i]

            if len(tunit) > 0:
                split_filename = filename.split('_')
                times.append(float(split_filename[0]))

            fin = open(stat_file[i],'r')
            for line in fin:
                words = line.strip().split()
                
                index = words.index('=')+1
                value = float(words[index])
                if ('Maximum' in words):
                    if ('Absolute' in words):
                        if ('X' in words):
                            maximum_absolute_error_location_x.append(value)
                        elif ('Y' in words):
                            maximum_absolute_error_location_y.append(value)
                        else:
                            maximum_absolute_error.append(value)
                    elif ('Relative' in words):
                        if ('X' in words):
                            maximum_relative_error_location_x.append(value)
                        elif ('Y' in words):
                            maximum_relative_error_location_y.append(value)
                        else:
                            maximum_relative_error.append(value)
                            
                elif ('Average' in words):
                    if ('Absolute' in words):
                        average_absolute_error.append(value)
                    elif ('Relative' in words):
                        average_relative_error.append(value)

        maximum_absolute_error_all_times = max(maximum_absolute_error)
        index = argmax(maximum_absolute_error)       
        self.maximum_absolute_error_index = index
        
        maximum_absolute_error_x_location_all_times = maximum_absolute_error_location_x[index]
        maximum_absolute_error_y_location_all_times = maximum_absolute_error_location_y[index]
        if len(tunit) > 0:
            maximum_absolute_error_time = times[index]
            self.maximum_absolute_error_time = '{} {}'.format(maximum_absolute_error_time,tunit)
        else:
            self.maximum_absolute_error_time = ' '
        
        maximum_relative_error_all_times = max(maximum_relative_error)
        index = argmax(maximum_relative_error)
        self.maximum_relative_error_index = index
        
        maximum_relative_error_x_location_all_times = maximum_relative_error_location_x[index]
        maximum_relative_error_y_location_all_times = maximum_relative_error_location_y[index]
        
        if len(tunit) > 0:
            maximum_relative_error_time = times[index]
            self.maximum_relative_error_time = '{} {}'.format(maximum_relative_error_time,tunit)
        else:
            self.maximum_relative_error_time = ' '
        
        maximum_average_absolute_error = max((average_absolute_error))
        index = argmax(average_absolute_error)
        self.maximum_average_absolute_error_index = index
        
        if len(tunit) > 0:
            maximum_average_absolute_error_time = times[index]
            self.maximum_average_absolute_error_time = '{} {}'.format(maximum_average_absolute_error_time,tunit)
        else:
            self.maximum_average_absolute_error_time = ' '
        
        maximum_average_relative_error = max((average_relative_error))
        index = argmax(average_relative_error)
        self.maximum_average_relative_error_index = index
        
        if len(tunit) > 0:
            maximum_average_relative_error_time = times[index]
            self.maximum_average_relative_error_time = '{} {}'.format(maximum_average_relative_error_time, tunit)
        else:
            self.maximum_average_relative_error_time = ' '
                
        self.maximum_absolute_error_all_times = '{} {}'.format(maximum_absolute_error_all_times, self.units)
        self.maximum_absolute_error_location_all_times = '({} m, {} m)'.format(maximum_absolute_error_x_location_all_times,maximum_absolute_error_y_location_all_times)
        
        self.maximum_relative_error_all_times = '{} %'.format(maximum_relative_error_all_times)
        self.maximum_relative_error_location_all_times = '({} m, {} m)'.format(maximum_relative_error_x_location_all_times,maximum_relative_error_y_location_all_times)
        
        self.maximum_average_absolute_error = '{} {}'.format(maximum_average_absolute_error,self.units)
        
        self.maximum_average_relative_error = '{} %'.format(maximum_average_relative_error)
        
        filename = '{}_{}_run{}_error_documentation.stat'.format(self.variable,self.template,self.run_number)
      
      ###save to write to text file
        with open(filename,'w') as f:
            f.write('Maximum Absolute Error = {} \n'.format(self.maximum_absolute_error_all_times))
            if len(tunit) > 0:
                f.write('Time = {} \n'.format(self.maximum_absolute_error_time))
            f.write('Location = {} \n'.format(self.maximum_absolute_error_location_all_times))
            f.write('Maximum Relative Error = {} \n'.format(self.maximum_relative_error_all_times))
            if len(tunit) > 0:
                f.write('Time = {} \n'.format(self.maximum_relative_error_time))
            f.write('Location = {} \n'.format(self.maximum_relative_error_location_all_times))
            f.write('Maximum Average Absolute Error = {} \n'.format(self.maximum_average_absolute_error))
            if len(tunit) > 0:
                f.write('Time = {} \n'.format(self.maximum_average_absolute_error_time))
            f.write('Maximum Average Relative Error = {} \n'.format(self.maximum_average_relative_error))
            if len(tunit) > 0:
                f.write('Time = {} \n'.format(self.maximum_average_relative_error_time))
    
    def calc_error_metrics_over_all_locations(self,stat_file,tunit):
           
        maximum_absolute_error = []
        maximum_relative_error = []
        average_absolute_error = []
        average_relative_error = []
        maximum_absolute_error_time = []
        maximum_relative_error_time = []
        
        x_locations = []
        y_locations = []
        z_locations = []
           
        for i in range(len(stat_file)):

            filename = stat_file[i]
            
            split_filename = filename.split('_')
            x_locations.append(float(split_filename[0]))
            y_locations.append(float(split_filename[1]))
            z_locations.append(float(split_filename[2]))

            fin = open(stat_file[i],'r')
            for line in fin:
                words = line.strip().split()

                index = words.index('=')+1
                value = float(words[index])
                if ('Maximum' in words):
                    if ('Absolute' in words):
                        if ('Time' in words):
                            maximum_absolute_error_time.append(value)
                        else:
                            maximum_absolute_error.append(value)
                    elif ('Relative' in words):
                        if ('Time' in words):
                            maximum_relative_error_time.append(value)
                        else:
                            maximum_relative_error.append(value)
                            
                elif ('Average' in words):
                    if ('Absolute' in words):
                        average_absolute_error.append(value)
                    elif ('Relative' in words):
                        average_relative_error.append(value)


        maximum_absolute_error_all_locations = max(maximum_absolute_error)
        index = argmax(maximum_absolute_error)  
        self.maximum_absolute_error_observation_index = index
        
        maximum_absolute_error_time_all_locations = maximum_absolute_error_time[index]
        
        maximum_absolute_error_x_location = x_locations[index]
        maximum_absolute_error_y_location = y_locations[index]
        maximum_absolute_error_z_location = z_locations[index]
        
        
        maximum_relative_error_all_locations = max(maximum_relative_error)
        index = argmax(maximum_relative_error)
        self.maximum_relative_error_observation_index = index
        
        maximum_relative_error_time_all_locations = maximum_relative_error_time[index]
        maximum_relative_error_x_location = x_locations[index]
        maximum_relative_error_y_location = y_locations[index]
        maximum_relative_error_z_location = z_locations[index]

        
        maximum_average_absolute_error = max((average_absolute_error))
        index = argmax(average_absolute_error)
        self.maximum_average_absolute_error_observation_index = index
        
        maximum_average_absolute_error_x_location = x_locations[index]
        maximum_average_absolute_error_y_location = y_locations[index]
        maximum_average_absolute_error_z_location = z_locations[index]
        
        maximum_average_relative_error = max((average_relative_error))
        index = argmax(average_relative_error)
        self.maximum_average_relative_error_observation_index = index
        
        maximum_average_relative_error_x_location = x_locations[index]
        maximum_average_relative_error_y_location = y_locations[index]
        maximum_average_relative_error_z_location = z_locations[index]
        
        self.maximum_absolute_error_all_locations = '{} {} \n'.format(maximum_absolute_error_all_locations,self.units)
        self.maximum_absolute_error_time_all_locations = '{} {}'.format(maximum_absolute_error_time_all_locations, tunit)
        self.maximum_absolute_error_locations = '{},{},{}'.format(maximum_absolute_error_x_location,maximum_absolute_error_y_location,maximum_absolute_error_z_location)
        
        self.maximum_relative_error_all_locations = '{} %'.format(maximum_relative_error_all_locations)
        self.maximum_relative_error_time_all_locations ='{} {}'.format(maximum_relative_error_time_all_locations,tunit)
        self.maximum_relative_error_locations = '{},{},{}'.format(maximum_relative_error_x_location,maximum_relative_error_y_location,maximum_relative_error_z_location)
        
        self.maximum_average_absolute_error_observation = '{} {}'.format(maximum_average_absolute_error, self.units)
        self.maximum_average_absolute_error_location = '{},{},{}'.format(maximum_average_absolute_error_x_location,maximum_average_absolute_error_y_location,maximum_average_absolute_error_z_location)
        
        self.maximum_average_relative_error_observation = '{} {}'.format(maximum_average_relative_error,self.units)
        self.maximum_average_relative_error_location = '{},{},{}'.format(maximum_average_relative_error_x_location,maximum_average_relative_error_y_location,maximum_average_relative_error_z_location)
        
        filename = '{}_{}_run{}_observation_error_documentation.stat'.format(self.variable,self.template,self.run_number)
      
      ###save to write to text file
        with open(filename,'w') as f:
            f.write('Maximum Absolute Error = {} \n'.format(self.maximum_absolute_error_all_locations))
            f.write('Location = {} \n'.format(self.maximum_absolute_error_locations))
            f.write('Time = {} \n'.format(self.maximum_absolute_error_time_all_locations))
            f.write('Maximum Relative Error = {} \n'.format(self.maximum_relative_error_all_locations))
            f.write('Location = {} \n'.format(self.maximum_relative_error_locations))
            f.write('Time = {} \n'.format(self.maximum_relative_error_time_all_locations))
            f.write('Maximum Average Absolute Error = {} \n'.format(self.maximum_average_absolute_error_observation))
            f.write('Location = {} \n'.format(self.maximum_average_absolute_error_location))
            f.write('Maximum Average Relative Error = {} \n'.format(maximum_average_relative_error,self.units))
            f.write('Location = {} \n'.format(self.maximum_average_relative_error_location))    

        

class Line:
  '''Based on the equation for a line y = mx + b where m is the slope and
     b is the y intercept at x = 0.
     '''
  def __init__(self,x1,y1,x2,y2):
      self.xstart = x1
      self.xend = x2
      self.ystart = y1
      self.yend = y2
      x2mx1 = x2-x1
      # avoid divide by zero
      if abs(x2mx1) > 0.:
          self.m = (y2-y1)/x2mx1
      else:
          self.m = 1.e20
      self.b = y1-self.m*x1
      
  def ValueYAtX(self,x):
      return self.m*x+self.b


