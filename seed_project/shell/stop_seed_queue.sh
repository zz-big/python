#!/bin/sh
echo "stop news find action"
user=`/usr/bin/whoami`
PID="`ps -ef|grep python|grep ${user}|grep seed_queue|grep -v grep|awk '{print $2}'`"
kill ${PID}
echo "stop finish..."
