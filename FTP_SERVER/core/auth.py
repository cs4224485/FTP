# Author: harry.cai
# DATE: 2018/3/18
import configparser
from config import settings
from core import md5
from core import userinfo


def login(username, password, conn):
    '''
    用户登录认证模块
    :param username: 用户登录用户名
    :param password: 用户登录密码
    :param conn: 与客户端建立的连接
    :return: 返回用户对象
    '''
    conf = configparser.ConfigParser()
    conf.read(settings.AccountPath)
    try:
        # 加载配置文件中的用户名密码
        load_username = conf.options(username)
        load_password = conf[username]['password']
        # 将用户传过来的密码做一个md5计算
        password_md5 = md5.Md5Action.md5_passwd(password)
        # 如果匹配则验证成功，返回用户对象
        if load_username and password_md5 == load_password:
            load_home = conf[username]['home']
            user_ogj = userinfo.users(username,load_home)
            conn.send('102'.encode(settings.code))
            user_ogj.is_login = True
            return user_ogj
        else:
            conn.send('103'.encode(settings.code))

    except:
         conn.send('103'.encode(settings.code))