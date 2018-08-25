# Author: harry.cai
# DATE: 2018/3/18

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from core import main
import threading
if __name__ == '__main__':
    client = main.MyClient(settings.server_address,settings.server_port)
    client.run()