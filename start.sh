#!/bin/bash
echo "Starting crawler..."
nohup bash -c "cd ProxyCrawl;scrapy crawlall" >/dev/null 2>&1 &
