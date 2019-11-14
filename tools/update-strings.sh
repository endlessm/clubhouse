#!/bin/bash -e
#
# Convience script to update the CSV strings files for the quests, episodes, and items.
#
# Copyright (c) 2019 Endless Mobile Inc.
#
# Authors: Joaquim Rocha <jrocha@endlessm.com>
#

ARGS=$(getopt -o h \
  -l "push,help" \
  -n "$0" -- "$@")
eval set -- "$ARGS"

usage() {
    cat <<EOF
Usage: $0 [OPTION]
Update the strings CSV files.

  --push                    Push to the branch specified in GIT_BRANCH or otherwise to master, if any commits were created
  -h, --help                Display this help and exit

EOF
}

PUSH=false

while true; do
    case "$1" in
    --push)
        PUSH=true
        shift
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    --)
        shift
        break
        ;;
    *)
        echo "Unrecognized option \"$1\"" >&2
        exit 1
        ;;
    esac
done

if [ $# -ne 0 ]; then
  echo "Unrecognized arguments: $@" >&2
  exit 1
fi

branch_name=${GIT_BRANCH:-'origin/master'}
# Strip "origin/"
branch_name=${branch_name#origin/}

# Try to update the branch in case a remote one exists already.
git pull --rebase origin HEAD 2> /dev/null || true

remote_hash=$(git rev-parse origin/$branch_name 2> /dev/null) || true

./tools/get-strings-file --commit
./tools/get-info-file episodes --commit
./tools/get-info-file quests_items --commit
./tools/get-info-file achievements --commit
./tools/get-info-file newsfeed --commit

new_hash=$(git rev-parse HEAD)
if [ "$remote_hash" = "$new_hash" ]; then
    echo "Nothing to update"
    exit 0
fi

if $PUSH; then
    # Try to update again since getting the files could have taken some time and this way we
    # minimize the chances of getting outdated and failing to push.
    git pull --rebase origin $branch_name 2> /dev/null || true
    echo "Pushing string updates $(git rev-parse HEAD) to $branch_name remote branch"
    git push origin HEAD:$branch_name
fi
