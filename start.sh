#!/bin/bash
echo "Starting crawler..."
nohup bash -c "cd ProxyCrawl;scrapy crawlall" >/dev/null 2>&1 &
nohup bash -c "cd ProxyWeb;python3 pp_console.py" >/dev/null 2>&1 &
