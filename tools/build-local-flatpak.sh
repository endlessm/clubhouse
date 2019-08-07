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

# If the GIT_CLONE_BRANCH var is not defined, we replace it so that it'll in fact set the
# git branch to "" but add also "type": "dir" so it builds from the current directory.
# This is hacky but until we need to keep git as the source type, then it's the less intrusive.
GIT_CLONE_BRANCH=${GIT_CLONE_BRANCH:-'", "type": "dir'}
REPO=${REPO:-repo}
BRANCH=${BRANCH:-master}
RUN_LINT=${CLUBHOUSE_BUILD_RUN_LINT:-true}
RUN_TESTS=${CLUBHOUSE_BUILD_RUN_TESTS:-true}

pre_commit_target=$(readlink "$precommit_hook_path") || true
if [ "$pre_commit_target" = "$precommit_hook_file" ]; then
    RUN_LINT="false"
fi

sed -e "s|@GIT_CLONE_BRANCH@|${GIT_CLONE_BRANCH}|g" \
    -e "s|@BRANCH@|${BRANCH}|g" \
    -e "s|@RUN_TESTS@|${RUN_TESTS}|g" \
    -e "s|-Drun-lint=true|-Drun-lint=$RUN_LINT|g" \
  com.endlessm.Clubhouse.json.in > com.endlessm.Clubhouse.json

# Add any extra options from the user to the flatpak-builder command (e.g. --install)
flatpak-builder build --user --force-clean com.endlessm.Clubhouse.json --repo=${REPO} $@ || ret=$?

# Reload the GSS to make sure we have the freshest changes in case it was modified for testing
# this Clubhouse build.
echo
echo Restarting the GSS
gdbus call -e -d com.endlessm.GameStateService -o /com/endlessm/GameStateService -m com.endlessm.GameStateService.Reload > /dev/null

popd

exit $ret