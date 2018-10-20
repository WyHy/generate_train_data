# coding: utf-8

"""
读取指定路径下的 csv 文件，按照 labelme 的 xml 格式要求，生成 xml 文件
"""

import csv
import os

from utils import FilesScanner, write_to_labelme_xml


def generate_labelme_format_xml(csv_files_path, xml_save_path):
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

            write_to_labelme_xml(dict_, xml_save_path)


if __name__ == '__main__':
    # 待处理 csv 文件路径
    csv_files_path = 'C:/tmp/csv'

    # 待生成的 labelme 格式的 xml 文件存放目录
    xml_files_save_path = 'C:/tmp/xmls'

    generate_labelme_format_xml(csv_files_path, xml_files_save_path)
