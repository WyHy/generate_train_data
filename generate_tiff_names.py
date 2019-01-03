# coding: utf-8

"""
   基于已审核的细胞图像文件名生成对应大图的 xml， xml 包含信息为对应大图里的已审核细胞位置
   细胞图像包含其来源大图名称，如
    # 1-p0.0000_markedAs_ASCH_2017-10-27-16_12_50_x9659_y28027_w616_h331.jpg
    # 1-p0.0000_markedAs_CC_2018-03-27-23_18_27_x5675_y23431_w230_h207_4x.jpg
    # 1-p0.0000_markedAs_ACTINO_2018-06-20_18_37_06_x34602_y10123_w145_h172_2x.jpg
    # 1-p0.0000_2017-11-24-13_16_54_x6626_y35845_w150_h79_4x.jpg
    # 1-p0.0001_2017-10-09-17_12_28_x19230_y29594_w370_h910_.jpg
    # m1_2018-04-04-17_50_08_x11194_y33583_w163_h112.jpg
    # m1_2018-06-20_18_37_06_x10880_y42947_w113_h122.jpg

"""

import json
import os
import re

from constants import PATHOLOGY_TYPE_CLASSES, METADATA_FILE_PATH, AGC_CLASSES, CHECKED_CELL_XML_SAVE_PATH, \
    TIFF_IMAGE_RESOURCE_PATH
from utils import FilesScanner, generate_checked_level_xml, get_location_from_filename, generate_name_path_dict

if not os.path.exists(METADATA_FILE_PATH):
    os.makedirs(METADATA_FILE_PATH, exist_ok=True)

if not os.path.exists(CHECKED_CELL_XML_SAVE_PATH):
    os.makedirs(CHECKED_CELL_XML_SAVE_PATH, exist_ok=True)


def gen_slide_names(path):
    files = FilesScanner(path, ['.bmp']).get_files()

    # # 1-p0.6042_BD1607254-子宫内膜C_2018-10-09 16_42_03_x23043_y40485_w162_h218_2x.jpg
    pattern00 = re.compile(r'1-p\d\.\d+_(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)(_\dx)?.bmp')

    # 2018-03-22-11_26_58_x15789_y31806_w63_h61_s385.jpg
    pattern01 = re.compile(r'(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)(_s\d+)?.bmp')

    names = []
    for item in files:
        # 细胞图文件名
        basename = os.path.basename(item).replace(' ', '-')

        items = re.findall(pattern00, basename)
        if not items:
            items = re.findall(pattern01, basename)

        if items:
            parent_name, x, y, w, h, _ = items[0]
            if parent_name not in names:
                names.append(parent_name)
        else:
            raise Exception("%s IS NOT ACCEPTED!" % basename)
            exit()

    return names


if __name__ == '__main__':
    # 自动标注细胞图像存储位置
    auto_path = [
        '/home/cnn/Development/DATA/NEW_REQUIREMENT_4X/CELLS',
    ]

    total = len(auto_path)
    for index, path in enumerate(auto_path):
        print("LOAD %s / %s ..." % (index + 1, total))
        names = gen_slide_names(path)
        with open("./works_slide_names.txt", 'w') as o:
            for name in names:
                o.write("%s\n" % name)
