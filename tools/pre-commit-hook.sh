#!/bin/sh
#
# Run flake8 (inside Pytohn's virtualenv) before commiting.
#
# Copyright (c) 2018 Endless Mobile Inc.
#
# Author: Joaquim Rocha <jrocha@endlessm.com>
#

source_dir="$(git rev-parse --show-toplevel)"

$source_dir/tools/run-lint || exit
if [ -z $SKIP_COMPILE_CSS ]; then
    $source_dir/tools/check-css || true
fi
if [ -z $SKIP_STRINGS_CHECK ]; then
    $source_dir/tools/check-strings || true
fi
