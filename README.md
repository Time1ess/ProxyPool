# ProxyPool

---
[阅读中文版本(Read in Chinese)](README_CN.md)

An Python implementation of proxy pool.

`ProxyPool` is a tool to create a proxy pool with [Scrapy](https://scrapy.org) and [Redis](http://redis.io), it will automatically add new available proxies to pool and maintain the pool to delete unusable proxies.

This tool currently only get available proxies from 3 sources, I would add more sources in the future.

## Compatibility

This tool has been tested on **macOS Sierra 10.12.4** and **Ubuntu 16.04 LTS** successfully.

System Requirements:

* UNIX-Like systems(macOS, Ubuntu, etc..)

Fundamental Requirements:

* Redis 3.2.8
* Python 3.0+

Python package requirements:

* Scrapy 1.3.3
* redis 2.10.5

I have not tested other versions of above packages, but I think it works fine for most users.

## Features

* Automatically add new available proxies
* Automatically delete unusable proxies
* Scalability to add more crawling sites

## How-to

To start the tool, simply:
> $ ./start.sh

It will start *Pool Maintainer* and *Proxy Crawler*.

To stop the tool, simply:
> $ sudo ./stop.sh

To add support for crawling more sites for proxies:

1. Change location to **spiders**.

	> $ cd ProxyCrawl/ProxyCrawl/spiders

2. Create a new spider with scrapy command:

	> $ scrapy genspider [spider_name] [site_domain]

	or you can create a new `.py` file manully

3. Open the new spider file and change its inheirtance to `base_spider.BaseSpider`(if structure of the site you choose to crawl is not like the defaults, you can write your own logic)

4. Overwrite attribute `url_fmt` and method `parse` to fit with predefined logic.
	* `url_fmt` will be used to generate crawling pages, it's often that the coding rule of these free proxy providing website is something like `xxx.com/yy/5`
	* `parse` method should take care of the content of response and parse it to create new `ProxyItem` which has been defined in `items.py`

5. It's done, the tool will handle the rest, just start the tool.

## Data in Redis

All proxy information are stored in Redis, the configuration of Redis is not necessary to this tool.

### proxy_info(hset)

key|description
:---|:---
proxy|full proxy address, format: 127.0.0.1:80
ip|proxy ip, format: 127.0.0.1
port|proxy port, format: 80
addr|where is the proxy
mode|anonymous or not
protocol| HTTP or HTTPS
validation_time|source website checking time
failed_times|recently failed times
latency|proxy latency to source website

### rookies_proxies(set)

New proxies which have not been tested yet will be stored at here, a new proxy will be moved to `available_proxies` after successfully tested or will be deleted after maximum retry times reached.

### available_proxies(set)

Available proxies will be stored at here, every proxy will be tested whether it is available or not in certain time.

### availables_checking(zset)

Available proxies test queue, the score of these proxies is a timestamp to indicate its priority.

### rookies_checking(zset)

New proxies test queue, similar to `availables_checking`.

## How it work

### Getting new proxies

1. Crawling pages
2. Extract `ProxyItem` from content
3. Store `ProxyItem` in Redis

### Maintaining proxy pool

**New proxies**:

* Iterate over each of new proxies
	* Available	
		* Move to `available_proxies`
	* Unavailable 
		* Delete proxy

**Proxies in pool**:

* Iterate over each of proxies
	* Available	
		* Reset retry times and wait for next test
	* Unavailable 
		* Not reach maximum retry times
			* wait for next test
		* Maximum retry times reached
			* Delete proxy

To retrieve currently available proxy, Just get one from `available_proxies` with any Redis client.