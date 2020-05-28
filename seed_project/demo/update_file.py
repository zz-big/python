#-*- encoding: utf-8 -*-
'''
update_file.py
Created on 2019/11/22 15:59
Copyright (c) 2019/11/22
'''
day = '20190620'
hour = '12'
minute = 6

for i in range(60,-5,-5):
    if minute < i:
        continue
    minute = i
    break

minute = '0%s' % minute if minute < 10 else minute
print '%s%s%s' % (day,hour,minute)