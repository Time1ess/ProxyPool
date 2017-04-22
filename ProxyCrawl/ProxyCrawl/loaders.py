#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 15:33
# Last modified: 2017-04-19 19:53
# Filename: loaders.py
# Description:
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Compose


def clean_addr(addr):
    return addr.strip('\n ')


def normalize_addr(addr):
    if not addr:
        return '未知'
    return addr


class ProxyItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

    proxy_out = Join(':')
    addr_out = Compose(Join(), clean_addr, normalize_addr)
    protocol_out = Compose(Join(), str.lower)
