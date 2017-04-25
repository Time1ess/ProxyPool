#!/bin/bash
echo "Starting maintainer..."
nohup python3 RedisDaemon/maintainer.py >/dev/null 2>&1 &
cd ProxyCrawl
echo "Starting crawler..."
nohup scrapy crawlall >../crawler.log 2>&1 &
