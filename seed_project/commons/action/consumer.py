#-*- encoding: utf-8 -*-
'''
consumer.py
Created on 2019/11/19 21:36
Copyright (c) 2019/11/19,ZZ 版权所有.
@author: ZZ
'''

import threading, random, time, traceback

from commons.util.log_util import LogUtil
from commons.action.base_consumer_action import ConsumerAction


class Consumer(threading.Thread):
    '''
    消费线程，用于从队列获得消费动作对象，然后调用消费动作对象的action()进行消费
    '''

    def __init__(self, queue, thread_name, max_sleep_time, max_retry_num):
        '''

        :param queue:       队列对象
        :param thread_name:  消费线程名称
        :param sleep_time:  每次消费后的休眠时间
        :param max_retry_num:   每次失败后最多的重试次数
        :return:
        '''
        # 调用父类初始化对象，这样才能运行run方法
        super(self.__class__, self).__init__()

        self.queue = queue
        self.thread_name = thread_name
        self.max_sleep_time = max_sleep_time
        self.max_retry_num = max_retry_num

        # 初始化日志
        self.logger = LogUtil().get_logger(self.thread_name, self.thread_name)

    def run(self):
        '''
        线程体
        :return:
        '''
        while True:
            try:
                # 随机休眠的时间
                random_sleep_time = round(random.uniform(0.2, self.max_sleep_time))
                # 线程开始时间
                start_time = time.time()

                # 从队列里取c_action对象
                c_action = self.queue.get()
                # 校验
                if not isinstance(c_action, ConsumerAction):
                    raise Exception("%s is not ConsumerAction instance" % c_action)

                # 调用c_action对象的action 方法消费
                result = c_action.action(self.thread_name)
                # 线程结束时间
                end_time = time.time()

                run_time = end_time - start_time

                success_flag = result[0]
                success_str = "SUCCESS" if result[0] else "FAIL"

                self.logger.info("thread.name=[%s], run_time=%.2f s, sleep_time=%.2f s, retry_times=%d, "
                                 "result=%s, detail=%s" %
                                 (self.thread_name, run_time, random_sleep_time, c_action.current_retry_num+1,
                                  success_str, result[1:]))

                # 如果消费失败，可以进行重试
                if not success_flag and c_action.current_retry_num < self.max_retry_num - 1:

                    c_action.current_retry_num += 1
                    # 把c_action 还回队列
                    self.queue.put(c_action)

                # 标记本次从队列里取出的c_action 已经执行完成
                self.queue.task_done()
                # 随机休眠

                time.sleep(random_sleep_time)

            except Exception, err:
                traceback.print_exc(err)
                self.logger.exception(err)