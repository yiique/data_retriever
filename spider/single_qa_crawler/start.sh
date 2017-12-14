#!/bin/sh
round=1000
for i in $(seq 0 12)
do
    arg1=`expr $i \* $round`
    arg2=`expr $i \* $round + $round`
    nohup python -u sqa_manager.py $arg1 $arg2 $i > nohup.a$i &
done
