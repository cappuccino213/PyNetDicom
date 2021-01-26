#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/12 17:11 
# @Author  : Zhangyp
# @File    : configuration.py
# @Software: PyCharm
# @license : Copyright(C), eWord Technology Co., Ltd.
# @Contact : yeahcheung213@163.com

"""本地scu节点配置"""
LocalAE = 'zyp_echo_scu'


"""Remote scp节点配置"""
AETitle = 'DYSERVICE'
addr = '192.168.1.18'
port = 108


"""log设置"""
# 调试模式
msg_mode = 'd'
# 'q' quiet mode, print no warnings and errors
# 'v' verbose mode, print processing details
# 'd' debug mode, print debug information

# 日志等级
log_level = 'debug'   # 'critical', 'error', 'warn', 'info', 'debug'


"""网络设置"""
network_timeout = 30  # 单位秒
acse_timeout = 30  # timeout for ACSE messages
dimse_timeout = 30  # timeout for DIMSE messages

pdu = 16382  # set max receive pdu to n bytes(最大接受影像)


"""查询参数"""
qr_mode = 'getscu'

qr_level = 'STUDY'  # PATIENT,STUDY,SERIES（大写） QR层次

# query_keyword = {"AccessionNumber":'25',"PatientID":'',"StudyInstanceUID":""}
qr_keyword = ['AccessionNumber=DY018028']
# qr_keyword = ['AccessionNumber=3']

# cmd查询条件
# qr_condition = 'AccessionNumber=149660'
# qr_condition = 'AccessionNumber=DY018028' XA
qr_condition = 'AccessionNumber=DY018996'


"""扩展参数"""
multi_frame = 1  # 是否多帧影像

"""输出参数"""
output = 1  # 是否接受影像后保存
# opd = r'E:\my project\PyNetDicom\ImageFiles'  # 输出路径
opd = r'E:\PyProject\PyNetDicom\ImageFiles'  # 输出路径

"""echo参数"""
repeat_num = 4