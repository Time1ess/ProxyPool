#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 18:43
# Last modified: 2017-04-22 19:40
# Filename: utils.py
# Description:
import time 

from urllib import request as Request
from concurrent.futures import CancelledError


def test_proxy_alive(proxy, protocol, url='http://www.baidu.com', timeout=10):
    request = Request.Request(url)
    request.set_proxy(proxy, protocol)
    try:
        response = Request.urlopen(request, timeout=timeout)
    except Exception as e:
        return (proxy, protocol, False)
    return (proxy, protocol, True)


def rookie_callback(conn, futures):
    def _wrapper(future):
        try:
            proxy, protocol, succeed = future.result()
        except CancelledError:
            return
        key = 'proxy_info:' + proxy
        conn.zrem('rookies_checking', proxy)
        if succeed:
            conn.hset(key, 'failed_times', 0)
            # Move proxy from rookies to availables
            conn.sadd('available_proxies', '{}://{}'.format(protocol, proxy))
            conn.srem('rookie_proxies', proxy)
            conn.zadd('availables_checking', proxy, time.time())
            print('New Available Proxy: {:50s}'.format(proxy))
        else:
            if conn.hincrby(key, 'failed_times', 1) < 3:
                # If not reach the maximum of failed_times
                # Since it is not important so re-check it after 10 seconds
                conn.zadd('rookies_checking', proxy, time.time() + 10)
            else:
                conn.srem('rookie_proxies', proxy)
                conn.delete(key)
                print('Bad Proxy: {:50s}'.format(proxy))
        futures.remove(future)
    return _wrapper


def available_callback(conn, futures):
    def _wrapper(future):
        try:
            proxy, protocol, succeed = future.result()
        except CancelledError:
            return
        key = 'proxy_info:' + proxy
        conn.zrem('availables_checking', proxy)
        if succeed:
            conn.hset(key, 'failed_times', 0)
            conn.zadd('availables_checking', proxy, time.time() + 30)
            print('Alive Proxy: {:50s}'.format(proxy))
        else:
            if conn.hincrby(key, 'failed_times', 1) < 3:
                conn.zadd('rookies_checking', proxy, time.time())
            else:
                conn.srem('available_proxies', '{}://{}'.format(protocol,
                                                                proxy))
                conn.delete(key)
                print('Proxy dead: {:50s}'.format(proxy))
        futures.remove(future)
    return _wrapper
