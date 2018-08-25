# Author: harry.cai
# DATE: 2018/3/18
import os
import sys
from core import Argv
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 连接服务器的IP从传入的参数获取
server_address = Argv.ArgvHandler.check_server()
# 连接服务器的端口号
server_port = 9000

# 字符编码
code = 'utf-8'
# 下载的路径
DownloadPath = os.path.join(BASEDIR,'download')

