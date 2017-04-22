#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 15:12
# Last modified: 2017-04-19 16:35
# Filename: items.py
# Description:
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy.loader.processors import Join, MapCompose, TakeFirst


class ProxycrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ProxyItem(scrapy.Item):
    proxy = scrapy.Field()
    ip = scrapy.Field()
    port = scrapy.Field()
    addr = scrapy.Field()
    mode = scrapy.Field()
    protocol = scrapy.Field()
    validation_time = scrapy.Field()
