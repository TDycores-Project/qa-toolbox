import sys
import shutil
import os
import configparser

from qa_common import *
from qa_debug import *

def compile_requirements(requirements_filename):
    debug_push('qa_requirements.compile_requirements')
    config = configparser.ConfigParser()
    config.read(requirements_filename)   
    requirements = config.items('requirements')

    requirements_dict = {}
    for requirement, attributes in requirements:
        attributes = attributes.split(',')
        for attribute in attributes:
            attribute = attribute.strip()
            if attribute in requirements_dict.keys():
                requirements_dict[attribute].append(requirement)
            else:
                requirements_dict[attribute] = [requirement]
    debug_pop()
                
    return requirements_dict
        
        
        
