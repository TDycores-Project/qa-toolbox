import sys
import shutil

import h5py
import numpy as np

from qa_debug import *
from qa_common import *

eps = 1.e-6
eps_loc=1.e-3

class QASolutionWriter(object):

    def __init__(self,filename,time_unit=None,space_unit=None):
        debug_push('QASolutionWriter init')
        self._filename = filename
        self._f = h5py.File(filename,'w')
        self._tunit = 'y'
        if time_unit:
            self._tunit = time_unit
        self._sunit = 'm'
        if space_unit:
            self.sunit = space_unit
        debug_pop()

    def set_time_unit(self,time_unit):
        debug_push('QASolutionWriter set_time_unit')
        time_unit=time_unit.lower()
        if not time_unit in units_dict:
            print_err_msg('Unrecognized time unit: {}'.format(time_unit))

        self._tunit = time_unit
        debug_pop()
        
    def set_spatial_unit(self,space_unit):
        debug_push('QASolutionWriter set_space_unit')
        ####ever need unit conversion for spatial???
        self._sunit = space_unit
        debug_pop()

    def write_coordinates(self,x,y,z):
        debug_push('QASolutionWriter write_coordinates')
        # x, y, z are 1D numpy arrays
        group_name = 'Time Slice/Coordinates' 
        self._f[group_name+'/X'] = x
        self._f[group_name+'/Y'] = y
        self._f[group_name+'/Z'] = z
        ###add units??
        debug_pop()
        
    def write_time(self,t):
        debug_push('QASolutionWriter write_time')
        group_name = 'Observation/Time'
        self._f[group_name+'/times'] = t
        self._f[group_name].attrs['time unit'] = self._tunit   
        debug_pop()

        
    def write_dataset(self,dimension,soln,dataset_name,group='Time Slice'):
        debug_push('QASolutionWriter write_dataset')
        # if not 3D convert to 3D
        if soln.ndim == 1:
            soln = np.reshape(soln,(soln.shape[0],1,1))
        elif soln.ndim == 2:
            soln = np.reshape(soln,(soln.shape[0],soln.shape[1],1))
        dataset_name = dataset_name.replace('/','_')
        ###Change group names to 1 Time, 1 Location, 2 Time, 2 Location?
        if group == 'Time Slice':
            group_name = '{}/Time: {:9.3e} {}'.format(group,dimension,self._tunit)
            self._f[group_name+'/'+dataset_name] = soln
            self._f[group_name].attrs['time'] = '{}'.format(dimension)
            self._f[group_name].attrs['time unit'] = '{}'.format(self._tunit)
          
        elif group == 'Observation': 
            
            group_name = '{}/Location: {:9.3e} {:9.3e} {:9.3e} {}'.format(group, \
                        dimension[0],dimension[1],dimension[2],self._sunit)
            self._f[group_name+'/'+dataset_name] = soln
            self._f[group_name].attrs['location'] = '{} {} {}'.format(dimension[0], \
                                                  dimension[1],dimension[2])
            self._f[group_name].attrs['location unit'] = '{}'.format(self._sunit)
        else:
            print_err_msg('Unrecognized group "{}" in '.format(group),
                            'QASolutionWriter write_dataset. '
                            'Available groups include: Time Slice or Observation') 
        
        if debug_verbose():
            print(group_name+'/'+dataset_name)
        debug_pop()

    def destroy(self):
        debug_push('QASolutionWriter destroy')
        self._f.close()
        debug_pop()

class QASolutionReader(object):


    def __init__(self,filename,simulator=None):
        debug_push('QASolutionReader init')
        self._filename = filename
        try:
            self._f = h5py.File(filename,'a') ##better way?
        except:
            print_err_msg('Unable to open {}.'.format(filename))
        self._coordinates_group = None
        self._time_group = None
        self._time_slice_solutions = []
        self._observation_solutions=[]
        self._reading_custom_labels = False
        self._simulator = simulator
        
        self.process_groups()
        
        
        debug_pop()


        
    def process_groups(self): 
        debug_push('QASolutionReader process_groups')

        for key in list(self._f.keys()):
            if key.startswith('Time Slice'):
                for tkey in list(self._f[key].keys()):

                    if tkey.startswith('Coordinates'):
                        self._coordinates_group = self._f[key+'/'+tkey]
                    
                    elif key.startswith('Time'):
                        w = tkey.split()
                        time = float(w[1])
                        if len(w) > 1:
                            time *= unit_conversion(self._f[key+'/'+tkey].attrs['time unit'])
                        self._time_slice_solutions.append([time,self._f[key+'/'+tkey]])
                    else:
                        print_err_msg('Unrecognized key "{}" '.format(tkey),
                                        'in QASolutionReader process_groups/',
                                        'Solutions')
                if self._coordinates_group == None:
                    print_err_msg('No coordinates found in Time Slice h5 file {}'.format(self._filename))
                elif len(self._time_slice_solutions) == 0:
                    print_err_msg('No solutions found in Time Slice h5 file {}'.format(self._filename))
                    
            elif key.startswith('Observation'):
                for lkey in list(self._f[key].keys()):
                    if lkey.startswith('Time'):
                        self._time_group = self._f[key+'/'+lkey]
                    elif lkey.startswith('Location') and not self._reading_custom_labels:
                        w = lkey.split()    
                        location = [float(w[1]),float(w[2]),float(w[3])]  ###save with more precision??
                        self._observation_solutions.append([location,self._f[key+'/'+lkey]])
                    elif lkey.startswith('Label'):
                        w = lkey.split(':')
                        s = ', '

                        location = s.join(w[1:])#w#.strip()## what if has colon

                        self._observation_solutions.append([location,self._f[key+'/'+lkey]])
                        self._reading_custom_labels = True
#                    else:
#                        print_err_msg('Unrecognized key "{}" '.format(lkey),
#                                'in QASolutionReader process_groups/',
#                                'Solutions')
                        ###put this back in
                if self._observation_solutions == None:
                    print_err_msg('No time array found in Observation h5 file {}'.format(self._filename))
                elif len(self._observation_solutions)==0:
                    print_err_msg('No solutions found in Observation h5 file {}'.format(self._filename))
            else:
                print_err_msg('Unrecognized key "{}" in '.format(key),
                                'QASolutionReader process_groups')
            
        debug_pop()
        
    def get_coordinates(self):
        debug_push('QASolutionReader get_coordinates')
        x = None
        y = None
        z = None
        g = self._coordinates_group
        if self._coordinates_group == None:
            print_err_msg('Time Slice solution and coordinates not outputted by simulator in  h5 file {}'.format(self._filename))
        
        for key in list(g.keys()):
            if key.startswith('X'):
                x = np.array(g[key])
            elif key.startswith('Y'):
                y = np.array(g[key])
            elif key.startswith('Z'):
                z = np.array(g[key])
            else:
                print_err_msg('Unrecognized key in QASolution: get_coordinates h5 file {}'.format(self._filename))
        debug_pop()
        return x, y, z
    
    def get_time(self):
        debug_push('QASolutionReader get_time')
        g = self._time_group
        
        if g == None:
            print_err_msg('Observation point specified in options file but '
                          'was not outputted by simulator in h5 file {}'.format(self._filename))
        for key in list(g.keys()):  
            if key.startswith('times'):   ###ever be more than one times?
                t = np.array(g[key])   
            else:
                print_err_msg('Unrecognized key in QASolution: get_time')
        
        debug_pop()
        return t
                    
    def get_time_unit(self):
        ###for observation points only
        debug_push('QASolutionReader get_time_unit')
        
        g = self._time_group
        
        time_unit=g.attrs['time unit']
        
        debug_pop()
        
        return time_unit
        
    def diff_coordinates(self,x2,y2,z2):
        debug_push('QASolutionReader diff_coordinates')
        coord_eps = 1.e-10
        x,y,z = self.get_coordinates()
        if x.size == x2.size:
            for i in range(x.size):
                if abs(x[i]-x2[i]) > coord_eps:
                    raise Exception('X coordinate mismatch at {}'.format(i+1))
        else:
            raise Exception('X coordinate dimension mismatch: {} {}'.
                            format(x.size,x2.size))
        if y.size == y2.size:
            for i in range(y.size):
                if abs(y[i]-y2[i]) > coord_eps:
                    raise Exception('Y coordinate mismatch at {}'.format(i+1))
        else:
            raise Exception('Y coordinate dimension mismatch: {} {}'.
                            format(y.size,y2.size))
        if z.size == z2.size:
            for i in range(z.size):
                if abs(z[i]-z2[i]) > coord_eps:
                    raise Exception('Z coordinate mismatch at {}'.format(i+1))
        else:
            raise Exception('Z coordinate dimension mismatch: {} {}'.
                            format(z.size,z2.size))
        if debug_verbose():
            print('Coordinates match')
        debug_pop()
    
    def get_solution(self,dimension,variable,Observation=False,Time_Slice=False):
        debug_push('QASolutionReader get_solution')
        
        if Time_Slice==True:
            array = self.get_solution_3D(dimension,variable)
            if not array.ndim == 3:
                print_err_msg('Solutions read in QASolutionReader.get_solution ',
                                'must be 3D: {}'.format(array.ndim))
            sizex = array.shape[0]
            sizey = array.shape[1]
            sizez = array.shape[2]
            # array is 1D
            if sizex > 1 and sizey == 1 and sizez == 1:
                array = self.convert_to_1D(array,'X')
            elif sizex == 1 and sizey > 1 and sizez == 1:
                array = self.convert_to_1D(array,'Y')
            elif sizex == 1 and sizey == 1 and sizez > 1:
                array = self.convert_to_1D(array,'Z')
            # array is 2D
            elif sizex > 1 and sizey > 1 and sizez == 1:
                array = self.convert_to_2D(array,'XY')
            elif sizex > 1 and sizey == 1 and sizez > 1:
                array = self.convert_to_2D(array,'XZ')
            elif sizex == 1 and sizey > 1 and sizez > 1:
                array = self.convert_to_2D(array,'YZ')

        elif Observation == True:
            array = self.get_observation_solution(dimension,variable)            
            
        else:
            print_err_msg('Must specify observation or time slice in QASolutionReader get_solution')
        debug_pop()
        return array

            
    def get_observation_solution(self,location,variable):
        debug_push('QASolutionReader get_observation_solution')
        group = None
        
        available_locations = []
        for l, g in self._observation_solutions:
            available_locations.append(l)
            if self._reading_custom_labels:

                if location.strip() == l.strip():
                    group = g
            else:
                if ((abs(location[0]-l[0]) < eps_loc) and 
                    (abs(location[1]-l[1]) < eps_loc) and 
                    (abs(location[2]-l[2]) < eps_loc)):                   
                        group = g
              
        if (group==None): 
            print_err_msg('Location "{}" not found in Observation group in h5 file {}\n'.format(location,
                                    self._filename),'Available locations {}'.format(available_locations))
    
        variable_key = None

        for key in group.keys(): 
            if key.startswith(variable):
                variable_key = key
                break
        if not variable_key:
              print_err_msg('Variable "{}" specified in options file not found in Observation group in h5 file {}. Available variables include:{}'. \
                            format(variable,self._filename,list(group.keys())))
        array = np.array(group[variable_key])
        array = np.array(array[:,0,0])
#        print(array.shape)

        debug_pop()
        return array


    def change_observation_label(self):
        labels = []
        for l, g in self._observation_solutions:
            
            label = input("Label for {} {} {} observation point on {}:".format(l[0],l[1],l[2],self._simulator))
            if label != "skip":
                new_group = '/Observation/Label: {}'.format(label)
                old_group = '/Observation/Location: 2.490e+01 5.000e-01 5.000e+00 m'
                self._f[new_group] = g
#            del g old group still in ...figure out how to delete it so doesn't process it above
                labels.append(label) #error check if labels == none
        return labels

        
    def get_solution_3D(self,time,variable):
        debug_push('QASolutionReader get_solution_3D')
        group = None
        
        available_times = [] 
        for t, g in self._time_slice_solutions:
            available_times.append(t)
            # time < 0 indicates steady state; use first dataset
            if time < 0 or abs(time-t) < eps:
                group = g
        if not group:
            print_err_msg('Time "{}" specified in options file not found in Time Slice group in h5 file {}. '
                          'Available times: {}'.format(t,self._filename,available_times))

        variable_key = None

        for key in group.keys():

            if key.startswith(variable):
                variable_key = key
                break
        if not variable_key:
              print_err_msg('Variable "{}" specified in options file not found in Time Slice group in h5 file {}. Available variables include:{}'. \
                            format(variable,self._filename,list(group.keys())))

        array = np.array(group[variable_key])

        debug_pop()
        return array

    def get_solution_2D(self,time,variable,plane,isection=None):
        debug_push('QASolutionReader get_solution_2D')
        array = self.get_solution_3D(time,variable)
        array = self.convert_to_2D(array,plane,isection)
        debug_pop()
        return array

    def get_solution_1D(self,time,variable,direction,isection1=None,
                        isection2=None):
        debug_push('QASolutionReader get_solution_1D')
        array = self.get_solution_3D(time,variable)
        array = self.convert_to_1D(array,direction,isection1,isection2)
        debug_pop()
        return array

    def convert_to_2D(self,array,plane,isection=None):
        if isection == None:
            isection = 0
        if plane == 'XY':
            array = np.array(array[:,:,isection])
        elif plane == 'XZ':
            array = np.array(array[:,isection,:])
        elif plane == 'YZ':
            array = np.array(array[isection,:,:])
        else:
            raise Exception('Plane "{}" not recognized in convert_to_2D'. \
                            format(plane))
        return array

    def convert_to_1D(self,array,direction,isection1=None,isection2=None):
        if isection1 == None:
            isection1 = 0
        if isection2 == None:
            isection2 = 0
        if direction == 'X':
            array = np.array(array[:,isection1,isection2])
        elif direction == 'Y':
            array = np.array(array[isection1,:,isection2])
        elif direction == 'Z':
            array = np.array(array[isection1,isection2,:])
        else:
            raise Exception('Direction "{}" not recognized in convert_to_1D'. \
                            format(direction))
        return array

    def destroy(self):
        debug_push('QASolutionReader destroy')
        self._f.close()
        debug_pop()
        
