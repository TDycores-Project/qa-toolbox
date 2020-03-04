# Makefile for running the QA Toolbox

PYTHON = python3
QA_TEST_SUITE = qa_test_suite.py
DOC_DIR = ${PWD}/docs
CURRENT_DIR = ${PWD}

all : clean_tests run_tests

clean_tests :
	$(PYTHON) qa_clean_tests.py $(CURRENT_DIR)

run_tests :
	$(PYTHON) $(QA_TEST_SUITE) --doc_dir $(DOC_DIR)

run_incremental_tests :
	$(PYTHON) $(QA_TEST_SUITE) --doc_dir $(DOC_DIR) --incremental_testing
