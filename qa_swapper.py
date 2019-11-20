# -*- coding: utf-8 -*-
'''
Created on Thu Nov 29 16:32:34 2018

@author: gehammo
'''

import sys
import re

from qa_debug import *

verbose_local = False

class Swapper:
    
    def __init__(self,dict_=None):
        self._dict = {}
        if dict_:
            self._dict = dict_

    def __str__(self):
        message = 'Hello World!'
        return message    

    def add_tuple(self,tupl):
        '''add a variable that will be swapped using a tuple ("string",value)
        '''
        self._dict.append(tupl)
        
    def add_tuple(self,tupl):
        '''add a variable that will be swapped using a tuple ("string",value)
        '''
        self._dict.append(tupl)

#    def get_out_filename(self,id_string=None):
#        filename = self._template.strip()
#        if filename.endswith('.template'):
#            filename = filename[:-9]
#        if id_string:
#            filename += id_string
#        filename += '.in'
#        return filename
    
      
    def swap_line(self,inline):
        debug_push('Swapper swap_line')
 #     need to reformulate so that we parse the string as we go; don't
 #     operate on a singel line by itself
        line = inline
        icount = 0
        while True: # find all occurrences in line 
            istart = line.find('swap{')
            if not istart > -1:
                break
            iend = line[istart:].find('}') + istart
            if True: #len(swap_lines) == 1:
                templine = line[istart+5:]
                istart2 = templine.find('swap{')
                if istart2 > -1 and istart2 < iend:
#                    print('line(before): '+line)
                    line = line[:istart+5] + self.swap_line(templine)
#                    print('line(after): '+line)
                # have to update end as line may have changed due to swapping
                iend = line[istart:].find('}') + istart
                segment = line[istart+5:iend]
#                print('segment: '+segment)
                [keyword,value] = segment.split(',')
                try:
#                    print('keyword: '+keyword.strip())
                    value = str(self._dict[keyword.strip()])
#                    if    isinstance(value,int):
#                        substring = str(int)
                except:
                    sub_string = value
                line = line[0:istart] + value + line[iend+1:]
        debug_pop()
#        sys.exit(0)
        return line
                
    def swap_new(self,in_filename,out_filename,dict_=None):
        '''swaps all strings in options list with their matching value in the
             template. if a swap{string,default_value} does not exist in the
             options list, the default value in the file is used.
        '''
        debug_push('Swapper swap_new')
        if dict_:
            self._dict = dict_
        f = open(out_filename,'w')
        with open(in_filename,'r') as s:
            while True:
                line = s.readline() # leave \n on to catch eof
                if not line:
                    break
                line = line.rstrip() # remove \n
                if verbose_local:
                    print(line)
                if line.find('swap{') > -1:
                    line = self.swap_line(line)
                f.write(line.rstrip()+'\n')
        f.close()
        debug_pop()
 
    def swap(self,in_filename,dict_=None):
        if dict_:
            self._dict = dict_
        f = open(self.get_out_filename(),'w')
        with open(in_filename,'r') as s:
            while True:
                line = s.readline() # leave \n on to catch eof
                if not line:
                    break
                line = line.rstrip() # remove \n
                print(line)
                istart = line.find('swap{')
                if istart > -1:
                    swap_count = 0
                    while True: # find all occurrences in line 
                        istart = line.find('swap{')
                        if not istart > -1:
                            break
                        swap_count += 1
                        swap_lines = []
                        end_found = False
                        while True:
                            swap_lines.append(line)
                            templine = line
                            while True:
                                iend = templine.find('}')
                                if iend > -1:
                                    swap_count -= 1
                                    print('swap_count %d'%swap_count)
                                    if swap_count == 0:
                                        end_found = True
                                        break
                                        templine = templine[min(len(templine),iend+1):]
                                else:
                                    break
                            if end_found:
                                break
                            line = s.readline().rstrip()
                            print(line)
                        if len(swap_lines) == 1:
                            segment = line[istart+5:iend]
                            [keyword,value] = segment.split(',')
                            try:
                                value = self._dict[keyword.strip()]
                            except:
                                value = value
                            line = line[0:istart] + value + line[iend+1:]
                            f.write(line.rstrip()+'\n')
                        else:
                            iend2 = swap_lines[0][istart:].find(',') + istart
                            keyword = swap_lines[0][istart+5:iend2]
                            print(keyword)
                            lines = []
                            try:
                                array = self._dict[keyword.strip()]
                                for i in range(len(array)):
                                    if i == 0:
                                        segment = swap_lines[i][:istart]
                                        lines.append(segment+array[i])
                                    elif i == len(swap_lines)-1:
                                        segment = swap_lines[i][iend:]
                                        lines.append(array[i]+segment)
                                    else:
                                        lines.append(array[i])
                            except:
                                lines = swap_lines
                                lines[0] = lines[0][:istart]+lines[0][iend2+1:]
                                i = len(lines)-1
                                lines[i] = lines[i][:iend]+lines[i][iend+1:]
                            print(lines)
                            for l in lines:
                                if len(l.strip()) > 0:
                                    f.write(l.rstrip()+'\n')
                            line = lines[len(lines)-1]
                else:
                    f.write(line.rstrip()+'\n')
        f.close()

if __name__ == "__main__":
    try:
        template = 'pflotran.template'
        dict_ = {}
        swapper = Swapper(dict_)
        swapper.swap_new()
        print("success")
        sys.exit(0)                     
    except Exception as error:
        print("failure")
        sys.exit(1)

        
