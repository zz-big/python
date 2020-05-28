#-*- encoding: utf-8 -*-
'''
update_test.py
Created on 2019/11/22 15:52
Copyright (c) 2019/11/22
'''
from configs.config import _HAINIU_DB
from commons.util.db_util import DBUtil

db_util =  DBUtil(_HAINIU_DB)
import datetime,traceback
try:



    #---on DUPLICATE KEY 的SQL例子---------------
    insert_web_seed_sql = """
    insert into hainiu_web_seed (url, md5,domain, host,category,last_crawl_time) values (%s,%s,%s,%s,%s,%s)
    on DUPLICATE KEY UPDATE fail_times=fail_times+1,fail_ip=%s, last_crawl_time=%s;
"""
    dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md5 = 'a1'
    params = ['www.baidu.com', md5, "com",'baidu.com', '搜索', dt, '160',dt]
    db_util.execute(insert_web_seed_sql, params)

    # print "insert sql success"
except Exception,message:
    db_util.rollback_close()
    traceback.print_exc()
    # logger.exception(message)