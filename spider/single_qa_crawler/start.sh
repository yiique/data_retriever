#!/bin/sh

for i in $(seq 1 23)
do
    nohup python -u sqa_manager.py 0*$i 1000*$i $i > nohup.$i &
done
