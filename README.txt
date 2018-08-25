简单FTP程序,C/S架构实现了文件上传下载，切换目录，查看目录下的文件，创建目录，断点续传等功能, 已通过线程池修改最大响应用户量
适用平台：Windows
服务器端命令语法：
    启动程序：python FTP_CLIENT.py -s SERVER_IP -u USERNAME -p PASSWORD 例如：python FTP_CLIENT.py -s 127.0.0.1 -u Harry -p cs1993413
    下载文件：get FileName 例如：get test.pdf
    上传文件：put LOCAL_FILENAME DES_PATH 例如：example： put G:\FTP\FTP_CLIENT\download\test2/pdf 111\test2.pdf
    查看目录：查看当前目录ls 查看指定目录ls TargetPath
    切换目录：cd TargetPath 切换至目标路径， cd .. 切换上一级目录
    创建目录：mkdir DirName
状态码：
    '001': '解决粘包',
    '101': '发送命令',
    '103': '认证失败,用户名或密码错误',
    '102': '认证通过,欢迎登录',
    '104': '参数错误',
    '203': '下载成功!',
    '201': '文件不存在',
    '202': '发送文件报头',
    '204': '准备接收报头',
    '205': '取消上传',
    '206': '重新上传',
    '207': '上传成功',
    '208': '上传失败',
    '301': '下载文件断点续传',
    '302': '上传文件断点续传',
    '303': '发送上传断点size',
    '304': '准备接收上传文件',
    '401': '路径有误',
    '402': '正确路径',
    '502': '成功切换路径',
    '503': '已经是顶级目录',
    '504': '准备接收当前新路径',
    '505': '创建目录成功',
    '506': '目录已存在'


FTP_SERVER TREE
    ├─bin
    │      CreateUsers.py     创建用户
    │      FTP_SERVER.py      服务器启动接口
    │      __init__.py
    │
    ├─config
    │  │  account.ini         用户配置文件
    │  │  settings.py         程序配置文件
    │  │  __init__.py
    │  │
    │
    │
    ├─core
    │  │  auth.py            认证模块
    │  │  header.py          报头制作
    │  │  main.py            程序主逻辑
    │  │  md5.py             MD5验证模块
    │  │  register.py        用户注册
    │  │  userinfo.py        用户信息类
    │  │  __init__.py
    │  │
    │
    │
    ├─Home                   用户家目录
    │  ├─Beal
    │  └─Harry
    │      │  est10.pdf
    │      │  test.swf
    │      │  test2.pdf
    │      │  test3.jpg
    │      │
    │      ├─111
    │      │      TEST
    │      │      test2.pdf
    │      │
    │      └─test
    │          └─testdir
    └─log                 log功能暂未实现
            __init__.py、

FTP client Tree
    ├─bin
    │      FTP_CLIENT.py    服务器程序启动入口
    │
    │
    ├─config
    │  │  settings.py       程序配文件
    │  │
    │
    │
    │
    ├─core
    │  │  Argv.py          参数验证模块
    │  │  header.py        头文件制作
    │  │  main.py          程序主逻辑
    │  │  MD5.py           MD5验证
    │  │  messages.py      消息输出
    │  │
    │
    │
    └─download            下载文件夹
            est10.pdf
        test2.pdf