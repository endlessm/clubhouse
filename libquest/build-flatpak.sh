#!/bin/bash
set -e
set -x
rm -rf var metadata export build

BRANCH=${BRANCH:-master}
GIT_CLONE_BRANCH=${GIT_CLONE_BRANCH:-HEAD}
RUN_TESTS=${RUN_TESTS:-false}
REPO=${REPO:-repo}

sed \
  -e "s|@BRANCH@|${BRANCH}|g" \
  -e "s|@GIT_CLONE_BRANCH@|${GIT_CLONE_BRANCH}|g" \
  -e "s|\"@RUN_TESTS@\"|${RUN_TESTS}|g" \
  com.hack_computer.Libquest.json.in \
  > com.hack_computer.Libquest.json

flatpak-builder build --ccache com.hack_computer.Libquest.json --repo=${REPO}
flatpak install -y --reinstall ./${REPO} com.hack_computer.Libquest//${BRANCH}

