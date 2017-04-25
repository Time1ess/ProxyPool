#!/bin/bash
echo "Try to kill all relevant processes..."
pid_maintainer=`ps aux|grep maintainer.py|grep -v grep|awk '{print $2}'`
pid_bash=`ps aux|grep "bash -c while true;do scrapy crawlall;done"|grep -v grep|awk '{print $2}'`
pid_scrapy=`ps aux|grep "scrapy"|grep -v grep|awk '{print $2}'`

sudo kill -9 $pid_maintainer
sudo kill -9 $pid_bash
sudo kill -9 $pid_scrapy
echo "Done."
