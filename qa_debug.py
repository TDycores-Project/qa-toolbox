# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 13:36:29 2018

@author: gehammo
"""

verbose = True
verbose = False

verbosity_ceiling = 5

verbose_error = False
indent_increment = 0
#indent_increment = 2
append_increment_integer = False
#append_increment_integer = True
if indent_increment == 0:
    append_increment_integer = False

stack = []

def debug_push(string):
    stack.append(string)
    if verbose and len(stack) <= verbosity_ceiling:
        m = len(stack)
        indent_string = ' '*(m*indent_increment)
        stack_string = debug_top_of_stack()
        if append_increment_integer:
            print('Begin '+indent_string+stack_string+' {}'.format(m))
        else:
            print('Begin '+indent_string+stack_string)
        
def debug_pop():
    if verbose and len(stack) <= verbosity_ceiling:
        m = len(stack)
        indent_string = ' '*(m*indent_increment)
        stack_string = debug_top_of_stack()
        if append_increment_integer:
            print('End   '+indent_string+stack_string+' {}'.format(m))
        else:
            print('End   '+indent_string+stack_string)
    stack.pop()

def debug_top_of_stack():
    if len(stack) > 0:
        return stack[len(stack)-1]
    return None
    
def debug_verbose():
    if verbose:
        return True
    return False

def debug_verbose_error():
    if verbose_error:
        return True
    return False

def debug_finalize():
    if not len(stack) == 0:
        print('\nERROR: Debug stack is not zero: {}\n'.format(len(stack)))
        while len(stack) > 0:
            print('  {}'.format(debug_top_of_stack()))
            stack.pop()
