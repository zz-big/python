#-*- encoding: utf-8 -*-
'''
config.py
Created on 2019/11/19 19:29
Copyright (c) 2019/11/19,ZZ 版权所有.
@author: ZZ
'''
#日志地址
_LOG_DIR = 'E:\python_workspaces\logs/%s'
#数据地址
_LOCAL_DATA_DIR = 'E:\python_workspaces\data/%s'
#数据地址redis xpath
_LOCAL_DATA_DIR_REDIS = 'E:\python_workspaces\data/%s'

# 数据库配置 测试
_ZZ_DB = {'HOST':'localhost', 'USER':'root', 'PASSWD':'root1', 'DB':'db', 'CHARSET':'utf8', 'PORT':3306}
# _ZZ_DB = {'HOST':'localhost', 'USER':'root', 'PASSWD':'root1', 'DB':'spark', 'CHARSET':'utf8', 'PORT':3306}

# NAME, P_SLEEP_TIME, C_MAX_NUM, C_MAX_SLEEP_TIME, C_RETRY_TIMES
_QUEUE_DEMO = {'NAME':'demo', 'P_SLEEP_TIME': 5, 'C_MAX_NUM': 1, 'C_MAX_SLEEP_TIME': 3, 'C_RETRY_TIMES':3}

_QUEUE_ZZ = {'NAME':'web', 'P_SLEEP_TIME': 1, 'C_MAX_NUM': 5,
                 'C_MAX_SLEEP_TIME': 1, 'C_RETRY_TIMES':3, 'MAX_FAIL_TIMES': 6,
                 'LIMIT_NUM': 5}


_QUEUE_APPLE = {'NAME':'apple', 'P_SLEEP_TIME': 1, 'C_MAX_NUM': 3, 'C_MAX_SLEEP_TIME': 3, 'C_RETRY_TIMES':3}


#报警电话
_ALERT_PHONE = '110'

#KAFKA队列配置
_KAFKA_CONFIG = {'HOST':'nn1.hadoop:9092,nn2.hadoop:9092,s1.hadoop:9092','TOPIC':'zz'}