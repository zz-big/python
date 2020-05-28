#-*- encoding: utf-8 -*-
'''
sql_queue.py
Created on 2019/11/21 20:56
Copyright (c) 2019/11/21,ZZ 版权所有.
@author: ZZ
'''
import traceback, sys, Queue, re,json
# sys.path.append('/home/hadoop/seed')

from commons.action.base_producer_action import ProducerAction
from commons.action.base_consumer_action import ConsumerAction
from commons.action.producer import Producer
from commons.util.html_util import HtmlUtil
from commons.util.db_util import DBUtil
from commons.util.redis_util import RedisUtill
from commons.util.request_util import RequestUtil
from commons.util.util import Util
from commons.util.time_util import TimeUtil
from bs4 import BeautifulSoup
from configs.config import _ZZ_DB, _QUEUE_ZZ


class WebProducerAction(ProducerAction):

    def queue_items(self):

        # 屏蔽ip的查询方式
        select_sql='''
        select id, action, params from web_queue where type=%s
        and is_work=%s and fail_ip != %s and fail_times < %s limit 0, %s for update;
        '''

        update_sql='''
        update web_queue set is_work=1 where id in(%s);
        '''
        db_util = DBUtil(_ZZ_DB)

        try:
            ip = Util().get_local_ip()
            sql_params = [1, 0, ip, _QUEUE_ZZ["MAX_FAIL_TIMES"], _QUEUE_ZZ["LIMIT_NUM"]]

            res = db_util.read_dict(select_sql, sql_params)
            actions = []

            ids = []
            for row in res:
                id = row["id"]
                ids.append(str(id))
                action = row["action"]
                params = row["params"]

                # 封装对象
                c_action = WebConsumerAction(id, action, params)
                actions.append(c_action)

            if len(actions) != 0:
                # 更新 is_work=1
                db_util.execute_no_commit(update_sql % ",".join(ids))

            db_util.commit()

        except Exception, err:
            actions = []
            db_util.rollback()
            traceback.print_exc(err)

        finally:
            db_util.close()

        return actions


class WebConsumerAction(ConsumerAction):
    def __init__(self, id, act, params):
        super(self.__class__, self).__init__()

        self.id = id
        self.act = act
        self.params = params

    def action(self, *values):

        # 插入内链表sql语句
        insert_seed_internally='''
        insert into web_seed_internally
        (url,md5,param,domain,host,a_url,a_md5,a_host,a_xpath,a_title,create_time,create_day,create_hour,update_time,status)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE update_time=VALUES(update_time);
        '''
        # 插入外链表sql语句
        insert_seed_externally='''
        insert into web_seed_externally
        (url,md5,param,domain,host,a_url,a_md5,a_host,a_xpath,a_title,create_time,create_day,create_hour,update_time,status)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE update_time=VALUES(update_time);
        '''

        # 获取时间
        a_time = TimeUtil()
        db_util = DBUtil(_ZZ_DB)
        # redis_d = RedisUtill()
        total_count = 0
        in_count = 0
        ex_count = 0
        try:
            # 解析主网页信息
            hu = HtmlUtil()

            domain = hu.get_url_domain(self.act)
            host = hu.get_url_host(self.act)
            u = Util()
            md5 = u.get_md5(self.act)

            # 解析a标签信息
            r = RequestUtil()
            # 通过phandomjs 请求url，返回网页，包括网页的ajax请求
            html = r.http_get_phandomjs(self.act)
            # 可以从HTML或XML文件中提取数据的Python第三方库
            soup = BeautifulSoup(html, 'lxml')
            # a链接dom对象列表
            aset = set()
            # 获取host
            a_host = hu.get_url_host(self.act)

            # a_docs = soup.find_all("a",href=re.compile("^(/|.*"+domain+")"))
            a_docs = soup.find_all("a")

            for a in a_docs:

                total_count += 1
                # 获取a标签的href
                a_url = hu.get_format_url(self.act,a,a_host)
                # 获取a标签的内容
                a_title = a.get_text().strip()
                if a_url == '' or a_title == '':
                    continue

                if aset.__contains__(a_url):
                    continue
                aset.add(a_url)

                # 获取a标签的host
                a_host = hu.get_url_host(a_url)

                # 获取a标签href链接url的md5
                a_md5 = u.get_md5(a_url)

                # 获取a标签所对应的xpath
                a_xpath = hu.get_dom_parent_xpath_js_new(a)

                create_time = a_time.get_timestamp()
                create_day = int(a_time.now_day(format='%Y%m%d'))
                create_hour = int(a_time.now_hour())

                params_sql = [self.act,md5,self.params,domain,host,a_url,a_md5,a_host,a_xpath,a_title,create_time,create_day,create_hour,create_time,0]
                if re.compile("^(/|.*"+domain+")").match(a_url) is not None:
                    db_util.execute(insert_seed_internally, params_sql)
                #
                #     # redis
                #     redis_md5 = u.get_md5(md5+"\001"+a_md5)
                #     find_key = redis_d.get_value_for_key('seed:%s:a_url' % redis_md5)
                #     if find_key == None:
                #         # url,md5,param,domain,host,a_url,a_md5,a_host,a_xpath,a_title,create_time,create_day,create_hour,update_time,status
                #         dicts = {'seed:%s:param' % redis_md5 :self.params, 'seed:%s:a_url' % redis_md5 : a_url,
                #                 'seed:%s:md5' % redis_md5 : md5, 'seed:%s:a_md5' % redis_md5 :a_md5}
                #
                #         dicts_temp = {'seed_temp:%s:param' % redis_md5 :self.params,'seed_temp:%s:a_url' % redis_md5 : a_url,
                #                     'seed_temp:%s:md5' % redis_md5 : md5, 'seed_temp:%s:a_md5' % redis_md5 : a_md5}
                #         redis_d.set_batch_datas(dicts)
                #         redis_d.set_batch_datas(dicts_temp)

                    in_count += 1
                else:
                    db_util.execute(insert_seed_externally, params_sql)
                    ex_count += 1

            r.close_phandomjs()
        except Exception, err:
            db_util.rollback()
            traceback.print_exc(err)
        finally:
            db_util.close()

            if (in_count + ex_count) > 0:

                return self.result(True, self.id, md5, create_time,  in_count, ex_count)
            else:
                return self.result(False, self.id, md5)

    def success_action(self, values):
        # 删除列表对应的记录
        del_sql = '''
        delete from web_queue where id =%s;
        '''
        # 更新seed表状态
        update_sql = '''
        update web_seed set last_crawl_time=%s,last_crawl_internally=%s,last_crawl_externally=%s where md5 =%s;
        '''
        db_util = DBUtil(_ZZ_DB)

        try:
            # 删除队列表
            id = values[0]
            sql_param = [id]
            db_util.execute(del_sql, sql_param)
            # 更新seed表
            # [(1574519076,), 95, 7, '824e29a21f2a02379f78b0675d1fc5eb']
            sql_param =[values[2], values[3],values[4],values[1]]
            db_util.execute(update_sql, sql_param)
        except Exception, err:
            db_util.rollback()
            traceback.print_exc(err)

        finally:
            db_util.close()

    def fail_action(self, values):
        # 每次失败都需要更新ip 和 失败次数
        update_sql1='''
        update web_queue set fail_ip = %s , fail_times = fail_times + 1 where id = %s;
        '''
        # 当失败次数到达每台机器的最大重试次数，就将该记录的is_work=0 ,让其重试
        update_sql2='''
        update web_queue set is_work = 0 where id = %s;
        '''
        # 更新seed表状态
        update_seed_sql = '''
        update web_seed set fail_times=fail_times + 1,fail_ip=%s where md5 =%s;
        '''
        # 更新externally表状态
        update_exter_sql = '''
        update web_seed_externally set fail_times=fail_times + 1,fail_ip=%s where a_md5 =%s;
        '''

        db_util = DBUtil(_ZZ_DB)

        try:
            id = values[0]
            ip = Util().get_local_ip()
            # 每次更新失败ip 和失败次数
            # queue表
            sql_params = [ip, id]
            db_util.execute_no_commit(update_sql1, sql_params)
            # seed 表
            sql_params = [ip, values[1]]
            db_util.execute(update_seed_sql, sql_params)
            # externally表
            db_util.execute(update_exter_sql, sql_params)

            if self.current_retry_num == _QUEUE_ZZ["C_RETRY_TIMES"] - 1:
                db_util.execute_no_commit(update_sql2 % id)

            db_util.commit()

        except Exception,err:
            db_util.rollback()
            traceback.print_exc(err)

        finally:
            db_util.close()


if __name__ == "__main__":

    reload(sys)
    sys.setdefaultencoding('utf-8')
    q = Queue.Queue()

    p_action = WebProducerAction()

    p = Producer(q, _QUEUE_ZZ['NAME'], p_action, _QUEUE_ZZ['P_SLEEP_TIME'], _QUEUE_ZZ['C_MAX_NUM'],
                 _QUEUE_ZZ['C_MAX_SLEEP_TIME'], _QUEUE_ZZ['C_RETRY_TIMES'])

    p.start_work()

    # p_action = SqlProducerAction()
    #
    # actions = p_action.queue_items()
    # for c_action in actions:
    #    print c_action.action()
