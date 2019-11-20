# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 13:36:29 2018

@author: gehammo
"""

verbose = True
#verbose = False

verbose_error = False

stack = []

def debug_push(string):
    stack.append(string)
    if verbose:
        print('Begin '+stack[len(stack)-1])
        
def debug_pop():
    if verbose:
        print('End   '+stack[len(stack)-1])
    stack.pop()
    
def debug_verbose():
    if verbose:
        return True
    return False

def debug_verbose_error():
    if verbose_error:
        return True
    return False
