
QA Test Suite Instructions
==========================

Installation Instructions
-------------------------

1. Download (clone) qa_tests off Bitbucket and checkout rosie/development branch.

  .. code-block:: bash
   
    $ git clone https://github.com/TDycores-Project/qa-toolbox.git
    $ cd qa-toolbox


  Tests are located in folders within the directory. Each test consists of input decks for each simulator, a configuration file, and an options file.

  Test can be run to produce a time slice (all locations at one time) or an observation point (one location at all times).


Running the Test Suite
-------------------------
       
1. Create a file named ``simulators.sim`` and set local paths to simulator exectuables. See ``default_simulators.sim`` as an example.

   
2. Create a file named ``config_files.txt`` and set the path to the configuration file for the desired tests. Multiple tests can be chosen to run. See ``default_config_files.txt`` as an example.


3. Run the test suite within the ``qa-toolbox/`` directory by running the makefile:


  .. code-block:: bash
   
    $ make


4. If the qa_test_suite is running you will see scrolling screen output that looks simular to what is displayed below:


  .. code-block:: bash
		    
    Namespace(doc_dir=None)
    Running QA tests :
    /Users/rleone/software/qa-toolbox/regression_tests/test.cfg

    *************** regression *************************************************** 

    simulators: sin,cos
    /Users/rleone/software/qa-toolbox/regression_tests
    /Users/rleone/software/qa-toolbox
    /regression_tests

  If ``plot_to_screen`` is set to ``True`` in the options file (default is ``False``), you should see displays pop up as the test suite plots results, to continue with the tests exit out of each display as they pop up. If the simulation has finished, you should see success at the end, like so:

  .. code-block:: bash

    success

5. As the simulation is running, output files, saved figure results, and documentation files  will be generated. They will be located in the same location as your input files.

   .. code-block:: bash
    
      $ cd mytest
      $ ls

      0.01_Liquid_Pressure_kolditz_2_2_9_run1.png      2.0_1.0_1.0_Liquid_Pressure_kolditz_2_2_9_run1.png

   Image files are named based on the time (if time slice) or location (if observation), the template name, the run number, and the variable being plotted.

   
Creating Documentation
----------------------

Documentation for the test suite is outputted as .rst files and compiled using Sphinx. It consists of a results summary listing maximum absolute and relative error and maximum average and relative error, a problem description, and detailed results with figures and error calculations.

1. Create a text file which describes the problem being run. Equations can be included following sphinx extension mathbase. The text file should be named in the following format: ``description_template.txt`` with template being the input value from the ``.cfg`` file. For example, in the tracer test located in the transport folder the description file is named ``description_tracer.txt``.

2. Set up the documentation directory:

   a. Create a documentation directory. If creating the documentation directory outside of the qa-toolbox or naming the directory something other than ``docs``, the user must specify the path to the directory when running the make file.

      .. code-block:: bash

	$ mkdir docs



   b. Cd into the documentation directory and set-up sphinx.

      .. code-block:: bash
		      
        $ cd docs
	$ sphinx-quickstart


   c. Set up the configuration file ``conf.py`` using desired theme or leave to default.


   d. Run the test suite and specify the documentation directory path if the docs directory is not in the qa-toolbox or if it is named differently than ``docs``.
		      
     .. code-block:: bash

	$ make doc_dir = /user/docs


   e. The qa_toolbox will automatically populate the index.rst file and toctree files.


   f. To make the html files cd into the Documentation directory and build the files.


     .. code-block:: bash

        $ cd Docs
        $ make clean
        $ make html

	
   e. The html file will be located in the _build/html directory. Open up index.html in a web browser to view documentation.

      
Adding Tests to Suite
---------------------
   
1. To create a new QA test within the toolbox, first create a new folder within the qa-toolbox directory and cd into the folder. The folder name will appear as the title for the documentation file.
   
  .. code-block:: bash
   
    $ mkdir my_test     
    $ cd mytest


2. Create two or more input files for the desired simulators you wish to test. Note: If working in 2D, 3D, or calculating error only two simulators may be run at a time. The input file has a file extension based on the simulator you wish to run, such as ``filename.pflotran, filename.python``. Additionally, you can browse the input decks within the sandbox directory. The filename will be specified in the configuration file. **NOTE: IF INPUT FILES TAKE IN A HDF FILE, IT MUST HAVE THE EXTENSION .HDF5 NOT .H5, FILES WITH A .H5 EXTENSION ARE DESIGNATED AS A FILE OUTPUTTED FROM THE TEST SUITE FILE AND WILL BE DELETED WHEN THE MAKEFILE IS RUN**


3. The QA test suite reads in an options file specified by the user in a standard ``.opt`` extension. The options file consist of a series of sections with key-value pairs.

  ::
      
   [section-name]
   key = value
     
  Section names are all lower case with an underscore between words. Required section names are:

   * output_options

  Optional section names include:

   * swap_options
   * mapping_options
   * tough_options


  An example output_options section is as follows:
   
  ::

   [output_options]
   times = 10.0 y, 50.0 y, 100.0 y
   locations = 1.0 1.0 1.0, 5.0 1.0 1.0
   plot_time_units = years
   plot_dimension = 1D
   plot_x_label = Time [yr], Distance X [m]
   plot_y_label = Liquid Pressure, Liquid Pressure
   plot_title = Pflotran Test
   variables = liquid_pressure
   plot_type = observation, time slice
   plot_to_screen = True
   plot_error = True

  * times: (Required for time slice) List of times to plot and compare solutions at. Must match the times of outputs created by simulators. Unit must come after the time.
  * locations: (Required for observation point) List of locations (x y z) where specified observation point(s) is indiciated in simulator file. Units in [m].
  * plot_time_units: (Required) Units of time to be displayed on plot.
  * plot_dimension: (Required) Dimension of simulation. Options include: 1D, 2D, 3D. If plotting in 2D or 3D only two simulators may be tested at a time.
  * plot_x_label: (Required) Label to be put on x axis of plot. If plotting both a time slice and an observation file, two values must be specified here separted by a comma and order must match order of plot_type.
  * plot_y_label: (Required) Label to be put on y axis of plot. If plotting both a time slice and an observation file, two values must be specified here separted by a comma and order must match order of plot_type.
  * plot_title: (Required) Title to be displayed on plot.
  * variables: (Required) Variable to be plotted from the output files. Must match the simulator output format. Custom mapping of variables can be specified in optional section ``mapping_options``.
  * plot_type: (Optional, default: time slice) Observation if plotting observation point, time slice if plotting time slice. If plotting both order must match plot_x_label and plot_y_label.
  * plot_error: (Optional, default: False) True if plotting relative and absolute error, False if not. If True only two simulatos may be run at a time.
  * print_error: (Optional, default: False) When set to True a .stat file will be created with list of error metrics.
  * plot_to_screen: (Optional, default: False) When set to True images will pop up as python script is being run.
    

  Optional section ``swap_options`` defines values of variables in input decks to be tested. Each value will correspond to a different run number when outputting figures. If no swap options are specified the run number will be 0.

  ::

   [swap_options]
   method = list
   nx = 20, 40
   ny = 30, 50


  * method: (default: list) Options: list, iterative.
     * List: Specifies list of values for different variables. All variables must have the same number of values. The length for each variable should be equal.
     * Iterative: Variables will be increased incrementally for an amount specified by max_attempts. A starting value and an increment should be specified sepearted by a comma. (For example: nx = 12,2 will start nx with a value of 12 and will multiple the value by 2 until max_attempts is reached.)
  * max_attemps: (Required if iterative) Maximum number of iterations to take with iterative method.

    Variables names are listed based on what is defined in the input simulator files.


  The optional section ``mapping_options`` can be used when trying to plot unconvential variables and when simulator output names do not match.

  ::
    
   [mapping_options]
   Free X1 [M] = X1
   Free_X1 [M] = X1

  where ``Free X1 [M]`` is the variable name outputted by the simulator and ``X1`` is the variable listed under the variables key in ``output_options``. As many key and value pairs can be listed as needed.


4. Create the configuration file as a standard ``.cfg`` and specify the option file, filename, and simulators.
    
   :: 
   
    [OPTIONSFILENAME]
    template = filename
    simulators = pflotran, python


   For example in analytical_test/test.cfg ``test.cfg`` reads:

   ::

    [richards]
    template = kolditz_2_2_10
    simulators = pflotran,python

   Where ``richards.opt`` is the options file and input files are named: ``kolditz_2_2_10.pflotran`` and ``kolditz_2_2_10.python``.

   Available simulators the test can run include:

   * pflotran
   * python
   * crunchflow
   * tough3
   * tdycore

5. Move back into the qa-toolbox directory, add the path name to the configuration file in ``config_files.txt`` and run the test suite.

   .. code-block:: bash

      $ make


Creating Python Files
^^^^^^^^^^^^^^^^^^^^^
If running a Python simulator certain commands and steps should be added and followed in order for the test suite to run correctly. A time slice (looking at the entire grid at certain times) and/or observation point (looking at one point over the entire time) can be implemented. If only running a time slice, the observation additions may be ignored and vice versa. Error metrics are implemented the same way as for other simulators, by setting `plot_error` and/or `print_error` to True in the options file.

1. Import sys, traceback, qa_common, qa_solution, and simulator_modules. Make sure paths are set correctly to simulator modules.

   .. code-block:: python

      import sys
      import traceback

      sys.path.insert(0,'..')
      sys.path.insert(0, '../simulator_module')

      from qa_common import *

      from qa_solution import QASolutionWriter
      from simulator_modules.python import *


2. Define filename variable which will be used to get the solution filename.

   .. code-block:: python

      filename = __file__

      
3. Set up your file by using a main function and then execute using a try and except block.

   .. code-block:: python

      def main(options):


   .. code-block:: python
		   
      if __name__ == "__main__":
        cmdl_options=[]
        try:
            suite_status = main(cmdl_options)
	    sys.exit(suite_status)
        except:
	    print(str(error))
	    traceback.print_exc()
	    print("failure")
	    sys.exit(1)

4. In the main function make sure the folloinwg are set:

   a. If the time unit is different than years than a time unit variable must be set.

      .. code-block:: python

         time_unit = 'd'

      Acceptable values include:

      * 'y','yr','yrs','year','years' = years
      * 'mo','month' = month
      * 'd','day' = day
      * 'h','hr','hour' = hour
      * 'm','min','minute' = minute
      * 's','sec','second' = second
	

   b. Make a SolutionWriter object which the test suite will use to convert the solution to h5 format.

      .. code-block:: python

	 solution_filename = get_python_solution_filename(filename)
	 solution = SolutionWriter(solution_filename, time_unit)

      The time_unit variable is an optional input paramater into SolutionWriter, as mentioned above if time units are in years this is not needed.
      

   c. Define x, y, and z numpy arrays even when working in less than 3D. For an observation point this will represent a point matching what is in the options file under `locations`.  

      Time Slice Example:     

      .. code-block:: python

	 x_time_slice = np.linspace(0. + (dx/2.),Lx-(dx/2.),nx)
	 y_time_slice =  np.array([0.5])
	 z_time_slice = np.array([0.5])


      Observation Point Example:

      .. code-block:: python

	 x_observation = np.array([15])
	 y_observation = np.array([0.5])
	 z_observation = np.array([0.5])


   d. If creating a solution for an observation point write the time and solution to the SolutionWriter object.

      .. code-block:: python

	solution.write_time(t_soln)

      Where `t_soln` is an array of times the function will run over.

  
      .. code-block:: python

	#solution.write_dataset(coordinates,solution,variable_string,'Observation')	      
	solution.write_dataset(np.concatenate((x_observation,y_observation,z_observation)),p_soln,'Liquid_Pressure','Observation')

      Coordinates must be in 3D (x,y,z), solution can be in 1D, 2D, or 3D, and variable_string matches what was inputted into the `variables` key in the options file.

      
   e. If creating a solution for a time slice output write the coordinates and solution to the SolutionWriter object.

      .. code-block:: python

	 solution.write_coordinates(x_time_slice,y_time_slice,z_time_slice)

      .. code-block:: python

	 #solution.write_dataset(time,solution,variable_string)	      
	 solution.write_dataset(t_soln[time],p_soln[time,:],'Liquid_Pressure')


      Time is the time the solution is for and is 1D, the solution is a numpy array that can be 1D, 2D, or 3D, and variable_string matches what was inputted into the `variables` key in the options file.

   f. Destroy the solution object.

      .. code-block:: python

         solution.destroy()

  
5. Putting it all together an example python file is below with added commands highlighted.

   .. code-block:: python
      :emphasize-lines: 1,2, 4, 5, 10, 12, 13, 15, 42, 43, 47, 63, 74, 91, 94

      import sys
      import traceback

      sys.path.insert(0,'..')
      sys.path.insert(0,'../simulator_module')

      import numpy as np
      import math

      from qa_common import *

      from simulator_modules.solution import SolutionWriter
      from simulator_modules.python import *

      filename = __file__
      epsilon_value = 1.e-30

      def main(options):

	print('Beginning {}.'.format(filename))

	nx = swap{nx,10}
	tx = 10
	time_unit = 'd' ####Unit for time
	Lx = 100
	dx = Lx/nx

	k = 1.0e-14
	mu = 1.728e-3
	por = 0.20
	kappa = 1.0e-9
	chi = k/(por*kappa*mu)
	p_offset = .101325

	t_soln = np.linspace(0,0.50,tx) ##array of times
	x_observation = np.array([15.0])
	y_observation = np.array([0.5])
	z_observation = np.array([0.5])
	p_soln = np.zeros((t_soln.size))#,tx))
    

	solution_filename = get_python_solution_filename(filename)
	solution = SolutionWriter(solution_filename,time_unit)

	#THIS IS AN OBSERVATION POINT EXAMPLE#
        ###########################################################
	solution.write_time(t_soln)
	for time in range(t_soln.size):
	    t = t_soln[time]*24.0*3600.0  # [sec]
	    sum_term_old = 0 # np.zeros(nx)
	    sum_term = 0 #np.zeros(nx)
	    n = 1
	    epsilon = 1.0
      
	    while epsilon > epsilon_value:
		sum_term_old = sum_term
		sum_term = sum_term_old + (np.cos(n*math.pi*x_observation/Lx)*np.exp(-chi*pow(n,2)*pow(math.pi,2)*t/pow(Lx,2))*(80./(3.*pow((n*math.pi),2)))*np.cos(n*math.pi/2.)*np.sin(n*math.pi/4.)*np.sin(3.*n*math.pi/20.))
		epsilon = np.max(np.abs(sum_term_old-sum_term))
		n = n + 1
	    p_soln[time] = ((0.50 + sum_term) + p_offset)*1.0e6

	#solution.write_dataset((x,y,z),solution,variable_string,'Observation')
	solution.write_dataset(np.concatenate((x_observation,y_observation,z_observation)),p_soln,'Liquid_Pressure','Observation')
        #######################################################

        #TIME SLICE EXAMPLE#
	######################################################
	t_soln = np.array([0.05,0.10,0.25,0.50]) 
	p_soln = np.zeros((t_soln.size,nx))
	x_time_slice = np.linspace(0.+(dx/2.),Lx-(dx/2.),nx)
	y_time_slice = np.array([0.5])
	z_time_slice = np.array([0.5])
    
	solution.write_coordinates(x_time_slice,y_time_slice,z_time_slice)

	for time in range(4):
	    t = t_soln[time]*24.0*3600.0  # [sec]
	    sum_term_old = np.zeros(nx)
	    sum_term = np.zeros(nx)
	    n = 1
	    epsilon = 1.0
      
	    while epsilon > epsilon_value:
		sum_term_old = sum_term
		sum_term = sum_term_old + (np.cos(n*math.pi*x_time_slice/Lx)*np.exp(-chi*pow(n,2)*pow(math.pi,2)*t/pow(Lx,2))*(80./(3.*pow((n*math.pi),2)))*np.cos(n*math.pi/2.)*np.sin(n*math.pi/4.)*np.sin(3.*n*math.pi/20.))
		epsilon = np.max(np.abs(sum_term_old-sum_term))
		n = n + 1
	    p_soln[time,:] = ((0.50 + sum_term) + p_offset)*1.0e6
	    
            #solution.write_dataset(time,solution,variable_string)
	    solution.write_dataset(t_soln[time],p_soln[time,:],'Liquid_Pressure')
	    ######################################################

	solution.destroy()
	print('Finished with {}.'.format(filename))

      if __name__ == "__main__":
	cmdl_options=[]
        try:
            suite_status=main(cmdl_options)
            sys.exit(suite_status)
        except Exception as error:
            print(str(error))
            traceback.print_exc()
            print("failure")
            sys.exit(1)
