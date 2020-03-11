# Makefile for running the QA Toolbox

PYTHON = python3
QA_TEST_SUITE = qa_test_suite.py
DOC_DIR = ${PWD}/docs
CURRENT_DIR = ${PWD}
CONFIG_FILE = config_files.txt
SIMULATORS_FILE = simulators.sim


all : clean_tests run_tests

clean_tests :
	$(PYTHON) qa_clean_tests.py $(CURRENT_DIR) $(CONFIG_FILES)

run_tests :
	$(PYTHON) $(QA_TEST_SUITE) --doc_dir $(DOC_DIR) --config_file $(CONFIG_FILE) --simulators_file $(SIMULATORS_FILE)

run_incremental_tests :
	$(PYTHON) $(QA_TEST_SUITE) --doc_dir $(DOC_DIR) --config_file $(CONFIG_FILE) --simulators_file $(SIMULATORS_FILE) --incremental_testing
