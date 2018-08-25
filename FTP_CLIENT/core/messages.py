# Author: harry.cai
# DATE: 2018/3/18


def message_handler(code):
    '''
    根据消息代码打印不同的信息
    :param code:
    :return:
    '''
    code_dic = {
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
    }
    if code in code_dic:
        print(code_dic[code])