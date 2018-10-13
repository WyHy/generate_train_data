# coding: utf-8

"""
    基于算法人员筛选的细胞图像重新构建大图对应 xml 文件
"""
import os
import re
from utils import FilesScanner, generate_selected_level_xml
from constants import SELECTED_CELL_XML_SAVE_PATH

if __name__ == '__main__':
    # 读取指定位置的算法人员筛选后的细胞文件路径
    cell_images_path = "C:/Development/data/CELLS"
    cell_images_lst = FilesScanner(cell_images_path, ['.jpg']).get_files()

    # 2018-03-22-11_26_58_x15789_y31806_w63_h61_s385.jpg
    pattern = re.compile(r'(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)_s(\d+).jpg')

    tiff_cell_dict = {}
    for path in cell_images_lst:
        cell_type = os.path.basename(os.path.dirname(path))
        jpg = os.path.basename(path)
        point = re.findall(pattern, jpg)
        tiff_name, x, y, w, h, _ = point[0]
        if tiff_name in tiff_cell_dict:
            tiff_cell_dict[tiff_name].append({"x": x, "y": y, "w": w, "h": h, "cell_type": cell_type})
        else:
            tiff_cell_dict[tiff_name] = [{"x": x, "y": y, "w": w, "h": h, "cell_type": cell_type}]

    for key, value in tiff_cell_dict.items():
        # 生成大图对应 筛选后的细胞标注点 xml 文件
        xml_file_name = os.path.join(SELECTED_CELL_XML_SAVE_PATH, key + '.xml')
        print('GENERATE XML %s' % xml_file_name)
        if len(value) > 0:
            generate_selected_level_xml(xml_file_name, value)

    print("TIFF COUNT: %s" % len(tiff_cell_dict))
    print("CELL COUNT: %s" % len(cell_images_lst))


