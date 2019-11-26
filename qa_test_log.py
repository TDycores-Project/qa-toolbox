import sys
import os
from pathlib import Path

class QATestLog(object):
    
    def __init__(self,root_dir):

        self.successful_tests = root_dir+'/successful_tests.log'
        self.failed_tests = root_dir+'/failed_tests.log'
        self.unrun_tests = root_dir+'/unrun_tests.log'
 
        # initialize each file
        open(self.successful_tests,'w').close()
        open(self.failed_tests,'w').close()
        open(self.unrun_tests,'w').close()
        
    def log_success(self,path,test):
        with open(self.successful_tests,"a+") as f:
            f.write('{}/{} \n'.format(path,test))

    def log_failure(self,path,test):
        with open(self.fauled_tests,"a+") as f:
            f.write('{}/{} \n'.format(path,test))
        
    def log_unrun(self,path,test):
        with open(unrun_tests,"a+") as f:
            f.write('{}/{} \n'.format(path,test))
        
        
    def _copy_contents_to_file(self,file_to_read,file_to_write):
        with open(file_to_read, "r") as f1:
            with open(file_to_write, "a+") as f2:
                for line in f1:
                    f2.write(line)
                    
                    
