#-*- encoding: utf-8 -*-
'''
inner_web_queue.py
Created on 2019/11/23 19:14
Copyright (c) 2019/11/23,ZZ 版权所有.
@author: ZZ
'''
import traceback,time,sys
sys.path.append('/home/hadoop/seed')

from tld import get_tld
from commons.util.db_util import DBUtil
from configs.config import _ZZ_DB, _QUEUE_ZZ


def put_seed():

    # 统计seed符合条件的记录数
    count_queue_sql='''
    select count(*) from web_seed where status=%s and fail_times < %s;
    '''

    # 统计web_seed表的符合条件的总记录数
    count_exter_sql='''
    select count(*) from web_seed_externally where status=0;
    '''

    # web_seed_externally 表的记录
    select_exter_limit_sql='''
    select id,a_url,a_md5,a_host,param from web_seed_externally where status=0 limit %s,%s;
    '''

    # 插入seed表记录
    insert_seed_sql = '''
    insert into web_seed (url,md5,domain,host,category) values (%s,%s,%s,%s,%s);
    '''

    # web_seed_internally status
    update_sql='''
    update web_seed_externally set status=1 where id in(%s);
     '''
    db_uitl = DBUtil(_ZZ_DB)

    sql_params = [0, _QUEUE_ZZ['MAX_FAIL_TIMES']]
    res1 = db_uitl.read_one(count_queue_sql, sql_params)
    total_num1 = res1[0]
    if total_num1 != 0:
        print "queue has %d records,not insert!" % total_num1
        return None

    start_time = time.time()

    res2 = db_uitl.read_one(count_exter_sql)
    total_num2 = res2[0]

    # 计算分多少页查询
    page_num = total_num2 / _QUEUE_ZZ["LIMIT_NUM"] if total_num2 % _QUEUE_ZZ["LIMIT_NUM"] == 0 else total_num2 / _QUEUE_ZZ["LIMIT_NUM"] + 1

    # hu = HtmlUtil()
    # u = Util()
    # 分页插入queue表
    try:
        ids = []
        for i in range(0, page_num):

            sql_params = [i*_QUEUE_ZZ["LIMIT_NUM"], _QUEUE_ZZ["LIMIT_NUM"]]
            res3 = db_uitl.read_dict(select_exter_limit_sql, sql_params)

            list1 = []

            for row in res3:
                id = row["id"]
                ids.append(str(id))

                url = row["a_url"]
                domain = get_tld(url)
                # host = hu.get_url_host(url)

                # md5 = u.get_md5(url)
                host = row["a_host"]
                md5 = row["a_md5"]
                category = row["param"]
                list1.append((url, md5, domain, host, category))
            # 批量插入queue
            db_uitl.executemany(insert_seed_sql, list1)

        # 更新status = 1
        db_uitl.execute(update_sql % ",".join(ids))

    except Exception, err:
        db_uitl.rollback()
        traceback.print_exc(err)
    finally:
        db_uitl.close()

    end_time=time.time()
    run_time = end_time - start_time
    print "total_num:%d, run_time:%.2f" % (total_num2, run_time)


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    put_seed()