# coding: utf-8

"""
常用变量 列表
"""

# 当前可识别病理类型 length = 12
import os

PATHOLOGY_TYPE_CLASSES = ["HSIL", "ASCH", "LSIL", "ASCUS", "SCC", "EC", "AGC", "FUNGI", "TRI", "CC", "ACTINO", "VIRUS", "MC", "SC", "RC", "GEC", ]

# 病理类型对应颜色 length = 12
PATHOLOGY_TYPE_COLORS = ["#aa0000", "#aa007f", "#005500", "#00557f", "#0055ff", "#aa55ff", "#ff5500", "#00aa00", "#00aa7f", "#00aaff", "#55aa00", "#55aa7f", "#000000", "#aa00ff", "#ff0000", "#aa5500", ]

# 统一归为 AGC 类别的病理图像类别
AGC_CLASSES = ['AGC1', 'AGC2', 'AGC3', 'ADC']

# 病理类别=>对应颜色
TYPE_to_COLOR_DICT = dict(zip(PATHOLOGY_TYPE_CLASSES, PATHOLOGY_TYPE_COLORS))

# 颜色=>对应病理类别
COLOR_to_TYPE_DICT = dict(zip(PATHOLOGY_TYPE_COLORS, PATHOLOGY_TYPE_CLASSES))

# 数据存储根目录
DATA_RESOURCE_ROOT_PATH = os.path.join(os.environ['HOME'] + "/Development/DATA/TRAIN_DATA")

# 病理图像本地资源库路径
TIFF_IMAGE_RESOURCE_PATH = os.path.join(DATA_RESOURCE_ROOT_PATH, "TIFFS")

# 中间数据文件生成目录
METADATA_FILE_PATH = os.path.join(DATA_RESOURCE_ROOT_PATH, "META")

# 训练 xml 数据保存目录
TRAIN_DATA_SAVE_PATH = os.path.join(DATA_RESOURCE_ROOT_PATH, "XMLS")

# 训练细胞图像数据保存目录
CELL_IMAGES_SAVE_PATH = os.path.join(DATA_RESOURCE_ROOT_PATH, "CELLS")

# 远程路径标识符
REMOTE_PATH_FLAG = "smb-share:server="

# 最低重叠率
ACCEPTED_OVERLAPPED_RATIO = 0.5

# 文件打开失败记录存储
TIFF_OPEN_FAIL_RECORDS = 'TIFF_OPEN_FAIL_RECORDS.txt'

# 细胞计数文件名称
CELL_COUNT_FILE_NAME = '[NOTICE]CELL_COUNT_BY_CLASS[DO NOT EDIT].txt'

if __name__ == '__main__':
    lst01 = dict(zip(PATHOLOGY_TYPE_CLASSES, PATHOLOGY_TYPE_COLORS))
    lst02 = dict(zip(PATHOLOGY_TYPE_COLORS, PATHOLOGY_TYPE_CLASSES))

    print(lst01 == TYPE_to_COLOR_DICT)
    print(lst02 == COLOR_to_TYPE_DICT)

    print(lst01)
    print(TYPE_to_COLOR_DICT)

    print(lst02)
    print(COLOR_to_TYPE_DICT)