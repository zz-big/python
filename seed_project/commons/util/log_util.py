#-*- encoding: utf-8 -*-
'''
log_util.py
Created on 2019/11/19 19:40
Copyright (c) 2019/11/19,ZZ 版权所有.
@author: ZZ
'''

from logging.handlers import TimedRotatingFileHandler
import logging
from configs import config
import content


class LogUtil:
    base_logger = content._NULL_STR

    log_dict = {}

    def get_base_logger(self):
        if LogUtil.base_logger == content._NULL_STR:
            LogUtil.base_logger = self.__get_logger('info', 'info')
        return LogUtil.base_logger

    def get_logger(self, log_name, file_name):
        key = log_name + file_name
        if not LogUtil.log_dict.has_key(key):
            LogUtil.log_dict[key] = self.__get_logger(log_name, file_name)
        return LogUtil.log_dict[key]

    def __get_new_logger(self, log_name, file_name):
        l = LogUtil()
        l.__get_logger(log_name, file_name)
        return l

    def __get_logger(self, log_name, file_name):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)

        fh = TimedRotatingFileHandler(config._LOG_DIR % (file_name), 'D')
        #fh = TimedRotatingFileHandler(config._LOG_DIR % (file_name), 'S', backupCount=5)
        #fh.suffix = '%Y%m%d.log'
        # 设置logger日志的级别
        fh.setLevel(logging.INFO)
        # 创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        return self

    def info(self, msg):
        self.logger.info(msg)
        self.logger.handlers[0].flush()

    def error(self, msg):
        self.logger.error(msg)
        self.logger.handlers[0].flush()

    def exception(self, msg='Exception Logged'):
        self.logger.exception(msg)
        self.logger.handlers[0].flush()

# if __name__ == '__main__':
#     b = LogUtil().get_base_logger()
#     import time
#     while True:
#         b.info('11')
#         b.error('22')
#
#         try:
#             1/0
#         except:
#             b.exception()
#             time.sleep(5)
