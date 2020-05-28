#-*- encoding: utf-8 -*-
'''
page_queue.py
Created on 2019/11/26 22:51
Copyright (c) 2019/11/26,ZZ 版权所有.
@author: ZZ
'''

import traceback, sys, Queue, os, shutil
sys.path.append('E:\python_workspaces\data')

from commons.action.base_producer_action import ProducerAction
from commons.action.base_consumer_action import ConsumerAction
from commons.action.producer import Producer
from commons.util.html_util import HtmlUtil
from commons.util.db_util import DBUtil
from commons.util.request_util import RequestUtil
from commons.util.util import Util
from commons.util.time_util import TimeUtil
from commons.util.content import _SEQ1,_SEQ2,_SEQ3,_SEQ4
from bs4 import BeautifulSoup
from commons.util.kafka_util import KafkaUtil
from configs.config import _ZZ_DB, _QUEUE_ZZ, _LOCAL_DATA_DIR, _KAFKA_CONFIG


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
            sql_params = [2, 0, ip, _QUEUE_ZZ["MAX_FAIL_TIMES"], _QUEUE_ZZ["LIMIT_NUM"]]

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

        # 插入page表sql语句
        insert_page='''
        insert into web_page
        (url,md5,param,domain,host,title,create_time,create_day,create_hour,update_time,status)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE update_time=VALUES(update_time);
        '''

        # 写入失败查询internally的title
        select_sql = '''
        select a_title from web_seed_internally where a_md5=%s;
        '''
        # 获取时间
        a_time = TimeUtil()
        total_count = 0
        try:

            create_time=a_time.get_timestamp()
            create_day=int(a_time.now_day(format='%Y%m%d'))
            file_day = a_time.now_day()
            create_hour=int(a_time.now_hour())

            # 每五分钟一个时间段
            minute =int(a_time.now_min())
            for i in range(60,-5,-5):
                if minute < i:
                    continue
                minute = i
                break

            minute = '0%s' % minute if minute < 10 else minute

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
            db_util = DBUtil(_ZZ_DB)

            a_title = soup.find("title").get_text().strip()

            # for a in a_docs:
            # # 获取a标签的href

            # 时间戳
            timestamp1 = '%s %s:%s:00' % (file_day,create_hour,minute)
            time1 = (a_time.str2timestamp(timestamp1)).__str__()[:-2]
            # 按时间段定文件名
            file_name = '%s_%s%s%s_%s.txt' % (values[0],create_day,create_hour,minute,time1)

            # 拼接写入的数据
            md5_url_html = u.get_md5(self.act+"\001"+str(html).replace("\r","").replace("\n","\002"))
            write_result = md5_url_html+"\001"+self.act+"\001"+str(html).replace("\r","").replace("\n","\002")+"\n"

            k = KafkaUtil(_KAFKA_CONFIG)
            html = html.replace(_SEQ1,'').replace(_SEQ2,_SEQ4)
            push_str = _SEQ3.join(('%s','%s')) % (self.act,html)
            push_str = _SEQ3.join(('%s','%s')) % (u.get_md5(push_str),push_str)
            push_str = bytes(push_str)
            is_success = k.push_message(push_str)

            if is_success:
                # 写入文件
                with open(_LOCAL_DATA_DIR % ('%s/%s' % ('tmp', file_name)), "a+") as f1:
                    f1.write(write_result)
                # with open(_LOCAL_DATA_DIR % ('%s/%s' % ('done', file_name)), "a+") as f2:
                #     f2.write(write_result)

                params_sql = [self.act,md5,self.params,domain,host,a_title,create_time,create_day,create_hour,create_time,1]
                db_util.execute(insert_page, params_sql)

                r.close_phandomjs()

                total_count=total_count+1

                # move 文件名
                time2 = int(time1) - 300
                minute_move = a_time.timestamp2str(time2,format='%Y%m%d%H%M')
                move_name = '%s_%s_%s.txt' % (values[0],minute_move,time2)

                tmp_path = _LOCAL_DATA_DIR % ('%s/%s' % ('tmp', move_name))
                done_path = _LOCAL_DATA_DIR % ('%s/%s' % ('done', move_name))
                if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                    shutil.move(tmp_path, done_path)

        except Exception, err:
            traceback.print_exc(err)
        finally:

            if total_count > 0:
                return self.result(True, self.id, md5, create_time)
            else:
                # select_param = [md5]
                # mid_title = db_util.read_dict(select_sql, select_param)
                # a_title = mid_title['a_title'][:200]
                a_title=''
                params_sql = [self.act,md5,self.params,domain,host,a_title,create_time,create_day,create_hour,create_time,2,a_title,create_time]
                db_util.execute(insert_page, params_sql)
                return self.result(False, self.id, md5)

            db_util.close()

    def success_action(self, values):
        # 删除列表对应的记录
        del_sql = '''
        delete from web_queue where id =%s;
        '''
        # 更新internally表状态
        update_sql = '''
        update web_seed_internally set update_time=%s where a_md5 =%s;
        '''
        db_util = DBUtil(_ZZ_DB)

        try:
            # 删除队列表
            id = values[0]
            sql_param = [id]
            db_util.execute(del_sql, sql_param)
            # 更新internally表
            sql_param =[values[2], values[1]]
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
        # 更新internally表状态
        update_page_sql = '''
        update web_seed_internally set fail_times=fail_times + 1,fail_ip=%s where a_md5 =%s;
        '''
        # 更新web_page表状态
        update_download_sql = '''
        update web_page set fail_times=fail_times + 1,fail_ip=%s where md5 =%s;
        '''

        db_util = DBUtil(_ZZ_DB)

        try:
            id = values[0]
            ip = Util().get_local_ip()
            # 每次更新失败ip 和失败次数
            # queue表
            sql_params = [ip, id]
            db_util.execute_no_commit(update_sql1, sql_params)
            # internally 表
            sql_params = [ip, values[1]]
            db_util.execute(update_page_sql, sql_params)
            # page 表
            sql_params = [ip, values[1]]
            db_util.execute(update_download_sql, sql_params)

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
