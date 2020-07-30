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
for i in $(cat ../sizes)
do
    for j in *.svg
    do
        # mid point
        j=$(echo $j | sed 's/.svg//g')
        fname="${j}_${i}"
        w=$(file $fname.png | cut -d"," -f2 | cut -d"x" -f1)
        h=$(file $fname.png | cut -d"," -f2 | cut -d"x" -f2)
        mw=$(echo $w / 2 | bc)
        mh=$(echo $h / 2 | bc)
        echo $i $mw $mh ${fname}.png 100
    done
done
