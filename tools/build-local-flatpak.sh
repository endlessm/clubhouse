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
script_path=$0
source_dir="$(dirname "$script_path")/.."

pushd "$source_dir"

# If the GIT_CLONE_BRANCH var is not defined, we replace it so that it'll in fact set the
# git branch to "" but add also "type": "dir" so it builds from the current directory.
# This is hacky but until we need to keep git as the source type, then it's the less intrusive.
GIT_CLONE_BRANCH=${GIT_CLONE_BRANCH:-'", "type": "dir'}

sed -e "s|@GIT_CLONE_BRANCH@|${GIT_CLONE_BRANCH}|g" \
  com.endlessm.Clubhouse.json.in > com.endlessm.Clubhouse.json

# Add any extra options from the user to the flatpak-builder command (e.g. --install)
flatpak-builder build --user --force-clean com.endlessm.Clubhouse.json $@ || ret=$?

popd

exit $ret
