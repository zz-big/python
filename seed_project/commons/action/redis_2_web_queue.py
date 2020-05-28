#-*- encoding: utf-8 -*-
'''
inner_web_queue.py
Created on 2019/11/23 19:14
Copyright (c) 2019/11/23,ZZ 版权所有.
@author: ZZ
'''
import traceback,time,sys,redis
sys.path.append('/home/hadoop/seed')

from commons.util.db_util import DBUtil
from commons.util.redis_util import RedisUtill
from commons.util.log_util import LogUtil
from configs.config import _ZZ_DB, _QUEUE_ZZ


def put_queue_inner():

    # 统计queue符合条件的记录数
    count_queue_sql='''
    select count(*) from web_queue where is_work=%s and fail_times < %s;
    '''

    # # 统计internally表的符合条件的总记录数
    # count_inner_sql='''
    # select count(*) from web_seed_internally where status=0;
    # '''
    #
    # # web_seed_internally 表的记录
    # select_inner_limit_sql='''
    # select id,a_url,param from web_seed_internally where status=0 limit %s,%s;
    # '''

    # 插入queue表记录
    insert_queue_sql='''
    insert into web_queue (type,action,params) values(%s,%s,%s);
    '''

    # web_seed_internally status
    update_sql='''
    update web_seed_internally set status=1 where md5=%s and a_md5=%s;
        '''
    try:
        # redis_tmp 数据
        redis_d = RedisUtill()
        db_uitl = DBUtil(_ZZ_DB)

        ips = ['192.168.235.136', '192.168.235.137', '192.168.235.138']
        port = '6379'
        list = []
        total_num = 0
        is_get_lock = redis_d.get_lock('seed_lock', 10)
        logger = LogUtil().get_base_logger()

        sql_params = [0, _QUEUE_ZZ['MAX_FAIL_TIMES']]
        res1 = db_uitl.read_one(count_queue_sql, sql_params)
        total_num1 = res1[0]
        if total_num1 != 0:
            logger.info("queue has %d records,not insert!" % total_num1)
            return None

        logger.info("正在获取锁...")
        if is_get_lock:
            logger.info("获取到锁")
            start_time = time.time()

            def scan_limit_to_queue_table(host, port, cursor, match, count):
                r = redis.Redis(host, port)
                rs = r.scan(cursor, match, count)
                # 新游标
                next_num = rs[0]
                # print rs
                li = rs[1]
                for i in li:
                    if i.__contains__('a_url'):
                        list.append(i)

                # 递归出口
                if next_num == 0:
                    return None
                scan_limit_to_queue_table(host, port, next_num, match, count)

            for ip in ips:
                scan_limit_to_queue_table(ip, port, 0,'seed_temp*', 100)

            # 分页插入queue表
            redis_result = []
            up_inner = []
            delete_list = []
            for k in list:
                if k.__contains__('a_url'):

                    # 确定同一MD5的其他参数的key
                    param = k.replace('a_url','param')
                    md5 = k.replace('a_url','md5')
                    a_md5 = k.replace('a_url','a_md5')

                    action = redis_d.get_value_for_key(k)
                    params = redis_d.get_value_for_key(param)
                    redis_result.append((2,action,params))

                    md5_val = redis_d.get_value_for_key(md5)
                    a_md5_val = redis_d.get_value_for_key(a_md5)
                    up_inner.append((md5_val,a_md5_val))
                    # 添加要删除的列表
                    delete_list.append(k)
                    delete_list.append(param)
                    delete_list.append(md5)
                    delete_list.append(a_md5)
                    total_num += 1

                # 批量插入queue
                if(len(redis_result) == 5):
                    db_uitl.executemany(insert_queue_sql,redis_result)
                    db_uitl.executemany(update_sql,up_inner)
                    redis_result = []
                    up_inner = []
            # 提交不满五个的最后一组
            db_uitl.executemany(insert_queue_sql,redis_result)
            db_uitl.executemany(update_sql,up_inner)
            # 删除redis_tmp
            redis_d.delete_batch(delete_list)

            redis_d.release('seed_lock')
            logger.info("释放锁")
        else:
            logger.info('其他线程正在处理，获取锁超过最大超时时间，退出处理逻辑 ')

        end_time=time.time()
        run_time = end_time - start_time
        logger.info("total_num:%d, run_time:%.2f" % (total_num, run_time))

    except Exception, err:
        db_uitl.rollback()
        redis_d.release('seed_lock')
        traceback.print_exc(err)
    finally:
        db_uitl.close()


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    put_queue_inner()