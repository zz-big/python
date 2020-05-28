#-*- encoding: utf-8 -*-
'''
Producer.py
Created on 2019/11/19 21:36
Copyright (c) 2019/11/19,ZZ 版权所有.
@author: ZZ
'''
import threading, traceback, time

from commons.util.log_util import LogUtil
from commons.action.consumer import Consumer
from commons.action.base_producer_action import ProducerAction


class Producer(threading.Thread):

    def __init__(self, queue, q_name, p_action, p_sleep_time, c_max_num, c_max_sleep_time, c_max_retry_num):
        '''

        :param queue:       队列对象
        :param q_name:       队列名称
        :param p_action:      生产动作对象
        :param p_sleep_time:    每次生产后的休眠时间
        :param c_max_num:       消费者的最大线程数
        :param c_max_sleep_time:  每次运行后的最大休眠时间
        :param c_max_retry_num:    运行失败后的最大重试次数
        :return:
        '''

        super(self.__class__, self).__init__()
        self.queue = queue
        self.q_name = q_name
        self.p_action = p_action
        self.p_sleep_time = p_sleep_time
        self.c_max_num = c_max_num
        self.c_max_sleep_time = c_max_sleep_time
        self.c_max_retry_num = c_max_retry_num

        # 校验p_action是不是ProducerAction的子类的实例对象
        if not isinstance(self.p_action, ProducerAction):
            raise Exception("%s is not ProducerAction instance" % self.p_action)

        # 初始化日志对象
        self.logger = LogUtil().get_logger('producer_%s' % self.q_name, 'producer_%s' % self.q_name)

    def run(self):
        '''
        线程体
        :return:
        '''

        actions = []

        while True:
            try:
                # 线程开始时间
                start_time = time.time()

                # 通过p_action 生产消费动作对象列表
                if len(actions) == 0:
                    actions = self.p_action.queue_items()

                # 本次生产了多少对象
                total_num = len(actions)

                self.logger.info('queue.name = [producer_%s], current time produce %d actions'
                               % (self.q_name, total_num))

                # 一个一个的放入队列
                while True:
                    if len(actions) == 0:
                        break
                    # 通过q.unfinished_tasks的数 小于 消费者最大线程数，就往队列里放
                    if self.queue.unfinished_tasks < self.c_max_num:
                        c_action = actions.pop()
                        self.queue.put(c_action)

                # 线程结束时间
                end_time = time.time()
                # 本次从生产到全部放到队列的秒数
                run_time = end_time - start_time
                rate = int(float(total_num) * 60 / run_time)

                self.logger.info("queue.name=[producer_%s], total_num=%d, "
                                 "producer %d actions/min, sleep_time=%d" %
                                 (self.q_name, total_num, rate, self.p_sleep_time))

                # 休眠一下
                time.sleep(self.p_sleep_time)

            except Exception, err:
                traceback.print_exc(err)
                self.logger.exception(err)

    def start_work(self):

        # 创建和启动 消费线程对象
        self.logger.info("init and start %d consumer thread" % self.c_max_num)
        for i in range(1, self.c_max_num+1):
            c = Consumer(self.queue, "consumer_%s_%d" % (self.q_name, i), self.c_max_sleep_time, self.c_max_retry_num)
            c.start()
        # 启动生产线程
        self.start()
