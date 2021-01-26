#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/4/27 10:58
# @Author  : Zhangyp
# @File    : c-echo.py
# @Software: PyCharm
# @license : Copyright(C), eWord Technology Co., Ltd.
# @Contact : yeahcheung213@163.com

"""将DICOM C-ECHO发送到对等验证SCP（在TCP / IP地址addr处 ，侦听端口号port ）"""
from pynetdicom import AE
from config import LocalAE, AETitle, addr, port

ae = AE(ae_title=LocalAE)
ae.add_requested_context('1.2.840.10008.1.1')
assoc = ae.associate(addr, port, ae_title=AETitle)
if assoc.is_established:
	status = assoc.send_c_echo()
	if status:
		print('C-ECHO Response: 0x{0:04x}'.format(status.Status))
	assoc.release()
