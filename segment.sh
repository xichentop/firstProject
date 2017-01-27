input=$1
for d in `ls $input`
do
	if [[ "$d" == *"annot"* ]]
	then
		echo $d
		for i in {1..15}
		do
			text="$input/$d/3-txt/d$i.txt"
			out="$input/$d/4-output/d$i.out"
			if [ -f $text ]
			then
				if [ -f $out ]
				then
					python3 segment.py $text $out
			
				fi
			fi
		done
	fi
done
