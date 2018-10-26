#!/bin/bash -e
#
# Script to fetch the strings CVS file.
#
# Copyright (c) 2018 Endless Mobile Inc.
#
# Author: Joaquim Rocha <jrocha@endlessm.com>
#

script_path=$0
source_dir="$(dirname "$script_path")/.."

KEY='162yiw_kW3lgLEIUwBq3PgiZxWTtcVBUHqpZKUXtF8qY'
SHEET='Dialog'
url="https://docs.google.com/spreadsheets/d/$KEY/gviz/tq?tqx=out:csv&sheet=$SHEET"

pushd "$source_dir"

ret=$(wget "$url" -O "$source_dir/data/quests_strings.csv") || ret=$?

popd

exit $ret
