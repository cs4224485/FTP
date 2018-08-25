# Author: harry.cai
# DATE: 2018/3/18
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import register

if __name__ == '__main__':
    register.register()