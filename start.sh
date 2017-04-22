#!/bin/bash
echo "Starting maintainer..."
nohup python3 RedisDaemon/maintainer.py >maintain.log 2>&1 &
cd ProxyCrawl
echo "Starting crawler..."
nohup scrapy crawl kuaidaili >../kuaidaili.log 2>&1 &
nohup scrapy crawl kuaidaili2 >../kuaidaili2.log 2>&1 &
nohup scrapy crawl xici >../xici.log 2>&1 &
