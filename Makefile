# Makefile for running the QA Toolbox

PYTHON = python3
QA_TEST_SUITE = qa_test_suite.py
DOC_DIR = ${PWD}/docs
REGRESSION_DOC = ${PWD}/regression_tests/Documentation_test/docs

all : run_tests

run_tests :
	$(PYTHON) $(QA_TEST_SUITE) --doc_dir $(DOC_DIR)

run_doc_check :
	$(PYTHON) $(QA_TEST_SUITE) --doc_dir $(REGRESSION_DOC) --doc_test True
