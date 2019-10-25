for j in *.svg
do
    for i in $(cat ../sizes)
    do
        n=$(echo $j | sed 's/.svg//g')
        org.inkscape.Inkscape -e ${n}_${i}.png -h $i $j
    done
done
