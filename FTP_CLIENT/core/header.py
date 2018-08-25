# Author: harry.cai
# DATE: 2018/3/19
import os
import json
from core import MD5
from config import settings


def make_header(file_path, des_path):
    '''
        制作文件报头，包括文件名，文件大小和MD5
        :param file_path:
        :return:
    '''
    file_size = os.path.getsize(file_path)
    file_md5 = MD5.md5_handler(file_path)

    head_dic = {
        'filename': os.path.basename(file_path),
        'md5': file_md5,
        'file_size': file_size,
        'des_path': des_path
    }

    return head_dic