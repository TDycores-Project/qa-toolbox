import sys
from h5py import *
import numpy as np

nx = 15; lx = 1; dx = lx/nx; 
ny = 15; ly = 1; dy = ly/ny
nz = 1; dz = 1; lz = 1
for k in range(len(sys.argv)-1):
  k = k + 1
  if sys.argv[k] == '-nx':
    nx = int(float(sys.argv[k+1]))
  if sys.argv[k] == '-ny':
    ny = int(float(sys.argv[k+1]))
  if sys.argv[k] == '-nz':
    nz = int(float(sys.argv[k+1]))
  if sys.argv[k] == '-dx':
    dx = float(sys.argv[k+1])
  if sys.argv[k] == '-dy':
    dy = float(sys.argv[k+1])
  if sys.argv[k] == '-dz':
    dz = float(sys.argv[k+1])
  if sys.argv[k] == '-lx':
    lx = float(sys.argv[k+1])
  if sys.argv[k] == '-ly':
    ly = float(sys.argv[k+1])
  if sys.argv[k] == '-lz':
    lz = float(sys.argv[k+1])

filename = 'dataset.h5'
h5file = File(filename,mode='w')

p0 = 1.0e5   # [Pa]
k = 1.0e-15  # [m2]
mu = 1.0e-5  # [Pa-s]

# 1d line in x
# Flux boundary condition; NORTH
h5grp = h5file.create_group('x_line_cell_centered_north')
h5grp.attrs['Cell Centered'] = True
h5grp.attrs['Interpolation Method'] = np.string_('STEP')
h5grp.attrs['Dimension'] = np.string_('X')
# Delta length between points [m]
h5grp.attrs['Discretization'] = [dx]
# Location of origin
h5grp.attrs['Origin'] = [0.]
# Load the dataset values
rarray = np.zeros(nx,'=f8')
for i in range(nx):
  x = (float(i)*lx)/nx + dx/2.
  p_gas = p0*np.sqrt(1+3*(x/lx))  # [Pa] from analytical solution at y=L
  rarray[i] = ((3*k)/(2*mu))*((p0**2)/lx)*(x/lx)   # [Pa m/s]
  rarray[i] = rarray[i]/p_gas                      # [m/s]
h5dset = h5grp.create_dataset('Data', data=rarray)

# 1d line in y
# Flux boundary condition; EAST
h5grp = h5file.create_group('y_line_cell_centered_east')
h5grp.attrs['Cell Centered'] = True
h5grp.attrs['Interpolation Method'] = np.string_('STEP')
h5grp.attrs['Dimension'] = np.string_('Y')
# Delta length between points [m]
h5grp.attrs['Discretization'] = [dy]
# Location of origin
h5grp.attrs['Origin'] = [0.]
# Load the dataset values
rarray = np.zeros(ny,'=f8')
for i in range(ny):
  y = (float(i)*ly)/ny + dy/2.
  p_gas = p0*np.sqrt(1+3*(y/ly))  # [Pa] from analytical solution at x=L
  rarray[i] = ((3*k)/(2*mu))*((p0**2)/ly)*(y/ly)   # [Pa m/s]
  rarray[i] = rarray[i]/p_gas                      # [m/s]
h5dset = h5grp.create_dataset('Data', data=rarray)
