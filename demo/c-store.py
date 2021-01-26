#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/4/27 13:52
# @Author  : Zhangyp
# @File    : c-store.py
# @Software: PyCharm
# @license : Copyright(C), eWord Technology Co., Ltd.
# @Contact : yeahcheung213@163.com
from config import *
import os
from pynetdicom import AE
from pydicom import dcmread

"""遍历影像文件"""


def find_images(path):
	images = []
	for file in os.listdir(path):
		if file.endswith('.dcm') or file.endswith('.DCM'):
			images.append(file)
	return images


"""影像c-store"""


def store_image(file):
	# 1.读取影像
	ds = dcmread(file)
	# 2.转化传输语法
	ds.file_meta.TransferSyntaxUID = '1.2.840.10008.1.2'  # 'Implicit VR Little Endian'
	# 3.Initialise the Application Entity
	ae = AE(ae_title=LocalAE)
	# 4.上下文添加影像类型
	class_uid = ds['SOPClassUID'].value
	ae.add_requested_context(class_uid)
	# 5.Associate with peer AE at IP 127.0.0.1 and port 11112
	assoc = ae.associate(addr, port, ae_title=AETitle)
	# 6.发送影像
	if assoc.is_established:
		# Use the C-STORE service to send the dataset #returns the response status as a pydicom Dataset
		status = assoc.send_c_store(ds)
		if status:
			# If the storage request succeeded this will be 0x0000
			print('C-STORE request status: 0x{0:04x}'.format(status.Status))
		else:
			print('Connection timed out, was aborted or received invalid response')
		# Release the association
		assoc.release()
	else:
		print('Association rejected, aborted or never connected')


"""批量c-store"""


def main():
	images = find_images(Path)
	for i in images:
		image_file = os.path.join(Path, i)
		store_image(image_file)


if __name__ == '__main__':
	# f = find_images(Path)
	# print(f)
	# store_image(r"E:\my project\PyNetDicom\ImageFiles\0001-0001-0001-W256L128.DCM")
	main()
