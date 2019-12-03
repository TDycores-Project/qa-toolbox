[![Build Status](https://travis-ci.org/TDycores-Project/qa-toolbox.svg?branch=master)](https://travis-ci.org/TDycores-Project/qa-toolbox)

# qa-toolbox
A framework for executing and documenting verification and validation tests.

## Instructions

1. Clone the repository: git clone git@github.com:TDycores-Project/qa-toolbox.git
1. Within qa-toolbox:
   1. Create a file *simulators.sim* listing simulator names mapped to the complete path of the executables. Use *default_simulators.sim* as an example.
   1. Create a file *config_files.txt* listing the relative path from the root directory to the .cfg files to be run. Use *default_configf_files.txt* as an example.
   1. Create the documentation directory structure:
      * SPHINX_DIR - Top level directory where *index.rst* resides
      * SPHINX_DIR/source - Directory for supporting .rst files. Additional underlying directories may be created.
1. Launch the test suite with **make all DOC_DIR=$SPHINX_DIR**.
   
