for i in $(cat ../sizes)
do
    for j in HoverB HoverC
    do
        # mid point
        fname="${j}_${i}"
        mw=0
        mh=0
        echo $i $mw $mh ${fname}.png 200
    done
done
