#!/bin/bash
echo "Starting maintainer..."
nohup python3 -u RedisDaemon/maintainer.py >maintain.log 2>&1 &
cd ProxyCrawl
echo "Starting crawler..."
nohup bash -c "while true;do scrapy crawlall;done" >../crawler.log 2>&1 &
