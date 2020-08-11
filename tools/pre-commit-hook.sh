#!/bin/sh
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

source_dir="$(git rev-parse --show-toplevel)"

$source_dir/tools/run-lint || exit
if [ -z $SKIP_COMPILE_CSS ]; then
    $source_dir/tools/check-css || true
fi
if [ -z $SKIP_STRINGS_CHECK ]; then
    $source_dir/tools/check-strings || true
fi
