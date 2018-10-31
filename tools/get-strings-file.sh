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

ret=0
wget "$url" -O "$source_dir/data/quests_strings.csv" || ret=$?

if [ "$ret" == 0  ] && [ "$1" == '--commit' ]; then
    # Ensure we don't include previously added things in this commit
    git reset HEAD > /dev/null
    # Add any changes to the CSV file and commit them
    git add "$source_dir/data/quests_strings.csv"
    git ci --no-verify -m 'data: Update quests strings CSV'
fi

popd

exit $ret
