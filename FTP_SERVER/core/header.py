# Author: harry.cai
# DATE: 2018/3/19
import struct
import json
import os
from core import md5
from config import settings


def make_header(file_path):
    '''
    制作文件报头，包括文件名，文件大小和MD5
    :param file_path:
    :return:
    '''
    file_size = os.path.getsize(file_path)
    file_md5 = md5.Md5Action.md5_check(file_path)

    head_dic = {
        'filename': os.path.basename(file_path),
        'md5': file_md5,
        'file_size': file_size
    }

    return head_dic
