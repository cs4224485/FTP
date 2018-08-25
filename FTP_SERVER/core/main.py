# Author: harry.cai
# DATE: 2018/3/18

import socket
import os
import struct
import json
import subprocess
import queue
from concurrent.futures import ThreadPoolExecutor
from config import settings
from core import auth
from core import header
from core import md5



class MultiUserFtp:
    '''
    主要负责FTP各个功能,实现并发FTP
    '''

    def __init__(self):
        '''

        :param conn: 与客户端的连接
        :param cmds: 客户端输入的命令
        :param user_obj: 用户对象
        '''
        self.ip = settings.address
        self.port = settings.port
        self.conn = None
        self.cmds = None
        self.user_obj = None
        self.thread_queue = queue.Queue()

    def create_socket(self):
        '''
        创建socket对象
        :return:
        '''
        server_socket = socket.socket()
        server_socket.bind((self.ip,self.port))
        server_socket.listen(10)
        return server_socket

    def run(self):
        '''
        用于启动程序
        :return:
        '''
        socket = self.create_socket()
        pool = self.create_threading_pool()

        while True:
            print('server start....')
            conn,addr = socket.accept()
            self.create_queen(conn)
            # 获取线程队列中与客户端的连接，然后再交给线程池去执行
            pool.submit(self.Multi_thread)

    def Multi_thread(self,):
        while True:
            try:
                con_res = self.thread_queue.get(block=False)
                print(con_res)
                self.handler(con_res)
            except  Exception:
                break

    def handler(self, conn):

        auth_info = conn.recv(1024).decode(settings.code)
        username = auth_info.split('_')[0]
        password = auth_info.split('_')[1]
        # 调用认证模块，如果认证成功返回用户对象
        user_obj = auth.login(username,password, conn)
        if user_obj:
            while True:
                try:
                    # 接收客户端传来的命令
                    cmds = conn.recv(1024).decode(settings.code)
                    if not cmds:break
                    action = cmds.split(' ')[0]

                    # 对客户端命令进行反射解析
                    if hasattr(self, action):
                        func = getattr(self,action)
                        self.conn = conn
                        self.cmds = cmds
                        self.user_obj = user_obj
                        func()
                    else:
                        conn.send('301'.encode(settings.code))
                except Exception as e:
                    break
            conn.close()

    def create_threading_pool(self):
        '''
        创建线程池
        :return:
        '''
        pool = ThreadPoolExecutor(settings.MaxThreads)
        return pool

    def create_queen(self,conn):
        '''
        将与客户端的连接放入线程队列
        :param conn:
        :return:
        '''

        self.thread_queue.put(conn)

    def param_check(self, params, min_param=None, max_param=None, exact=None):
        '''
        对参数合法性进行检查
        :param params: 用户输入的参数
        :param min_param: 最小参数限制
        :param max_param: 最大参数限制
        :param exact: 精确参数
        :return:
        '''
        params = params.split(' ')
        print(len(params))
        if min_param:
            if len(params) < min_param:
                return False
        if max_param:
            if len(params) > max_param:
                return False
        if exact:
            if len(params) != exact:
                return False

        return True

    def send_msg(self,code,**kwargs):
        '''
        负责向客户端发送信息
        :param code: 状态代码
        :param kwargs:
        :return:
        '''
        state_code = code

        msg = {
            'code':state_code,
        }
        if kwargs:
            msg.update(kwargs)
        # 将信息转为bytes发送
        msg_json = json.dumps(msg)
        msg_bytes = msg_json.encode(settings.code)
        msg_size = struct.pack('i',len(msg_bytes))

        self.conn.send(msg_size)
        self.conn.send(msg_bytes)

    def get_respond(self):
        '''

        拿到客户端响应，解析后返回
        :return: 解析后的数据
        '''

        msg_size_obj = self.conn.recv(4)
        msg_size = struct.unpack('i', msg_size_obj)[0]
        msg_data = self.conn.recv(msg_size)
        msg = json.loads(msg_data.decode(settings.code))
        return msg

    def get(self, *args, **kwargs):
        '''
        实现对文件的下载功能
        :param args:
        :param kwargs:
        :return:
        '''
        param_check_state = self.param_check(self.cmds, min_param=2)

        if param_check_state:
            # print(self.cmds)
            # 拼接下载文件的路径
            filename = self.cmds.split(' ')[1]
            current_path = self.user_obj.current_dir
            file_path = os.path.join(current_path,filename)
            # 如果不在则返回相应的状态码
            if not os.path.exists(file_path):
                self.send_msg('201')
                return
            # 制作并发送报头
            head_dic = header.make_header(file_path)
            self.send_msg('202', head_dic=head_dic)

            has_send = 0
            f = open(file_path, 'rb')
            message = self.get_respond()
            # 如果需要续传则将已发送的位置seek到'recv_size'实现断点续传
            is_continue = message['code']
            if is_continue == '301':
                has_send = message['recv_size']
                ack = self.get_respond()
            f.seek(has_send)
            for line in f:
                self.conn.send(line)
        else:
            self.send_msg('104')

    def put(self, *args, **kwargs):
        '''
        文件上传功能
        :param args:
        :param kwargs:
        :return:
        '''
        param_check = self.param_check(self.cmds,exact=3)
        if param_check:
            self.send_msg('204')  # 发送状态码告知客户端准备接收报头

            # 接收客户端响应
            message = self.get_respond()
            if message['code'] == '202':
                head_dic = message['head_dic']
                des_path = os.path.join(self.user_obj.home,head_dic['des_path'])
                # 判断目标的目录是否存在
                if os.path.isdir(os.path.dirname(des_path)):
                    recv_size = 0
                    # 判断文件是否存在，如果存在则询问客户端是否要续传，如果不存在则直接开始上传
                    if os.path.exists(des_path):
                        self.send_msg('302')
                        is_continue = self.get_respond()['code']
                        if is_continue == '302':
                            recv_size = os.path.getsize(des_path)
                            self.send_msg('303',recv_size=recv_size)
                            f = open(des_path, 'ab')
                        else:
                            f = open(des_path, 'wb')
                    else:
                        self.send_msg('304')
                        f = open(des_path, 'wb')
                    f.seek(recv_size)
                    while recv_size != head_dic['file_size']:
                        data = self.conn.recv(1024)
                        f.write(data)
                        recv_size += len(data)
                    f.close()

                    # 上传完成后对文件进行MD5校验如果匹配则代表上传成功
                    file_md5_check = md5.Md5Action.md5_check(des_path)
                    if file_md5_check == head_dic['md5']:
                        self.send_msg('207')
                    else:
                        self.send_msg('208')
        else:
            self.send_msg('104')

    def ls(self, *args, **kwargs):
        '''
        列出指定路径下的文件和目录
        :param args:
        :param kwargs:
        :return:
        '''
        if  len(self.cmds.split(' ')) == 2:
            dir_name = self.cmds.split(' ')[1]
            dir_path = os.path.join(self.user_obj.current_dir, dir_name)
        else:
            self.send_msg('401')
            dir_path = self.user_obj.current_dir
            return

        # 判断目录是否是已存在目录, 如果是则执行系统的dir命令并返回给客户端
        if os.path.isdir(dir_path):
            self.send_msg('402')
            cmd = 'dir %s' %dir_path
            cmd_obj = subprocess.Popen(cmd,shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            stderr_out = cmd_obj.stderr.read()
            stdout = cmd_obj.stdout.read()
            result_size = len(stderr_out+stdout)
            head = struct.pack('i',result_size)
            ack = self.conn.recv(1024)
            self.conn.send(head)
            self.conn.send(stderr_out)
            self.conn.send(stdout)
        else:
            self.send_msg('401')
            return

    def cd(self,*args,**kwargs):
        '''
        将用户当前路径切换至指定路径下
        :param args:
        :param kwargs:
        :return:
        '''
        param_check = self.param_check(self.cmds, exact=2)
        if param_check:
            # 对当前路径和要切换到的目标路径进行拼接
            target_path = self.cmds.split(' ')[1]
            change_dir = os.path.abspath(os.path.join(self.user_obj.current_dir,target_path))
            if os.path.isdir(change_dir):

                # 如果切换后的路径是以用户自己的目录开头则进行顺利切换，否则代表已经在用户的根目录无法再往上一级切换
                if change_dir.startswith(self.user_obj.home):
                    self.user_obj.current_dir = change_dir

                    # 以用户名为分割符进行切换，后面的代表用户的目录，如果无法切割代表当前所在目录就是根目录
                    if self.user_obj.current_dir.split(self.user_obj.username)[1]:
                        replace_dir = self.user_obj.current_dir.replace(self.user_obj.home, '')
                        self.send_msg('502',replace_dir=replace_dir)
                    else:
                        self.send_msg('502', replace_dir='\\')
                else:
                    self.send_msg('503')
            else:
                self.send_msg('401')
        else:
            self.send_msg('401')

    def mkdir(self,*args,**kwargs):
        '''
        创建目录
        :param args:
        :param kwargs:
        :return:
        '''
        param_check = self.param_check(self.cmds, exact=2)
        if param_check:
            dir_name = self.cmds.split(' ')[1]
            full_path = os.path.join(self.user_obj.current_dir, dir_name)
            # 如果目标目录存在则告知服务器目录已存在否则就创建目录
            if os.path.isfile(full_path):
                self.send_msg('506')
            else:
                os.makedirs(full_path)
                self.send_msg('505')