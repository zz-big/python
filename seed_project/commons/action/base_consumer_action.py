#-*- encoding: utf-8 -*-
'''
base_consumer_action.py
Created on 2019/11/19 20:56
Copyright (c) 2019/11/19,ZZ 版权所有.
@author: ZZ
'''


class ConsumerAction(object):
    '''
    这是消费者的动作基类，用于制定标准
    '''

    def __init__(self):
        # 当前重试次数
        self.current_retry_num = 0

    def action(self):
        '''
        用于消费者动作对象进行消费，这是个抽象方法，由子类去实现
        :return:
        '''

        pass

    def result(self, success_flag, *values):
        # *values 将多余的数据变成元组
        # 若果没有重写success_action 或者 fail_action这两个方法不会执行
        if success_flag:
            self.success_action(values)
        else:
            self.fail_action(values)

        results = []

        results.append(success_flag)
        for v in values:
            results.append(v)
        return results

    def success_action(self, values):
        '''
        这是action成功后的动作，是抽象方法，具体由子类去实现
        :param values:
        :return:
        '''
        pass

    def fail_action(self, values):
        '''
        这是action失败后的动作，是抽象方法，具体由子类去实现
        :param values:
        :return:
        '''
        pass
