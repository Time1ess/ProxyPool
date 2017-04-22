#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 15:51
# Last modified: 2017-04-19 19:57
# Filename: pipelines.py
# Description:
# Define your item pipelines here
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time

import redis

from scrapy.exceptions import DropItem

from ProxyCrawl.items import ProxyItem


class ProxycrawlPipeline(object):
    def process_item(self, item, spider):
        return item


class ProxyItemPipeline:
    def open_spider(self, spider):
        self.conn = redis.Redis()

    def process_item(self, item, spider):
        if not isinstance(item, ProxyItem):
            return item
        if self.conn.sismember('rookie_proxies', item['proxy']) or\
                self.conn.sismember('available_proxies', item['proxy']):
            raise DropItem('Already in the waiting list')
        self.conn.sadd('rookie_proxies', item['proxy'])
        self.conn.zadd('rookies_checking', item['proxy'], time.time())
        key = 'proxy_info:'+item['proxy']
        self.conn.hset(key, 'proxy', item['proxy'])
        self.conn.hset(key, 'ip', item['ip'])
        self.conn.hset(key, 'port', item['port'])
        self.conn.hset(key, 'addr', item['addr'])
        self.conn.hset(key, 'mode', item['mode'])
        self.conn.hset(key, 'protocol', item['protocol'])
        self.conn.hset(key, 'validation_time', item['validation_time'])
        self.conn.hset(key, 'failed_times', 0)
        self.conn.hset(key, 'latency', 1000)
        return item
