#!/bin/bash
#
# Convenience script to build a Flatpak bundle with the local contents (the original manifest)
# builds from git so changes need to be committed.
#
# Copyright (c) 2018 Endless Mobile Inc.
#
# Author: Joaquim Rocha <jrocha@endlessm.com>
#

set -e

source_dir="$(git rev-parse --show-toplevel)"

# Import the precommit_hook_* vars
source "$source_dir/tools/setup-git-hooks"

pushd "$source_dir"
./katamari/tools/build-clubhouse || ret=$?

popd

exit $ret
