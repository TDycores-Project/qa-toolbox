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
  
    def plot_error(self,x1,y1,z1,values1,x2,y2,z2,values2,x_label='x',y_label='y',difference_string='all'):
        debug_push('QAPlotError init')

        if self.dimension == '1D':
            dimension1 = find_axis_1D(x1,y1,z1)
            ##print error
            dimension2 = find_axis_1D(x2,y2,z2)
                
            filename = self.plot_error_1D(dimension1,values1,dimension2,values2,x_label,difference_string)
            
        elif self.dimension == '2D':
            dimension1,dimension2 = find_axis_2D(x1,y1,z1)
                
            filename = self._plot_error_2D(dimension1,dimension2,values1,values2,x_label,y_label)
        
        debug_pop()
        return filename
        
        
    def plot_error_1D(self,times1,values1,times2,values2,x_label,difference_string='all'):
        [absolute_area,absolute_times,absolute_values] = self._calc_absolute_error(times1,values1,times2,values2,difference_string)
        [relative_times,relative_values] = self._calc_relative_error(times1,values1,times2,values2,difference_string)
      
        maximum_absolute_error = self._get_maximum_error(absolute_values)
        maximum_relative_error = self._get_maximum_error(relative_values)
      
        average_absolute_error = self._get_average_absolute_error(absolute_area,absolute_times)
        average_relative_error = self._calc_average_relative_error(relative_times,relative_values)
      
        f,ax = plt.subplots(2,1,figsize=(9,8))
        plt.subplots_adjust(hspace=0.5)

        ax[0].plot(absolute_times,absolute_values,marker='x')
        ax[1].plot(relative_times,relative_values*100,marker='x')
      
        ax[0].set_xlabel(x_label) 
        ax[0].set_ylabel('Absolute Error')
        ax[1].set_xlabel(x_label)
        ax[1].set_ylabel('Relative Error (%)')
      
        if abs(average_absolute_error) < 1:
#        ax[0].ticklabel_format(axis='y',style='scientific',scilimits=(0,0))
            ax[0].yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
        
        if abs(average_relative_error) < 1:
#        ax[1].ticklabel_format(axis='y',style='scientific',scilimits=(0,0))
            ax[1].yaxis.set_major_formatter(FormatStrFormatter('%.2e'))

        
        if (abs(average_absolute_error)) >= 1 and abs(average_absolute_error) < 1000: 
            ax[0].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
          
        if (abs(average_relative_error)) >= 1 and (abs(average_relative_error) < 1000):
            ax[1].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
          
        if abs(average_absolute_error) > 1000:
#        ax[0].ticklabel_format(axis='y',style='scientific',scilimits=(0,0))
            ax[0].yaxis.set_major_formatter(FormatStrFormatter('%.2e'))

          
        if abs(average_relative_error) >= 1000:
#        ax[1].ticklabel_format(axis='y',style='scientific',scilimits=(0,0))
            ax[1].yaxis.set_major_formatter(FormatStrFormatter('%.2e'))



      ###Make annotations better
      

        ax[0].annotate('Maximum Absolute Error = {:.2g} \n'    #update precision
                       'Average Absolute Error = {:.2g} \n'.format \
                       (maximum_absolute_error, average_absolute_error), 
                     xy=(.03, .940),
                     xycoords='figure fraction',
                     horizontalalignment='left',
                     verticalalignment='top',fontsize=10)

                      
        ax[1].annotate('Maximum Relative Error = {:.2g}% \n' 
                       'Average Relative Error = {:.2g}%'.format \
                       (maximum_relative_error*100, average_relative_error*100), 
                     xy=(.03, .48),
                     xycoords='figure fraction',
                     horizontalalignment='left',
                     verticalalignment='top',fontsize=10)

      

        
        f.suptitle(self.variable,fontsize=14)
        if self.observation == True:
            filename = '{}_{}_{}_{}_{}_run{}_error.png'.format(self.converted_time[0],self.converted_time[1],self.converted_time[2],self.variable,self.template,self.run_number)
        else:
            filename = '{}_{}_{}_run{}_error.png'.format(self.converted_time,self.variable,self.template,self.run_number)
        plt.savefig(filename)
        if self.plot_to_screen == True:
            plt.show()
        plt.close()
        return filename 

      
    def print_error(self,x1,y1,z1,values1,x2,y2,z2,values2):
        if self.dimension == '1D':
            dimension1 = find_axis_1D(x1,y1,z1)
            ##print error
            dimension2 = find_axis_1D(x2,y2,z2)
            ##print error

            filename = self.print_error_1D(dimension1,values1,dimension2,values2)
                        
        elif self.dimension=='2D':
            ###assume uniform same grid
            
            dimension1, dimension2 = find_axis_2D(x1,y1,z1)
    
            filename = self.print_error_2D(dimension1,dimension2,values1,values2)
            
        return filename
            
    def print_error_2D(self,dimension1,dimension2,values1,values2):
                
#        [absolute_error,relative_error,absolute_area,total_area]=self._calc_error_2D(dimension1,dimension2,values1,values2)
        
#        self.average_absolute_error = self._get_average_absolute_error_2D(absolute_area,total_area)
            
#        self.absolute_relative_area=self._calc_absolute_relative_error_2D(dimension1,dimension1,values1,absolute_area)

        self.calc_error_stats_2D(dimension1,dimension2,values1,values2)

        if self.observation == True:
            filename='{}_{}_{}_{}_{}_run{}_error.stat'.format(self.converted_time[0],self.converted_time[1],self.converted_time[2],self.variable,self.template,self.run_number)
        else:
            filename = '{}_{}_{}_run{}_error.stat'.format(self.converted_time,self.variable,self.template,self.run_number)
      
      ###save to write to text file
        with open(filename,'w') as f:
#          f.write('Absolute Relative Error = {} \n'.format(self.absolute_relative_error))
          f.write('Average Absolute Error = {} {} \n'.format(self.average_absolute_error, self.units))
          f.write('Average Relative Error = {} % \n'.format(self.average_relative_error*100.))
          f.write('Maximum Absolute Error = {} {} \n'.format(self.maximum_absolute_error, self.units)) ####MAKE APPLICABLE FOR OBSERVATION POINTS
          f.write('Maximum Relative Error = {} % \n'.format(self.maximum_relative_error*100.))
          f.write('X Location of Maximum Absolute Error = {} m \n'.format(self.maximum_absolute_error_location_x)) ##add unit --> do I want to save this in here?
          f.write('Y Location of Maximum Absolute Error = {} m \n'.format(self.maximum_absolute_error_location_y))
          f.write('X Location of Maximum Relative Error = {} m \n'.format(self.maximum_relative_error_location_x))
          f.write('Y Location of Maximum Relative Error = {} m \n'.format(self.maximum_relative_error_location_y))
      
        
        return filename
        
    def print_error_1D(self,dimension1,values1,dimension2,values2,time_unit= ' ', difference_string='all'):
        self.calc_error_stats_1D(dimension1,values1,dimension2,values2,difference_string)

        
        
        if self.observation == True:
            filename = '{}_{}_{}_{}_{}_run{}_error.stat'.format(self.converted_time[0],self.converted_time[1],self.converted_time[2],self.variable,self.template,self.run_number)
        else:
            filename = '{}_{}_{}_run{}_error.stat'.format(self.converted_time,self.variable,self.template,self.run_number)
      
      ###save to write to text file
        with open(filename,'w') as f:
#          f.write('Absolute Relative Error = {} \n'.format(self.absolute_relative_error))
          f.write('Average Absolute Error = {} {} \n'.format(self.average_absolute_error,self.units))
          f.write('Average Relative Error = {} % \n'.format(self.average_relative_error*100.))
          f.write('Maximum Absolute Error = {} {} \n'.format(self.maximum_absolute_error,self.units)) ####MAKE APPLICABLE FOR OBSERVATION POINTS
          f.write('Maximum Relative Error = {} % \n'.format(self.maximum_relative_error*100.))
          
          if self.observation == True:
              f.write('Time of Maximum Absolute Error = {} {} \n'.format(self.maximum_absolute_error_location,time_unit)) ##add unit --> do I want to save this in here?
              f.write('Time of Maximum Relative Error = {} {} \n'.format(self.maximum_relative_error_location,time_unit))
          else:
              f.write('Location of Maximum Absolute Error = {} m \n'.format(self.maximum_absolute_error_location)) ##add unit --> do I want to save this in here?
              f.write('Location of Maximum Relative Error = {} m \n'.format(self.maximum_relative_error_location))
        
        
        return filename
    
         

    def _NonOverlappingAreaOfNonIntersectingLines(self,tstart,tend,line1,line2):
        if tend <= tstart:
            if tend < tstart:
                print('Error in NonOverlappingAreaOfNonIntersectingLines:')
                print('  end time (%f) < start time (%f)' % (tend,tstart))
                exit(0)
            return 0.
        return abs((line1.ValueYAtX(tstart)+line1.ValueYAtX(tend))-
                   (line2.ValueYAtX(tstart)+line2.ValueYAtX(tend)))/2.*(tend-tstart)
        
        
    def _calc_relative_error(self,times1,values1,times2,values2,difference_string):  ##add 1D
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
       #  times3 = zeros(max(size1,size2),dtype='f8')
       #  values3 = zeros(max(size1,size2),dtype='f8')
        times3 = zeros(3,dtype='f8')
        values3 = zeros(3,dtype='f8')
       # Evaluate over segments between 0 and maximum time
        tstart = min_time
        i1 = 0
        i2 = 0
        count3 = 0

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
         #  times3 = zeros(max(size1,size2),dtype='f8')
         #  values3 = zeros(max(size1,size2),dtype='f8')
        times3 = zeros(3,dtype='f8')
        values3 = zeros(3,dtype='f8')
         # Evaluate over segments between 0 and maximum time
        tstart = min_time
        i1 = 0
        i2 = 0
        count3 = 0
        total_area = 0.
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
       
      
      
    def _calc_absolute_relative_error(self,times1,values1,absolute_difference_area):   ##how useful is this?
        times2 = times1
        values2 = zeros(len(values1))
        
        [solution_area,times3,values3] = self._calc_absolute_error(times1,values1,times2,values2,'all')

        if abs(solution_area) > 0:
            relative_error = absolute_difference_area / solution_area
        else:
            relative_error = 1.e20
        
        return relative_error
  
    
    def _calc_average_relative_error(self,relative_times,relative_values):
        #calculate average relative error given relative error
        times2 = relative_times
        values2 = zeros(len(relative_values))
        
        [relative_area,times3,values3] = self._calc_absolute_error(relative_times,relative_values,times2,values2,'all')

        average_relative_error = relative_area / (max(times3)-min(times3)) 

        
        return average_relative_error
    
    
    def _get_maximum_error(self,values):
        return amax(abs(values))
    
    def _get_index_max_error(self,values):
        index = unravel_index(argmax(abs(values)),values.shape)
        return index
    
    
    def _get_average_absolute_error(self,absolute_area,absolute_times):
        return absolute_area / (max(absolute_times)-min(absolute_times))
    
    
    def calc_error_stats_1D(self,times1,values1,times2,values2,difference_string='all'):
        [absolute_area,absolute_times,absolute_values] = self._calc_absolute_error(times1,values1,times2,values2,difference_string)
        [relative_times,relative_values] = self._calc_relative_error(times1,values1,times2,values2,difference_string)

        self.maximum_absolute_error = self._get_maximum_error(absolute_values)
        self.average_absolute_error = self._get_average_absolute_error(absolute_area,absolute_times)
        self.maximum_relative_error = self._get_maximum_error(relative_values)
        self.average_relative_error = self._calc_average_relative_error(relative_times,relative_values)
        
        self.absolute_relative_error = self._calc_absolute_relative_error(times1,values1,absolute_area)
        
        self.absolute_error = absolute_values
        self.relative_error = relative_values
        
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

       
    def _plot_error_2D(self,x,y,solution1,solution2,xlabel,ylabel):

        [absolute_error,relative_error,absolute_area,total_area] = self._calc_error_2D(x,y,solution1,solution2)
        
        maximum_absolute_error = self._get_maximum_error(absolute_error)
        maximum_relative_error = self._get_maximum_error(relative_error)
        
        average_absolute_error = self._get_average_absolute_error_2D(absolute_area,total_area)
        average_relative_error = self._calc_average_relative_error_2D(x,y,relative_error)
        
        X,Y = np.meshgrid(x,y)

        
        plt.figure(figsize=(11,10))
        plt.contourf(X,Y,absolute_error)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
#        plt.clabel(surface)
        plt.annotate('Maximum Absolute Error = {:.2g} \n'    #update precision
                       'Average Absolute Error = {:.2g} \n'.format \
                       (maximum_absolute_error, average_absolute_error), 
                     xy=(.03, .950),
                     xycoords='figure fraction',
                     horizontalalignment='left',
                     verticalalignment='top',fontsize=14)
        if abs(average_absolute_error) < 1:
            plt.colorbar(format='%.2e')
                
        if (abs(average_absolute_error)) >= 1 and abs(average_absolute_error < 1000): 
            plt.colorbar(format='%.2f')
          
        if abs(average_absolute_error > 1000):
            plt.colorbar(format='%.2e')


#        plt.colorbar(format='%.0e')
        plt.title(self.variable,fontsize=18)
        if self.plot_to_screen == True:
            plt.show()
        plt.close()

        
        plt.figure(figsize=(11,10))
        plt.contourf(X,Y,relative_error*100)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
#        plt.clabel(surface)
        plt.annotate('Maximum Relative Error = {:.2g}% \n'    #update precision
                       'Average Relative Error = {:.2g}% \n'.format \
                       (maximum_relative_error*100, average_relative_error*100), 
                     xy=(.03, .950),
                     xycoords='figure fraction',
                     horizontalalignment='left',
                     verticalalignment='top',fontsize=14)
        
        if abs(average_relative_error) < 1:
            plt.colorbar(format='%.2e')
                  
        if (abs(average_relative_error)) >= 1 and (abs(average_relative_error) < 1000):
            plt.colorbar(format='%.2f')
                             
        if abs(average_relative_error >= 1000):
            plt.colorbar(format='%.2e')
            
#        plt.colorbar(format='%.3e')
        plt.title(self.variable)
        filename = '{}_{}_{}_run{}_error.png'.format(self.converted_time,self.variable,self.template,self.run_number)
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

#        for i in range(len(x)):
#            for j in range(len(y)):
#                if i==0 and j==0:
#                    area_of_cell = ((abs(x[i+1]-x[i])/2)*2)*((abs(y[j+1]-y[j])/2)*2)   
#                elif i==(len(x)-1) and j==(len(y)-1):
#                    area_of_cell = ((abs(x[i]-x[i-1])/2)*2)*((abs(y[j]-y[j-1])/2)*2)
#                elif i==0 and j==(len(y)-1):
#                    area_of_cell = ((abs(x[i+1]-x[i])/2)*2)*((abs(y[j]-y[j-1])/2)*2)
#                elif i==(len(x)-1) and j==0:
#                    area_of_cell = ((abs(x[i]-x[i-1])/2)*2)*((abs(y[j+1]-y[j])/2)*2)
#                elif i==0:
#                    area_of_cell = ((abs(x[i+1]-x[i])/2)*2)*(abs(y[j+1]-y[j])/2+abs(y[j]-y[j-1])/2)
#                elif j==0:
#                    area_of_cell= (abs(x[i+1]-x[i])/2+abs(x[i]-x[i-1])/2)*((abs(y[j+1]-y[j])/2)*2)
#                elif i==(len(x)-1):
#                    area_of_cell = ((abs(x[i]-x[i-1])/2)*2)*(abs(y[j+1]-y[j])/2+abs(y[j]-y[j-1])/2)
#                elif j==(len(y)-1):
#                    area_of_cell = (abs(x[i+1]-x[i])/2+abs(x[i]-x[i-1])/2)*((abs(y[j]-y[j-1])/2)*2)
#                else:
#                    area_of_cell = (abs(x[i+1]-x[i])/2+abs(x[i]-x[i-1])/2)*(abs(y[j+1]-y[j])/2+abs(y[j]-y[j-1])/2)
#                    
#                
#                
#                total_error = total_error+abs(solution1[i][j]-solution2[i][j])*area_of_cell
#                total_area = total_area+area_of_cell

        total_absolute_error = abs(absolute_error).sum()*area_of_cell
        total_area = area_of_cell*len(x)*len(y)
        
        
        return absolute_error,relative_error,total_absolute_error,total_area
        
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
    #            for line in fin:

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

        ###save to write to text file
        ##key off regression test flag to write this?
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
    #            for line in fin:

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
            self.maximum_relative_error_time =' '
        
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


