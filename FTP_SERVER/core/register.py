# Author: harry.cai
# DATE: 2018/3/18

import configparser
import os
from config import settings
from core.md5 import Md5Action
conf = configparser.ConfigParser()


def register():
    '''
    账号注册，写入用户配置文件
    :return:
    '''
    username = input('请输入用户名：')
    password = input('请输入密码：')
    password_md5 = Md5Action.md5_passwd(password)
    home = os.path.join(settings.HomeDir,username)
    try:
        os.makedirs(home)
    except Exception as e:
        print(e)
    quota = '500m'
    conf.add_section(username)
    conf[username]['password'] = password_md5
    conf[username]['home'] = home
    conf[username]['quota'] = quota
    conf.write(open(settings.AccountPath, 'a'))