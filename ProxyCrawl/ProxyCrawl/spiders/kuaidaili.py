#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 19:46
# Last modified: 2017-04-25 18:50
# Filename: kuaidaili.py
# Description:
import scrapy

from scrapy.http import Request

from ProxyCrawl.items import ProxyItem
from ProxyCrawl.loaders import ProxyItemLoader
from ProxyCrawl.spiders.base_spiders import BaseSpider


class KuaidailiSpider(BaseSpider):
    name = "kuaidaili"
    url_fmt = 'http://www.kuaidaili.com/free/intr/{}'
    row_xpath = '//div[@id="list"]/table//tr'
    host_xpath = 'td[1]/text()'
    port_xpath = 'td[2]/text()'
    addr_xpath = 'td[5]//text()'
    mode_xpath = 'td[3]/text()'
    proto_xpath = 'td[4]/text()'
    vt_xpath = 'td[7]/text()'


class KuaidailiSpider2(KuaidailiSpider):
    name = "kuaidaili2"
    url_fmt = 'http://www.kuaidaili.com/free/inha/{}'
