#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 15:51
# Last modified: 2017-04-30 11:05
# Filename: pipelines.py
# Description:
# Define your item pipelines here
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time

import redis

from scrapy.exceptions import DropItem

from ProxyCrawl.items import ProxyItem


class ProxyItemPipeline:
    def open_spider(self, spider):
        self.conn = redis.Redis()

    def process_item(self, item, spider):
        if not isinstance(item, ProxyItem):
            return item
        if not item.get('ip', None) or not item.get('port', None):
            raise DropItem('Bad ProxyItem')
        item.setdefault('addr', 'Unknown')
        item.setdefault('mode', 'Unknown')
        item.setdefault('protocol', 'http')
        item.setdefault('validation_time', 'Unknown')
        proxy = '{}://{}'.format(item['protocol'], item['proxy'])
        if self.conn.sismember('rookie_proxies', proxy) or\
                self.conn.sismember('available_proxies', proxy) or\
                self.conn.sismember('lost_proxies', proxy) or\
                self.conn.sismember('dead_proxies', proxy):
            raise DropItem('Already in the waiting list')
        key = 'proxy_info:'+item['proxy']
        pipe = self.conn.pipeline(False)
        pipe.sadd('rookie_proxies', proxy)
        pipe.zadd('rookies_checking', item['proxy'], time.time())
        pipe.hmset(key, dict(item))
        pipe.hset(key, 'failed_times', 0)
        pipe.execute()
        return item
