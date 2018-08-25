# Author: harry.cai
# DATE: 2018/3/18


class users:
    '''
    用户对象，完成认证后实例化对象并返回
    '''
    def __init__(self,username,home):
        '''

        :param username: 用户名
        :param home: 用户家目录
        '''
        self.username = username
        self.home = home
        # 认证状态
        self.is_login = False
        # 用户当前目录
        self.current_dir = self.home
