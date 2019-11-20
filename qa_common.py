# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 09:41:07 2018

@author: gehammo
"""
import re
import sys
import numpy as np

from qa_debug import *

header_ = re.compile('-')

units_dict = {}
units_dict['y'] = 3600.*24.*365.
units_dict['yr'] = units_dict['y']
units_dict['yrs'] = units_dict['y']
units_dict['year'] = units_dict['y']
units_dict['years'] = units_dict['y']
units_dict['mo'] = units_dict['y']/12.
units_dict['month'] = units_dict['mo']
units_dict['d'] = 3600.*24.
units_dict['day'] = units_dict['d']
units_dict['h'] = 3600.
units_dict['hr'] = units_dict['h']
units_dict['hour'] = units_dict['h']
units_dict['m'] = 60.
units_dict['min'] = units_dict['m']
units_dict['minute'] = units_dict['m']
units_dict['s'] = 1.
units_dict['sec'] = units_dict['s']
units_dict['second'] = units_dict['s']

def dict_to_string(dictionary):
    string = ''
    for key, value in dictionary.items():
        string += '      {0} : {1}\n'.format(key,value)
    return string
  
def list_to_string(list_):
    return ','.join(list_)
    
def time_strings_to_float_list(strings):
    list_of_times = []
    for string in strings:
        
        try:
            w = string.split()
            
            # time in seconds
            time = float(w[0])
            if len(w) > 1:
                time *= unit_conversion(w[1])
        except:
            print('error converting float in list_to_floats')
            raise
        list_of_times.append(time)
    return list_of_times

def time_strings_to_float_list_for_documentation(strings):
    list_of_times = []
    for string in strings:
        
        try:
            w = string.split()
            
            # time in seconds
            time = float(w[0])
        except:
            print('error converting float in list_to_floats')
            raise
        list_of_times.append(time)
    return list_of_times

def location_strings_to_float_list(loc):
    
    locations=[x.strip() for x in loc.split(',')]  
    
    list_of_locations=[]
    for i in range(len(locations)):
        w = locations[i].split()
        w = [float(n) for n in w]
        list_of_locations.append(w)
    return list_of_locations
    
def unit_conversion(string):
    # scales to seconds
    scale = 1.
    if string.startswith('y'):
        scale = 3600.*24.*365.
    elif string.startswith('mo'):
        scale = 3600.*24.*365./12.
    elif string.startswith('d'):
        scale = 3600.*24.
    elif string.startswith('h'):
        scale = 3600.
    elif string.startswith('m'):
        scale = 60.
    elif string.startswith('s'):
        scale = 1.
    else:
        print('error converting time units: {}'.format(string))
        raise
    return scale
    
  
def list_to_dict(input_list):
    """Converts list of items to a dict"""
    debug_push('list_to_dict')
    dictionary = {}
    for item in input_list:
        dictionary[item[0]] = item[1]
    debug_pop()
    return dictionary
    
def print_header(char,title):
    string = '---------------------------------------------------------'
    string=header_.sub(char,string)
    tab = 15
    clip_len = 78-len(title)-tab-2
    print('\n {} {} {} \n'.format(string[:tab],title,string[:clip_len]))
    
def string_to_number(string):
    try:
        number = int(string)
    except:
        try:
            number = float(string)
        except:        
            print('cannot use a string for values in options')
            sys.exit(0)
    return number


def exponent_conversion(s):
    try:
        val = float(s)
    except ValueError:
        s = s.replace('+', 'E+').replace('-', 'E-')
    return s

def get_h5_output_filename(input_filename,simulator_name):
    strings = []
    strings.append(input_filename.rsplit('.',1)[0])
    if len(simulator_name) > 1:
        strings.append('_')
        strings.append(simulator_name)
    strings.append('.h5')
    return ''.join(strings)

def qa_lookup(dictionary,keyword,default_value):
    value = default_value
    
    if keyword in dictionary:
      value = dictionary[keyword]
    else:
        if default_value == "fail_on_missing_keyword":
            print_err_msg('Need to specify {} in options file'.format(keyword))
    if value == 'True':
      value = True
    elif value == 'False':
      value = False
      
    return value

def find_axis_1D(x,y,z):
    x_axis = None
    if len(x) > 1:
        if check_array_equal(x)==False:
            x_axis = x
    elif len(y)>1:
        if check_array_equal(x)==False:
            x_axis = y
    elif len(z)>1:
        if check_array_equal(x)==False:
            x_axis = z
    try:   
        if x_axis == None:
            raise Exception('Invalid coordinates, check x,y, and z') ###better error message here
    except:    
        return x_axis


def find_axis_2D(x,y,z):
#    x_axis = None
 #   y_axis = None
    
    if len(x) == 1:
        x_axis = y
        y_axis = z
    elif len(y)==1:
        x_axis = x
        y_axis = z
    elif len(z)==1:
        x_axis = x
        y_axis = y
        
#    if x_axis == None and y_axis == None:
#        raise Exception('Invalid coordinates, check x,y, and z')
        
    return x_axis, y_axis
    
def print_err_msg(*strings):
    list = []
    for string in strings:
        list.append(string)
    string = ''.join(list)
    if debug_verbose_error():
        raise Exception(string)
    else:
        print(string)
        sys.exit(1)
        
def check_array_equal(x):
    x = iter(x)
    try:
        first = next(x)
    except StopIteration:
        return True
    return all(first == rest for rest in x)

def check_coordinates_2D(x,x2,y,y2):
#        debug_push('SolutionReader diff_coordinates')
    coord_eps = 1.e-6

    if x.size == x2.size:
        for i in range(x.size):
            if abs(x[i]-x2[i]) > coord_eps:
                print_err_msg('X coordinate between two solutions mismatch at index {}. \
                               Grids must match for 2D solutions'.format(i+1))
    else:
        print_err_msg('X coordinate dimension mismatch between two solutions: {} {} \
                         Grids must match for 2D solutions'. \
                        format(x.size,x2.size))
    if y.size == y2.size:
        for i in range(y.size):
            if abs(y[i]-y2[i]) > coord_eps:
                print_err_msg('Y coordinate between two solutions mismatch at index {}. \
                               Grids must match for 2D solutions'.format(i+1))
    else:
        print_err_msg('Y coordinate dimension mismatch between two solutions: {} {} \
                         Grids must match for 2D solutions'. \
                        format(y.size,y2.size))

    if debug_verbose():
        print('Coordinates match')
#        debug_pop()
    
