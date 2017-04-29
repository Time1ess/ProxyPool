#!/bin/bash
echo "Try to kill all relevant processes..."
pid_scrapy=`ps aux|grep "bash -c cd ProxyCrawl;scrapy crawlall"|grep -v grep|awk '{print $2}'`

sudo kill -9 $pid_scrapy
echo "Done."
