#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 16:58
# Last modified: 2017-04-27 18:40
# Filename: maintainer.py
# Description:
import time

from concurrent.futures import ThreadPoolExecutor

import redis

from utils import test_proxy_alive, rookie_callback, available_callback


def maintain(conn):
    futures = set()
    key_cb = {
        'rookies_checking': rookie_callback(conn, futures),
        'availables_checking': available_callback(conn, futures)
    }
    with ThreadPoolExecutor(500) as executor:
        last_check_time = 0
        while True:
            for idx, (check_key, callback) in enumerate(key_cb.items()):
                check_time = time.time()
                proxies = conn.zrangebyscore(check_key, last_check_time,
                                             check_time)
                for proxy in proxies:
                    key = 'proxy_info:'+proxy
                    protocol = conn.hget(key, 'protocol')
                    future = executor.submit(test_proxy_alive, proxy, protocol)
                    futures.add(future)
                    future.add_done_callback(callback)
            last_check_time = check_time
            time.sleep(0.1)
            conn.set('futures', len(futures))


if __name__ == '__main__':
    conn = redis.Redis(decode_responses=True)
    maintain(conn)
