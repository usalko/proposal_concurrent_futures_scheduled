#!/bin/bash
rm -fr build
rm -fr dist
python3 setup.py bdist_wheel
