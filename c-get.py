#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/4/28 16:56
# @Author  : Zhangyp
# @File    : c-get.py
# @Software: PyCharm
# @license : Copyright(C), eWord Technology Co., Ltd.
# @Contact : yeahcheung213@163.com
from pydicom.dataset import Dataset

from pynetdicom import (
	AE, evt, build_role,
	PYNETDICOM_IMPLEMENTATION_UID,
	PYNETDICOM_IMPLEMENTATION_VERSION
)

from pynetdicom.sop_class import (
	_QR_CLASSES as QR,
	_STORAGE_CLASSES as ST
)

import os
from config import LocalAE, AETitle, IP, PORT, SavePath


# 创建文件夹
def mkdir(path):
	folder = os.path.exists(path)
	if not folder:
		os.makedirs(path)
		print('文件夹创建成功')
	else:
		pass
		print("文件夹已存在")


# 实现处理存储
def handle_store(event):
	"""Handle a C-STORE request event."""
	ds = event.dataset
	context = event.context
	
	# Add the DICOM File Meta Information
	meta = Dataset()
	meta.MediaStorageSOPClassUID = ds.SOPClassUID
	meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
	meta.ImplementationClassUID = PYNETDICOM_IMPLEMENTATION_UID
	meta.ImplementationVersionName = PYNETDICOM_IMPLEMENTATION_VERSION
	meta.TransferSyntaxUID = context.transfer_syntax
	
	# Add the file meta to the dataset
	ds.file_meta = meta
	
	ds.file_meta.TransferSyntaxUID = '1.2.840.10008.1.2'
	# Set the transfer syntax attributes of the dataset
	# ds.is_little_endian = context.transfer_syntax.is_little_endian
	# ds.is_implicit_VR = context.transfer_syntax.is_implicit_VR
	
	# 按实例名保存影像
	# file_path = os.path.join(SavePath, ds.StudyInstanceUID)  # 拼接存储路径
	# mkdir(file_path)  # 若不存在创建实例文件夹
	# save_path = os.path.join(file_path, ds.SOPInstanceUID)
	# ds.save_as(save_path, write_like_original=False)
	ds.save_as(ds.SOPInstanceUID, write_like_original=False)
	return 0x0000  # 成功返回0


# 存储事件
handlers = [(evt.EVT_C_STORE, handle_store)]

ae = AE(ae_title=LocalAE)
# Add the requested presentation contexts (QR SCU)
# ae.add_requested_context(QR["PatientRootQueryRetrieveInformationModelGet"])
ae.add_requested_context(QR["StudyRootQueryRetrieveInformationModelGet"])
# Add the requested presentation context (Storage SCP)
ae.add_requested_context(ST['CTImageStorage'])

# Create an SCP/SCU Role Selection Negotiation item for DX Image Storage
# role = build_role(ST['DigitalXRayImagePresentationStorage'], scp_role=True)
role = build_role(ST['CTImageStorage'], scp_role=True)

# QR层次定义
ds = Dataset()
ds.QueryRetrieveLevel = 'SERIES'  # QR层次 PATIENT\STUDY\SERIES\IMAGE
"""查询条件"""
# Unique key for STUDY level
ds.AccessionNumber = '212'
ds.StudyInstanceUID = '2.25.32134402068659753216365745016710468715'
ds.SeriesInstanceUID = '2.25.200415808230095236475307643644746736546'
# ds.SeriesInstanceUID = '1.3.12.2.1107.5.1.4.65270.30000020032317201059800119336'

# 建立节点连接
assoc = ae.associate(IP, PORT, ae_title=AETitle, ext_neg=[role], evt_handlers=handlers)
if assoc.is_established:
	responses = assoc.send_c_get(ds, QR["StudyRootQueryRetrieveInformationModelGet"])
	for (status, identifier) in responses:
		if status:
			print('C-GET query status: 0x{0:04x}'.format(status.Status))
			# If the status is 'Pending' then `identifier` is the C-GET response
			if status.Status in (0xFF00, 0xFF01):
				print(identifier)
		else:
			print('Connection timed out, was aborted or received invalid response')
	# Release the association
	assoc.release()
else:
	print('Association rejected, aborted or never connected')
# TODO
# FIXME c-get失败，不会创建指定文件目录，整理代码结构