import sys
import numpy as np
import math
import matplotlib.pyplot as plt
from h5py import *

sys.path.append("..")

from qa_test_error import QATestError

filename_error_metrics = 'error_metrics.gold'
filename_absolute_error = 'absolute_error.gold'
filename_relative_error = 'relative_error.gold'

h5_file_cos='cos_dataset.h5'
h5_file_sin='sin_dataset.h5'

group='/Time Slice/Time: 0.000e+00 y'

f=File(h5_file_cos,'r')   

times1=np.array(f['/Time Slice/Coordinates/X'])
values1=np.array(f[group+'/Pressure'])
f.close()

f=File(h5_file_sin,'r')   

times2=np.array(f['/Time Slice/Coordinates/X'])
values2=np.array(f[group+'/Pressure'])
f.close()

values1=np.array(values1[:,0,0])
values2=np.array(values2[:,0,0])


#plt.plot(values2)
error=QATestError()
error.calc_error_regression_test(times1,values1,times2,values2)     
###save to write to text file
with open(filename_error_metrics,'w') as f:
    f.write('Average Absolute Error = {} \n'.format(error.average_absolute_error))
    f.write('Maximum Absolute Error = {} \n'.format(error.maximum_absolute_error))
    f.write('Maximum Relative Error = {} \n'.format(error.maximum_relative_error))
    f.write('Average Relative Error = {} \n'.format(error.average_relative_error))
    f.write('Absolute Relative Area = {}'.format(error.absolute_relative_area))

np.savetxt(filename_absolute_error,error.absolute_error)
np.savetxt(filename_relative_error,error.relative_error)

##gold files needed:
#image files: observation & time slice
#image files: error
#error metrics --> stats & absolute/relative error