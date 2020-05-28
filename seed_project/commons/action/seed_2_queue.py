#-*- encoding: utf-8 -*-
'''
put_query.py
Created on 2019/11/21 23:48
Copyright (c) 2019/11/21,ZZ 版权所有.
@author: ZZ
'''
import sys, traceback, time
# sys.path.append('/home/hadoop/seed')

from commons.util.db_util import DBUtil
from configs.config import _ZZ_DB, _QUEUE_ZZ


def put_queue(page_show_num):

    db_util = DBUtil(_ZZ_DB)
    # 统计queue符合条件的记录数
    count_queue_sql='''
    select count(*) from web_queue where is_work=%s and fail_times < %s;
    '''

    # 统计web_seed表的符合条件的总记录数
    count_seed_sql='''
    select count(*) from web_seed where status=0;
    '''

    # 分页查询web_seed 表的记录
    select_seed_limit_sql='''
    select id,url,category from web_seed where status=0 limit %s,%s;
    '''

    # 插入queue表记录
    insert_queue_sql='''
    insert into web_queue (type,action,params) values(%s,%s,%s);
    '''

    # 更新web_seed表中的 status
    update_sql='''
    update web_seed set status=1 where id in(%s);
    '''

    try:
        sql_params = [0, _QUEUE_ZZ["MAX_FAIL_TIMES"]]
        res1 = db_util.read_one(count_queue_sql, sql_params)
        total_num1 = res1[0]
        if total_num1 != 0:
            print "queue has %d records,not insert!" % total_num1
            return None

        start_time =time.time()

        # 统计web_seed 表符合条件的总记录数
        res2 = db_util.read_one(count_seed_sql)
        total_num2 = res2[0]

        # 计算分多少页查询
        page_num = total_num2 / page_show_num if total_num2 % page_show_num == 0 else total_num2 /page_show_num + 1

        # 分页查询
        ids = []

        for i in range(0, page_num):
            sql_params =[i*page_show_num, page_show_num]
            print sql_params
            res3 = db_util.read_dict(select_seed_limit_sql, sql_params)

            list1 = []

            for row in res3:
                id = row["id"]
                ids.append(str(id))
                action = row["url"]
                params = row["category"]
                type = 1
                list1.append((type, action, params))

            # 批量插入queue
            db_util.executemany(insert_queue_sql, list1)

        # 更新 status=1
        db_util.execute_no_commit(update_sql % ",".join(ids))

        db_util.commit()

        end_time=time.time()
        run_time = end_time - start_time
        print "total_num:%d, run_time:%.2f" % (total_num2, run_time)

    except Exception, err:
        db_util.rollback()
        traceback.print_exc(err)
    finally:
        db_util.close()


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    page_show_num = 5
    put_queue(page_show_num)