#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 14:16
# Last modified: 2017-04-25 18:50
# Filename: xici.py
# Description:
import scrapy

from scrapy.http import Request

from ProxyCrawl.items import ProxyItem
from ProxyCrawl.loaders import ProxyItemLoader
from ProxyCrawl.spiders.base_spiders import BaseSpider


class XiciSpider(BaseSpider):
    name = "xici"
    url_fmt = 'http://www.xicidaili.com/nt/{}'
    row_xpath= '//table[@id="ip_list"]//tr'
    host_xpath = 'td[2]/text()'
    port_xpath = 'td[3]/text()'
    addr_xpath = 'td[4]//text()'
    mode_xpath = 'td[5]/text()'
    proto_xpath = 'td[6]/text()'
    vt_xpath = 'td[10]/text()'
