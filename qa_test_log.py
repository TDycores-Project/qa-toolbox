import sys
import os
import numpy as np


###make this a text file and read in???? ###these names are titles but what does test output??
#list_of_tests=[kolditz_2_2_9,kolditz_2_2_10,tough3,crunchflow]
####assume all in different folders...


unrun_tests = 'unrun_tests.log' #not_runned_tests

failed_tests = 'failed_tests.log'   ###assumes these files are already created....

successful_tests = 'successful_tests.log' ##change to tests   'test_test.txt'#

root_dir = os.getcwd()

class QATestLog(object):
    
    def __init__(self,test_path): ###test list config files or template???????? #### what if regression test failed????? won't update .txt files
        os.chdir(root_dir)
        
        self.test = test_path.replace('{}/'.format(root_dir),'') #use os.path.split instead???
        
        self._delete_tests_in_file(failed_tests,self.test)
        with open(failed_tests,"a+") as f:    ##a+  ###what happens if already in....
            f.write('{} \n'.format(self.test))
                
        ##remove files from successful tests if rerunning        
        self._delete_tests_in_file(successful_tests,self.test)
        
        ###remove files from unrun tests
        self._delete_tests_in_file(unrun_tests,self.test)
        
        
        
    def add_test_to_pass_list(self):
        os.chdir(root_dir)

        with open(successful_tests,"a+") as f:
            f.write('{} \n'.format(self.test))
        self._delete_tests_in_file(failed_tests,self.test)
        
    def reset_tests(self):
        self._copy_contents_to_file(successful_tests,unrun_tests)
        open(successful_tests,"w").close()

        self._copy_contents_to_file(failed_tests,unrun_tests)   ###do we want to delete failed tests when reseting??
        open(failed_tests,"w").close()            

                    
                    
    def _delete_tests_in_file(self,file,test):
        if os.path.exists(file):
            with open(file,"r+") as f:    ###Definitely not the fastest way to do this, making a new text file would be faster?? 
    #            for i in range(len(test_list)):
                    lines = f.readlines()
                    f.seek(0)
                    for line in lines:
    
                        if test not in line: ##not in
                            f.write(line)
                    f.truncate()
        else:
            open(file,'a').close()
                
    def _copy_contents_to_file(self,file_to_read,file_to_write):
        with open(file_to_read, "r") as f1:
            with open(file_to_write, "a+") as f2:
                for line in f1:
                    f2.write(line)
                    
                    
#test='/user/rosie/test/test.cfg'
#test='/users/rosie/software'#/qa_tests/sandbox/analytical_test/test.cfg'
#new_test=test.replace('/users/rosie/','')
#print(new_test)
        
                

