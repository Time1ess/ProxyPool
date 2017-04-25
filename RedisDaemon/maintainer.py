#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 16:58
# Last modified: 2017-04-25 22:05
# Filename: maintainer.py
# Description:
import time

from concurrent.futures import ThreadPoolExecutor

import redis

from utils import test_proxy_alive, rookie_callback, available_callback


def maintain(conn, log_interval=5):
    futures = set()
    key_cb = {
        'rookies_checking': rookie_callback(conn, futures),
        'availables_checking': available_callback(conn, futures)
    }
    print('Maintain started.')
    log_fmt = 'Rookies: {:5d}, Availables: {:5d}, Futures: {:5d}'
    last_log = time.time()
    with ThreadPoolExecutor(500) as executor:
        while True:
            if conn.get('system_status') == 'finished':
                print('Detected system finish signal, canceling works')
                for future in futures:
                    future.cancel()
                break
            for idx, (check_key, callback) in enumerate(key_cb.items()):
                check_time = time.time()
                proxies = conn.zrangebyscore(check_key, 0, check_time,
                                             withscores=True)
                conn.zremrangebyscore(check_key, 0, check_time)
                for proxy, score in proxies:
                    key = 'proxy_info:'+proxy
                    protocol = conn.hget(key, 'protocol')
                    future = executor.submit(test_proxy_alive, proxy, protocol)
                    futures.add(future)
                    future.add_done_callback(callback)
            rookies_num = conn.zcard('rookies_checking')
            availables_num = conn.scard('available_proxies')
            now = time.time()
            if now - last_log >= log_interval:
                last_log = now
                print(log_fmt.format(
                    rookies_num, availables_num, len(futures)))
    print('Maintain finished.')


if __name__ == '__main__':
    conn = redis.Redis(decode_responses=True)
    maintain(conn)
