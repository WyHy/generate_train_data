# coding: utf-8

"""
    基于算法人员筛选的细胞图像重新构建大图对应 xml 文件
"""
import os
import re
from concurrent.futures import ProcessPoolExecutor, as_completed

from utils import FilesScanner, generate_selected_level_xml
from constants import SELECTED_CELL_XML_SAVE_PATH, CELL_IMAGES_SAVE_PATH, MAX_CPU_WORKERS

if not os.path.exists(SELECTED_CELL_XML_SAVE_PATH):
    os.makedirs(SELECTED_CELL_XML_SAVE_PATH, exist_ok=True)

if __name__ == '__main__':
    # 读取指定位置的算法人员筛选后的细胞文件路径
    # cell_images_path = CELL_IMAGES_SAVE_PATH

    cell_images_path = '/home/cnn/Development/DATA/TRAIN_DATA/OK_20181012/CELL_FANGXING'
    print("SCANNING PATH %s..." % cell_images_path)
    cell_images_lst = FilesScanner(cell_images_path, ['.jpg']).get_files()

    # 2018-03-22-11_26_58_x15789_y31806_w63_h61_s385.jpg
    pattern = re.compile(r'(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)_s(\d+).jpg')

    print("COLLECT POINT INFO FROM JPG FILES...")
    tiff_cell_dict = {}
    for path in cell_images_lst:
        cell_type = os.path.basename(os.path.dirname(path))
        jpg = os.path.basename(path)
        point = re.findall(pattern, jpg)
        if not point:
            print(path)
        tiff_name, x, y, w, h, _ = point[0]
        if tiff_name in tiff_cell_dict:
            tiff_cell_dict[tiff_name].append({"x": x, "y": y, "w": w, "h": h, "cell_type": cell_type})
        else:
            tiff_cell_dict[tiff_name] = [{"x": x, "y": y, "w": w, "h": h, "cell_type": cell_type}]

    dict_size = len(tiff_cell_dict)
    print("START GENERATING XML FILES...")

    executor = ProcessPoolExecutor(max_workers=MAX_CPU_WORKERS)
    tasks = []
    for key, value in tiff_cell_dict.items():
        # 生成大图对应 筛选后的细胞标注点 xml 文件

        xml_file_name = os.path.join(SELECTED_CELL_XML_SAVE_PATH, key + '.xml')
        
        if len(value) > 0:
            tasks.append(executor.submit(generate_selected_level_xml, xml_file_name, value))
        else:
            print("FOUND 0 CELLS IN TIFF %s" % tiff_name)

    job_count = len(tasks)
    for future in as_completed(tasks):
        job_count -= 1
        print("LAST JOB NUM %s" % job_count)

    print("TIFF COUNT: %s" % dict_size)
    print("CELL COUNT: %s" % len(cell_images_lst))


