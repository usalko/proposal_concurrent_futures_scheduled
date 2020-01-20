#!/bin/bash

###############################################################################
# Script Name	: test-on-another-python.sh
# Description	: Run tests/test_scheduled_thread_pool_executor.py on different
#             : pythons
# Args       	: Vali python version name (like 3.5.0)
# Author      : Ivan Usalko
# Email      	: ivict@rambler.ru
###############################################################################

PYTHON_VERSION=${1:-3.5.0}
PYTHON_VERSION_MAJOR=$(echo "$PYTHON_VERSION"| cut -d'.' -f 1)
PYTHON_VERSION_MINOR=$(echo "$PYTHON_VERSION"| cut -d'.' -f 2)
PYTHON_VERSION_BUILD=$(echo "$PYTHON_VERSION"| cut -d'.' -f 3)


CURRENT_FOLDER=$(pwd)

mkdir tmp
cd tmp || exit

TESTS_ROOT_FOLDER=$CURRENT_FOLDER/tmp

# DOWNLOAD STEP
if [ -e "Python-$PYTHON_VERSION.tgz" ]; then
  echo "Omit download step for Python-$PYTHON_VERSION.tgz"
else
  wget "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"
fi

# UNPACK STEP
if [ -e "Python-$PYTHON_VERSION" ]; then
  echo "Omit unpack step for Python-$PYTHON_VERSION"
else
  tar -zxf "Python-$PYTHON_VERSION.tgz"
fi

# COMPILATION STEP
if [ -e "Python-$PYTHON_VERSION-Tests" ]; then
  echo "Omit compilation step for Python-$PYTHON_VERSION-Tests"
else
  cd "Python-$PYTHON_VERSION" || exit
  time ./configure
  time make
  mkdir "$TESTS_ROOT_FOLDER/Python-$PYTHON_VERSION-Tests"
  time make DESTDIR="$TESTS_ROOT_FOLDER/Python-$PYTHON_VERSION-Tests" install
  time make clean
fi

cd "$CURRENT_FOLDER" || exit

PYTHON="$TESTS_ROOT_FOLDER/Python-$PYTHON_VERSION-Tests/usr/local/bin/python$PYTHON_VERSION_MAJOR"

$PYTHON -m unittest -v tests/test_scheduled_thread_pool_executor.py
