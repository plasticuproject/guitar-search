#!/bin/sh

# Lint with flake8

echo "\nPerforming Linting and Syntax Checks:\n"
# stop the build if there are Python syntax errors or undefined names
flake8 test --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 services --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 db --count --select=E9,F63,F7,F82 --show-source --statistics
# exit-zero treats all errors as warnings
flake8 test --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
flake8 services --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
flake8 db --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
echo "\n----------------------------------------------------------------------"


# Static type checking with mypy

echo "\nPerforming Static Type Analysis:\n"
python -m mypy --strict test
python -m mypy --strict services
python -m mypy --strict db
echo "\n----------------------------------------------------------------------"


# Doctests
#echo "\nPerforming Python Doctests:\n"
#python -m doctest -f -v *.py
#echo "\n----------------------------------------------------------------------"


# Unit tests and code coverage reporting

echo "\nPerforming Unit Tests:\n"
python -m coverage run -m unittest discover -v
echo "\n----------------------------------------------------------------------"
echo "\nGenerating Code Coverage Report:\n"
python -m coverage lcov -o ./coverage/lcov.info
python -m coverage html
python -m coverage xml
echo "\n"
python -m coverage report
echo "\n----------------------------------------------------------------------\n"
