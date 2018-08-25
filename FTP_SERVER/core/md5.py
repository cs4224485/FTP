# Author: harry.cai
# DATE: 2018/3/18
import hashlib


class Md5Action:
    """
    做MD5计算
    """
    @staticmethod
    def md5_passwd(password):
        '''
        负责对密码进行MD5
        :param password:
        :return: 返回密码的MD5值
        '''
        md = hashlib.md5()
        md.update(password.encode('utf-8'))
        password_md5 = md.hexdigest()
        return password_md5

    @staticmethod
    def md5_check(file_path):
        '''
        对文件进行MD5校验
        :param file_path:
        :return:
        '''
        obj = hashlib.md5()
        f = open(file_path, 'rb')
        while True:
            b = f.read(8096)
            if not b:
                break
            obj.update(b)
        f.close()
        return obj.hexdigest()