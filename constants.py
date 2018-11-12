# coding: utf-8

"""
常用变量 列表
"""

# 当前可识别病理类型 length = 12
import os

PATHOLOGY_TYPE_CLASSES = [  "HSIL_B",   "HSIL_M",   "HSIL_S",   "ASCH",     "LSIL_E",   "LSIL_F",   "ASCUS",    "SCC_G",    "SCC_R",    "EC",       "AGC",      "FUNGI",    "TRI",      "CC",       "ACTINO",   "VIRUS",    "MC",       "SC",      "RC",        "GEC", ]

# 病理类型对应颜色 length = 12
PATHOLOGY_TYPE_COLORS = [   "#aa0000",  "#aa0000",  "#aa0000",  "#aa007f",  "#005500",  "#005500",  "#00557f",  "#0055ff",  "#0055ff",  "#aa55ff",  "#ff5500",  "#00aa00",  "#00aa7f",  "#00aaff",  "#55aa00",  "#55aa7f",  "#000000",  "#aa00ff",  "#ff0000",  "#aa5500", ]

# 统一归为 AGC 类别的病理图像类别
AGC_CLASSES = ['AGC1', 'AGC2', 'AGC3', 'ADC']

# 病理类别=>对应颜色
TYPE_to_COLOR_DICT = dict(zip(PATHOLOGY_TYPE_CLASSES, PATHOLOGY_TYPE_COLORS))

# 颜色=>对应病理类别
COLOR_to_TYPE_DICT = dict(zip(PATHOLOGY_TYPE_COLORS, PATHOLOGY_TYPE_CLASSES))

# 数据存储根目录
DATA_RESOURCE_ROOT_PATH = os.path.join(os.environ['HOME'] + "/Development/DATA/TEST_20181111_PENG_ZHENGZHOU/")
# DATA_RESOURCE_ROOT_PATH = os.path.join("C:/" + "/Development/DATA/TRAIN_DATA")

# 病理图像本地资源库路径
TIFF_IMAGE_RESOURCE_PATH = os.path.join(os.environ['HOME'], "/Development/DATA/TEST_20181111_PENG_ZHENGZHOU/TIFFS")

# 中间数据文件生成目录
METADATA_FILE_PATH = os.path.join(DATA_RESOURCE_ROOT_PATH, "META")

# 审阅后 xml 数据保存目录
CHECKED_CELL_XML_SAVE_PATH = os.path.join(DATA_RESOURCE_ROOT_PATH, "XMLS_CHECKED")

# 筛选后 xml 数据保存目录
SELECTED_CELL_XML_SAVE_PATH = os.path.join(DATA_RESOURCE_ROOT_PATH, "XMLS_SELECTED")

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

# 默认写入 Labelme 配置文件的 Image 大小
LABELME_DEFAULT_IMAGE_SIZE = 608

# 默认输出的 labelme xml 文件输出目录
LABELME_DEFAULT_XML_OUTPUT_PATH = os.path.join(DATA_RESOURCE_ROOT_PATH, "Labelme", 'xmls')

# 最大可用 CPU 数量
MAX_CPU_WORKERS = 20

if __name__ == '__main__':
    lst01 = dict(zip(PATHOLOGY_TYPE_CLASSES, PATHOLOGY_TYPE_COLORS))
    lst02 = dict(zip(PATHOLOGY_TYPE_COLORS, PATHOLOGY_TYPE_CLASSES))

    print(lst01 == TYPE_to_COLOR_DICT)
    print(lst02 == COLOR_to_TYPE_DICT)

    print(lst01)
    print(TYPE_to_COLOR_DICT)

    print(lst02)
    print(COLOR_to_TYPE_DICT)
