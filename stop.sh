#!/bin/bash
echo "Try to kill all relevant processes..."
pid_bash_scrapy=`ps aux|grep "bash -c cd ProxyCrawl;scrapy crawlall"|grep -v grep|awk '{print $2}'`
pid_scrapy=`ps aux|grep "scrapy crawlall"|grep -v grep|awk '{print $2}'`
pid_bash_flask=`ps aux|grep "bash -c cd ProxyWeb;python3 pp_console.py"|grep -v grep|awk '{print $2}'`
pid_flask=`ps aux|grep "pp_console.py"|grep -v grep|awk '{print $2}'`

sudo kill -9 $pid_bash_scrapy
sudo kill -9 $pid_scrapy
sudo kill -9 $pid_bash_flask
sudo kill -9 $pid_flask
echo "Done."
