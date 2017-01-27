./segment.sh $1 > segmented
python3 desc_finder_trainer.py segmented $2/desc_model
./cat_trainer.sh segmented $2

