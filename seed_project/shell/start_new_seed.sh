#!/bin/sh
echo "start news find action"
nohup /usr/local/bin/python /home/hadoop/seed/commons/action/new_seed.py > /dev/null 2>&1 &
echo "start finish..."
