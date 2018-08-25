# Author: harry.cai
# DATE: 2018/3/18
import sys
import re


class ArgvHandler:
    '''
    接收用户参数
    -s SERVER_IP -u USERNAME -p PASSWORD
    '''
    args = sys.argv
    try:
        server_addr = args[2]
        username = args[4]
        password = args[6]

    except:
        print('语法错误: USAGE Python FTP_CLIENT.PY -s SERVER_ADDR -u USERNAME -p PASSWORD')
        exit()

    @classmethod
    def check_user_info(cls):
        return cls.username, cls.password

    @classmethod
    def check_server(cls):
        '''
        检查IP地址输入的合法性
        :return:
        '''
        server_addr = re.search('(([0-9]{1,3})\.){3}[0-9]{1,3}', cls.server_addr)
        if server_addr:
            return server_addr.group()
        else:
            print('非法IP地址')
            exit()