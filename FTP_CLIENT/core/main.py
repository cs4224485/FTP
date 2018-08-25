# Author: harry.cai
# DATE: 2018/3/18

import socket
import struct
import json
import os
from core import Argv
from config import settings
from core import messages
from core import MD5
from core import header


class MyClient:
    '''
    FTP客户端的主要逻辑和功能
    '''
    AddressFamily = socket.AF_INET
    Protocol = socket.SOCK_STREAM

    def __init__(self, server_address, server_port):
        '''

        :param server_address: 服务器地址
        :param server_port: 服务器端口
        '''

        self.server_address = server_address
        self.server_port = server_port
        # 当前所在路径
        self.current_path = '\\'
        self.client = None
        self.cmds = None

    def create_socket(self):
        '''
        创建socket
        :return: 返回socket对象
        '''
        return socket.socket(self.AddressFamily, self.Protocol)

    def connect_server(self):
        '''
        与服务器建立通信
        :return:
        '''
        socket_client = self.create_socket()
        socket_client.connect((self.server_address,self.server_port))
        return socket_client

    def run(self):
        '''
        服务器启动接口
        :return:
        '''
        # 先将传入用户名和密码发送给服务器认证
        username,password = Argv.ArgvHandler.check_user_info()
        auth_info = '_'.join([username, password])
        self.client = self.connect_server()
        self.client.send(auth_info.encode(settings.code) )
        code = self.client.recv(1024)
        # 对认证结果信息判断，认证成功后通过反射调用响应的功能
        if code.decode(settings.code) == '102':
            messages.message_handler(code.decode(settings.code))
            while True:
                self.cmds = input(r'[%s:%s]' % (username,self.current_path)) # 命令输入提示符
                cmd = self.cmds.split(' ')[0]
                if hasattr(self,cmd):
                    self.client.send(self.cmds.encode(settings.code))
                    func = getattr(self, cmd)
                    func()
        else:
            messages.message_handler(code.decode(settings.code))
            self.client.close()
            exit()

    def get_respond(self):
        '''
        获取并解析服务器响应
        :return:
        '''
        msg_size_obj = self.client.recv(4)
        # print(msg_size_obj)
        msg_size = struct.unpack('i',msg_size_obj)[0]
        msg_data = self.client.recv(msg_size)
        msg_json = msg_data.decode(settings.code)
        msg = json.loads(msg_json)
        return msg

    def send_msg(self, code, **kwargs):
        '''
        封装并向服务器发送信息
        :param code:
        :param kwargs:
        :return:
        '''

        state_code = code
        msg = {
            'code': state_code,
        }
        if kwargs:
            msg.update(kwargs)
        msg_json = json.dumps(msg)
        msg_bytes = msg_json.encode(settings.code)
        msg_size = struct.pack('i', len(msg_bytes))
        self.client.send(msg_size)
        self.client.send(msg_bytes)

    def get(self, *args, **kwargs):
        """
        文件下载功能
        :param args:
        :param kwargs:
        :return:
        """
        message = self.get_respond()
        result_code = message['code']

        # 判读接收码
        if result_code == '202':  # 接收文件报头

            head_dic = message['head_dic']

            file_path = os.path.join(settings.DownloadPath, head_dic['filename'])
            file_md5 = head_dic['md5']
            md5_file_path = file_path.replace(head_dic['filename'],file_md5)
            recv_size = 0

            # 先以MD5的值作为文件名，如果已经存在判断是否需要继续下载
            if os.path.exists(md5_file_path):
                is_continue = input('文件已存在，是否继续下载[Y/N]:')
                if is_continue == 'Y':
                    recv_size = os.path.getsize(md5_file_path)
                    self.send_msg('301', recv_size=recv_size)

                    f = open(md5_file_path, 'ab')
                else:
                    f = open(md5_file_path, 'wb')
            else:
                f = open(md5_file_path, 'wb')
            f.seek(recv_size)
            print('开始下载')
            self.send_msg('001')
            bar_generator = self.process_bar(head_dic['file_size'],head_dic['filename'])
            bar_generator.__next__()
            while recv_size < head_dic['file_size']:
                data = self.client.recv(1024)
                f.write(data)
                recv_size += len(data)
                bar_generator.send(recv_size)
            f.close()
            # 下载成功后再对MD5值做比较，如果匹配则下载成功，将文件名改为原来的文件名。
            file_md5_check = MD5.md5_handler(md5_file_path)
            if file_md5_check == file_md5:
                if os.path.isfile(file_path):
                    is_exist = input('文件已存在是否覆盖[Y/N]:')
                    if is_exist == 'Y':
                        os.remove(file_path)
                        os.rename(md5_file_path, file_path)
                    else:
                        os.remove(md5_file_path)
                else:
                    os.rename(md5_file_path, file_path)
                    print()
                    messages.message_handler('203')
        else:
            print(result_code)
            messages.message_handler(result_code)

    def put(self, *args, **kwargs):
        '''
        文件上传功能
        :param args:
        :param kwargs:
        :return:
        '''

        cmd = self.cmds.split(' ')[0]
        local_path = self.cmds.split(' ')[1]
        des_path = self.cmds.split(' ')[2]
        state_code = self.get_respond()['code']

        # 先判断本地文件是否存在
        if not os.path.exists(local_path):
            self.send_msg('205')
            messages.message_handler('201')
            return

        if state_code == '204':
            head_dic = header.make_header(local_path, des_path)
            self.send_msg('202', head_dic=head_dic)

            # 如果服务器端之前有过上传询问是否继续上传
            continue_code = self.get_respond()['code']
            has_send = 0
            if continue_code == '302':
                is_continue = input('是否继续上传[Y/N]')
                if is_continue == 'Y':
                    self.send_msg('302')
                    has_send = self.get_respond()['recv_size']
                else:
                    self.send_msg('206')
            f = open(local_path, 'rb')
            f.seek(has_send)
            bar_generator = self.process_bar(os.path.getsize(local_path), os.path.basename(local_path))
            bar_generator.__next__()

            while has_send < os.path.getsize(local_path):
                data = f.read(1024)
                self.client.send(data)
                has_send += len(data)
                bar_generator.send(has_send)
            # 服务返回上传结果码
            upload_state = self.get_respond()['code']
            messages.message_handler(upload_state)

    def ls(self, *args, **kwargs):
        '''
        查看当前目录的文件
        :param args:
        :param kwargs:
        :return:
        '''
        state_code = self.get_respond()['code']
        if state_code == '402':
            self.client.send('204'.encode(settings.code))
            result_size_obj = self.client.recv(4)
            result_size = struct.unpack('i', result_size_obj)[0]
            has_recv = 0
            recv_data = b''
            while has_recv != result_size:
                data = self.client.recv(1024)
                recv_data += data
                has_recv += len(data)
            print(recv_data.decode('gbk'))
        else:
            messages.message_handler(state_code)

    def cd(self,*args,**kwargs):
        '''
        切换目录
        :param args:
        :param kwargs:
        :return:
        '''
        message = self.get_respond()
        state_code = message['code']
        if state_code == '502':
            new_path = message['replace_dir']
            self.current_path = new_path
        else:
            messages.message_handler(state_code)

    def mkdir(self, *arg, **kwargs):
        '''
        创建目录
        :param arg:
        :param kwargs:
        :return:
        '''
        state_code = self.get_respond()['code']
        messages.message_handler(state_code)

    def process_bar(self, total_size,file_name):
        '''
        进度条
        :param total_size:
        :param file_name:
        :return:
        '''
        current_percent = 0
        last_percent = 0
        while True:
            size = yield
            current_percent = int(size / total_size *100)
            if current_percent > last_percent:
                print('#' * int(current_percent / 2) + ' {percent}% {file_name}'.
                      format(percent=current_percent, file_name=file_name), flush=True, end='\r', )
                last_percent = current_percent
