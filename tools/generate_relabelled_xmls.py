# coding: utf-8

"""
读取指定路径下的 csv 文件，按照 labelme 的 xml 格式要求，生成 xml 文件
"""

import csv
import os
import sys
import shutil
from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree as ET

sys.path.append('..')

from utils import FilesScanner, write_to_labelme_xml, generate_name_path_dict


def write_to_labelme_xml(lst, xml_save_path, image_size=608):
    """
    将标注点信息写入 xml 文件， 用于 Labelme 审核
    :param points_dict:
    :param xml_save_path: xml 文件写入路径
    :param image_size: 待写入的 Image 文件尺寸
    :return:
    """

    root = ET.Element("annotation")
    ET.SubElement(root, "folder").text = "folder"
    ET.SubElement(root, "filename").text = key + ".jpg"
    ET.SubElement(root, "path").text = "path"

    source = ET.SubElement(root, "source")
    ET.SubElement(source, "database").text = "Unknown"

    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(image_size)
    ET.SubElement(size, "height").text = str(image_size)
    ET.SubElement(size, "depth").text = "3"

    ET.SubElement(root, "segmented").text = "0"

    for point in lst:
        object = ET.SubElement(root, "object")
        ET.SubElement(object, "name").text = point['name']
        ET.SubElement(object, "pose").text = "Unspecified"
        ET.SubElement(object, "truncated").text = "0"
        ET.SubElement(object, "difficult").text = "0"
        bndbox = ET.SubElement(object, "bndbox")
        ET.SubElement(bndbox, "xmin").text = str(int(point['xmin']))
        ET.SubElement(bndbox, "ymin").text = str(int(point['ymin']))
        ET.SubElement(bndbox, "xmax").text = str(int(point['xmax']))
        ET.SubElement(bndbox, "ymax").text = str(int(point['ymax']))

    raw_string = ET.tostring(root, "utf-8")
    reparsed = parseString(raw_string)

    with open(xml_save_path, "w") as o:
        o.write(reparsed.toprettyxml(indent="\t"))


def generate_labelme_format_xml(csv_files_path, patch_dict, xml_save_path):
    """
    将 csv 文件内容写入 xml
    :param csv_files_path: 读取的 csv 存放目录
    :param xml_save_path: 输出的 xml 存放路径
    :return:
    """
    files = FilesScanner(csv_files_path, postfix=['.csv']).get_files()
    clas_files = [item for item in files if item.endswith('_clas.csv')]

    # 待处理 csv 文件总数
    total = len(clas_files)
    for index, file in enumerate(clas_files):
        print("Processing %s / %s %s" % (index + 1, total, os.path.basename(file)))

        with open(file) as f:
            lines = csv.reader(f)

            dict_ = {}
            next(lines, None)

            for line in lines:
                key = line[0]
                box = {
                    'name': line[3],
                    'xmin': 0 if float(line[5]) < 0 else int(float(line[5]) + 0.5),
                    'ymin': 0 if float(line[6]) < 0 else int(float(line[6]) + 0.5),
                    'xmax': 0 if float(line[7]) < 0 else int(float(line[7]) + 0.5),
                    'ymax': 0 if float(line[8]) < 0 else int(float(line[8]) + 0.5),
                }

                if key not in dict_:
                    dict_[key] = [box]
                else:
                    dict_[key].append(box)

            for key, lst in dict_.items():
                if key in patch_dict:
                    patch = patch_dict[key]
                    label = patch['label']
                    image_path = patch['path']

                    save_path = os.path.join(xml_save_path, label)
                    if not os.path.exists(save_path):
                        os.makedirs(save_path)

                    write_to_labelme_xml(lst, os.path.join(save_path, key + '.xml'))
                    shutil.copy(image_path, save_path)
                else:
                    raise Exception("%s NOT FOUND IN DICT" % file)



if __name__ == '__main__':

    image_608_path = "/home/tsimage/Development/DATA/remark"
    image_608_dict = generate_name_path_dict(image_608_path, ['.jpg'])


    data_save_path = "/home/tsimage/Development/DATA/recheck_xml_and_608"

    dict_ = {}
    for key, value in image_608_dict.items():
        parent = os.path.dirname(value)
        label = os.path.basename(parent)

        dict_[key] = {
            "label": label,
            "path": value
        }


    # 待处理 csv 文件路径
    csv_files_path = '/home/tsimage/Development/DATA/meta_test'

    generate_labelme_format_xml(csv_files_path, dict_, data_save_path)
