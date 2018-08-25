# Author: harry.cai
# DATE: 2018/3/18
import os
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 字符编码
code = 'utf-8'

# 监听的ip地址和端口
address = '127.0.0.1'
port = 9000

# 家目录路径
HomeDir = os.path.join(BASEDIR, 'Home')

# 用户配置路径
AccountPath = os.path.join(BASEDIR,'config','account.ini')

# 最大线程
MaxThreads = 5