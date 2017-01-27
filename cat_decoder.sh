#!/bin/sh
#process test file and predicts category using the cat.classifier and regex; and generates d*.out files
#format: ./cat_decoder.sh test_input_file output_file cat.classifier 
export PATH=$PATH:/NLP_TOOLS/tool_sets/mallet/latest/bin
export CLASSPATH=.:/NLP_TOOLS/tool_sets/mallet/latest/lib/mallet-deps.jar
python data_prep.py $1 'test' > test.feat.input
mallet classify-file --input test.feat.input --output ml.result --classifier $3
python predict_cat.py ml.result ~/dropbox/16-17/570/project/annotation/category-list $1 > $2

#end
