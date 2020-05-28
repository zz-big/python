#-*- encoding: utf-8 -*-
'''
new_seed.py
Created on 2019/11/22 19:55
Copyright (c) 2019/11/22,ZZ 版权所有.
@author: ZZ
'''
import sys
# sys.path.append('/home/hadoop/seed')

from commons.util.log_util import LogUtil
from commons.util.db_util import DBUtil
from commons.util.html_util import HtmlUtil
from configs import config
from tld import get_tld
from commons.util.util import Util


def create_seed():
    sql = """
    insert into web_seed (url,md5,domain,host,category,status) values
    ('%s','%s','%s','%s','%s',0);
    """
    url = "https://news.sina.com.cn/"
    catetory = "新闻"
    hu = HtmlUtil()
    domain = get_tld(url)
    host = hu.get_url_host(url)
    u = Util()
    md5 = u.get_md5(url)

    rl = LogUtil().get_base_logger()
    try:
        d = DBUtil(config._ZZ_DB)
        sql = sql % (url,md5,domain,host,catetory)
        d.execute(sql)
    except:
        rl.exception()
        d.rollback()
    finally:
        d.close()


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    create_seed()