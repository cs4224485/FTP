# Author: harry.cai
# DATE: 2018/3/19
import hashlib


def md5_handler(file_path):
    '''
    文件MD5校验
    :param file_path:
    :return:
    '''
    obj = hashlib.md5()
    f = open(file_path, 'rb')
    while True:
        b = f.read(1024)
        if not b:
            break
        obj.update(b)
    f.close()
    return obj.hexdigest()