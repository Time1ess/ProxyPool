#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 20:23
# Last modified: 2017-04-25 21:08
# Filename: base_spiders.py
# Description:
import scrapy

from scrapy.http import Request
from ProxyCrawl.items import ProxyItem
from ProxyCrawl.loaders import ProxyItemLoader


class BaseSpider(scrapy.Spider):
    name = None
    url_fmt = None
    row_xpath = None  # Extract one data row from response
    host_xpath = None  # Extract host from data row
    port_xpath = None  # Extract port from data row
    addr_xpath = None
    mode_xpath = None
    proto_xpath = None
    vt_xpath = None  # validation_time
    max_page = 100

    def __check_vals(self):
        if not all([
                self.name, self.url_fmt, self.row_xpath, self.host_xpath,
                self.port_xpath, self.addr_xpath, self.mode_xpath,
                self.proto_xpath, self.vt_xpath]):
            raise ValueError('Arguments not set properly')

    def __init__(self, *args, **kwargs):
        self.__check_vals()
        self.start_urls = [self.url_fmt.format(k)
            for k in range(1, self.max_page)]

    def parse(self, response):
        if response.status != 200:
            return None
        ip_list = response.xpath(self.row_xpath)[1:]
        for ip_item in ip_list:
            l = ProxyItemLoader(item=ProxyItem(), selector=ip_item)
            l.add_xpath('proxy', self.host_xpath)
            l.add_xpath('proxy', self.port_xpath)
            l.add_xpath('ip', self.host_xpath)
            l.add_xpath('port', self.port_xpath)
            l.add_xpath('addr', self.addr_xpath)
            l.add_xpath('mode', self.mode_xpath)
            l.add_xpath('protocol', self.proto_xpath)
            l.add_xpath('validation_time', self.vt_xpath)
            yield l.load_item()
