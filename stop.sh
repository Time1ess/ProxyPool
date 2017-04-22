#!/bin/bash
echo "Try to kill all relevant processes..."
pid_maintainer=`ps aux|grep maintainer.py|grep -v grep|awk '{print $2}'`
pid_scrapy=`ps aux|grep scrapy|grep -v grep|awk '{print $2}'`

sudo kill -9 $pid_maintainer
for pid in $pid_scrapy
do
    sudo kill -9 $pid
done
echo "Done."
