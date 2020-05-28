#-*- encoding: utf-8 -*-
'''
single_test.py
Created on 2019/3/19 9:14
Copyright (c) 2019/3/19
'''
import time,threading

print '---第一种单例模式不适合多线程---'
#第一种单例模式不适合多线程
class Singleton(object):
    def __init__(self):
        # print "__init__"
        import time
        time.sleep(1)

    #classmethod   标明为类的方法，而类的方法第一个参数是cls，对象方法的第一个参数的是self，类方法是属于类的，
    #              而对象方法是属于对象的，类方法是公用的。而对象方法是属于对象自己的。
    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(Singleton, "_instance"):
            Singleton._instance = Singleton()
        return Singleton._instance

# 单线程是可以用的单例
obj1 = Singleton.instance()
print obj1
obj2 = Singleton.instance()
print obj2
#但多线程时这个单例模式线程不安全
def task(arg):
    obj = Singleton.instance()
    print obj

for i in range(10):
    t = threading.Thread(target=task,args=[i,])
    t.start()

time.sleep(2)
print '2#' * 10


print '---第二种单例模式加了线程锁，变成适合多线程---'
#第二种单例模式在第一种单例模式基础上加了线程锁，变成适合多线程
import time
import threading
class Singleton(object):
    # 线程锁
    _instance_lock = threading.Lock()
    def __init__(self):
        time.sleep(1)
    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(Singleton, "_instance"):
            with Singleton._instance_lock:
                if not hasattr(Singleton, "_instance"):
                    Singleton._instance = Singleton()
        return Singleton._instance

def task(arg):
    obj = Singleton.instance()
    print(obj)
for i in range(10):
    t = threading.Thread(target=task,args=[i,])
    t.start()

obj = Singleton.instance()
print obj
#
time.sleep(2)
print '3#' * 10

print '---第三种使用__new__方法 + 线程锁---'
#第三种使用__new__方法
#import time
import threading
class Singleton(object):

    _instance_lock = threading.Lock()
    def __init__(self):
        time.sleep(1)

    def __new__(cls, *args, **kwargs):
        with Singleton._instance_lock:
            if not hasattr(Singleton, "_instance"):
                Singleton._instance = object.__new__(cls, *args, **kwargs)
        return Singleton._instance
#
def task(arg):
    obj = Singleton()
    print obj
for i in range(10):
    t = threading.Thread(target=task,args=[i,])
    t.start()


print '---第四种方法使用元类__metaclass_ + 线程锁---'
#第四种方法使用元类__metaclass__
import threading
#元类是创建【类实例】的类
#自定义元类需要继承 type
class SingletonType(type):
    _instance_lock = threading.Lock()
    def __call__(self, *args, **kwargs):

        with SingletonType._instance_lock:
            if not hasattr(self, "_instance"):
                print '__call__'
                self._instance = super(SingletonType,self).__call__(*args, **kwargs)
        return self._instance

class Singleton(object):
    # 当创建Singleton时，看看当前类里有没有 __metaclass__ 属性，如果有就用 __metaclass__ 来创建对象
    # 否则用 type 来创建对象
    # 当用__metaclass__创建对象时，会调用 类的 __call__ 方法
    __metaclass__ = SingletonType

    def __new__(cls, *args, **kwargs):
        print "__new__"
        return object.__new__(cls)

    def __init__(self,name):
        time.sleep(1)
        print "__init__"
        self.name = name

#
def task(arg):
    # 类Singleton 是元类SingletonType的对象实例，所以在执行 Singleton(arg) 时，
    # 会调用SingletonType 的 __call__() 来创建Singleton类实例
    obj = Singleton(arg)
    print obj
for i in range(10):
    t = threading.Thread(target=task,args=[i,])
    t.start()



class PP (object):
    def __init__(self):
        print '__init__'

    def __new__(cls, *args, **kwargs):
        print '__new__'
        return super(PP, cls).__new__(cls,*args, **kwargs)

    def __call__(self, *args, **kwargs):
        print '__call__'

p = PP()
print '----------'
p()

