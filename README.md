# ProxyPool

---
> This tool is in developing and `README` may be out-dated.

[阅读中文版本(Read in Chinese)](README_CN.md)

An Python implementation of proxy pool.

`ProxyPool` is a tool to create a proxy pool with [Scrapy](https://scrapy.org) and [Redis](http://redis.io), it will automatically add new available proxies to pool and maintain the pool to delete unusable proxies.

This tool currently only get available proxies from 4 sources, I would add more sources in the future.

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
* Flask 0.12

I have not tested other versions of above packages, but I think it works fine for most users.

## Features

* Automatically add new available proxies
* Automatically delete unusable proxies
* Less coding work by adding crawl rule, improve scalability

## How-to

To start the tool, simply:
> $ ./start.sh

It will start *Crawling service*、*Pool maintain service*、*Maintain schedule service*、*Rule Maintain service* and *Web console*

To stop the tool, simply:
> $ sudo ./stop.sh

To add support for crawling more sites for proxies, this tool provides a usual crawling structure which should work for most free proxies site:

1. Start the tool
2. Open [Web console](http://localhost:5000)(default port:5000)
3. Switch to **Rule management** page
4. Click **New rule** button
5. Finish the form and submit
	* `rule_name` will be used to distinguish different rules
	* `url_fmt` will be used to generate crawling pages, it's often that the coding rule of these free proxy providing website is something like `xxx.com/yy/5`
	* `row_xpath` will be used to extract a data row from page content.
	* `host_xpath` will be used to extract proxy ip from a data row extracted earlier.
	* `port_xpath` will be used to extract proxy port.
	* `addr_xpath` will be used to extract proxy address.
	* `mode_xpath` will be used to extract proxy mode.
	* `proto_xpath` will be used to extract proxy protocol.
	* `vt_xpath` will be used to extract proxy validation time.
	* `max_page` will be used to control the size of crawling pages.
	* Above `xpath`s can be set to `null` to get a default `unknown` value.
6. Once the form is submitted the rule will be applied automatically and start a new crawling process.

## Data in Redis

All proxy information are stored in Redis, the configuration of Redis is not necessary to this tool.

### Rule(hset)

key|description
:---|:---
name|..
url_fmt|format: http://www.kuaidaili.com/free/intr/{}
row_xpath|format: //div[@id="list"]/table//tr
host_xpath|format: td[1]/text()
port_xpath|..
addr_xpath|..
mode_xpath|..
proto_xpath|..
vt_xpath|..
max_page|a int

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

### Jobs(list)

FIFO queue, format:`cmd|rule_name`, tell *Rule maintain service* how to deal with the rule-specific spider's action such as start、pause、stop and delete.

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

## Retrieve a available proxy for others

To retrieve currently available proxy, Just get one from `available_proxies` with any Redis client.
An scrapy middleware example:

```Python
class RandomProxyMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        s.conn = redis.Redis(decode_responses=True)
        return s

    def process_request(self, request, spider):
        proxies = list(self.conn.smembers('available_proxies'))
        if proxies:
            while True:
                proxy = choice(proxies)
                if proxy.startswith('http'):
                    break
            request.meta['proxy'] = proxy
```