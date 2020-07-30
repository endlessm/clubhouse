#!/bin/bash -e
##
## Copyright © 2020 Endless OS Foundation LLC.
##
## This file is part of clubhouse
## (see https://github.com/endlessm/clubhouse).
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with this program; if not, write to the Free Software Foundation, Inc.,
## 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
##

# Convience script to update the CSV strings files and compile the CSS.

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

./tools/compile-css --commit
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
