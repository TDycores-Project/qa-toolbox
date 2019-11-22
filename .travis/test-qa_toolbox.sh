#!/bin/sh

python3 directory_setup.py
make all

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
  echo "QA Toolbox tests failed" >&2
  exit 1
else
  echo "QA Toolbox tests succeeded" >&2
  exit 0
fi


