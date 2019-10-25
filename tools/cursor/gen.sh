#!/bin/bash

xcursorgen="xcursorgen"
source .env
mkdir -p output

for i in arrow left_ptr1 left_ptr2 watch
do
    cd $i
    ./gen-png.sh
    ./gen.in.sh > $i.in
    $xcursorgen $i.in ../output/$i
    cd ..
done
