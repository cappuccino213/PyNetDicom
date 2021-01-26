#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/13 9:37 
# @Author  : Zhangyp
# @File    : common.py
# @Software: PyCharm
# @license : Copyright(C), eWord Technology Co., Ltd.
# @Contact : yeahcheung213@163.com
import logging
import os
from datetime import date
from struct import pack

from configuration import (
    msg_mode, log_level,
    qr_level, qr_keyword,
    output, opd)
from pydicom.dataset import Dataset
from pydicom.datadict import tag_for_keyword, repeater_has_keyword, get_entry
from pydicom.filewriter import write_file_meta_info
from pydicom.tag import Tag
from pydicom.uid import DeflatedExplicitVRLittleEndian

from pynetdicom.dsutils import encode

"""dicom常用的操作的方法"""


# 设置日志
def setup_logging(app_name):
    formatter = logging.Formatter('%(levelname).1s: %(message)s')

    # Setup pynetdicom library's logging
    pynd_logger = logging.getLogger('pynetdicom')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    pynd_logger.addHandler(handler)
    pynd_logger.setLevel(logging.ERROR)

    # Setup application's logging
    app_logger = logging.getLogger('pynetdicom')
    # handler = logging.StreamHandler()
    # handler.setFormatter(formatter)
    app_logger.addHandler(handler)
    app_logger.setLevel(logging.ERROR)

    if msg_mode == 'q':
        app_logger.handlers = []
        app_logger.addHandler(logging.NullHandler())
        pynd_logger.handlers = []
        pynd_logger.addHandler(logging.NullHandler())
    elif msg_mode == 'v':
        app_logger.setLevel(logging.INFO)
        pynd_logger.setLevel(logging.INFO)
    elif msg_mode == 'd':
        app_logger.setLevel(logging.DEBUG)
        pynd_logger.setLevel(logging.DEBUG)

    if log_level:
        levels = {
            'critical': logging.CRITICAL,
            'error': logging.ERROR,
            'warn': logging.WARNING,
            'info': logging.INFO,
            'debug': logging.DEBUG
        }
        app_logger.setLevel(levels[log_level])
        pynd_logger.setLevel(levels[log_level])

    return app_logger


# 创建dcm数据集
def create_dataset(logger=None):
    ds = Dataset()
    ds.QueryRetrieveLevel = qr_level  # 一定传查询层次，不然不会生效

    if qr_keyword:
        try:
            elements = [ElementPath(path) for path in qr_keyword]
            for elem in elements:
                ds = elem.update(ds)
        except Exception as exc:
            if logger:
                logger.error(
                    'Exception raised trying to parse the supplied keywords'
                )
            raise exc
    return ds


class ElementPath(object):
    """Class for parsing DICOM data elements defined using a string path.

    **Path Format**

    The path for the element is defined as
    ``{element(item number).}*element=value``.

    Examples
    --------

    Empty (0010,0010) *Patient Name* element

    >>> ElementPath('PatientName=')
    >>> ElementPath('(0010,0010)=')

    *Patient Name* set to ``CITIZEN^Jan``

    >>> ElementPath('PatientName=CITIZEN^Jan')
    >>> ElementPath('(0010,0010)=CITIZEN^Jan')

    Numeric VRs like (0028,0011) *Columns* are converted to either ``int``
    or ``float``.

    >>> ElementPath('Columns=1024')

    Byte VRs like (7fe0,0010) *Pixel Data* are converted to bytes

    >>> ElementPath('PixelData=00ffea08')

    Elements with VM > 1 can be set by using '\\' (where appropriate)

    >>> ElementPath('AcquisitionIndex=1\\2\\3\\4')

    Empty (300a,00b0) *Beam Sequence*

    >>> ElementPath('BeamSequence=')
    >>> ElementPath('(300a,00b0)=')

    *Beam Sequence* with one empty item

    >>> ElementPath('BeamSequence[0]=')

    *Beam Sequence* with one non-empty item

    >>> ElementPath('BeamSequence[0].PatientName=CITIZEN^Jan')

    Nested sequence items

    >>> ElementPath('BeamSequence[0].BeamLimitingDeviceSequence[0].NumberOfLeafJawPairs=1')

    *Beam Sequence* with 4 empty items

    >>> ElementPath('BeamSequence[3]=')
    """

    def __init__(self, path, parent=None):
        """Initialise a new ElementPath.

        Parameters
        ----------
        path : str
            The string describing the complete path of a DICOM data element.
        parent : ElementPath or None
            The parent of the current ``ElementPath`` (if there is one) or
            ``None``.
        """
        # Default pydicom empty value
        self._value = ''

        self.components = path
        self._parent = parent

    @property
    def child(self):
        """Return the current object's child ElementPath (or None).

        Returns
        -------
        ElementPath or None
            If the path ends with the current object then returns ``None``,
            otherwise returns an ``ElementPath`` instance for the next
            component of the path.
        """
        if len(self.components) == 1:
            return None

        return ElementPath('.'.join(self.components[1:]), self)

    @property
    def components(self):
        """Return the current Element's components as list of str.

        Returns
        -------
        list of str
            The path starting from the current object.
        """
        return self._components

    @components.setter
    def components(self, path):
        """Set the element's components str.

        Parameters
        ----------
        str
            The path to use for the current object.
        """
        value = ''
        if '=' in path:
            path, value = path.split('=', 1)

        self._components = path.split('.')

        # Parse current component and set attributes accordingly
        tag = self.tag
        try:
            # Try DICOM dictionary for public elements
            self._entry = get_entry(tag)
        except Exception as exc:
            # Private element
            self._entry = ('UN', '1', 'Unknown', False, 'Unknown')

        # Try to convert value to appropriate type
        self.value = value

    @property
    def is_sequence(self):
        """Return True if the current component is a sequence."""
        start = self.components[0].find('[')
        end = self.components[0].find(']')
        if start >= 0 or end >= 0:
            is_valid = True
            if not (start >= 0 and end >= 0):
                is_valid = False
            if start > end:
                is_valid = False
            if start + 1 == end:
                is_valid = False

            if is_valid:
                try:
                    item_nr = int(self.components[0][start + 1:end])
                    if item_nr < 0:
                        is_valid = False
                except:
                    is_valid = False

            if not is_valid:
                raise ValueError(
                    "Element path contains an invalid component: '{}'"
                        .format(self.components[0])
                )
            self._item_nr = item_nr

            return True

        return False

    @property
    def item_nr(self):
        """Return the element's sequence item number.

        Returns
        -------
        int or None
            If the current component of the path is a sequence then returns
            the item number, otherwise returns ``None``.
        """
        if self.is_sequence:
            return self._item_nr

        return None

    @property
    def keyword(self):
        """Return the element's keyword as a str.

        Returns
        -------
        str
            The element's keyword if an official DICOM element, otherwise
            'Unknown'.
        """
        return self._entry[4]

    @property
    def parent(self):
        """Return the current object's parent ElementPath.

        Returns
        -------
        ElementPath or None
            If the current component was part of a larger path then returns
            the previous component as an ``ElementPath``, otherwise returns
            ``None``.
        """
        return self._parent

    @property
    def tag(self):
        """Return the element's tag as a pydicom.tag.Tag."""
        tag = self.components[0]
        if self.is_sequence:
            tag = tag.split('[')[0]

        # (gggg,eeee) based tag
        if ',' in tag:
            group, element = tag.split(',')
            if '(' in group:
                group = group.replace('(', '')
            if ')' in element:
                element = element.replace(')', '')

            if len(group) != 4 or len(element) != 4:
                raise ValueError(
                    "Unable to parse element path component: '{}'"
                        .format(self.components[0])
                )

            return Tag(group, element)

        # From this point on we assume that a keyword was supplied
        kw = tag
        # Keyword based tag - private keywords not allowed
        if repeater_has_keyword(kw):
            raise ValueError(
                "Repeating group elements must be specified using "
                "(gggg,eeee): '{}'".format(self.components[0])
            )

        tag = tag_for_keyword(kw)
        # Test against None as 0x00000000 is a valid tag
        if tag is not None:
            return Tag(tag)

        raise ValueError(
            "Unable to parse element path component: '{}'"
                .format(self.components[0])
        )

    def update(self, ds):
        """Return a pydicom Dataset after updating it.

        Parameters
        ----------
        ds : pydicom.dataset.Dataset
            The dataset to update.

        Returns
        -------
        pydicom.dataset.Dataset
            The updated dataset.
        """
        if self.tag not in ds:
            # Add new element or sequence to dataset
            if self.is_sequence:
                # Add new SequenceElement with no items
                ds.add_new(self.tag, self.VR, [])

                # Add [N] empty items
                if self.item_nr is not None:
                    for ii in range(self.item_nr + 1):
                        ds[self.tag].value.append(Dataset())

                # SequenceElement=
                if self.child is None:
                    return ds
            else:
                # Element=(value)
                ds.add_new(self.tag, self.VR, self.value)
                return ds

        else:
            elem = ds[self.tag]
            # Either update or add new item
            if not self.is_sequence:
                # Update Element=(value)
                elem.value = self.value
                return ds

            # Check if we need to add a new item to an existing sequence
            # SequenceElement currently has N items
            nr_items = len(elem.value)
            if nr_items - self.item_nr == 0:
                # New SequenceElement[N + 1] item
                elem.value.append(Dataset())
            elif nr_items < self.item_nr:
                for ii in range(self.item_nr - nr_items):
                    elem.value.append(Dataset())

        if self.child:
            self.child.update(ds[self.tag].value[self.item_nr])

        return ds

    @property
    def value(self):
        """Return the value assigned to the data element."""
        if self.parent is None:
            return self._value

        parent = self.parent
        while parent.parent:
            parent = parent.parent

        return parent._value

    @value.setter
    def value(self, value):
        """Set the element's value.

        Parameters
        ----------
        value : str
            A string representation of the value to use for the element.

            * If the element VR is AE, AS, AT, CS, DA, DS, DT, IS, LO, LT, PN,
              SH, ST, TM, UC, UI, UR or UT then no conversion will be
              performed.
            * If the element VR is SL, SS, SV, UL, US or UV then the ``str``
              will be converted to an ``int`` using ``int(value)``.
            * If the element VR is FD or FL then the ``str`` will be converted
              to a ``float`` using ``float(value)``.
            * If the VR is not one of the above then the ``str`` will be
              converted to ``bytes`` using the assumption that ``value`` is a
              string of hex bytes with the correct endianness (e.g.
              '0aff00f0ec').
        """
        _str = [
            'AE', 'AS', 'AT', 'CS', 'DA', 'DS', 'DT', 'IS', 'LO',
            'LT', 'PN', 'SH', 'ST', 'TM', 'UC', 'UI', 'UR', 'UT'
        ]
        _int = ['SL', 'SS', 'SV', 'UL', 'US', 'UV']
        _float = ['FD', 'FL']
        _byte = ['OB', 'OD', 'OF', 'OL', 'OW', 'OV', 'UN']

        # Try to convert value to appropriate type
        if self.VR == 'AT' and '\\' in value:
            value = value.split('\\')
        elif self.VR in _str or self.VR == 'SQ':
            pass
        elif self.VR in _int and value:
            if '\\' in value:
                value = [int(vv) for vv in value.split('\\')]
            else:
                value = int(value)
        elif self.VR in _float and value:
            if '\\' in value:
                value = [float(vv) for vv in value.split('\\')]
            else:
                value = float(value)
        elif not value:
            value = ''
        else:
            # Convert to byte, assuming str is in hex
            value = [
                value[ii] + value[ii + 1] for ii in range(0, len(value), 2)
            ]
            value = [int(ii, 16) for ii in value]
            value = pack('{}B'.format(len(value)), *value)

        self._value = value

    @property
    def VR(self):
        """Return the element's VR as str."""
        return self._entry[0]


# 处理存储
def handle_store(event, app_logger):
    try:
        ds = event.dataset
        # Remove any Group 0x0002 elements that may have been included
        ds = ds[0x00030000:]
    except Exception as exc:
        app_logger.error("Unable to decode the dataset")
        app_logger.exception(exc)
        # Unable to decode dataset
        return 0x210

    # Add the file meta information elements
    ds.file_meta = event.file_meta

    # 获取影像信息，供存储文件的路径使用
    try:
        sop_class = ds.SOPClassUID
        study_instance = ds.StudyInstanceUID
        sop_instance = ds.SOPInstanceUID
    except Exception as exc:
        app_logger.error(
            "Unable to decode the received dataset or missing 'SOP Class "
            "UID' and/or 'SOP Instance UID' elements"
        )
        app_logger.exception(exc)
        # Unable to decode dataset
        return 0xC210

    try:
        # Get the elements we need
        mode_prefix = SOP_CLASS_PREFIXES[sop_class][
            0]  # 获取检查类型前缀,如果获取不到,可以从venv\Lib\site-packages\pynetdicom\sop_class.py的_STORAGE_CLASSES获得对照，在SOP_CLASS_PREFIXES补上去
    except KeyError:
        mode_prefix = 'UN'

    filename = '{0!s}.{1!s}.dcm'.format(mode_prefix, sop_instance)
    app_logger.info('Storing DICOM file: {0!s}'.format(filename))

    if os.path.exists(filename):
        app_logger.warning('DICOM file already exists, overwriting')

    status_ds = Dataset()
    status_ds.Status = 0x0000

    # Try to save to output-directory
    if output == 1:
        today = date.today().strftime('%Y%m%d')  # 获的当前日期
        store_dir = '{0!s}/{1!s}'.format(today, study_instance)
        out_put_dir = os.path.join(opd, store_dir)
        filename = os.path.join(out_put_dir, filename)
        try:
            os.makedirs(out_put_dir, exist_ok=True)  # 创建输出文件夹
        except Exception as exc:
            app_logger.error('Unable to create the output directory:')
            app_logger.error("    {0!s}".format(opd))
            app_logger.exception(exc)
            # Failed - Out of Resources - IOError
            status_ds.Status = 0xA700
            return status_ds

    try:
        if event.context.transfer_syntax == DeflatedExplicitVRLittleEndian:
            # Workaround for pydicom issue #1086
            with open(filename, 'wb') as f:
                f.write(b'\x00' * 128)
                f.write(b'DICM')
                f.write(write_file_meta_info(f, event.file_meta))
                f.write(encode(ds, False, True, True))
        else:
            # We use `write_like_original=False` to ensure that a compliant
            #   File Meta Information Header is written
            ds.save_as(filename, write_like_original=False)
        status_ds.Status = 0x0000  # Success

    except IOError as exc:
        app_logger.error('Could not write file to specified directory:')
        app_logger.error("    {0!s}".format(os.path.dirname(filename)))
        app_logger.exception(exc)
        # Failed - Out of Resources - IOError
        status_ds.Status = 0xA700
    except Exception as exc:
        app_logger.error('Could not write file to specified directory:')
        app_logger.error("    {0!s}".format(os.path.dirname(filename)))
        app_logger.exception(exc)
        # Failed - Out of Resources - Miscellaneous error
        status_ds.Status = 0xA701

    return status_ds


# 影像存储类型映射
SOP_CLASS_PREFIXES = {
    '1.2.840.10008.5.1.4.1.1.2': ('CT', 'CT Image Storage'),
    '1.2.840.10008.5.1.4.1.1.2.1': ('CTE', 'Enhanced CT Image Storage'),
    '1.2.840.10008.5.1.4.1.1.4': ('MR', 'MR Image Storage'),
    '1.2.840.10008.5.1.4.1.1.4.1': ('MRE', 'Enhanced MR Image Storage'),
    '1.2.840.10008.5.1.4.1.1.128': (
        'PT', 'Positron Emission Tomography Image Storage'
    ),
    '1.2.840.10008.5.1.4.1.1.130': ('PTE', 'Enhanced PET Image Storage'),
    '1.2.840.10008.5.1.4.1.1.481.1': ('RI', 'RT Image Storage'),
    '1.2.840.10008.5.1.4.1.1.481.2': ('RD', 'RT Dose Storage'),
    '1.2.840.10008.5.1.4.1.1.481.5': ('RP', 'RT Plan Storage'),
    '1.2.840.10008.5.1.4.1.1.481.3': ('RS', 'RT Structure Set Storage'),
    '1.2.840.10008.5.1.4.1.1.1': ('CR', 'Computed Radiography Image Storage'),
    '1.2.840.10008.5.1.4.1.1.6.1': ('US', 'Ultrasound Image Storage'),
    '1.2.840.10008.5.1.4.1.1.6.2': ('USE', 'Enhanced US Volume Storage'),
    '1.2.840.10008.5.1.4.1.1.12.1': (
        'XA', 'X-Ray Angiographic Image Storage'
    ),
    '1.2.840.10008.5.1.4.1.1.12.1.1': ('XAE', 'Enhanced XA Image Storage'),
    '1.2.840.10008.5.1.4.1.1.20': ('NM', 'Nuclear Medicine Image Storage'),
    '1.2.840.10008.5.1.4.1.1.7': ('SC', 'Secondary Capture Image Storage'),
    '1.2.840.10008.5.1.4.1.1.1.1': ('DX', 'Digital XRay Image Presentation Storage')
}
