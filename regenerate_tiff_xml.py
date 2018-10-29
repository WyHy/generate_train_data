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

if __name__ == '__main__':
    # 读取指定位置的算法人员筛选后的细胞文件路径
    # cell_images_path = CELL_IMAGES_SAVE_PATH

    cell_images_path = '/home/cnn/Development/DATA/TRAIN_DATA/20181029_pure_data/CHECKED_PURE_DATA/MERGED'
    print("SCANNING PATH %s..." % cell_images_path)
    cell_images_lst = FilesScanner(cell_images_path, ['.jpg']).get_files()
    print("CELLS COUNT: %s" % len(cell_images_lst))

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
        x, y, w, h = int(x), int(y), int(w), int(h)

        # 处理 2+ 图像，图像切图扩大两倍
        if '2+' in cell_type:
            x = int(x - w / 2)
            y = int(y - h / 2)
            w = 2 * w
            h = 2 * h

        # 处理 2- 图像，图像切图缩小两倍
        if '2-' in cell_type:
            x = int(x + w / 4)
            y = int(y + h / 4)
            w = int(w / 2)
            h = int(h / 2)

        if tiff_name in tiff_cell_dict:
            tiff_cell_dict[tiff_name].append({"x": x, "y": y, "w": w, "h": h, "cell_type": cell_type})
        else:
            tiff_cell_dict[tiff_name] = [{"x": x, "y": y, "w": w, "h": h, "cell_type": cell_type}]

    # print(len(tiff_cell_dict))
    # exit()

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
        # 生成大图对应 筛选后的细胞标注点 xml 文件

    #     xml_file_name = os.path.join(SELECTED_CELL_XML_SAVE_PATH, key + '.xml')

    #     if len(value) > 0:
    #         tasks.append(executor.submit(generate_selected_level_xml, xml_file_name, value))
    #     else:
    #         print("FOUND 0 CELLS IN TIFF %s" % tiff_name)

    # job_count = len(tasks)
    # for future in as_completed(tasks):
    #     job_count -= 1
    #     print("LAST JOB NUM %s" % job_count)

    print("TIFF COUNT: %s" % dict_size)
    print("CELL COUNT: %s" % len(cell_images_lst))
