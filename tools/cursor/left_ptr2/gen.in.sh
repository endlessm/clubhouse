for i in $(cat ../sizes)
do
    # mid point
    fname="left_ptr_${i}"
    mw=0
    mh=0
    echo $i $mw $mh ${fname}.png
done
