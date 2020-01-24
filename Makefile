# Makefile for running the QA Toolbox

PYTHON = python3
QA_TEST_SUITE = qa_test_suite.py
DOC_DIR = ${PWD}/docs

all : clean_tests run_tests

clean_tests :
	-find . -type f -name '*.png' -print0 | xargs -0 rm
	-find . -type f -name '*.stat' -print0 | xargs -0 rm
	-find . -type f -name '*.tec' -print0 | xargs -0 rm
	-find . -type f -name '*.stdout' -print0 | xargs -0 rm
	-find . -type f -name '*.in' -print0 | xargs -0 rm
	-find . -type f -name '*.out' -print0 | xargs -0 rm
##	-find . -type f -name '*.rst' -print0 | xargs -0 rm
	-find . -type f -name '*run1.py' -print0 | xargs -0 rm
	-find . -type f -name '*run2.py' -print0 | xargs -0 rm
	-find . -type f -name '*pflotran_run*.h5' -print0 | xargs -0 rm
	-find . -type f -name '*python_run*.h5' -print0 | xargs -0 rm
	-find . -type f -name '*pflotran_run*.h5' -print0 | xargs -0 rm
	-find . -type f -name '*tdycore_run*.h5' -print0 | xargs -0 rm
	-find . -type f -name '*tough3_run*.h5' -print0 | xargs -0 rm
	-find . -type f -name 'FOFT*' -print0 | xargs -0 rm
	-find . -type f -name 'OUTPUT*' -print0 | xargs -0 rm
#	-find . -type f -name '*.h5' -print0 | xargs -0 rm
	-find . -type f -name 'GENER' -print0 | xargs -0 rm
	-find . -type f -name 'SAVE' -print0 | xargs -0 rm
	-find . -type f -name 'TABLE' -print0 | xargs -0 rm
	-find . -type f -name 'MESHA' -print0 | xargs -0 rm
	-find . -type f -name 'MESHB' -print0 | xargs -0 rm
	-find . -type f -name 'INCON' -print0 | xargs -0 rm
	-find . -type f -name 'documentation*.rst' -print0 | xargs -0 rm
	-find . -type f -name 'include_*.rst' -print0 | xargs -0 rm
	-find . -type f -name 'intro_*.rst' -print0 | xargs -0 rm
	-find . -type f -name 'successful_tests.log' -print0 | xargs -0 rm

run_tests :
	$(PYTHON) $(QA_TEST_SUITE) --doc_dir $(DOC_DIR)

run_incremental_tests :
	$(PYTHON) $(QA_TEST_SUITE) --doc_dir $(DOC_DIR) --incremental_testing
