#!/bin/bash -e

echo "Compiling Python files"
python3 -m compileall $1 -b

echo "Compiling non-pyc files"
find $1 ! -name \*.pyc -type f -delete
