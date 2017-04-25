#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 15:33
# Last modified: 2017-04-25 21:43
# Filename: loaders.py
# Description:
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Join, Compose


def clean_addr(addr):
    return addr.strip('\n ')


def normalize_addr(addr):
    if not addr:
        return 'Unknown'
    return addr


def normalize(v):
    v.append('Unknown')
    return v


def normalize_proto(v):
    if not v:
        return ['http']
    else:
        return v


class ProxyItemLoader(ItemLoader):
    default_output_processor = Compose(normalize, TakeFirst())

    proxy_out = Join(':')
    addr_out = Compose(Join(), clean_addr, normalize_addr)
    protocol_out = Compose(normalize_proto, TakeFirst(), str.lower)
