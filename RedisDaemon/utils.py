#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 18:43
# Last modified: 2017-04-27 18:40
# Filename: utils.py
# Description:
import time

from urllib import request as Request
from concurrent.futures import CancelledError


def test_proxy_alive(proxy, protocol, url='http://www.baidu.com', timeout=10):
    request = Request.Request(url)
    request.set_proxy(proxy, protocol)
    try:
        Request.urlopen(request, timeout=timeout)
    except Exception as e:
        return (proxy, protocol, False)
    return (proxy, protocol, True)


def rookie_callback(conn, futures):
    def _wrapper(future):
        futures.remove(future)
        try:
            proxy, protocol, succeed = future.result()
        except CancelledError:
            return
        key = 'proxy_info:' + proxy
        if succeed:
            pipe = conn.pipeline(False)
            pipe.zrem('rookies_checking', proxy)
            pipe.hset(key, 'failed_times', 0)
            # Move proxy from rookies to availables
            pipe.smove('rookie_proxies', 'available_proxies',
                       '{}://{}'.format(protocol, proxy))
            pipe.zadd('availables_checking', proxy, time.time() + 30)
            pipe.execute()
        else:
            if conn.hincrby(key, 'failed_times', 1) < 3:
                # If not reach the maximum of failed_times
                # Since it is not important so re-check it after 10 seconds
                conn.zadd('rookies_checking', proxy, time.time() + 10)
            else:
                pipe = conn.pipeline(False)
                pipe.zrem('rookies_checking', proxy)
                pipe.smove('rookie_proxies', 'dead_proxies',
                           '{}://{}'.format(protocol, proxy))
                pipe.execute()
    return _wrapper


def available_callback(conn, futures):
    def _wrapper(future):
        futures.remove(future)
        try:
            proxy, protocol, succeed = future.result()
        except CancelledError:
            return
        key = 'proxy_info:' + proxy
        pipe = conn.pipeline(False)
        if succeed:
            pipe.hset(key, 'failed_times', 0)
            pipe.zadd('availables_checking', proxy, time.time() + 30)
            pipe.smove('lost_proxies', 'available_proxies',
                       '{}://{}'.format(protocol, proxy))
        else:
            if conn.hincrby(key, 'failed_times', 1) < 3:
                pipe.zadd('availables_checking', proxy, time.time() + 10)
                pipe.smove('available_proxies', 'lost_proxies',
                           '{}://{}'.format(protocol, proxy))
            else:
                pipe.zrem('availables_checking', proxy)
                pipe.smove('lost_proxies', 'dead_proxies',
                           '{}://{}'.format(protocol, proxy))
                pipe.delete(key)
        pipe.execute()
    return _wrapper
