# -*- coding: utf-8 -*-
# @Time    : 2019/9/7 15:49
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : run.py
# @Software: PyCharm


import os
import sys
import toml
import time
from GeetestCracker import api
from GeetestCracker import cracker3
from multiprocessing import Process


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
    try:
        config = toml.load(config_path)
    except:
        return
    global_config = config.get('global', {})
    server_config = config.get('server', {})
    worker_config = config.get('worker', {})
    address = global_config.get('address', "127.0.0.1")
    port = global_config.get('port', 8778)
    print(f"URL: http://{address}:{port}/")
    process_list = []
    try:
        if server_config.get('enable'):
            print("Server: ON")
            Process(target=api.main, args=("0.0.0.0", port)).start()
        else:
            print("Server: OFF")
        if worker_config.get('enable'):
            print("Worker: ON")
            Process(target=cracker3.main, args=(
                address, port, worker_config.get('headless', False), worker_config.get('workers', 2),
                worker_config.get('delay', 2))).start()
        else:
            print("Worker: OFF")
        while True:
            # 避免进入死循环, 无法关闭主进程
            time.sleep(1)

    except KeyboardInterrupt:
        # Ctrl C 杀死未关闭进程
        for process in process_list:
            if process.is_alive():
                process.terminate()


if __name__ == "__main__":
    main()
