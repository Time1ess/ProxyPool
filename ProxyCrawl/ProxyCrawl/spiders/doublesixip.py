#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-25 18:58
# Last modified: 2017-04-25 21:19
# Filename: doublesixip.py
# Description:
import scrapy

from ProxyCrawl.spiders.base_spiders import BaseSpider


class DoubleSixipSpider(BaseSpider):
    name = "DoubleSixip"
    url_fmt = 'http://www.66ip.cn/{}.html'
    row_xpath= '//div[@id="main"]//tr'
    host_xpath = 'td[1]/text()'
    port_xpath = 'td[2]/text()'
    addr_xpath = 'td[3]/text()'
    mode_xpath = 'td[4]/text()'
    proto_xpath = 'null'
    vt_xpath = 'td[5]/text()'
