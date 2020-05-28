#-*- encoding: utf-8 -*-
'''
inner_web_queue.py
Created on 2019/11/23 19:14
Copyright (c) 2019/11/23,ZZ 版权所有.
@author: ZZ
'''
import traceback,time,sys
sys.path.append('/home/hadoop/seed')

from commons.util.db_util import DBUtil
from configs.config import _ZZ_DB, _QUEUE_ZZ


def put_queue_inner():

    # 统计queue符合条件的记录数
    count_queue_sql='''
    select count(*) from web_queue where is_work=%s and fail_times < %s;
    '''

    # 统计internally表的符合条件的总记录数
    count_inner_sql='''
    select count(*) from web_seed_internally where status=0;
    '''

    # web_seed_internally 表的记录
    select_inner_limit_sql='''
    select id,a_url,param from web_seed_internally where status=0 limit %s,%s;
    '''

    # 插入queue表记录
    insert_queue_sql='''
    insert into web_queue (type,action,params) values(%s,%s,%s);
    '''

    # web_seed_internally status
    update_sql='''
    update web_seed_internally set status=1 where id in(%s);
        '''
    db_uitl = DBUtil(_ZZ_DB)
    try:
        sql_params = [0, _QUEUE_ZZ['MAX_FAIL_TIMES']]
        res1 = db_uitl.read_one(count_queue_sql, sql_params)
        total_num1 = res1[0]
        if total_num1 != 0:
            print "queue has %d records,not insert!" % total_num1
            return None

        start_time = time.time()

        res2 = db_uitl.read_one(count_inner_sql)
        total_num2 = res2[0]

        # 计算分多少页查询
        page_num = total_num2 / _QUEUE_ZZ["LIMIT_NUM"] if total_num2 % _QUEUE_ZZ["LIMIT_NUM"] == 0 else total_num2 / _QUEUE_ZZ["LIMIT_NUM"] + 1

        # 分页插入queue表
        ids = []
        for i in range(0, page_num):
            sql_params = [i*_QUEUE_ZZ["LIMIT_NUM"], _QUEUE_ZZ["LIMIT_NUM"]]
            res3 = db_uitl.read_dict(select_inner_limit_sql, sql_params)

            list1 = []

            for row in res3:
                id = row["id"]
                ids.append(str(id))
                action = row["a_url"]
                params1 = row["param"]
                type = 2
                list1.append((type, action, params1))
            # 批量插入queue
            db_uitl.executemany(insert_queue_sql, list1)

        # 更新status = 1
        db_uitl.execute(update_sql % ",".join(ids))
        db_uitl.commit()

        end_time=time.time()
        run_time = end_time - start_time
        print "total_num:%d, run_time:%.2f" % (total_num2, run_time)

    except Exception, err:
        db_uitl.rollback()
        traceback.print_exc(err)
    finally:
        db_uitl.close()


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    put_queue_inner()