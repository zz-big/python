#-*- encoding: utf-8 -*-
'''
base_producer_action.py
Created on 2019/11/19 20:57
Copyright (c) 2019/11/19,ZZ 版权所有.
@author: ZZ
'''

class ProducerAction(object):
    '''
    这是生产者动作基类，用于制定标准
    '''

    def queue_items(self):
        '''
        生产【消费动作对象】列表，这是各抽象方法，用于制定标准
        :return:
        '''
        pass