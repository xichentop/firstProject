input=$1
for d in `ls $input`
do
	if [[ "$d" == *"annot"* ]]
	then
		echo -n "" > dout_list.txt
		mkdir $3/$d
		mkdir $3/$d/4-output
		for i in {1..15}
		do
			text="$input/$d/3-txt/d$i.txt"
			if [ -f $text ]
			then
				python3 segment_decoder.py $text > d$i.segment
				python3 desc_finder_decoder.py d$i.segment $2/desc_model  d$i
				./cat_decoder.sh d$i $3/$d/4-output/d$i.out $2/cat.classifier
				echo "$3/$d/4-output/d$i.out" >> dout_list.txt
			fi
		done
		python3 summarizer.py dout_list.txt $3/$d/4-output/summary.out
	fi
done
