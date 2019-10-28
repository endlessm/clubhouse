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
