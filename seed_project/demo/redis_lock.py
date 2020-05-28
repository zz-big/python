#-*- encoding: utf-8 -*-
'''
redis_lock.py
Created on 2019/8/14 8:31
Copyright (c) 2019/8/14
'''

import threading,time

from commons.util.redis_utill import RedisUtill
def task(n):
    time.sleep(1)
    is_get_lock = ru.get_lock("lock_key", 2,10)
    if is_get_lock:
        for i in range(1,n):
            print i
    else:
        print "锁超过最大超时时间"


    # 释放锁，如果不主动释放，会调用超时释放锁的逻辑
    ru.release("lock_key")


ru = RedisUtill()

for i in range(5):
    t = threading.Thread(target=task,args=[3,])
    t.start()

