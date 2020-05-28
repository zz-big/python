#-*- encoding: utf-8 -*-
'''
redisxPath.py
Created on 2019/12/27 15:35
Copyright (c) 2019/12/27,ZZ 版权所有.
@author: ZZ
'''
import traceback,time,sys,redis

from commons.util.file_util import FileUtil
from commons.util.time_util import TimeUtil
from configs.config import _LOCAL_DATA_DIR_REDIS,_ZZ_DB
from commons.util.log_util import LogUtil
from commons.util.db_util import DBUtil


def redis2Hdfs():

    select_xpath_rule_sql = """select host,xpath,type from stream_extract_xpath_rule where host='%s' and status=0"""
    rl = LogUtil().get_base_logger()
    try:
        d = DBUtil(_ZZ_DB)

        start = 0
        is_finish = True
        host_set = set()

        f = FileUtil()
        t = TimeUtil()
        time_str = t.now_time(format='%Y%m%d%H%M%S')
        #local_xpath_file_path = '/user/zengqingyong17/spark/xpath_cache_file' + time_str
        local_xpath_file_path = 'E:/python_workspaces/data/xpath/xpath_file' + time_str

        starttime = time.clock()
        r = redis.Redis('nn1.hadoop', '6379', db=6)
        while is_finish:
            values = set()
            rs = r.scan(start, "total_z:*", 10)
            # 新游标
            start = rs[0]
            if start ==0:
                is_finish = False
            # print rs
            for i in rs[1]:
                host = i.split(":")[1]
                total_key = i
                txpath_key = 'txpath_z:%s' % host
                fxpath_key = 'fxpath_z:%s' % host
                total = r.get(total_key)

                # 降序排序获得次数(0,1)
                txpath = r.zrevrange(txpath_key, 0, 1)
                row_format = "%s\t%s\t%s\t%s"

                if txpath:
                    txpath_num = int(r.zscore(txpath_key, txpath[0]))
                    if txpath.__len__() == 2:
                        # 返回txpath_key 中txpath[1]的数值
                        txpath_num_1 = int(r.zscore(txpath_key, txpath[1]))
                        txpath_num_1 = txpath_num_1 if txpath_num_1 is not None else 0
                    if txpath_num / float(total) >= 0.8:
                        values.add(row_format % (host, txpath[0], 'true', '0'))
                        host_set.add(host)
                    else:
                        if txpath_num >= 100:
                            values.add(row_format % (host, txpath[0], 'true', '0'))
                            host_set.add(host)
                        if txpath_num_1 is not None and txpath_num_1 >= 100:
                            values.add(row_format % (host, txpath[1], 'true', '0'))
                            host_set.add(host)

                # 获得fxpath_key的全部值
                fxpath = r.smembers(fxpath_key)
                if fxpath:
                    # print 'fxpath:%s' % fxpath
                    for fx in fxpath:
                        values.add(row_format % (host, fx, 'false', '1'))
                    host_set.add(host)

                sql = select_xpath_rule_sql % host
                list_rule = d.read_tuple(sql)
                for rule in list_rule:
                    type = rule[2]
                    if type == 0:
                        values.add(row_format % (rule[0], rule[1], 'true', '2'))
                        host_set.add(host)
                    elif type == 1:
                        values.add(row_format % (rule[0], rule[1], 'false', '3'))
                        host_set.add(host)

            f.write_file_line_pattern(local_xpath_file_path, values, "a")

        #上传到HDFS的XPATH配置文件目录
        # c.upload("/user/qingniu/xpath_cache_file/", local_xpath_file_path)
        endtime = time.clock()
        worksec = int(round((endtime - starttime)))
        rl.info('total host %s,action time %s\'s' % (host_set.__len__(), worksec))
    except:
        rl.exception()
        d.rollback()
    finally:
        d.close()


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")
    redis2Hdfs()





