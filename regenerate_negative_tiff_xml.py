# coding: utf-8

"""
    基于算法人员筛选的细胞图像重新构建大图对应 xml 文件
"""
import os
import re
from concurrent.futures import ProcessPoolExecutor, as_completed

from constants import SELECTED_CELL_XML_SAVE_PATH, MAX_CPU_WORKERS
from utils import FilesScanner, generate_selected_level_xml

if not os.path.exists(SELECTED_CELL_XML_SAVE_PATH):
    os.makedirs(SELECTED_CELL_XML_SAVE_PATH, exist_ok=True)


NEGATIVE_CATEGORY_LST = ["SC", "RC", "MC", "GEC"]

if __name__ == '__main__':
    # 读取指定位置的算法人员筛选后的细胞文件路径
    # cell_images_path = CELL_IMAGES_SAVE_PATH

    cell_images_path = '/home/cnn/Development/DATA/NEGATIVE_TIFF_20181113/CELLS'
    print("SCANNING PATH %s..." % cell_images_path)
    cell_images_lst = FilesScanner(cell_images_path, ['.jpg']).get_files()
    print("CELLS COUNT: %s" % len(cell_images_lst))

    # # 1-p0.6042_BD1607254-子宫内膜C_2018-10-09 16_42_03_x23043_y40485_w162_h218_2x.jpg
    pattern00 = re.compile(r'1-p\d\.\d{4}_(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)(_\dx)?.jpg')

    # 2018-03-22-11_26_58_x15789_y31806_w63_h61_s385.jpg
    pattern01 = re.compile(r'(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)(_s\d+)?.jpg')

    print("COLLECT POINT INFO FROM JPG FILES...")
    tiff_cell_dict = {}

    negative_category_cell_count = 0
    for path in cell_images_lst:
        cell_type = os.path.basename(os.path.dirname(path))
        if "_" in cell_type:
            cell_type = cell_type.split("_")[0]

        if cell_type in NEGATIVE_CATEGORY_LST:
            negative_category_cell_count += 1
            continue

        jpg = os.path.basename(path)
        point = re.findall(pattern00, jpg)
        if not point:
            point = re.findall(pattern01, jpg)

        try:
            tiff_name, x, y, w, h, _ = point[0]
        except:
            print("RE ERROR")
            print(jpg)

        x, y, w, h = int(x), int(y), int(w), int(h)

        if tiff_name in tiff_cell_dict:
            tiff_cell_dict[tiff_name].append({"x": x, "y": y, "w": w, "h": h, "cell_type": cell_type})
        else:
            tiff_cell_dict[tiff_name] = [{"x": x, "y": y, "w": w, "h": h, "cell_type": cell_type}]

    dict_size = len(tiff_cell_dict)
    print("START GENERATING XML FILES...")

    executor = ProcessPoolExecutor(max_workers=MAX_CPU_WORKERS)
    tasks = []
    count = 1
    total = len(tiff_cell_dict)
    for key, value in tiff_cell_dict.items():
        print("%s / %s %s... " % (count, total, key))
        xml_file_name = os.path.join(SELECTED_CELL_XML_SAVE_PATH, key + '.xml')
        generate_selected_level_xml(xml_file_name, value)
        count += 1

    print("TIFF COUNT: %s" % dict_size)
    print("CELL COUNT: %s" % len(cell_images_lst))
    print("NEGATIVE CELL COUNT: %s" % negative_category_cell_count)
