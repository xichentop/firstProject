#!/bin/sh
#takes a segmentated text as input and outputs a cat.classifier using MaxEnt trainer 
#cmd format: ./cat_trainer.sh training_input_file model_dir
export PATH=$PATH:/NLP_TOOLS/tool_sets/mallet/latest/bin
export CLASSPATH=.:/NLP_TOOLS/tool_sets/mallet/latest/lib/mallet-deps.jar
python data_prep.py $1 'train' > train.feat.input
mallet import-file --input train.feat.input --output train.feat.vectors
mallet train-classifier --trainer MaxEnt --input train.feat.vectors --output-classifier $2/cat.classifier 1>log.stdout 2>log.stderr 
#end
