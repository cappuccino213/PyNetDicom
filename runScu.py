#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/22 11:04 
# @Author  : Zhangyp
# @File    : runScu.py
# @Software: PyCharm
# @license : Copyright(C), eWord Technology Co., Ltd.
# @Contact : yeahcheung213@163.com
from subprocess import run
# from configuration import (AETitle, LocalAE, addr, port, log_level, qr_level,
#                            repeat_num, qr_condition,
#                            msg_mode)
from configuration import *


# 加载参数
def load_parameter_hint():
    print("""
    --加载参数
    scu-AE:{0}
    RemoteAE:{1}  
    RemoteAddr:{2}  
    RemotePort:{3} 
    LogLevel:{4}
    QueryLevel:{5}  
    """.format(LocalAE, AETitle, addr, port, log_level, qr_level))


# 控制台输入输出
def option_cmd():
    print("""请输入scu操作的序号：
    1 c-echo
    2 c-find
    3 c-get
    4 c-move
    """)
    # option_num = sys.argv[0]
    while True:
        option_num = int(input())
        if option_num == 1:
            load_parameter_hint()
            cmd_line = "python echoscu.py {0!s} {1!s} -ll {2!s} -aet {3!s} -aec {4!s} --repeat {5!s} -{6}".format(addr,
                                                                                                                  port,
                                                                                                                  log_level,
                                                                                                                  LocalAE,
                                                                                                                  AETitle,
                                                                                                                  repeat_num,
                                                                                                                  msg_mode)
            break
        elif option_num == 2:
            load_parameter_hint()
            cmd_line = "python findscu.py {0} {1} -aet {2} -aec {3} -ll {4}  -k {5} -{6}".format(addr, port, LocalAE,
                                                                                                 AETitle, log_level,
                                                                                                 qr_condition, msg_mode)
            break
        elif option_num == 3:
            load_parameter_hint()
            cmd_line = "python getscu.py {0} {1} -ll {2}  -aet {3} -aec {4} -k {5} -od {6} -{7} --{8}".format(addr,
                                                                                                              port,
                                                                                                              log_level,
                                                                                                              LocalAE,
                                                                                                              AETitle,
                                                                                                              qr_condition,
                                                                                                              opd,
                                                                                                              msg_mode,
                                                                                                              qr_level.lower())
            break
        elif option_num == 4:
            load_parameter_hint()
            cmd_line = "4"
            break
        else:
            print("输入错误,请输入1~4")
    return cmd_line


# 执行cmd命令
def run_cmd(cmd_line):
    if cmd_line:
        run(cmd_line, shell=True)


if __name__ == '__main__':
    run_cmd(option_cmd())
